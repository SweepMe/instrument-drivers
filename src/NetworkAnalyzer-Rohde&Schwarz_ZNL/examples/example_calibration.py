"""
Example calibration of ZNL network analyser with pysweepMe

Please use the source code of the driver to find all functions and their docstrings.
To use this example in your own project, you need to modify the driver path.
"""

import os

import pysweepme  # use "pip install pysweepme" in command line to install

""" connect to device """
# the name of the driver where this example file is in
driver_name = os.path.dirname(os.path.dirname(
    (os.path.abspath(__file__)))).split(os.sep)[-1]

# the path of the driver where this example file is in
driver_path = os.path.dirname(
    (os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))

# user settings
port_str = 'GPIB3::20::INSTR'
VNA_ports = [1, 2]
single_port_calibration_standards = ["OPEN", "SHORT", "MATCH"]

znl = pysweepme.get_driver(driver_name, driver_path, port_str)

identification = znl.port.get_identification()
print("Connection check, ZNL identification:", identification)

# ZNL setup
znl.set_trigger_continuous()
znl.set_sweep_mode("CONT")
znl.set_output_enabled(True)


# turn display on
print("...turn display on...")
znl.set_display_update(True)
print("error? ---> %s" % znl.get_error())

# select cal kit
print("...select calibration kit...")
# calibration_kit = "Z67-X-GSG-100"  # NEEDS TO BE CHANGED TO THE ONE OF YOUR PROBES
calibration_kit = "85032F"  # NEEDS TO BE CHANGED TO THE ONE OF YOUR PROBES
znl.port.write(":SENSE:CORRECTION:CKIT:N50:SELECT '%s'" % calibration_kit)
print("error? ---> %s" % znl.get_error())

# select port connectors
print("...select port connectors...")
for port in VNA_ports:
    znl.port.write(":SENSE1:CORRECTION:COLLECT:CONNECTION%i N50MALE" % port)
    print("port %i: error? ---> %s" % (port, znl.get_error()))

# select calibration method
print("...select calibration method...")
znl.port.write(
    ":SENSe1:CORRection:COLLect:METHod:DEFine 'test_cal_tosm_12', TOSM, 1, 2")
print("error? ---> %s" % znl.get_error())

# measure single port standards OPEN, SHORT, MATCH
for port in VNA_ports:
    for standard in single_port_calibration_standards:
        input("...land probes on standard %s... and then press ENTER" %
              standard)
        znl.port.write(":SENSe1:CORRection:COLLect:ACQuire:SELected %s, %i" %
                       (standard, port))
        print("port %i: error? ---> %s" % (port, znl.get_error()))

# measure THROUGH standard
input('...land probes on standard "THROUGH" ... and then press ENTER')
# @Tester : 1,2 hard coded --> VNA_ports
znl.port.write(":SENSe1:CORRection:COLLect:ACQuire:SELected THROUGH, 1, 2")
print("error? ---> %s" % znl.get_error())

# apply calibration
znl.apply_calibration()
print("error? ---> %s" % znl.get_error())

# store calibration
znl.port.write(
    ":MMEMORY:STORE:CORRection 1, 'TOSM12.cal'"
)  # QUESTION: What is the meaning of 1 after CORRection
print("error? ---> %s" % znl.get_error())

znl.set_output_enabled(False)

# Keysight:      SOLT = Short, Open, Load,  Thru
# Rohde&Schwarz: TOSM = Thru,  Open, Short, Match

# OPEN: contacted, Structure is not connected -> Contact characterization
# SHORT: contacted, Structure is connected -> Contact resistance
# MATCH/LOAD: contacted, Structure with defined interconnect of 50 Ohm.
# THROUGH: contacted, Signal contacts are connected and all grounds are connected.
