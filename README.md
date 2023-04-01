# Squat Form Analyser
Squat Form Analyser is a real-time pose estimation and analysis tool that helps users maintain proper form while performing squats. It leverages the power of the MediaPipe library to detect human poses and provides feedback on squat form, including joint angles, posture, and joint levels.

## Features
Real-time pose estimation and analysis
Feedback on joint angles, posture, and joint levels
Customizable form criteria based on user orientation (face-on or side-on)
Support for live video streams and recorded videos
Visual output with pose landmarks and feedback text

## Installation
### Requirements
Python 3.6 or higher
OpenCV
MediaPipe
(Optional) imutils

### Steps
Clone this repository:
git clone https://github.com/yourusername/squat-form-analyser.git

Change into the repository directory:
cd squat-form-analyser

(Optional) Create a virtual environment:
python3 -m venv venv
source venv/bin/activate

Install the required packages:
pip install -r requirements.txt

## Usage
You can run the Squat Form Analyser using the following command:

python main.py [--video VIDEO_PATH] [--show_output]

- `--video VIDEO_PATH`: (Optional) Specify a video file to use instead of a live video stream. By default, the live video stream from the default camera will be used.
- `--show_output`: (Optional) Display the visual output with pose landmarks and feedback text. Note that enabling this option may slow down performance.

## Customization
You can customize the form criteria for face-on and side-on orientations by modifying the `form_thresholds_beginner` and `form_thresholds_advanced` dictionaries in the `SquatFormAnalyser` class. Update the joint angle ranges and level thresholds as needed to fit your specific requirements.

## License
TODO
