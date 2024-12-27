import React, { useEffect, useState } from 'react';
import { Image, StyleSheet, Text, View, DeviceEventEmitter } from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';
import { LinearGradient } from 'react-native-linear-gradient';
import credentials from '../credentials.json';
import { FlatList, ScrollView } from 'react-native-gesture-handler';

const base_url_tmdb = 'https://image.tmdb.org/t/p/original';

type RouteParams = {
	anime: any;
};

const remote = {
	'left': 21,
	'right': 22,
	'up': 19,
	'down': 20,
	'return': 4,
	'confirm': 23,
}

const get_data_from_tmdb = async (id: number) => {
	const url = `https://api.themoviedb.org/3/search/tv?api_key=${credentials.key_api_tmbd}&query=${id}`;
	const response = await fetch(url);
	const data = await response.json();
	const idAnime: number = data?.results[0]?.id;

	// get all data from the anime
	// const url3 = `https://api.themoviedb.org/3/tv/${idAnime}?api_key=${credentials.key_api_tmbd}&language=fr-FR`;
	// const response3 = await fetch(url3);
	// const data3 = await response3.json();
	// console.log(data3);


	const url2 = `https://api.themoviedb.org/3/tv/${idAnime}/images?api_key=${credentials.key_api_tmbd}`;
	const response2 = await fetch(url2);
	const data2 = await response2.json();
	return (data2);
}

const Background = ({ img }: any) => {
	return (
		<View style={{flex: 1, position: 'absolute', width: '100%', height: '100%'}}>
			{img &&
			<Image
				source={{ uri: img }}
				style={{ width: '100%', height: '100%', position: 'absolute' }}
			/>
			}
			<LinearGradient
				colors={
					['rgba(0, 0, 0, 0.9)', 'rgba(0, 0, 0, 0)']
				}
				style={styles.gradientOverlay}
				start={{ x: 0, y: 0 }}
				end={{ x: 1, y: 0 }}
			/>
		</View>
	);
}

const AnimeScreen = () => {
	const route = useRoute<RouteProp<{ params: RouteParams }, 'params'>>();
	const { anime } = route.params;
	const [logo, setLogo] = useState<string>('');
	const [logoDim, setLogoDim] = useState<any>({ width: 300, height: 0 });
	const [genre, setGenre] = useState<string[]>([]);
	const [epsFocused, setEpsFocused] = useState<number>(1);

	useEffect(() => {
		const	banGenre = ['VOSTFR', 'VF', 'cardListAnime', 'Anime', '-'];
		let		genreString :string[] = [];

		get_data_from_tmdb(anime.title).then((data) => {
			const logoData = data?.logos[0];
			if (logoData) {
				setLogo(base_url_tmdb + logoData.file_path);
				const aspectRatio = logoData.width / logoData.height;
				setLogoDim({ width: 300, height: 300 / aspectRatio });
			}
		});
		anime?.genre?.map((genre: string) => {
			if (!banGenre.includes(genre))
				genreString?.push(genre);
		});
		setGenre(genreString);
	}, []);

	useEffect(() => {
		function handleKeyPress(keycode: number)
		{
			if (keycode == remote.up) {
				if (epsFocused > 1)
					setEpsFocused(epsFocused - 1);
			}
			else if (keycode == remote.down) {
				if (epsFocused < 20)
					setEpsFocused(epsFocused + 1);
			}
		}
		DeviceEventEmitter.addListener('remoteKeyPress', handleKeyPress);
		return () => {
			DeviceEventEmitter.removeAllListeners('remoteKeyPress');
		};
	}, [epsFocused]);

	return (
		<View style={styles.body}>
			<Background img={anime.img} />
			<View style={styles.contentLeft}>
				{logo &&
				<Image source={{ uri: logo }} style={{width: logoDim.width, height: logoDim.height}} />
				}
				<View>
					<Text style={styles.title}>{anime.title}</Text>
					<Text style={styles.genre}>{genre.join(', ')}</Text>
				</View>
				<View >
					<Text style={styles.button}>Reprendre</Text>
					<Text style={styles.underButton}>vostfr/saison1 episode 1</Text>
				</View>
				<Text style={styles.button}>Changer de saison</Text>
				<View style={{flex: 1, justifyContent: 'flex-end'}}>
					<Text style={styles.button}>Retour</Text>
				</View>
			</View>
			<View style={styles.contentRight}>
				<View style={styles.island}>
					<Text style={styles.season}>vostfr/saison1</Text>
					<FlatList
						data={[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}
						renderItem={({ item }) => <Text style={epsFocused == item ? styles.epsFocused : styles.eps}>Episode {item}</Text>}
						keyExtractor={(item) => item.toString()}
					/>
				</View>
			</View>
		</View>
	);
};


const styles = StyleSheet.create({
	body: {
		flex: 1,
		backgroundColor: '#222',
		alignItems: 'center',
		justifyContent: 'center',
	},
	gradientOverlay: {
		...StyleSheet.absoluteFillObject,
		zIndex: 1,
	},
	contentLeft: {
		flex: 1,
		position: 'absolute',
		width: '50%',
		height: '100%',
		left: 0,
		top: 0,
		zIndex: 3,
		alignItems: 'center',
		padding: 20,
	},
	contentRight: {
		flex: 1,
		position: 'absolute',
		width: '50%',
		height: '100%',
		right: 0,
		top: 0,
		zIndex: 3,
		alignItems: 'center',
		padding: 20,
	},
	title: {
		color: '#fff',
		fontSize: 22,
		fontWeight: 'bold',
		marginTop: 10,
		textAlign: 'center',
	},
	genre: {
		color: '#ffffff90',
		fontSize: 16,
		textAlign: 'center',
	},
	button: {
		color: '#fff',
		fontSize: 20,
		fontWeight: 'bold',
		marginTop: 20,
		textAlign: 'center',
	},
	island: {
		backgroundColor: '#333',
		borderRadius: 10,
		width: '90%',
		height: '100%',
		padding: 20,
	},
	season: {
		color: '#fff',
		fontSize: 22,
		fontWeight: 'bold',
		marginBottom: 20,
	},
	eps: {
		color: '#ffffff',
		fontSize: 18,
		padding: 5,
	},
	epsFocused: {
		color: '#ffffff',
		fontSize: 18,
		padding: 5,
		fontWeight: 'bold',
		backgroundColor: '#222',
	},
	underButton: {
		color: '#ffffff90',
		fontSize: 16,
		textAlign: 'center',
	}
});

export default AnimeScreen;