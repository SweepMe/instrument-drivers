"""
Basic usage example for the Undalogic uSMU driver with pysweepme.

Please use the source code of the driver to find all functions and their docstrings.
To use this example in your own project, you may need to modify the driver path.
"""

import os
import pysweepme  # use "pip install pysweepme" in command line to install

# Automatically resolve the driver name and path from this example's location
driver_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split(os.sep)[-1]
driver_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# The uSMU appears as a USB virtual COM port, e.g. "COM3"
port_string = "COM3"

smu = pysweepme.get_driver(driver_name, driver_path, port_string)

# Verify connection
identity = smu.get_identification()
print(f"Connected to: {identity}")

# Configure the channel: 20 mA compliance, oversampling = 25
smu.set_current_limit(20.0)
smu.set_oversample_rate(25)

# Enable output and apply a voltage
smu.enable_output()
voltage, current = smu.set_voltage_and_measure(1.0)
print(f"V = {voltage:.6f} V, I = {current:.9f} A")

# Disable output
smu.disable_output()
