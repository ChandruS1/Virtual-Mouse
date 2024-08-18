import mediapipe as mp
import cv2
import pyautogui
import win32api
import time
from math import sqrt

# Initialize MediaPipe components
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = win32api.GetSystemMetrics(0), win32api.GetSystemMetrics(1)
CURSOR_SCALE_X, CURSOR_SCALE_Y = SCREEN_WIDTH / 640, SCREEN_HEIGHT / 480  # Assuming 640x480 resolution for webcam
CLICK_THRESHOLD = 30  # Adjust as needed

# Open video capture
video = cv2.VideoCapture(0)

click = 0
indexfingertip_x = indexfingertip_y = None
thumbfingertip_x = thumbfingertip_y = None

with mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.8) as hands:
    while video.isOpened():
        ret, frame = video.read()
        if not ret:
            break

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = cv2.flip(image, 1)
        imageHeight, imageWidth, _ = image.shape

        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for handLandmarks in results.multi_hand_landmarks:
                for point in mp_hands.HandLandmark:
                    normalizedLandmark = handLandmarks.landmark[point]
                    pixelCoordinatesLandmark = mp_drawing._normalized_to_pixel_coordinates(
                        normalizedLandmark.x, normalizedLandmark.y, imageWidth, imageHeight
                    )

                    if pixelCoordinatesLandmark:
                        x, y = pixelCoordinatesLandmark
                        
                        if point == mp_hands.HandLandmark.INDEX_FINGER_TIP:
                            indexfingertip_x, indexfingertip_y = x, y
                            # Move the cursor
                            win32api.SetCursorPos((int(indexfingertip_x * CURSOR_SCALE_X), int(indexfingertip_y * CURSOR_SCALE_Y)))
                        
                        elif point == mp_hands.HandLandmark.THUMB_TIP:
                            thumbfingertip_x, thumbfingertip_y = x, y

                        # Check if both fingertips are available and calculate distance
                        if indexfingertip_x is not None and thumbfingertip_x is not None:
                            distance_x = abs(indexfingertip_x - thumbfingertip_x)
                            distance_y = abs(indexfingertip_y - thumbfingertip_y)
                            
                            if distance_x < CLICK_THRESHOLD and distance_y < CLICK_THRESHOLD:
                                click += 1
                                if click % 5 == 0:
                                    print("single click")
                                    pyautogui.click()
                            else:
                                # Reset click count if fingers are too far apart
                                click = 0

        cv2.imshow('Hand Tracking', image)

        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

video.release()
cv2.destroyAllWindows()
