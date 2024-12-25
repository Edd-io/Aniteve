import TcpSocket from 'react-native-tcp-socket';
import axios from 'axios';

function proxy()
{

	const proxyServer = TcpSocket.createServer((clientSocket) => {
		console.log('Client connecté.');
		clientSocket.on('data', (clientData) => {
			if (clientData.toString().includes('sibnet'))
			{
				let url1 = 'https://video.sibnet.ru' + clientData.toString().split('sibnet')[1].split('?')[0]; // it's a mp4 file
				let url2 = clientData.toString().split('?from=')[1];
				console.log("URL1 : ", url1);
				console.log("URL2 : ", url2);

 				//accept: */*
				// accept-encoding:
				// identity;q=1, *;q=0
				// accept-language:
				// en-US,en;q=0.9,fr;q=0.8
				// cache-control:
				// no-cache
				// connection:
				// keep-alive
				// cookie:
				// __sibc_vuid=kEP0SGpEDCrcGunRLKX_1725186107; sib_userid=e3995bc88445122e7eb5ecb2e9623a72; OAID=2d62b89bb2767052dfc259f00a6a2fdb; visitor_session=6SvrbgW5q1UEYIECXZadpmSS69Ix5X
				// dnt:
				// 1
				// host:
				// video.sibnet.ru
				// pragma:
				// no-cache
				// range:
				// bytes=0-
				// referer:
				// https://video.sibnet.ru/shell.php?videoid=5700596
				// sec-ch-ua:
				// "Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"
				// sec-ch-ua-mobile:
				// ?0
				// sec-ch-ua-platform:
				// "macOS"
				// sec-fetch-dest:
				// video
				// sec-fetch-mode:
				// no-cors
				// sec-fetch-site:
				// same-origin
				// user-agent:
				// Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
				axios.get(url1, {
					headers: {
						host: "video.sibnet.ru",
						referer: url2
					},
					withCredentials: true // Pour gérer les cookies si nécessaire
				})
				.then((response) => {
					clientSocket.write(response.data);
				})
				.catch((err) => {
					console.warn(err);
				});
			}
		});
	});

	proxyServer.listen({ port: 8080, host: '0.0.0.0' }, () => {
		console.log('Proxy en écoute sur le port 8080');
	});
	return (proxyServer);
}

export {proxy};