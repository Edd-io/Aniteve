import React from 'react';
import { Text, View } from 'react-native';
import { useRoute, RouteProp } from '@react-navigation/native';
import Video, {VideoRef} from 'react-native-video';

interface RouteParams {
	data: any;
}

const PlayerScreen = () => {
	const route = useRoute<RouteProp<{ params: RouteParams }, 'params'>>();
	const { data } = route.params;

	console.log(data);
	return (
		<View>
			<Text>Player Screen</Text>
			{/* <Video
				source={{ uri: data.listUrlEpisodes['eps1'][0] }}
				ref={(ref: VideoRef) => {
					ref.presentFullscreenPlayer();
				}}
				style={{ width: '100%', height: 300 }}
				controls
			/> */}
		</View>
	);
}

export default PlayerScreen;