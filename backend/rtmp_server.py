from flask import Flask, Response
import subprocess

app = Flask(__name__)

@app.route('/stream')
def stream():
    cmd = 'ffmpeg -i rtmp://localhost:1935/live/stream -c copy -f flv rtmp://your-rtmp-server-url/stream'
    p = subprocess.Popen(cmd, shell=True)
    return Response(gen(), mimetype='video/x-flv')

def gen():
    cmd = 'ffmpeg -f avfoundation -framerate 30 -video_size 1280x720 -i "0" -c:v libx264 -f flv rtmp://localhost:1935/live/stream'
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    while True:
        data = p.stdout.read(1024)
        if len(data) == 0:
            break
        yield data

if __name__ == '__main__':
    app.run(host='192.168.0.28', port=5000)
