from enum import Enum
import numpy as np
from mediapipe_estimator import MediaPipeDetector
from squat_check import SquatFormAnalyzer
import cv2
import mediapipe as mp
import time


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


# def rescale_frame(frame, percent=50):
#     width = int(frame.shape[1] * percent/ 100)
#     height = int(frame.shape[0] * percent/ 100)
#     dim = (width, height)
#     return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)


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
    else:
        print(f'Beginning LIVE CAMERA FEED ...')

    # Get video capture and constants
    cap = cv2.VideoCapture(video_source)
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / fps
    start_time = time.time()
    frame_width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    # Squat form constants
    good_form_colour = text_colour
    bad_form_colour = (0, 0, 255)
    class RepQuality(Enum):
        BAD_DEPTH = 1
        BAD_LOCKOUT = 2
        NO_DESCENT = 3
        NO_ASCENT = 4
    
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
    # rep_history = []
    form_analysis = 'No rep Performed'
    form_colour = good_form_colour

    # Begin loop
    while True:
        # Get the frame
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

                    # TODO: account for all transitions
                    # ..., standing, ascending, ... = 
                    if len(squat_path) >= 2:
                        if squat_path[-2] == 'Standing' and squat_path[-1] == 'Descending':
                            form_analysis = 'In Progress'
                            form_colour = good_form_colour
                            squat_start_time = time.time()
                            # current_rep_quality = []

                        elif squat_path[-2] == 'Descending' and squat_path[-1] == 'Bottom':
                            form_analysis = 'Good Depth'

                        elif squat_path[-2] == 'Bottom' and squat_path[-1] == 'Ascending':
                            form_analysis = 'Good Depth'

                        elif squat_path[-2] == 'Descending' and squat_path[-1] == 'Ascending':
                            form_analysis = 'Bad Depth'
                            form_colour = bad_form_colour
                            # current_rep_quality.append(RepQuality.BAD_DEPTH)

                        elif squat_path[-2] == 'Standing' and squat_path[-1] == 'Bottom':
                            form_analysis = 'Descent Not Detected'
                            form_colour = bad_form_colour
                            # current_rep_quality.append(RepQuality.NO_DESCENT)

                        elif squat_path[-2] == 'Ascending' and squat_path[-1] == 'Descending':
                            form_analysis = 'No Lockout'
                            form_colour = bad_form_colour
                            squat_start_time = time.time()
                            # current_rep_quality.append(RepQuality.BAD_LOCKOUT)

                        elif squat_path[-2] == 'Bottom' and squat_path[-1] == 'Standing':
                            form_analysis = 'Ascent Not Detected'
                            form_colour = bad_form_colour
                            squat_end_time = time.time()
                            # current_rep_quality.append(RepQuality.NO_ASCENT)

                        elif squat_path[-2] == 'Ascending' and squat_path[-1] == 'Standing':
                            form_colour = good_form_colour
                            squat_end_time = time.time()

                        else:
                            form_analysis = ''


                        # ONLY COUNT CLEAN REPS?
                        if len(squat_path) >= 4 and squat_path[-4:] == ['Descending', 'Bottom', 'Ascending', 'Standing']:
                            # if len(squat_path) > 10: # set a limit to squat_path for memory optimisation (necessary?)
                            #     squat_path = squat_path[5:]
                            rep_count += 1


                        # when does a general rep start?
                            # ..., standing, descending, ...
                            # ..., ascending, descending, ...

                        # when does a general rep end?
                            # ..., ascending, standing, ...
                            # ..., bottom, standing, ...
                            
                        # TODO: determine overall rep here, add to rep history
                        # cleanup any unused variables/ constants and above if block

                        # if squat_path[-2:] in [['Ascending', 'Standing'], ['Bottom', 'Standing']]:
                        #     start = None
                        #     for i in range(len(squat_path) - 3):
                        #         if squat_path[i:i+2] in [['Standing', 'Descending'], ['Ascending', 'Descending']]:
                        #             start = i
                        #             break
                        #     if start is not None:
                        #         rep_history.append(squat_path[start:])
                            
                        #     squat_path = []

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

    cap.release()
    cv2.destroyAllWindows()

    processed_time = time.time()
    print(f'Video was processed in: {time.strftime("%Mm %Ss", time.gmtime(round(processed_time - start_time, 3)))}')

    if post_analysis:
        print('\nProducing post-set analysis...')
        good_reps = 0
        poor_depth_reps = 0
        poor_lockout_reps = 0
        no_asc_reps = 0
        no_desc_reps = 0

        print(squat_path)
        
        # for thing in rep_history:
        #     print(thing)

        # when does a general rep start?
        # ..., standing, descending, ...
        # ..., ascending, descending, ...

        # when does a general rep end?
        # ..., ascending, standing, ...
        # ..., bottom, standing, ...

        # need to account for back and forths of stage mid rep, e.g. STANDING, DESC, asc, desc, asc, desc, BOTTOM, ASC, STANDING

        print(f'In total there were {rep_count} qualifying reps detected')
        # Remove starting stages until first 'Standing'
        for i in range(len(squat_path)):
            if squat_path[i] == 'Standing':
                squat_path = squat_path[i:]
                break
        
        for stage in squat_path:
            # use flowchart to determine squat path
            # remember:
                    # when does a general rep start?
                    # ..., standing, descending, ...
                    # ..., ascending, descending, ...

                    # when does a general rep end?
                    # ..., ascending, standing, ...
                    # ..., bottom, standing, ...
            pass

        # # TODO: ensure rep_history is constructed correctly / this all can't be done more efficiently?
        # for rep in rep_history:
        #     # count good reps:
        #     if rep == ['Standing', 'Descending', 'Bottom', 'Ascending', 'Standing']:
        #         good_reps += 1
        #     elif rep == ['Ascending', 'Descending', 'Bottom', 'Ascending', 'Standing']:
        #         poor_lockout_reps += 1
        #     elif rep == ['Ascending', 'Descending', 'Ascending', 'Standing'] or \
        #         ['Standing', 'Descending', 'Bottom', 'Ascending', 'Standing']:
        #         poor_depth_reps += 1
        #     # etc.

        print('good_reps', good_reps)
        print('poor_depth_reps', poor_depth_reps)
        print('poor_lockout_reps', poor_lockout_reps)
        print('no_asc_reps', no_asc_reps)
        print('no_desc_reps', no_desc_reps)
        # use data in squat_path, (save squat durations?), ...
        # produce graphs / summary e.g...
        # 5 good reps performed with tempos of ... indicating RPE of ...
        # 2 reps had poor depth at the bottom. try doing ... next time
        # 1 rep had a poor lockout while standing...
        # 1 rep did not register you descending, ensure the camera is in a good spot...
        # No asymmetries detected in joint paths
        # blah?

        print()

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
    # comment unwanted
    # videos.append("backend/assets/person_walking.mp4")
    videos.append("backend/assets/barbell_back_squat.mp4")
    videos.append("backend/assets/barbell_front_squat.mp4")
    videos.append("backend/assets/goblet_squat.mp4")
    videos.append("backend/assets/dumbbell_goblet_squat.mp4")
    videos.append("backend/assets/dan_squat.mp4")
    videos.append("backend/assets/me_squat.mp4")
    # videos.append(0)

    # TODO: look into this for threading:
    # https://pyimagesearch.com/2017/02/06/faster-video-file-fps-with-cv2-videocapture-and-opencv/
    # TODO: fix squat stage detection to work better for all examples. extract data for easier analysis rather than watching video?
    # TODO: redo how squat stages are interpreted. come up with flowchart for analysing motion
    # TODO: move constants out of loop

    for video_path in videos:
        # ensure that video is ~720x1280 @ 30fps for best results
        process_data(video_path, frame_stack, frame_skip, show_output=False, post_analysis=False, save_video=True)
