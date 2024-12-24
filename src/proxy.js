import TcpSocket from 'react-native-tcp-socket';

function proxy()
{

	const proxyServer = TcpSocket.createServer((clientSocket) => {
		console.log('Client connecté.');
		clientSocket.on('data', (clientData) => {
			console.log('Requête client reçue :\n', clientData);
		});
	});

	proxyServer.listen({ port: 8080, host: '0.0.0.0' }, () => {
		console.log('Proxy en écoute sur le port 8080');
	});
	return (proxyServer);
}

export {proxy};