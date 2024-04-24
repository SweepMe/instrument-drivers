import pysweepme

driver_name = "Switch-PREVAC_TMC13-Shutter"
driver_path = r"C:\Code\instrument-drivers\src"
port_string = "COM3"  # Change this to the correct port

# Initialize Driver
shutter = pysweepme.get_driver(driver_name, driver_path, port_string)

# Set measurement parameter
shutter.set_parameters(
    {
        "SweepMode": "State",
        "Shutter number": "1",
        "State at start": "Closed",
        "State at end": "Closed",
    },
)

shutter.connect()
shutter.configure()

print("Opening shutter")
shutter.value = "Open"
shutter.apply()

shutter.measure()
print(f"New state: {shutter.call()}")

shutter.unconfigure()