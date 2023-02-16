import { useEffect, useState, useRef } from 'react';
import { Text, View, StyleSheet, Platform, Image } from 'react-native';
import { Camera, CameraType, FlashMode } from 'expo-camera';
import * as tf from '@tensorflow/tfjs';
import { cameraWithTensors } from '@tensorflow/tfjs-react-native';
import { tensorToBase64 } from './TensorToJpeg';
import axios from 'axios';

const TensorCamera = cameraWithTensors(Camera);

export default function PoseCamera() {
  const cameraRef = useRef();
  const [hasCameraPermission, setHasCameraPermission] = useState(false);
  const [processedFrame, setProcessedFrame] = useState();
  const textureDim =
    Platform.OS === "ios"
      ? { width: 1920, height: 1080 }
      : { width: 1200, height: 1600 };
  let requestAnimationFrameId = 0;
    
  useEffect(() => {
    (async () => {
      const { status } = await Camera.requestCameraPermissionsAsync();
      setHasCameraPermission(status === 'granted')
    })();
  }, []);

  useEffect(() => {
    return () => {
      cancelAnimationFrame(requestAnimationFrameId);
    };
  }, [requestAnimationFrameId]);

  const handleCameraStream = (images, updatePreview, gl, cameraTexture) => {
    // console.log('camera ready')
    const loop = async () => {
      console.log('Entering loop')
      console.log(images)
      const nextImageTensor = images.next().value;
      console.log(nextImageTensor)

      const base64Frame = await tensorToBase64(nextImageTensor);
      tf.dispose(nextImageTensor);

      const { data } = await axios.post('http://192.168.0.28:5000/process_frame', {
        'frame': base64Frame
      })

      // display data somehow
      setProcessedFrame(data)
  
      requestAnimationFrameId = requestAnimationFrame(loop);
    }

    loop();
  }

  return (
    <View style={styles.container}>
      {hasCameraPermission ? (
        <TensorCamera
          ref={cameraRef}
          // Standard Camera props
          style={styles.camera}
          type={CameraType.front}
          flashMode={FlashMode.off}
          // Tensor related props
          cameraTextureHeight={textureDim.height}
          cameraTextureWidth={textureDim.width}
          resizeHeight={200}
          resizeWidth={152}
          resizeDepth={3}
          onReady={handleCameraStream}
          autorender={true}
          useCustomShadersToResize={false}
        />
      ) : (
        <Text>NO CAMERA PERMISSION</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFF',
    alignItems: 'center',
    justifyContent: 'center',
  },
  camera: {
    flex: 1,
    width: '100%',
    height: '100%',
  },
})
