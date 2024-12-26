import React, {useState, useCallback, useEffect, useRef} from 'react';
import { View, Text, StyleSheet, TouchableHighlight, Image, ScrollView, FlatList, TouchableOpacity } from 'react-native';
import { LinearGradient } from 'react-native-linear-gradient';

const urlApiGetAllAnime = 'http://10.0.2.2:8080/api/get_all_anime';

const HomeScreen = () =>
{
	const [selectedAnime, setSelectedAnime] = useState<Number>(2); // 0: search, 1: settings, 2: first anime
	const [animeList, setAnimeList] = useState<any>([]);

	useEffect(() => {
		fetch(urlApiGetAllAnime).then((response) => {
			return response.json();
		}).then((data) => {
			setAnimeList(data.anime_list);
		}).catch((error) => {
			console.warn(error);
		});
	}, []);
	

	return (
		<View style={{flex: 1, backgroundColor: '#222'}}>
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
				<Image source={{uri: animeList[selectedAnime - 2]?.img}} style={{width: '100%', height: 250}} />
				<Text style={styles.titleAnime}>{animeList[selectedAnime - 2]?.title}</Text>
			</View>
			<FlatList
				data={animeList}
				renderItem={({item}) => {
					return (
						<TouchableOpacity onPress={() => setSelectedAnime(item.id + 1)}>
							<View style={styles.animeContainer}>
								<Image source={{uri: item.img}} style={[styles.animeImage, {transform: (selectedAnime == (item.id + 1)) ? 'scale(1.1)' : 'scale(1)'}]} onError={(e) => console.log('Erreur de chargement de l\'image:', e.nativeEvent.error)}/>
							</View>
						</TouchableOpacity>
					);
				}}
				keyExtractor={(item) => item.id}
				numColumns={4}
				contentContainerStyle={{padding: 20, zIndex: 2}}
				columnWrapperStyle={{justifyContent: 'space-evenly'}}

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
		fontSize: 20,
		fontWeight: 'bold',
		padding: 20,
		position: 'absolute',
		bottom: 0,
		zIndex: 2,
	},
});

export default HomeScreen;