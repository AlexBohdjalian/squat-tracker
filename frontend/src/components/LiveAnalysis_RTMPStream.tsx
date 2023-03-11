
import React, { useState, useEffect, useRef } from 'react';
import { Text, View, StyleSheet, TouchableOpacity } from 'react-native';
import { NodeCameraView } from 'react-native-nodemediaclient';


export default function CameraStream() {
  // const [hasPermission, setHasPermission] = useState(null);
  const clientRef = useRef<NodeCameraView>(null);



  const startStreaming = () => {
    clientRef.current.start();
  };

  const stopStreaming = () => {
    clientRef.current.stop();
  };

  // if (hasPermission === null) {
  //   return <View />;
  // }

  // if (hasPermission === false) {
  //   return <Text>No access to camera</Text>;
  // }

  return (
    <View style={styles.container}>
      <NodeCameraView 
        style={{ height: 400 }}
        ref={(vb) => {this.vb = vb}}
        outputUrl = {"rtmp://192.168.0.28:5000/live/stream"}
        camera={{ cameraId: 1, cameraFrontMirror: true }}
        audio={{ bitrate: 32000, profile: 1, samplerate: 44100 }}
        video={{ preset: 12, bitrate: 400000, profile: 1, fps: 15, videoFrontMirror: false }}
        autopreview={true}
      >
        <View
          style={{
            flex: 1,
            backgroundColor: 'transparent',
            flexDirection: 'row',
          }}
        >
          <TouchableOpacity
            style={{
              flex: 0.1,
              alignSelf: 'flex-end',
              alignItems: 'center',
            }}
          >
            <Text style={{ fontSize: 18, marginBottom: 10, color: 'white' }}> Flip </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={{
              flex: 0.1,
              alignSelf: 'flex-end',
              alignItems: 'center',
            }}
            onPress={startStreaming}
          >
            <Text style={{ fontSize: 18, marginBottom: 10, color: 'white' }}> Start </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={{
              flex: 0.1,
              alignSelf: 'flex-end',
              alignItems: 'center',
            }}
            onPress={stopStreaming}
          >
            <Text style={{ fontSize: 18, marginBottom: 10, color: 'white' }}> Stop </Text>
          </TouchableOpacity>
        </View>
      </NodeCameraView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
});
