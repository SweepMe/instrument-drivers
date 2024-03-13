import pysweepme

driver_name = "Logger-PREVAC_TMC13"
driver_path = r"C:\Code\instrument-drivers\src"
port_string = "COM3"

# Initialize Driver
tmcontrol = pysweepme.get_driver(driver_name, driver_path, port_string)

# Set measurement parameter
tmcontrol.set_parameters(
    {
        "Channel": "1",  # Currently not used
        "Reset thickness": False,
        "Set Tooling": False,
        "Tooling in %": "100.0",
        "Set Density": False,
        "Density in g/cm^3": "1.3",
        "Set Acoustic Impedance": False,
        "Acoustic impedance in 1e5 g/cm²/s": 1.0,
    },
)

tmcontrol.connect()

# print('Get material density')
# tmcontrol.get_material_density()

tmcontrol.initialize()
tmcontrol.configure()

print("Getting Pressure")
pressure = tmcontrol.get_pressure()
print("Pressure: ", repr(pressure))

# values = tmcontrol.call()
#
# for n in range(3):
#     print(tmcontrol.variables[n], values[n], tmcontrol.units[n])

#
# # print(tmcontrol.find_ports())
