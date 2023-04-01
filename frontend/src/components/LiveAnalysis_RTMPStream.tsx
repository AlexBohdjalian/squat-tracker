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
const RTMP_SERVER_URL = `http://${ip}:8080`;
const FEEDBACK_URL = `http://${ip}:5000`;

export default function App() {
  // LOCAL STATE
  // Stream view
  const [streaming, setStreaming] = useState(false);
  const [camera, setCamera] = useState<'front' | 'back'>('back');
  const [warning, setWarning] = useState<{
    display: boolean;
    message: string;
  }>({ display: false, message: '' });
  const [formFeedback, setFormFeedback] = useState<string>('');

  const [settings, setSettings] = useState<ISettingsState>({
    resolution: '720p',
    framerate: 10,
    videoBitrate: 1400,
    rtmpEndpoint: `rtmp://${ip}:1935/form_analyser`,
    streamKey: '22022001',
  });

  // CONSTANTS
  const ref = useRef<LiveStreamMethods | null>(null);
  const isAndroid = Platform.OS === 'android';
  const style = styles(streaming, isAndroid, warning.display);
  const growAnim = useRef(new Animated.Value(0)).current;

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

  // HANDLERS
  // const shrink = () => {
  //   Animated.timing(growAnim, {
  //     toValue: 0,
  //     duration: 200,
  //     useNativeDriver: false,
  //   }).start();
  // };

  const fetchFormFeedback = async () => {
    try {
      const response = await axios.get(`${FEEDBACK_URL}/form-feedback`);
      const data = response.data;
      // TODO: get timestamp of feedback and try sink camera preview to that?
      setFormFeedback(data.join(', '));
    } catch (error) {
      console.error('Error fetching form feedback:', error);
    }
  };

  // Call the fetchFormFeedback function every 3 seconds when the streaming is on
  useEffect(() => {
    if (streaming) {
      const intervalId = setInterval(() => {
        fetchFormFeedback();
      }, 500);
  
      return () => {
        clearInterval(intervalId);
      };
    }
  }, [streaming]);

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
          setStreaming(true);
        })
        .catch((_: any) => {
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
          setFormFeedback('');
        }}
        onConnectionFailed={(reason: string) => {
          console.log('Received onConnectionFailed: ' + reason);
          setStreaming(false);
        }}
        onDisconnect={() => {
          console.log('Received onDisconnect');
          setStreaming(false);
          setFormFeedback('');
        }}
      />

      <View style={button({ bottom: isAndroid ? 20 : 40 }).container}>
        <TouchableOpacity style={style.streamButton} onPress={handleStreaming}>
          {streaming ? (
            <Icon name="stop-circle-outline" size={50} color="#FF0001" />
          ) : (
            <Text style={style.streamText}>Start streaming</Text>
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
