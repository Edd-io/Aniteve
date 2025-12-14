import sqlite3
import threading
import ast
import os
import requests
from credientials import *
import time
import shutil
from Class.WorkerLock import WorkerLock

class Database:
	thread_backup = None
	threads_started = False
	backup_lock = None

	def __init__(self):
		self.conn = sqlite3.connect('data/database.db', check_same_thread=False)
		self.create_table()
		
		if not self.threads_started:
			self.backup_lock = WorkerLock('backup')
			if self.backup_lock.acquire():
				self.thread_backup = threading.Thread(target=self.create_backup)
				self.thread_backup.start()
				self.threads_started = True

	def create_table(self):
		cursor = self.conn.cursor()
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS users (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				username TEXT NOT NULL
			)''')
		self.conn.commit()
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS anime_list (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				title TEXT NOT NULL,
				alternative_title TEXT,
				genre TEXT,
				url TEXT,
				img TEXT
			)''')
		self.conn.commit()
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS progress (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				id_user INTEGER,
				id_anime INTEGER,
				episode INTEGER,
				season TEXT,
				progress FLOAT,
				status INTEGER,
				see_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				poster TEXT,
				FOREIGN KEY (id_anime) REFERENCES anime_list (id) ON DELETE CASCADE,
				FOREIGN KEY (id_user) REFERENCES users (id) ON DELETE CASCADE
			)''')
		self.conn.commit()
		cursor.execute('''
			CREATE TABLE IF NOT EXISTS download (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT,
				failed BOOLEAN,
				finished BOOLEAN,
				poster TEXT
			)''')
		self.conn.commit()
		self.update(cursor)
		cursor.close()
		self.init_download()
		print('Table created')

	def update(self, cursor):
		cursor.execute("PRAGMA table_info(progress)")
		columns = [col[1] for col in cursor.fetchall()]
		if "season_name" not in columns:
			cursor.execute('''
				ALTER TABLE progress ADD COLUMN season_name TEXT
			''')
			self.conn.commit()
		if "language" not in columns:
			cursor.execute('''
				ALTER TABLE progress ADD COLUMN language TEXT
			''')
			self.conn.commit()
		try:
			cursor = self.conn.cursor()
			cursor.execute("SELECT COUNT(*) FROM anime_list WHERE url LIKE ? OR url LIKE ?", ('%anime-sama.fr%', '%anime-sama.org%'))
			count = cursor.fetchone()[0]
			if count > 0:
				cursor.execute(
					"UPDATE anime_list SET url = REPLACE(url, ?, ?) WHERE url LIKE ?",
					('anime-sama.fr', 'anime-sama.eu', '%anime-sama.fr%')
				)
				cursor.execute(
					"UPDATE anime_list SET url = REPLACE(url, ?, ?) WHERE url LIKE ?",
					('anime-sama.org', 'anime-sama.eu', '%anime-sama.org%')
				)
				self.conn.commit()
				print(f"Updated {count} anime_list URL(s) to 'anime-sama.eu'")
		except Exception as e:
			print(f"Error updating anime_list URLs: {e}")
		finally:
			try:
				cursor.close()
			except:
				pass
		

	def insert_user(self, username):
		cursor = self.conn.cursor()
		cursor.execute('''
			INSERT INTO users (username)
			VALUES (?)''', (username,))
		self.conn.commit()
		cursor.close()

	def get_users(self):
		data = []
		cursor = self.conn.cursor()
		users = cursor.execute('''
			SELECT * FROM users
		''').fetchall()
		cursor.close()
		for user in users:
			data.append({
				'id': user[0],
				'name': user[1]
			})
		return (data)
	
	def get_name_by_id(self, id):
		cursor = self.conn.cursor()
		user = cursor.execute('''
			SELECT * FROM users
			WHERE id = ?''', (id,)).fetchone()
		cursor.close()
		data = {
			'id': user[0],
			'name': user[1]
		}
		return (data)

	def insert_anime(self, anime):
		if anime['url'] and anime['url'][-1] == '/':
			anime['url'] = anime['url'][:-1]
		cursor = self.conn.cursor()
		isPresent = cursor.execute('''
			SELECT * FROM anime_list
			WHERE url = ?''', (anime['url'],)).fetchone()
		if isPresent:
			return
		else:
			print('Inserting ' + anime['title'])
		cursor.execute('''
			INSERT INTO anime_list (title, alternative_title, genre, url, img)
			VALUES (?, ?, ?, ?, ?)''', (anime['title'], anime['alternative_title'], str(anime['genre']), anime['url'], anime['img']))
		self.conn.commit()
		cursor.close()

	def get_all_anime(self):
		cursor = self.conn.cursor()
		anime_list = cursor.execute('''
			SELECT * FROM anime_list
			ORDER BY title''').fetchall()
		cursor.close()
		return (anime_list)

	def get_random_anime(self, limit=10):
		cursor = self.conn.cursor()
		anime_list = cursor.execute('''
			SELECT * FROM anime_list
			ORDER BY RANDOM()
			LIMIT ?''', (limit,)).fetchall()
		cursor.close()
		return (anime_list)

	def get_anime_by_genre(self, genre, limit=10):
		cursor = self.conn.cursor()
		anime_list = cursor.execute('''
			SELECT * FROM anime_list
			WHERE genre LIKE ?
			ORDER BY RANDOM()
			LIMIT ?''', (f'%{genre}%', limit)).fetchall()
		cursor.close()
		return (anime_list)

	def get_all_genres(self):
		cursor = self.conn.cursor()
		anime_list = cursor.execute('''
			SELECT genre FROM anime_list''').fetchall()
		cursor.close()
		print(f"[DEBUG] Found {len(anime_list)} anime for genres")
		genres = set()
		for anime in anime_list:
			try:
				raw_genre = anime[0]
				if raw_genre:
					if raw_genre.startswith('['):
						genre_list = ast.literal_eval(raw_genre)
					else:
						genre_list = [g.strip() for g in raw_genre.split(',')]

					for genre in genre_list:
						if genre and genre.strip():
							main_genre = genre.strip().split(' - ')[0].strip()
							if main_genre:
								genres.add(main_genre)
			except Exception as e:
				print(f"[DEBUG] Error parsing genre '{anime[0]}': {e}")
		print(f"[DEBUG] Returning {len(genres)} genres: {sorted(list(genres))[:5]}...")
		return sorted(list(genres))

	def get_main_genres(self):
		main_genres = [
			'Action', 'Aventure', 'Comédie', 'Drame', 'Fantasy',
			'Horreur', 'Romance', 'Sci-Fi', 'Shonen', 'Seinen',
			'Shojo', 'Sport', 'Thriller', 'Mystère', 'Surnaturel',
			'Slice of Life', 'Mecha', 'Musique', 'Psychologique', 'Historique'
		]

		all_genres = self.get_all_genres()
		available_genres = []

		for main in main_genres:
			for genre in all_genres:
				if genre.lower() == main.lower():
					available_genres.append(genre)
					break

		return available_genres

	def get_recent_anime(self, limit=10):
		cursor = self.conn.cursor()
		anime_list = cursor.execute('''
			SELECT * FROM anime_list
			ORDER BY id DESC
			LIMIT ?''', (limit,)).fetchall()
		cursor.close()
		return (anime_list)

	def search_anime(self, query, limit=8):
		cursor = self.conn.cursor()
		search_pattern = f'%{query}%'
		anime_list = cursor.execute('''
			SELECT * FROM anime_list
			WHERE title LIKE ? OR alternative_title LIKE ?
			ORDER BY
				CASE
					WHEN title LIKE ? THEN 0
					WHEN title LIKE ? THEN 1
					ELSE 2
				END,
				title
			LIMIT ?''', (search_pattern, search_pattern, f'{query}%', search_pattern, limit)).fetchall()
		cursor.close()
		return (anime_list)

	def get_user_stats(self, id_user):
		cursor = self.conn.cursor()
		stats = {}

		cursor.execute('''
			SELECT COUNT(DISTINCT id_anime) FROM progress WHERE id_user = ?
		''', (id_user,))
		stats['total_anime'] = cursor.fetchone()[0] or 0

		cursor.execute('''
			SELECT COUNT(*) FROM progress WHERE id_user = ? AND status = 1
		''', (id_user,))
		stats['anime_completed'] = cursor.fetchone()[0] or 0

		cursor.execute('''
			SELECT COUNT(*) FROM progress WHERE id_user = ? AND (status = 0 OR status = 2)
		''', (id_user,))
		stats['anime_in_progress'] = cursor.fetchone()[0] or 0

		cursor.execute('''
			SELECT COUNT(*) FROM progress WHERE id_user = ? AND status = 3
		''', (id_user,))
		stats['anime_new_season'] = cursor.fetchone()[0] or 0

		cursor.execute('''
			SELECT SUM(episode) FROM progress WHERE id_user = ?
		''', (id_user,))
		stats['total_episodes'] = cursor.fetchone()[0] or 0

		stats['total_watch_time_hours'] = round((stats['total_episodes'] * 24) / 60, 1)

		cursor.execute('''
			SELECT COUNT(*) FROM progress WHERE id_user = ? AND language LIKE '%vostfr%'
		''', (id_user,))
		stats['vostfr_count'] = cursor.fetchone()[0] or 0

		cursor.execute('''
			SELECT COUNT(*) FROM progress WHERE id_user = ? AND language LIKE '%vf%' AND language NOT LIKE '%vostfr%'
		''', (id_user,))
		stats['vf_count'] = cursor.fetchone()[0] or 0

		cursor.execute('''
			SELECT anime_list.genre FROM progress
			JOIN anime_list ON progress.id_anime = anime_list.id
			WHERE progress.id_user = ?
		''', (id_user,))
		genre_rows = cursor.fetchall()
		genre_count = {}
		for row in genre_rows:
			try:
				genres = ast.literal_eval(row[0]) if row[0] else []
				for genre in genres:
					main_genre = genre.split(' - ')[0].strip()
					if main_genre and main_genre.lower() not in ['vostfr', 'vf', 'anime', 'scans', 'film', '-']:
						genre_count[main_genre] = genre_count.get(main_genre, 0) + 1
			except:
				pass
		sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:5]
		stats['top_genres'] = [{'name': g[0], 'count': g[1]} for g in sorted_genres]

		cursor.execute('''
			SELECT strftime('%w', see_date) as day, COUNT(*) as count
			FROM progress
			WHERE id_user = ?
			GROUP BY day
			ORDER BY day
		''', (id_user,))
		day_activity = cursor.fetchall()
		days = ['Dim', 'Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam']
		stats['activity_by_day'] = [{'day': days[int(d[0])], 'count': d[1]} for d in day_activity]

		cursor.execute('''
			SELECT strftime('%Y-%m', see_date) as month, COUNT(*) as count
			FROM progress
			WHERE id_user = ? AND see_date >= date('now', '-6 months')
			GROUP BY month
			ORDER BY month
		''', (id_user,))
		month_activity = cursor.fetchall()
		stats['activity_by_month'] = [{'month': m[0], 'count': m[1]} for m in month_activity]

		cursor.execute('''
			SELECT anime_list.title, anime_list.img, progress.episode, progress.season_name
			FROM progress
			JOIN anime_list ON progress.id_anime = anime_list.id
			WHERE progress.id_user = ?
			ORDER BY progress.episode DESC
			LIMIT 5
		''', (id_user,))
		top_anime = cursor.fetchall()
		stats['top_anime'] = [{'title': a[0], 'img': a[1], 'episodes': a[2], 'season': a[3]} for a in top_anime]

		cursor.execute('''
			SELECT anime_list.title, anime_list.img, progress.episode, progress.season_name,
				   datetime(progress.see_date, 'localtime') as local_date
			FROM progress
			JOIN anime_list ON progress.id_anime = anime_list.id
			WHERE progress.id_user = ?
			ORDER BY progress.see_date DESC
			LIMIT 10
		''', (id_user,))
		recent = cursor.fetchall()
		stats['recent_activity'] = [{'title': r[0], 'img': r[1], 'episode': r[2], 'season': r[3], 'date': r[4]} for r in recent]

		if stats['total_anime'] > 0:
			stats['completion_rate'] = round((stats['anime_completed'] / stats['total_anime']) * 100, 1)
		else:
			stats['completion_rate'] = 0

		if stats['total_anime'] > 0:
			stats['avg_episodes_per_anime'] = round(stats['total_episodes'] / stats['total_anime'], 1)
		else:
			stats['avg_episodes_per_anime'] = 0

		cursor.execute('''
			SELECT MIN(see_date), MAX(see_date) FROM progress WHERE id_user = ?
		''', (id_user,))
		dates = cursor.fetchone()
		stats['first_watch'] = dates[0] if dates[0] else None
		stats['last_watch'] = dates[1] if dates[1] else None

		cursor.close()
		return stats

	# status: 0 = watching, 1 = completed, 2 = new episode, 3 = new season
	def update_progress(self, anime):
		cursor = self.conn.cursor()
		isPresent = cursor.execute('''
			SELECT * FROM progress
			WHERE id_anime = ? AND id_user = ?
		''', (anime['id'], anime['idUser'])).fetchone()
		status = 0

		# Get current season info with defaults
		current_season = anime['allSeasons'][anime['seasonId']] if anime['seasonId'] < len(anime['allSeasons']) else {}
		season_url = current_season.get('url', '')
		season_name = current_season.get('name', 'Saison 1')
		season_lang = current_season.get('lang', 'vostfr')

		if (anime['progress'] >= 80):
			if (anime['episode'] < anime['totalEpisode']):
				anime['episode'] += 1
				anime['progress'] = 0
			else:
				isInVostfr = season_lang.find('vostfr') != -1
				next_season_idx = anime['seasonId'] + 1
				if next_season_idx < len(anime['allSeasons']):
					next_season = anime['allSeasons'][next_season_idx]
					next_lang = next_season.get('lang', '')
					if (next_lang.find('vostfr') != -1) == isInVostfr and next_lang.find('saison') != -1:
						anime['seasonId'] = next_season_idx
						anime['episode'] = 1
						anime['progress'] = 0
						season_url = next_season.get('url', '')
						season_name = next_season.get('name', 'Saison 1')
						season_lang = next_season.get('lang', 'vostfr')
					else:
						status = 1
						anime['progress'] = 100
				else:
					status = 1
					anime['progress'] = 100

		if isPresent:
			cursor.execute('''
				UPDATE progress
				SET episode = ?,
					season = ?,
					progress = ?,
					status = ?,
					see_date = CURRENT_TIMESTAMP,
					season_name = ?,
					language = ?
				WHERE id_anime = ? AND id_user = ?
			''', (anime['episode'], season_url, anime['progress'], status, season_name, season_lang, anime['id'], anime['idUser']))
		else:
			cursor.execute('''
				INSERT INTO progress (id_anime, episode, season, progress, status, poster, id_user, season_name, language)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (anime['id'], anime['episode'], season_url, anime['progress'], status, anime['poster'], anime['idUser'], season_name, season_lang))
		self.conn.commit()
		cursor.close()

	def get_progress(self, anime):
		cursor = self.conn.cursor()
		progress = cursor.execute('''
			SELECT * FROM progress
			WHERE id_anime = ? AND id_user = ?
		''', (anime['id'], anime['idUser'])).fetchone()
		cursor.close()
		if not progress:
			return ({'find': False})
		dataProgress = {
			'find': True,
			'episode': progress[3],
			'season': progress[4],
			'progress': progress[5],
			'status': progress[6],
			'season_name': progress[9] if len(progress) > 9 else None,
			'lang': progress[10] if len(progress) > 10 else None,
		}
		return (dataProgress)
	
	def get_all_progress(self, id_user):
		cursor = self.conn.cursor()
		progress = cursor.execute('''
			SELECT progress.*, datetime(progress.see_date, 'localtime') AS local_see_date, anime_list.*
			FROM progress
			JOIN anime_list ON progress.id_anime = anime_list.id
			WHERE progress.id_user = ?
			ORDER BY progress.see_date DESC
		''', (id_user,)).fetchall()
		cursor.close()
		for i in range(len(progress)):
			progress[i] = {
				"anime": {
					"title": progress[i][13],
					"alternative_title": progress[i][14],
					"genre": ast.literal_eval(progress[i][15]),
					"id": progress[i][12],
					"img": progress[i][17],
					"url": progress[i][16],
				},
				"episode": progress[i][3],
				"season": progress[i][4],
				"progress": progress[i][5],
				"completed": progress[i][6],
				"poster": progress[i][8],
				"season_name": progress[i][9],
				"lang": progress[i][10],
			}
		return (progress)

		
	def update_anime_status(self, list_anime):
		cursor = self.conn.cursor()
		for anime in list_anime:
			anime_id = cursor.execute("""
				SELECT id
				FROM anime_list
				WHERE url = ?
			""", (anime['url'],)).fetchone()
			if not anime_id:
				continue
			sawInVOSTFR = cursor.execute("""
				SELECT season
				FROM progress
				WHERE id_anime = ?
			""", (anime_id[0],)).fetchone()
			if sawInVOSTFR:
				sawInVOSTFR = sawInVOSTFR[0].find('vostfr') != -1
			else:
				continue
			if sawInVOSTFR == (anime['season'].find('vostfr') != -1):
				cursor.execute("""
					UPDATE progress
					SET status = 2, episode = episode + 1, progress = 0, see_date = CURRENT_TIMESTAMP
					WHERE id_anime = ? AND status = 1 AND season = ? AND episode < ?
				""", (anime_id[0], anime['season'], anime['episode']))
				cursor.execute("""
					UPDATE progress
					SET status = 3, episode = 1, progress = 0, season = ?, see_date = CURRENT_TIMESTAMP
					WHERE id_anime = ? AND status = 1 AND season != ?
				""", (anime['season'], anime_id[0], anime['season']))
				print('Maybe an update for ' + anime['title'])
		self.conn.commit()
		cursor.close()

	def delete_progress(self, id_anime, id_user):
		cursor = self.conn.cursor()
		data = cursor.execute('''
			DELETE FROM progress
			WHERE id_user = ? AND id_anime = ?
		''', (id_user, id_anime, ))

	def init_download(self):
		cursor = self.conn.cursor()
		data = cursor.execute('''
			SELECT * FROM download
		''').fetchall()
		for download in data:
			print('Checking ' + download[1])
			if (download[2] == False and download[3] == False):
				cursor.execute('''
					UPDATE download
					SET failed = 1
					WHERE name = ?''', (download[1],))
		self.conn.commit()
		cursor.close()

	def insert_download(self, name, poster):
		cursor = self.conn.cursor()
		cursor.execute('''
			INSERT INTO download (name, failed, finished, poster)
			VALUES (?, ?, ?, ?)''', (name, False, False, poster))
		self.conn.commit()
		cursor.close()
	
	def get_download(self):
		cursor = self.conn.cursor()
		downloads = cursor.execute('''
			SELECT * FROM download
		''').fetchall()
		cursor.close()
		return (downloads)
	
	def get_download_by_name(self, name):
		cursor = self.conn.cursor()
		download = cursor.execute('''
			SELECT * FROM download
			WHERE name = ?''', (name,)).fetchone()
		cursor.close()
		return (download)
	
	def update_download(self, name, failed=False, finished=False):
		cursor = self.conn.cursor()
		cursor.execute('''
			UPDATE download
			SET failed = ?,
				finished = ?
			WHERE name = ?''', (failed, finished, name))
		self.conn.commit()
		cursor.close()

	def delete_download(self, id):
		cursor = self.conn.cursor()
		download = cursor.execute('''
			SELECT * FROM download
			WHERE id = ?''', (id,)).fetchone()
		if download:
			name = download[1]
			if any(x in name for x in ('..', '/', '\\')):
				cursor.close()
				raise ValueError('Invalid filename')
			file_path = os.path.join('./downloaded', name)
			if os.path.isdir(file_path):
				shutil.rmtree(file_path)
			elif os.path.isfile(file_path):
				os.remove(file_path)
		cursor.execute('''
			DELETE FROM download
			WHERE id = ?''', (id,))
		self.conn.commit()
		cursor.close()

	def create_backup(self):
		try:
			if not webhook_url or webhook_url == '' or not webhook_url.startswith(('http://', 'https://')):
				print('Webhook URL not set or invalid, backup disabled')
				return
		except:
			print('Webhook URL not set, backup disabled')
			return
		time.sleep(10)
		while (1):
			try:
				with open('data/database.db', 'rb') as file:
					files = {'file': ("database.db", file)}
					data = {'content': 'Nouvelle sauvegarde de la base de données'}
					
					response = requests.post(webhook_url, data=data, files=files)
			except Exception as e:
				message = f"Erreur lors de l'envoi : {e}"
				print(message)
				try:
					if webhook_url and webhook_url.startswith(('http://', 'https://')):
						requests.post(webhook_url, data={'content': message})
				except:
					pass
			time.sleep(604800)
