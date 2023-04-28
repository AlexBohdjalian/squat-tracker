import { StyleSheet } from 'react-native';

export default (streaming: boolean, android: boolean, warning: boolean, feedbackType: 'NONE' | 'GOOD' | 'TIP' | 'CRITICAL') =>
  StyleSheet.create({
    container: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      borderColor: feedbackType === 'GOOD' ? 'green' : feedbackType === 'TIP' ? 'darkorange' : feedbackType === 'CRITICAL' ? 'red' : 'transparent',
      borderWidth: feedbackType === 'NONE' ? 0 : 8,
    },
    formFeedbackContainer: {
      position: 'absolute',
      bottom: android ? 75 : 95,
      alignSelf: 'center',
      backgroundColor: 'rgba(232, 232, 232, 0.8)',
      borderRadius: 10,
      borderColor: '#7C7C7C',
      borderWidth: 3,
      marginBottom: 10,
      paddingHorizontal: 10,
      paddingVertical: 5,
    },
    formFeedbackText: {
      fontSize: 34,
      fontWeight: 'bold',
      textAlign: 'center',
    },    
    repCounterContainer: {
      position: 'absolute',
      top: android ? 20 : 40,
      alignSelf: 'center',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'rgba(232, 232, 232, 0.8)',
      width: '40%',
      height: '7%',
      borderRadius: 10,
      paddingHorizontal: 12,
      paddingVertical: 8,
      borderColor: '#7C7C7C',
      borderWidth: 3,
    },
    repCounterText: {
      fontSize: 20,
      fontWeight: 'bold',
      textAlign: 'center',
    },
    countdownTimerContainer: {
      position: 'absolute',
      alignSelf: 'center',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: 'rgba(232, 232, 232, 0.8)',
      width: 150,
      height: 150,
      borderRadius: 75, // Make the container circular
      borderColor: '#7C7C7C',
      borderWidth: 3,
    },
    countdownTimerText: {
      fontSize: 34,
      fontWeight: 'bold',
      textAlign: 'center',
    },
    livestreamView: {
      flex: 1,
      backgroundColor: 'black',
      alignSelf: 'stretch',
    },
    streamButton: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 60,
      width: streaming ? 50 : undefined,
      height: streaming ? 50 : undefined,
      backgroundColor: streaming ? undefined : '#E53101',
      paddingVertical: streaming ? undefined : 15,
      paddingHorizontal: streaming ? undefined : 25,
    },
    streamText: {
      color: '#FFFFFF',
      fontSize: 16,
      fontWeight: '700',
    },
    resolutionButton: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 50,
      backgroundColor: 'yellow',
      width: 50,
      height: 50,
    },
    audioButton: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: 50,
      height: 50,
    },
    cameraButton: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      width: 50,
      height: 50,
    },
    settingsButton: {
      position: 'absolute',
      display: 'flex',
      flexDirection: 'row',
      alignItems: 'center',
      top: android ? 20 : 60,
      right: 15,
      minHeight: 50,
      paddingVertical: 5,
      paddingHorizontal: 15,
      borderRadius: warning ? 60 : undefined,
      borderColor: '#FFFFFF',
      borderWidth: warning ? 0.5 : undefined,
      backgroundColor: warning ? '#DC3546' : undefined,
    },
    settingsIcon: {
      position: 'absolute',
      right: 10,
    },
    warningContainer: {
      marginRight: 20,
    },
    warning: {
      color: '#FFFFFF',
      fontSize: 10,
      fontWeight: '700',
    },
  });

interface IButtonParams {
  top?: number;
  bottom?: number;
  left?: number;
  right?: number;
}

export const button = (position: IButtonParams) =>
  StyleSheet.create({
    container: {
      position: 'absolute',
      top: position.top,
      bottom: position.bottom,
      left: position.left,
      right: position.right,
    },
  });
