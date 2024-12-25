import requests
from flask import Response, request

class Proxy:
	@staticmethod
	def sibnet(url):
		headers = {
			'host': 'video.sibnet.ru',
			'referer': 'https://video.sibnet.ru',
			'sec-fetch-dest': 'video',
		}
		if 'Range' in request.headers:
			headers['Range'] = request.headers['Range']
		response = requests.get(url, headers=headers, stream=True)
		return Response(
			response.iter_content(chunk_size=1024),
			content_type=response.headers.get('Content-Type', 'application/octet-stream'),
			status=response.status_code,
			headers={k: v for k, v in response.headers.items() if k.lower() in {'content-type', 'content-range', 'accept-ranges'}}
		)