from bs4 import BeautifulSoup
import requests
import subprocess
import json

SERV_URL_SRCFILE = 'http://localhost:8080' + '/api/srcFile?'
SERV_URL_VIDEO = 'http://localhost:8080' + '/api/video?'

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
		for anime in all_anime:
			self.db.insert_anime(anime)

	def get_anime_season(self, anime):
		response	= requests.get(anime['url'])
		response	= response.text.split('\n')
		season		= []

		for line in response:
			if (line.find('/*') != -1):
				continue
			if (line.find('panneauAnime("') != -1):
				season.append(line.strip().split('"')[-2])
		return (season)
	
	def get_anime_episodes(self, anime, season):
		response	= requests.get(anime['url'] + season + '/episodes.js')

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
				episodes[episode][j] = episodes[episode][j].replace('https:/', SERV_URL_SRCFILE)
		data = {'number': len(episodes)}
		data['episodes'] = episodes
		print(data['episodes']['eps1'])
		return (episodes)

	def get_source_file(self, episode):
		if (episode.find('sibnet') != -1):
			return (self.__get_source_file_from_sibnet(episode))
	
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
