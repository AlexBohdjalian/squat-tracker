import time
import numpy as np
import squat_analyser as sa2
import cv2

form_analyser = sa2.SquatFormAnalyser()

videos = [
    'backend/assets/goblet_squat.mp4',
    'backend/assets/barbell_back_squat.mp4',
    'backend/assets/barbell_front_squat.mp4',
    'backend/assets/dan_squat.mp4',
    'backend/assets/me_squat.mp4',
]

for vid in videos:
    print('Assessing: ' + vid)
    process_start_time = time.time()
    cap = cv2.VideoCapture(vid)

    feedback_received = 0
    prev_f = ''
    all_f = []
    while True:
        f, suc = form_analyser.analyse(cap, False)
        if not suc:
            break

        if f != prev_f:
            prev_f = f
            if len(f) > 0 and f != ['Not Detected'] and f != ['Insufficient Joint Data']:
                print(f)
                all_f.append(f)
            feedback_received = time.time()
        elif time.time() - feedback_received > 5000:
            
            feedback_received = time.time()

    end_time = time.time()

    if len(all_f) == 0:
        print('No Problems Found In Form')
    else:
        flat = []
        for f in all_f:
            for i in f:
                flat.append(i)
        print('\nSome problems were found:')
        print(np.unique(flat))

    if vid != 0:
        fps = cap.get(cv2.CAP_PROP_FPS)
        video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        print(f'Total video length is : {time.strftime("%Mm %Ss", time.gmtime(video_length))}')
    print('Video Processed in:', time.strftime('%Mm %Ss', time.gmtime(end_time - process_start_time)))
    print()
