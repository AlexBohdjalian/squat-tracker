import { StyleSheet } from 'react-native';
import { View } from '../components/Themed';
import { useState } from 'react';
import CameraButton from '../components/CameraButton';
import LocalCamera from '../components/LocalCamera';
import Colors from '../../constants/Colors';
import useColorScheme from '../../hooks/useColorScheme';
import { RootTabScreenProps } from '../../types';
import PoseCamera from '../components/PoseCameraV3';

export default function VideoFeedScreen({ navigation }: RootTabScreenProps<'VideoFeed'>) {
  const [trackingForm, setTrackingForm] = useState(false);
  const scheme = useColorScheme();

  if (trackingForm) {
    return (
      <View style={styles.container}>
        <PoseCamera />
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
