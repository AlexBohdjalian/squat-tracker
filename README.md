# Squat Tracker
Squat Tracker is a real-time pose estimation and analysis tool that helps users maintain proper form while performing squats. It leverages the power of the MediaPipe library to detect human poses and provides feedback on squat form, including joint angles, posture, and joint levels.

## Features
Real-time pose estimation and analysis
Feedback on joint angles, posture, and joint levels
Customizable form criteria based on user orientation (face-on or side-on)
Visual output with pose landmarks and feedback text

## Installation

### Steps
Clone the repository:

    git clone https://github.com/AlexBohdjalian/squat-tracker.git

Build frontend packages:

    cd squat-tracker
    cd frontend
    yarn

## Usage
Install Expo Go onto your phone and run `npx expo start` in the `frontend/` directory.
From the app, you can then select the `squat-tracker` app from the list.

For live video analysis, navigate to `backend/live_analysis/` and run the `rtmp_server.py` file then within a short time-frame, start the form analysis in the app. The file will end automatically when the analysis is done. Variables `show_stream` and `show_feedback` are available if you want to see feedback in the console or the live video stream. Note that this file needs to be re-run each time you want to do some form-analysis. In an ideal world I would have made it so that the script was constantly running on a high-performance cloud-hosted server but this would cost more than I can afford.

For non-live video analysis, navigate to `backend/non_live_analysis/` and run the `server.py` file. While this file is running you can choose to process as many videos as you like at your own pace. When you are done, shut down the server with the `ctrl+c` command in the terminal.
