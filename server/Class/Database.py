import sqlite3
from time import sleep

class Database:
	def __init__(self):
		self.conn = sqlite3.connect('database.db', check_same_thread=False)
		self.create_table()

	def create_table(self):
		cursor = self.conn.cursor()
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
				id_anime INTEGER,
				episode INTEGER,
				season INTEGER,
				progress FLOAT,
				status INTEGER,
				see_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				FOREIGN KEY (id_anime) REFERENCES anime_list (id) ON DELETE CASCADE
			)''')
		self.conn.commit()
		cursor.close()
		print('Table created')

	def insert_anime(self, anime):
		cursor = self.conn.cursor()
		isPresent = cursor.execute('''
			SELECT * FROM anime_list
			WHERE title = ?''', (anime['title'],)).fetchone()
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

	# status: 0 = watching, 1 = completed
	def update_progress(self, anime):
		cursor = self.conn.cursor()
		isPresent = cursor.execute('''
			SELECT * FROM progress
			WHERE id_anime = ?''', (anime['id'],)).fetchone()
		status = 0

		if (anime['progress'] >= 80):
			if (anime['episode'] < anime['totalEpisode']):
				anime['episode'] += 1
				anime['progress'] = 0
			else:
				isInVostfr = anime['allSeasons'][anime['seasonId']].find('vostfr') != -1
				if (anime['seasonId'] + 1 < len(anime['allSeasons']) and (anime['allSeasons'][anime['seasonId'] + 1].find('vostfr') != -1) == isInVostfr):
					anime['seasonId'] += 1
					anime['episode'] = 1
				else:
					status = 1
					anime['progress'] = 100
		if isPresent:
			print('Updating id ' + str(anime['id']))
			cursor.execute('''
				UPDATE progress
				SET episode = ?,
					season = ?,
					progress = ?,
					status = ?
				WHERE id_anime = ?''', (anime['episode'], anime['allSeasons'][anime['seasonId']], anime['progress'], status, anime['id']))
		else:
			print('Inserting id ' + str(anime['id']))
			cursor.execute('''
				INSERT INTO progress (id_anime, episode, season, progress, status)
				VALUES (?, ?, ?, ?, ?)''', (anime['id'], anime['episode'], anime['allSeasons'][anime['seasonId']], anime['progress'], status))
		self.conn.commit()
		cursor.close()

	def get_progress(self, anime):
		cursor = self.conn.cursor()
		progress = cursor.execute('''
			SELECT * FROM progress
			WHERE id_anime = ?''', (anime['id'],)).fetchone()
		cursor.close()
		if not progress:
			return ({'find': False})
		dataProgress = {
			'find': True,
			'episode': progress[2],
			'season': progress[3],
			'progress': progress[4],
			'status': progress[5],		
		}
		return (dataProgress)
	
	def get_all_progress(self):
		cursor = self.conn.cursor()
		progress = cursor.execute('''
			SELECT * FROM progress''').fetchall()
		cursor.close()
		return (progress)