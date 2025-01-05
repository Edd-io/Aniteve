import sqlite3
import ast

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
				season TEXT,
				progress FLOAT,
				status INTEGER,
				see_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				poster TEXT,
				FOREIGN KEY (id_anime) REFERENCES anime_list (id) ON DELETE CASCADE
			)''')
		self.conn.commit()
		cursor.close()
		print('Table created')

	def insert_anime(self, anime):
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
			WHERE id_anime = ?''', (anime['id'],)).fetchone()
		status = 0

		if (anime['progress'] >= 80):
			if (anime['episode'] < anime['totalEpisode']):
				anime['episode'] += 1
				anime['progress'] = 0
			else:
				isInVostfr = anime['allSeasons'][anime['seasonId']].find('vostfr') != -1
				if (anime['seasonId'] + 1 < len(anime['allSeasons']) and (anime['allSeasons'][anime['seasonId'] + 1].find('vostfr') != -1) == isInVostfr and anime['allSeasons'][anime['seasonId'] + 1].find('saison') != -1):
					anime['seasonId'] += 1
					anime['episode'] = 1
					anime['progress'] = 0
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
				INSERT INTO progress (id_anime, episode, season, progress, status, poster)
				VALUES (?, ?, ?, ?, ?, ?)''', (anime['id'], anime['episode'], anime['allSeasons'][anime['seasonId']], anime['progress'], status, anime['poster']))
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
			SELECT progress.*, datetime(progress.see_date, 'localtime') AS local_see_date, anime_list.*
			FROM progress
			JOIN anime_list ON progress.id_anime = anime_list.id
			ORDER BY progress.see_date DESC
		''').fetchall()
		cursor.close()
		for i in range(len(progress)):
			progress[i] = {
				"anime": {
					"title": progress[i][10],
					"alternative_title": progress[i][11],
					"genre": ast.literal_eval(progress[i][12]),
					"id": progress[i][1],
					"img": progress[i][14],
					"url": progress[i][13],
				},
				"episode": progress[i][2],
				"season": progress[i][3],
				"progress": progress[i][4],
				"completed": progress[i][5],
				"poster": progress[i][7],
			}
		return (progress)

		
	def update_anime_status(self, list_anime):
		cursor = self.conn.cursor()
		for anime in list_anime:
			anime_id = cursor.execute("""--sql
				SELECT id
				FROM anime_list
				WHERE url = ?
			""", (anime['url'],)).fetchone()
			if not anime_id:
				continue
			sawInVOSTFR = cursor.execute("""--sql
				SELECT season
				FROM progress
				WHERE id_anime = ?
			""", (anime_id[0],)).fetchone()
			if sawInVOSTFR:
				sawInVOSTFR = sawInVOSTFR[0].find('vostfr') != -1
			else:
				continue
			if sawInVOSTFR == (anime['season'].find('vostfr') != -1):
				cursor.execute("""--sql
					UPDATE progress
					SET status = 2, episode = episode + 1, progress = 0
					WHERE id_anime = ? AND status = 1 AND season = ?
				""", (anime_id[0], anime['season']))
				cursor.execute("""--sql
					UPDATE progress
					SET status = 3, episode = 1, progress = 0, season = ?
					WHERE id_anime = ? AND status = 1 AND season != ?
				""", (anime['season'], anime_id[0], anime['season']))
				print('Maybe an update for ' + anime['title'])
		self.conn.commit()
		cursor.close()