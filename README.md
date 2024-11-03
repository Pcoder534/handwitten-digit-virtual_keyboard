# Handwritten Digit Virtual Keyboard

This project creates a virtual keyboard that allows users to input handwritten digits (0-9) directly into any text editor. You can draw a digit on a grid, and a neural network will recognize it, sending the result to a custom device driver. The driver then simulates the corresponding keypress, inputting the digit wherever your text cursor is placed.

## Setup and Installation

To set up and run the project, open the project directory in the terminal and follow these steps:

1. **Install Required Libraries**:
   ```bash
   sudo apt install -y python3 python3-pygame python3-numpy python3-opencv python3-scipy
2. **Compile the Device Driver**: Use `make` to compile the custom device driver.
   ```bash
   make
3. **Load the Device Driver**: Insert the compiled module into the kernel.
   ```bash
   sudo insmod digit_key_driver.ko
4. **Set Device Permissions**: Allow all users to access the driver.
   ```bash
   sudo chmod 666 /dev/digit_key_driver  
5. **Run the Python Input Script**: Start the main script to open the drawing grid for digit input.
    ```bash
   python3 input.py
   
## Usage Instructions

1. **Open a Text Editor**: Place the text cursor where you want the digit input to appear.
2. **Draw a Digit**: In the drawing window, draw a digit by holding and moving the left mouse button. Release to recognize the digit.
3. **Input in Text Editor**: Once recognized, the digit is automatically entered at the cursor position, and the grid resets for new input.

## Unload the Driver

To remove the driver when done, use the command to unload the module from the kernel.
```bash
sudo rmmod digit_key_driver
