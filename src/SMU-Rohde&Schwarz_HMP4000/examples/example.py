"""Example: control a Rohde & Schwarz HMP power supply with pysweepme.

Please use the source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path.
"""

import os

import pysweepme  # use "pip install pysweepme" in command line to install

# create a driver instance using 'get_driver' with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "TCPIP0::192.168.150.40::5025::SOCKET"

# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

port_string = "TCPIP0::192.168.150.40::5025::SOCKET"

hmp = pysweepme.get_driver(driver_name, driver_path, port_string)
hmp.set_parameters({"Port": port_string, "Channel": 1, "SweepMode": "Voltage in V", "Compliance": 0.1})
hmp.connect()  # sets the socket terminators
hmp.initialize()  # reads the model from *IDN?, so that only existing channels are accepted

print(hmp.get_identification())

channel = 1
hmp.set_current(channel, 0.1)  # current limit in A
hmp.set_voltage(channel, 1.0)  # voltage in V
hmp.set_output(channel, True)  # arms the channel and switches the general output on

print("Voltage setpoint:", hmp.get_voltage_setpoint(channel), "V")
print("Measured voltage:", hmp.get_voltage(channel), "V")
print("Measured current:", hmp.get_current(channel), "A")

hmp.set_output(channel, False)  # disarms the channel; the other channels stay as they are
hmp.unlock_local_interface()
hmp.disconnect()
