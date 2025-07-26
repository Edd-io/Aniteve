import requests
from flask import Response, request

class Proxy:
	@staticmethod
	def sibnet(url):
		referer = url.split('|')
		url = referer[0]
		headers = {
			'host': 'video.sibnet.ru',
			'referer': 'https://video.sibnet.ru',
			'sec-fetch-dest': 'video',
			'Referer': referer[1],
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
		}
		if 'Range' in request.headers:
			headers['Range'] = request.headers['Range']
		response = requests.get(url, headers=headers, stream=True, timeout=10)
		return Response(
			response.iter_content(chunk_size=1024),
			content_type=response.headers.get('Content-Type', 'application/octet-stream'),
			status=response.status_code,
			headers={
				**{k: v for k, v in response.headers.items() if k.lower() in {'content-type', 'content-range', 'accept-ranges'}},
				'Access-Control-Allow-Origin': '*'
			}
		)
	
	@staticmethod
	def vidmoly(url):
		host = url.split('/')[2]
		
		if 'vidmoly.to' in host:
			referer = 'https://vidmoly.to'
		else:
			referer = 'https://vidmoly.net'
			
		if (url.find('.m3u8') != -1):
			headers = {
				'host': host,
				'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
				'referer': referer,
			}
			try:
				response = requests.get(url, headers=headers, timeout=30)
				data = response.text.replace('https://', '/api/video?')
				return (Response(
					headers={
						'Access-Control-Allow-Origin': '*', 
				 		'Content-Type': 'application/vnd.apple.mpegurl'
					},
					response=data,
				))
			except Exception as e:
				print(f"Vidmoly m3u8 request failed: {e}")
				return Response(
					response='Video stream not available',
					status=404,
					headers={'Access-Control-Allow-Origin': '*'}
				)
		else:
			headers = {
				'host': host,
				'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
				'referer': referer,
			}
			try:
				response = requests.get(url, headers=headers, stream=True, timeout=30)
				return Response(
					response.iter_content(chunk_size=1024),
					content_type=response.headers.get('Content-Type', 'application/octet-stream'),
					status=response.status_code,
					headers={
						**{k: v for k, v in response.headers.items() if k.lower() in {'content-type', 'content-range', 'accept-ranges'}},
						'Access-Control-Allow-Origin': '*'
					}
				)
			except Exception as e:
				print(f"Vidmoly video request failed: {e}")
				return Response(
					response='Video not available',
					status=404,
					headers={'Access-Control-Allow-Origin': '*'}
				)
		
	@staticmethod
	def oneupload(url):
		response = requests.get(url, stream=True)
		return (Response(
			headers={'Access-Control-Allow-Origin': '*'},
			status=response.status_code,
			response=response.text,
		))
	
	@staticmethod
	def sendvid(url):
		headers = {
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
			'sec-fetch-dest': 'video',
		}
		if 'Range' in request.headers:
			headers['Range'] = request.headers['Range']
		try:
			response = requests.get(url, headers=headers, stream=True, timeout=10)
			return Response(
				response.iter_content(chunk_size=1024),
				content_type=response.headers.get('Content-Type', 'application/octet-stream'),
				status=response.status_code,
				headers={k: v for k, v in response.headers.items() if k.lower() in {'content-type', 'content-range', 'accept-ranges'}}
			)
		except Exception as e:
			return Response(
				response='Erreur lors de la récupération de la vidéo',
				status=404,
			)