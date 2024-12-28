from bs4 import BeautifulSoup
import requests
import subprocess
import json

SERV_URL_SRCFILE = 'http://192.168.1.172:8080' + '/api/srcFile?'
SERV_URL_VIDEO = 'http://192.168.1.172:8080' + '/api/video?'
AVAILABLE_PLAYER = ['sibnet', 'oneupload', 'sendvid', 'vidmoly']
js_function = '''
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
	url = "https://anime-sama.fr/catalogue/listing_all.php"

	def __init__(self, db):
		self.db = db
		self.get_anime_list()
	
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
			img = anime.find('img')['src']
			all_anime.append({'title': title, 'alternative_title': alternative_title, 'genre': anime['class'], 'url': url, 'img': img})
		for anime in all_anime:
			anime['title'] = anime['title'].capitalize()
			if anime['alternative_title']:
				anime['alternative_title'] = anime['alternative_title'].capitalize()
			anime['genre'] = [genre.capitalize() for genre in anime['genre']]
		all_anime.sort(key=lambda x: x['title'])
		for anime in all_anime:
			self.db.insert_anime(anime)
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
		response	= requests.get(anime['url'] + '/' + anime['season'] + '/episodes.js')
		if (response.status_code != 200):
			return ({'episodes': {}, 'number': 0})
		data = response.text
		data += '\n' + js_function
		process = subprocess.run(
			['node', '-e', data],
			capture_output=True,
			text=True
		)
		episodes = json.loads(process.stdout)
		for i, episode in enumerate(episodes):
			for j, link in enumerate(episodes[episode]):
				episodes[episode][j] = episodes[episode][j].replace('https://', SERV_URL_SRCFILE)
				# find = False
				# for player in AVAILABLE_PLAYER:
				# 	if episodes[episode][j].find(player) != -1:
				# 		find = True
				# 		break
				# if find == False:
				# 	episodes[episode].pop(j)
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

	def get_source_file(self, episode):
		if (episode.find('sibnet') != -1):
			return (self.__get_source_file_from_sibnet(episode))
		elif (episode.find('oneupload') != -1):
			return (self.__get_source_file_from_oneupload(episode))
		elif (episode.find('sendvid') != -1):
			return (self.__get_source_file_from_sendvid(episode))
		else:
			return (self.__get_source_file_from_vidmoly(episode))
	
	def __get_source_file_from_sibnet(self, episode):
		response	= requests.get(episode)
		response	= response.text.split('\n')
		url			= None

		for line in response:
			pos = line.find('src: "')
			if (pos == -1):
				continue
			url = SERV_URL_VIDEO + 'video.sibnet.ru' + line[pos + 6:line.find('"', pos + 6)]
		return (url)
	
	def __get_source_file_from_vidmoly(self, episode):
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
			url = SERV_URL_VIDEO + line[pos + 8:endPos + 5]
		return (url)
	
	def __get_source_file_from_oneupload(self, episode):
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
			url = SERV_URL_VIDEO + line[pos + 8:posEnd]
		return (url)

	def __get_source_file_from_sendvid(self, episode):
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
			url = SERV_URL_VIDEO + line[pos + 8:posEnd]
		return (url)