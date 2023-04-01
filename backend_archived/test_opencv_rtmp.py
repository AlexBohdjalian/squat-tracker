import cv2
import ffmpeg
import subprocess
import time

video_path = 'backend/assets/goblet_squat.mp4'
rtmp_url = 'rtmp://localhost/live/stream'

def stream_video(video_path, rtmp_url):
    # Get video information using ffprobe
    # probe = ffmpeg.probe(video_path)
    # video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
    # width = int(video_info['width'])
    # height = int(video_info['height'])
    # fps = int(eval(video_info['avg_frame_rate']))

    # Define the command for FFmpeg to stream the video
    command = [
        'ffmpeg',
        '-re',  # Read input at native frame rate
        '-i', video_path,
        '-vcodec', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-preset', 'ultrafast',
        '-acodec', 'aac',
        '-strict', '-2',
        '-f', 'flv',
        rtmp_url
    ]

    # Start the FFmpeg process to stream the video
    ffmpeg_process = subprocess.Popen(command, stderr=subprocess.PIPE)

    return ffmpeg_process

def play_rtmp_stream(rtmp_url):
    # Open the RTMP stream using OpenCV
    cap = cv2.VideoCapture(rtmp_url, cv2.CAP_FFMPEG)

    # Check if the stream was opened successfully
    if not cap.isOpened():
        print("Error: Could not open the RTMP stream.")
        return

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Break the loop if we reached the end of the stream
        if not ret:
            break

        # Display the resulting frame
        cv2.imshow('RTMP Stream', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture and close the display window
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # Stream the video to the RTMP server
    ffmpeg_process = stream_video(video_path, rtmp_url)

    # Allow some time for the stream to start before trying to play it
    time.sleep(5)

    # Play the RTMP stream using OpenCV
    play_rtmp_stream(rtmp_url)

    # Terminate the FFmpeg process when done playing the stream
    ffmpeg_process.terminate()
