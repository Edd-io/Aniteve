from bs4 import BeautifulSoup
from .getAllAnime import getAllAnime
from time import sleep
import subprocess
import threading
import requests
import json
import re

URL_AS				= 'https://anime-sama.org/'
SERV_URL_SRCFILE	= '/api/srcFile?'
SERV_URL_VIDEO		= '/api/video?'
AVAILABLE_PLAYER	= ['sibnet', 'oneupload', 'sendvid', 'vidmoly']
JS_FUNCTION			= '''
	function parseFileEpisode()
	{
		let i = 1;
		let data = {};

		while (1)
		{
			if (!global['eps' + i])
				break ;
			for (let j = 1; j < global['eps' + i].length + 1; j++)
			{
				if (data['eps' + j] == undefined)
					data['eps' + j] = [];
				data['eps' + j].push(global['eps' + i][j - 1]);
			}
			i++;
		}
		return (data);
	}
	console.log(JSON.stringify(parseFileEpisode()));
'''

class AnimeSama:
	url = URL_AS + "catalogue/listing_all.php"
	thread_status_anime = None
	thread_new_anime = None
	disable_get_anime_status = False
	disable_get_new_animes = False
	filever_nb = 0

	def __init__(self, db):
		self.db = db
		if not self.disable_get_new_animes:
			self.get_anime_list()
		else:
			print("\033[91mGet new animes is disabled.\033[0m")
		if not self.disable_get_anime_status:
			self.start_threads()
		else:
			print("\033[91mGet anime status is disabled.\033[0m")

	def start_threads(self):
		print("Starting threads...")
		self.thread_status_anime = threading.Thread(target=self.get_anime_status)
		self.thread_status_anime.start()
		self.thread_new_anime = threading.Thread(target=self.get_new_animes)
		self.thread_new_anime.start()
		self.threads_started = True

	def get_anime_list(self):
		getAllAnime(self.db)

	def get_anime_season(self, anime):
		response	= requests.get(anime['url'])
		response	= response.text.split('\n')
		season		= []
		isInComment = False

		for line in response:
			if (line.find('/*') != -1):
				if (line.find('*/') != -1):
					isInComment = False
				else:
					isInComment = True
				continue
			if (line.find('*/') != -1 and isInComment == True):
				isInComment = False
			elif (isInComment == True):
				continue
			elif (line.find('panneauAnime("') != -1):
				match = re.search(r'panneauAnime\("([^"]+)",\s*"([^"]+)"\)', line)
				if match:
					season_name = match.group(1)
					season_url = match.group(2)
					lang = season_url.split('/')[-1]
					season.append({'name': season_name, 'url': season_url, 'lang': lang})
					print(f"Found season: {season_name} with URL: {season_url} and Language: {lang}")
				else:
					print(f"Could not parse season line: {line}")
		return (season)
	
	def get_anime_episodes(self, anime):
		response = requests.get(anime['url'] + '/' + anime['season'] + '/episodes.js?filever=' + str(self.filever_nb))
		self.filever_nb += 1
		if (response.status_code != 200):
			return ({'episodes': {}, 'number': 0})
		data = response.text
		data += '\n' + JS_FUNCTION
		process = subprocess.run(
			['/usr/bin/node', '-e', data],
			capture_output=True,
			text=True
		)
		episodes = json.loads(process.stdout)
		for i, episode in enumerate(episodes):
			for j in range(len(episodes[episode])):
				if (episodes[episode][j].find('vidmoly.to') != -1):
					episodes[episode][j] = episodes[episode][j].replace('vidmoly.to', 'vidmoly.net')
				episodes[episode][j] = episodes[episode][j].replace('https://', anime['serverUrl'] + SERV_URL_SRCFILE)
				episodes[episode][j] = "".join(episodes[episode][j].split())
			k = 0
			while k < len(episodes[episode]):
				find = False
				for player in AVAILABLE_PLAYER:
					if episodes[episode][k].find(player) != -1:
						find = True
						break
				if find == False:
					episodes[episode].pop(k)
				else:
					k += 1

		data = {}
		data['episodes'] = episodes
		data['number'] = len(episodes)
		return (data)

	def get_source_file(self, episode, serverUrl):
		if (episode.find('sibnet') != -1):
			return (self.__get_source_file_from_sibnet(episode, serverUrl))
		elif (episode.find('oneupload') != -1):
			return (self.__get_source_file_from_oneupload(episode, serverUrl))
		elif (episode.find('sendvid') != -1):
			return (self.__get_source_file_from_sendvid(episode, serverUrl))
		else:
			return (self.__get_source_file_from_vidmoly(episode, serverUrl))
	
	def __get_source_file_from_sibnet(self, episode, serverUrl):
		headers = {
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
		}
		response	= requests.get(episode, headers=headers)
		response	= response.text.split('\n')
		url			= None

		for line in response:
			pos = line.find('src')
			endPos = line.find('.mp4')
			if (pos == -1 or endPos == -1):
				continue
			endPos += 4
			pos = endPos - 4
			while (line[pos] != '"' and line[pos] != "'"):
				pos -= 1
			url = serverUrl + SERV_URL_VIDEO + 'video.sibnet.ru' + line[pos + 1:endPos] + '|' + episode
		return (url)
	
	def __get_source_file_from_vidmoly(self, episode, serverUrl):
		if 'vidmoly.to' in episode:
			domain = 'vidmoly.to'
		else:
			domain = 'vidmoly.net'
			
		headers = {
			'Host': domain,
			'Referer': f'https://{domain}',
			'sec-fetch-dest': 'video',
			'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
		}
		print("Fetching video from Vidmoly...")
		print(f"Episode URL: {episode}")
		
		original_episode = episode
		if 'vidmoly.to' in episode:
			episode_net = episode.replace('vidmoly.to', 'vidmoly.net')
			print(f"Also trying with .net domain: {episode_net}")
		else:
			episode_net = None
			
		timeout_duration = 3 if 'vidmoly.to' in episode else 30
		
		try:
			response = requests.get(episode, headers=headers, timeout=timeout_duration)
			print(f"Response status: {response.status_code}")
			print(f"Response length: {len(response.text)}")
		except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
			print(f"Request to {episode} failed after {timeout_duration}s: {e}")
			if episode_net:
				print(f"Trying alternative domain: {episode_net}")
				try:
					headers['Host'] = 'vidmoly.net'
					headers['Referer'] = 'https://vidmoly.net'
					response = requests.get(episode_net, headers=headers, timeout=30)
					episode = episode_net
				except Exception as e2:
					print(f"Alternative request also failed: {e2}")
					return None
			else:
				return None
		except Exception as e:
			print(f"Request failed: {e}")
			if episode_net:
				print(f"Trying alternative domain: {episode_net}")
				try:
					headers['Host'] = 'vidmoly.net'
					headers['Referer'] = 'https://vidmoly.net'
					response = requests.get(episode_net, headers=headers, timeout=30)
					episode = episode_net
				except Exception as e2:
					print(f"Alternative request also failed: {e2}")
					return None
			else:
				return None
		response	= response.text.split('\n')
		url			= None

		for line in response:
			pos = line.find('https://')
			endPos = line.find('.m3u8')
			if (pos == -1 or line.find('file:') == -1 or endPos == -1):
				continue
			while (line[endPos] != '"' and line[endPos] != "'"):
				endPos += 1
			original_url = line[pos + 8:endPos]
			if episode_net and episode == episode_net and 'vidmoly.to' in original_url:
				original_url = original_url.replace('vidmoly.to', 'vidmoly.net')
			url = serverUrl + SERV_URL_VIDEO + original_url
			break
		return (url)
	
	def __get_source_file_from_oneupload(self, episode, serverUrl):
		response	= requests.get(episode)
		response	= response.text.split('\n')
		url			= None

		for line in response:
			if (line.find('{file:') == -1):
				continue
			pos = line.find('https://')
			posEnd = line.find('.m3u8')
			if (pos == -1 or posEnd == -1):
				continue
			while (line[posEnd] != '"' and line[posEnd] != "'"):
				posEnd += 1
			url = serverUrl + SERV_URL_VIDEO + line[pos + 8:posEnd]
		return (url)

	def __get_source_file_from_sendvid(self, episode, serverUrl):
		headers = {
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
		}
		response	= requests.get(episode, headers=headers)
		response	= response.text.split('\n')
		url			= None

		for line in response:
			if (line.find('video_source') == -1):
				continue
			pos = line.find('https://')
			posEnd = line.find('.mp4')
			if (pos == -1 or posEnd == -1):
				continue
			while (line[posEnd] != '"' and line[posEnd] != "'"):
				posEnd += 1
			url = serverUrl + SERV_URL_VIDEO + line[pos + 8:posEnd]
		return (url)

	def get_anime_status(self):
		while (1):
			try:
				sleep(30)
				response = requests.get(URL_AS)
				soup = BeautifulSoup(response.text, 'html.parser')
				list_anime = soup.find('div', id='containerAjoutsAnimes')
				list_title = list_anime.find_all('h1')
				list_url = list_anime.find_all('a')
				list_episode = list_anime.find_all('button', class_='bg-cyan-600')
				list_season = []
				list_redirect = []
				list_number_episode = []
				
				for i, title in enumerate(list_title):
					list_title[i] = title.text
				for i, url in enumerate(list_url):
					j = len(url['href']) - 1
					nb_slash = 0
					while (url['href'][j - 1]):
						if (url['href'][j - 1] == '/'):
							nb_slash += 1
						if (nb_slash == 2):
							list_season.append(url['href'][j:-1])
							list_redirect.append(url['href'][:j - 1])
							break
						j -= 1
					if (nb_slash != 2):
						list_url.pop(i)
				for i, episode in enumerate(list_episode):
					try:
						ep = episode.text.lower().split('episode ')[1]
						ep = ep.split(' ')[0]
						ep = int(ep)
					except:
						ep = -1
					list_number_episode.append(ep)
				data = []
				for i, title in enumerate(list_title):
					if (list_number_episode[i] == -1):
						continue
					data.append({'title': title, 'season': list_season[i], 'url': list_redirect[i].replace('anime-sama.fr', 'anime-sama.org'), 'episode': list_number_episode[i]})
				self.db.update_anime_status(data)
				sleep(1800)
			except Exception as e:
				sleep(1800)
				pass
		self.thread_status_anime = None
		return
	
	def get_new_animes(self):
		while (1):
			try:
				sleep(259200)
				self.get_anime_list()
			except Exception as e:
				sleep(259200)
				pass
		self.thread_new_anime = None
		return
