import { useState } from 'react';
import { StyleSheet, Modal, ActivityIndicator, SafeAreaView } from 'react-native';
import { Video } from 'expo-av';
import Button from '../components/Button';
import { Text, View } from '../components/Themed';
import { RootTabScreenProps } from '../../types';
import * as ImagePicker from 'expo-image-picker';
import axios from 'axios';
import * as FileSystem from 'expo-file-system';
import * as MediaLibrary from 'expo-media-library';


export default function MenuScreen({ navigation }: RootTabScreenProps<'Menu'>) {
  const [modalState, setModalState] = useState<'NOT_VISIBLE'|'PROCESSING'|'SAVING'|'DONE'>('NOT_VISIBLE');
  const [savedVideoUri, setSavedVideoUri] = useState('');
  const [displaySavedVideo, setDisplaySavedVideo] = useState(false);
  const [squatFormData, setSquatFormData] = useState();

  const getModalText = (state) => {
    if (state == 'PROCESSING') {
      return 'Video is being processed'
    }
    if (state == 'SAVING') {
      return 'Processed video is being saved'
    }
    if (state == 'DONE') {
      return 'Done'
    }
  }

  const openSavedVideo = async () => {
    setModalState('NOT_VISIBLE')
    
    if (savedVideoUri != '') {
      console.log('Opening: ' + savedVideoUri)
      
      setDisplaySavedVideo(true)
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
        setModalState('PROCESSING')

        const base64VideoData = await FileSystem.readAsStringAsync(result.assets[0].uri, {
          encoding: FileSystem.EncodingType.Base64,
        });

        try {
          // think about what data should be received and how to display
          const { data } = await axios.post('http://192.168.0.28:5000/process_video', {
            'video': base64VideoData
          });
          const videoData = data['video']
          setSquatFormData(data['analysis'])

          setModalState('SAVING');
          // Save the received video (video_data)
          const fileUri = FileSystem.documentDirectory + 'received_video.mp4';
          FileSystem.writeAsStringAsync(fileUri, videoData, {
            encoding: FileSystem.EncodingType.Base64,
          });

          const asset = await MediaLibrary.createAssetAsync(fileUri);
          setSavedVideoUri(asset.uri);
          setModalState('DONE');
        } catch (e) {
          setModalState('NOT_VISIBLE') // change this to error // also change modal to be component
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
        visible={displaySavedVideo}
      >
        <View style={styles.videoModalView}>
          <Video
            source={{ uri: savedVideoUri }}
            style={{ width: '100%', height: '85%' }}
            rate={1.0}
            isMuted={true}
            shouldPlay
            isLooping
          />
          <Text>{JSON.stringify(squatFormData)}</Text>
          <Button
            title="Close Video"
            onPress={() => setDisplaySavedVideo(false)}
          />
        </View>
      </Modal>
      <Modal
        animationType='slide'
        transparent={true}
        visible={modalState != 'NOT_VISIBLE'}
        onRequestClose={() => setModalState('NOT_VISIBLE')}
      >
        <View style={styles.modalView}>
          <Text style={styles.modalText}>{getModalText(modalState)}</Text>
          { modalState == 'DONE' ? (
            <Button title="See Video" onPress={openSavedVideo}/>
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
