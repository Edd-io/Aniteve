import React, {useEffect, useState} from "react";
import { View, Text, StyleSheet, DeviceEventEmitter, TextInput, NativeModules, Keyboard, Alert} from "react-native";
import AsyncStorage from '@react-native-async-storage/async-storage';
import RNRestart from 'react-native-restart';
import { localData } from "../Default";

const remote = {
	'left': 21,
	'right': 22,
	'up': 19,
	'down': 20,
	'return': 4,
	'confirm': 23,
}

const nbLine = 2;
const {TestNativeModule} = NativeModules;

const SettingsPopup = ({setSettingPopup}: any) => {
	const [selectedLine, setSelectedLine] = useState<number>(0);
	const refTextInputAddress = React.createRef<TextInput>();
	const refTextInputTimeSkip = React.createRef<TextInput>();
	const [valueAddress, setValueAddress] = useState<string>('');
	const [valueTimeSkip, setValueTimeSkip] = useState<string>('');

	useEffect(() => {
		AsyncStorage.getItem('serverAddress').then((value) => {
			if (value !== null)
				setValueAddress(value);
		});
		AsyncStorage.getItem('timeSkip').then((value) => {
			if (value !== null)
				setValueTimeSkip(value);
		});
	}, []);

	useEffect(() => {
		const keyboardDidHideListener = Keyboard.addListener('keyboardDidHide', () => {
			refTextInputAddress.current?.blur();
			refTextInputTimeSkip.current?.blur();
			Keyboard.dismiss();
			TestNativeModule.userHasGetUp();
			if (selectedLine === 0)
			{
				AsyncStorage.setItem('serverAddress', valueAddress);
				setValueAddress(valueAddress);
				Alert.alert('Information', 'Les modifications seront prises en compte après un redémarrage de l\'application. Voulez-vous redémarrer l\'application ?', [
					{
						text: 'Annuler',
						onPress: () => {},
						style: 'cancel'
					},
					{
						text: 'Redémarrer',
						onPress: () => RNRestart.Restart(),
					}
				]);
			}
			if (selectedLine === 1)
			{
				const nbSec = parseInt(valueTimeSkip);
				AsyncStorage.setItem('timeSkip', nbSec.toString());
				setValueTimeSkip(nbSec.toString());
				localData.timeSkip = nbSec;
			}
		});
		return () => {
			keyboardDidHideListener.remove();
		};
	}, [valueAddress, valueTimeSkip]);

	const handleKeyPress = (data: any) => {

		if (data.screen !== 'SettingsPopup')
		{
			DeviceEventEmitter.removeAllListeners('remoteKeyPress');
			return ;
		}
		if (data.keycode === remote.up && selectedLine > 0)
			setSelectedLine(selectedLine - 1);
		else if (data.keycode === remote.down && selectedLine < nbLine - 1)
			setSelectedLine(selectedLine + 1);
		else if (data.keycode === remote.return)
			setSettingPopup(false);
		else if (data.keycode === remote.confirm)
		{
			if (selectedLine === 0)
				refTextInputAddress.current?.focus();
			if (selectedLine === 1)
				refTextInputTimeSkip.current?.focus();
		}
	}

	DeviceEventEmitter.removeAllListeners('remoteKeyPress');
	DeviceEventEmitter.addListener('remoteKeyPress', handleKeyPress);

	return (
		<View style={styles.popupSettings}>
			<View style={styles.island}>
				<Text style={styles.titlePopup}>Paramètres</Text>
				
				<View style={{backgroundColor: 0 === selectedLine ? '#555' : '#333', borderRadius: 10}}>
					<View style={styles.line}>
						<Text style={styles.text}>Adresse serveur</Text>
						<TextInput
							style={styles.textInput}
							placeholder="Adresse du serveur"
							placeholderTextColor={'#333'}
							ref={refTextInputAddress}
							keyboardType="url"
							onChangeText={(text) => setValueAddress(text)}
							value={valueAddress}
						/>
						</View>
					<Text style={styles.info}>Définissez l'adresse du serveur sur lequel est lancé le docker.</Text>
					<Text style={[styles.info, {marginBottom: 10}]}>Exemple : http://192.168.1.24:8080</Text>
				</View>

				<View style={{backgroundColor: 1 === selectedLine ? '#555' : '#333', borderRadius: 10}}>
					<View style={styles.line}>
						<Text style={styles.text}>Navigation temporelle</Text>
						<TextInput
							style={styles.textInput}
							placeholder="Temps en secondes"
							placeholderTextColor={'#333'}
							ref={refTextInputTimeSkip}
							keyboardType="numeric"
							onChangeText={(text) => setValueTimeSkip(text)}
							value={valueTimeSkip}
						/>
						</View>
					<Text style={[styles.info, {marginBottom: 10}]}>Définissez le temps de saut (en secondes) pour le lecteur vidéo.</Text>
				</View>
			</View>
		</View>
	)
};

const styles = StyleSheet.create({
	popupSettings : {
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
		overflow: 'hidden',
		width: '100%',
		justifyContent: 'space-between',
		alignItems: 'center',
	},
	text: {
		color: 'white',
		fontSize: 16,
		fontWeight: 'bold'
	},
	textInput: {
		backgroundColor: '#666',
		color: '#fff',
		borderRadius: 10,
		fontSize: 12,
		width: 200,
		alignItems: 'center',
	},
	info: {
		color: '#aaa',
		fontSize: 12,
		fontWeight: 'bold',
		paddingInline: 20,
	}
});

export default SettingsPopup;