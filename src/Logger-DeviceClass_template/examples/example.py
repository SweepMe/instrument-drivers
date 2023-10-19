"""
This is a pysweepme example with the Logger_Device template. It shows how one can make an instance of a driver with
pysweepme, handing over the port string, and call functions of the driver.
Please use the source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path.
"""

import pysweepme  # use "pip install pysweepme" in command line to install
import os

# create a driver instance using 'get_driver' with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::15::INSTR", "COM1" or "USBTMC".

# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  

port_string = None  # not needed here, otherwise "COM1" or "GPIB0::1::INSTR")

logger = pysweepme.get_driver(driver_name, driver_path, port_string)

# This function is typically not needed when the port manager is used in the driver script. When the driver connects
# manually to the instrument, it is needed to establish the connection
logger.connect()

# The next lines call the SweepMe semantic standard functions keeping the sequence with which SweepMe calls them.
# Note that this is an example and all functions are not necessarily needed or included in an instrument driver.
logger.initialize()

logger.configure()

logger.poweron()

logger.start()

logger.value = 1
logger.apply()

logger.reach()

logger.measure()

logger.finish()

logger.poweroff()

logger.unconfigure()

logger.deinitialize()
