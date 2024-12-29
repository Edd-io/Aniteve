from flask import Flask, request, jsonify
from Class.Database import Database
from Class.AnimeSama import AnimeSama
from Class.Proxy import Proxy
import ast

db = Database()
site = AnimeSama(db)
app = Flask(__name__)

@app.route('/api/srcFile')
def proxy():
	url = 'https://' + request.url.split('?', 1)[1]
	return {'src': site.get_source_file(url)}

@app.route('/api/video')
def video():
	url = 'https://' + request.url.split('?', 1)[1]
	if (url.find('sibnet') != -1):
		return (Proxy.sibnet(url))
	elif (url.find('oneupload') != -1):
		return (Proxy.oneupload(url))
	elif (url.find('sendvid') != -1):
		return (Proxy.sendvid(url))
	else:
		return (Proxy.vidmoly(url))
	
@app.route('/api/get_all_anime')
def get_all_anime():
	anime_list = db.get_all_anime()
	all_anime = []
	for anime in anime_list:
		all_anime.append({
			'id': anime[0],
			'title': anime[1],
			'alternative_title': anime[2],
			'genre': ast.literal_eval(anime[3]),
			'url': anime[4],
			'img': anime[5]
		})
	return {'anime_list': all_anime}

@app.route('/api/get_anime_season', methods=['POST'])
def get_anime_season():
	print('Requete get_anime_season |', request.get_json())
	anime = request.get_json()
	season = site.get_anime_season(anime)
	return {'season': season}

@app.route('/api/get_anime_episodes', methods=['POST'])
def get_anime_episodes():
	print('Requete get_anime_episodes |', request.get_json())
	try:
		anime = request.get_json()
		episode = site.get_anime_episodes(anime)
		return episode
	except Exception as e:
		return {'error': str(e)}

if __name__ == '__main__':
	# season = site.get_anime_season({'url': 'https://anime-sama.fr/catalogue/arifureta/'})
	# episode = site.get_anime_episodes({'url': 'https://anime-sama.fr/catalogue/arifureta/'}, season[2])
	# print(episode['eps1'][4])
	# m3u8_link = site.get_source_file(episode['eps1'][4].replace('http://localhost:8080/api/srcFile?', 'https://'))
	# print("\n" + m3u8_link)


	# season = site.get_anime_season({'url': 'https://anime-sama.fr/catalogue/365-days-to-the-wedding/'})
	# print(season)
	# episode = site.get_anime_episodes({'url': 'https://anime-sama.fr/catalogue/365-days-to-the-wedding/'}, season[0])
	# print(episode['eps1'][3])
	# m3u8_link = site.get_source_file(episode['eps1'][3].replace('http://localhost:8080/api/srcFile?', 'https://'))
	# print(m3u8_link)

	# db = Database()
	# site = AnimeSama(db)
	# season = site.get_anime_season({'url': 'https://anime-sama.fr/catalogue/one-piece/'})
	# print(season)
	# episode = site.get_anime_episodes({'url': 'https://anime-sama.fr/catalogue/one-piece/'}, season[0])
	# print(episode['eps1'][0])

	# m3u8_link = site.get_source_file(episode['eps1'][2].replace('http://localhost:8080/api/srcFile?', 'https:/'))
	# print(m3u8_link)
	# Proxy.vidmoly(m3u8_link.replace('http://localhost:8080/api/video?', 'https://'))
	# # Proxy.vidmoly('https://trst-1113-t.vmrest.space/hls/xqx2ou7egjokjiqbtg2sh6q3xmhtpqdntvkmx64kfllroqm6jbbz6zj7foga/index-v1-a1.m3u8')
	# # Proxy.vidmoly('http://localhost:8080/api/video?vidmoly.to/hls/xqx2okhmgjokjiqbtg2sh6iyvcgs6mbzz7i3iohm7jx5csbw3ejxtgvqkeva/index-v1-a1.m3u8'.replace('http://localhost:8080/api/video?', 'https://'))
	# # all_m3u8_link = site.get_source_file(m3u8_link)
	# print(all_m3u8_link)

	# episode = site.get_source_file('https://video.sibnet.ru/shell.php?videoid=5700596')
	# print(episode)
	app.run(debug=False, port=8080, host='0.0.0.0')