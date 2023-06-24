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

# port_string = "GPIB0::6::INSTR"
port_string = "GPIB3::6::INSTR"

uf = pysweepme.get_driver(driver_name, driver_path, port_string)

uf.connect()  # needed to create an AccretechProber instance inside the driver instance

uf.print_info()  # prints out general static information

uf.print_status()  # prints out the current system status

stb = uf.prober.check_status_byte(100)  # command should trigger a status byte 100 for testing purposes
if stb == 100:
    print("Service request event and status byte communication successful!")
else:
    print("Unable to receive the correct status byte, expected 100, received %s" % str(stb))