# @file __init__.py
# @author Markus Führer
# @date 7 Jan 2022
# @copyright Copyright © 2022 by Bentham Instruments Ltd. 

"""Simple control package for Bentham Instruments SCPI-controllable 
devices

This package provides a "Device" class, and a "list_connected_devices" 
function.

Instantiating the Device class connects to the target device, which can then
be controlled with the instance's .write, .read, and .query commands, for 
example:

>>> myDevice = bendev.Device(serial_number="99999/9")
>>> print(myDevice.query("MEAS:CURRENT?"))
"5.402"

A query consists of a write followed by a read.

Which devices are connected can be discovered using the 
list_connected_devices function, which filters the available devices by 
product name or manufacturer and returns a list of device descriptor 
dictionaries.

For more information see:
    help(bendev.device)
"""

from bendev.device import Device, list_connected_devices
