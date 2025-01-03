import React, {useState} from "react";
import { ActivityIndicator, Text, View, StyleSheet } from "react-native";
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { HomeScreen } from './Home/Home';
import AnimeScreen from './Anime/Anime';
import PlayerScreen from './Player';
import AsyncStorage from '@react-native-async-storage/async-storage';

const Stack = createStackNavigator();

const localData = {
	addr: null as string | null,
	timeSkip: 0 as number,
}

const Default = () => {
	const [serverAddress, setServerAddress] = useState<string | null>(null);
	const [timeSkip, setTimeSkip] = useState<number | null>(null);

	AsyncStorage.getItem('serverAddress').then((value) => {
		localData.addr = value;
		setServerAddress(value || '');
	});
	AsyncStorage.getItem('timeSkip').then((value) => {
		localData.timeSkip = parseInt(value || '0');
		setTimeSkip(parseInt(value || '15'));
	});

	if (serverAddress == null || timeSkip == null)
	{
		return (
			<LoadingScreen animeName='Aniteve' />
		);
	}
	return (
		<NavigationContainer>
			<Stack.Navigator initialRouteName="Home" screenOptions={{headerShown: false}}>
				<Stack.Screen name="Home" component={HomeScreen} />
				<Stack.Screen name="Anime" component={AnimeScreen} />
				<Stack.Screen name="Player" component={PlayerScreen} />
			</Stack.Navigator>
		</NavigationContainer>
	);
}

const LoadingScreen = ({animeName}: any) => {
	return (
		<View style={[styles.LoadingScreen]}>
			<Text style={{color: '#fff', fontSize: 42, margin: 0,}}>{animeName}</Text>
			<Text style={{color: '#aaa', fontSize: 20, margin: 20}}>Chargement</Text>
			<ActivityIndicator size='large' color='#fff' />
		</View>
	);
}

const styles = StyleSheet.create({
	LoadingScreen: {
		flex: 1,
		position: 'absolute',
		width: '100%',
		height: '100%',
		alignItems: 'center',
		justifyContent: 'center',
		zIndex: 10,
		backgroundColor: '#333',
	}
});


export { Default, localData };