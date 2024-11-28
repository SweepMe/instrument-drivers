"""Created 2020/09

Author:                     Jahns_P
Version Number:             1
Date of last change:        2020/09/02
Requires:                   R&S NRT2, FW 1.10.17092001 or newer and adequate options
                            Installed VISA e.g. R&S Visa 5.12.x or newer

Description:    Initialization of the instrument and performing a standard measurement
                of forward and reflected power - simplyfied version


General Information:

Please allways check this example script for unsuitable setting that may
destroy your DUT befor connecting it to the instrument!
This example does not claim to be complete. All information has been
compiled with care. However errors can not be ruled out.
"""

# --> Import necessary packets
from time import sleep

import visa

# Define variables
resource = "TCPIP0::10.205.0.39::inst0::INSTR"  # VISA Resource String of the device


# Preparation of the communication (termination, etc...)
def comprep():
    rm = visa.ResourceManager()
    global NRT2
    NRT2 = rm.open_resource(resource)
    NRT2.timeout = 5 * 1000

    # Set the device's buffer to a defined state:
    NRT2.clear

    # Set the termination value (no need to set here when already
    # configured for specific device under
    # "Settings/Instruments/<instrumentname>/Attributes/term_chars")
    NRT2.write_termination = "\n"
    NRT2.read_termination = "\n"


# Close the VISA session
def close():
    NRT2.close()


# Perform a reset and wait for completion
def reset():
    NRT2.write("*RST")
    sleep(2)
    # Check for existing errors (should be 0 at this moment) by SYST:ERR?


# Prepare measurement
def prepmeas():
    # Define measurement frequency - 1GHz
    NRT2.write("SENS1:FREQ 1 GHz")
    # Set 1st and 2nd measurement function to
    # Forward Power, Reverse Power
    NRT2.write("CALC1:CHAN1:FEED1 'POW:FORW:AVER,POW:REV'")
    # Set power unit to dBm
    NRT2.write("UNIT1:POWER DBM")


# Perform measurement
def meas():
    # Initiate trigger event and wait for completion through errorcheck
    NRT2.write("TRIGGER:IMM")
    # Read the measurement data (two values in this case)
    data = NRT2.query("SENS1:DATA?")
    print(data)


##
##-------------------------
## Main Program begins here
##-------------------------
##

comprep()
reset()
prepmeas()
meas()
close()

print("I'm done")
