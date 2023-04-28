from squat_analyser import process_video_from_fe

if __name__ == "__main__":
    videos = []
    videos.append('backend/assets/barbell_back_squat.mp4')
    videos.append('backend/assets/goblet_squat.mp4')
    videos.append('backend/assets/barbell_front_squat.mp4')
    videos.append('backend/assets/dumbbell_goblet_squat.mp4')
    videos.append('backend/assets/me_squat.mp4')

    for video in videos:
        print('Video:', video)
        processed_vid_path, form_analysis = process_video_from_fe(video)
        print(processed_vid_path)
        for rep_dur, rep_seq in form_analysis['reps']:
            if rep_seq == ['Standing', 'Transition', 'Bottom', 'Transition']:
                print(f'\u001b[32mGood Rep, duration: {round(rep_dur, 2)}s')
            else:
                print(f'\u001b[31mBad Rep, duration: {round(rep_dur, 2)}s, seq: {rep_seq}')
        print('\u001b[0m')