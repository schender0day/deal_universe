import cv2
import numpy as np
import pyautogui
import tkinter as tk
from PIL import ImageGrab

# Create tkinter root
root = tk.Tk()

# Hide the main window
root.withdraw()

# Create a full screen overlay root for the screen selection
overlay = tk.Toplevel(root)
overlay.attributes('-fullscreen', True)
overlay.attributes('-alpha', 0.3)
overlay.attributes('-topmost', True)

# Draw a canvas for user interaction
canvas = tk.Canvas(overlay)
canvas.pack(fill="both", expand=True)

# Use this to store screen selection coordinates
start_x, start_y, end_x, end_y = 0, 0, 0, 0

# Mouse button click event
def on_mouse_down(event):
    global start_x, start_y
    start_x = event.x
    start_y = event.y

# Mouse movement event
def on_mouse_move(event):
    global start_x, start_y, canvas
    canvas.delete("selection")
    canvas.create_rectangle(start_x, start_y, event.x, event.y,
                            outline='red', tags="selection")

# Mouse button release event
def on_mouse_up(event):
    global end_x, end_y
    end_x = event.x
    end_y = event.y
    overlay.destroy()

# Bind the events
canvas.bind("<Button-1>", on_mouse_down)
canvas.bind("<B1-Motion>", on_mouse_move)
canvas.bind("<ButtonRelease-1>", on_mouse_up)

# Start the application's main loop
root.mainloop()

# Set the recording area
recording_area = (min(start_x, end_x), min(start_y, end_y), abs(end_x - start_x), abs(end_y - start_y))

# Define the codec using VideoWriter_fourcc and create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 8.0, (recording_area[2], recording_area[3]))

# Start capturing the screen
while True:
    # Capture screen using PyAutoGUI
    img = ImageGrab.grab(bbox=(recording_area))
    # Convert the image into numpy array representation
    frame = np.array(img)
    # Write the RGB image to file
    out.write(frame)
    # Display screen/frame being recorded
    cv2.imshow('Screen Recorder', frame)
    # Wait for the user to press 'q' key to stop the
