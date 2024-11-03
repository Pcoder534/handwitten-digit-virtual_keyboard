Handwritten Digit Virtual Keyboard

This project is a virtual keyboard that enables users to input handwritten digits (0-9) into any text editor. Users can draw a digit on a grid, and a neural network recognizes the digit, which is then sent to a custom device driver. The device driver simulates the corresponding keystroke, and the digit is entered into the active text editor.
Setup and Installation

To set up and run the project, follow these steps:

    Clone the Repository and open a terminal in the project directory.

    Run the following commands to install dependencies, compile the driver, and set up the environment:

    bash

    # Install required Python libraries
    sudo apt install -y python3 python3-pygame python3-numpy python3-opencv python3-scipy

    # Compile the device driver
    make

    # Insert the device driver module
    sudo insmod digit_key_driver.ko

    # Set permissions for the device
    sudo chmod 666 /dev/digit_key_driver

    # Run the Python input script
    python3 input.py

Explanation of Setup Steps

    Install Dependencies: Installs the required Python libraries to run the drawing and digit recognition code.
    Compile the Driver: Compiles the custom Linux device driver for handling digit entry.
    Insert the Module: Loads the device driver module, enabling interaction with the virtual keyboard.
    Set Device Permissions: Allows non-root users to access the device.
    Run Input Script: Launches the application that displays the drawing grid for digit input.

Using the Virtual Keyboard

    Open a Text Editor: Start any text editor or application where you’d like to input the digits. Place the text cursor where you want the digits to appear.
    Draw a Digit: In the drawing window, use your mouse to draw a digit (0-9). Hold down the left mouse button to draw, and release it once you've completed the digit.
    Recognition and Input: When you release the mouse button, the application recognizes the digit using a neural network. The drawing grid will clear for new input, and the recognized digit will appear at the cursor location in your text editor.

Unloading the Driver Module

When you are finished using the virtual keyboard, you can remove the driver module with the following command:

bash

sudo rmmod digit_key_driver
