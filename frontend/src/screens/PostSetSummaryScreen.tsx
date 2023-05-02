import { useState } from 'react';
import { StyleSheet, ScrollView, LogBox, TextInput } from 'react-native';
import { Video } from 'expo-av';
import { Table, Row, Rows } from 'react-native-table-component';
import { Text, View } from '../components/Themed';
import { FinalSummary, RootStackParamList, RootStackScreenProps } from '../../types';
import Button from '../components/Button';
import { RouteProp } from '@react-navigation/native';

// NOTE: there is a bug in react-native-table-component that can be ignored
LogBox.ignoreLogs(['Warning: Failed prop type: Invalid prop `textStyle` of type `array` supplied to `Cell`, expected `object`.'])

interface IProps {
  navigation: RootStackScreenProps<'PostSetSummary'>;
  route: RouteProp<RootStackParamList, 'PostSetSummary'>;
}

export default function PostSetSummaryScreen({ navigation, route }: IProps) {
  const [displayVideo, setDisplayVideo] = useState<boolean>(false);
  const [canDoRpe, setCanDoRpe] = useState<boolean>(false);
  const [input1RM, setInput1RM] = useState('');
  const [weightUsed, setWeightUsed] = useState('');
  const { summary, videoUri }: RootStackParamList["PostSetSummary"] = route.params;
  const tableHeaders = ['Rep', 'Mistake'];
  const tableData = summary.mistakesMade
    .filter(mistakeInfo => mistakeInfo.mistakes.length > 0)
    .map(mistakeInfo => [
      mistakeInfo.rep,
      mistakeInfo.mistakes.map((mistake, index) => {
        const suffix = (index === mistakeInfo.mistakes.length - 1) ? '\n' : '';
        return `\n\u2022 ${mistake}${suffix}`;
      })
  ]);

  function arraysEqual(arr1, arr2) {
    if (arr1.length !== arr2.length) return false;
    if (arr1 == null || arr2 == null) return false;

    for (let i = 0; i < arr1.length; i++) {
      if (arr1[i] !== arr2[i]) return false;
    }
    return true;
  }

  const determineRepQuality = (rep: string[]) => {
    let repQuality = 'Unable to determine.';
    if (arraysEqual(rep, ["STANDING", "TRANSITION", "BOTTOM", "TRANSITION"])) {
      repQuality = 'The quality of the rep was good!';
    } else if (arraysEqual(rep, ["STANDING", "TRANSITION"])) {
      repQuality = 'Depth in this rep may have been poor.'
    } else if (arraysEqual(rep, ["STANDING", "TRANSITION", "BOTTOM", "TRANSITION"])) {
      repQuality = 'Your knees may not have fully locked out in this rep.'
    }

    return repQuality;
  }

  const handleDoRpe = () => {
    if (canDoRpe) {
      setCanDoRpe(false);
    } else if (!Number.isNaN(input1RM) && parseFloat(input1RM) > 0 && parseFloat(weightUsed) > 0) {
      setCanDoRpe(true);
    }
  }

  const calculateRPE = (reps: FinalSummary['stateSequences']) => {
    // NOTE: This is an attempt that did not work

  //   // NOTE: weightUsed and input1RM are retrived from user input from textboxes
  //   const percent1RM = parseFloat(weightUsed) / parseFloat(input1RM);

  //   const firstRepConcentric = reps[0].durations[1];
  //   const lastRepConcentric = reps[reps.length - 1].durations[1];

  //   const targetVelocity = lastRepConcentric / firstRepConcentric;
  //   const RIR = Math.log(percent1RM) / Math.log(targetVelocity);

  //   const RPE = 10 - RIR;
  //   return roundNumber(RPE, 1);

    return 'This feature does not currently work :(';
  }

  const roundNumber = (num: number, dp: number) => {
    const pow = Math.pow(10, dp);
    return JSON.stringify(Math.round(num * pow) / pow);
  }

  return (
    <View style={styles.container}>
      {displayVideo ? (
        <Video
          source={{ uri: videoUri }}
          style={{ width: '100%', height: '91%' }}
          rate={1.0}
          isMuted={true}
          shouldPlay
          useNativeControls
        />
      ) : (
        <ScrollView style={styles.scrollView}>
          <Text style={[styles.textBold, { marginBottom: 0 }]}>Reps Complete</Text>
          <View style={styles.repsContainer}>
            <View>
              <Text style={styles.textBold}>Good Reps</Text>
              <Text style={styles.text}>{summary.goodReps}</Text>
            </View>

            <View>
              <Text style={styles.textBold}>Bad Reps</Text>
              <Text style={styles.text}>{summary.badReps}</Text>
            </View>
          </View>
          <View style={styles.separator} />

          <Text style={styles.textBold}>Mistakes Made</Text>
          <Table borderStyle={{borderWidth: 1}}>
            <Row
              data={tableHeaders}
              style={styles.headerRow}
              flexArr={[1, 3]}
              textStyle={styles.headerText}
            />
            <Rows
              data={tableData}
              flexArr={[1, 3]}
              style={styles.row}
              textStyle={styles.rowText}
            />
          </Table>
          <View style={[styles.separator, { marginTop: 40 }]} />

          <View style={styles.finalCommentsContainer}>
            <Text style={styles.textBold}>Final Comments</Text>
            <Text style={styles.text}>"{summary.finalComments}"</Text>
          </View>
          <View style={[styles.separator, { marginTop: 40 }]} />
          
          <View style={styles.detailedRepsContainer}>
            <Text style={styles.textBold}>Detailed Breakdown of Reps</Text>
            {summary.stateSequences.map((sequence, index) => (
              <View key={index} style={{ alignItems: 'center', marginBottom: 20 }}>
                <Text style={styles.textBold}>Rep: {index}</Text>
                <Text style={styles.text}>Eccentric time: {roundNumber(sequence.durations[0], 3)} secs</Text>
                <Text style={styles.text}>Concentric time: {roundNumber(sequence.durations[1], 3)} secs</Text>
                <Text style={styles.text}>Overall: {determineRepQuality(sequence.states)}</Text>
              </View>
            ))}
          </View>
          <View style={[styles.separator, { marginTop: 40 }]} />

          <View style={{ alignItems: 'center' }}>
            <Text style={styles.textBold}>Rating of Perceived Exertion (RPE)</Text>
            {canDoRpe ? (
              <View style={{ alignItems: 'center' }}>
                <Text style={styles.text}>Estimated RPE: {calculateRPE(summary.stateSequences)}</Text>
                <Button
                  title={'Try again'}
                  onPress={handleDoRpe}
                  style={{ width: '40%', height: '26%', marginTop: 0 }}
                />
              </View>
            ) : (
              <View style={{ flexDirection: 'row' }}>
                <View>
                  <TextInput
                    style={styles.textInput}
                    onChangeText={setInput1RM}
                    value={input1RM}
                    placeholder="Enter 1 rep max (kg)"
                    keyboardType="numeric"
                  />
                  <TextInput
                    style={styles.textInput}
                    onChangeText={setWeightUsed}
                    value={weightUsed}
                    placeholder="Enter weight used (kg)"
                    keyboardType="numeric"
                  />
                </View>
                <Button
                  title={'Calculate RPE'}
                  onPress={handleDoRpe}
                  style={{ width: '40%', height: '40%', marginTop: 40 }}
                />
              </View>
            )}
          </View>
          <View style={[styles.separator, { marginTop: 40 }]} />
        </ScrollView>
      )}

      <Button
        title={displayVideo ? 'Go Back' : 'Watch Video Replay'}
        onPress={() => setDisplayVideo(!displayVideo)}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 20,
  },
  scrollView: {
    width: '100%',
    paddingVertical: 20,
    marginBottom: 10,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  textBold: {
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 10,
  },
  text: {
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 10,
  },
  separator: {
    alignSelf: 'center',
    marginVertical: 30,
    height: 1,
    width: '90%',
    backgroundColor: '#000',
  },
  repsContainer: {
    width: '100%',
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingHorizontal: 30,
    marginTop: 20,
  },
  headerRow: {
    backgroundColor: '#FFFFFF',
  },
  headerText: {
    fontWeight: 'bold',
    textAlign: 'center',
    fontSize: 18,
  },
  row: {
    flex: 3,
    borderBottomWidth: 1,
    borderColor: '#CCC',
  },
  rowText: {
    textAlign: 'center',
    paddingHorizontal: 14,
    fontSize: 18,
  },
  finalCommentsContainer: {
    paddingBottom: 20,
  },
  detailedRepsContainer: {
    alignItems: 'center',
  },
  textInput: {
    height: 40,
    margin: 12,
    borderWidth: 1,
    padding: 10,
  },
});
