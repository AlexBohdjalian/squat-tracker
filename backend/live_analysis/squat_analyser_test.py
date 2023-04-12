import time

import cv2
import squat_analyser as sa2


NORMAL = '\u001b[0m'
RED = '\u001b[31m'
GREEN = '\u001b[32m'
BLUE = '\u001b[34m'

videos = [
    # (0, ('', 0)),
    ('../assets/goblet_squat_paused_start.mp4', ('GOOD', 3)),
    ('../assets/goblet_squat.mp4', ('BAD', 0)), # No pause at start so set doesn't start
    # ('./assets/barbell_back_squat.mp4', ('GOOD', 11)), # TODO: edit to have pause?
    # ('./assets/barbell_front_squat.mp4', ('GOOD', 11)), # TODO: edit to have pause?
    # 'backend/assets/dan_squat.mp4',# TODO: probably remove
    # 'backend/assets/me_squat.mp4', # TODO: probably remove
    # TODO: need some bad form videos
    # TODO: edit videos to have pause at start so check_set_has_begun passes
]


any_test_failed = False
for vid, (actual_form_quality, actual_rep_count) in videos:
    form_analyser = sa2.SquatFormAnalyser(use_advanced_criteria=True)
    cap = cv2.VideoCapture(vid)

    print(BLUE, f'Assessing: {vid}', NORMAL)
    process_start_time = time.time()

    current_test_failed = False
    frame_index = 0
    prev_feedback = ''
    all_f = []
    state_sequences = []
    while True:
        feedback, success = form_analyser.analyse(cap, show_output=False)
        if not success:
            break

        # TODO: modify from here on so that tag is checked in feedback

        if feedback != prev_feedback:
            prev_feedback = feedback
            if len(feedback) > 0 and feedback[0][0] not in ['USER_INFO', 'TIP']:
                for tag, f in feedback:
                    if tag == 'STATE_SEQUENCE':
                        state_sequences.append(f)
                    else:
                        all_f.append((frame_index, f))
                # print(f)

        frame_index += 1

    end_time = time.time()

    print('State Sequences:')
    for (eccentric_time, concentric_time), state_sequence in state_sequences:
        print(f'Eccentric Time: {round(eccentric_time, 3)}s, Concentric Time: {round(concentric_time, 3)}s, State Sequence: {state_sequence}')

    if actual_rep_count == len(state_sequences):
        print(GREEN, 'Reps:', len(state_sequences), NORMAL)
    else:
        print(RED, 'Reps:', len(state_sequences), 'Actual:', actual_rep_count, NORMAL)
        any_test_failed = current_test_failed = True


    if len(all_f) == 0:
        print(BLUE, 'No Problems Found In Form', NORMAL)
    else:
        print(BLUE, '\nSome problems were found:', NORMAL)

        output = []
        start = all_f[0][0]
        end = all_f[0][0]
        msg = all_f[0][1]

        for feedback in range(1, len(all_f)):
            if all_f[feedback][0] == end + 1 and all_f[feedback][1] == msg:
                end = all_f[feedback][0]
            else:
                output.append((start, end, msg))
                start = all_f[feedback][0]
                end = all_f[feedback][0]
                msg = all_f[feedback][1]
        output.append((start, end, msg))

        for i in output:
            print(i)

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