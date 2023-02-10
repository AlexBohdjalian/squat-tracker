import cv2
import numpy as np
import time
from enum import Enum
import mediapipe as mp
from imutils.video import FileVideoStream
from mediapipe_estimator import MediaPipeDetector
from squat_check import SquatFormAnalyzer


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

def display_angle_at_joint(frame, joint, angle):
    if joint.visibility > 0.5:
        joint_pos = [joint.x, joint.y]
        draw_text(
            frame,
            str(angle) + ' deg',
            pos=tuple(np.multiply(joint_pos, frame.shape[:2][::-1]).astype(int)),
            to_centre=True
        )

def process_data(video_source, frame_stack, frame_skip, show_output, post_analysis, save_video):
    if video_source != 0:
        print(f'Beginning "{video_source}" ...')
        cap = FileVideoStream(video_source).start()
        cap_stream = cap.stream
    else:
        print(f'Beginning LIVE CAMERA FEED ...')
        cap = cv2.VideoCapture(video_source)
        cap_stream = cap

    # Get video capture and constants
    start_time = time.time()
    fps = cap_stream.get(cv2.CAP_PROP_FPS)
    video_length = int(cap_stream.get(cv2.CAP_PROP_FRAME_COUNT)) / fps
    frame_width  = cap_stream.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = cap_stream.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    # Squat form constants
    good_form_colour = text_colour
    bad_form_colour = (0, 0, 255)
    
    # Window dimensions
    window_width = None
    window_height = 500
    aspect_dim = get_aspect_dim((frame_height, frame_width), window_width, window_height)

    # Output video information
    print(f'Total video length is : {time.strftime("%Mm %Ss", time.gmtime(video_length))}')

    # Initiate variables
    frames = []
    results_stack = []
    rep_count = 0
    squat_start_time = 0
    squat_end_time = 0
    prev_frame_time = 0
    squat_details = ['Unsure', '', '', '', ''] # move this into squat_check and get via call. also use in determine_squat_stage()
    squat_path = []
    rep_indexes = []
    form_analysis = 'No rep Performed'
    form_colour = good_form_colour

    # Begin loop
    while True:
        # Get the frame
        if video_source != 0:
            frame = cap.read()
            if frame is None: # is this robust?
                break
        else:
            success, frame = cap.read()
            if not success:
                break

        # Process then send the data
        pose_landmarks = pose_detector.make_prediction(frame)

        if len(results_stack) > 0 and len(results_stack) % frame_stack == 0:
            new_squat_details = form_analyser.analyse_landmark_stack(results_stack)
            results_stack = []

            if new_squat_details[0] != 'Unsure':
                squat_details = new_squat_details

                if len(squat_path) == 0:
                    squat_path.append(squat_details[0])
                elif squat_path[-1] != squat_details[0]:
                    squat_path.append(squat_details[0])

                    if len(squat_path) >= 2:
                        if squat_path[-2] == 'Standing' and squat_path[-1] == 'Descending':
                            form_colour = good_form_colour
                            form_analysis = 'In Progress'
                            squat_start_time = time.time()
                            rep_indexes.append(('start', len(squat_path) - 1))

                        elif squat_path[-2] == 'Standing' and squat_path[-1] == 'Bottom':
                            form_colour = good_form_colour
                            form_analysis = 'Good Depth' # Ascent not detected
                            squat_start_time = time.time()
                            rep_indexes.append(('start', len(squat_path) - 1))

                        elif squat_path[-2] == 'Standing' and squat_path[-1] == 'Ascending':
                            form_analysis = form_analysis
                            squat_path.pop(-1) # this stage sequence can only happen in error

                        elif squat_path[-2] == 'Descending' and squat_path[-1] == 'Bottom':
                            form_colour = good_form_colour
                            form_analysis = 'Good Depth'

                        elif squat_path[-2] == 'Descending' and squat_path[-1] == 'Ascending':
                            form_colour = bad_form_colour
                            form_analysis = 'Bad Depth' # Bad Depth

                        elif squat_path[-2] == 'Descending' and squat_path[-1] == 'Standing':
                            form_analysis = form_analysis
                            squat_path.pop(-1) # this stage sequence can only happen in error

                        elif squat_path[-2] == 'Bottom' and squat_path[-1] == 'Ascending':
                            form_analysis = form_analysis # Maintain prev message

                        elif squat_path[-2] == 'Bottom' and squat_path[-1] == 'Standing':
                            form_colour = good_form_colour
                            form_analysis = 'Good Lockout' # Ascent not detected
                            squat_end_time = time.time()
                            rep_indexes.append(('end', len(squat_path) - 1))

                        elif squat_path[-2] == 'Bottom' and squat_path[-1] == 'Descending':
                            form_analysis = form_analysis
                            squat_path.pop(-1) # this stage sequence can only happen in error

                        elif squat_path[-2] == 'Ascending' and squat_path[-1] == 'Standing':
                            form_colour = good_form_colour
                            form_analysis = 'Good Lockout'
                            squat_end_time = time.time()
                            rep_indexes.append(('end', len(squat_path) - 1))

                        elif squat_path[-2] == 'Ascending' and squat_path[-1] == 'Descending':
                            form_colour = bad_form_colour
                            form_analysis = 'Bad Lockout' # Bad Lockout
                            squat_start_time = time.time()
                            squat_end_time = time.time()
                            rep_indexes.append(('start', len(squat_path) - 1))
                            rep_indexes.append(('end', len(squat_path) - 2))

                        elif squat_path[-2] == 'Ascending' and squat_path[-1] == 'Bottom':
                            form_analysis = form_analysis
                            squat_path.pop(-1) # this stage sequence can only happen in error

                        else:
                            form_colour = bad_form_colour
                            form_analysis = 'Unknown State'

                        # ONLY COUNT CLEAN REPS?
                        if len(squat_path) >= 4 and squat_path[-4:] == ['Descending', 'Bottom', 'Ascending', 'Standing']:
                            rep_count += 1

        if pose_landmarks is None:
            results_stack = []
        elif len(frames) % (frame_skip + 1) == 0:
            results_stack.append(pose_landmarks)

        # Draw the pose annotation
        mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
        )
        
        # Draw angles next to joints
        if pose_landmarks is not None and squat_details[4] != '':
            most_visible_hip_index = form_analyser.landmark_names[squat_details[4] + 'hip']
            hip = pose_landmarks.landmark[most_visible_hip_index]

            most_visible_knee_index = form_analyser.landmark_names[squat_details[4] + 'knee']
            knee = pose_landmarks.landmark[most_visible_knee_index]

            most_visible_ankle_index = form_analyser.landmark_names[squat_details[4] + 'ankle']
            ankle = pose_landmarks.landmark[most_visible_ankle_index]

            display_angle_at_joint(frame, ankle, squat_details[1])
            display_angle_at_joint(frame, knee, squat_details[2])
            display_angle_at_joint(frame, hip, squat_details[3])

        if squat_end_time >= squat_start_time:
            squat_duration = round(squat_end_time - squat_start_time, 2)
        else:
            squat_duration = round(time.time() - squat_start_time, 2)

        # Draw text with background
        box_len = 4
        if show_output:
            box_len = 5
        cv2.rectangle(frame, (0, 0), (frame.shape[0], 30+40*box_len), (0, 0, 0), -1)
        cv2.putText(frame, squat_details[0], (5, 50), cv2.FONT_HERSHEY_PLAIN, 4, text_colour, 2)
        cv2.putText(frame, 'Repetitions: ' + str(rep_count), (5, 90), cv2.FONT_HERSHEY_PLAIN, 2, text_colour, 2)
        cv2.putText(frame, 'Form: ' + form_analysis, (5, 130), cv2.FONT_HERSHEY_PLAIN, 2, form_colour, 2)

        # Make this display live time, then pause while standing
        cv2.putText(frame, 'Duration: ' + str(squat_duration) + 's', (5, 170), cv2.FONT_HERSHEY_PLAIN, 2, text_colour, 2)

        # If the output is being shown in real-time, enforce desired fps and calculate actual fps
        if show_output:
            elapsed_time = time.time() - prev_frame_time
            prev_frame_time = time.time()
            wait_time = int(1000.0 * (1.0 / fps - elapsed_time))

            if wait_time <= 0:
                wait_time = 1

            actual_fps = int(1 / (elapsed_time + wait_time / 1000))
            if cv2.waitKey(wait_time) & 0xFF == ord('q'):
                break

            cv2.putText(frame, 'FPS: ' + str(actual_fps), (5, 210), cv2.FONT_HERSHEY_PLAIN, 2, text_colour, 2)
            cv2.imshow('MediaPipe Pose', cv2.resize(frame, aspect_dim, cv2.INTER_AREA))

        frames.append(frame)

    cap_stream.release()
    if video_source != 0:
        cap.stop()
    cv2.destroyAllWindows()

    processed_time = time.time()
    print(f'Video was processed in: {time.strftime("%Mm %Ss", time.gmtime(round(processed_time - start_time, 3)))}')

    if post_analysis:
        print('\n\033[36mProducing post-set analysis (NOT COMPLETE)...')
        good_reps = 0
        poor_depth_reps = 0
        poor_lockout_reps = 0
        no_asc_reps = 0
        no_desc_reps = 0
        unknown_reps = 0

        squat_path = "".join([word[0] for word in squat_path])

        started = True
        begin = 0
        reps = []
        for (t, i) in rep_indexes:
            if not started:
                if t == 'start':
                    begin = i
                    started = True
                else:
                    reps[-1] = squat_path[begin:i+1]
            else:
                if t == 'end':
                    reps.append(squat_path[begin:i+1])
                    started = False
                else:
                    begin = i

        # Check this num is correct
        # print(f'In total there were {len(reps)} reps of varying quality detected')

        for rep in reps:
            if rep == 'DBAS':
                good_reps += 1
            elif rep == 'DAS':
                poor_depth_reps += 1
            elif rep == 'DBA':
                poor_lockout_reps += 1
            elif rep == 'DA':
                poor_depth_reps += 1
                poor_lockout_reps += 1
            elif rep == 'BAS':
                no_desc_reps += 1
            elif rep == 'DBS':
                no_asc_reps += 1
            else:
                print('Unknown rep sequence:', rep)
                unknown_reps += 1

        print('Good Reps:\t', good_reps)
        print('Poor Depth:\t', poor_depth_reps)
        print('Poor Lockout:\t', poor_lockout_reps)
        print('No Ascent:\t', no_asc_reps)
        print('No Descent:\t', no_desc_reps)
        print('Unknown:\t', unknown_reps)
        # use data in squat_path, (save squat durations?), ...
        # produce graphs / summary e.g...
        # 5 good reps performed with tempos of ... indicating RPE of ...
        # 2 reps had poor depth at the bottom. try doing ... next time
        # 1 rep had a poor lockout while standing...
        # 1 rep did not register you descending, ensure the camera is in a good spot...
        # No asymmetries detected in joint paths
        # blah?
    print('\033[0m')

    if save_video:
        processed_video_path = f'{video_source[:-4]}_processed.mp4'
        print(f'Saving video to "{processed_video_path}" ...')

        # Save video
        f_shape = frames[0].shape
        out = cv2.VideoWriter(
            processed_video_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (f_shape[1], f_shape[0])
        )
        for frame in frames:
            out.write(frame)
        out.release()

    print('Done.\n')

if __name__ == '__main__':
    pose_detector = MediaPipeDetector()
    form_analyser = SquatFormAnalyzer()
    frame_stack = 2 # min 2 (for now, start and end frame is only used so this is best as 2)
    frame_skip = 3
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    mp_pose = mp.solutions.pose
    text_colour = (219, 123, 3)

    videos = []
    videos.append("backend/assets/barbell_back_squat.mp4")
    # videos.append("backend/assets/barbell_front_squat.mp4")
    # videos.append("backend/assets/goblet_squat.mp4")
    # videos.append("backend/assets/dumbbell_goblet_squat.mp4")
    # videos.append("backend/assets/dan_squat.mp4")
    # videos.append("backend/assets/me_squat.mp4")
    # videos.append(0)

    # TODO: Refactor process_data to reduce complexity
        # TODO: move constants out of loop
    # TODO: make app select video from album for now
    # TODO: use post_analysis bool in above loop to improve performance is False
    # TODO: record rep durations?
    # TODO: create review video highlighting mistakes

    for video_path in videos:
        # ensure that video is ~720x1280 @ 30fps for best results
        process_data(video_path, frame_stack, frame_skip, show_output=True, post_analysis=True, save_video=False)
