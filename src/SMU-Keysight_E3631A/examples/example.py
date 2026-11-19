"""
Please use the source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path.
"""

import pysweepme  # use "pip install pysweepme" in command line to install
import os

# create a driver instance using 'get_driver' with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::5::INSTR"

# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))

port_string = "GPIB0::5::INSTR"

supply = pysweepme.get_driver(driver_name, driver_path, port_string)

# every command acting on an output takes its channel; the driver selects the output when it changes
supply.set_current("+6V", 0.1)
supply.set_voltage("+6V", 1.5)

# TRACK25V switches tracking on: -25V follows +25V with the opposite sign
supply.set_current("TRACK25V", 0.05)
supply.set_voltage("TRACK25V", 12.0)

supply.set_output(True)  # all three outputs at once

print("+6V:", supply.get_voltage("+6V"), "V,", supply.get_current("+6V"), "A")
print("-25V:", supply.get_voltage("-25V"), "V")  # reading -25V leaves tracking on

supply.set_output(False)
supply.set_tracking(False)
