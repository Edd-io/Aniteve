import requests
import string
import os

class Downloader:
	listAnime = []

	def __init__(self):
		pass

	def add(self, data):
		anime = {
			'episode': data['episode'],
			'link': data['src'].replace(data['serverUrl'], 'http://localhost:8080'),
			'name': self.__generate_filename(data['name'], data['episode'], data['season'])
		}
		if (data['src'].find('.mp4') != -1):
			anime['type'] = 'mp4'
		elif (data['src'].find('.m3u8') != -1):
			anime['type'] = 'm3u8'
		else:
			anime['type'] = 'unknown'
		print('New anime added: ', end='')
		self.listAnime.append(anime)
		self.download()
		
	def download(self):
		os.system('mkdir -p ./downloaded')
		for i, anime in enumerate(self.listAnime):
			if (anime['type'] == 'mp4'):
				self.__mp4(anime['link'], anime['name'], i)
			elif (anime['type'] == 'm3u8'):
				self.m3u8(anime['link'])
			else:
				print('Unknown type for ' + anime['name'])
	
	def __mp4(self, src, name, index):
		response = requests.get(src, stream=True, headers={'Range': 'bytes=0-'})
		total_size = int(str(response.headers.get('Content-Range')).split('/')[1])
		range_start = 0
		chunk_size = 1024 * 1024

		with open(name, "wb") as f:
			while True:
				headers = {"Range": f"bytes={range_start}-{range_start + chunk_size - 1}"}
				response = requests.get(src, headers=headers, stream=True)
				if (response.status_code in (200, 206)):
					f.write(response.content)
					range_start += chunk_size
					self.listAnime[index]['progress'] = round(range_start / total_size * 100, 2)
					print(f'{name}: {self.listAnime[index]["progress"]}%')
				else:
					self.listAnime[index]['failed'] = True
					break
				if range_start >= total_size:
					self.listAnime[index]['finished'] = True
					break

	def __generate_filename(self, name, episode, season):
		valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

		name = ''.join(c for c in name if c in valid_chars)
		lang = season.split('/')[1]
		season = ''.join(c for c in season.split('/')[0] if c in valid_chars)
		episode = ''.join(c for c in str(episode) if c in valid_chars)
		return (f'{name}-{season}-EP{episode}-{lang.upper()}.mp4'.replace(' ', '_'))