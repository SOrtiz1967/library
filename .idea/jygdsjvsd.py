import numpy as np
import cv2

# Capturing video through webcam
webcam = cv2.VideoCapture(0)

# Function to draw a grid of colored squares and return their positions
def draw_color_grid(frame):
    height, width, _ = frame.shape
    # Define square size and spacing based on screen size
    square_size = min(width, height) // 10  # Adjusted size for 9 columns
    padding_x = (width - (9 * square_size)) // 10  # Horizontal padding
    padding_y = (height - (3 * square_size)) // 4  # Vertical padding

    positions = []
    # Define more colors to cover 9 columns (alternating colors per column)
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), 
              (255, 255, 0), (255, 0, 255), (128, 0, 128), (255, 165, 0), (0, 128, 128)]
    
    for row in range(3):
        row_positions = []
        for col in range(9):
            # Calculate top-left corner of the square
            x = padding_x + col * (square_size + padding_x)
            y = padding_y + row * (square_size + padding_y)

            # Draw rectangle (hollow square)
            color = colors[col % len(colors)]  # Cycle through colors list
            cv2.rectangle(frame, (x, y), (x + square_size, y + square_size), color, 2)

            # Save position of the rectangle
            row_positions.append((x, y, x + square_size, y + square_size))
        positions.append(row_positions)

    return positions

# Function to restrict mask to a specific rectangle
def apply_mask_to_rectangle(mask, rectangle):
    x1, y1, x2, y2 = rectangle
    mask_out = np.zeros_like(mask)
    mask_out[y1:y2, x1:x2] = mask[y1:y2, x1:x2]
    return mask_out

# Function to check if a color is detected in a rectangle
def is_color_detected(mask, rectangle):
    x1, y1, x2, y2 = rectangle
    mask_section = mask[y1:y2, x1:x2]
    return np.any(mask_section > 0)

# Function to add detection text inside rectangles
def add_detection_text(frame, rectangle, color_name):
    x1, y1, x2, y2 = rectangle
    text_position = (x1 + 10, y1 + (y2 - y1) // 2)
    cv2.putText(frame, color_name, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

# Function to check if a full row is correct based on color detection for each column
def check_row_correctness(red_mask, green_mask, blue_mask, row_rectangles, frame, colors):
    row_correct = True
    for idx, rectangle in enumerate(row_rectangles):
        color = colors[idx % len(colors)]  # Get the expected color for this square
        if color == "Red":
            detected = is_color_detected(red_mask, rectangle)
            if detected:
                add_detection_text(frame, rectangle, "Red Detected")
            row_correct &= detected
        elif color == "Green":
            detected = is_color_detected(green_mask, rectangle)
            if detected:
                add_detection_text(frame, rectangle, "Green Detected")
            row_correct &= detected
        elif color == "Blue":
            detected = is_color_detected(blue_mask, rectangle)
            if detected:
                add_detection_text(frame, rectangle, "Blue Detected")
            row_correct &= detected
    return row_correct

# Define expected colors for each square in a row (9 colors)
expected_colors = ["Red", "Green", "Blue", "Yellow", "Cyan", "Magenta", "Purple", "Orange", "Teal"]

# Start a while loop
while True:
    # Reading the video from the webcam in image frames
    _, imageFrame = webcam.read()

    # Convert the imageFrame from BGR to HSV color space
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

    # Define color ranges
    red_lower = np.array([136, 87, 111], np.uint8)
    red_upper = np.array([180, 255, 255], np.uint8)
    green_lower = np.array([25, 52, 72], np.uint8)
    green_upper = np.array([102, 255, 255], np.uint8)
    blue_lower = np.array([94, 80, 2], np.uint8)
    blue_upper = np.array([120, 255, 255], np.uint8)

    # Create masks for red, green, and blue
    red_mask = cv2.inRange(hsvFrame, red_lower, red_upper)
    green_mask = cv2.inRange(hsvFrame, green_lower, green_upper)
    blue_mask = cv2.inRange(hsvFrame, blue_lower, blue_upper)

    # Morphological Transform, Dilation for each color
    kernel = np.ones((5, 5), "uint8")
    red_mask = cv2.dilate(red_mask, kernel)
    green_mask = cv2.dilate(green_mask, kernel)
    blue_mask = cv2.dilate(blue_mask, kernel)

    # Draw the 3x9 grid of hollow colored squares and get their positions
    rectangles = draw_color_grid(imageFrame)

    # Check each row for correctness
    row_1_correct = check_row_correctness(red_mask, green_mask, blue_mask, rectangles[0], imageFrame, expected_colors)
    row_2_correct = check_row_correctness(red_mask, green_mask, blue_mask, rectangles[1], imageFrame, expected_colors)
    row_3_correct = check_row_correctness(red_mask, green_mask, blue_mask, rectangles[2], imageFrame, expected_colors)

    # Print the correct row if the colors are detected in the right order
    if row_1_correct:
        print("Fila 1 correcta")
    if row_2_correct:
        print("Fila 2 correcta")
    if row_3_correct:
        print("Fila 3 correcta")

    # Show the image with the grid and detection texts
    cv2.imshow("Multiple Color Detection in Real-Time", imageFrame)

    # Program Termination
    if cv2.waitKey(10) & 0xFF == ord('q'):
        webcam.release()
        cv2.destroyAllWindows()
        break
