import asyncio
import websockets
from backend_archived.squat_check import SquatFormAnalyzer
from backend.mediapipe_estimator import MediaPipeDetector
import json



# create handler for each connection
async def handler(websocket, path):
    data = await websocket.recv()
    parsed_data = json.loads(data)
    
    # Process data here
    landmarks = pose_estimator.make_prediction(parsed_data)
    squat_data = form_analyser(landmarks)

    await websocket.send(json.dumps(squat_data))


pose_estimator = MediaPipeDetector()
form_analyser = SquatFormAnalyzer(0.01, 0.5)

start_server = websockets.serve(handler, "localhost", 8000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
