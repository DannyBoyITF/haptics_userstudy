import tkinter as tk
from tkinter import ttk
from pydualsense import pydualsense
import threading
import time

def update_pressure():
    """Update the pressure level of the progress bar based on the R2 trigger pressure."""
    while True:
        r2_pressure = dualsense.state.R2  # Get the current pressure level of R2
        progress_bar['value'] = r2_pressure  # Update the progress bar with the current pressure

        # Change color of the progress bar and control rumble based on pressure value
        if r2_pressure < 127.5 or r2_pressure > 204:  # Less than 50% or more than 80%
            progress_bar['style'] = 'red.Horizontal.TProgressbar'
            dualsense.setLeftMotor(255)  # Max strength for left motor
            dualsense.setRightMotor(100)  # Moderate strength for right motor
        else:
            progress_bar['style'] = 'green.Horizontal.TProgressbar'
            dualsense.setLeftMotor(0)  # Turn off left motor
            dualsense.setRightMotor(0)  # Turn off right motor

        root.update_idletasks()  # Update the GUI
        time.sleep(0.05)  # Update interval

def on_closing():
    """Handle the window closing event."""
    dualsense.close()  # Properly close the controller connection
    root.destroy()  # Destroy the root window

# Setup DualSense controller
dualsense = pydualsense()
dualsense.init()

# Setup the GUI
root = tk.Tk()
root.title("R2 Trigger Pressure")

# Create style for progress bar
style = ttk.Style(root)
style.theme_use('clam')  # Use the 'clam' theme for more styling options

# Define custom styles for the progress bar
style.configure('green.Horizontal.TProgressbar', troughcolor='black', background='green')
style.configure('red.Horizontal.TProgressbar', troughcolor='black', background='red')

# Configure the progress bar
progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate', maximum=255, style='green.Horizontal.TProgressbar')
progress_bar.pack(pady=20)

# Start the thread for updating the pressure
thread = threading.Thread(target=update_pressure)
thread.daemon = True
thread.start()

# Set the closing protocol
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI loop
root.mainloop()
