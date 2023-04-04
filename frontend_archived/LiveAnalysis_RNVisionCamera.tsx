import React, { useState, useEffect } from 'react';
import {
  Camera,
  useFrameProcessor,
  useCameraDevices,
  CameraPosition,
  Frame
} from 'react-native-vision-camera';
import { Text, View } from 'react-native';
import 'react-native-reanimated';

const SERVER_URL = 'http://192.168.0.28:5000/process_frame';

export default function PoseCameraRNVC() {
  const [formFeedback, setFormFeedback] = useState('No Feedback Yet');
  const [cameraPosition, setCameraPosition] = useState<CameraPosition>('back');
  const devices = useCameraDevices();
  const device = devices[cameraPosition];

  useEffect(() => {
    (async () => {
      const status = await Camera .requestCameraPermission();
      if (status !== 'authorized') {
        alert('Permission to access camera is required!');
        return;
      }
    })();
  }, []);

  const handleCameraFrame = async (frame: Frame) => {
    const base64Data = frame;
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
  };

  const frameProcessor = useFrameProcessor((frame) => {
    'worklet';
    setFormFeedback('Handling Frame, time: ' + Date.now());
    handleCameraFrame(frame);
  }, []);

  // const captureFrame = async () => {
  //   if (!isCapturing && cameraRef.current) {
  //     setIsCapturing(true); // Set the flag
  //     const frame = await cameraRef.current({ base64: true });
  //     handleCameraFrame(frame);
  //   }
  // };

  if (!device) {
    return (
      <Text>Loading...</Text>
    )
  }

  return (
    <View style={{flex: 1}}>
      <Camera
        style={{ flex: 1 }}
        device={device}
        isActive={true}
        frameProcessor={frameProcessor}
        frameProcessorFps={0.5} // default to 1 for now.
      />
      <Text style={{textAlign:'center', fontSize: 18}}>{formFeedback}</Text>
    </View>
  );
}
