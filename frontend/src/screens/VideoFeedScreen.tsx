import { StyleSheet } from 'react-native';
import { RootTabScreenProps } from '../../types';
import PoseCameraRTMP from '../components/LiveAnalysis_RTMPStream';

export default function VideoFeedScreen({ navigation }: RootTabScreenProps<'VideoFeed'>) {
  return <PoseCameraRTMP />;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    paddingBottom: 20,
  },
  trackingToggle: {

    marginTop: 'auto',
  },
});
