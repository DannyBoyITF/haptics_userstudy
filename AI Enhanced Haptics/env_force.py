import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from pydualsense import *
import threading
import numpy as np
import time
import pygame  # Import pygame for sound handling

# Initialize pygame for sound playback
pygame.init()
pygame.mixer.init()
rumble_sound = pygame.mixer.Sound("rumble.wav")  # Load your rumble sound file

def start_application():
    start_frame.pack_forget()  # Hide the start screen
    main_frame.pack(fill=tk.BOTH, expand=True)  # Show the main application frame
    thread.start()  # Start the thread that manages pressure updates and motor control

def update_gauge(psi_value):
    global counter
    needle.set_data([0, np.cos(np.radians(psi_value / 10000 * 180 - 90))], [0, np.sin(np.radians(psi_value / 10000 * 180 - 90))])
    canvas.draw_idle()

    if 7000 <= psi_value <= 7500:
        status_label.config(text=f"Good - Holding for {counter} seconds", fg="green")
        counter += 1
    else:
        status_label.config(text="Bad", fg="red")
        counter = 0

    if counter >= 15:
        root.destroy()

def update_pressure():
    sound_playing = False
    while True:
        r2_pressure = dualsense.state.R2
        psi_value = np.interp(r2_pressure, [0, 255], [0, 10000])
        update_gauge(psi_value)
        trigger_force_value = int(np.interp(psi_value, [0, 10000], [0, 255]))
        dualsense.triggerR.setMode(TriggerModes.Rigid)
        

        if psi_value < 7000 or psi_value > 7500:
            # dualsense.setLeftMotor(255)  # Start motor rumbling
            # dualsense.setRightMotor(100)
            dualsense.triggerR.setForce(1, trigger_force_value)
            # if not sound_playing:
            #     rumble_sound.play(-1)  # Play the rumble sound continuously
            #     sound_playing = True
            # # Set trigger force to maximum when motors are rumbling
            
        else:
            #dualsense.triggerR.setForce(1, 0)
            dualsense.setLeftMotor(0)  # Stop motor rumbling
            dualsense.setRightMotor(0)
            # if sound_playing:
            #     rumble_sound.stop()  # Stop the sound when motors are off
            #     sound_playing = False
            # Reset the trigger force settings when motors are not rumbling

        time.sleep(0.1)


def on_closing():
    pygame.quit()  # Quit pygame when closing the application
    dualsense.close()
    root.destroy()

# Setup DualSense controller
dualsense = pydualsense()
dualsense.init()

root = tk.Tk()
root.title("Pressure Gauge Simulator")

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
ax.set_aspect('equal', 'box')

circle = plt.Circle((0, 0), 1, edgecolor='black', facecolor='none', lw=2)
ax.add_artist(circle)
ax.axis('off')

for label in range(0, 11000, 1000):
    angle = np.radians(label / 10000 * 180 - 90)
    ax.text(np.cos(angle) * 1.1, np.sin(angle) * 1.1, str(label), horizontalalignment='center', verticalalignment='center')

canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack(fill=tk.BOTH, expand=True)

status_label = tk.Label(main_frame, text="Good", fg="green", font=("Helvetica", 16))
status_label.pack(pady=20)

# Thread initialization without starting
thread = threading.Thread(target=update_pressure)
thread.daemon = True

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
