import React, {useState, useCallback, useEffect, useRef} from 'react';
import { View, Text, StyleSheet, TextInput, Image, FlatList, NativeModules, DeviceEventEmitter, Alert, BackHandler, Keyboard } from 'react-native';
import { LinearGradient } from 'react-native-linear-gradient';
import { useNavigation } from '@react-navigation/native';

const urlApiGetAllAnime = 'http://192.168.1.172:8080/api/get_all_anime';
const {TestNativeModule} = NativeModules;

let anime_list_complete: any = [];
let anime_list_search: any = [];
let rangeStart = 0;
let rangeEnd = 12;
const remote = {
	'left': 21,
	'right': 22,
	'up': 19,
	'down': 20,
	'return': 4,
	'confirm': 23,
}
let lastSelectedAnime = 2;
let lastRangeStart = 0;
let lastRangeEnd = 12;
let arrIdAnime: number[] = [];

const AnimeItem = React.memo(({ item, selectedAnimeId }: any) => {
	const isSelected = selectedAnimeId === (item.id + 1);
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

const TopBar = ({ selectedAnimeId, refTextInput, setSearchInput}: any) => {
	return (
		<View style={styles.topBar}>
			<Text style={styles.aniteve}>Aniteve</Text>
			<View style={{flexDirection: 'row'}}>
				<View style={[styles.topBarButtons, {backgroundColor: selectedAnimeId === 0 ? '#ffffff30' : 'transparent', overflow: 'hidden', flexDirection: 'row', alignItems: 'center'}]}>
					<TextInput
						style={{backgroundColor: '#ffffff30', color: '#fff', padding: 5, borderRadius: 10, width: 200, margin: 0, marginRight: 10}}
						placeholder="Rechercher un anime..."
						ref={refTextInput}
						onChangeText={(text) => setSearchInput(text)}
					/>
					<Image source={require('../assets/img/search.png')} style={{width: 20, height: 20}} />
				</View>
				<View style={[styles.topBarButtons, {backgroundColor: selectedAnimeId === 1 ? '#ffffff30' : 'transparent', overflow: 'hidden'}]}>
					<Image source={require('../assets/img/settings.png')} style={{width: 20, height: 30}} resizeMode='contain' />
				</View>
			</View>
		</View>
	);
}

const AnimeInfo = ({ anime, selectedAnimeId }: any) => {
	const	availableLanguagesVOSTFR = anime?.genre?.includes('Vostfr');
	const	availableLanguagesVF = anime?.genre?.includes('Vf');
	const	banGenre = ['vostfr', 'vf', 'cardlistanime', 'anime', '-', 'scans', 'film'];
	let		genreString :string[] = [];


	anime?.genre?.map((genre: string) => {
		if (!banGenre.includes(genre.toLowerCase()))
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
			{selectedAnimeId === -1 &&
				<Text style={[styles.titleAnime, {textAlign: 'center', width: '100%'}]}>Aucun résultat</Text>
			}
			<Text style={styles.genreAnime}>{genreString.join(', ').length > 100 ? genreString.join(', ').substring(0, 100) + '...' : genreString.join(', ')}</Text>
			{selectedAnimeId > 1 &&
				<View style={styles.availableLanguages}>
					<Text style={[styles.availableLanguagesText, {color: availableLanguagesVOSTFR ? '#fff' : '#ffffff30'}]}>VOSTFR</Text>
					<Text style={[styles.availableLanguagesText, {color: availableLanguagesVF ? '#fff' : '#ffffff30'}]}>VF</Text>
				</View>
			}
		</View>
	);
}

const HomeScreen = () =>
{
	const [selectedAnimeId, setSelectedAnimeId] = useState<number>(lastSelectedAnime); // 0: search, 1: settings, 2: first anime
	const [selectedAnimeVisual, setSelectedAnimeVisual] = useState<number>(lastSelectedAnime);
	const [animeList, setAnimeList] = useState<any>([]);
	const [refresh, setRefresh] = useState<boolean>(false);
	const [refreshSearchList, setRefreshSearchList] = useState<boolean>(false);
	const [searchInput, setSearchInput] = useState<string>('');
	const refTextInput = useRef<TextInput>(null);
	const flatListRef = useRef<FlatList>(null);
	const navigation = useNavigation();

	useEffect(() => {
		const unsubscribe = navigation.addListener('focus', () => {
			setSelectedAnimeId(lastSelectedAnime);
			rangeStart = lastRangeStart;
			rangeEnd = lastRangeEnd;
			setAnimeList(anime_list_search.slice(rangeStart, rangeEnd));
			if (lastSelectedAnime > 4)
				flatListRef.current?.scrollToOffset({ animated: false, offset: 70 });
			DeviceEventEmitter.removeAllListeners('remoteKeyPress');
			DeviceEventEmitter.addListener('remoteKeyPress', handleKeyPress);
			TestNativeModule.userHasGetUp();
		});
	
		return (unsubscribe);
	}, [navigation]);

	useEffect(() => {
		const keyboardDidShowListener = Keyboard.addListener('keyboardDidShow', () => {
			refTextInput.current?.focus();
		});
		const keyboardDidHideListener = Keyboard.addListener('keyboardDidHide', () => {
			refTextInput.current?.blur();
			TestNativeModule.userHasGetUp();
			setSelectedAnimeId(arrIdAnime[0] ? arrIdAnime[0] : 2);
			setSelectedAnimeVisual(2);
		});

		return () => {
			keyboardDidHideListener.remove();
			keyboardDidShowListener.remove();
		};
	}, []);

	useEffect(() => {
		const handleNativeKey = () => {
			TestNativeModule.resolveTest().then((res: any) => {
				DeviceEventEmitter.emit('remoteKeyPress', {screen: navigation.getState()?.routeNames[navigation.getState()?.index], keycode: parseInt(res)});
				setRefresh(!refresh);
			});
		};
		handleNativeKey();
	}, [refresh]);

	useEffect(() => {
		rangeStart = 0;
		rangeEnd = 12;
		arrIdAnime = [];
		if (searchInput.length == 0)
		{
			anime_list_search = [...anime_list_complete];
			arrIdAnime = Array.from(Array(anime_list_search.length).keys() , (x, i) => i + 2);
		}
		else
		{
			anime_list_search = [];
			for (let i = 0; i < anime_list_complete.length; i++)
			{
				if (anime_list_complete[i].title.toLowerCase().includes(searchInput.toLowerCase()))
					anime_list_search.push(anime_list_complete[i]);
				else if (anime_list_complete[i].alternative_title?.toLowerCase().includes(searchInput.toLowerCase()))
					anime_list_search.push(anime_list_complete[i]);
				else
					continue
				arrIdAnime.push(i + 2);
			}
		}
		console.log('arrIdAnime = :', arrIdAnime);
		setAnimeList(anime_list_search.slice(rangeStart, rangeEnd));
		console.log(anime_list_search);
		setSelectedAnimeVisual(2);
		setSelectedAnimeId(arrIdAnime[0] ? arrIdAnime[0] : -1);
		flatListRef.current?.scrollToOffset({ animated: false, offset: 0 });
	}, [searchInput, refreshSearchList]);

	useEffect(() => {
		fetch(urlApiGetAllAnime).then((response) => {
			return response.json();
		}).then((data) => {
			anime_list_complete = data.anime_list;
			setRefreshSearchList(!refreshSearchList);
			setAnimeList(anime_list_complete.slice(rangeStart, rangeEnd));
		}).catch((error) => {
			console.warn(error);
		});
	}, []);

	function handleKeyPress(data: any)
	{
		const	keycode = data.keycode;
		const	pos = selectedAnimeVisual - 2;

		console.log('pos = ', pos, '| selectedAnimeVisual = ', selectedAnimeVisual, '| selectedAnimeId = ', selectedAnimeId, '| rangeStart = ', rangeStart, '| rangeEnd = ', rangeEnd);
		if (data.screen !== 'Home')
			return ;
		if (keycode === remote.left)
		{
			if (selectedAnimeId === 0 || selectedAnimeId === 1)
			{
				setSelectedAnimeId(0);
				setSelectedAnimeVisual(0);
			}
			else if (pos % 4 != 0)
			{
				setSelectedAnimeId(arrIdAnime[pos - 1])
				setSelectedAnimeVisual(selectedAnimeVisual - 1);
			}
		}
		else if (keycode === remote.right)
		{
			if (selectedAnimeId === 0 || selectedAnimeId === 1)
			{
				setSelectedAnimeId(1);
				setSelectedAnimeVisual(1);
			}
			else if (pos % 4 != 3 && arrIdAnime[pos + 1])
			{
				setSelectedAnimeId(arrIdAnime[pos + 1])
				setSelectedAnimeVisual(selectedAnimeVisual + 1);
			}
		}
		else if (keycode === remote.up)
		{
			if (pos >= 4)
			{
				if (pos >= 4 && pos < 8)
					flatListRef.current?.scrollToOffset({ animated: false, offset: 0 });
				else
				{
					rangeStart -= 4;
					rangeEnd -= 4;
					setAnimeList(anime_list_search.slice(rangeStart, rangeEnd));
				}
				if (pos >= 4)
				{
					setSelectedAnimeId(arrIdAnime[pos - 4])
					setSelectedAnimeVisual(selectedAnimeVisual - 4);
				}
			}
			else
			{
				setSelectedAnimeId(0);
				setSelectedAnimeVisual(0);
			}
		}
		else if (keycode === remote.down && pos < anime_list_search.length - 4)
		{
			if (selectedAnimeId === 0 || selectedAnimeId === 1)
			{
				setSelectedAnimeId(arrIdAnime[0])
				setSelectedAnimeVisual(2);
			}
			else
			{
				if (pos < 4 && pos >= 0)
					flatListRef.current?.scrollToOffset({ animated: false, offset: 70 });
				else
				{
					rangeStart += 4;
					rangeEnd += 4;
					setAnimeList(anime_list_search.slice(rangeStart, rangeEnd));
				}
				if (pos < anime_list_search.length - 4)
				{
					setSelectedAnimeId(arrIdAnime[pos + 4])
					setSelectedAnimeVisual(selectedAnimeVisual + 4);
				}
			}
		}
		else if (keycode === remote.confirm)
		{
			if (selectedAnimeId > 1)
			{
				lastSelectedAnime = selectedAnimeId;
				lastRangeStart = rangeStart;
				lastRangeEnd = rangeEnd;
				navigation.navigate('Anime', {anime: anime_list_complete[selectedAnimeId - 2]});
			}
			else if (selectedAnimeId === 0)
			{
				setSearchInput('');
				refTextInput.current?.clear();
				refTextInput.current?.focus();
			}
			else if (selectedAnimeId === 1)
			{
			}
		}
		else if (keycode === remote.return)
		{
			if (selectedAnimeId > 2)
			{
				setSelectedAnimeId(2);
				setSelectedAnimeVisual(2);
			}
			else if (selectedAnimeId === 0 || selectedAnimeId === 1)
			{
				setSelectedAnimeId(2);
				setSelectedAnimeVisual(2);
			}
			else
			{
				Alert.alert('Quitter', 'Voulez-vous vraiment quitter l\'application ?', [
					{
						text: 'Non',
						onPress: () => {},
					},
					{
						text: 'Oui',
						onPress: () => TestNativeModule.exitApp(),
					},
				]);
			}
		}
	}

	DeviceEventEmitter.removeAllListeners('remoteKeyPress');
	DeviceEventEmitter.addListener('remoteKeyPress', handleKeyPress);
	
	const renderItem = useCallback(({ item }: any) => (
		<AnimeItem item={item} selectedAnimeId={selectedAnimeId} />
	), [selectedAnimeId]);

	return (
		<View style={{flex: 1, backgroundColor: '#222'}}>
			<TopBar
				selectedAnimeId={selectedAnimeId}
				refTextInput={refTextInput}
				setSearchInput={setSearchInput}
			/>
			<AnimeInfo anime={anime_list_complete[selectedAnimeId - 2]} selectedAnimeId={selectedAnimeId} />
			<FlatList
				ref={flatListRef}
				data={animeList}
				renderItem={renderItem}
				keyExtractor={(item) => item.id.toString()}
				numColumns={4}
				contentContainerStyle={{ paddingBlock: 20, zIndex: 2}}
				columnWrapperStyle={{ justifyContent: 'flex-start', paddingHorizontal: 20 }}
				scrollEnabled={false}
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
		padding: 6,
		marginInline: 6,
		borderRadius: 10,
	},
	animeContainer: {
		backgroundColor: '#333',
		borderRadius: 10,
		width: '20%',
		margin: '2.5%',
		marginBlock: 5,
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