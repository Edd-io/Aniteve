from bs4 import BeautifulSoup
from time import sleep
import subprocess
import threading
import requests
import json

URL_AS				= 'https://anime-sama.fr/'
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
	db = None
	disable_get_anime_status = True

	def __init__(self, db):
		self.db = db
		self.get_anime_list()
		if self.disable_get_anime_status == False:
			thread_status_anime = threading.Thread(target=self.get_anime_status)
			thread_status_anime.start()
		else:
			print("\033[91mGet anime status is disabled.\033[0m")
	
	def get_anime_list(self):
		response	= requests.get(self.url)
		soup		= BeautifulSoup(response.text, 'html.parser')
		anime_list	= soup('div', class_='Anime')
		anime_list2	= soup('div', class_='Anime,')
		all_anime	= []

		for i, anime in enumerate(anime_list):
			for j, animeClass in enumerate(anime['class']):
				if animeClass.find(',') != -1:
					anime_list[i]['class'][j] = animeClass.split(',')[0]
			title = anime.find('h1').text
			alternative_title = anime.find('p').text
			if alternative_title == '':
				alternative_title = None
			url = anime.find('a')['href']
			if (url[len(url) - 1] == '/'):
				url = url[:-1]
			img = anime.find('img')['src']
			all_anime.append({'title': title, 'alternative_title': alternative_title, 'genre': anime['class'], 'url': url, 'img': img})
		for i, anime in enumerate(anime_list2):
			for j, animeClass in enumerate(anime['class']):
				if animeClass.find(',') != -1:
					anime_list2[i]['class'][j] = animeClass.split(',')[0]
			title = anime.find('h1').text
			alternative_title = anime.find('p').text
			if alternative_title == '':
				alternative_title = None
			url = anime.find('a')['href']
			if (url[len(url) - 1] == '/'):
				url = url[:-1]
			img = anime.find('img')['src']
			all_anime.append({'title': title, 'alternative_title': alternative_title, 'genre': anime['class'], 'url': url, 'img': img})
		for anime in all_anime:
			anime['title'] = anime['title'].title()
			if anime['alternative_title']:
				anime['alternative_title'] = anime['alternative_title'].title()
			anime['genre'] = [genre.replace('-', ' ').capitalize() for genre in anime['genre']]
			if "Cardlistanime" in anime['genre']:
				anime['genre'].remove("Cardlistanime")
			k = len(anime['genre']) - 1
			while k >= 0:
				if anime['genre'][k].strip() == '':
					anime['genre'].pop(k)
				k -= 1

		all_anime.sort(key=lambda x: x['title'])
		for anime in all_anime:
			self.db.insert_anime(anime)

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
				season.append(line.strip().split('"')[-2])
		return (season)
	
	def get_anime_episodes(self, anime):
		response = requests.get(anime['url'] + '/' + anime['season'] + '/episodes.js')
		if (response.status_code != 200):
			return ({'episodes': {}, 'number': 0})
		data = response.text
		data += '\n' + JS_FUNCTION
		process = subprocess.run(
			['node', '-e', data],
			capture_output=True,
			text=True
		)
		episodes = json.loads(process.stdout)
		for i, episode in enumerate(episodes):
			for j, link in enumerate(episodes[episode]):
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
		headers = {
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
		}
		response	= requests.get(episode, headers=headers)
		response	= response.text.split('\n')
		url			= None

		for line in response:
			pos = line.find('https://')
			endPos = line.find('.m3u8')
			if (pos == -1 or line.find('file:') == -1 or endPos == -1):
				continue
			url = serverUrl + SERV_URL_VIDEO + line[pos + 8:endPos + 5]
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
		response	= requests.get(episode)
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
				list_season = []
				list_redirect = []
				
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

				data = []
				for i, title in enumerate(list_title):
					data.append({'title': title, 'season': list_season[i], 'url': list_redirect[i]})
				self.db.update_anime_status(data)
				sleep(1800)
			except Exception as e:
				pass
		self.thread_status_anime = None
		return