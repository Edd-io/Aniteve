import sqlite3
import threading
import ast
import os
import requests
from credientials import *
import time
import shutil

class Database:
	thread_backup = None
	threads_started = False

	def __init__(self):
		self.conn = sqlite3.connect('data/database.db', check_same_thread=False)
		self.create_table()
		if not self.threads_started:
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
			cursor.execute("SELECT COUNT(*) FROM anime_list WHERE url LIKE ?", ('%anime-sama.fr%',))
			count = cursor.fetchone()[0]
			if count > 0:
				cursor.execute(
					"UPDATE anime_list SET url = REPLACE(url, ?, ?) WHERE url LIKE ?",
					('anime-sama.fr', 'anime-sama.org', '%anime-sama.fr%')
				)
				self.conn.commit()
				print(f"Updated {count} anime_list URL(s) from 'anime-sama.fr' to 'anime-sama.org'")
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

	# status: 0 = watching, 1 = completed, 2 = new episode, 3 = new season
	def update_progress(self, anime):
		cursor = self.conn.cursor()
		isPresent = cursor.execute('''
			SELECT * FROM progress
			WHERE id_anime = ? AND id_user = ?
		''', (anime['id'], anime['idUser'])).fetchone()
		status = 0

		if (anime['progress'] >= 80):
			if (anime['episode'] < anime['totalEpisode']):
				anime['episode'] += 1
				anime['progress'] = 0
			else:
				isInVostfr = anime['allSeasons'][anime['seasonId']]['lang'].find('vostfr') != -1
				if (anime['seasonId'] + 1 < len(anime['allSeasons']) and (anime['allSeasons'][anime['seasonId'] + 1]['lang'].find('vostfr') != -1) == isInVostfr and anime['allSeasons'][anime['seasonId'] + 1]['lang'].find('saison') != -1):
					anime['seasonId'] += 1
					anime['episode'] = 1
					anime['progress'] = 0
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
			''', (anime['episode'], anime['allSeasons'][anime['seasonId']]['url'], anime['progress'], status, anime['allSeasons'][anime['seasonId']]['name'], anime['allSeasons'][anime['seasonId']]['lang'], anime['id'], anime['idUser']))
		else:
			cursor.execute('''
				INSERT INTO progress (id_anime, episode, season, progress, status, poster, id_user, season_name, language)
				VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (anime['id'], anime['episode'], anime['allSeasons'][anime['seasonId']]['url'], anime['progress'], status, anime['poster'], anime['idUser'], anime['allSeasons'][anime['seasonId']]['name'], anime['allSeasons'][anime['seasonId']]['lang']))
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
					
					if response.status_code == 204:
						print("Fichier envoyé avec succès !")
					else:
						print(f"Erreur lors de l'envoi : {response.status_code} - {response.text}")
			except Exception as e:
				message = f"Erreur lors de l'envoi : {e}"
				print(message)
				# Don't try to post error to webhook if webhook itself is the problem
				try:
					if webhook_url and webhook_url.startswith(('http://', 'https://')):
						requests.post(webhook_url, data={'content': message})
				except:
					pass  # Silently ignore if error notification fails
			time.sleep(604800)
