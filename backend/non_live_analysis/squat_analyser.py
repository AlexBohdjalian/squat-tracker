import cv2
import numpy as np
import time
import mediapipe as mp
from imutils.video import FileVideoStream
from mediapipe_estimator import MediaPipeDetector
from squat_form_analyser import SquatFormAnalyzer


pose_detector = MediaPipeDetector()
form_analyser = SquatFormAnalyzer()
frame_stack = 2
frame_skip = 3
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose
text_colour = (219, 123, 3)

def get_aspect_dim(image_dim, width, height):
    """ Gets the dimension to resize a frame to while maintaining aspect ratio """
    (h, w) = image_dim

    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return dim

def save_final_video(path, frames, fps):
    f_shape = frames[0].shape
    out = cv2.VideoWriter(
        path,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (f_shape[1], f_shape[0])
    )
    for frame in frames:
        out.write(frame)
    out.release()

def draw_text(img, text,
          to_centre=False,
          font=cv2.FONT_HERSHEY_PLAIN,
          pos=(0, 0),
          font_scale=3,
          font_thickness=2,
          text_color=(219, 123, 3),
          text_color_bg=(0, 0, 0)
          ):
    """ Draws text on a cv2 image in a given spot with a background """
    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    if to_centre:
        x -= text_w // 2
        y -= text_h // 2
    cv2.rectangle(img, (x, y), (x + text_w, y + text_h), text_color_bg, -1)
    cv2.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness)

    return text_size

def display_angle_at_joint(frame, joint, angle):
    if joint[3] > 0.5:
        draw_text(
            frame,
            str(angle) + ' deg',
            pos=tuple(np.multiply(joint[0:2], frame.shape[:2][::-1]).astype(int)),
            to_centre=True
        )

def extract_reps_from_path(path, indexes):
    start = 0
    end = 0
    reps = []
    for (t, i) in indexes:
        if t == 'start':
            start = i
        elif t == 'end':
            end = i
            reps.append(path[start:end+1])
    return reps

def process_live_video_from_fe(cap, show_output=False):
    suc, frame = cap.read()
    if not suc:
        return 'Video End', suc

    feedback, pose_landmarks = process_frame_from_fe(frame)

    if feedback is None:
        return 'No Landmarks Detected', suc

    if show_output:
        mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )
        frame = cv2.resize(frame, (360, 640))
        cv2.imshow('Live Stream', frame)
        cv2.waitKey(1)

    return feedback, suc

def process_frame_from_fe(frame):
    s = time.time()
    pose_landmarks = pose_detector.make_prediction(frame)
    if pose_landmarks is None:
        return None, []

    return 'Landmarks detected in: ' + str(time.time() - s), pose_landmarks

def process_video_from_fe(video_source):
    # Guard against invalid video source
    if not isinstance(video_source, str) or video_source == 0:
        raise ValueError('Invalid video source')

    # Get video capture and constants
    cap = FileVideoStream(video_source).start()
    cap.stream.set(cv2.CAP_PROP_CONVERT_RGB, 1)
    fps = cap.stream.get(cv2.CAP_PROP_FPS)
    video_length = int(cap.stream.get(cv2.CAP_PROP_FRAME_COUNT)) / fps
    
    # Squat analysis constants
    global good_form_colour, bad_form_colour
    good_form_colour = text_colour
    bad_form_colour = (0, 0, 255)
    most_visible_side = ''
    form_thresholds_beginner = {
        'ankle': 45, # max angle  # currently unused
        'knee': (50, 70, 95), # 
        'hip': (10, 50), # min/max angle
    }
    form_thresholds_advanced = {
        'ankle': 30, # max angle  # currently unused
        'knee': (50, 80, 95), # 
        'hip': (15, 50), # min/max angle
    }
    form_thresholds = form_thresholds_advanced

    # Squat analysis variables
    frames = []
    reps = []
    state_sequence = ['Standing']
    current_form_text = ''
    current_form_text_colour = good_form_colour
    squat_start_time = 0
    squat_mid_time = 0
    squat_end_time = 0
    squat_duration = 0

    # Debugging
    debugging = False
    if debugging:
        window_width = None
        window_height = 600
        frame_width  = cap.stream.get(cv2.CAP_PROP_FRAME_WIDTH)
        frame_height = cap.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
        aspect_dim = get_aspect_dim((frame_height, frame_width), window_width, window_height)
        cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Video', aspect_dim[0], aspect_dim[1])

    # Begin loop
    print('Processing video...')
    print(f'Total video length is : {time.strftime("%Mm %Ss", time.gmtime(video_length))}')
    process_start_time = time.time()
    while True:
        # Get the frame
        frame = cap.read()
        if frame is None:
            break

        # Determine landmarks and get angle
        pose_landmarks = pose_detector.make_prediction(frame)
        if pose_landmarks is None:
            continue
        
        if most_visible_side == '':
            most_visible_side = form_analyser.get_most_visible_side(pose_landmarks)

            # Video has not shown enough yet
            if most_visible_side == '':
                continue

        # Determine quality of rep ######################
        ankle_vertical_angle, knee_vertical_angle, hip_vertical_angle = form_analyser.get_main_joint_vertical_angles(pose_landmarks, most_visible_side)
        if knee_vertical_angle is not None:
            if state_sequence != ['Standing'] and knee_vertical_angle <= 32:
                if state_sequence[-1] == 'Transition':
                    squat_end_time = time.time()
                elif state_sequence[-1] == 'Bottom':
                    print('Transition not detected. Was standing now bottom.')

                # TODO: split this into concentric and eccentric times
                squat_duration = squat_end_time - squat_start_time
                reps.append([
                    [
                        squat_mid_time - squat_start_time,
                        squat_end_time - squat_mid_time
                    ],
                    state_sequence
                ])

                state_sequence = ['Standing']
            elif state_sequence[-1] != 'Transition' and 35 <= knee_vertical_angle <= 65:
                if state_sequence[-1] == 'Standing':
                    squat_start_time = time.time()
                elif state_sequence[-1] == 'Bottom':
                    squat_mid_time = time.time()
                if state_sequence[-1] != 'Transition':
                    state_sequence.append('Transition')
            elif state_sequence[-1] != 'Bottom' and 75 <= knee_vertical_angle <= 95:
                if state_sequence[-1] == 'Standing':
                    print('Transition not detected. Was bottom now standing.')
                if state_sequence[-1] != 'Bottom':
                    state_sequence.append('Bottom')

        # Determine feedback #############################
        current_form_text = []
        if hip_vertical_angle is not None:
            if hip_vertical_angle > form_thresholds['hip'][1]:
                current_form_text.append('Bend Backwards')
                pass
            elif hip_vertical_angle < form_thresholds['hip'][0]:
                current_form_text.append('Bend Forward')
                pass

        if knee_vertical_angle is not None:
            if form_thresholds['knee'][0] < knee_vertical_angle < form_thresholds['knee'][1] and \
                state_sequence.count('s2') == 1:
                current_form_text.append('Lower Hips')
                pass
            elif knee_vertical_angle > form_thresholds['knee'][2]:
                # 'Deep Squat'
                current_form_text.append('Incorrect Posture')
                pass

        # Visualise rep details ##########################
        mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )      
        if squat_end_time < squat_start_time:
            squat_duration = round(time.time() - squat_start_time, 2)
        ankle, knee, hip, _ = form_analyser.get_main_joints(pose_landmarks, most_visible_side)
        if ankle_vertical_angle is not None:
            display_angle_at_joint(frame, ankle, round(ankle_vertical_angle))
        if knee_vertical_angle is not None:
            display_angle_at_joint(frame, knee, round(knee_vertical_angle))
        if hip_vertical_angle is not None:
            display_angle_at_joint(frame, hip, round(hip_vertical_angle))
        cv2.rectangle(frame, (0, 0), (frame.shape[0], 30+40*(3+len(current_form_text))), (0, 0, 0), -1)
        cv2.putText(frame, str(state_sequence[-1]), (5, 50), cv2.FONT_HERSHEY_PLAIN, 4, text_colour, 2)
        cv2.putText(frame, 'Repetitions: ' + str(len(reps)), (5, 90), cv2.FONT_HERSHEY_PLAIN, 2, text_colour, 2)
        cv2.putText(frame, 'Duration: ' + str(round(squat_duration, 3)) + 's', (5, 130), cv2.FONT_HERSHEY_PLAIN, 2, text_colour, 2)
        for i in range(len(current_form_text)):
            cv2.putText(frame, current_form_text[i], (5, 170 + i * 30), cv2.FONT_HERSHEY_PLAIN, 2, current_form_text_colour, 2)

        if debugging:
            cv2.imshow('Video', frame)
            cv2.waitKey(1)

        frames.append(frame)
    
    print(f'Processed in : {time.strftime("%Mm %Ss", time.gmtime(time.time() - process_start_time))}')
    print('Creating response video...')
    cap.stream.release()
    if video_source != 0:
        cap.stop()
    cv2.destroyAllWindows()

    processed_video_path = f'{video_source[:-4]}_processed.mp4'
    save_final_video(processed_video_path, frames, fps)

    print('Post analysis...')
    # Post set analysis plan:
    # list of all reps and details e.g. quality, duration, etc.
    # estimated rpe
    # final comments on form
    # etc.

    post_analysis = {'reps': reps}

    # do post analysis

    # NOTES:
    # TODO: see https://github.com/Pradnya1208/Squats-angle-detection-using-OpenCV-and-mediapipe_v1/blob/main/Squat%20pose%20estimation.ipynb
        # for other calculations (also below)
    # TODO: below
    # Range of motion
    # Partial squat (0-40 degrees knee angle)
    # Parallel squat (hips parallel to knees or 70-100 degrees knee angle)
    # Deep squat (full range or >100 degrees knee angle)

    # ref: https://www.raynersmale.com/blog/2014/1/31/optimising-your-squat
    # TODO: Toque calculation: https://squatuniversity.com/2016/04/20/the-real-science-of-the-squat/
    # TODO: angles: Trunk angle, Shank angle Thigh segment angle Ankle segment angle ref: https://www.quinticsports.com/squatting_technique/

    # use data in squat_path, (save squat durations?), ...
    # produce graphs / summary e.g...
    # 5 good reps performed with tempos of ... indicating RPE of ...
    # 2 reps had poor depth at the bottom. try doing ... next time
    # 1 rep had a poor lockout while standing...
    # 1 rep did not register you descending, ensure the camera is in a good spot...
    # No asymmetries detected in joint paths
    # blah?

    print(f'Done. Final time: {time.strftime("%Mm %Ss", time.gmtime(time.time() - process_start_time))}')
    return processed_video_path, post_analysis
