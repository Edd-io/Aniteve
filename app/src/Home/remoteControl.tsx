import React, {
	useEffect,
} from 'react';
import {
	DeviceEventEmitter,
	Alert,
	NativeModules,
} from 'react-native';

const remote = {
	'left': 21,
	'right': 22,
	'up': 19,
	'down': 20,
	'return': 4,
	'confirm': 23,
}

const	{TestNativeModule} = NativeModules;
let		lastRangeStart = 0;
let		lastRangeEnd = 12;

const remoteControl = ({selectedAnimeId, setSelectedAnimeId, selectedAnimeVisual, searchInput,
	setSelectedAnimeVisual, anime_list, setAnimeList, range, setSearchInput, refTextInput, 
	flatListRef, navigation, arrIdAnime, last, setPopupResume}: any) => {

	useEffect(() => {
		const unsubscribe = navigation.addListener('focus', () => {
			setSelectedAnimeId(last.selectedAnime);
			range.start = lastRangeStart;
			range.end = lastRangeEnd;
			setAnimeList(anime_list.search.slice(range.start, range.end));
			if (last.selectedAnime > 5)
				flatListRef.current?.scrollToOffset({ animated: false, offset: 100 });
			DeviceEventEmitter.removeAllListeners('remoteKeyPress');
			DeviceEventEmitter.addListener('remoteKeyPress', handleKeyPress);
			TestNativeModule.userHasGetUp();
		});
	
		return (unsubscribe);
	}, [navigation]);

	function handleKeyPress(data: any)
	{
		const	keycode = data.keycode;
		const	pos = selectedAnimeVisual - 2;

		if (data.screen !== 'Home')
			return ;
		if (keycode === remote.left)
			remoteLeftButton(pos);
		else if (keycode === remote.right)
			remoteRightButton(pos);
		else if (keycode === remote.up)
			remoteUpButton(pos);
		else if (keycode === remote.down && pos < anime_list.search.length - 4)
			remoteDownButton(pos);
		else if (keycode === remote.confirm)
			remoteConfirmButton(pos);
		else if (keycode === remote.return)
			remoteReturnButton(pos);
	}

	function remoteLeftButton(pos: number)
	{
		if (selectedAnimeId === -1 || selectedAnimeId === 0 || selectedAnimeId === 1)
		{
			setSelectedAnimeId(selectedAnimeId - 1 < -1 ? -1 : selectedAnimeId - 1);
			setSelectedAnimeVisual(selectedAnimeVisual - 1 < -1 ? -1 : selectedAnimeVisual - 1);
		}
		else if (pos % 4 != 0)
		{
			setSelectedAnimeId(arrIdAnime[pos - 1])
			setSelectedAnimeVisual(selectedAnimeVisual - 1);
		}
	}

	function remoteRightButton(pos: number)
	{
		if (selectedAnimeId === -1 || selectedAnimeId === 0 || selectedAnimeId === 1)
		{
			setSelectedAnimeId(selectedAnimeId + 1 > 1 ? 1 : selectedAnimeId + 1);
			setSelectedAnimeVisual(selectedAnimeVisual + 1 > 1 ? 1 : selectedAnimeVisual + 1);
		}
		else if (pos % 4 != 3 && arrIdAnime[pos + 1])
		{
			setSelectedAnimeId(arrIdAnime[pos + 1])
			setSelectedAnimeVisual(selectedAnimeVisual + 1);
		}
	}

	function remoteUpButton(pos: number)
	{
		if (pos >= 4)
		{
			if (pos >= 4 && pos < 8)
				flatListRef.current?.scrollToOffset({ animated: false, offset: 0 });
			else
			{
				range.start -= 4;
				range.end -= 4;
				setAnimeList(anime_list.search.slice(range.start, range.end));
			}
			if (pos >= 4)
			{
				setSelectedAnimeId(arrIdAnime[pos - 4])
				setSelectedAnimeVisual(selectedAnimeVisual - 4);
			}
		}
		else
		{
			setSelectedAnimeId(-1);
			setSelectedAnimeVisual(-1);
		}
	}

	function remoteDownButton(pos: number)
	{
		if (selectedAnimeId === -1 || selectedAnimeId === 0 || selectedAnimeId === 1)
		{
			setSelectedAnimeId(arrIdAnime[0])
			setSelectedAnimeVisual(2);
		}
		else
		{
			if (pos < 4 && pos >= 0)
				flatListRef.current?.scrollToOffset({ animated: false, offset: 100 });
			else
			{
				range.start += 4;
				range.end += 4;
				setAnimeList(anime_list.search.slice(range.start, range.end));
			}
			if (pos < anime_list.search.length - 4)
			{
				setSelectedAnimeId(arrIdAnime[pos + 4])
				setSelectedAnimeVisual(selectedAnimeVisual + 4);
			}
		}
	}

	function remoteConfirmButton(pos: number)
	{
		if (selectedAnimeId > 1)
		{
			last.selectedAnime = selectedAnimeId;
			lastRangeStart = range.start;
			lastRangeEnd = range.end;
			navigation.navigate('Anime', {anime: anime_list.complete[selectedAnimeId - 2]});
		}
		else if (selectedAnimeId === -1)
		{
			setSearchInput('');
			refTextInput.current?.clear();
			refTextInput.current?.focus();
		}
		else if (selectedAnimeId === 0)
			setPopupResume(true);
		else if (selectedAnimeId === 1)
		{
		}
	}

	function remoteReturnButton(pos: number)
	{
		if (selectedAnimeId > 2 || searchInput.length > 0)
		{
			setSelectedAnimeId(2);
			setSelectedAnimeVisual(2);
			refTextInput.current?.clear();
			setSearchInput('');
			range.start = 0;
			range.end = 12;
			setAnimeList(anime_list.search.slice(range.start, range.end));
			flatListRef.current?.scrollToOffset({ animated: false, offset: 0 });

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

	DeviceEventEmitter.removeAllListeners('remoteKeyPress');
	DeviceEventEmitter.addListener('remoteKeyPress', handleKeyPress);
}

export default remoteControl;
