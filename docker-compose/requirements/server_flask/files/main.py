from flask import Flask, request, Response, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from Class.Database import Database
from Class.AnimeSama.AnimeSama import AnimeSama
from Class.Proxy import Proxy
from Class.Downloader import Downloader
from Class.RoomManager import RoomManager
import ast
import jwt
import json
from gevent.lock import Semaphore
import requests
from credientials import *
from flask_cors import CORS
from PIL import Image
from io import BytesIO

db = Database()
site = AnimeSama(db)
app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
download = Downloader(db)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')
room_manager = RoomManager()
list_available_ip = []
lock_list_available_ip = Semaphore()

def generate_token():
	return (jwt.encode({}, app.config['SECRET_KEY'], algorithm='HS256'))

def decode_token(token):
	try:
		return (jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256']))
	except jwt.ExpiredSignatureError:
		return (None)
	except jwt.InvalidTokenError:
		return (None)

@app.route('/api/health')
def health():
	return jsonify({'status': 'ok'})

@app.route('/api/login', methods=['POST'])
def login():
	data = request.get_json()
	need_keys = ['password']

	try:
		for key in need_keys:
			if key not in data:
				return jsonify({'error': 'Missing key ' + key})
		if (data['password'] == password):
			return jsonify({'token': generate_token()})
		return jsonify({'error': 'Invalid password'})
	except Exception as e:
		return jsonify({'error': str(e)})
	
@app.route('/api/check_token', methods=['POST'])
def check_token():
	data = request.get_json()
	need_keys = ['token']

	try:
		for key in need_keys:
			if key not in data:
				return jsonify({'error': 'Missing key ' + key})
		if (decode_token(data['token']) == None):
			return jsonify({'error': 'Invalid token'})
		return jsonify({'status': 'success'})
	except Exception as e:
		return jsonify({'error': str(e)})
	
def check_token_in_request():
	if (request.headers.get('Authorization') == None or decode_token(request.headers.get('Authorization')) == None):
		return (Response(
			response=json.dumps({'error': 'Invalid or missing token'}),
			status=401,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	return (None)

@app.route('/api/add_user', methods=['POST'])
def add_user():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['name']
	data = request.get_json()

	try:
		for key in need_keys:
			if key not in data:
				return jsonify({'error': 'Missing key ' + key})
		db.insert_user(data['name'])
		return jsonify({'status': 'success'})
	except Exception as e:
		return jsonify({'error': str(e)})

@app.route('/api/get_users')
def get_users():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	try:
		users = db.get_users()
		return jsonify(users)
	except Exception as e:
		return jsonify({'error': str(e)})
	
@app.route('/api/get_name', methods=['POST'])
def get_name():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['id']
	data = request.get_json()

	try:
		for key in need_keys:
			if key not in data:
				return jsonify({'error': 'Missing key ' + key})
		name = db.get_name_by_id(data['id'])
		return (name)
	except Exception as e:
		return jsonify({'error': str(e)})


@app.route('/api/get_all_anime')
def get_all_anime():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
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
		return (Response(
			response=json.dumps(all_anime),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))

@app.route('/api/get_random_anime')
def get_random_anime():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	try:
		limit = request.args.get('limit', 10, type=int)
		anime_list = db.get_random_anime(limit)
		all_anime = []
		for anime in anime_list:
			all_anime.append({
				'id': anime[0],
				'title': anime[1],
				'alternative_title': anime[2],
				'genre': ast.literal_eval(anime[3]) if anime[3] else [],
				'url': anime[4],
				'img': anime[5]
			})
		return (Response(
			response=json.dumps(all_anime),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))

@app.route('/api/get_anime_by_genre')
def get_anime_by_genre():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	try:
		genre = request.args.get('genre', '', type=str)
		limit = request.args.get('limit', 10, type=int)
		if not genre:
			return jsonify({'error': 'Missing genre parameter'})
		anime_list = db.get_anime_by_genre(genre, limit)
		all_anime = []
		for anime in anime_list:
			all_anime.append({
				'id': anime[0],
				'title': anime[1],
				'alternative_title': anime[2],
				'genre': ast.literal_eval(anime[3]) if anime[3] else [],
				'url': anime[4],
				'img': anime[5]
			})
		return (Response(
			response=json.dumps(all_anime),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))

@app.route('/api/get_all_genres')
def get_all_genres():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	try:
		genres = db.get_all_genres()
		return (Response(
			response=json.dumps(genres),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))

@app.route('/api/get_recent_anime')
def get_recent_anime():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	try:
		limit = request.args.get('limit', 10, type=int)
		anime_list = db.get_recent_anime(limit)
		all_anime = []
		for anime in anime_list:
			all_anime.append({
				'id': anime[0],
				'title': anime[1],
				'alternative_title': anime[2],
				'genre': ast.literal_eval(anime[3]) if anime[3] else [],
				'url': anime[4],
				'img': anime[5]
			})
		return (Response(
			response=json.dumps(all_anime),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))

@app.route('/api/search_anime')
def search_anime():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	try:
		query = request.args.get('q', '', type=str)
		limit = request.args.get('limit', 8, type=int)
		if not query or len(query) < 2:
			return (Response(
				response=json.dumps([]),
				status=200,
				mimetype='application/json',
				headers={'Access-Control-Allow-Origin': '*'}
			))
		anime_list = db.search_anime(query, limit)
		all_anime = []
		for anime in anime_list:
			all_anime.append({
				'id': anime[0],
				'title': anime[1],
				'alternative_title': anime[2],
				'genre': ast.literal_eval(anime[3]) if anime[3] else [],
				'url': anime[4],
				'img': anime[5]
			})
		return (Response(
			response=json.dumps(all_anime),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))

@app.route('/api/get_user_stats', methods=['POST'])
def get_user_stats():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	try:
		data = request.get_json()
		if 'idUser' not in data:
			return jsonify({'error': 'Missing idUser'})
		stats = db.get_user_stats(data['idUser'])
		return (Response(
			response=json.dumps(stats),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))

@app.route('/api/get_home_data')
def get_home_data():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	try:
		import random

		main_genres = db.get_main_genres()

		# Shuffle and pick 3 random main genres
		if len(main_genres) > 3:
			selected_genres = random.sample(main_genres, 3)
		else:
			selected_genres = main_genres

		result = {
			'sections': []
		}

		for genre in selected_genres:
			anime_list = db.get_anime_by_genre(genre, 8)
			if len(anime_list) > 0:
				section = {
					'title': genre,
					'anime': []
				}
				for anime in anime_list:
					section['anime'].append({
						'id': anime[0],
						'title': anime[1],
						'alternative_title': anime[2],
						'genre': ast.literal_eval(anime[3]) if anime[3] else [],
						'url': anime[4],
						'img': anime[5]
					})
				result['sections'].append(section)

		return (Response(
			response=json.dumps(result),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))

@app.route('/api/get_anime_season', methods=['POST'])
def get_anime_season():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['url']
	anime = request.get_json()

	try:
		for key in need_keys:
			if key not in anime:
				return jsonify({'error': 'Missing key ' + key})
		season = site.get_anime_season(anime)
		return (Response(
			response=json.dumps({'season': season}),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))

@app.route('/api/get_anime_episodes', methods=['POST'])
def get_anime_episodes():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['url', 'serverUrl', 'season']

	try:
		anime = request.get_json()
		for key in need_keys:
			if key not in anime:
				return jsonify({'error': 'Missing key ' + key})
		episode = site.get_anime_episodes(anime)
		return (Response(
			response=json.dumps(episode),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	
@app.route('/api/srcFile', methods=['POST'])
def srcFile():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	url = 'https://' + request.url.split('?', 1)[1]
	need_keys = ['serverUrl']

	with lock_list_available_ip:
		if (request.headers['X-Real-IP'] not in list_available_ip):
			list_available_ip.append(request.headers['X-Real-IP'])
	try:
		anime = request.get_json()
		if (url == 'https://'):
			return {'error': 'Missing url'}
		for key in need_keys:
			if key not in anime:
				return jsonify({'error': 'Missing key ' + key})
		return (Response(
			response=json.dumps({'src': site.get_source_file(url, anime['serverUrl'])}),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return (Response(
			response=json.dumps({'error': str(e)}),
			status=500,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))

@app.route('/api/video')
def video():
	try:
		with lock_list_available_ip:
			if (request.headers['X-Real-IP']not in list_available_ip):
				return (Response(
					response=json.dumps({'error': 'Access denied'}),
					status=403,
					mimetype='application/json',
					headers={'Access-Control-Allow-Origin': '*'}
				))
	except Exception as e:
		pass

	url = 'https://' + request.url.split('?', 1)[1]
	try:
		if (url == 'https://'):
			return (Response(
				response=json.dumps({'error': 'Missing url'}),
				status=500,
				mimetype='application/json',
				headers={'Access-Control-Allow-Origin': '*'}
			))
		if (url.find('sibnet') != -1):
			return (Proxy.sibnet(url))
		elif (url.find('oneupload') != -1):
			return (Proxy.oneupload(url))
		elif (url.find('sendvid') != -1):
			return (Proxy.sendvid(url))
		else:
			return (Proxy.vidmoly(url))
	except Exception as e:
		return jsonify({'error': str(e)})

@app.route('/api/update_progress', methods=['POST'])
def update_progress():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['id', 'episode', 'seasonId', 'progress', 'totalEpisode', 'allSeasons', 'poster', 'idUser']
	anime = request.get_json()

	try:
		for key in need_keys:
			if key not in anime:
				return jsonify({'error': 'Missing key ' + key})
		db.update_progress(anime)
		return jsonify({'status': 'success'})
	except Exception as e:
		return jsonify({'error': str(e)})
	
@app.route('/api/get_progress', methods=['POST'])
def get_progress():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['id', 'idUser']
	anime = request.get_json()

	try:
		for key in need_keys:
			if key not in anime:
				return jsonify({'error': 'Missing key ' + key})
		progress = db.get_progress(anime)
		return (progress)
	except Exception as e:
		return jsonify({'error': str(e)})
	
@app.route('/api/get_all_progress', methods=['POST'])
def get_all_progress():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['idUser']
	anime = request.get_json()

	try:
		for key in need_keys:
			if key not in anime:
				return jsonify({'error': 'Missing key ' + key})
		progress = db.get_all_progress(anime['idUser'])
		return (progress)
	except Exception as e:
		return jsonify({'error': str(e)})
	
@app.route('/api/tmdb', methods=['POST'])
def tmdb():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['url']
	data = request.get_json()

	try:
		for key in need_keys:
			if key not in data:
				return jsonify({'error': 'Missing key ' + key})
		if (data['url'].startswith('https://api.themoviedb.org/3/') == False):
			return {'error': 'Invalid url'}
		response = requests.get(data['url'].replace('{api_key_tmdb}', 'api_key=' + key_api_tmdb))
		return (Response(
			response=response.text,
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return jsonify({'error': str(e)})
	
@app.route('/api/get_average_color', methods=['POST'])
def get_average_color():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['url']
	data = request.get_json()

	try:
		for key in need_keys:
			if key not in data:
				return jsonify({'error': 'Missing key ' + key})
		response = requests.get(data['url'])
		image = Image.open(BytesIO(response.content))
		image = image.resize((25, 25))
		pixels = list(image.getdata())
		total_pixels = len(pixels)
		avg_color = tuple(sum(channel) // total_pixels for channel in zip(*pixels))
		return (Response(
			response=json.dumps({'average_color': avg_color}),
			status=200,
			mimetype='application/json',
			headers={'Access-Control-Allow-Origin': '*'}
		))
	except Exception as e:
		return jsonify({'error': str(e)})


@app.route('/api/download', methods=['POST'])
def download_func():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['src', 'name', 'episode', 'season', 'serverUrl', 'poster']
	data = request.get_json()

	try:
		for key in need_keys:
			if key not in data:
				return jsonify({'error': 'Missing key ' + key})
		download.add(data)
		return jsonify({'status': 'success'})
	except Exception as e:
		return {'error': str(e)}

@app.route('/api/get_status_download')
def get_status_download():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	try:
		status = download.get_status()
		return (status)
	except Exception as e:
		return jsonify({'error': str(e)})
	
@app.route('/api/del_download', methods=['POST'])
def delete_download():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['id']
	data = request.get_json()

	try:
		for key in need_keys:
			if key not in data:
				return jsonify({'error': 'Missing key ' + key})
		download.delete(data['id'])
		return jsonify({'status': 'success'})
	except Exception as e:
		return {'error': str(e)}

@app.route('/api/download/<name>')
def downloadEp(name):
	try:
		with lock_list_available_ip:
			if (request.headers['X-Real-IP'] not in list_available_ip):
				return (Response(
					response=json.dumps({'error': 'Access denied'}),
					status=403,
					mimetype='application/json',
					headers={'Access-Control-Allow-Origin': '*'}
				))
	except Exception as e:
		pass

	try:
		return (download.download(name))
	except Exception as e:
		return jsonify({'error': str(e)})

@app.route('/api/delete_progress', methods=['POST'])
def deleteProgress():
	token_valid = check_token_in_request()

	if (token_valid != None):
		return (token_valid)
	need_keys = ['id', 'idUser']
	data = request.get_json()

	try:
		for key in need_keys:
			if key not in data:
				return jsonify({'error': 'Missing key ' + key})
		db.delete_progress(data['id'], data['idUser'])
		return jsonify({'status': 'success'})
	except Exception as e:
		return {'error': str(e)}

# Together/Rooms endpoints
@app.route('/api/rooms', methods=['GET'])
def get_rooms():
	token_valid = check_token_in_request()
	if (token_valid != None):
		return (token_valid)
	try:
		rooms = room_manager.get_all_rooms()
		return jsonify({'rooms': rooms})
	except Exception as e:
		return jsonify({'error': str(e)})

@app.route('/api/rooms/create', methods=['POST'])
def create_room():
	token_valid = check_token_in_request()
	if (token_valid != None):
		return (token_valid)
	try:
		data = request.get_json()
		user_id = data.get('user_id')
		username = data.get('username')
		room_name = data.get('room_name')

		if not user_id or not username:
			return jsonify({'error': 'Missing user_id or username'})

		room = room_manager.create_room(user_id, username, room_name)
		if not room:
			return jsonify({'error': 'Maximum rooms reached (2 per user)'})

		return jsonify({
			'room_id': room.room_id,
			'name': room.name
		})
	except Exception as e:
		return jsonify({'error': str(e)})

# WebSocket events
@socketio.on('join_room')
def handle_join_room(data):
	try:
		room_id = data.get('room_id')
		user_id = data.get('user_id')
		username = data.get('username')
		session_id = request.sid

		print(f"[WS] User {username} (ID: {user_id}) joining room {room_id}")

		result = room_manager.join_room(room_id, user_id, username, session_id)
		if result and 'error' in result:
			print(f"[WS] Join error: {result['error']}")
			emit('error', result)
			return

		join_room(room_id)
		print(f"[WS] User joined successfully. Room now has {len(result['users'])} users")

		# Send full room state to the user who just joined
		emit('room_state', result, to=request.sid)

		# Notify everyone else in the room
		emit('user_joined', {
			'user_id': user_id,
			'username': username,
			'users': result['users']
		}, to=room_id, skip_sid=request.sid)
	except Exception as e:
		print(f"[WS] Join error: {e}")
		emit('error', {'error': str(e)})

@socketio.on('leave_room')
def handle_leave_room():
	try:
		session_id = request.sid
		room_id = room_manager.get_room_by_session(session_id)

		if room_id:
			# Get user info and old host before leaving
			room_state = room_manager.get_room_state(room_id)
			user_info = None
			old_host_id = room_state['host_user_id'] if room_state else None
			leaving_user_was_host = False

			if room_state:
				for user in room_state['users']:
					if any(u.session_id == session_id for u in room_manager.rooms[room_id].users.values() if u.user_id == user['user_id']):
						user_info = user
						leaving_user_was_host = user.get('is_host', False)
						break

			deleted_room_id = room_manager.leave_room(session_id)
			leave_room(room_id)

			if not deleted_room_id:
				# Room still exists, notify others
				new_state = room_manager.get_room_state(room_id)
				new_host_id = new_state['host_user_id'] if new_state else None

				# Check if host changed (automatic transfer)
				if leaving_user_was_host and new_host_id != old_host_id:
					print(f"[WS] Host automatically transferred from {old_host_id} to {new_host_id}")
					emit('host_transferred', new_state, to=room_id)
				else:
					emit('user_left', {
						'user_id': user_info['user_id'] if user_info else None,
						'users': new_state['users'] if new_state else []
					}, to=room_id)
	except Exception as e:
		print(f"Error in leave_room: {e}")

@socketio.on('disconnect')
def handle_disconnect():
	handle_leave_room()

@socketio.on('update_video')
def handle_update_video(data):
	try:
		session_id = request.sid
		room_id = room_manager.get_room_by_session(session_id)

		if not room_id:
			emit('error', {'error': 'Not in a room'})
			return

		result = room_manager.update_video_state(
			room_id,
			session_id,
			source=data.get('source'),
			current_time=data.get('current_time'),
			is_playing=data.get('is_playing'),
			anime_id=data.get('anime_id'),
			anime_title=data.get('anime_title'),
			episode=data.get('episode'),
			season_url=data.get('season_url')
		)

		if result and 'error' in result:
			emit('error', result)
			return

		emit('video_state', result, room=room_id, include_self=False)
	except Exception as e:
		emit('error', {'error': str(e)})

@socketio.on('transfer_host')
def handle_transfer_host(data):
	try:
		session_id = request.sid
		room_id = room_manager.get_room_by_session(session_id)
		new_host_user_id = data.get('new_host_user_id')

		if not room_id:
			emit('error', {'error': 'Not in a room'})
			return

		result = room_manager.transfer_host(room_id, new_host_user_id, session_id)

		if result and 'error' in result:
			emit('error', result)
			return

		room_state = room_manager.get_room_state(room_id)
		emit('host_transferred', room_state, room=room_id)
	except Exception as e:
		emit('error', {'error': str(e)})

if __name__ == '__main__':
	import os
	debug_mode = os.environ.get('FLASK_DEBUG', '0') == '1'
	socketio.run(app, debug=debug_mode, port=8000, host='0.0.0.0')
