import cv2
import numpy as np

# Function to get RGB color at mouse click position
def get_color_at_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        # Get the BGR values at the mouse click position
        bgr_color = frame[y, x]
        # Convert BGR to RGB
        rgb_color = (bgr_color[2], bgr_color[1], bgr_color[0])
        print(f"Clicked at ({x}, {y}) - RGB Color: {rgb_color}")

# Capture video from webcam
webcam = cv2.VideoCapture(0)

# Create a named window and set the mouse callback function
cv2.namedWindow('Color Detection at Click')
cv2.setMouseCallback('Color Detection at Click', get_color_at_click)

while True:
    # Read each frame from the webcam
    ret, frame = webcam.read()
    
    if not ret:
        break
    
    # Show the current frame
    cv2.imshow('Color Detection at Click', frame)

    # Break loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
webcam.release()
cv2.destroyAllWindows()
