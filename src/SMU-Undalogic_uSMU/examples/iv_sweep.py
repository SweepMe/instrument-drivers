"""
Software-driven I-V sweep example for the Undalogic uSMU driver with pysweepme.

The uSMU performs sweeps in software (one point at a time), so this example
simply loops over a linear voltage array and measures each point atomically.
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

# Sweep parameters
start_voltage = -1.0
end_voltage = 1.0
points = 21

# Build a linear voltage list without requiring numpy at import time
step = (end_voltage - start_voltage) / (points - 1) if points > 1 else 0.0
voltages = [start_voltage + i * step for i in range(points)]

# Configure the channel
smu.set_current_limit(0.02)   # 20 mA compliance, in amperes (SweepMe! convention)
smu.set_oversample_rate(25)

smu.enable_output()
try:
    print(f"\n{'Voltage (V)':>12}  {'Current (A)':>14}")
    print("-" * 28)
    for v in voltages:
        measured_v, measured_i = smu.set_voltage_and_measure(v)
        print(f"{measured_v:12.6f}  {measured_i:14.9f}")
finally:
    smu.disable_output()
