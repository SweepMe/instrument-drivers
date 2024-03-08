import time
import pysweepme

driver_name = "Switch-MBRAUN_SCU101"
driver_path = r"C:\~\instrument-drivers\src"
port_string = "COM3"

# Initialize Driver
shutter = pysweepme.get_driver(driver_name, driver_path, port_string)

# Set measurement parameter
shutter.set_parameters(
    {
        "SweepMode": "State",
        "MB Address": "3",
        "Shutter Number": "1"
    },
)

shutter.connect()
shutter.initialize()
print('Initial State:', shutter.call())

shutter.set_value("open")
shutter.apply()
time.sleep(3)

shutter.measure()
print('New state: ', shutter.call())

shutter.disconnect()