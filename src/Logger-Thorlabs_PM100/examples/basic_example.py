import os
import pysweepme


# create a driver instance using 'get_driver' with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "COM4"

# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  

port_str = "USB0::0x1313::0x8078::PM003842::0::INSTR"

# creating a driver instance
pm100 = pysweepme.get_driver(driver_name, driver_path, port_str)

sensor_status = pm100.get_sensor_status()
print("Sensor status:", sensor_status)
pm100.set_correction_wavelength(500)
power = pm100.read_power()
# power_range = pm100.get_power_range()
# print(power_range)
print("Measured power: ", power)