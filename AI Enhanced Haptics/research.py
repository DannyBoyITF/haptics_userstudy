import tkinter as tk
from tkinter import ttk
import subprocess

def run_script(script_name):
    """Run the specified Python script."""
    subprocess.run(["python", script_name], check=True)
    root.deiconify()  # Bring the GUI back after script execution

def launch(script_name):
    """Hide the main window and run the chosen script."""
    root.withdraw()  # Hide the main window
    root.after(100, run_script, script_name)  # Delay needed to let the GUI close

# Set up the main window
root = tk.Tk()
root.title("Python Script Launcher")

# Configure the grid layout
root.columnconfigure(0, weight=1)

# Create buttons for each script
script_names = [
    "force_config1.py", "force_config2.py", 
    "visuals_config1.py", "visuals_config2.py", 
    "vibration_config1.py", "vibration_config2.py", 
    "sound_config1.py", "sound_config2.py"
]
for idx, script_name in enumerate(script_names):
    ttk.Button(root, text=script_name[:-3], command=lambda name=script_name: launch(name)).grid(row=idx, column=0, sticky="ew", padx=5, pady=5)

# Start the GUI
root.mainloop()
