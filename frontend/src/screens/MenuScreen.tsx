import { useEffect, useState } from 'react';
import { StyleSheet, Platform } from 'react-native';
import * as FileSystem from 'expo-file-system';
import * as ImagePicker from 'expo-image-picker';
import * as MediaLibrary from 'expo-media-library';
import Button from '../components/Button';
import { Text, View } from '../components/Themed';
import { RootTabScreenProps } from '../../types';

const ip = '192.168.0.28';
const UPLOAD_VIDEO_ENDPOINT = `http://${ip}:5000/upload_video`;

export default function MenuScreen({ navigation }: RootTabScreenProps<'Menu'>) {
  const [galleyButtonDisabled, setGalleryButtonDisabled] = useState<boolean>(true);

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

          console.log(finalSummary);
          navigation.navigate(
            'PostSetSummary',
            { summary: finalSummary, videoUri: asset.uri }
          );
        } else {
          console.warn('Response code ' + response.status);
        }
      }
    } catch (e) {
      console.warn(e);
    }
  }

  return (
    <View style={{flex: 1}}>
      <View style={styles.container}>
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
        </View>
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
