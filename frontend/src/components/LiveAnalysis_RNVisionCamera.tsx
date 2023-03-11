import React, { useState, useEffect, useRef } from 'react';
import { Camera, useFrameProcessor, useCameraDevices, CameraPosition, Frame } from 'react-native-vision-camera';
import { Text } from 'react-native';

const SERVER_URL = 'http://192.168.0.28:5000/process_frame';

export default function PoseCameraRNVC() {
  const [formFeedback, setFormFeedback] = useState('');
  const [cameraPosition, setCameraPosition] = useState<CameraPosition>('back');
  const devices = useCameraDevices();
  const device = devices[cameraPosition];

  useEffect(() => {
    (async () => {
      const status = await Camera.requestCameraPermission();
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
    handleCameraFrame(frame);
  }, []);

  // const captureFrame = async () => {
  //   if (!isCapturing && cameraRef.current) {
  //     setIsCapturing(true); // Set the flag
  //     const frame = await cameraRef.current({ base64: true });
  //     handleCameraFrame(frame);
  //   }
  // };

  return (
    <Camera
      device={device}
      isActive={true}
      frameProcessor={frameProcessor}
      frameProcessorFps={1} // default to 1 for now.
    >
      <Text>{formFeedback}</Text>
    </Camera>
  );
}
