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

port_string = "T4:SN440017833"  # replace with your port string, find e.g. in SweepMe! using the driver

labjack = pysweepme.get_driver(driver_name, driver_path, port_string)

print("Labjack driver instance:", labjack)

labjack.connect()  # semantic function to make sure we can communication with the labjack device

print("Device infos:", labjack.get_infos())

analog_pins = ["AIN0", "AIN1"]

for i in range(100):
    print(i, labjack.read_pins(pin_names=analog_pins, auto_switch_to_input=True))
    time.sleep(0.1)

labjack.disconnect()