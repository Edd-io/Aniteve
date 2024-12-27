import React, {useState, useCallback, useEffect, useRef} from 'react';
import { View, Text, StyleSheet, TouchableHighlight, Image, FlatList, NativeModules, DeviceEventEmitter } from 'react-native';
import { LinearGradient } from 'react-native-linear-gradient';
import { useNavigation } from '@react-navigation/native';

const urlApiGetAllAnime = 'http://192.168.1.172:8080/api/get_all_anime';
const {TestNativeModule} = NativeModules;

let anime_list_complete: any = [];
let rangeStart = 0;
let rangeEnd = 16;
const remote = {
	'left': 21,
	'right': 22,
	'up': 19,
	'down': 20,
	'return': 4,
	'confirm': 23,
}
let haveOffset = false;

const AnimeItem = React.memo(({ item, selectedAnime }: any) => {
	const isSelected = selectedAnime === (item.id + 1);
	return (
		<View style={styles.animeContainer}>
			<Image
				source={{ uri: item.img }}
				style={[styles.animeImage, { transform: [{ scale: isSelected ? 1.1 : 1 }] }]}
				onError={(e) => console.log('Erreur de chargement de l\'image:', e.nativeEvent.error)}
			/>
		</View>
	);
});

const TopBar = () => {
	return (
		<View style={styles.topBar}>
			<Text style={styles.aniteve}>Aniteve</Text>
			<View style={{flexDirection: 'row'}}>
				<TouchableHighlight style={styles.topBarButtons} onPress={() => {}}>
					<Image source={require('../assets/img/search.png')} style={{width: 20, height: 20}} />
				</TouchableHighlight>
				<TouchableHighlight style={styles.topBarButtons} onPress={() => {}}>
					<Image source={require('../assets/img/settings.png')} style={{width: 20, height: 20}} />
				</TouchableHighlight>
			</View>
		</View>
	);
}

const AnimeInfo = ({ anime }: any) => {
	const	availableLanguagesVOSTFR = anime?.genre?.includes('VOSTFR');
	const	availableLanguagesVF = anime?.genre?.includes('VF');
	const	banGenre = ['VOSTFR', 'VF', 'cardListAnime', 'Anime', '-'];
	let		genreString :string[] = [];

	anime?.genre?.map((genre: string) => {
		if (!banGenre.includes(genre))
			genreString?.push(genre);
	});

	return (
		<View>
			<LinearGradient
				colors={
					['rgba(0, 0, 0, 0.8)', 'rgba(0, 0, 0, 0)']
				}
				style={styles.gradientOverlay}
				start={{ x: 0, y: 0 }}
				end={{ x: 0, y: 0.5 }}
			/>
			<LinearGradient
				colors={
					['rgba(0, 0, 0, 0)', 'rgba(34, 34, 34, 1)']
				}
				style={styles.gradientOverlay}
				start={{ x: 0, y: 0.7 }}
				end={{ x: 0, y: 1 }}
			/>
			<Image source={{uri: anime?.img}} style={{width: '100%', height: 250}} />
			<Text style={styles.titleAnime}>{anime?.title}</Text>
			<Text style={styles.genreAnime}>{genreString.join(', ').length > 100 ? genreString.join(', ').substring(0, 100) + '...' : genreString.join(', ')}</Text>
			<View style={styles.availableLanguages}>
				<Text style={[styles.availableLanguagesText, {color: availableLanguagesVOSTFR ? '#fff' : '#ffffff30'}]}>VOSTFR</Text>
				<Text style={[styles.availableLanguagesText, {color: availableLanguagesVF ? '#fff' : '#ffffff30'}]}>VF</Text>
			</View>
		</View>
	);
}

const HomeScreen = () =>
{
	const [selectedAnime, setSelectedAnime] = useState<number>(2); // 0: search, 1: settings, 2: first anime
	const [animeList, setAnimeList] = useState<any>([]);
	const [refresh, setRefresh] = useState<boolean>(false);
	const flatListRef = useRef<FlatList>(null);
	const navigation = useNavigation();

	useEffect(() => {
		fetch(urlApiGetAllAnime).then((response) => {
			return response.json();
		}).then((data) => {
			anime_list_complete = data.anime_list;
			setAnimeList(anime_list_complete.slice(rangeStart, rangeEnd));
		}).catch((error) => {
			console.warn(error);
		});
	}, []);

	useEffect(() => {
		function handleKeyPress(keycode: number)
		{
			const pos = selectedAnime - 2;
			console.log('keycode from home screen:', keycode);
	
			if (keycode === remote.left && pos % 4 != 0)
				setSelectedAnime(selectedAnime - 1);
			else if (keycode === remote.right && pos % 4 != 3 && pos < anime_list_complete.length - 1)
				setSelectedAnime(selectedAnime + 1);
			else if (keycode === remote.up && pos > 3)
			{
				if (pos - 4 < 4)
					flatListRef.current?.scrollToOffset({ animated: false, offset: 0 });
				setSelectedAnime(selectedAnime - 4);
				if (pos - 4 > 3)
				{
					rangeStart -= 4;
					rangeEnd -= 4;
					setAnimeList(anime_list_complete.slice(rangeStart, rangeEnd));
				}
			}
			else if (keycode === remote.down && pos < anime_list_complete.length - 2)
			{
				if (pos < 4)
				{
					flatListRef.current?.scrollToOffset({ animated: false, offset: 70 });
					haveOffset = true;
				}
				setSelectedAnime(selectedAnime + 4);
				if (pos + 4 > 7)
				{
					rangeStart += 4;
					rangeEnd += 4;
					setAnimeList(anime_list_complete.slice(rangeStart, rangeEnd));
				}
			}
			else if (keycode === remote.confirm)
			{
				navigation.navigate('Anime', {anime: anime_list_complete[selectedAnime - 2]});
				DeviceEventEmitter.removeAllListeners('remoteKeyPress');
			}
		}
		DeviceEventEmitter.addListener('remoteKeyPress', handleKeyPress);
		return () => {
			DeviceEventEmitter.removeAllListeners('remoteKeyPress');
		};
	}, [selectedAnime]);


	useEffect(() => {
		const handleKeyPress = () => {
			TestNativeModule.resolveTest().then((res: any) => {
				DeviceEventEmitter.emit('remoteKeyPress', parseInt(res));
				setRefresh(!refresh);
			});
		};
		handleKeyPress();
	}, [refresh]);
	
	const renderItem = useCallback(({ item }: any) => (
		<AnimeItem item={item} selectedAnime={selectedAnime} />
	), [selectedAnime]);

	return (
		<View style={{flex: 1, backgroundColor: '#222'}}>
			<TopBar />
			<AnimeInfo anime={anime_list_complete[selectedAnime - 2]} />
			<FlatList
				ref={flatListRef}
				data={animeList}
				renderItem={renderItem}
				keyExtractor={(item) => item.id.toString()}
				numColumns={4}
				contentContainerStyle={{ paddingBlock: 20, zIndex: 2}}
				columnWrapperStyle={{ justifyContent: 'space-evenly' }}
			/>
		</View>
	);
}

const styles = StyleSheet.create({
	topBar: {
		flexDirection: 'row',
		justifyContent: 'space-between',
		alignItems: 'center',
		padding: 20,
		position: 'absolute',
		width: '100%',
		zIndex: 2,
	},
	aniteve : {
		fontSize: 20,
		color: '#fff',
		fontWeight: 'bold',
	},
	topBarButtons: {
		paddingInline: 10,
	},
	animeContainer: {
		backgroundColor: '#333',
		borderRadius: 10,
		width: 200,
		height: 100,
		marginBottom: 20,
	},
	animeImage: {
		width: 200,
		height: 100,
		borderRadius: 10,
	},
	gradientOverlay: {
		...StyleSheet.absoluteFillObject,
		zIndex: 1,
	},
	titleAnime: {
		color: '#fff',
		fontSize: 22,
		fontWeight: 'bold',
		padding: 20,
		position: 'absolute',
		bottom: 20,
		zIndex: 2,
		textShadowColor: 'rgba(0, 0, 0, 0.5)',
		textShadowOffset: { width: 0, height: 0 },
		textShadowRadius: 10,
	},
	genreAnime: {
		color: '#ffffff90',
		fontSize: 16,
		fontWeight: 'bold',
		padding: 20,
		position: 'absolute',
		bottom: 0,
		left: 0,
		zIndex: 2,
		textShadowColor: 'rgba(0, 0, 0, 0.5)',
		textShadowOffset: { width: -1, height: 1 },
		textShadowRadius: 10,
	},
	availableLanguages: {
		flexDirection: 'row',
		justifyContent: 'space-between',
		padding: 20,
		position: 'absolute',
		bottom: 0,
		right: 0,
		zIndex: 2,
	},
	availableLanguagesText: {
		color: '#ffffff30',
		fontSize: 18,
		fontWeight: 'bold',
		marginLeft: 10,
	},
});

export default HomeScreen;