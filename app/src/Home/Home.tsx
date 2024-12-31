import React, {useState, useCallback, useEffect, useRef} from 'react';
import { View, Text, StyleSheet, TextInput, Image, FlatList, NativeModules, DeviceEventEmitter, Alert, BackHandler, Keyboard } from 'react-native';
import { LinearGradient } from 'react-native-linear-gradient';
import { useNavigation } from '@react-navigation/native';
import remoteControl from './remoteControl';
import ResumePopup from './ResumePopup'


const urlApiGetAllAnime = 'http://192.168.1.172:8080/api/get_all_anime';
const {TestNativeModule} = NativeModules;

let anime_list: any = {
	complete: [],
	search: [],
}
let range: any  = {
	start: 0,
	end: 12,
}
let last: any = {
	selectedAnime: 2,
}
let arrIdAnime: number[] = [];
let animationBorderSelected: any = {
	id: -1,
	setWidthBorderFunc: null,
	timeout: null,
	focus: true,
}

let speed = 0;

const AnimeItem = React.memo(({ item, selectedAnimeId }: any) => {
	const [widthBorder, setWidthBorder] = useState(0);
	const isSelected = selectedAnimeId === (item.id + 1);
	if (isSelected)
	{
		if (animationBorderSelected.id != item.id && animationBorderSelected.setWidthBorderFunc !== null)
			speed = 0;
		animationBorderSelected = {
			id: item.id,
			setWidthBorderFunc: setWidthBorder,
			timeout: setTimeout(() => {
				let width = Math.sin(speed) + 1.5;
				speed += 0.075;
				setWidthBorder(width * 3);
			}, 16)
		}
	}
	
	return (
		<View style={styles.animeContainer}>
			<Image
				source={{ uri: item.img }}
				style={[styles.animeImage,
					{
						transform: [{ scale: isSelected ? 1.1 : 1 }],
						borderColor: '#79a4ed',
						borderWidth: selectedAnimeId < 2 ? 0 : isSelected ? widthBorder : 0,
					}
				]}
				onError={(e) => console.log('Error loading image', e)}
			/>
		</View>
	);
});

const TopBar = ({ selectedAnimeId, refTextInput, setSearchInput, popupResume}: any) => {
	return (
		<View style={styles.topBar}>
			<Text style={styles.aniteve}>Aniteve</Text>
			<View style={{flexDirection: 'row'}}>
				<View style={[styles.topBarButtons, {backgroundColor: selectedAnimeId === -1 ? '#ffffff30' : 'transparent', overflow: 'hidden', flexDirection: 'row', alignItems: 'center'}]}>
					<TextInput
						style={{backgroundColor: '#ffffff30', color: '#fff', padding: 5, borderRadius: 10, width: 200, margin: 0, marginRight: 10}}
						placeholder="Rechercher un anime..."
						ref={refTextInput}
						onChangeText={(text) => setSearchInput(text)}
					/>
					<Image source={require('../../assets/img/search.png')} style={{width: 20, height: 20}} />
				</View>
				<View style={[styles.topBarButtons, {backgroundColor: !popupResume && (selectedAnimeId === 0) ? '#ffffff30' : 'transparent', overflow: 'hidden'}]}>
					<Image source={require('../../assets/img/resume.png')} style={{width: 30, height: 30}} resizeMode='contain' />
				</View>
				<View style={[styles.topBarButtons, {backgroundColor: selectedAnimeId === 1 ? '#ffffff30' : 'transparent', overflow: 'hidden'}]}>
					<Image source={require('../../assets/img/settings.png')} style={{width: 20, height: 30}} resizeMode='contain' />
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
			{selectedAnimeId === -2 &&
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
	const [selectedAnimeId, setSelectedAnimeId] = useState<number>(last.selectedAnime); // -1: search, 0: resume, 1: settings, 2: first anime
	const [selectedAnimeVisual, setSelectedAnimeVisual] = useState<number>(last.selectedAnime);
	const [animeList, setAnimeList] = useState<any>([]);
	const [refresh, setRefresh] = useState<boolean>(false);
	const [refreshSearchList, setRefreshSearchList] = useState<boolean>(false);
	const [searchInput, setSearchInput] = useState<string>('');
	const [popupResume, setPopupResume] = useState<boolean>(false);
	const refTextInput = useRef<TextInput>(null);
	const flatListRef = useRef<FlatList>(null);
	const navigation = useNavigation();

	useEffect(() => {
		const keyboardDidShowListener = Keyboard.addListener('keyboardDidShow', () => {
			refTextInput.current?.focus();
		});
		const keyboardDidHideListener = Keyboard.addListener('keyboardDidHide', () => {
			refTextInput.current?.blur();
			TestNativeModule.userHasGetUp();
			setSelectedAnimeId(arrIdAnime[0] ? arrIdAnime[0] : -2);
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
				let actualScreen = null;

				if (popupResume)
					actualScreen = 'ResumePopup';
				else
					actualScreen = navigation.getState()?.routeNames[navigation.getState()?.index]
				DeviceEventEmitter.emit('remoteKeyPress', {
					screen: actualScreen,
					keycode: parseInt(res)
				});
				setRefresh(!refresh);
			});
		};
		handleNativeKey();
	}, [refresh]);

	useEffect(() => {
		range.start = 0;
		range.end = 12;
		arrIdAnime = [];
		if (searchInput.length == 0)
		{
			anime_list.search = [...anime_list.complete];
			arrIdAnime = Array.from(Array(anime_list.search.length).keys() , (x, i) => i + 2);
		}
		else
		{
			anime_list.search = [];
			for (let i = 0; i < anime_list.complete.length; i++)
			{
				if (anime_list.complete[i].title.toLowerCase().includes(searchInput.toLowerCase()))
					anime_list.search.push(anime_list.complete[i]);
				else if (anime_list.complete[i].alternative_title?.toLowerCase().includes(searchInput.toLowerCase()))
					anime_list.search.push(anime_list.complete[i]);
				else
					continue
				arrIdAnime.push(i + 2);
			}
		}
		setAnimeList(anime_list.search.slice(range.start, range.end));
		setSelectedAnimeVisual(2);
		setSelectedAnimeId(arrIdAnime[0] ? arrIdAnime[0] : -2);
		flatListRef.current?.scrollToOffset({ animated: false, offset: 0 });
	}, [searchInput, refreshSearchList]);

	useEffect(() => {
		fetch(urlApiGetAllAnime).then((response) => {
			return response.json();
		}).then((data) => {
			anime_list.complete = data.anime_list;
			setRefreshSearchList(!refreshSearchList);
			setAnimeList(anime_list.complete.slice(range.start, range.end));
		}).catch((error) => {
			console.warn(error);
		});
	}, []);
	
	const renderItem = useCallback(({ item }: any) => (
		<AnimeItem item={item} selectedAnimeId={selectedAnimeId} />
	), [selectedAnimeId]);

	remoteControl({selectedAnimeId, setSelectedAnimeId, selectedAnimeVisual, searchInput, setSelectedAnimeVisual, anime_list, setAnimeList, range, setSearchInput, refTextInput, flatListRef, navigation, arrIdAnime, last, setPopupResume});

	return (
		<View style={{flex: 1, backgroundColor: '#222'}}>
			<TopBar
				selectedAnimeId={selectedAnimeId}
				refTextInput={refTextInput}
				setSearchInput={setSearchInput}
				popupResume={popupResume}
			/>
			{
				popupResume && 
				<ResumePopup setPopupResume={setPopupResume} navigation={navigation} />
			}
			<AnimeInfo anime={anime_list.complete[selectedAnimeId - 2]} selectedAnimeId={selectedAnimeId} />
			<FlatList
				ref={flatListRef}
				data={animeList}
				renderItem={renderItem}
				keyExtractor={(item) => item.id.toString()}
				numColumns={4}
				contentContainerStyle={{ paddingBlock: 20, zIndex: 2}}
				columnWrapperStyle={{ justifyContent: 'flex-start', width: '95%', marginInline: 'auto'}}
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
		position: 'absolute',
		paddingInline: 20,
		marginTop: 10,
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
		width: '22%',
		margin: '1.5%',
		height: 120,
		marginBottom: 10,
	},
	animeImage: {
		width: '100%',
		height: '100%',
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