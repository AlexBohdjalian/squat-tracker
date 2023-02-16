import React, { useRef, useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, Dimensions } from 'react-native';
import { Camera } from 'expo-camera';
import WebSocket from 'react-native-websocket';

const screenWidth = Dimensions.get('screen').width;
const screenHeight = Dimensions.get('screen').height;

export default function PoseCamera() {
  const [isStreaming, setIsStreaming] = useState(false);
  const cameraRef = useRef();
  const wsRef = useRef();
  
  const onOpen = () => {
    console.log("WebSocket connection established");
  };

  const onMessage = (message) => {
    console.log(`WebSocket message received: ${message}`);
  };

  const onError = (error) => {
    console.error(`WebSocket error: ${error}`);
  };

  const onClose = () => {
    console.log("WebSocket connection closed");
  };

  useEffect(() => {
    const ws = new WebSocket("https://390c-86-8-102-74.eu.ngrok.io");
    ws.onopen = onOpen;
    ws.onmessage = onMessage;
    ws.onerror = onError;
    ws.onclose = onClose;
    wsRef.current = ws
  }, [])

  useEffect(() => {
    if (isStreaming && wsRef.current && cameraRef.current) {
      const camera: Camera = cameraRef.current;
      const sendFrame = async () => {
        const { uri } = await camera.takePictureAsync();
        console.log('Sending image...');
        wsRef.current.send(uri);
      };
      const intervalId = setInterval(sendFrame, 100);
      return () => {
        clearInterval(intervalId);
      };
    }
  }, [isStreaming, wsRef, cameraRef]);

  return (
    <View style={{ flex: 1 }}>
      <Camera
        ref={cameraRef}
        style={{ width: screenWidth, height: screenHeight }}
      />
      <TouchableOpacity
        style={{ position: "absolute", bottom: 20, right: 20 }}
        onPress={() => setIsStreaming(!isStreaming)}
      >
        <Text style={{ fontSize: 20 }}>
          {isStreaming ? "Stop" : "Start"}
        </Text>
      </TouchableOpacity>
    </View>
  );
};
