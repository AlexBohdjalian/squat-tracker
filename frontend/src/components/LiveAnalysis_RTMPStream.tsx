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
import styles, { button } from '../styles/LiveAnalysis_RTMPStreamStyle';


export interface ISettingsState {
  resolution: Resolution;
  framerate: number;
  videoBitrate: number;
  rtmpEndpoint: string;
  streamKey: string;
}

const ip = '192.168.0.28';
const FEEDBACK_URL = `http://${ip}:5000/form-feedback`;

export default function App() {
  // LOCAL STATE
  // Stream view
  const [streaming, setStreaming] = useState(false);
  const [feedbackType, setFeedbackType] = useState<'NONE'|'GOOD'|'TIP'|'CRITICAL'>('NONE');
  const [camera, setCamera] = useState<'front' | 'back'>('front');
  const [warning, setWarning] = useState<{
    display: boolean;
    message: string;
  }>({ display: false, message: '' });
  const [formFeedback, setFormFeedback] = useState<string>('');

  // CONSTANTS
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
    setFormFeedback('');
    setFeedbackType('NONE');
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
      const intervalId = setInterval(() => {
        fetchFormFeedback();
      }, 1000 / settings.framerate);

      return () => {
        clearInterval(intervalId);
      };
    }
  }, [streaming]);

  const fetchFormFeedback = async () => {
    try {
      const response = await axios.get(FEEDBACK_URL);
      if (response.data) {
        handleFormFeedback(response.data);
      }
    } catch (error) {
      if (error.message !== "Network Error") {
      console.error('Error fetching form feedback:', error);
      }
    }
  };

  const handleFormFeedback = (data: any) => {
    setFormFeedback(data.join(', '));

    // TODO: for each feedback in data, figure out what to do, add to queue?
      // Either take highest priority point or,
      // add to queue and display in priority order

    const tags = data.map(feedback => feedback[0]);
    if (tags.includes('FEEDBACK') || (tags.includes('USER_INFO') && data.map(feedback => feedback[0]).includes('Not Detected'))) {
      setFeedbackType('CRITICAL');
    } else if (tags.includes('TIP')) {
      setFeedbackType('TIP');
    } else if (tags.includes('STATE_SEQUENCE')) {
      setFeedbackType('GOOD');
    } else {
      setFeedbackType('NONE');
    }
  }

  const handleStreaming = (): void => {
    // Reset warning
    setWarning({ display: false, message: '' });
    // No RTMP
    if (settings.rtmpEndpoint.trim().length === 0) {
      setWarning({
        display: true,
        message: 'Please enter a valid RTMP endpoint in settings',
      });
      return;
    }
    // No stream key
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

  // RETURN
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

      {formFeedback !== '' && (
        <View style={style.formFeedbackContainer}>
          <Text style={style.formFeedbackText}>{formFeedback}</Text>
        </View>
      )}
    </View>
  );
}
