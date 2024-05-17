import tkinter as tk
from tkinter import ttk
from pydualsense import pydualsense
import threading
import time  # Import the time module

def update_pressure():
    """Update the pressure level of the progress bar based on the R2 trigger pressure."""
    while True:
        r2_pressure = dualsense.state.R2  # Get the current pressure level of R2
        progress_bar['value'] = r2_pressure  # Update the progress bar with the current pressure
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

# Configure the progress bar
progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='determinate', maximum=255)
progress_bar.pack(pady=20)

# Start the thread for updating the pressure
thread = threading.Thread(target=update_pressure)
thread.daemon = True
thread.start()

# Set the closing protocol
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI loop
root.mainloop()
