import React, { useEffect, useState } from 'react';
import { View, Text } from 'react-native';
// import * as tf from 'react-native-tensorflow';
import * as tf from '@tensorflow/tfjs';
// import { bundleResourceIO } from 'react-native-tensorflow'; 
import { PoseNet } from '@tensorflow-models/posenet';
// import * as posenet from '@tensorflow-models/posenet';


interface Pose {
  [key: string]: any;
}

const PoseDetector: React.FC = () => {
  const [pose, setPose] = useState<Pose | undefined>();
  const [model, setModel] = useState<PoseNet | undefined>();
  // const [weightManifest, setWeightManifest] = useState();

  useEffect(() => {
    async function loadAndPredict() {
      // Load the PoseNet model
      // const weightManifest = require('../assets/model/model-stride16.json');
      // const modelWeights = require('../assets/model/posenet_weights.bin');

      // 'https://tfhub.dev/tensorflow/tfjs-model/posenet/mobilenet/float/075/1/default/1';
      const modelUrl = 'https://tfhub.dev/google/imagenet/mobilenet_v2_140_224/classification/2';

      console.log('Loading posenet model...')
      const posenetModel = await tf.loadGraphModel(
        modelUrl,
        { fromTFHub: true }
      );
      setModel(posenetModel);
      console.log('Model loaded.')
        
      // const model = await posenet.load({
      //   architecture: 'MobileNetV1',
      //   outputStride: 16,
      //   inputResolution: { width: 640, height: 480 },
      //   multiplier: 0.75
      // });
      // setModel(model)

      // Get the image data
      // const image = await RNFS.readFileAssets('assets/squat.jpg', 'base64')
      // const imageTensor = tf.node.decodeImage(image, 3)
      const image = require('../assets/squat.jpg')

      const pose = await model.estimateSinglePose(image)
      setPose(JSON.parse(JSON.stringify(pose)))

      // Preprocess the image data
      // const preprocessed = tf.tensor4d(image, [1, image.height, image.width, 3], 'int32');

      // Run the model
      // const output = await posenet.predict(preprocessed);

      // Extract the poses from the model's output
      // const poses = tf.tensor(output[0], [output[1].height, output[1].width, 17], 'float32');

      // Analyze the form of the squat using the poses
      // ...
      // setPose(JSON.parse(JSON.stringify(poses)));
    }
    loadAndPredict();
  }, []);

  return (
    <View>
      {pose ? (
        <Text>{JSON.stringify(pose)}</Text>
      ) : (
        <Text>Loading...</Text>
      )}
    </View>
  );
};

export default PoseDetector;
