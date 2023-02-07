import numpy as np
from mediapipe_estimator import MediaPipeDetector
from squat_check import SquatFormAnalyzer
import cv2
import mediapipe as mp
import time


def draw_text(img, text,
          font=cv2.FONT_HERSHEY_PLAIN,
          pos=(0, 0),
          font_scale=3,
          font_thickness=2,
          text_color=(0, 255, 0),
          text_color_bg=(0, 0, 0)
          ):
    """ Draws text on a cv2 image in a given spot with a background """
    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
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


def rescale_frame(frame, percent=50):
    width = int(frame.shape[1] * percent/ 100)
    height = int(frame.shape[0] * percent/ 100)
    dim = (width, height)
    return cv2.resize(frame, dim, interpolation =cv2.INTER_AREA)


def display_angle_at_joint(frame, joint, angle):
    if joint.visibility > 0.5:
        joint_pos = [joint.x, joint.y]
        draw_text(
            frame,
            str(angle) + ' deg',
            pos=tuple(np.multiply(joint_pos, frame.shape[:2][::-1]).astype(int))
        )


def process_data(video_source, frame_stack, frame_skip, show_output, save_video):
    print(f'Beginning "{video_source}" ...')

    # Get video capture and constants (organize these)
    cap = cv2.VideoCapture(video_source)
    fps = cap.get(cv2.CAP_PROP_FPS)
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) / fps
    start_time = time.time()
    frame_width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    frame_height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    # Window dimensions
    window_width = None
    window_height = 500
    dim = get_aspect_dim((frame_height, frame_width), window_width, window_height)

    # Output video information
    print(f'Total video length is : {time.strftime("%Mm %Ss", time.gmtime(video_length))}')

    # Initiate variables
    frames = []
    results_stack = []
    rep_count = 0
    squat_start_time = 0
    squat_end_time = 0
    initiated_squat = False
    squat_details = ['Unsure', '', '', '', ''] # move this into squat_check and get via call. also use in determine_squat_stage()

    # Begin loop
    while True:
        # Get the frame
        frame_start_time = time.time()
        success, frame = cap.read()
        if not success:
            break

        # Process then send the data
        pose_landmarks = pose_detector.make_prediction(frame)

        if len(results_stack) > 0 and len(results_stack) % frame_stack == 0:
            squat_details = form_analyser.analyse_landmark_stack(results_stack)
            results_stack = []

            if not initiated_squat and squat_details[0] == 'Descending':
                initiated_squat = True
                squat_start_time = time.time()
            elif initiated_squat and squat_details[0] == 'Standing':
                initiated_squat = False
                squat_end_time = time.time()
                rep_count += 1

        if pose_landmarks is None:
            results_stack = []
        elif len(frames) % (frame_skip + 1) == 0:
            results_stack.append(pose_landmarks)

        # Draw the pose annotation
        frame.flags.writeable = True
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

        # Draw squat stage and repetitions
        draw_text(frame, squat_details[0], font_scale=4)
        draw_text(frame, 'Repetitions: ' + str(rep_count), pos=(0, 40))

        # Calculate and draw the rep duration
        if squat_end_time >= squat_start_time:
            squat_duration = round(squat_end_time - squat_start_time, 2)
        draw_text(frame, 'Duration: ' + str(squat_duration) + 's', pos=(0, 70))

        # If the output is being shown in real-time, enforce desired fps and calculate actual fps
        if show_output:
            elapsed_time = time.time() - frame_start_time
            wait_time = int(1000/fps - elapsed_time)
            wait_time -= 35 # account for system delay

            if wait_time <= 0:
                wait_time = 1

            actual_fps = int(1 / (elapsed_time + wait_time/1000))
            if cv2.waitKey(wait_time) & 0xFF == ord('q'):
                break

            # Display final output
            draw_text(frame, 'FPS: ' + str(actual_fps), pos=(0, 100))
            cv2.imshow('MediaPipe Pose', cv2.resize(frame, dim, cv2.INTER_AREA))

        frames.append(frame)

    cap.release()
    cv2.destroyAllWindows()

    processed_time = time.time()
    print(f'Video was processed in: {time.strftime("%Mm %Ss", time.gmtime(round(processed_time - start_time, 3)))}')

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

    videos = []
    # comment unwanted
    # videos.append("backend/assets/person_walking.mp4")
    videos.append("backend/assets/barbell_back_squat.mp4")
    videos.append("backend/assets/barbell_front_squat.mp4")
    videos.append("backend/assets/dumbbell_goblet_squat.mp4")
    videos.append("backend/assets/dan_squat.mp4")
    videos.append("backend/assets/me_squat.mp4")
    # videos.append(0)

    for video_path in videos:
        # ensure that video is ~720x1280 @ 30fps for best results
        process_data(video_path, frame_stack, frame_skip, show_output=False, save_video=True)
