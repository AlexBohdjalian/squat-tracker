import React, { useState, useEffect, useRef } from 'react';
import { Camera, CameraType } from 'expo-camera';
import { View, Text, StyleSheet } from 'react-native';

const SERVER_URL = 'http://192.168.0.28:5000/process_frame';

export default function PoseCameraExpo() {
  const [formFeedback, setFormFeedback] = useState('');
  const cameraRef = useRef<Camera>();
  const [isCapturing, setIsCapturing] = useState(false);

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

  const captureFrame = async () => {
    if (!isCapturing && cameraRef.current) {
      setIsCapturing(true); // Set the flag
      const frame = await cameraRef.current.takePictureAsync({ base64: true });
      handleCameraFrame(frame);
    }
  };

  // TODO: need to find quick way to capture frames from camera
  return (
    <View style={styles.container}>
      <Camera
        ref={cameraRef}
        type={CameraType.back}
        onCameraReady={() => setInterval(captureFrame, 10)}
        style={styles.cameraPreview}
      >
        <Text>{formFeedback}</Text>
      </Camera>
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
