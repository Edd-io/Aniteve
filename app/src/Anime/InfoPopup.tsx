import React from 'react';
import { Text, View, StyleSheet, Image } from 'react-native';

const InfoPopup = ({animeData}: any) => {
	console.log(animeData.firstAirDate);
	return (
		<View style={styles.popupInfo}>
			<View style={styles.island}>
				{animeData.noData ? 
				<Text style={styles.noData}>Aucune donnée disponible</Text>
				:
				<View style={{flexDirection: 'row', height: '100%', justifyContent: 'space-between'}}>
					<View style={styles.leftPart}>
						<View style={styles.titles}>
							<Text style={styles.titlePopup}>{animeData.title}</Text>
							<Text style={styles.underTitlePopup}>{animeData.originalName}</Text>
						</View>
						<View style={styles.infoLine}>
							<Text style={[styles.text, {fontWeight: 'bold'}]}>Date de sortie</Text>
							<Text style={styles.text}>{new Date(animeData.firstAirDate).toLocaleDateString()}</Text>
						</View>
						<View style={styles.infoLine}>
							<Text style={[styles.text, {fontWeight: 'bold'}]}>Popularité</Text>
							<Text style={styles.text}>{Number(animeData.popularity).toFixed(2)}</Text>
						</View>
						<View style={styles.lastInfoLine}>
							<Text style={[styles.text, {fontWeight: 'bold'}]}>Note</Text>
							<Text style={styles.text}>{Number(animeData.note).toFixed(2)}/10 ({animeData.nbVotes} votes)</Text>
						</View>
						<Text style={[styles.text, {textAlign: "justify"}]}>{animeData.overview}</Text>
					</View>
					<View style={styles.rightPart}>
						<Image
							source={{uri: animeData.poster}}
							style={{flex: 1, borderRadius: 10}}
							resizeMode='cover'
						/>
					</View>
				</View>
				}
			</View>
		</View>
	);
}

const styles = StyleSheet.create({
	popupInfo : {
		position: 'absolute',
		backgroundColor: '#00000077',
		width: '100%',
		height: '100%',
		flex: 1,
		zIndex: 4
	},
	island: {
		width: '80%',
		height: '90%',
		backgroundColor: '#333',
		borderRadius: 20,
		margin: 'auto',
		padding: 20,
		overflow: 'hidden',
	},
	noData: {
		color: 'white',
		fontSize: 24,
		textAlign: 'center',
		justifyContent: 'center',
		marginTop: '27%',
	},
	titles: {
		top: 0,
	},
	titlePopup: {
		color: 'white',
		fontSize: 24,
		textAlign: 'center',
		fontWeight: 'bold',
	},
	underTitlePopup: {
		color: 'white',
		fontSize: 16,
		textAlign: 'center',
		marginBottom: 20
	},
	text: {
		color: 'white',
		fontSize: 14,
		marginBottom: 10,
	},
	infoLine: {
		flexDirection: 'row',
		justifyContent: 'space-between',
		marginInline: 15,
		paddingInline: 10,
		borderColor: '#ccc',
		borderBottomWidth: 1,
		paddingTop: 10,
	},
	lastInfoLine: {
		flexDirection: 'row',
		justifyContent: 'space-between',
		marginInline: 15,
		paddingInline: 10,
		paddingTop: 10,
		marginBottom: 15,
	},
	leftPart: {
		width: '56%',
		justifyContent: 'center',
	},
	rightPart: {
		width: '42%',
		height: '100%',
	},
});

export default InfoPopup;