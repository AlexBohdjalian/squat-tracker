import axios from 'axios';
import { StyleSheet } from 'react-native';
import { View } from '../components/Themed';
import { RootTabScreenProps } from '../../types';
import { Camera, CameraCapturedPicture } from 'expo-camera';
import { useState, useRef } from 'react';
import CameraButton from '../components/CameraButton';
import AndroidCamera from '../components/AndroidCamera';
import Colors from '../../constants/Colors';
import useColorScheme from '../../hooks/useColorScheme';

export default function VideoFeedScreen({ navigation }: RootTabScreenProps<'VideoFeed'>) {
  const [hasCameraPermission, setHasCameraPermission] = useState(false);
  const [trackingForm, setTrackingForm] = useState(false);
  const cameraRef = useRef<Camera|null>(null);
  const scheme = useColorScheme();

  async function sendImage({ image }: { image: CameraCapturedPicture }) {
    const data = new FormData();

    data.append('file', JSON.stringify({ uri: image.uri, name: 'anyname.jpg', type: 'image/jpg' }));

    const response = await axios.post('URL', data);

    const { id, url } = response.data;

    // create a component which displays takes an image,
    // sends it using this,
    // then displays the response
  }

  if (trackingForm) {
    return (
      <View style={styles.container}>
        <AndroidCamera innerCameraRef={cameraRef} />
        <View style={styles.trackingToggle}>
          <CameraButton
            title={'Stop Tacking'}
            icon="stop"
            color={Colors[scheme].text}
            onPress={() => setTrackingForm(false)}
          />
        </View>
      </View>
    );
  } else {
    return (
      <View style={styles.container}>
        <AndroidCamera innerCameraRef={cameraRef} />
        <View style={styles.trackingToggle}>
          <CameraButton
            title={'Begin Tracking'}
            icon="play"
            color={Colors[scheme].text}
            onPress={() => setTrackingForm(true)}
          />
        </View>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    paddingBottom: 5,
  },
  trackingToggle: {

    marginTop: 'auto',
  },
});
