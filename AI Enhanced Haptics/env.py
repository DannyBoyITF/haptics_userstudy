import tkinter as tk
from pydualsense import *
import threading
import time

# function to handle controller inputs
def handle_controller():
    with pydualsense as ds:
        ds.init()
        ds.lightBar(0, 0, 0)  # turn off light bar initially
        while True:
            ds.update()
            trigger_right = ds.state.R2  # get right trigger value
            if trigger_right > 0:  # if the right trigger is pressed
                canvas.config(bg="green")  # change canvas to green
            else:
                canvas.config(bg="red")  # change canvas to red
            time.sleep(0.1)

# setup the GUI
root = tk.Tk()
root.title("DualSense Trigger Indicator")
canvas = tk.Canvas(root, width=100, height=100, bg='red')
canvas.pack()

# threading to handle controller input without freezing GUI
thread = threading.Thread(target=handle_controller)
thread.daemon = True
thread.start()

root.mainloop()
