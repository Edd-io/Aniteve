import React from 'react';
import { Text, StyleSheet } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useNavigation } from '@react-navigation/native';
import HomeScreen from './src/Home';
import AnimeScreen from './src/Anime';
import PlayerScreen from './src/Player';

const Stack = createStackNavigator();

function App()
{
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

const styles = StyleSheet.create({

});

export default App;
