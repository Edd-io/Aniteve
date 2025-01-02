import React from 'react';
import {DeviceEventEmitter, Alert} from 'react-native';
import { localData } from '../Default';

const remote = {
	'left': 21,
	'right': 22,
	'up': 19,
	'down': 20,
	'return': 4,
	'confirm': 23,
}

const remoteControl = ({navigation, anime, listUrlEpisodes, logo, resumeData, allSeasons,
	listEps, nbEpisodes, imageWhoNeedToLoaded, loadedImg, setNeedRefresh, needRefresh,
	setEpsFocused, epsFocused, setLeftPartFocused, leftPartFocused, setShowAvailableSeasons,
	showAvailableSeasons, setOnSelectedSeasons, onSelectedSeasons, listSeasons, pageSelected,
	setPageSelected, pageSelectedSeasons, setPageSelectedSeasons, leftButtonSelected,
	setLeftButtonSelected, idSelectedSeason, setIdSelectedSeason, setListSeasons, setPopupInfo, popupInfo}: any) => {

	function handleKeyPress(data: any)
	{
		const keycode = data.keycode;

		if (data.screen !== 'Anime')
			return ;
		if (keycode == remote.up && loadedImg >= imageWhoNeedToLoaded && !popupInfo)
			remoteUpButton();
		else if (keycode == remote.down && loadedImg >= imageWhoNeedToLoaded && !popupInfo)
			remoteDownButton();
		else if (keycode == remote.left && loadedImg >= imageWhoNeedToLoaded && !popupInfo)
			remoteLeftButton();
		else if (keycode == remote.right && loadedImg >= imageWhoNeedToLoaded && !popupInfo)
			remoteRightButton();
		else if (keycode == remote.return)
			remoteReturnButton();
		else if (keycode == remote.confirm && loadedImg >= imageWhoNeedToLoaded && !popupInfo)
			remoteConfirmButton();
		setNeedRefresh(!needRefresh)
	}

	function remoteUpButton()
	{
		if (!leftPartFocused)
		{
			if (!showAvailableSeasons && epsFocused > 1)
				setEpsFocused(epsFocused - 1);
			else if (onSelectedSeasons > 0)
				setOnSelectedSeasons(onSelectedSeasons - 1);
		}
		else if (leftButtonSelected > 0)
			setLeftButtonSelected(leftButtonSelected - 1);
	}

	function remoteDownButton()
	{
		if (!leftPartFocused)
		{
			if (!showAvailableSeasons && epsFocused < listEps.length)
				setEpsFocused(epsFocused + 1);
			else if (onSelectedSeasons < listSeasons.length - 1)
				setOnSelectedSeasons(onSelectedSeasons + 1);
		}
		else if (leftButtonSelected < 2)
			setLeftButtonSelected(leftButtonSelected + 1);
	}

	function remoteLeftButton()
	{
		if (!leftPartFocused)
		{
			if (pageSelected == 1 && !showAvailableSeasons)
			{
				setLeftPartFocused(true);
				setLeftButtonSelected(0);
			}
			else if (showAvailableSeasons && pageSelectedSeasons == 1)
			{
				setLeftPartFocused(true);
				setLeftButtonSelected(0);
			}
			else
			{
				if (!showAvailableSeasons)
					setPageSelected(pageSelected - 1);
				else
				{
					setPageSelectedSeasons(pageSelectedSeasons - 1);
					setListSeasons(allSeasons.slice((pageSelectedSeasons - 2) * 12, (pageSelectedSeasons - 1) * 12));
				}
			}
		}
	}
	
	function remoteRightButton()
	{
		if (leftPartFocused)
			setLeftPartFocused(false);
		else
		{
			if (!showAvailableSeasons)
			{
				if (pageSelected < Math.ceil(nbEpisodes / 12))
				{
					setPageSelected(pageSelected + 1);
					if (pageSelected * 12 + epsFocused > nbEpisodes)
						setEpsFocused(nbEpisodes % 12);
				}
			}
			else
			{
				if (pageSelectedSeasons < Math.ceil(allSeasons.length / 12))
				{
					setPageSelectedSeasons(pageSelectedSeasons + 1);
					if (pageSelectedSeasons * 12 + onSelectedSeasons > allSeasons.length)
						setOnSelectedSeasons(allSeasons.length % 12);
					setListSeasons(allSeasons.slice(pageSelectedSeasons * 12, (pageSelectedSeasons + 1) * 12));
				}
			}
		}
	}

	function remoteReturnButton()
	{
		if (popupInfo)
			setPopupInfo(false);
		else if (leftPartFocused)
			navigation.goBack();
		else
			setLeftPartFocused(true);
	}

	function remoteConfirmButton()
	{
		if (leftPartFocused)
		{
			if (leftButtonSelected == 0 && resumeData && resumeData.find)
			{
				if (resumeData.status === 1)
				{
					Alert.alert('Attention', 'Vous avez déjà vu cette épisode, voulez-vous vraiment le recommencer ?', [
						{
							text: 'Non',
							onPress: () => {},
						},
						{
							text: 'Oui',
							onPress: () => {
								navigation.navigate('Player', {data: {
									season: allSeasons,
									episode: resumeData.episode,
									selectedSeasons: allSeasons.indexOf(resumeData.season),
									url: anime.url,
									title: anime.title,
									listUrlEpisodes: {},
									logo: logo,
									back: anime,
								}});
							}
						}
					]);
				}
				else
				{
					navigation.navigate('Player', {data: {
						season: allSeasons,
						episode: resumeData.episode,
						selectedSeasons: allSeasons.indexOf(resumeData.season),
						url: anime.url,
						title: anime.title,
						listUrlEpisodes: {},
						logo: logo,
						back: anime,
						resumeTime: resumeData.progress,
					}});
				}
			}
			else if (leftButtonSelected == 1)
			{
				setShowAvailableSeasons(!showAvailableSeasons);
				setLeftPartFocused(false);
			}
			else if (leftButtonSelected == 2)
				setPopupInfo(true);
		}
		else
		{
			if (!showAvailableSeasons)
			{
				navigation.navigate('Player', {data: {
					season: allSeasons,
					episode: (pageSelected - 1) * 12 + epsFocused,
					selectedSeasons: idSelectedSeason,
					url: anime.url,
					title: anime.title,
					listUrlEpisodes: listUrlEpisodes,
					logo: logo,
					back: anime,
				}});
			}
			else
			{
				setIdSelectedSeason((pageSelectedSeasons - 1) * 12 + onSelectedSeasons);
				setShowAvailableSeasons(!showAvailableSeasons);
				setEpsFocused(1);
			}
		}
	}

	DeviceEventEmitter.removeAllListeners('remoteKeyPress');
	DeviceEventEmitter.addListener('remoteKeyPress', handleKeyPress);
}

export default remoteControl;