import { useState, useRef } from 'react';
import { StyleSheet, ScrollView, LogBox } from 'react-native';
import { Video } from 'expo-av';
import { Table, Row, Rows } from 'react-native-table-component';
import { Text, View } from '../components/Themed';
import { RootStackParamList, RootStackScreenProps } from '../../types';
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
  const { summary, videoUri }: RootStackParamList["PostSetSummary"] = route.params;
  const tableHeaders = ['Rep', 'Mistake'];
  const tableData = summary.mistakesMade.map((mistakeInfo) => {
    return [mistakeInfo.rep, mistakeInfo.mistakes.map((mistake, index) => {
      const suffix = (index === mistakeInfo.mistakes.length - 1) ? '\n' : '';
      return `\n\u2022 ${mistake}${suffix}`;
    })];
  });

  if (displayVideo) {
    return (
      <View style={styles.container}>
        <Video
          source={{ uri: videoUri }}
          style={{ width: '100%', height: '91%' }}
          rate={1.0}
          isMuted={true}
          shouldPlay
          useNativeControls
          isLooping
        />
        <Button
          title="Go Back"
          onPress={() => setDisplayVideo(false)}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
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
      </ScrollView>

      <Button
        title="Watch Video Replay"
        onPress={() => setDisplayVideo(true)}
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
  backgroundVideo: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
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
  tableTitle: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  tableTitleText: {
    fontSize: 18,
    textAlign: 'center',
    maxHeight: 50,
    maxWidth: 200,
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
});
