import { useState, useEffect } from 'react';
import { Text, StyleSheet } from 'react-native';
import { Video } from 'expo-av';
import { View } from '../components/Themed';
import { RootTabScreenProps } from '../../types';
import Button from '../components/Button';

export default function FormReviewScreen({ route, navigation }: RootTabScreenProps<'FormReview'>) {
  /**
   * This Screen is deprecated.
   */
  const [savedVideoUri, setSavedVideoUri] = useState<string>('');
  const [squatFormData, setSquatFormData] = useState<{'reps': []}>();
  const [showVideo, setShowVideo] = useState<boolean>(false);
  const [percent1RM, setPercent1RM] = useState<number>(0.9);

  useEffect(() => {
    const { videoUri, formData } = route.params;
    setSavedVideoUri(videoUri);
    setSquatFormData(formData);
  }, []);

  const getButtonText = (showVideo) => {
    if (showVideo) {
      return 'See Form Data';
    } else {
      return 'See Video';
    }
  }

  function arraysEqual(arr1, arr2) {
    if (arr1.length !== arr2.length) {
      return false;
    }
    for (let i = 0; i < arr1.length; i++) {
      if (arr1[i] !== arr2[i]) {
        return false;
      }
    }
    return true;
  }

  const calculateRPE = (reps) => {
    const repTimes = reps.map((value, _) => { return value[0][1] });
  
    const targetVelocity = repTimes[repTimes.length - 1] / repTimes[0];
    const RIR = Math.log(percent1RM) / Math.log(targetVelocity);

    // Calculate the estimated RPE based on the RIR
    const RPE = 10 - RIR;
    return RPE;
  }

  const determineRepQuality = (rep) => {
    return arraysEqual(rep, ["Standing", "Transition", "Bottom", "Transition"]) ?
        "Good Rep!"
      : "Bad Rep!";
  }

  if (!squatFormData || !savedVideoUri) {
    return (
      <View style={styles.container}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {showVideo ? (
        <Video
          source={{ uri: savedVideoUri }}
          style={{ width: '100%', height: '85%' }}
          rate={1.0}
          isMuted={true}
          shouldPlay
          isLooping
        />
      ) : (
        <View style={styles.formDataContainer}>
          {squatFormData.reps.map((rep, index) => (
            <View style={styles.repDetailsContainer} key={index}>
              <Text style={styles.repDetailsText}>Rep {index + 1}</Text>
              <Text style={styles.repDetailsText}>Eccentric Duration: {JSON.stringify(Math.round(rep[0][0] * 1000) / 1000)}</Text>
              <Text style={styles.repDetailsText}>Concentric Duration: {JSON.stringify(Math.round(rep[0][1] * 1000) / 1000)}</Text>
              <Text style={styles.repDetailsText}>Rep Quality: {determineRepQuality(rep[1])}</Text>
            </View>
          ))}
          <Text>* STATE ASSUMPTIONS/CAVEATS HERE *</Text>
          <Text>Assuming {percent1RM*100}% of 1RM</Text>
          <Text>Estimated RPE: {calculateRPE(squatFormData.reps)}</Text>
        </View>
      )}
      <View style={{ flexDirection: 'column' }}>
        <Button
          title={getButtonText(showVideo)}
          onPress={() => setShowVideo(!showVideo)}
        />
        <Button
          title="Close Video"
          onPress={() => navigation.navigate('Root')}
        />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 30,
  },
  videoViewContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  formDataContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  repDetailsContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 12,
    paddingBottom: 20,
  },
  repDetailsText: {
    fontSize: 14,
    textAlign: 'center',
  },
});
