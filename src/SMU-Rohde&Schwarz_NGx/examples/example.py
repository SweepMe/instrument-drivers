"""
Please use the source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path.
"""

import pysweepme  # use "pip install pysweepme" in command line to install
import os

# create a driver instance using 'get_driver' with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::15::INSTR"

# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  

port_string = "GPIB0::1::INSTR"

ngx = pysweepme.get_driver(driver_name, driver_path, port_string)

ngx.set_channel(1)
ngx.set_voltage(0.1)
ngx.set_output_on()
ngx.set_generation_on()

print("Voltage applied")

voltage, current = ngx.read_data()
print("Voltge:", voltage, "Current:", current)

ngx.set_generation_off()
ngx.set_output_off()