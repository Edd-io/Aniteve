import React, {useState, useCallback, useEffect, useRef} from 'react';
import { View, Text, StyleSheet, TouchableHighlight } from 'react-native';
import Video, {VideoRef} from 'react-native-video';
import { proxy } from './src/proxy';
import { WebView } from 'react-native-webview';
import { parseFileEpisode } from './src/parseFileEpisode';
import { GetSourceFile } from './src/GetSourceFile';
import axios from 'axios';

function App()
{
	const [data, setData] = useState<any>('');
	const [urlVideo, setUrlVideo] = useState<string>('');
	const videoRef = useRef<VideoRef>(null);

	useEffect(() => {
		console.log('Reload');
		const proxyServer = proxy();
		setTimeout(() => {
			axios('https://anime-sama.fr/catalogue/365-days-to-the-wedding/saison1/vostfr/episodes.js')
			.then((content) => {
				let data: string = content.data;
				data = data.replaceAll('var ', "globalThis.")
				try {
					eval(data);
					setData("episode recu");
					const eps: any = parseFileEpisode();
					GetSourceFile.from(eps['eps1'][0])?.then((videosUrl) => {
						setUrlVideo(videosUrl[0] + '?from=' + eps['eps1'][0]);
					});
				} catch (e) {
					console.error('Erreur dans eval :', e);
				}
			})
			.catch((err) => console.warn('Erreur lors de la requête :', err));
		}, 1000);
		return () => {
		    proxyServer.close(() => {
		        console.log('Proxy arrêté.');
		    });
		};
	}, []);
	return (
		<View style={{flex: 1, backgroundColor: 'black'}}>
			<WebView style={{flex: 1, width: '100%', height: '100%'}}
				source={{
					html: `
						<h1>dlksahdlsahsajkh</h1>
						<video controls style="width:100%; height:50%;" autoplay>
							<source src="${urlVideo}" type="video/mp4">
							Your browser does not support the video tag.
						</video>`
				}}
			/>
			<Text style={{color: 'white'}}>{data}</Text>
		</View>
	);
}

const styles = StyleSheet.create({
	topBar: {
		width: '99.95%',
		backgroundColor: 'green',
		padding: 10,
		justifyContent: 'space-between',
		flexDirection: 'row',
		alignItems: 'center'
	},
	title : {
		fontSize: 32,
		color: 'white',
		fontFamily: "Product Sans",
		fontWeight: "bold",
	}
});

export default App;
