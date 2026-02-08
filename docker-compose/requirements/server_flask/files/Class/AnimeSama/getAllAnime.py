import sys
import cloudscraper
from bs4 import BeautifulSoup
from time import sleep
from random import uniform
from .getUrl import get_url

def getAllAnime(db):
	all_anime = []
	url = str(get_url())

	print(f'URL: {url}')
	if url.startswith('/'):
		if url.endswith('/'):
			url = url[1:]
	url = url + '/catalogue/?type%5B0%5D=Anime&page='
	page = 1
	
	scraper = cloudscraper.create_scraper(
		browser={
			'browser': 'chrome',
			'platform': 'windows',
			'desktop': True
		}
	)
	while True:
		try:
			response = scraper.get(url + str(page), timeout=30)
			if response.status_code != 200:
				print(f'Failed to retrieve page {page}, status code: {response.status_code}')
				if response.status_code == 403:
					print(f'Cloudflare protection may have been updated. Consider using selenium or playwright.')
				break
		except Exception as e:
			print(f'Error retrieving page {page}: {e}')
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
					item['url'] = item['url']
				if 'img' in item and isinstance(item['img'], str):
					item['img'] = item['img']
		all_anime.extend(res)
		page += 1
		delay = uniform(0.5, 1.5)
		sleep(delay)
	print(f'{len(all_anime)} anime found', end='\n\n')
	for anime in all_anime:
		db.insert_anime(anime)

def getList(soup):
	id_div = 'list_catalog'
	list_anime = soup.find('div', id=id_div)
	
	if list_anime is None:
		print(f'Could not find div with id="{id_div}". The website structure may have changed.')
		return None
	
	anime = list_anime.find_all('div', class_='shrink-0')
	list_anime = []
	if (len(anime) == 0):
		return (None)
	for anime in anime:
		title = anime.find('h2').text
		url = anime.find('a')['href']
		img = anime.find('img')['src']
		alternative_title = anime.find('p', class_='alternate-titles').text
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
	genre = anime_soup.find('p', class_='info-value').text
	genre = genre.split(', ')
	languages = availableLanguages(anime_soup)
	for language in languages:
		genre.append(language)
	return (genre)

def availableLanguages(anime_soup):
	languages = []

	line = anime_soup.find_all('p', class_='info-value')[2]
	languages = line.text.split(', ')
	for i, language in enumerate(languages):
		languages[i] = language.title()
	return (languages)