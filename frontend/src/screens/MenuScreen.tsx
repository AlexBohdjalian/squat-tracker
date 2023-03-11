import axios from 'axios';
import { useEffect, useState } from 'react';
import { StyleSheet, Modal, ActivityIndicator, Platform } from 'react-native';
import * as FileSystem from 'expo-file-system';
import * as ImagePicker from 'expo-image-picker';
import * as MediaLibrary from 'expo-media-library';
import Button from '../components/Button';
import { Text, View } from '../components/Themed';
import { RootTabScreenProps } from '../../types';

enum ModalStates {
  NOT_VISIBLE = 'not-visible',
  PROCESSING = 'processing',
  SAVING = 'saving',
  DONE = 'done',
}

export default function MenuScreen({ navigation }: RootTabScreenProps<'Menu'>) {
  const [modalState, setModalState] = useState<ModalStates>(ModalStates.NOT_VISIBLE);
  const [savedVideoUri, setSavedVideoUri] = useState('');
  const [squatFormData, setSquatFormData] = useState();

  // useEffect that asks for MediaLibrary permissions once at the start
  useEffect(() => {
    (async () => {
      const { status } = await MediaLibrary.requestPermissionsAsync();
      if (status !== 'granted') {
        alert('Sorry, we need camera roll permissions to make this work!');
      }
    })();
  }, []);

  const getModalText = (state: ModalStates) => {
    if (state == ModalStates.PROCESSING) {
      return 'Video is being processed'
    }
    if (state == ModalStates.SAVING) {
      return 'Processed video is being saved'
    }
    if (state == ModalStates.DONE) {
      return 'Done'
    }
  }

  const handleSeeVideo = () => {
    setModalState(ModalStates.NOT_VISIBLE);
    if (savedVideoUri && squatFormData) {
      navigation.navigate('FormReview', { videoUri: savedVideoUri, formData: squatFormData });
    }
  }

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
        setModalState(ModalStates.PROCESSING)

        const base64VideoData = await FileSystem.readAsStringAsync(result.assets[0].uri, {
          encoding: FileSystem.EncodingType.Base64,
        });

        try {
          // think about what data should be received and how to display
          // TODO: consider using filestream here to improve speed
          // TODO: or, use this https://narainsreehith.medium.com/upload-image-video-to-flask-backend-from-react-native-app-expo-app-1aac5653d344
          const { data } = await axios.post('http://192.168.0.28:5000/process_video', {
            'video': base64VideoData
          });
          const videoData = data['video']
          setSquatFormData(data['analysis'])

          setModalState(ModalStates.SAVING);
          // Save the received video (video_data)
          const fileUri = FileSystem.documentDirectory + 'received_video.mp4';
          FileSystem.writeAsStringAsync(fileUri, videoData, {
            encoding: FileSystem.EncodingType.Base64,
          });

          // save this to an asset album e.g. 'SquatTracker'
          const asset = await MediaLibrary.createAssetAsync(fileUri);
          if (Platform.OS === 'ios') {
            const hash = asset.id.split('/')[0];
            const videoUri = `assets-library://asset/asset.mp4?id=${hash}&ext=mp4`;
            setModalState(ModalStates.DONE);
            setSavedVideoUri(videoUri);
          } else {
            const videoUri = asset.uri;
            setModalState(ModalStates.DONE);
            setSavedVideoUri(videoUri);
          }
        } catch (e) {
          setModalState(ModalStates.NOT_VISIBLE) // change this to error // also change modal to be component
          console.warn(e);
        }
      }
    } catch (e) {
      console.warn(e)
    }
  }

  return (
    <View style={{flex: 1}}>
      <View style={styles.container}>
        <Text style={styles.title}>Choose an action</Text>
        <View style={styles.separator} lightColor="#eee" darkColor="rgba(255,255,255,0.1)" />
        <View style={styles.buttonsContainer}>
          <Button
            onPress={() => navigation.navigate('VideoFeed')}
            title="Go To Live Squat Tracker (NOT WORKING YET)"
          />
          <Button
            onPress={selectAndProcessVideo}
            title="Select Video From Gallery"
          />
          <Button
            onPress={() => {}} // TODO: this
            title="See Previous Lifts (NOT WORKING YET)"
          />
        </View>
      </View>
      <Modal
        animationType='slide'
        transparent={true}
        visible={modalState != ModalStates.NOT_VISIBLE}
        onRequestClose={() => setModalState(ModalStates.NOT_VISIBLE)}
      >
        <View style={styles.modalView}>
          <Text style={styles.modalText}>{getModalText(modalState)}</Text>
          {modalState == ModalStates.DONE? (
            <Button title="See Video" onPress={handleSeeVideo} />
          ) : (
            <ActivityIndicator size={'small'} />
          )}
        </View>
      </Modal>
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
