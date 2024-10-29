import numpy as np
import cv2
import serial, time

# Conexión al puerto serial
arduino = serial.Serial('COM8', 9600, timeout=1)
time.sleep(2)  # Espera para que se establezca la conexión
print("se ejecuto correctamente")

# Capturing video through webcam
webcam = cv2.VideoCapture(0)

# Variables globales para el arrastre
dragging = False
selected_rect = None
offset_x = 0
offset_y = 0

# Dimensiones de los rectángulos
rect_width = 0
rect_height = 0
rectangles = []

# Expected colors for each square in a row (9 colors)
expected_colors = ["Red", "Green", "Blue", "Yellow", "Cyan", "Magenta", "Purple", "Orange", "Teal"]

# Define color ranges for each expected color
color_ranges = {
    "Red": (np.array([136, 87, 111], np.uint8), np.array([180, 255, 255], np.uint8)),
    "Green": (np.array([25, 52, 72], np.uint8), np.array([102, 255, 255], np.uint8)),
    "Blue": (np.array([94, 80, 2], np.uint8), np.array([120, 255, 255], np.uint8)),
    "Yellow": (np.array([22, 93, 0], np.uint8), np.array([45, 255, 255], np.uint8)),
    "Cyan": (np.array([78, 158, 124], np.uint8), np.array([99, 255, 255], np.uint8)),
    "Magenta": (np.array([125, 60, 60], np.uint8), np.array([150, 255, 255], np.uint8)),
    "Purple": (np.array([129, 50, 70], np.uint8), np.array([158, 255, 255], np.uint8)),
    "Orange": (np.array([5, 50, 50], np.uint8), np.array([15, 255, 255], np.uint8)),
    "Teal": (np.array([85, 50, 50], np.uint8), np.array([95, 255, 255], np.uint8))
}

# Function to initialize the grid of rectangles
def initialize_grid_positions(frame):
    global rect_width, rect_height, rectangles

    height, width, _ = frame.shape
    rect_width = min(width, height) // 10
    rect_height = rect_width * 2  # Double the height

    padding_x = (width - (9 * rect_width)) // 10
    padding_y = (height - (3 * rect_height)) // 4

    rectangles.clear()
    colors = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), 
              (255, 255, 0), (255, 0, 255), (128, 0, 128), (255, 165, 0), (0, 128, 128)]
    
    for row in range(3):
        row_positions = []
        for col in range(9):
            x = padding_x + col * (rect_width + padding_x)
            y = padding_y + row * (rect_height + padding_y)
            row_positions.append([x, y, x + rect_width, y + rect_height, colors[col % len(colors)]])
        rectangles.append(row_positions)

# Function to draw the rectangles on the frame
def draw_color_grid(frame):
    for row_rectangles in rectangles:
        for rect in row_rectangles:
            color = rect[4]
            cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), color, 2)

# Function to check if a point is inside a rectangle
def point_in_rectangle(x, y, rect):
    return rect[0] <= x <= rect[2] and rect[1] <= y <= rect[3]

# Mouse callback function to handle dragging
def mouse_callback(event, x, y, flags, param):
    global dragging, selected_rect, offset_x, offset_y

    if event == cv2.EVENT_LBUTTONDOWN:
        for row_index, row_rectangles in enumerate(rectangles):
            for col_index, rect in enumerate(row_rectangles):
                if point_in_rectangle(x, y, rect):
                    dragging = True
                    selected_rect = (row_index, col_index)
                    offset_x = x - rect[0]
                    offset_y = y - rect[1]
                    return

    elif event == cv2.EVENT_MOUSEMOVE:
        if dragging and selected_rect is not None:
            row_index, col_index = selected_rect
            rect = rectangles[row_index][col_index]
            rect[0] = x - offset_x
            rect[1] = y - offset_y
            rect[2] = rect[0] + rect_width
            rect[3] = rect[1] + rect_height

    elif event == cv2.EVENT_LBUTTONUP:
        dragging = False
        selected_rect = None

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

# Function to add detection text inside rectangles with short labels
def add_detection_text(frame, rectangle, label):
    x1, y1, x2, y2 = rectangle
    text_position = (x1 + 10, y1 + (y2 - y1) // 2)
    cv2.putText(frame, label, text_position, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

# Main loop
cv2.namedWindow("Multiple Color Detection in Real-Time")
cv2.setMouseCallback("Multiple Color Detection in Real-Time", mouse_callback)

while True:
    # Read frame from webcam
    _, imageFrame = webcam.read()

    # Initialize the grid positions only once
    if not rectangles:
        initialize_grid_positions(imageFrame)

    # Convert the imageFrame from BGR to HSV color space
    hsvFrame = cv2.cvtColor(imageFrame, cv2.COLOR_BGR2HSV)

    # Draw the grid based on current positions
    draw_color_grid(imageFrame)

    # Initialize flag for all rows being correct
    all_rows_correct = True

    # Check each row for the correct colors
    for row_index, row_rectangles in enumerate(rectangles):
        row_correct = True  # Flag to track if current row is correct

        for col_index, rectangle in enumerate(row_rectangles):
            color_name = expected_colors[col_index]
            color_range = color_ranges[color_name]
            mask = cv2.inRange(hsvFrame, color_range[0], color_range[1])
            mask = apply_mask_to_rectangle(mask, rectangle[:4])

            # Check if the correct color is detected for the rectangle
            if is_color_detected(mask, rectangle[:4]):
                label = f"C{col_index + 1}"  # Short label format
                add_detection_text(imageFrame, rectangle[:4], label)
            else:
                row_correct = False  # Mark row as incorrect if any color is missing

        # If row is correct, print row number
        if row_correct:
            print(f"Fila {row_index + 1} correcta")
            
            
        all_rows_correct &= row_correct  # Update all_rows_correct flag

    # If all rows are correct, print "si"
    if all_rows_correct:
        print("todas correctas pancho")
        arduino.write(b'5')
    # Check for input "deyverson" from terminal
    user_input = input("Escribe un comando: ")
    if user_input.lower() == "deyverson":
        arduino.write(b'5')

    # Show the image with the grid and detection texts
    cv2.imshow("Multiple Color Detection in Real-Time", imageFrame)

    # Exit on pressing 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        webcam.release()
        cv2.destroyAllWindows()
        break
