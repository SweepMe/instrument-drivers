import pysweepme
import time

driver_name = 'Switch-FTDI_FTD2xx'
driver_path = r'C:\Code\instrument-drivers\src'
port_string = b'FTBHYRHM' # 'USB'

# Initialize Driver
switch = pysweepme.get_driver(driver_name, driver_path, port_string)

# Set measurement parameter
switch.set_parameters(
    {
        "Encoding": "HEX",
    },
)

# print(type(port_string))
serial = b'FTBHYRHM'
id = 67330049

# Initialize Device
switch.find_ports()
switch.connect()
switch.configure()

switch.set_value("01 00 00 00 02")
switch.apply()

switch.disconnect()