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

pm100 = pysweepme.get_driver(driver_name, driver_path, port_str)
pm100._target_wavelength = 601.1
pm100._num_averages = 1

# sweepme standard calls https://wiki.sweep-me.net/wiki/Sequencer_procedure
pm100.initialize()
pm100.configure()
pm100.measure()
print("results", pm100.call())
# pm100.unconfigure()
pm100.disconnect()
