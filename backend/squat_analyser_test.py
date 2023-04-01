import time
import squat_analyser as sa2
import cv2


NORMAL = '\u001b[0m'
RED = '\u001b[31m'
GREEN = '\u001b[32m'
BLUE = '\u001b[34m'

videos = [
    ('backend/assets/goblet_squat.mp4', ('GOOD', 3)),
    ('backend/assets/barbell_back_squat.mp4', ('GOOD', 11)),
    ('backend/assets/barbell_front_squat.mp4', ('GOOD', 11)),
    # 'backend/assets/dan_squat.mp4',
    # 'backend/assets/me_squat.mp4',
    # TODO: need some bad form videos
]


any_test_failed = False
for vid, (actual_form_quality, actual_rep_count) in videos:
    form_analyser = sa2.SquatFormAnalyser()
    cap = cv2.VideoCapture(vid)

    print(BLUE, f'Assessing: {vid}', NORMAL)
    process_start_time = time.time()

    current_test_failed = False
    frame_index = 0
    prev_feedback = ''
    all_f = []
    state_sequences = []
    while True:
        feedback, suc = form_analyser.analyse(cap, False)
        if not suc:
            break

        # TODO: modify from here on so that tag is checked in f

        if feedback != prev_feedback and feedback != [('FEEDBACK', 'Not Detected')] and feedback != [('FEEDBACK', 'Insufficient Joint Data')]:
            prev_feedback = feedback
            if len(feedback) > 0:
                for tag, f in feedback:
                    if tag == 'STATE_SEQUENCE':
                        state_sequences.append(f)
                    else:
                        all_f.append((frame_index, f))
                # print(f)

        frame_index += 1

    end_time = time.time()

    print('State Sequences:')
    [print(ss) for ss in state_sequences]

    if actual_rep_count == len(state_sequences):
        print(GREEN, 'Reps:', len(state_sequences), NORMAL)
    else:
        print(RED, 'Reps:', len(state_sequences), 'Actual:', actual_rep_count, NORMAL)
        any_test_failed = current_test_failed = True


    if len(all_f) == 0:
        if actual_form_quality == 'GOOD':
            print(GREEN, 'No Problems Found In Form', NORMAL)
        else:
            print(RED, 'No Problems Found In Form', NORMAL)
            any_test_failed = current_test_failed = True
    else:
        if actual_form_quality == 'BAD':
            print(GREEN, '\nSome problems were found:', NORMAL)
        else:
            print(RED, '\nSome problems were found:', NORMAL)
            any_test_failed = current_test_failed = True


        output = []
        start = all_f[0][0]
        end = all_f[0][0]
        msg = all_f[0][1]

        print(all_f)
        for feedback in range(1, len(all_f)):
            if all_f[feedback][0] == end + 1 and all_f[feedback][1] == msg:
                end = all_f[feedback][0]
            else:
                output.append((start, end, msg))
                start = all_f[feedback][0]
                end = all_f[feedback][0]
                msg = all_f[feedback][1]

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
        cv2.destroyAllWindows()

    if vid != 0:
        fps = cap.get(cv2.CAP_PROP_FPS)
        video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        print(BLUE, f'Total video length is : {time.strftime("%Mm %Ss", time.gmtime(video_length))}', NORMAL)
    print(BLUE, 'Video Processed in:', time.strftime('%Mm %Ss', time.gmtime(end_time - process_start_time)), NORMAL)
    
    if current_test_failed:
        print(RED, 'TEST FAILED', NORMAL)
    else:
        print(GREEN, 'TEST PASSED', NORMAL)
    print()

if any_test_failed:
    print(RED, 'Some Tests Failed', NORMAL)
else:
    print(GREEN, 'All Tests Passed', NORMAL)