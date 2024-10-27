import numpy as np
import cv2

# Capturing video through webcam
webcam = cv2.VideoCapture(0)

# Function to draw a grid of colored squares and return their positions
def draw_color_grid(frame):
    height, width, _ = frame.shape
    # Define square size and spacing based on screen size
    square_size = min(width, height) // 4  # Make squares larger
    padding_x = (width - (3 * square_size)) // 4  # Horizontal padding
    padding_y = (height - (3 * square_size)) // 4  # Vertical padding

    positions = []
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0)]  # Red, Green, Blue
    for row in range(3):
        row_positions = []
        for col in range(3):
            # Calculate top-left corner of the square
            x = padding_x + col * (square_size + padding_x)
            y = padding_y + row * (square_size + padding_y)

            # Draw rectangle (hollow square)
            color = colors[col % len(colors)]  # Cycle through red, green, blue
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
    cv2.putText(frame, color_name, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

# Function to check if a full row is correct (red, green, blue)
def check_row_correctness(red_mask, green_mask, blue_mask, row_rectangles, frame):
    red_detected = is_color_detected(red_mask, row_rectangles[0])  # Red in the first square
    green_detected = is_color_detected(green_mask, row_rectangles[1])  # Green in the second square
    blue_detected = is_color_detected(blue_mask, row_rectangles[2])  # Blue in the third square

    if red_detected:
        add_detection_text(frame, row_rectangles[0], "Red Detected")
    if green_detected:
        add_detection_text(frame, row_rectangles[1], "Green Detected")
    if blue_detected:
        add_detection_text(frame, row_rectangles[2], "Blue Detected")

    return red_detected and green_detected and blue_detected

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

    # Draw the 3x3 grid of hollow colored squares and get their positions
    rectangles = draw_color_grid(imageFrame)

    # For each row, restrict masks to their respective color rectangle
    row_1_correct = check_row_correctness(
        apply_mask_to_rectangle(red_mask, rectangles[0][0]),
        apply_mask_to_rectangle(green_mask, rectangles[0][1]),
        apply_mask_to_rectangle(blue_mask, rectangles[0][2]),
        rectangles[0],
        imageFrame
    )
    row_2_correct = check_row_correctness(
        apply_mask_to_rectangle(red_mask, rectangles[1][0]),
        apply_mask_to_rectangle(green_mask, rectangles[1][1]),
        apply_mask_to_rectangle(blue_mask, rectangles[1][2]),
        rectangles[1],
        imageFrame
    )
    row_3_correct = check_row_correctness(
        apply_mask_to_rectangle(red_mask, rectangles[2][0]),
        apply_mask_to_rectangle(green_mask, rectangles[2][1]),
        apply_mask_to_rectangle(blue_mask, rectangles[2][2]),
        rectangles[2],
        imageFrame
    )

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
