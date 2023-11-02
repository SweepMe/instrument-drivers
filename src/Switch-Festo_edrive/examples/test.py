"""
Please use the source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path, the driver name, and the port string
"""

import pysweepme  # use "pip install pysweepme" in command line to install
import os
import time

# create a driver instance using 'get_driver' with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::15::INSTR"

# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))

port_string = "192.168.0.1"  # replace with your port string, find e.g. in SweepMe! using the driver

stage = pysweepme.get_driver(driver_name, driver_path, port_string)

print("Festo edrive driver instance:", stage)

stage.connect()  # semantic function to make sure we can communication with the stage device
stage.initialize()  # semantic function to enable powerstage and reference move

# stage.edrive is a MotionHandler object created by the festo-edcon library that we access here
for i in range(0, 100000, 20000):
    stage.edrive.position_task(i, 1000, absolute=True, nonblocking=True)
    if not stage.edrive.target_position_reached():
        stage.edrive.wait_for_target_position()
    print("Current position:", stage.edrive.current_position())
    
stage.edrive.stop_motion_task()

stage.deinitialize()  # semantic function to shutdown powerstage and move back to 0
stage.disconnect()  # semantic function to shutdown Modbus communication