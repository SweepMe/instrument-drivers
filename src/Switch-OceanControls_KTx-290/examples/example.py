"""
SweepMe drivers can also be run directly or used in pure python codes through pysweepme. For this purpose a driver
contains two sets of functions, standard functions, which are called by SweepMe! iteratively and
convenience functions. Here is a simple example how to write your own script.
Please use the source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path.
"""

import pysweepme  # use "pip install pysweepme" in command line to install
import os

# create a driver instance using 'get_driver' with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "COM4"

# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  

# change to your COM port
port_string = "COM4"

# SweepMe drivers can also be run directly or used in pure python codes through pysweepme. For this purpose a driver
# contains two sets of functions, standard functions, which are called by SweepMe! iteratively and
# convenience functions. Here is a simple example of directly running the driver.

ktx = pysweepme.get_driver(driver_name, driver_path, port_string)
print(ktx)
print(ktx.reset())

# example for axis = 1
axis = 1
print(ktx.report_frequencies(axis))
ktx.relative_move(axis, 1000)
ktx.relative_move(axis, -1000)

ktx.save()  # save current set position to memory
