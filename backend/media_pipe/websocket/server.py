import asyncio
import websockets
from mediapipe_estimator import MediaPipeDetector
import json
import numpy as np


pose_estimator = MediaPipeDetector()

# create handler for each connection
async def handler(websocket, path):
    data = await websocket.recv()
    parsed_data = json.loads(data)
    
    print('Image received')
    print(parsed_data)

    await websocket.send(json.dumps(parsed_data))

start_server = websockets.serve(handler, "localhost", 8000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
