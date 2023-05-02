import { useEffect, useState } from 'react';
import { ActivityIndicator, StyleSheet, TextInput } from 'react-native';
import * as FileSystem from 'expo-file-system';
import * as ImagePicker from 'expo-image-picker';
import * as MediaLibrary from 'expo-media-library';
import Button from '../components/Button';
import { Text, View } from '../components/Themed';
import { FinalSummary, RootTabScreenProps } from '../../types';

const ip = '192.168.0.28';
const UPLOAD_VIDEO_ENDPOINT = `http://${ip}:5000/upload_video`;

export default function MenuScreen({ navigation }: RootTabScreenProps<'Menu'>) {
  const [galleyButtonDisabled, setGalleryButtonDisabled] = useState<boolean>(true);
  const [videoIsProcessing, setVideoIsProcessing] = useState<boolean>(false);
  const [errorOccurred, setErrorOccurred] = useState<boolean>(false);

  useEffect(() => {
    (async () => {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        alert('Sorry, we need camera roll permissions to make this work!');
      } else {
        setGalleryButtonDisabled(false);
      }
    })();
  }, []);

  const selectAndProcessVideo = async () => {
    try {
      // Fetch the video from the device gallery
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Videos,
        aspect: [4, 3],
        allowsEditing: true,
        quality: 1,
      });

      if (!result.canceled) {
        setVideoIsProcessing(true);
        // Send video to backend for processing
        const base64VideoData = await FileSystem.readAsStringAsync(result.assets[0].uri, {
          encoding: FileSystem.EncodingType.Base64,
        });
        const response = await fetch(UPLOAD_VIDEO_ENDPOINT, {
          method: 'POST',
          body: base64VideoData
        });

        if (response.status === 200) {
          const jsonData = await response.json();
          const processedBase64 = jsonData['processed_video'];
          const finalSummary = jsonData['final_summary'];

          // Save the video to the device
          const fileUri = FileSystem.documentDirectory + 'received_video.mp4';
          await FileSystem.writeAsStringAsync(fileUri, processedBase64, {
            encoding: FileSystem.EncodingType.Base64,
          });
          const asset = await MediaLibrary.createAssetAsync(fileUri);

          console.log(finalSummary)

          setVideoIsProcessing(false);
          navigation.navigate(
            'PostSetSummary',
            { summary: finalSummary, videoUri: asset.uri }
          );
        } else {
          setErrorOccurred(true);
          console.warn('Response code ' + response.status);
        }
      }
    } catch (e) {
      setErrorOccurred(true);
      console.warn(e);
    }
  }

  const clearError = () => {
    setVideoIsProcessing(false);
    setErrorOccurred(false);
  }

  // const testData: FinalSummary = {
  //   goodReps: 1,
  //   badReps: 3,
  //   mistakesMade: [
  //     {rep: 1, mistakes: []},
  //     {rep: 2, mistakes: ['Hips went out of alignment with feet', 'Shoulders went out of alignment with feet']},
  //     {rep: 3, mistakes: ['Hips went out of alignment with feet']},
  //     {rep: 4, mistakes: ['Hips went out of alignment with feet', 'Shoulders were not level', 'Shoulders went out of alignment with feet']},
  //   ],
  //   stateSequences: [
  //     {durations: [1.066868543624878, 0.1766049861907959], states: ['STANDING', 'TRANSITION', 'BOTTOM', 'TRANSITION']},
  //     {durations: [0.8746097087860107, 0.2374439239501953], states: ['STANDING', 'TRANSITION', 'BOTTOM', 'TRANSITION']},
  //     {durations: [0.9108970165252686, 0.3012425899505615], states: ['STANDING', 'TRANSITION']},
  //     {durations: [1.1003923004023002, 0.2652425899505615], states: ['STANDING', 'TRANSITION', 'BOTTOM', 'TRANSITION']},
  //   ],
  //   finalComments: 'NOT IMPLEMENTED YET'
  // }

  return (
    <View style={styles.container}>
      {videoIsProcessing ? (
        <>
        {errorOccurred ? (
          <>
            <Text>An error occurred</Text>
            <Button title={'Back to menu'} onPress={clearError()}/>
          </>
          ) : (
          <>
            <Text style={[styles.title, { marginBottom: 20 }]}>Video is processing</Text>
            <ActivityIndicator size={'large'} />
          </>
        )}
        </>
      ) : (
        <>
          <Text style={styles.title}>Choose an action</Text>
          <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
          <View style={styles.buttonsContainer}>
            <Button
              onPress={() => navigation.navigate('LiveFormAnalyser')}
              title="Go To Live Squat Tracker"
            />
            <Button
              onPress={selectAndProcessVideo}
              title="Select Video From Gallery"
              disabled={galleyButtonDisabled}
            />
            {/* <Button
              onPress={() => navigation.navigate(
                'PostSetSummary',
                {
                  summary: testData,
                  videoUri: ''
                }
              )}
              title="Test post set summary"
            /> */}
          </View>
        </>
      )}
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
  modalView: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 20,
    marginVertical: 250,
    backgroundColor: '#FFF',
    borderRadius: 20,
    padding: 35,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  videoModalView: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    margin: 20,
    backgroundColor: '#FFF',
    borderRadius: 20,
    paddingHorizontal: 40,
    paddingVertical: 60,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  squatFormData: {
    // flex: 1,
    // margin: 10,
    height: 40,
    backgroundColor: 'rgba(255,255,255,0.1)',
  },
  modalText: {
    marginBottom: 15,
    textAlign: 'center',
    fontWeight: 'bold',
    fontSize: 16,
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
