import React, { useRef } from 'react';
import RTMPPublisher, { RTMPPublisherRefProps } from 'react-native-rtmp-publisher';


export default function CameraStreamingComponent() {
  const publisherRef = useRef<RTMPPublisherRefProps>();

  return (
    <RTMPPublisher
      ref={publisherRef}
      streamURL="rtmp://your-publish-url"
      streamName="stream-name"
      onConnectionFailed={(error) => console.warn(error)}
      onConnectionStarted={() => console.log('Connection Started')}
      onConnectionSuccess={() => console.log('Connection Success')}
      onDisconnect={() => console.log('Disconnected')}
      onNewBitrateReceived={(newBitRate) => console.log('New Bitrate Received: ' + newBitRate)}
    />
  );
}
