# code base source: https://github.com/google-ai-edge/mediapipe/blob/master/docs/solutions/hands.md
# adjusted by Luca & Leonie

import cv2
import math
import mediapipe as mp
import sys
import time
import pyautogui
from pynput.mouse import Button, Controller

VIDEO_ID = 0

# set your camera resolution for mouse movement (for example 1280x720 (720p HD resolution))
camera_width, camera_height = 1280, 720

if len(sys.argv) > 1:
    VIDEO_ID = int(sys.argv[1])
elif len(sys.argv) > 3:
    camera_width = int(sys.argv[2])
    camera_height = int(sys.argv[3])

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

radius_index = 20
padding_x = 100
padding_y = 100

prev_frame_time = 0
new_frame_time = 0

# calculate fps for interpolation
def calculate_fps():
    global prev_frame_time, new_frame_time
    new_frame_time = time.time()
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    return int(fps)


# get screen resolution
screen_width, screen_height = pyautogui.size()

# For static images:
IMAGE_FILES = []
with mp_hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5) as hands:
    for idx, file in enumerate(IMAGE_FILES):
        # Read an image, flip it around y-axis for correct handedness output (see
        # above).
        image = cv2.flip(cv2.imread(file), 1)
        # Convert the BGR image to RGB before processing.
        results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

# For webcam input:
mouse = Controller()
cap = cv2.VideoCapture(VIDEO_ID)

with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_height, image_width, _ = image.shape
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # index finger position
                index_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x * image_width
                index_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y * image_height

                # add padding to camera image so you can reach the edge of the screen with the mouse
                adjusted_image_width = image_width - 2 * padding_x
                adjusted_image_height = image_height - 2 * padding_y

                # calculate mouse coordinates
                mouse_x = screen_width - (screen_width * (index_tip_x - padding_x) / adjusted_image_width)
                mouse_y = screen_height * (index_tip_y - padding_y) / adjusted_image_height

                mouse.position = (mouse_x, mouse_y)

                # uncomment if you want to perform a left click with pushing index and thumb together
                
                radius_thumb = 20
                
                
                # thumb position
                thumb_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x * image_width
                thumb_tip_y = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].y * image_height
                
                # Calculate the distance between the centers of the two circles
                distance = math.sqrt((index_tip_x - thumb_tip_x) ** 2 + (index_tip_y - thumb_tip_y) ** 2)
                
                # Check if the distance is less than or equal to the sum of the radii
                if distance <= (radius_index + radius_thumb):
                    mouse.press(Button.left)
                else:
                    mouse.release(Button.left)
               
                image = cv2.circle(image, (int(thumb_tip_x), int(thumb_tip_y)), radius_thumb, (0, 0, 255), 2)
               

                image = cv2.circle(image, (int(index_tip_x), int(index_tip_y)), radius_index, (255, 0, 0), 2)

        fps = calculate_fps()

        # print fps -> uncomment the following
        # print(f'FPS: {fps}')

        # Check FPS and interpolate frames if below 20
        # Interpolate frames using cv2.INTER_LINEAR or cv2.INTER_CUBIC
        if fps < 20:
            image = cv2.resize(image, (camera_width, camera_height), interpolation=cv2.INTER_LINEAR)

        # uncomment if you want to see your tracked index
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))

        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
