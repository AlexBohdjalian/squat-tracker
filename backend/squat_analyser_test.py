import time
import numpy as np
import squat_analyser as sa2
import cv2


NORMAL = '\u001b[0m'
RED = '\u001b[31m'
GREEN = '\u001b[32m'
BLUE = '\u001b[34m'


videos = [
    ('GOOD', 'backend/assets/goblet_squat.mp4'),
    ('GOOD', 'backend/assets/barbell_back_squat.mp4'),
    ('GOOD', 'backend/assets/barbell_front_squat.mp4'),
    # 'backend/assets/dan_squat.mp4',
    # 'backend/assets/me_squat.mp4',
    # TODO: need some bad form videos
]

# TODO: change this to check registers good and bad form
test_failed = False

for actual_form_quality, vid in videos:
    print(BLUE, f'Assessing: {vid}', NORMAL)
    process_start_time = time.time()
    cap = cv2.VideoCapture(vid)
    form_analyser = sa2.SquatFormAnalyser()

    frame_index = 0
    prev_f = ''
    all_f = []
    while True:
        f, suc = form_analyser.analyse(cap, True)
        if not suc:
            break

        if f != prev_f and f != ['Not Detected'] and f != ['Insufficient Joint Data']:
            prev_f = f
            if len(f) > 0:
                for thing in f:
                    all_f.append((frame_index, thing))
                # print(f)

        frame_index += 1

    end_time = time.time()

    if len(all_f) == 0:
        print(GREEN, 'No Problems Found In Form', NORMAL)
        if actual_form_quality == 'GOOD':
            print(GREEN, 'TEST PASSED', NORMAL)
        else:
            print(RED, 'TEST FAILED', NORMAL)
            test_failed = True
    else:
        if actual_form_quality == 'BAD':
            print(GREEN, 'TEST PASSED', NORMAL)
        else:
            print(RED, 'TEST FAILED', NORMAL)
            test_failed = True

        print(RED, '\nSome problems were found:', NORMAL)

        output = []
        start = all_f[0][0]
        end = all_f[0][0]
        msg = all_f[0][1]

        for i in range(1, len(all_f)):
            if all_f[i][0] == end + 1 and all_f[i][1] == msg:
                end = all_f[i][0]
            else:
                output.append((start, end, msg))
                start = all_f[i][0]
                end = all_f[i][0]
                msg = all_f[i][1]

        output.append((start, end, msg))

        [print(i) for i in output]
        
        frames = [f[1] for f in all_f]
        cap = cv2.VideoCapture(vid)
        frame_count = 0
        while cap.isOpened():
            suc, frame = cap.read()
            if not suc:
                break

            frame_indexes = [f[0] for f in all_f]
            if frame_count in frame_indexes:
                frame = cv2.resize(frame, None, fx=0.5, fy=0.5)
                cv2.imshow('Frame', frame)
                cv2.waitKey(100)

            frame_count += 1


    if vid != 0:
        fps = cap.get(cv2.CAP_PROP_FPS)
        video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        print(BLUE, f'Total video length is : {time.strftime("%Mm %Ss", time.gmtime(video_length))}', NORMAL)
    print(BLUE, 'Video Processed in:', time.strftime('%Mm %Ss', time.gmtime(end_time - process_start_time)), NORMAL)
    print()

if test_failed:
    print(RED, 'Some Tests Failed', NORMAL)
else:
    print(GREEN, 'All Tests Passed', NORMAL)