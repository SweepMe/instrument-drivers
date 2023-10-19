"""
Please use the  source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path.
"""

import pysweepme  # use "pip install pysweepme" in command line to install
import os

# create a driver instance using get_driver with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::15::INSTR"
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  # the path of the driver where this example file is in, please change in your own project
port_string = "GPIB0::15::INSTR"
dg535 = pysweepme.get_driver("Signal-Stanford_DG535", driver_path, port_string)  

# resets the instrument to default values
dg535.clear_instrument()

# change the delay of channel A with respect to T0 
dg535.set_delay("A", "T0", 6e-12)

delay = dg535.get_delay("A")
print("Delay of A:", delay)

# change impedance of channel A to High-Z
dg535.set_impedance("A", 1)

# change output mode of channel A to TTL
dg535.set_output_mode("A", 0)

# change trigger rate to 1000 Hz
dg535.set_trigger_rate(0, 1000)

# change trigger mode to Internal
dg535.set_trigger_mode(0)

# change trigger mode to Single-Shot
dg535.set_trigger_mode(2)

# perform single trigger in Single-Shot mode
dg535.trigger_single()

