import React, {useState} from "react";
import { ActivityIndicator, Text, View } from "react-native";
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { HomeScreen } from './Home/Home';
import AnimeScreen from './Anime/Anime';
import PlayerScreen from './Player';
import AsyncStorage from '@react-native-async-storage/async-storage';

const Stack = createStackNavigator();

const localData = {
	addr: null as string | null,
	timeSkip: null as number | null,
}

const Default = () => {
	const [serverAddress, setServerAddress] = useState<string | null>(null);
	const [timeSkip, setTimeSkip] = useState<number | null>(null);

	AsyncStorage.getItem('serverAddress').then((value) => {
		localData.addr = value;
		setServerAddress(value);
	});
	AsyncStorage.getItem('timeSkip').then((value) => {
		localData.timeSkip = parseInt(value || '0');
		setTimeSkip(parseInt(value || '0'));
	});

	if (serverAddress == null || timeSkip == null)
	{
		return (
			<View style={{flex: 1, justifyContent: 'center', alignItems: 'center'}}>
				<ActivityIndicator size="large" color="#0000ff" />
				<Text>Chargement...</Text>
			</View>
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

export { Default, localData };