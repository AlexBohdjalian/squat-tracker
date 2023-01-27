// import axios from 'axios';
import { StyleSheet } from 'react-native';
import { View } from '../components/Themed';
import { useState } from 'react';
import CameraButton from '../components/CameraButton';
import LocalCamera from '../components/LocalCamera';
import Colors from '../../constants/Colors';
import useColorScheme from '../../hooks/useColorScheme';
import { RootTabScreenProps } from '../../types';
// import * as HandDetector from '../../pose_estimation/HandDetection';
import PoseDetector from '../../pose_estimation/PoseNetDetector';

export default function VideoFeedScreen({ navigation }: RootTabScreenProps<'VideoFeed'>) {
  const [trackingForm, setTrackingForm] = useState(false);
  const scheme = useColorScheme();

  // async function sendImage({ image }: { image: CameraCapturedPicture }) {
  //   const data = new FormData();

  //   data.append('file', JSON.stringify({ uri: image.uri, name: 'anyname.jpg', type: 'image/jpg' }));

  //   const response = await axios.post('URL', data);

  //   const { id, url } = response.data;

  //   // create a component which displays takes an image,
  //   // sends it using this,
  //   // then displays the response
  // }

  if (trackingForm) {
    return (
      <View style={styles.container}>
        {/* <LocalCamera /> */}
        <PoseDetector />
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
        <LocalCamera />
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
