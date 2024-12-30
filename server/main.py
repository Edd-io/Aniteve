from flask import Flask, request, jsonify
from Class.Database import Database
from Class.AnimeSama import AnimeSama
from Class.Proxy import Proxy
import ast

db = Database()
site = AnimeSama(db)
app = Flask(__name__)
	
@app.route('/api/get_all_anime')
def get_all_anime():
	try:
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
		return ({'anime_list': all_anime})
	except Exception as e:
		return ({'error': str(e)})

@app.route('/api/get_anime_season', methods=['POST'])
def get_anime_season():
	need_keys = ['url']
	anime = request.get_json()

	try:
		for key in need_keys:
			if key not in anime:
				return ({'error': 'Missing key ' + key})
		season = site.get_anime_season(anime)
		return ({'season': season})
	except Exception as e:
		return ({'error': str(e)})

@app.route('/api/get_anime_episodes', methods=['POST'])
def get_anime_episodes():
	need_keys = ['url']

	try:
		anime = request.get_json()
		for key in need_keys:
			if key not in anime:
				return ({'error': 'Missing key ' + key})
		episode = site.get_anime_episodes(anime)
		return (episode)
	except Exception as e:
		return ({'error': str(e)})
	
@app.route('/api/srcFile')
def proxy():
	url = 'https://' + request.url.split('?', 1)[1]

	try:
		if (url == 'https://'):
			return {'error': 'Missing url'}
		return ({'src': site.get_source_file(url)})
	except Exception as e:
		return ({'error': str(e)})

@app.route('/api/video')
def video():
	url = 'https://' + request.url.split('?', 1)[1]

	try:
		if (url == 'https://'):
			return ({'error': 'Missing url'})
		if (url.find('sibnet') != -1):
			return (Proxy.sibnet(url))
		elif (url.find('oneupload') != -1):
			return (Proxy.oneupload(url))
		elif (url.find('sendvid') != -1):
			return (Proxy.sendvid(url))
		else:
			return (Proxy.vidmoly(url))
	except Exception as e:
		return ({'error': str(e)})

@app.route('/api/update_progress', methods=['POST'])
def update_progress():
	need_keys = ['id', 'episode', 'seasonId', 'progress', 'totalEpisode', 'allSeasons']
	anime = request.get_json()

	try:
		for key in need_keys:
			if key not in anime:
				return {'error': 'Missing key ' + key}
		db.update_progress(anime)
		return {'status': 'success'}
	except Exception as e:
		return {'error': str(e)}
	
@app.route('/api/get_progress', methods=['POST'])
def get_progress():
	need_keys = ['id']
	anime = request.get_json()

	try:
		for key in need_keys:
			if key not in anime:
				return {'error': 'Missing key ' + key}
		progress = db.get_progress(anime)
		return (progress)
	except Exception as e:
		return {'error': str(e)}
	
@app.route('/api/get_all_progress')
def get_all_progress():
	anime = request.get_json()

	try:
		progress = db.get_all_progress(anime)
		return (progress)
	except Exception as e:
		return {'error': str(e)}


if __name__ == '__main__':
	app.run(debug=False, port=8080, host='0.0.0.0')