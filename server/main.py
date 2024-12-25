from flask import Flask, request
from Class.Database import Database
from Class.AnimeSama import AnimeSama
from Class.Proxy import Proxy

app = Flask(__name__)

@app.route('/')
def hello():
	return 'Hello, World!'

@app.route('/api/srcFile')
def proxy():
	url = 'https:/' + request.url.split('?', 1)[1]
	Proxy.test()
	return "Proxy"

@app.route('/api/video')
def video():
	url = 'https://' + request.url.split('?', 1)[1]
	return Proxy.sibnet(url)

if __name__ == '__main__':
	db = Database()
	site = AnimeSama(db)
	# season = site.get_anime_season({'url': 'https://anime-sama.fr/catalogue/one-piece/'})
	# site.get_anime_episodes({'url': 'https://anime-sama.fr/catalogue/one-piece/'}, season[0])
	# app.run(debug=False, port=8080)
	site.get_source_file('https://vidmoly.to/embed-ze0dv8b88jpo.html')