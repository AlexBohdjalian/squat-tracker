import { Camera, CameraType, FlashMode } from 'expo-camera';
import CameraButton from './CameraButton';
import React, { useEffect, useRef, useState } from 'react';
import { StyleSheet, Text, useWindowDimensions, View } from 'react-native';
import * as MediaLibrary from 'expo-media-library'

export default function LocalCamera() {
  const [hasCameraPermission, setHasCameraPermission] = useState(false);
  const [type, setType] = useState(CameraType.back);
  const [flash, setFlash] = useState(FlashMode.off);
  const cameraRef = useRef(null);

  useEffect(() => {
    (async () => {
      // MediaLibrary.requestPermissionsAsync();
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasCameraPermission(status === 'granted')
    })();
  }, [])

  const { width } = useWindowDimensions();
  const height = Math.round((width * 16) / 9);

  if (hasCameraPermission === null) {
    return (
      <View style={styles.information}>
        <Text>Waiting for camera permissions</Text>
      </View>
    );
  } else if (hasCameraPermission === false) {
    return (
      <View style={styles.information}>
        <Text>No access to camera</Text>
      </View>
    );
  } else {
    return (
      <View style={styles.container}>
        <Camera
          style={{...styles.cameraPreview, height: height}}
          ref={cameraRef}
          flashMode={flash}
          type={type}
        >
          <View style={styles.cameraButtonsContainer}>
            <CameraButton
              icon={'retweet'}
              onPress={() => {
                if (type === CameraType.front) setFlash(FlashMode.off);
                setType(type === CameraType.back ? CameraType.front : CameraType.back);
              }}
            />
            <CameraButton
              icon={'flash'}
              color={flash === FlashMode.off ? 'gray' : '#f1f1f1'}
              onPress={() => {
                setFlash(flash === FlashMode.off
                  ? FlashMode.torch
                  : FlashMode.off
                )
              }}
              disabled={type === CameraType.front}
            />
          </View>
        </Camera>
      </View>
    );
  }
}

const styles = StyleSheet.create({
  information: { 
    flex: 1,
    justifyContent: 'center',
    alignContent: 'center',
    alignItems: 'center',
  },
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center'
  },
  cameraButtonsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 30,
  },
  cameraPreview: {
    flex: 1,
    width: '100%',
  }
});