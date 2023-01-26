import { StyleSheet } from 'react-native';
import Button from '../components/Button';
import AddGifImage from '../components/ComingSoonGif';
import { Text, View } from '../components/Themed';
import { RootTabScreenProps } from '../types';

export default function MenuScreen({ navigation }: RootTabScreenProps<'Menu'>) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Choose an action</Text>
      <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
      <View style={styles.buttonsContainer}>
        <Button
          onPress={() => navigation.navigate('VideoFeed')}
          title="Go To Squat Tracker"
        />
        <Button
          onPress={() => {}} // TODO: this
          title={'See Previous Lifts'}
        >
          <AddGifImage />
        </Button>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
    paddingHorizontal: 15,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: '80%',
  },
  buttonsContainer: {
    marginVertical: 10,
    alignItems: 'center',
  },
});
