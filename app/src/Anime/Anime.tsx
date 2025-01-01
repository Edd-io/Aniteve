import React, { useEffect, useState } from 'react';
import { Image, StyleSheet, Text, View, FlatList, ActivityIndicator} from 'react-native';
import { useRoute, RouteProp, useNavigation, NavigationProp } from '@react-navigation/native';
import { LinearGradient } from 'react-native-linear-gradient';
import credentials from '../../credentials.json';
import remoteControl from './remoteControl';
import InfoPopup from './InfoPopup';
import { localData } from '../Default';

const base_url_tmdb	= 'https://image.tmdb.org/t/p/original';

type RouteParams = {
	anime: any;
};
type RootStackParamList = {
	Player: {
		data: {
			season: any,
			episode: number,
			selectedSeasons: number,
			url: string,
			title: string,
			listUrlEpisodes: string[],
			logo: string,
			back: any,
			resumeTime?: number
		};
	};
};
type PlayerScreenNavigationProp = NavigationProp<RootStackParamList, 'Player'>;
const dataAnime: any = {
	title: '',
	firstAirDate: '',
	name: '',
	originalName: '',
	overview: '',
	poster: '',
	popularity: 0,
	note: 0,
	nbVotes: 0,
	noData: true,
}

let imageWhoNeedToLoaded = 2;

const get_data_from_tmdb = async (id: string, isMovie: boolean) => {
	let allDiff: any = [];
	let response = null;
	let data = null;
	let url = null;
	let allAnimeData = [];

	if (!isMovie)
	{
		url = `https://api.themoviedb.org/3/search/tv?api_key=${credentials.key_api_tmbd}&query=${id}&language=fr-FR`;
		response = await fetch(url);
		data = await response.json();
		allAnimeData = data?.results.filter((result: any) => result.genre_ids.includes(16));
	}
	else
	{
		url = `https://api.themoviedb.org/3/search/movie?api_key=${credentials.key_api_tmbd}&query=${id}&language=fr-FR`;
		response = await fetch(url);
		data = await response.json();
		allAnimeData = data?.results.filter((result: any) => result.genre_ids.includes(16));
	}
	if (allAnimeData.length === 0)
	{
		dataAnime.noData = true;
		return (null);
	}
	for (let i = 0; i < allAnimeData.length; i++)
		allDiff.push(allAnimeData[i][isMovie ? 'title' : 'name'].length - id.length);
	
	let animeData = allAnimeData[allDiff.indexOf(Math.min(...allDiff))];
	let idAnime: number = animeData?.id;

	dataAnime.title = animeData.title ? animeData.title : animeData.name;
	dataAnime.firstAirDate = animeData.first_air_date;
	dataAnime.name = animeData.name;
	dataAnime.originalName = animeData.original_name;
	dataAnime.overview = animeData.overview;
	dataAnime.poster = base_url_tmdb + animeData.poster_path;
	dataAnime.popularity = animeData.popularity;
	dataAnime.note = animeData.vote_average;
	dataAnime.nbVotes = animeData.vote_count;
	dataAnime.noData = false;

	url = `https://api.themoviedb.org/3/${isMovie ? 'movie' : 'tv'}/${idAnime}/images?api_key=${credentials.key_api_tmbd}&include_image_language=ja,en,null`;
	response = await fetch(url);
	data = await response.json();
	if (data.logos.length === 0) 
	{
		const fallbackUrl = `https://api.themoviedb.org/3/${isMovie ? 'movie' : 'tv'}/${idAnime}/images?api_key=${credentials.key_api_tmbd}`;
		response = await fetch(fallbackUrl);
		data = await response.json();
	}
	return (data);
}

const LoadingScreen = ({animeName}: any) => {
	return (
		<View style={[styles.LoadingScreen]}>
			<Text style={{color: '#fff', fontSize: 20, margin: 0}}>{animeName}</Text>
			<Text style={{color: '#aaa', fontSize: 20, margin: 20}}>Chargement</Text>
			<ActivityIndicator size='large' color='#fff' />
		</View>
	);
}

let nbEpisodes = 0;
let listUrlEpisodes: any = null;
let allSeasons: string[] = [];

const AnimeScreen = () => {
	const route = useRoute<RouteProp<{ params: RouteParams }, 'params'>>();
	const { anime } = route.params;
	const [logo, setLogo] = useState<string>('');
	const [BackgroundImg, setBackgroundImg] = useState<string>('');
	const [genre, setGenre] = useState<string[]>([]);
	const [leftButtonSelected, setLeftButtonSelected] = useState<number>(0); // 0 = reprendre, 1 = saison, 2 = retour
	const [leftPartFocused, setLeftPartFocused] = useState<boolean>(true); // true = left, false = right
	const [needRefresh, setNeedRefresh] = useState<boolean>(false);
	const [loadedImg, setLoadedImg] = useState<number>(0);
	const [popupInfo, setPopupInfo] = useState<boolean>(false);
	
	const [epsFocused, setEpsFocused] = useState<number>(1);
	const [listEps, setListEps] = useState<number[]>([]);
	const [pageSelected, setPageSelected] = useState<number>(1);
	
	const [listSeasons, setListSeasons] = useState<string[]>([]);
	const [onSelectedSeasons, setOnSelectedSeasons] = useState<number>(0); // on season in the list without confirm
	const [showAvailableSeasons, setShowAvailableSeasons] = useState<boolean>(false);
	const [pageSelectedSeasons, setPageSelectedSeasons] = useState<number>(1);
	const [idSelectedSeason, setIdSelectedSeason] = useState<number>(0);
	const [resumeData, setResumeData] = useState<any>(null);
	const navigation = useNavigation<PlayerScreenNavigationProp>();

	useEffect(() => {
		setTimeout(() => {
			setLoadedImg(3);
		}, 2000);
		const	banGenre = ['vostfr', 'vf', 'cardlistanime', 'anime', '-', 'scans', 'film'];
		let		genreString :string[] = [];

		imageWhoNeedToLoaded = 2;
		anime?.genre?.map((genre: string) => {
			if (!banGenre.includes(genre.toLowerCase()))
				genreString?.push(genre); 
		});
		fetch(localData.addr + '/api/get_anime_season', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({url: anime.url, serverUrl: localData.addr}),
		}).then((response) => {
			return response.json();
		}).then((data) => {
			let season = data.season;
			let isMovie = false;
		
			if (anime.genre.includes('Vf'))
			{
				data.season.forEach((element: string) => {
					element = element.replace('vostfr', 'vf');
					season.push(element);
				});
			}
			allSeasons = season;
			setListSeasons(allSeasons.slice(0, 12));
			isMovie = season[0]?.toLowerCase().includes('film');
			get_data_from_tmdb(anime.title, isMovie).then((data) => {
				let logoData = null;
				let i = 0;
	
				while (data && data.logos[i])
				{
					if (!data.logos[i].file_path.includes('svg') && data.logos[i].iso_639_1 != 'ko')
					{
						logoData = data.logos[i];
						break ;
					}
					i++;
				}
				imageWhoNeedToLoaded = (logoData ? 1 : 0) + (data?.backdrops[0] ? 1 : 0);
				if (logoData)
					setLogo(base_url_tmdb + logoData.file_path);
				const backdropData = data?.backdrops[0];
				if (backdropData)
					setBackgroundImg(base_url_tmdb + backdropData.file_path);
				else
					setBackgroundImg(anime.img);
			});
		}).catch((error) => {
			console.warn(error);
		});
		fetch(localData.addr + '/api/get_progress', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({id: anime.id}),
		}).then((response) => {
			return response.json();
		}).then((data) => {
			setResumeData(data);
		}).catch((error) => {
			console.warn(error);
		});
		setGenre(genreString);
	}, []);

	useEffect(() => {
		if (allSeasons.length == 0)
			return ;
		fetch(localData.addr + '/api/get_anime_episodes', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			}, 
			body: JSON.stringify({url: anime.url, season: allSeasons[idSelectedSeason], serverUrl: localData.addr}),
		}).then((response) => {
			return response.json();
		}).then((data) => {
			nbEpisodes = data.number;
			listUrlEpisodes = data.episodes;
			if (nbEpisodes >= 12)
				setListEps([...Array(12).keys()].map(x => x + 1));
			else
				setListEps([...Array(nbEpisodes).keys()].map(x => x + 1));
		}).catch((error) => {
			console.warn(error);
		});
	}, [idSelectedSeason, listSeasons]);

	const NbPages = () => {
		const pages = Math.ceil(showAvailableSeasons ? allSeasons.length / 12 : nbEpisodes / 12);
		let pagesArray = [];
		for (let i = 0; i < pages; i++)
			pagesArray.push(
				<Text
					key={i}
					style={[
						styles.pageSquare,
						{
							backgroundColor: (showAvailableSeasons ? pageSelectedSeasons : pageSelected) == i + 1 ? '#fff' : '#333',
							color: (showAvailableSeasons ? pageSelectedSeasons : pageSelected) == i + 1 ? '#222' : '#fff',
						}
					]}>
					{i + 1}
				</Text>
			);
		if (pagesArray.length == 0 && !showAvailableSeasons)
			return (<Text style={styles.title}>Pas d'episodes disponibles</Text>);
		else if (pagesArray.length == 0 && showAvailableSeasons)
			return (<Text style={styles.title}>Pas de saisons disponibles</Text>);
		return (
			<View style={{width: '100%', height: 50, flexDirection: 'row', justifyContent: 'center', alignItems: 'center'}}>
				<Text></Text>
				{pagesArray.map((page) => page)}
			</View>
		);
	}

	remoteControl({navigation, anime, listUrlEpisodes, logo, resumeData, allSeasons,
		listEps, nbEpisodes, imageWhoNeedToLoaded, loadedImg, setNeedRefresh, needRefresh,
		setEpsFocused, epsFocused, setLeftPartFocused, leftPartFocused, setShowAvailableSeasons,
		showAvailableSeasons, setOnSelectedSeasons, onSelectedSeasons, listSeasons, pageSelected,
		setPageSelected, pageSelectedSeasons, setPageSelectedSeasons, leftButtonSelected,
		setLeftButtonSelected, idSelectedSeason, setIdSelectedSeason, setListSeasons, setPopupInfo, popupInfo
	});

	return (
		<View style={styles.body}>
			{loadedImg < imageWhoNeedToLoaded &&
			<LoadingScreen animeName={anime.title} />
			}
			{popupInfo &&
				<InfoPopup animeData={dataAnime} setPopupInfo={setPopupInfo} />
			}
			<View style={{flex: 1, position: 'absolute', width: '100%', height: '100%'}}>
				{BackgroundImg &&
				<Image
					source={{ uri: BackgroundImg }}
					style={{ width: '100%', height: '100%', position: 'absolute' }}
					onLoad={() => {
						setLoadedImg(prevLoadedImg => prevLoadedImg + 1);
					}}
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
			<View style={styles.contentLeft}>
				{logo &&
				<Image
					source={{ uri: logo }}
					style={{width: 300, height: 160}}
					resizeMode='contain'
					onLoad={() => {
						setLoadedImg(loadedImg + 1);
					}}
				/>
				}
				<View>
					<Text style={styles.title}>{anime.title}</Text>
					<Text style={styles.genre}>{genre.join(', ')}</Text>
				</View>
				<View>
					<Text style={[
						leftPartFocused && (leftButtonSelected == 0) ? styles.buttonSelected : styles.button,
						resumeData && resumeData.find ? {color: '#fff'} : {color: '#555555'}
						]}>
						Reprendre
					</Text>
					{resumeData && resumeData.find &&
					<Text style={styles.underButton}>{resumeData.season} - Episode {resumeData.episode}</Text>
					}
				</View>
				<View>
					<Text style={leftPartFocused && (leftButtonSelected == 1)? styles.buttonSelected : styles.button}>Changer de saison</Text>
					<Text style={styles.underButton}>{allSeasons[idSelectedSeason]}</Text>
				</View>
				<Text style={leftPartFocused && (leftButtonSelected == 2)? styles.buttonSelected : styles.button}>Information</Text>
			</View>
			<View style={styles.contentRight}>
				<View style={styles.island}>
					<NbPages />
					<View style={{width: '100%', height: '100%', paddingInline: 20}}>
						{
							!showAvailableSeasons ?
							<FlatList
							data={listEps}
							renderItem={({ item }) =>
								(pageSelected - 1) * 12 + item > nbEpisodes ?
								null :
								<Text style={!leftPartFocused && epsFocused == item ? styles.epsFocused : styles.eps}>Episode {(pageSelected - 1) * 12 + item}</Text>}
							keyExtractor={(item) => item.toString()}
							/> :
							<FlatList
							data={listSeasons}
							renderItem={({ item, index }) => <Text style={!leftPartFocused && onSelectedSeasons == index ? styles.epsFocused : styles.eps}>{item}</Text>}
							keyExtractor={(item) => item}
							/>
						}
					</View>
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
		overflow: 'hidden',
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
		padding: 5,
		marginTop: 20,
		textAlign: 'center',
	},
	buttonSelected: {
		color: '#fff',
		fontSize: 20,
		fontWeight: 'bold',
		marginTop: 20,
		padding: 5,
		textAlign: 'center',
		backgroundColor: '#333333E0',
		borderRadius: 10,
	},
	island: {
		width: '90%',
		height: '100%',
		overflow: 'hidden',
		borderRadius: 20,
		backgroundColor: '#333333E0',
	},
	season: {
		color: '#fff',
		fontSize: 22,
		fontWeight: 'bold',
		padding: 20,
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
	},
	pageSquare: {
		color: '#fff',
		fontSize: 20,
		width: 30,
		borderColor: '#fff',
		borderWidth: 1,
		textAlign: 'center',
		margin: 2,
	},
	LoadingScreen: {
		flex: 1,
		position: 'absolute',
		width: '100%',
		height: '100%',
		alignItems: 'center',
		justifyContent: 'center',
		zIndex: 10,
		backgroundColor: '#333',
	}
});

export default AnimeScreen;