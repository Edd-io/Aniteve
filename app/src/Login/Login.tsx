import React, { useState, useEffect, useRef } from 'react';
import { Text, StyleSheet, View, TextInput, NativeModules, Keyboard, Alert } from 'react-native';
import { checkLogin } from './checkLogin';

const {TestNativeModule} = NativeModules;
const remote = {
	'left': 21,
	'right': 22,
	'up': 19,
	'down': 20,
	'return': 4,
	'confirm': 23,
}

const Login = ({setIsConnecting}: any) => {
	const	[selectorOn, setSelectorOn] = useState<number>(0);
	const	[refresh, setRefresh] = useState<boolean>(false);
	const	refTextInputServer = useRef<TextInput>(null);
	const	refTextInputPassword = useRef<TextInput>(null);
	const	[serverAddr, setServerAddr] = useState<string>('');
	const	[password, setPassword] = useState<string>('');
	const	[tokenValid, setTokenValid] = useState<number>(-1);

	useEffect(() => {
		const handleNativeKey = () => {
			TestNativeModule.resolveTest().then((res: any) => {
				if (parseInt(res) == remote.up)
					setSelectorOn(selectorOn == 0 ? 2 : selectorOn - 1);
				else if (parseInt(res) == remote.down)
					setSelectorOn(selectorOn == 2 ? 0 : selectorOn + 1);
				else if (parseInt(res) == remote.confirm)
				{
					if (selectorOn == 2)
						checkLogin(serverAddr, password, setTokenValid);
					else
						focusSelectedInput(selectorOn, refTextInputServer, refTextInputPassword);
				}
				setRefresh(!refresh);
			});
		};
		handleNativeKey();
	}, [refresh]);

	useEffect(() => {
		if (tokenValid == 0)
		{
			Alert.alert('Erreur', 'Adresse du serveur ou mot de passe invalide');
			refTextInputPassword.current?.clear();
			setTokenValid(-1);
		}
		else if (tokenValid == 1)
			setIsConnecting(1);
	}, [tokenValid]);

	useEffect(() => {
		const keyboardDidHideListener = Keyboard.addListener('keyboardDidHide', () => {
			refTextInputServer.current?.blur();
			refTextInputPassword.current?.blur();
			Keyboard.dismiss();
			TestNativeModule.userHasGetUp();
		});
		return () => {
			keyboardDidHideListener.remove();
		};
	}, []);

	return (
		<View style={{flex: 1, justifyContent: 'center', alignItems: 'center'}}>
			<Text style={styles.title}>Aniteve</Text>
			<Text style={styles.info}>Veuillez entrer les information de connexion</Text>
			<View style={{alignItems: 'center', backgroundColor: selectorOn == 0 ? '#555' : '', padding: 10, marginTop: 10}}>
				<Text style={styles.inputTitle}>Adresse du serveur</Text>
				<TextInput style={styles.input} ref={refTextInputServer} value={serverAddr} onChangeText={(text) => setServerAddr(text)} />
			</View>
			<View style={{alignItems: 'center', backgroundColor: selectorOn == 1 ? '#555' : '', padding: 10, marginTop: 10}}>
				<Text style={styles.inputTitle}>Mot de passe</Text>
				<TextInput style={styles.input} ref={refTextInputPassword} secureTextEntry={true} value={password} onChangeText={(text) => setPassword(text)} />
			</View>
			<View style={[{backgroundColor: selectorOn == 2 ? '#aaa' : '#555'}, styles.btn]}>
				<Text style={{color: '#fff', fontSize: 16, fontWeight: 'bold'}}>Se connecter</Text>
			</View>
		</View>
	)
}

function focusSelectedInput(selectorOn: number, refTextInputServer: any, refTextInputPassword: any)
{
	if (selectorOn == 0)
		refTextInputServer.current?.focus();
	else if (selectorOn == 1)
		refTextInputPassword.current?.focus();
}

const styles = StyleSheet.create({
	title: {
		color: 'white',
		fontSize: 25,
		fontWeight: 'bold',
		textAlign: 'center',
		marginBottom: 20,
	},
	info: {
		color: '#aaa',
		fontSize: 16,
		fontWeight: 'bold',
		paddingInline: 20,
	},
	inputTitle: {
		color: 'white',
		fontSize: 16,
		fontWeight: 'bold',
	},
	input: {
		backgroundColor: '#666',
		color: '#fff',
		borderRadius: 10,
		fontSize: 12,
		width: 300,
		alignItems: 'center',
		marginTop: 10,
	},
	btn: {
		padding: 10,
		borderRadius: 10,
		marginTop: 20,
		color: '#fff',
	}
});

export default Login;