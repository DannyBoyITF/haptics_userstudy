import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from pydualsense import pydualsense, TriggerModes
import threading
import numpy as np
import time
from datetime import datetime, timedelta
import csv

start_time = None
end_time = None

# Initialize the DualSense controller
dualsense = pydualsense()
dualsense.init()
dualsense.triggerR.setMode(TriggerModes.Rigid)



# Tank settings
max_tank_capacity = 10000  # Maximum PSI the tank can hold
current_tank_fill = 0  # Current fill level of the primary tank
secondary_tank_fill = 0  # Current fill level of the secondary tank



def fill_tank(pressure):
    global current_tank_fill, secondary_tank_fill
    fill_increment = pressure * max_tank_capacity / 25555  # Proportional fill based on trigger pressure
    current_tank_fill += fill_increment
    current_tank_fill = min(current_tank_fill, max_tank_capacity)

    if current_tank_fill > 5000:
        secondary_increment = (pressure * current_tank_fill / 255) / 20  # Example rate: 10% of the overflow above 5000
        if pressure == 0:
            secondary_increment = 10
        secondary_tank_fill += secondary_increment
        secondary_tank_fill = min(secondary_tank_fill, max_tank_capacity)
    else:
        secondary_tank_fill = 0   # Reset secondary tank fill when primary is below threshold

    return current_tank_fill, secondary_tank_fill

def update_gauge(psi_value_primary, psi_value_secondary):
    needle.set_data([0, np.cos(np.radians(psi_value_primary / 10000 * 180 - 90))], [0, np.sin(np.radians(psi_value_primary / 10000 * 180 - 90))])
    canvas.draw_idle()

    primary_fill_percentage = (psi_value_primary / max_tank_capacity) * 100
    primary_progress_bar['value'] = primary_fill_percentage
    secondary_fill_percentage = (psi_value_secondary / max_tank_capacity) * 100
    secondary_progress_bar['value'] = secondary_fill_percentage
    secondary_percentage_label.config(text=f"{int(secondary_fill_percentage)}% Extended")

    status_text = f"Primary Tank Pressure: {int(psi_value_primary)} PSI"
    if psi_value_primary > 7000:
        status_label.config(text=f"Pressure Exceeded! {status_text}", fg="red")
    else:
        status_label.config(text=status_text, fg="green")

def start_application():
    global start_time
    start_frame.pack_forget()
    main_frame.pack(fill=tk.BOTH, expand=True)
    thread.start()
    start_time = datetime.now()  # Capture start time
    print(f"Simulation started at {start_time}")
thread_stop = threading.Event()

def update_pressure():
    while not thread_stop.is_set():
        trigger_pressure = dualsense.state.R2
        simulated_pressure_primary, simulated_pressure_secondary = fill_tank(trigger_pressure)
        update_gauge(simulated_pressure_primary, simulated_pressure_secondary)
        rumble_value = int(np.interp(simulated_pressure_primary, [0, 10000], [0, 255]))
        dualsense.setLeftMotor(rumble_value)  # Max strength for left motor
        dualsense.setRightMotor(rumble_value)  # Moderate strength for right motor
        time.sleep(0.1)

def cross_down(state):
    global last_press_time
    current_time = datetime.now()
    global end_time, current_tank_fill, secondary_tank_fill, max_tank_capacity
    if current_time - last_press_time > debounce_interval:
        end_time = datetime.now()  # Capture end time
        elapsed_time = end_time - start_time  # Calculate duration
        secondary_fill_percentage = (secondary_tank_fill / max_tank_capacity) * 100 if secondary_tank_fill > 0 else 0
        print(f"Cross button pressed. Ending simulation after {elapsed_time}.")
        write_time_to_csv(start_time, end_time, elapsed_time, current_tank_fill,secondary_fill_percentage)
        reset_simulation()
        last_press_time = current_time

def write_time_to_csv(start, end, elapsed, current_psi, secondary_percentage):
    filename = 'vibration_config2.csv'
    header = ['Start Time', 'End Time', 'Elapsed Time','End PSI', 'Extension %']
    data = [
        start.strftime('%Y-%m-%d %H:%M:%S'), 
        end.strftime('%Y-%m-%d %H:%M:%S'), 
        str(elapsed), 
        str(current_psi), 
        f"{secondary_percentage:.2f}%"
    ]
    try:
        # Check if file exists, if not, write header
        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:  # file.tell() returns the current position of file pointer
                writer.writerow(header)
            writer.writerow(data)
    except Exception as e:
        print(f"Failed to write to CSV: {e}")
def reset_simulation():
    global current_tank_fill, secondary_tank_fill, thread, thread_stop

    # Stop the thread safely
    if thread.is_alive():
        thread_stop.set()
        thread.join()

    # Reset the simulation state
    current_tank_fill = 0
    secondary_tank_fill = 0

    # Reset threading event and restart the thread
    thread_stop.clear()
    thread = threading.Thread(target=update_pressure)
    thread.daemon = True
    thread.start()
    


    # Reset UI components as previously described



def on_closing():
    try:
        if thread.is_alive():
            thread_stop.set()  # Signal the thread to stop
            if threading.current_thread() is not thread:
                thread.join()  # Only join if not in the same thread
    except NameError:
        pass  # Thread was not started
    # Safely close the DualSense controller
    if threading.current_thread() is not dualsense.report_thread:
        dualsense.close()
    else:
        # Optionally set a flag to close later or handle differently
        print("Avoid closing from within the same thread")

    if end_time is not None:
        print(f"Total elapsed time: {end_time - start_time}")
    
    primary_progress_window.destroy()
    secondary_progress_window.destroy()
    main_frame.destroy()
    root.destroy()


# Setup the GUI
root = tk.Tk()
root.title("Hydraulic Cylinder Simulation")

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

# Progress Bars in separate windows
primary_progress_window = tk.Toplevel(root)
primary_progress_window.title("Primary Tank Fill Level")
primary_progress_window.withdraw()  # Initially hide this window
primary_progress_bar = ttk.Progressbar(primary_progress_window, orient="horizontal", length=200, mode='determinate')
primary_progress_bar.pack(pady=20, padx=20)

secondary_progress_window = tk.Toplevel(root)
secondary_progress_window.title("Cylinder Extention Progress")
secondary_progress_bar = ttk.Progressbar(secondary_progress_window, orient="horizontal", length=200, mode='determinate')
secondary_progress_bar.pack(pady=20, padx=20)
secondary_percentage_label = tk.Label(secondary_progress_window, text="0% Extended", font=("Helvetica", 16))
secondary_percentage_label.pack(pady=10)

# Thread initialization without starting
thread = threading.Thread(target=update_pressure)
thread.daemon = True

dualsense.cross_pressed += cross_down
last_press_time = datetime.min
debounce_interval = timedelta(seconds=1) # 1 second between valid presses

root.protocol("WM_DELETE_WINDOW", on_closing)
primary_progress_window.protocol("WM_DELETE_WINDOW", on_closing)
secondary_progress_window.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
