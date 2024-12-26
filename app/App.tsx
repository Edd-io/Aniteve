import React, {useState, useCallback, useEffect, useRef} from 'react';
import { View, Text, StyleSheet, TouchableHighlight } from 'react-native';
import Video, {VideoRef} from 'react-native-video';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { useNavigation } from '@react-navigation/native';
import { enableScreens } from 'react-native-screens';
import HomeScreen from './src/Home';

enableScreens();

const Stack = createStackNavigator();

const SettingsScreen = () =>
{
	const navigation = useNavigation();
	return (
		<Text>Settings Screen</Text>
	);
}


function App()
{
	return (
	<NavigationContainer>
		<Stack.Navigator initialRouteName="Home" screenOptions={{headerShown: false}}>
			<Stack.Screen name="Home" component={HomeScreen} />
			<Stack.Screen name="Settings" component={SettingsScreen} />
		</Stack.Navigator>
	</NavigationContainer>
	);
}

const styles = StyleSheet.create({

});

export default App;
