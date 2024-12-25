import sqlite3
from time import sleep

class Database:
	def __init__(self):
		self.conn = sqlite3.connect('database.db')
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
