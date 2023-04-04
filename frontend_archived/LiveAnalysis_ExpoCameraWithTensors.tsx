import React, { useState, useEffect, useRef } from 'react';
import { Camera, CameraType } from 'expo-camera';
import { View, Text, StyleSheet, Platform } from 'react-native';
import { cameraWithTensors } from '@tensorflow/tfjs-react-native';
import * as tf from '@tensorflow/tfjs-core';
import { GLView, ExpoWebGLRenderingContext } from 'expo-gl';


const SERVER_URL = 'http://192.168.0.28:5000/process_frame';
const TensorCamera = cameraWithTensors(Camera);

export default function PoseCameraExpoWithTensors() {
  const [formFeedback, setFormFeedback] = useState('');
  const cameraRef = useRef<Camera>();
  const [isCapturing, setIsCapturing] = useState(false);
  const textureDims = Platform.OS === "ios"
    ? { width: 1920, height: 1080 }
    : { width: 1200, height: 1600 };

  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      if (status !== 'granted') {
        alert('Permission to access camera is required!');
        return;
      }
    })();
  }, []);

  const handleCameraFrame = async (frame) => {
    const base64Data = frame.base64;
    const response = await fetch(SERVER_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        frame: base64Data,
      }),
    });
    const formFeedbackFromEndpoint = await response.text();
    setFormFeedback(formFeedbackFromEndpoint);
    setIsCapturing(false); // Reset the flag
  };

  // const captureFrame = async () => {
  //   if (!isCapturing && cameraRef.current) {
  //     setIsCapturing(true); // Set the flag
  //     const frame = await cameraRef.current.takePictureAsync({ base64: true });
  //     handleCameraFrame(frame);
  //   }
  // };

  const handleCameraStream = (images: IterableIterator<tf.Tensor3D>, updateCameraPreview: () => void, gl: ExpoWebGLRenderingContext, cameraTexture: WebGLTexture) => {
    const loop = async () => {
      const nextImageTensor = images.next().value;
      console.log('meow');
      console.log(nextImageTensor);

      // do something with tensor here
      handleCameraFrame(nextImageTensor)

      requestAnimationFrame(loop);
    }
    loop();
  }

  // TODO: need to find quick way to capture frames from camera
  return (
    <View style={styles.container}>
      <TensorCamera
        // Standard Camera Props
        style={styles.cameraPreview}
        type={CameraType.back}
        // Tensor Related Props
        cameraTextureHeight={textureDims.height}
        cameraTextureWidth={textureDims.width}
        resizeHeight={200} // change me?
        resizeWidth={152} // change me?
        resizeDepth={3}
        onReady={handleCameraStream}
        autorender={true}
        useCustomShadersToResize={false}
      >
        <Text>{formFeedback}</Text>
      </TensorCamera>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000',
    justifyContent: 'center'
  },
  cameraPreview: {
    flex: 1,
    height: '100%',
    width: '100%',
  }
})
