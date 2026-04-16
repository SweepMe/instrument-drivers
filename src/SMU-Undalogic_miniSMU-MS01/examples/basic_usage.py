"""
Basic usage example for the Undalogic miniSMU MS01 driver with pysweepme.

Please use the source code of the driver to find all functions and their docstrings.
To use this example in your own project, you may need to modify the driver path.
"""

import os
import pysweepme  # use "pip install pysweepme" in command line to install

# Automatically resolve the driver name and path from this example's location
driver_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split(os.sep)[-1]
driver_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# For USB: use the COM port, e.g. "COM3"
# For WiFi: use "TCPIP0::<ip>::3333::SOCKET", e.g. "TCPIP0::192.168.1.100::3333::SOCKET"
port_string = "COM3"

smu = pysweepme.get_driver(driver_name, driver_path, port_string)

# Verify connection
identity = smu.get_identification()
print(f"Connected to: {identity}")

# Set Channel 1 to FVMI mode (Force Voltage, Measure Current)
smu.set_voltage(1, 0.0)

# Enable output
smu._send_command("OUTP1 ON")

# Apply a voltage and measure
smu.set_voltage(1, 1.0)
voltage, current = smu.get_voltage_and_current(1)
print(f"V = {voltage:.6f} V, I = {current:.9f} A")

# Disable output
smu._send_command("OUTP1 OFF")
