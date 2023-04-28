import axios from 'axios';
import React, { useEffect, useState, useRef } from 'react';
import {
  View,
  TouchableOpacity,
  Platform,
  Text,
  StatusBar,
  Animated,
} from 'react-native';
import {
  LiveStreamView,
  LiveStreamMethods,
  Resolution,
} from '@api.video/react-native-livestream';
import Icon from 'react-native-vector-icons/Ionicons';
import styles, { button } from '../styles/LiveFormAnalyserStyle';
import { FinalSummary, RootStackScreenProps } from '../../types';
import Button from '../components/Button';


export interface ISettingsState {
  resolution: Resolution;
  framerate: number;
  videoBitrate: number;
  rtmpEndpoint: string;
  streamKey: string;
}

type FormFeedback = {
  tag: string;
  message?: string;
  summary?: FinalSummary;
};

const ip = '192.168.0.28';
const FEEDBACK_URL = `http://${ip}:5000/form-feedback`;
const abortController = new AbortController();

export default function LiveFormAnalyser({ navigation }: RootStackScreenProps<'LiveFormAnalyser'>) {
  const [streaming, setStreaming] = useState(false);
  const [setStarted, setSetStarted] = useState<boolean>(false);
  const [feedbackType, setFeedbackType] = useState<'NONE'|'GOOD'|'TIP'|'CRITICAL'>('NONE');
  const [feedbackTimer, setFeedbackTimer] = useState<ReturnType<typeof setTimeout> | null>(null);
  const [countdownTimer, setCountdownTimer] = useState<string>('');
  const [repCounter, setRepCounter] = useState(0);
  const [displayedFeedback, setDisplayedFeedback] = useState<{tag: string, message: string, priority: number}>({tag: '', message: '', priority: -1});

  const [camera, setCamera] = useState<'front' | 'back'>('front');
  const [warning, setWarning] = useState<{
    display: boolean;
    message: string;
  }>({ display: false, message: '' });

  const settings: ISettingsState = {
    resolution: '720p',
    framerate: 10, // TODO: try higher fps here?
    videoBitrate: 1400, // TODO: remove and make automatic? see how this impacts speed
    rtmpEndpoint: `rtmp://${ip}:1935/form_analyser`,
    streamKey: '22022001',
  };
  const ref = useRef<LiveStreamMethods | null>(null);
  const isAndroid = Platform.OS === 'android';
  const style = styles(streaming, isAndroid, warning.display, feedbackType);
  const growAnim = useRef(new Animated.Value(0)).current;

  const initialiseStates = () => {
    setDisplayedFeedback({tag: '', message: '', priority: -1});
    setFeedbackType('NONE');
    setRepCounter(0);
    setCountdownTimer('');
    setSetStarted(false);
  }

  useEffect(() => {
    const grow = () => {
      Animated.timing(growAnim, {
        toValue: isAndroid ? 265 : 290,
        duration: 200,
        useNativeDriver: false,
      }).start();
    };
    warning.display && grow();
  }, [warning.display, growAnim, isAndroid]);

  useEffect(() => {
    if (streaming) {  
      const fetchFormFeedback = async () => {
        try {
          const response = await axios.get(FEEDBACK_URL, {
            signal: abortController.signal,
          });
          if (response.data) {
            handleFormFeedback(response.data);
          }
        } catch (error) {
          if (error.name !== 'AbortError') {
            console.error('Error fetching form feedback:', error);
          }
        }
      };
  
      const intervalId = setInterval(fetchFormFeedback, 1000 / settings.framerate);
  
      return () => {
        clearInterval(intervalId);
        abortController.abort();
      };
    }
  }, [streaming]);

  const handleFormFeedback = (data: FormFeedback[]) => {
    // Process the feedback data
    data.forEach((feedback: FormFeedback) => {
      const tag = feedback.tag;
      // TODO: NEED TO CHANGE BACK END TO RETURN A DICT OF {tag: 'SET_START_COUNTDOWN'|'STATE_SEQUENCE'|'NOT_DETECTED'|'FEEDBACK'|'TIP', message: string} | {tag: bloo, summary: FinalFeedback}

      let priority = -1;
      if (tag === 'SET_ENDED' && feedback.summary) {
        handleStreaming();
        initialiseStates();

        navigation.navigate(
          'PostSetSummary',
          feedback.summary
          // {goodReps: 4, badReps: 3, mistakesMade: [{rep: 1, mistakes: ['Poor Depth']}, {rep: 3, mistakes: ['Shoulders Not Level', 'Hips Shifted To The Left']}, {rep: 7, mistakes: ['Hips Not Vertically Aligned With Feet']}], finalComments: "Here are some final comments! Here are some final comments! Here are some final comments! Here are some final comments! Here are some final comments! "}
        )
        priority = 0
      } else {
        const message = feedback.message;
        if (tag === 'SET_START_COUNTDOWN') {
          // TODO: if timer resets, warn the user to stay still
          if (parseFloat(message) < 0.0) {
            setCountdownTimer('0');
            setSetStarted(true);
          } else {
            setCountdownTimer(message);
          }

          return;
        } else if (tag === 'STATE_SEQUENCE') {
          setRepCounter(prevRepCounter => prevRepCounter + 1);

          return;
        } else if (tag === 'NOT_DETECTED') {
          priority = 1
        } else if (tag === 'FEEDBACK') {
          priority = 2
        } else if (tag === 'TIP') {
          priority = 3
        }

        if (priority !== -1 && (displayedFeedback.priority === -1 || priority < displayedFeedback.priority)) {
          if (priority === 1 || priority === 2) {
            setFeedbackType('CRITICAL')
          } else if (priority === 3) {
            setFeedbackType('TIP')
          } else {
            setFeedbackType('NONE');
          }
          
          if (feedbackTimer) {
            clearTimeout(feedbackTimer);
          }
          setDisplayedFeedback({
            tag,
            message,
            priority
          });
          setFeedbackTimer(setTimeout(() => {
            setDisplayedFeedback(prev => ({...prev, message: '', priority: -1}));
            setFeedbackType('NONE');
          }, 3000));
        }
      }
    });
  }

  const handleStreaming = (): void => {
    setWarning({ display: false, message: '' });
    if (settings.rtmpEndpoint.trim().length === 0) {
      setWarning({
        display: true,
        message: 'Please enter a valid RTMP endpoint in settings',
      });
      return;
    }
    if (settings.streamKey.trim().length === 0) {
      setWarning({
        display: true,
        message: 'Please enter a valid stream key in settings',
      });
      return;
    }

    if (streaming) {
      ref.current?.stopStreaming();
      setStreaming(false);
    } else {
      ref.current
        ?.startStreaming(settings.streamKey, settings.rtmpEndpoint)
        .then((_: boolean) => {
          console.log('Stream started!')
          setStreaming(true);
        })
        .catch((e: any) => {
          console.log('Stream failed!')
          console.log(e)
          setStreaming(false);
        });
    }
  };

  const handleCamera = (): void => {
    if (camera === 'back') setCamera('front');
    else setCamera('back');
  };

  return (
    <View style={style.container}>
      <StatusBar animated={true} barStyle="light-content" />

      <LiveStreamView
        style={style.livestreamView}
        ref={ref}
        camera={camera}
        video={{
          bitrate: settings.videoBitrate * 1000,
          fps: settings.framerate,
          resolution: settings.resolution,
        }}
        audio={{ bitrate: 0 }}
        isMuted={true}
        enablePinchedZoom={true}
        onConnectionSuccess={() => {
          console.log('Received onConnectionSuccess');
          initialiseStates();
        }}
        onConnectionFailed={(reason: string) => {
          console.log('Received onConnectionFailed: ' + reason);
          setStreaming(false);
          initialiseStates();
        }}
        onDisconnect={() => {
          console.log('Received onDisconnect');
          setStreaming(false);
          initialiseStates();
        }}
      />

      <View style={button({ bottom: isAndroid ? 20 : 40 }).container}>
        <TouchableOpacity style={style.streamButton} onPress={handleStreaming}>
          {streaming ? (
            <Icon name="stop-circle-outline" size={50} color="#FF0001" />
          ) : (
            <Text style={style.streamText}>Start Analysing Form</Text>
          )}
        </TouchableOpacity>
      </View>

      <View
        style={button({ bottom: isAndroid ? 20 : 40, right: 20 }).container}
      >
        <TouchableOpacity style={style.cameraButton} onPress={handleCamera}>
          <Icon name="camera-reverse-outline" size={30} color="#FFFFFF" />
        </TouchableOpacity>
      </View>

      {!streaming && (
        <Animated.View style={[style.settingsButton, { width: growAnim }]}>
          {warning.display && (
            <View style={style.warningContainer}>
              <Text style={style.warning} numberOfLines={1}>
                {warning.message}
              </Text>
            </View>
          )}
        </Animated.View>
      )}

      {streaming && !setStarted && (
        <View style={style.countdownTimerContainer}>
          <Text style={style.countdownTimerText}>{countdownTimer}</Text>
        </View>
      )}

      {displayedFeedback.message !== '' && (
        <View style={style.formFeedbackContainer}>
          <Text style={style.formFeedbackText}>{displayedFeedback.message}</Text>
        </View>
      )}

      {streaming && (
        <View style={style.repCounterContainer}>
          <Text style={style.repCounterText}>Reps: {repCounter}</Text>
        </View>
      )}
    </View>
  );
}
