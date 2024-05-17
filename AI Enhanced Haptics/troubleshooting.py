from pydualsense import *


def cross_down(state):
    print(f'cross {state}')


def circle_down(state):
    print(f'circle {state}')




# create dualsense
dualsense = pydualsense()
# find device and initialize
dualsense.init()

# add events handler functions
dualsense.cross_pressed += cross_down
dualsense.circle_pressed += circle_down


# read controller state until R1 is pressed
while not dualsense.state.R1:
    ...

# close device
dualsense.close()