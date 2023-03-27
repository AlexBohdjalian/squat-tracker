import React, { useState, useEffect, useRef } from 'react';
import { View } from 'react-native';
import { Camera, CameraType } from 'expo-camera';
import NodeMediaClient from 'react-native-nodemediaclient';

export default function PoseCameraNMC() {
  const [client, setClient] = useState(null);
  const [endpoint, setEndpoint] = useState('rtmp://192.168.0.28:1935/form_analyser');
  const cameraRef = useRef(null);

  useEffect(() => {
    if (client) {
      client.connect(endpoint);
      return () => {
        client.stop();
      };
    }
  }, [client, endpoint]);

  useEffect(() => {
    const createClient = async () => {
      const newClient = new NodeMediaClient();
      await newClient.prepare('rtc', true);
      newClient.setCameraPreview(cameraRef.current);
      setClient(newClient);
    };
    createClient();
  }, []);

  return (
    <View style={{ flex: 1 }}>
      {client && (
        <NodeMediaClient
          ref={(ref) => {
            setClient(ref);
          }}
          style={{ flex: 1 }}
          outputUrl={endpoint}
          video={{ preset: 12, fps: 10, bitrate: 4000000, profile: 1 }}
          audio={{ bitrate: 0 }}
          autopreview={false}
        />
      )}
      <Camera
        style={{ flex: 1 }}
        type={CameraType.back}
        ratio={'16:9'}
        ref={cameraRef}
      />
    </View>
  );
};
