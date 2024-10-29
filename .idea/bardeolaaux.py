import numpy as np
import cv2
import serial, time

# Conexión al puerto serial
arduino = serial.Serial('COM8', 9600, timeout=1)
time.sleep(1)  # Espera para que se establezca la conexión
print("se ejecutó correctamente")

# Captura de video
webcam = cv2.VideoCapture(1)

# Variables globales para el arrastre
dragging = False
selected_rect = None
offset_x = 0
offset_y = 0

# Dimensiones de los rectángulos
rect_width = 0
rect_height = 0
rectangles = []

# Colores y sus nombres
expected_colors = ["Rosa", "Celeste", "Fuego", "Bordo", "Verde Lima", "Verde Oscuro", "Azul", "Naranja", "Marrón"]

# Conversión de colores RGB a HSV
color_ranges = {
    "Rosa": (np.array([164, 92, 94], np.uint8), np.array([174, 110, 110], np.uint8)),
    "Celeste": (np.array([20, 178, 125], np.uint8), np.array([30, 238, 225], np.uint8)),
    "Fuego": (np.array([115, 167, 110], np.uint8), np.array([125, 247, 210], np.uint8)),
    "Bordo": (np.array([130, 127, 76], np.uint8), np.array([140, 207, 176], np.uint8)),
    "Verde Lima": (np.array([80, 118, 122], np.uint8), np.array([90, 188, 222], np.uint8)),
    "Verde Oscuro": (np.array([80, 77, 72], np.uint8), np.array([90, 187, 172], np.uint8)),
    "Azul": (np.array([105, 194, 69], np.uint8), np.array([115, 254, 169], np.uint8)),
    "Naranja": (np.array([15, 175, 152], np.uint8), np.array([25, 235, 202], np.uint8)),
    "Marrón": (np.array([110, 74, 84], np.uint8), np.array([120, 164, 184], np.uint8))
}

# Función para inicializar la cuadrícula de rectángulos
def initialize_grid_positions(frame):
    global rect_width, rect_height, rectangles

    height, width, _ = frame.shape
    rect_width = min(width, height) // 15
    rect_height = rect_width * 2  # Altura doble

    padding_x = (width - (9 * rect_width)) // 10
    padding_y = (height - (3 * rect_height)) // 4

    rectangles.clear()
    # Colores BGR para los recuadros
    colors = [(98, 98, 169), (29, 131, 187), (202, 84, 70), (158, 78, 101), 
              (134, 148, 72), (11, 107, 99), (4, 94, 169), (195, 134, 102), (95, 84, 104)]
    
    for row in range(3):
        row_positions = []
        for col in range(9):
            x = padding_x + col * (rect_width + padding_x)
            y = padding_y + row * (rect_height + padding_y)
            row_positions.append([x, y, x + rect_width, y + rect_height, colors[col % len(colors)]])
        rectangles.append(row_positions)

# Función para dibujar los rectángulos en el marco
def draw_color_grid(frame):
    for row_rectangles in rectangles:
        for rect in row_rectangles:
            color = rect[4]
            cv2.rectangle(frame, (rect[0], rect[1]), (rect[2], rect[3]), color, 2)

# Resto del código permanece igual...


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

    # Show the image with the grid and detection texts
    cv2.imshow("Multiple Color Detection in Real-Time", imageFrame)

    # Exit on pressing 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        webcam.release()
        cv2.destroyAllWindows()
        break
