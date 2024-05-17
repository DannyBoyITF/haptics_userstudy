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
    needle.set_data([0, psi_value / 10000 * 180 - 90], [0, 1])  # Normalize and map psi_value to degrees
    canvas.draw_idle()

def update_pressure():
    """Update the gauge based on the R2 trigger pressure."""
    while True:
        r2_pressure = dualsense.state.R2  # Get the current pressure level of R2
        psi_value = np.interp(r2_pressure, [0, 255], [0, 10000])  # Map 0-255 to 0-10k PSI
        update_gauge(psi_value)

        if r2_pressure < 127.5 or r2_pressure > 204:
            dualsense.setLeftMotor(255)
            dualsense.setRightMotor(100)
        else:
            dualsense.setLeftMotor(0)
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
needle, = ax.plot([0, 0.5], [0, 1], color='red', lw=2)  # Initial needle position, adjusted size and origin
ax.set_aspect('equal', 'box')

# Create a circle for the gauge face
circle = plt.Circle((0, 0), 1, edgecolor='black', facecolor='none', lw=2)
ax.add_artist(circle)

# Remove plot frame and ticks
ax.axis('off')

# Embed the plot in the tkinter window
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

# Start the thread for updating the pressure
thread = threading.Thread(target=update_pressure)
thread.daemon = True
thread.start()

# Set the closing protocol
root.protocol("WM_DELETE_WINDOW", on_closing)

# Start the GUI loop
root.mainloop()
