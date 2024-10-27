import numpy as np 
import cv2 

# Capturing video through webcam 
webcam = cv2.VideoCapture(0) 

def get_coordinates(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f'Coordenadas: ({x}, {y})')

# Set mouse callback
cv2.namedWindow("Multiple Color Detection in Real-Time")
cv2.setMouseCallback("Multiple Color Detection in Real-Time", get_coordinates)

# Start a while loop 
while(1): 
    # Reading the video from the webcam in image frames 
    _, imageFrame = webcam.read() 

    # Convert the imageFrame in BGR to HSV color space 
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV) 

    # Define color ranges
    red_lower = np.array([136, 87, 111], np.uint8) 
    red_upper = np.array([180, 255, 255], np.uint8)
    green_lower = np.array([25, 52, 72], np.uint8) 
    green_upper = np.array([102, 255, 255], np.uint8) 
    blue_lower = np.array([94, 80, 2], np.uint8) 
    blue_upper = np.array([120, 255, 255], np.uint8) 

    # Create masks
    red_mask = cv2.inRange(hsvFrame, red_lower, red_upper)
    green_mask = cv2.inRange(hsvFrame, green_lower, green_upper) 
    blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper) 

    # Morphological Transform, Dilation for each color 
    kernel = np.ones((5, 5), "uint8") 
    red_mask = cv2.dilate(red_mask, kernel) 
    green_mask = cv2.dilate(green_mask, kernel) 
    blue_mask = cv2.dilate(blue_mask, kernel) 

    # Function to draw contours and labels
    def draw_contours(mask, color, label):
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
        for contour in contours: 
            area = cv2.contourArea(contour) 
            if area > 300: 
                x, y, w, h = cv2.boundingRect(contour) 
                cv2.rectangle(imageFrame, (x, y), (x + w, y + h), color, 2) 
                cv2.putText(imageFrame, label, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color) 

    # Draw contours for each color
    draw_contours(red_mask, (0, 0, 255), "Red Colour")
    draw_contours(green_mask, (0, 255, 0), "Green Colour")
    draw_contours(blue_mask, (255, 0, 0), "Blue Colour")

    # Show the image
    cv2.imshow("Multiple Color Detection in Real-Time", imageFrame) 

    # Program Termination 
    if cv2.waitKey(10) & 0xFF == ord('q'): 
        webcam.release() 
        cv2.destroyAllWindows() 
        break
