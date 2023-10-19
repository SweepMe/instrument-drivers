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

port_string = "GPIB0::2::INSTR"

mb = pysweepme.get_driver(driver_name, driver_path, port_string)

identifier = mb.get_identification()
print("Identifier:", identifier)

mb.reset()
mb.open_all_channels()
mb.close_channel(["A1", "B2"])

closed_channels = mb.get_closed_channels()
print("Closed channels:", closed_channels)
