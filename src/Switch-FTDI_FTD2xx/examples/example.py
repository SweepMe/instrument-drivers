import pysweepme

driver_name = 'Switch-FTDI_FTD2xx'
driver_path = r'C:\Code\instrument-drivers\src'
port_string = b'FTDCYSHN' # insert your device serial number here

# Initialize Driver
switch = pysweepme.get_driver(driver_name, driver_path, port_string)

# Set measurement parameter
switch.set_parameters({"Encoding": "HEX"})

# Initialize Device
switch.find_ports() # print to see available port_strings
switch.connect()
switch.configure()

switch.set_value("01 00 00 00 02")
switch.apply()

switch.disconnect()