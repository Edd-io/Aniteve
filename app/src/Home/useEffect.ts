import {NativeModules, DeviceEventEmitter, Keyboard} from 'react-native';
import {range, arrIdAnime, last} from './Home';
import { localData } from '../Default';

const {TestNativeModule} = NativeModules;

function useEffectHandleNativeKey(navigation: any, popupResume: boolean, setRefresh: any, refresh: boolean, popupSettings: boolean)
{
	const handleNativeKey = () => {
		TestNativeModule.resolveTest().then((res: any) => {
			let actualScreen = null;

			if (popupResume)
				actualScreen = 'ResumePopup';
			else if (popupSettings)
				actualScreen = 'SettingsPopup';
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
}

function updateAnimeListWithSearchInput(searchInput: string, setAnimeList: any, anime_list: any, setSelectedAnimeVisual: any, setSelectedAnimeId: any, flatListRef: any)
{
	range.start = 0;
	range.end = 12;
	arrIdAnime.anime = [];
	if (searchInput.length == 0)
	{
		anime_list.search = [...anime_list.complete];
		arrIdAnime.anime = Array.from(Array(anime_list.search.length).keys() , (x, i) => i + 2);
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
			arrIdAnime.anime.push(i + 2);
		}
	}
	setAnimeList(anime_list.search.slice(range.start, range.end));
	if (searchInput.length == 0)
	{
		setSelectedAnimeVisual(last.selectedAnime);
		setSelectedAnimeId(last.selectedAnime);
	}
	else
	{
		setSelectedAnimeVisual(2);
		setSelectedAnimeId(arrIdAnime.anime[0] ? arrIdAnime.anime[0] : -2);
		flatListRef.current?.scrollToOffset({ animated: false, offset: 0 });
	}
}

function fetchCompleteAnimeList(setAnimeList: any, anime_list: any, range: any, setRefreshSearchList: any, refreshSearchList: boolean, setErrServer: any)
{
	if (!(localData.addr?.length))
		return ;
	fetch(localData.addr + '/api/get_all_anime').then((response) => {
		return (response.json());
	}).then((data) => {
		console.log(data);
		let animeList = data;
		for (let i = 0; i < animeList.length; i++)
			animeList[i].idInList = i + 1;
		anime_list.complete = animeList;
		setRefreshSearchList(!refreshSearchList);
		setAnimeList(anime_list.complete.slice(range.start, range.end));
	}).catch((error) => {
		setErrServer(true);
	});
}

function keyboardHandler(refTextInput: any, setSelectedAnimeId: any, setSelectedAnimeVisual: any, popupSettings: boolean)
{
	const keyboardDidShowListener = Keyboard.addListener('keyboardDidShow', () => {
		if (popupSettings)
			return ;
		refTextInput.current?.focus();
	});
	const keyboardDidHideListener = Keyboard.addListener('keyboardDidHide', () => {
		if (popupSettings)
			return ;
		refTextInput.current?.blur();
		TestNativeModule.userHasGetUp();
		setSelectedAnimeId(arrIdAnime.anime[0] ? arrIdAnime.anime[0] : -2);
		setSelectedAnimeVisual(2);
	});
	return ([keyboardDidShowListener, keyboardDidHideListener]);
}

export {useEffectHandleNativeKey, updateAnimeListWithSearchInput, fetchCompleteAnimeList, keyboardHandler};