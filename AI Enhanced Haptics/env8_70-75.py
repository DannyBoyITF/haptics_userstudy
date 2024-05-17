import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib as mpl
from pydualsense import pydualsense
import threading
import numpy as np

def update_gauge(psi_value):
    """Update the gauge with the current PSI value."""
    needle.set_data([0, np.cos(np.radians(psi_value / 10000 * 180 - 90))], [0, np.sin(np.radians(psi_value / 10000 * 180 - 90))])
    canvas.draw_idle()

    # Update the status label based on the pressure range
    if 7000 <= psi_value <= 7500:
        status_label.config(text="Good", fg="green")
    else:
        status_label.config(text="Bad", fg="red")

def update_pressure():
    """Update the gauge based on the R2 trigger pressure."""
    while True:
        r2_pressure = dualsense.state.R2  # Get the current pressure level of R2
        psi_value = np.interp(r2_pressure, [0, 255], [0, 10000])  # Map 0-255 to 0-10k PSI

        # Update the gauge and check the pressure value
        update_gauge(psi_value)

        # Set motor rumble based on the PSI range
        if 7000 <= psi_value <= 7500:
            dualsense.setLeftMotor(255)  # Set left motor to maximum when within the desired range
            dualsense.setRightMotor(100)  # Set right motor to a moderate level
        else:
            dualsense.setLeftMotor(0)  # Turn off motors when outside the desired range
            dualsense.setRightMotor(0)

def on_closing():
    """Handle the window closing event."""
    dualsense.close()
    root.destroy()

# Setup DualSense controller
dualsense = pydualsense()
dualsense.init()

# Setup the GUI
root = tk.Tk()
root.title("R2 Trigger Pressure Gauge")

# Setup the matplotlib figure and axis
fig, ax = plt.subplots()
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
needle, = ax.plot([0, 0.5], [0, 1], color='red', lw=2)  # Initial needle position
ax.set_aspect('equal', 'box')

# Create a circle for the gauge face
circle = plt.Circle((0, 0), 1, edgecolor='black', facecolor='none', lw=2)
ax.add_artist(circle)

# Remove plot frame and ticks
ax.axis('off')

# Add gauge labels
for label in range(0, 11000, 1000):  # Labels from 0 to 10,000 PSI every 1000 PSI
    angle = np.radians(label / 10000 * 180 - 90)
    ax.text(np.cos(angle) * 1.1, np.sin(angle) * 1.1, str(label), horizontalalignment='center', verticalalignment='center')

# Embed the plot in the tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Add a status label to the GUI
status_label = tk.Label(root, text="Good", fg="green", font=("Helvetica", 16))
status_label.pack(pady=20)

# Start the thread for updating the pressure
thread = threading.Thread(target=update_pressure)
thread.daemon = True
thread.start()

# Set the closing protocol
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI loop
root.mainloop()
