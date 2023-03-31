import numpy as np
import squat_analyser as sa2
import cv2

form_analyser = sa2.SquatFormAnalyser()

videos = [
    # 'backend/assets/goblet_squat.mp4',
    # 'backend/assets/barbell_back_squat.mp4',
    # 'backend/assets/barbell_front_squat.mp4',
    'backend/assets/dan_squat.mp4',
    'backend/assets/me_squat.mp4',
]

for vid in videos:
    cap = cv2.VideoCapture(vid)

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

    print(all_f)
    if len(all_f) == 0:
        print('No Problems Found In Form')
    else:
        print('Some problems were found:', np.unique(all_f))


[
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 117 and should be less than 100'
    ],
    ['Bend Backwards'],
    ['Bend Backwards'],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 138 and should be less than 100'
    ],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 173 and should be less than 100'
    ],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 171 and should be less than 100'
    ],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 177 and should be less than 100'
    ],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 164 and should be less than 100'
    ],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 169 and should be less than 100'
    ],
    [
        'Bend Backwards'],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 112 and should be less than 100'
    ],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 100 and should be less than 100'
    ],
    ['Bend Backwards'],
    ['Bend Backwards',
    'Incorrect Posture. Knee angle is: 127 and should be less than 100'
    ],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 119 and should be less than 100'
    ],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 138 and should be less than 100'
    ],
    ['Bend Backwards'],
    ['Bend Backwards'],
    ['Bend Backwards'],
    ['Bend Backwards'],
    ['Bend Backwards'],
    ['Bend Backwards'],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 120 and should be less than 100'
    ],
    [
        'Bend Backwards',
        'Incorrect Posture. Knee angle is: 117 and should be less than 100'
    ]
]