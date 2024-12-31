
import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Image, DeviceEventEmitter} from 'react-native';

const urlApiGetAllProgress = 'http://192.168.1.172:8080/api/get_all_progress';

const remote = {
	'left': 21,
	'right': 22,
	'up': 19,
	'down': 20,
	'return': 4,
	'confirm': 23,
}
const range = {
	start: 0,
	end: 4,
}

const ElemList = ({index, selectedLine, data}: any) => {
	const	season = data.season.charAt(0).toUpperCase() + data.season.slice(1).split('/')[0];
	const	lang = data.season.split('/')[1].toUpperCase();
	let		title = data.anime.title;
	let		info = null;

	if (title.length > 25)
		title = title.slice(0, 25) + '...'
	if (index < range.start || index >= range.end)
		return (null);
	if (data.completed == 1)
		info = 'À jour avec la diffusion';
	else if (data.completed == 2)
		info = 'Nouveau épisode';
	else if (data.completed == 3)
		info = 'Nouvelle saison disponible';
	return (
		<View style={[styles.line, {backgroundColor: index === selectedLine ? '#555' : '#333'}]}>
			<Image
				source={{uri: data.anime.img}}
				style={styles.img}
			/>
			<View style={{justifyContent: 'center', paddingInline: 10, flex: 1}}>
				<Text style={styles.title}>{title}</Text>
				<Text style={styles.underTitle}>{season} - {lang}</Text>
				<Text style={styles.underTitle}>Episode {data.episode + (!!data.completed ? ' - ' : '')}
					{!!data.completed &&
						<Text style={[styles.underTitle, {color: '#5de383'}]}>{info}</Text>
					}
				</Text>
				<View style={{width: '100%', height: 5, backgroundColor: 'rgba(255, 255, 255, 0.5)', borderRadius: 5, marginVertical: 5}}>
					<View style={{width: `${data.progress}%`, height: '100%', backgroundColor: 'rgba(255, 255, 255, 1)', borderRadius: 5}}></View>
				</View>
			</View>
		</View>
	)
}

const ResumePopup = ({setPopupResume, navigation}: any) => {
	const [selectedLine, setSelectedLine] = useState<number>(0);
	const [progressList, setProgressList] = useState<any>([]);

	useEffect(() => {
		fetch(urlApiGetAllProgress)
		.then((response) => {
			return (response.json());
		})
		.then((json) => {
			setProgressList(json);
		})
		.catch((error) => {
			console.warn(error);
		});
	}, []);

	const handleKeyPress = (data: any) => {
		
		if (data.screen !== 'ResumePopup')
		{
			DeviceEventEmitter.removeAllListeners('remoteKeyPress');
			return ;
		}
		if (data.keycode === remote.up && selectedLine > 0)
		{
			if (selectedLine > 0 && range.start > 0 && selectedLine < progressList.length - 1)
			{
				range.start--;
				range.end--;
			}
			if (selectedLine !== 0)
				setSelectedLine(selectedLine - 1);
		}
		else if (data.keycode === remote.down && selectedLine < progressList.length)
		{
			if (selectedLine > 0 && range.end <= progressList.length)
			{
				range.start++;
				range.end++;
			}
			if (selectedLine !== progressList.length - 1)
				setSelectedLine(selectedLine + 1);
		}
		else if (data.keycode === remote.confirm || data.keycode === remote.return)
		{
			range.start = 0;
			range.end = 4;
			if (data.keycode === remote.confirm)
				navigation.navigate('Anime', {anime: progressList[selectedLine].anime});
			setPopupResume(false);
		}
	}

	DeviceEventEmitter.removeAllListeners('remoteKeyPress');
	DeviceEventEmitter.addListener('remoteKeyPress', handleKeyPress);

	return (
		<View style={styles.popupResume}>
			<View style={styles.island}>
				<Text style={styles.titlePopup}>Reprendre</Text>
				{progressList.map((elem: any, index: number) => {
					return (
						<ElemList key={index} selectedLine={selectedLine} index={index} data={elem} />
					)
				})}
			</View>
		</View>
	)
}

const styles = StyleSheet.create({
	popupResume : {
		position: 'absolute',
		backgroundColor: '#00000077',
		width: '100%',
		height: '100%',
		flex: 1,
		zIndex: 4
	},
	island: {
		width: '50%',
		height: '90%',
		backgroundColor: '#333',
		borderRadius: 20,
		margin: 'auto',
		padding: 20,
		overflow: 'hidden'
	},
	titlePopup: {
		color: 'white',
		fontSize: 24,
		textAlign: 'center',
		fontWeight: 'bold',
		marginBottom: 20,
	},
	line: {
		flexDirection: 'row',
		padding: 10,
		borderRadius: 10,
		width: '100%',
	},
	img: {
		width: 100,
		height: 100,
		borderRadius: 10
	},
	title: {
		color: 'white',
		fontSize: 18,
		fontWeight: 'bold'
	},
	underTitle: {
		color: '#aaa',
		fontSize: 16,
		fontWeight: 'bold'
	}
});

export default ResumePopup;