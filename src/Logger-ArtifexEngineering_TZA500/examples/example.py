import os

import pysweepme

# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

port_string = "TZA500 - 12345"

logger = pysweepme.get_driver(driver_name, driver_path, port_string)

print(logger.find_ports()) # Print available devices

logger.connect()

logger.initialize()

print(logger._units) # Print units to choose from
print(logger.gain_steps.keys()) # Print gain levels to choose from
print(logger.bandwith_steps.keys()) # Print bandwiths to choose from

logger.set_parameters({
    "Unit": "Microwatts (µW)",
    "Gain": "x1",
    "Bandwith": "10 kHz",
    "Initial action": "Auto zero reset", # or Auto zero
    "Invert input polarity": False
})

logger.configure()

print(logger.tza_get_measurement())

logger.disconnect()