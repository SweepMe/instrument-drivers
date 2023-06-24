"""
Please use the source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path.
"""

import pysweepme  # use "pip install pysweepme" in command line to install
import os

# create a driver instance using 'get_driver' with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::15::INSTR"

# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  

# port_string = "GPIB0::1::INSTR"
port_string = "GPIB3::6::INSTR"

uf = pysweepme.get_driver(driver_name, driver_path, port_string)

uf.connect()  # needed to create an AccretechProber instance inside the driver instance

# Info
# uf is a Device instance of a SweepMe! driver
# uf.prober is an AccretechProber instance that encapsulates all handling with the prober

uf.print_info()  # prints out general static information

uf.print_status() # prints out the current system status

""" The following command can be used to load the control map i.e. a list of dies to probe
Only dies in state "PROB" will be returned """
# dies_to_probe = uf.read_controlmap("test.MDF")  # please enter a path to your control map MDF file
# print("Control map with PROB dies:", dies_to_probe)

""" The following commands are commented and should be uncommented step by step """

# Alarm message and alarm tone
# uf.prober.set_alarm("THIS IS A TEST")

# Reset alarm
# uf.prober.reset_alarm()

# Wafer sensing "jw" command
# uf.prober.sense_wafers()

# Load specified wafer
# uf.prober.load_specified_wafer(1,2)  # first cassette, first wafer

# Move to specified die
# uf.prober.move_specified_die(135,133)  # die at index x = 0, y = 0

# Chuck up
# uf.prober.z_up()

# Chuck down
# uf.prober.z_down()

# Unload wafer by terminating lot process
# uf.prober.terminate_lot_process_immediately()
