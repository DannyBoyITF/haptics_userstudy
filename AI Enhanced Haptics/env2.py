from pydualsense import pydualsense
import time

def main():
    # Create and initialize the DualSense controller
    dualsense = pydualsense()
    dualsense.init()

    print("Press CTRL+C to stop.")
    
    try:
        # Continuously read the state of the R2 trigger
        while True:
            # There's no need to manually update the state, assuming it's auto-updated
            r2_value = dualsense.state.R2  # Read the R2 trigger pressure level
            print(f"R2 Trigger Pressure: {r2_value}")  # Print the pressure level
            time.sleep(0.1)  # Sleep to limit the number of prints per second
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        # Properly close the controller connection
        dualsense.close()

if __name__ == "__main__":
    main()


