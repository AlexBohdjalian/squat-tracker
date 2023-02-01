import React, { useState, useEffect, useRef } from 'react';
import { Camera } from 'expo-camera';
import { View, Text, Image } from 'react-native';

const PoseCamera = () => {
  const [hasCameraPermission, setHasCameraPermission] = useState(null);
  const [feed, setFeed] = useState(null);

  useEffect(() => {
    (async () => {
    //   MediaLibrary.requestPermissionsAsync();
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasCameraPermission(status === 'granted');
    })();
  }, [])

  useEffect(() => {
    if (hasCameraPermission) {
      const camera = Camera;
      camera.startPreview();
      setFeed(camera.getPreviewTexture());
    }
  }, [hasCameraPermission]);

  // const sendDataToAPI = async (base64) => {
  //   try {
  //     const response = await fetch('http://localhost:8888', {
  //       method: 'POST',
  //       headers: {
  //         'Content-Type': 'application/json'
  //       },
  //       body: JSON.stringify({ image: base64 })
  //     });
  //     const responseJson = await response.json();
  //     setFrame(overlayLandmarks(base64, responseJson));
  //   } catch (error) {
  //     console.error(error);
  //   }
  // };

  const overlayLandmarks = (base64, responseJson) => {
    // implement the function to overlay the landmarks on the image
    return base64;
  };

  if (hasCameraPermission === null) {
    return <View />;
  }
  if (hasCameraPermission === false) {
    return <Text>No access to camera</Text>;
  }
  return (    
    <View style={{ flex: 1 }}>
      <Text>Camera working</Text>
      {feed && <Camera.Preview feed={feed} />}
      {/*  <Image
         source={{ uri: frame }}
         style={{ flex: 1 }}
       /> */}
    </View>
  );
};

export default PoseCamera;
