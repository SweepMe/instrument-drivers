import os

import pysweepme

# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

port_string = "OPM150 - 12345"

logger = pysweepme.get_driver(driver_name, driver_path, port_string)

print(logger.find_ports()) # Print available devices

logger.connect()

logger.initialize()

print(logger._units) # Print units to choose from

logger.set_parameters({
    "Unit": "Microwatts (µW)",
    "Wavelength in nm": "660",
    "Gain": "x1",
    "Filter factor": "1"
})

logger.configure()

print(logger.opm_get_measurement())

logger.disconnect()