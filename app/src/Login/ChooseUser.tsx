import React, { useEffect, useState } from "react";
import { Text, View, StyleSheet, NativeModules } from "react-native";
import { localData } from "../Default";

const {TestNativeModule} = NativeModules;
const remote = {
	'left': 21,
	'right': 22,
	'up': 19,
	'down': 20,
	'return': 4,
	'confirm': 23,
}

const ChooseUser = ({setUser}: any) => {

	const	[refresh, setRefresh] = useState<boolean>(false);
	const	[users, setUsers] = useState([]);
	const	[onUser, setOnUser] = useState(0);

	function getUsers()
	{
		fetch(localData.addr + '/api/get_users', {
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				'Authorization': localData.token || '',
			},
		})
		.then(response => response.json())
		.then(data => {
			setUsers(data);
		})
		.catch((error) => {
			console.warn('Error:', error);
		});
	}

	useEffect(() => {
		getUsers();
	}, []);

	useEffect(() => {
		const handleNativeKey = () => {
			TestNativeModule.resolveTest().then((res: any) => {
				if (parseInt(res) == remote.up)
					setOnUser(onUser == 0 ? users.length - 1 : onUser - 1);
				else if (parseInt(res) == remote.down)
					setOnUser(onUser == users.length - 1 ? 0 : onUser + 1);
				else if (parseInt(res) == remote.confirm)
				{
					console.log(users[onUser]);
					localData.user = users[onUser];
					setUser(users[onUser]);
				}
				setRefresh(!refresh);
			});
		};
		handleNativeKey();
	}, [refresh, users]);

	return (
		<View style={styles.container}>
			<Text style={styles.title}>Qui êtes-vous ?</Text>
			<View style={styles.list}>
				{users.map((user: any, index: number) => {
					console.log(user);
					return (
						<Text key={user.id} style={[{backgroundColor: onUser === index ? '#777' : '#333', transform: [{ scale: onUser === index ? 1.02 : 1 }]}, styles.user]}>
							{user.name}
						</Text>
					);
				})}
			</View>
		</View>
	);
}

const styles = StyleSheet.create({
	container: {
		flex: 1,
		justifyContent: 'center',
		alignItems: 'center',
	},
	title: {
		fontSize: 24,
		color: '#fff',
	},
	list: {
		marginTop: 20,
		width: '50%',
		backgroundColor: '#555',
		alignItems: 'center',
		justifyContent: 'center',
		padding: 20,
		borderRadius: 10,
	},
	user: {
		margin: 5,
		padding: 5,
		width: '100%',
		textAlign: 'center',
		borderRadius: 5,
		color: '#fff',
	}
});

export default ChooseUser;