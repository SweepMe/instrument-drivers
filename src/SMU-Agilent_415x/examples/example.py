"""
Please use the  source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path.
"""

import pysweepme  # use "pip install pysweepme" in command line to install
import os

# create a driver instance using get_driver with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::15::INSTR"

driver_name = "SMU-Agilent_415x"
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  # the path of the driver where this example file is in, please change in your own project
port_string = "GPIB0::17::INSTR"

ag415x = pysweepme.get_driver(driver_name, driver_path, port_string)  

ag415x.reset()
        
ag415x.set_user_mode()
        
ag415x.clear_buffer()
        
ag415x.set_autozero(0)  # Auto-Zero off

ag415x.set_data_format(1,2)

# NPLC
ag415x.port.write("SLI 1")  # Fast

# Integration time
ag415x.port.write("SIT 3,320e-3")
ag415x.port.write("SIT 1,640e-6")

# Averages
ag415x.port.write("AV 1")

ag415x.set_measurement_mode(2, 1, 2, 3)  # Sweep measurement for channels 1, 2, and 3


channel = 2
listsweepmode = 1  # linear sweep
voltage_range = 0  # autorange
start = 0.0
end = 10
points = 11
compliance = 1e-3

ag415x.set_sweep_voltage(channel,
                       listsweepmode,
                       voltage_range, 
                       start, 
                       end, 
                       points, 
                       compliance,
                       )
                       
                       
channel = 1
voltage_range = 0  # autorange
start = 0.0
end = 0.0
compliance = 1e-3

ag415x.set_sweep_synchronous_voltage(channel,
                                   voltage_range, 
                                   start, 
                                   end, 
                                   compliance,
                                   )
                                   
channel = 3
voltage_range = 0  # autorange
start = 10.0
end = 10.0
compliance = 1e-3

ag415x.set_sweep_synchronous_voltage(channel,
                                   voltage_range, 
                                   start, 
                                   end, 
                                   compliance,
                                   )
                                   
ag415x.execute_measurement()

ag415x.port.write("*OPC?")
ag415x.port.read()


data_number = ag415x.get_number_data()
print("Number of points in buffer:", data_number)

reply = ag415x.read_measurement_data()
print("RMD? response:", reply)