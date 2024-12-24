import React, {useState, useCallback, useEffect} from 'react';
import { View, Text, StyleSheet, TouchableHighlight } from 'react-native';
import { proxy } from './src/proxy';
import { parseFileEpisode } from './src/parseFileEpisode';
import { GetSourceFile } from './src/GetSourceFile';

function App()
{
	const [data, setData] = useState<any>('');
	useEffect(() => {
		fetch('https://anime-sama.fr/catalogue/365-days-to-the-wedding/saison1/vostfr/episodes.js')
		.then((response) => {
			if (!response.ok) {
				throw new Error(`Erreur HTTP : ${response.status}`);
			}
			return response.text();
		})
		.then((content) => {
			content = content.replaceAll('var ', "globalThis.")
			try {
				eval(content);
				setData("episode recu");
				const eps: any = parseFileEpisode();
				GetSourceFile.from(eps['eps1'][0])?.then((videoUrl) => {
					console.log(videoUrl);
				})
			} catch (e) {
				console.error('Erreur dans eval :', e);
			}
		})
		.catch((err) => console.warn('Erreur lors de la requête :', err));
		// console.log('Reload');
		// const proxyServer = proxy();
		// return () => {
		//     proxyServer.close(() => {
		//         console.log('Proxy arrêté.');
		//     });
		// };

	}, []);
	return (
		<View>
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
