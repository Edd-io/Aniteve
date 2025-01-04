import requests
from flask import Response, request

SERVER_PROXY_URL = 'http://192.168.1.172:8080'

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
		response = requests.get(url, headers=headers, stream=True)
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
		if (url.find('.m3u8') != -1):
			headers = {
				'host': host,
				'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
				'referer': 'https://vidmoly.to',
			}
			response = requests.get(url, headers=headers)
			data = response.text.replace('https://', SERVER_PROXY_URL + '/api/video?')
			return (Response(
				headers={
					'Access-Control-Allow-Origin': '*', 
			 		'Content-Type': 'application/vnd.apple.mpegurl'
				},
				response=data,
			))
		else:
			headers = {
				'host': host,
				'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
				'referer': 'https://vidmoly.to',
			}
			response = requests.get(url, headers=headers, stream=True)
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
		response = requests.get(url, headers=headers, stream=True)
		return Response(
			response.iter_content(chunk_size=1024),
			content_type=response.headers.get('Content-Type', 'application/octet-stream'),
			status=response.status_code,
			headers={k: v for k, v in response.headers.items() if k.lower() in {'content-type', 'content-range', 'accept-ranges'}}
		)