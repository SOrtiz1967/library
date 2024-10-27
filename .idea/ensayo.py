import cv2
import numpy as np

# Function to draw a grid of 3 rows and 9 columns of rectangles and return their positions
def draw_color_grid(frame):
    height, width, _ = frame.shape
    # Define rectangle width and height based on screen size
    rect_width = min(width, height) // 12  # Keep the width the same
    rect_height = int(rect_width * 1.5)  # Make the height 1.5 times the width
    padding_x = (width - (9 * rect_width)) // 10  # Horizontal padding
    padding_y = (height - (3 * rect_height)) // 4  # Vertical padding

    positions = []
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]  # Red, Green, Blue (can be cycled)
    for row in range(3):
        row_positions = []
        for col in range(9):
            # Calculate top-left corner of the rectangle
            x = int(padding_x + col * (rect_width + padding_x))
            y = int(padding_y + row * (rect_height + padding_y))

            # Draw rectangle (hollow rectangle)
            color = colors[col % len(colors)]  # Cycle through red, green, blue
            cv2.rectangle(frame, (x, y), (x + rect_width, y + rect_height), color, 2)

            # Save position of the rectangle
            row_positions.append((x, y, x + rect_width, y + rect_height))
        positions.append(row_positions)

    return positions

# Function to check if a color is detected in a rectangle
def is_color_detected(mask, rectangle):
    x1, y1, x2, y2 = rectangle
    mask_section = mask[y1:y2, x1:x2]
    return np.any(mask_section > 0)

# Function to write the name of the detected color inside the rectangle
def write_color_name(frame, color_name, rect):
    x1, y1, x2, y2 = rect
    # Calculate the center of the rectangle
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    # Set font, scale, and thickness
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2
    color = (255, 255, 255)  # White text
    # Put the text in the center of the rectangle
    cv2.putText(frame, color_name, (center_x - 30, center_y), font, font_scale, color, thickness)

# Function to process color detection and labeling
def detect_colors_and_label(frame, red_mask, green_mask, blue_mask, rectangles):
    for row in rectangles:
        for rect in row:
            if is_color_detected(red_mask, rect):
                write_color_name(frame, "Red", rect)
            elif is_color_detected(green_mask, rect):
                write_color_name(frame, "Green", rect)
            elif is_color_detected(blue_mask, rect):
                write_color_name(frame, "Blue", rect)

# Capture video from webcam
webcam = cv2.VideoCapture(0)

while True:
    # Read each frame from the webcam
    ret, frame = webcam.read()
    
    if not ret:
        break

    # Convert the frame to HSV
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define color ranges for red, green, and blue in HSV
    red_lower = np.array([136, 87, 111], np.uint8)
    red_upper = np.array([180, 255, 255], np.uint8)
    green_lower = np.array([25, 100, 72], np.uint8)
    green_upper = np.array([102, 255, 255], np.uint8)
    blue_lower = np.array([94, 80, 2], np.uint8)
    blue_upper = np.array([120, 255, 255], np.uint8)

    # Create masks for the colors
    red_mask = cv2.inRange(hsv_frame, red_lower, red_upper)
    green_mask = cv2.inRange(hsv_frame, green_lower, green_upper)
    blue_mask = cv2.inRange(hsv_frame, blue_lower, blue_upper)

    # Apply dilation to remove noise in the masks
    kernel = np.ones((5, 5), "uint8")
    red_mask = cv2.dilate(red_mask, kernel)
    green_mask = cv2.dilate(green_mask, kernel)
    blue_mask = cv2.dilate(blue_mask, kernel)

    # Draw the 3x9 grid of hollow colored rectangles and get their positions
    rectangles = draw_color_grid(frame)

    # Detect colors and label them inside the rectangles
    detect_colors_and_label(frame, red_mask, green_mask, blue_mask, rectangles)

    # Show the current frame
    cv2.imshow('Color Detection with Labels', frame)

    # Break loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
webcam.release()
cv2.destroyAllWindows()
