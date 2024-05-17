import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from pydualsense import pydualsense
import threading
import numpy as np
import time

# Initialize the DualSense controller
dualsense = pydualsense()
dualsense.init()

# Tank settings
max_tank_capacity = 10000  # Maximum PSI the tank can hold
current_tank_fill = 0  # Current fill level of the tank

def fill_tank(pressure):
    global current_tank_fill
    fill_increment = pressure * max_tank_capacity / 25555  # Proportional fill based on trigger pressure
    current_tank_fill += fill_increment
    current_tank_fill = min(current_tank_fill, max_tank_capacity)  # Cap the fill at the tank's capacity
    return current_tank_fill

def reset_tank(event=None):
    global current_tank_fill
    current_tank_fill = 0  # Reset tank fill to zero
    update_gauge(0)  # Update the gauge to show zero pressure

def update_gauge(psi_value):
    needle.set_data([0, np.cos(np.radians(psi_value / 10000 * 180 - 90))], [0, np.sin(np.radians(psi_value / 10000 * 180 - 90))])
    canvas.draw_idle()
    status_label.config(text=f"Tank Pressure: {int(psi_value)} PSI", fg="green")

def start_application():
    start_frame.pack_forget()  # Hide the start screen
    main_frame.pack(fill=tk.BOTH, expand=True)  # Show the main application frame
    thread.start()  # Start the thread that manages pressure updates and motor control

def update_pressure():
    while True:
        trigger_pressure = dualsense.state.R2
        simulated_pressure = fill_tank(trigger_pressure)
        update_gauge(simulated_pressure)
        time.sleep(0.1)

def on_closing():
    dualsense.close()
    root.destroy()

# Setup the GUI
root = tk.Tk()
root.title("Tank Filling Simulation")

# Start Screen Setup
start_frame = tk.Frame(root)
start_frame.pack(fill=tk.BOTH, expand=True)
welcome_label = tk.Label(start_frame, text="Welcome to the Pressure Gauge Simulator", font=("Helvetica", 18))
welcome_label.pack(pady=20)
start_button = tk.Button(start_frame, text="Start", command=start_application, font=("Helvetica", 14))
start_button.pack(pady=10)

# Main Application Setup
main_frame = tk.Frame(root)
fig, ax = plt.subplots()
ax.set_xlim(-1.5, 1.5)
ax.set_ylim(-1.5, 1.5)
needle, = ax.plot([0, 0.5], [0, 1], color='red', lw=2)
circle = plt.Circle((0, 0), 1, edgecolor='black', facecolor='none', lw=2)
ax.add_artist(circle)
ax.axis('off')
canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)
status_label = tk.Label(main_frame, text="Tank Pressure: 0 PSI", fg="green", font=("Helvetica", 16))
status_label.pack(pady=20)

# Bind the Enter key to reset the tank
root.bind("<Return>", reset_tank)

# Thread initialization without starting
thread = threading.Thread(target=update_pressure)
thread.daemon = True

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
