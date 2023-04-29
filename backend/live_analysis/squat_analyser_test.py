import time

import cv2
import squat_analyser as sa2


NORMAL = '\u001b[0m'
RED = '\u001b[31m'
GREEN = '\u001b[32m'
BLUE = '\u001b[34m'
RED_BG = '\u001b[41m'

videos = [
    { 'path': '../assets/goblet_squat_paused_start.mp4', 'any_problems': False, 'reps': 3 },
    { 'path': '../assets/barbell_back_squat_paused_start.mp4', 'any_problems': False, 'reps': 11 },
    # { 'path': '../assets/barbell_front_squat_paused_start.mp4', 'any_problems': False, 'reps': 11 },
        # NOTE: this video changes perspectives (Not possible in context of software), split video up
    { 'path': '../assets/goblet_squat.mp4', 'any_problems': False, 'reps': 0 },
    { 'path': '../assets/barbell_back_squat.mp4', 'any_problems': False, 'reps': 0 },
    { 'path': '../assets/barbell_front_squat.mp4', 'any_problems': False, 'reps': 0 },
    { 'path': '../assets/me_bad_form_squat.mp4', 'any_problems': True, 'reps': 2 },
    # TODO: need to test set ends
]


any_test_failed = False
for vid in videos:
    form_analyser = sa2.SquatFormAnalyser(use_advanced_criteria=True)
    cap = cv2.VideoCapture(vid['path'])
    if not cap.isOpened():
        cap.release()
        print(f'{RED_BG} Failed to open video: {vid["path"]} {NORMAL}')
        exit()

    print(BLUE, f'Assessing: {vid["path"]}', NORMAL)

    current_test_failed = False
    frame_index = 0
    prev_feedback = ''
    all_f = []
    state_sequences = []

    process_start_time = time.time()
    while True:
        # NOTE: the script works with time to determine some things. without a bit of a natural delay, it messes up. Solution is to replace time with frame count
        feedback, success = form_analyser.analyse(cap, show_output=True)
        if not success:
            break

        # NOTE: this script is sorta broken after STATE_SEQUENCE TAG WAS REMOVED
        if feedback != prev_feedback:
            prev_feedback = feedback
            if len(feedback) > 0 and feedback[0]['tag'] not in ['SET_START_COUNTDOWN', 'NOT_DETECTED', 'TIP']:
                for f in feedback:
                    tag = f['tag']
                    if tag == 'STATE_SEQUENCE':
                        # TODO: check that each state sequence is valid?
                            # times are positive
                            # sequence is valid i.e. ['STANDING', 'TRANSITION', 'BOTTOM', 'TRANSITION']
                        state_sequences.append(f['message'])
                    elif tag == 'SET_ENDED':
                        all_f.append((frame_index, f['summary']))
                    else:
                        all_f.append((frame_index, f['message']))

        frame_index += 1

    end_time = time.time()

    if vid['reps'] == len(state_sequences):
        print(GREEN, 'Reps:', len(state_sequences), NORMAL)
    else:
        print(RED, 'Reps:', len(state_sequences), 'Actual:', vid['reps'], NORMAL)

        print(RED, 'State Sequences:', NORMAL)
        for (e_time, c_time), s_seq in state_sequences:
            print(f' Eccentric Time: {round(e_time, 3)}s, Concentric Time: {round(c_time, 3)}s, State Sequence: {s_seq}')

        current_test_failed = True

    if len(all_f) == 0:
        if vid['any_problems']:
            print(RED, 'No Problems Found In Form', NORMAL)
            current_test_failed = True
        else:
            print(GREEN, 'No Problems Found In Form', NORMAL)

    else:
        if vid['any_problems']:
            print(GREEN, 'Some problems were found:', NORMAL)
        else:
            print(RED, 'Some problems were found:', NORMAL)
            current_test_failed = True

        any_test_failed = any_test_failed or current_test_failed

        start = all_f[0][0]
        end = all_f[0][0]
        msg = all_f[0][1]
        for feedback in range(1, len(all_f)):
            if all_f[feedback][0] == end + 1 and all_f[feedback][1] == msg:
                end = all_f[feedback][0]
            else:
                print(f'({start}, {end}): {msg}')
                start = all_f[feedback][0]
                end = all_f[feedback][0]
                msg = all_f[feedback][1]
        print(f'({start}, {end}): {msg}')

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

    cv2.destroyAllWindows()
    cap.release()


if any_test_failed:
    print(RED, 'Some Tests Failed', NORMAL)
else:
    print(GREEN, 'All Tests Passed', NORMAL)