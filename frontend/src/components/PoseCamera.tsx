import { useState, useRef, useEffect } from 'react';
import useWebSocket, { ReadyState } from 'react-native-use-websocket';
import { Text, View } from 'react-native';
import { Camera, CameraType, FlashMode } from 'expo-camera';
import * as MediaLibrary from 'expo-media-library'


export default function PoseCamera() {
  const [socketUrl] = useState("https://390c-86-8-102-74.eu.ngrok.io");
  const [hasCameraPermission, setHasCameraPermission] = useState(false)
  const cameraRef = useRef();
  
  const {
    sendJsonMessage,
    lastJsonMessage,
    readyState
  } = useWebSocket(socketUrl, {
    shouldReconnect: (closeEvent) => true
  });

  // const image = require('../../assets/squat.jpg')
  // const sendP = () => sendJsonMessage(image);
  // const handleSendPic = useCallback(sendP, [sendP]);

  useEffect(() => {
    (async () => {
      MediaLibrary.requestPermissionsAsync();
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasCameraPermission(status === 'granted')
    })();
  }, [])

  const connectionStatus = {
    [ReadyState.CONNECTING]: "Connecting",
    [ReadyState.OPEN]: "Open",
    [ReadyState.CLOSING]: "Closing",
    [ReadyState.CLOSED]: "Closed",
    [ReadyState.UNINSTANTIATED]: "Uninstantiated",
  }[readyState];

  useEffect(() => {
    if (cameraRef.current && readyState === ReadyState.OPEN && hasCameraPermission) {
      const camera: Camera = cameraRef.current
      const sendFrame = async () => {
        console.log('sending message')
        const { uri } = await camera.takePictureAsync();
        sendJsonMessage(uri)
      }
      const intervalId = setInterval(sendFrame, 1000/ 30);
      return () => {
        clearInterval(intervalId);
      };
    }
  }, [cameraRef, readyState, hasCameraPermission]);

  return (
    <View>
      <Text>The WebSocket is currently {connectionStatus}</Text>
      {/* {lastJsonMessage.data ? <Image source={lastJsonMessage.data}/> : null} */}
      <Camera
        ref={cameraRef}
        style={{ flex: 1 }}
        flashMode={FlashMode.off}
        type={CameraType.back}
        autoFocus={false}
      />
    </View>
  );
}
