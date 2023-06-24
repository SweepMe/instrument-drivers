"""
Please use the  source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path.
"""

import pysweepme  # use "pip install pysweepme" in command line to install
import os
import time

# create a driver instance using get_driver with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::15::INSTR"

driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  # the path of the driver where this example file is in, please change in your own project
port_string = "COM4"

la100 = pysweepme.get_driver(driver_name, driver_path, port_string)

la100.reset()

address = la100.get_address()
print("Address:", address)

version = la100.get_version()
print("Version:", version)

la100.set_diameter(20.0)

diameter = la100.get_diameter()
print("Diameter:", diameter)

la100.set_phase(1)
la100.set_rate(15.0, "MM")
la100.set_volume(1.0)
la100.set_pumping_direction("WDR")

phase = la100.get_phase()
print("Phase:", phase)

function = la100.get_phase_function()
print("Function:", function)

rate = la100.get_rate()
print("Rate:", rate)

volume = la100.get_volume()
print("Volume:", volume)

la100.set_pumping_direction("INF")

la100.clear_dispensed_volume()

la100.run_program()

la100.wait_for_program()

la100.set_pumping_direction("WDR")

la100.clear_dispensed_volume()

la100.run_program()

la100.wait_for_program()

la100.stop_program()