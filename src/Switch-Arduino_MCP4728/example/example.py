import time

import pysweepme

driver_name = "Switch-Arduino_MCP4728"
driver_path = r"path_to\instrument-drivers\src"  # Path to the instrument-driver repository
port_string = "COM1"  # You can get the COM Port from Arduino IDE or SweepMe

# Initialize Driver
mcp = pysweepme.get_driver(driver_name, driver_path, port_string)

# Set measurement parameter
mcp.set_parameters(
    {
        "Channel": "all",
        "I2C Address": "0,1,2,3",
        "SweepMode": "Voltage in V",
        "Voltage reference": "External",
        "External voltage in V": 5.0,
    },
)

# Initialize Device
mcp.connect()
mcp.configure()

# Set output values as colon-divided string
values = "0.15:0.25:0.35:0.45:1.19:1.29:1.39:1.49:2.19:2.29:2.39:2.49:3.19:3.29:3.39:3.49"
mcp.set_value(values)
mcp.apply()

# optional wait
time.sleep(5)

# Disconnect and unconfigure at the end to set voltages back to 0
mcp.unconfigure()
mcp.disconnect()
