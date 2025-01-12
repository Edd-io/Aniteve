import AsyncStorage from '@react-native-async-storage/async-storage';
import { localData } from '../Default';

function checkLogin(serverAddr: string, password: string, setTokenValid: any)
{
	fetch(serverAddr + '/api/login', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			password: password,
		}),
	}).then((response) => {
		return (response.json());
	}).then((data) => {
		if (data.token)
		{
			localData.token = data.token;
			AsyncStorage.setItem('token', data.token);
			AsyncStorage.setItem('serverAddress', serverAddr);
			setTokenValid(1);
		}
		else
			setTokenValid(0);
	}).catch((error) => {
		setTokenValid(0);
	});
}

async function checkToken(serverAddr: string, setTokenValid: any)
{
	const token = await AsyncStorage.getItem('token');

	if (!token)
	{
		setTokenValid(0);
		return ;
	}
	fetch(serverAddr + '/api/check_token', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({
			token: token,
		}),
	}).then((response) => {
		return (response.json());
	}).then((data) => {
		console.log(data);
		if (data.error)
			setTokenValid(0);
		else
		{
			localData.token = token;
			setTokenValid(1);
		}
	}).catch((error) => {
		setTokenValid(0);
	});
}

export { checkLogin, checkToken };