# Volume Control via Hand Gestures

A Python project that uses computer vision and machine learning to control system volume via hand gestures.

## Table of Contents

1. #introduction
2. #requirements
3. #installation
4. #usage
5. #how-it-works
6. #contributing
7. #license

## Introduction

This project uses OpenCV and MediaPipe to detect hand gestures and control system volume accordingly. It's a fun and innovative way to interact with your computer.

## Requirements

- Python 3.x
- OpenCV
- MediaPipe
- pycaw (for Windows volume control)

## Installation

1. Clone the repository: git clone https://github.com/lakshyash5820/volume-control-via-hand-gestures.git
2. Install required libraries: pip install opencv-python mediapipe pycaw

## Usage

1. Run the script: python volume_control.py
2. Use hand gestures to control volume:
    - Palm facing upwards: increase volume
    - Palm facing downwards: decrease volume
    - Fist: mute/unmute volume

## How it Works

1. The script uses OpenCV to capture video frames from the webcam.
2. MediaPipe's Hands API detects hand landmarks in each frame.
3. Based on the hand landmarks, the script determines the hand gesture and controls system volume accordingly.

## Contributing

Contributions are welcome! If you'd like to improve this project, please fork the repository and submit a pull request.

## License

This project is licensed under the MIT License. See LICENSE for details.
