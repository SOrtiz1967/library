import numpy as np
import cv2

# Inicializa la captura de video desde la cámara
webcam = cv2.VideoCapture(1)

# Variables globales
dragging = False
selected_rect = None
offset_x = 0
offset_y = 0

# Dimensiones de los rectángulos
rect_width = 0
rect_height = 0
rectangles = []

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

# Start a while loop
cv2.namedWindow("Multiple Color Detection in Real-Time")
cv2.setMouseCallback("Multiple Color Detection in Real-Time", mouse_callback)

# Main loop
while True:
    # Read frame from webcam
    _, imageFrame = webcam.read()

    # Initialize the grid positions only once
    if not rectangles:
        initialize_grid_positions(imageFrame)

    # Draw the grid based on current positions
    draw_color_grid(imageFrame)

    # Show the frame
    cv2.imshow("Multiple Color Detection in Real-Time", imageFrame)

    # Exit on pressing 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        webcam.release()
        cv2.destroyAllWindows()
        break
