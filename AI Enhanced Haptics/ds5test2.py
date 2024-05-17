from pydualsense import *

# get dualsense instance
dualsense = pydualsense()
# initialize controller and connect
dualsense.init()

print('Trigger Effect demo started')

# set left and right rumble motors
dualsense.setLeftMotor(255)
dualsense.setRightMotor(100)

# set left l2 trigger to Rigid and set index 1 to force 255
dualsense.triggerL.setMode(TriggerModes.Rigid)
dualsense.triggerL.setForce(1, 255)

# set left r2 trigger to Rigid
dualsense.triggerR.setMode(TriggerModes.Pulse_A)
dualsense.triggerR.setForce(0, 200)
dualsense.triggerR.setForce(1, 255)
dualsense.triggerR.setForce(2, 175)

# loop until r1 is pressed to feel effect
while not dualsense.state.R1:
    ...

# terminate the thread for message and close the device
dualsense.close()