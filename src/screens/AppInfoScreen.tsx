import { FlatList, StyleSheet } from 'react-native';
import { Text, View } from '../components/Themed';
import Button from '../components/Button';

const infoMessages = [
  "My app uses your mobile phone camera to analyse your squat form and provide feedback during and after your lift.",
  "By analyzing your form, this app can help you improve your technique and reduce the risk of injury.",
  "Whether you're a beginner or an experienced weightlifter, this app can help you achieve your fitness goals.",
  "If you have any feedback or questions, please fill in the form below.",
]

export default function AppInfoScreen() {
  return (
    <View style={{ flex: 1 }}>
      <View style={styles.container}>
        <Text style={styles.title}>Info</Text>
        <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
        <FlatList
          style={{ height: '76%' }}
          data={infoMessages}
          renderItem={({ item }) => {
            return (
              <View style={styles.listItem}>
                <Text style={styles.mainInfoText}>{item}</Text>
              </View>
            );
          }}
          />
      </View>
      <View style={styles.feedbackButtonBar} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" >
        <Button
          title={'Feedback/Questions Form'}
          onPress={()=>{}}
          >
        </Button>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 20,
    paddingHorizontal: 15,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    alignSelf: 'center',
    textAlign: 'center'
  },
  separator: {
    marginVertical: 30,
    height: 1,
    width: '80%',
  },
  mainInfoText: {
    fontSize: 16,
    textAlign: 'center',
    alignSelf: 'center',
  },
  listItem: {
    paddingVertical: 10,
  },
  feedbackButtonBar: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingTop: 7,
    height: 70,
    width: '100%',
    position: 'absolute',
    bottom: 0
  }
});
