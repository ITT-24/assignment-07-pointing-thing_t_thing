# 01 - pointing input 
## Overview

This project allows you to control your mouse using hand gestures captured by your camera. By utilizing OpenCV (cv2) and the Google MediaPipe Hand Landmarker model, you can track your index finger to determine the mouse's position. Additionally, when activated, you can perform a left-click action by pinching your index finger and thumb together.

## Features

- Mouse Position Control: The position of your mouse cursor is controlled by tracking the movement of your index finger.
- Left-Click Action: Simulate a left-click by pinching your index finger and thumb together.

## Installation 
```
pip install -r requirements.txt
```

## Usage 

### Default

To run the program with the default settings, use the following command:

```
python3 pointing_input.py
```

The default settings are:

- VIDEO_ID = 0 (use the default camera)
- CLICK_IS_ACTIVE = False (left-click action is disabled)
- camera_width = 1280 (camera resolution width)
- camera_height = 720 (camera resolution height)


### Set Parameters via terminal:

These parameters can also be customized when running the program. For example:

```
python3 pointing_input.py 1 False 1280 720
```

```
python3 pointing_input.py <VIDEO_ID> <CLICK_IS_ACTIVE> <camera_width> <camera_height>
```

- <VIDEO_ID>: Integer representing the camera ID.
- <CLICK_IS_ACTIVE>: True or False to enable or disable left-click.
- <camera_width>: Integer for the camera resolution width.
- <camera_height>: Integer for the camera resolution height.

**Ensure that the camera_width and camera_height match the resolution of your camera for accurate mouse movement tracking.**

### Parameter Descriptions

- VIDEO_ID (default: 0):
The ID of the camera to use. If you have multiple cameras, you can select which one by specifying its ID.

- CLICK_IS_ACTIVE (default: False):
Whether the left-click action is enabled. Set to True to enable left-click by pinching the index finger and thumb together.

- camera_width (default: 1280):
The width resolution of the camera. Ensure this matches the resolution of your camera for optimal performance.

- camera_height (default: 720):
The height resolution of the camera. Ensure this matches the resolution of your camera for optimal performance.


## Troubleshooting
Sometimes a left click will not be recognized if your fingers are smaller or bigger than expected. If so it might be neccessary to adjust the `FINGER_RADIUS` (line 19 in pointing_input.py):

### Adjusting Parameters
- For larger fingers (typically males): FINGER_RADIUS = 18
- For smaller fingers (typically females): FINGER_RADIUS = 10


## Credits

- This project uses the [MediaPipe Hand Landmarker by Google](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker?hl=de).
- As code base we used the this GIT Repo: [google-ai-edge/mediapipe](https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/hands.md).

# 02 - Fitt's Law Experiment

## Overview
In this project, we conducted a Fitts Law experiment where participants had to click on a red circle. These circles were arranged in a circular pattern, with a total of 7 circles. The purpose of this experiment was to gather data on the performance of different input devices under various conditions.

## Usage
### 1. Change the Config File:

Open the config file and adjust the settings to your preferences.
- Set the participant ID.
- Set the latency (in seconds).
- Choose the input device.

Other parameters can also be modified as desired.

### 2. Run the File:

```
python3 fitts-law.py
```

### 3. Add Latency (if you want):

To add latency, click on the "Add Latency" button. The button will turn green if latency is activated.

### 4. Start the Experiment:

To begin the experiment, click on the large red circle.

### 5. Save the Results:

After the experiment concludes, the results will be saved automatically.
If a file with the same settings already exists, you have the following options:
- Press y: A new file with the current timestamp added to the filename is created.
- Press n: The file will be deleted, and no changes will be saved from the experiment.
- Press o: Override the existing file with the current settings.

## Experiment Details
- Task: Participants were required to click on red circles arranged in a circular pattern.
- Number of Circles: 7
- All experiments were done on the same Laptop: MacBook Air 2020 (Apple Silicon M1)

### Logged Data: The following data was logged into a file named id-inputdevice.csv:

- location: folder logs


- id: Participant ID
- trial: Trial number
- radius: Radius of the target circle
- distance: Distance from one target circle to the other 
- latency: Latency introduced (if any)
- hit: Whether the target was hit or not
- time: Time between clicks
- accuracy: Accuracy of the click (how far away from the center)
- click_x: X-coordinate of the click
- click_y: Y-coordinate of the click
- target_x: X-coordinate of the target
- target_y: Y-coordinate of the target
- click_time: Timestamp of the click

## Input Devices
We tested the following input devices:

- Standard mouse
- Mouse with a 150ms latency
- Hand gesture control (index finger and thumb) using the pointing_input.py script
- Touchpad

## Participants
Three participants took part in the experiment:

- Clara
- Leonie
- Luca


## Config 

Using the `config.csv`, you can change any parameter. That file will be used by default. Alternativly use: `py fitts-law.py -c path/to/config.csv`, for a custom file(path) (with the same format)

### Config Manual
- latency should be written in seconds (0.15 = 150 ms)
- repetitions is how many rounds of the experiment run
  - e.g. if you have 3 conditions (radii, distances), than those 3 conditions all run 3 times each
- device is the input device
  - used for saving the file
  - if you forget to change it, the program will not override files, but will ask you how to proceed (in the terminal) 


## Logs (for us):
**The application logs:** (in `logs`-folder)
- [x] hit (True/False)
- [x] position of cursor on click 
- [x] position of clicked target
- [x] time between appearance of new marked target and next click
- [x] parameters set in config (id, radius, distance, trial, ...)
- [x] add latency 
- [x] add start screen
- [x] a timestamp of the when a the click occurs
- [x] written evaluation


## 03 - Evaluation

See `evaluation/fitts.ipynb` where we evaluated and interpretated our results.

Here you can also find a Problem Section as wished.


## Probleme
- Lag hat am anfang nicht funktioniert
Am anfang hatten wir verzögerung ums doppelte und dann mit threading gelöst

- kamera boundary für task 1
ende der kamera war nicht ende des bildschirms (Rand) -> haben padding eingebau und von klein auf groß umgerechnet 

- Falls ein Klick-Event ausgeführt werden sollte, wurden immer ganz viele ausgelöst
Am Ende einen einfachen Check eingeführt, bei dem man erst "loslassen" muss, bevor ein neuer Event triggern kann



[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/KHzC7ivQ)

