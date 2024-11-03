import pygame
import numpy as np
import cv2
from scipy import ndimage
import subprocess
import time

def ReLU(n):
    return np.maximum(0, n)

def softmax(L):
    A = np.exp(L) / sum(np.exp(L))
    return A

def read_matrix_from_file(filename):
    with open(filename, 'r') as file:
        rows, cols = map(int, file.readline().split())
        matrix = np.zeros((rows, cols), dtype=float)
        for i in range(rows):
            row_elements = list(map(float, file.readline().split()))
            matrix[i, :] = row_elements
    return matrix

def preprocess_image(gray):
    if np.sum(gray) == 0:
        print('empty matrix')
        return gray
    
    while gray.shape[0] > 0 and np.sum(gray[0]) == 0:
        gray = gray[1:]
    while gray.shape[1] > 0 and np.sum(gray[:, 0]) == 0:
        gray = np.delete(gray, 0, 1)
    while gray.shape[0] > 0 and np.sum(gray[-1]) == 0:
        gray = gray[:-1]
    while gray.shape[1] > 0 and np.sum(gray[:, -1]) == 0:
        gray = np.delete(gray, -1, 1)
    
    if gray.size == 0:
        raise ValueError("The input image is empty after trimming black rows and columns.")
    
    rows, cols = gray.shape

    if rows > cols:
        factor = 20.0 / rows
        rows = 20
        cols = int(round(cols * factor))
        gray = cv2.resize(gray, (cols, rows))
    else:
        factor = 20.0 / cols
        cols = 20
        rows = int(round(rows * factor))
        gray = cv2.resize(gray, (cols, rows))
    
    colsPadding = (int(np.ceil((28 - cols) / 2.0)), int(np.floor((28 - cols) / 2.0)))
    rowsPadding = (int(np.ceil((28 - rows) / 2.0)), int(np.floor((28 - rows) / 2.0)))
    gray = np.lib.pad(gray, (rowsPadding, colsPadding), 'constant')

    if gray.shape != (28, 28):
        raise ValueError("The padded image is not 28x28.")
    
    shiftx, shifty = getBestShift(gray)
    gray = shift(gray, shiftx, shifty)

    return gray

def getBestShift(img):
    cy, cx = np.array(ndimage.center_of_mass(img))
    rows, cols = img.shape
    shiftx = np.round(cols / 2.0 - cx).astype(int)
    shifty = np.round(rows / 2.0 - cy).astype(int)
    return shiftx, shifty

def shift(img, sx, sy):
    M = np.float32([[1, 0, sx], [0, 1, sy]])
    shifted = cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))
    return shifted

# Function to switch focus to a window using xdotool
def focus_window(window_id):
    try:
        subprocess.run(["xdotool", "windowactivate", window_id])
        print("Focused on window:", window_id)
    except Exception as e:
        print("Error focusing window:", e)

# Get the ID of the currently focused window
def get_current_window_id():
    try:
        result = subprocess.run(["xdotool", "getactivewindow"], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print("Error getting active window ID:", e)
        return None

# Set the size of the window and the matrix
window_size = 448
matrix_size = 28
scaling_factor = window_size // matrix_size  # Scaling factor for better visualization

# Read weight and bias matrices from files
w1 = read_matrix_from_file("w1new.txt")
w2 = read_matrix_from_file("w2new.txt")
w3 = read_matrix_from_file("w3new.txt")
b1 = read_matrix_from_file("b1new.txt")
b2 = read_matrix_from_file("b2new.txt")
b3 = read_matrix_from_file("b3new.txt")

# Initialize Pygame
pygame.init()

# Create the window
window = pygame.display.set_mode((window_size, window_size))
pygame.display.set_caption("Mouse Input Example")

# Create a 28x28 matrix to store mouse input
matrix = np.zeros((matrix_size, matrix_size), dtype=float)

# Main loop
running = True
drawing = False
erase_mode = False  # Initialize erase mode
pygame_window_id = None  # To store the Pygame window ID
other_window_id = None  # To store the ID of any other active window

# Set background color to black
background_color = (0, 0, 0)

# Text input variables
out = 0
font = pygame.font.Font(None, 36)
text_color = (255, 255, 255)

# Store the Pygame window ID
pygame_window_id = str(pygame.display.get_wm_info()['window'])  # Get the Pygame window ID
while running:
    # Continuously check the current window ID
    current_window_id = get_current_window_id()

    # Update other_window_id if the active window is not Pygame
    if current_window_id != pygame_window_id:
        other_window_id = current_window_id

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Check for mouse input
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button for drawing
                drawing = True
                erase_mode = False  # Ensure erase mode is off
            elif event.button == 3:  # Right mouse button for erasing
                drawing = True
                erase_mode = True

        elif event.type == pygame.MOUSEBUTTONUP:
            drawing = False
            if event.button == 3:  # Reset erase_mode only for the right mouse button
                erase_mode = False
            blurred_matrix = preprocess_image(matrix.copy())
            X = np.reshape(blurred_matrix, (784, 1))

            z1 = w1.dot(X) + b1
            hl1 = ReLU(z1)
            z2 = w2.dot(hl1) + b2
            hl2 = ReLU(z2)
            z3 = w3.dot(hl2) + b3
            Y = softmax(z3)

            out = np.argmax(Y)
            
            print("\nThe guessed digit:", out, 'accuracy:', Y[out] * 100)
            print()

            if other_window_id is not None:
                focus_window(other_window_id)  # Focus back to the other active window
            time.sleep(0.1)
            # Write to /dev/digit_key_driver
            try:
                with open("/dev/digit_key_driver", "w") as device_file:
                    device_file.write(str(out))
                print("Written to /dev/digit_key_driver:", out)
            except IOError as e:
                print("Error writing to /dev/digit_key_driver:", e)
            
            # Clear the matrix for the next input
            matrix = np.zeros((matrix_size, matrix_size), dtype=float)
            blurred_matrix = np.zeros((matrix_size, matrix_size), dtype=float)
            print("Matrix Cleared")
            time.sleep(0.1)
            focus_window(pygame_window_id)
                
        elif event.type == pygame.MOUSEMOTION and drawing:
            mouse_pos = pygame.mouse.get_pos()

            if 0 <= mouse_pos[0] < window_size and 0 <= mouse_pos[1] < window_size:
                matrix_x = mouse_pos[0] * matrix_size // window_size
                matrix_y = mouse_pos[1] * matrix_size // window_size

                if erase_mode:
                    matrix[matrix_y, matrix_x] = 0
                else:
                    matrix[matrix_y, matrix_x] = 1

    window.fill(background_color)

    blurred_matrix = cv2.GaussianBlur(matrix.astype(float), (5, 5), 0)
    blurred_matrix = np.minimum(blurred_matrix * 3, 1)

    def printmat():
        for i in range(matrix_size):
            for j in range(matrix_size):
                if blurred_matrix[i, j] > 0.2:
                    grey_value = int(blurred_matrix[i, j] * 255)
                    pygame.draw.rect(window, (grey_value, grey_value, grey_value),
                                     (j * scaling_factor, i * scaling_factor,
                                      scaling_factor, scaling_factor))
                else:
                    blurred_matrix[i][j] = 0

    printmat()
    pygame.display.flip()

# Quit Pygame
pygame.quit()

