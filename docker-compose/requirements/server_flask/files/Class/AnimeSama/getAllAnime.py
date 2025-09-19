import requests
from bs4 import BeautifulSoup
from time import sleep

def getAllAnime(db):
	all_anime = []
	url = 'https://anime-sama.fr/catalogue/?type%5B0%5D=Anime&page='
	page = 1
	while True:
		response = requests.get(url + str(page))
		if response.status_code != 200:
			break
		soup = BeautifulSoup(response.text, 'html.parser')
		res = getList(soup)
		if (res == None):
			break
		if isinstance(res, list):
			for item in res:
				if not isinstance(item, dict):
					continue
				if 'url' in item and isinstance(item['url'], str):
					item['url'] = item['url'].replace('anime-sama.org', 'anime-sama.fr')
				if 'img' in item and isinstance(item['img'], str):
					item['img'] = item['img'].replace('anime-sama.org', 'anime-sama.fr')
			all_anime.extend(res)
		else:
			try:
				fixed = res.replace('anime-sama.org', 'anime-sama.fr')
			except Exception:
				fixed = res
			if hasattr(fixed, '__iter__') and not isinstance(fixed, dict):
				all_anime.extend(fixed)
			else:
				all_anime.append(fixed)
		page += 1
		sleep(0.5)
	print(f'{len(all_anime)} anime found', end='\n\n')
	for anime in all_anime:
		db.insert_anime(anime)

def getList(soup):
	id_div = 'list_catalog'
	list_anime = soup.find('div', id=id_div)
	
	anime = list_anime.find_all('div', class_='shrink-0')
	list_anime = []
	if (len(anime) == 0):
		return (None)
	for anime in anime:
		title = anime.find('h1').text
		url = anime.find('a')['href']
		img = anime.find('img')['src']
		alternative_title = anime.find('p', class_='text-white text-xs opacity-40 truncate italic').text
		genre = getGenre(anime)
		list_anime.append({
			'title': title,
			'url': url,
			'img': img,
			'alternative_title': alternative_title,
			'genre': str(genre)
		})
	return (list_anime)

def getGenre(anime_soup):
	genre = anime_soup.find('p', class_='mt-0.5 text-gray-300 font-medium text-xs truncate').text
	genre = genre.split(', ')
	languages = availableLanguages(anime_soup)
	for language in languages:
		genre.append(language)
	return (genre)

def availableLanguages(anime_soup):
	languages = []

	line = anime_soup.find_all('p', class_='mt-0.5 text-gray-300 font-medium text-xs truncate')[2]
	languages = line.text.split(', ')
	for i, language in enumerate(languages):
		languages[i] = language.title()
	return (languages)