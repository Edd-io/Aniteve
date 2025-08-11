import requests
import string
import os
import m3u8
import asyncio
from flask import Response

class Downloader:
	onDownloading = False
	listAnime = []
	db = None

	def __init__(self, database):
		self.db = database
		pass

	def add(self, data):
		anime = {
			'episode': data['episode'],
			'link': data['src'].replace(data['serverUrl'], 'http://localhost:8000'),
			'name': self.__generate_filename(data['name'], data['episode'], data['season']),
			'episode': data['episode'],
			'season': data['season'],
			'poster': data['poster'],
		}
		if (self.db.get_download_by_name(anime['name'])):
			print("Already added " + anime['name'])
			return
		print("Adding " + anime['name'])
		self.db.insert_download(anime['name'], anime['poster'])
		if (data['src'].find('.mp4') != -1):
			anime['type'] = 'mp4'
		elif (data['src'].find('.m3u8') != -1):
			anime['type'] = 'm3u8'
		else:
			anime['type'] = 'unknown'
		anime['progress'] = 0
		anime['failed'] = False
		anime['finished'] = False
		anime['waiting'] = True
		self.listAnime.append(anime)
		if (self.onDownloading == False):
			asyncio.create_task(self.download_list())
		
	async def download_list(self):
		self.onDownloading = True
		os.system('mkdir -p ./downloaded')
		print('Start downloading')
		for i, anime in enumerate(self.listAnime):
			if (anime['finished'] or anime['failed']):
				continue
			anime['waiting'] = False
			print('Downloading ' + anime['name'])
			if (anime['type'] == 'mp4'):
				self.__mp4(anime['link'], anime['name'], i)
			elif (anime['type'] == 'm3u8'):
				self.__m3u8(anime['link'], anime['name'], i)
			else:
				print('Unknown type for ' + anime['name'])
		self.onDownloading = False
	
	def __mp4(self, src, name, index):
		response = requests.head(src, headers={'Range': 'bytes=0-'})
		total_size = int(response.headers.get('Content-Range').split('/')[1])
		range_start = 0
		chunk_size = 7 * 1024 * 1024

		with open(f'./downloaded/{name}', "wb") as f:
			while range_start < total_size:
				headers = {"Range": f"bytes={range_start}-{min(range_start + chunk_size - 1, total_size - 1)}"}
				response = requests.get(src, headers=headers, stream=True, timeout=50)
				if response.status_code in (200, 206):
					content_range = response.headers.get('Content-Range')
					if content_range:
						actual_start = int(content_range.split(' ')[1].split('-')[0])
						if actual_start != range_start:
							raise ValueError("Server doesn't support range requests")
					f.write(response.content)
					range_start += len(response.content)
					self.listAnime[index]['progress'] = round(range_start / total_size * 100, 2)
					print(f'{name}: {self.listAnime[index]["progress"]}%')
				else:
					self.listAnime[index]['failed'] = True
					self.db.update_download(name, failed=True)
					break
		if not self.listAnime[index]['failed']:
			self.db.update_download(name, finished=True)
			self.listAnime[index]['finished'] = True
		print(f'{name}: Finished')

	def __m3u8(self, src, name, index):
		playlists = m3u8.load(src)
		best_playlist = max(
			playlists.playlists,
			key=lambda p: (p.stream_info.resolution or (0, 0), p.stream_info.bandwidth)
		)
		code = os.system(f'ffmpeg -i {best_playlist.uri} -c copy ./downloaded/{name}')
		if code == 0:
			self.db.update_download(name, finished=True)
			self.listAnime[index]['finished'] = True
		else:
			self.db.update_download(name, failed=True)
			self.listAnime[index]['failed'] = True
		print(f'{name}: Finished')

	def __generate_filename(self, name, episode, season):
		valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

		name = ''.join(c for c in name if c in valid_chars)
		lang = season.split('/')[1]
		season = ''.join(c for c in season.split('/')[0] if c in valid_chars)
		episode = ''.join(c for c in str(episode) if c in valid_chars)
		return (f'{name}-{season}-EP{episode}-{lang.upper()}.mp4'.replace(' ', '_'))
	
	def get_status(self):
		status = []
		data_db = self.db.get_download()
		for anime in data_db:
			anime_dict = None
			for item in self.listAnime:
				if item['name'] == anime[1]:
					anime_dict = item
					break
			progress = -1
			waiting = False
			if anime_dict:
				if anime_dict['waiting']:
					waiting = True
				if (anime_dict['type'] == 'mp4'):
					progress = anime_dict['progress']
				else:
					progress = -1
			status.append({
				'id': anime[0],
				'name': anime[1],
				'failed': anime[2],
				'finished': anime[3],
				'poster': anime[4],
				'progress': progress,
				'waiting': waiting,
			})
		return (status)
	
	def delete(self, id):
		self.db.delete_download(id)
		for i, anime in enumerate(self.listAnime):
			if anime['id'] == id:
				self.listAnime.pop(i)
				break
		return ({'status': 'success'})
	
	def download(self, name):
		import re
		if not re.fullmatch(r'[\w\-.() ]+', name):
			return ({'error': 'Invalid name'})
		if name.startswith('.') or '/' in name or '\\' in name or '..' in name:
			return ({'error': 'Invalid name'})
		file_path = os.path.join('./downloaded', name)
		if os.path.exists(file_path):
			return (Response(
				open(file_path, 'rb'),
				mimetype='application/octet-stream',
				headers={
					"Content-Disposition": f"attachment;filename={name}",
					"Content-Length": str(os.path.getsize(file_path))
				}
			))
		else:
			return ({'error': 'File not found'})