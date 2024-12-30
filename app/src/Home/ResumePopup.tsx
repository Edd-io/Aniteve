
import React, {useState} from 'react';
import { View, Text, StyleSheet, Image} from 'react-native';


const ElemList = () => {
	return (
		<View style={styles.line}>
			<Image
				source={{uri: 'https://i0.wp.com/picjumbo.com/wp-content/uploads/pure-nature-landscape-single-tree-in-green-field-free-photo.jpg?w=600&quality=80'}}
				style={styles.img}
			/>
			<View style={{justifyContent: 'center', paddingInline: 10}}>
				<Text style={styles.title}>Anime Name</Text>
				<Text style={styles.underTitle}>Saison1 - VOSTFR</Text>
				<Text style={styles.underTitle}>Episode 6</Text>
			</View>
		</View>
	)
}

const ResumePopup = () => {
	return (
		<View style={styles.popupResume}>
			<View style={styles.island}>
				<Text style={styles.titlePopup}>Reprendre</Text>
				<ElemList />
				<ElemList />
				<ElemList />
				<ElemList />
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
		marginBottom: 10
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