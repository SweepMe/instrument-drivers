"""Created 2020/09

Author:                     Jahns_P
Version Number:             1
Date of last change:        2020/09/02
Requires:                   R&S NRT2, FW 1.10.17092001 or newer and adequate options
                            Installed VISA e.g. R&S Visa 5.12.x or newer

Description:    Initialization of the instrument and performing a standard measurement
                of forward and reflected power


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
x = 1  # For counters
y = 1  # For counters also
loopResponse = "1"  # Variable for diverse loop requests
Response = "0"  # Variable for diverse requests
global tracetime  # Example for a global variable
tracetime = 0.05  # Predefine tracetime in s


# Define additional variables if needed


## Define subroutines for error and command completion requests
def errorcheck():  # combines esrcheck and system error check
    esrcheck()
    systerr()


# esrcheck is a loop for detection of command completion
# If it's used, it's important to reset the ESR before using *CLS and build
# a command chain like "*IDN?;*OPC". If *OPC will be used separately,
# it will set Bit 0 of the ESR correlating to itself. The command before
# is only factored in when building a command chain.
# --> See ESR-examples in the other sub routines.
def esrcheck():
    loopResponse = 0
    x = 1
    while loopResponse != "1":
        Request = NRT2.query("*ESR?")
        loopdec = int(Request)
        loopbin = bin(loopdec)
        binlen = len(loopbin)
        loopResponse = loopbin[binlen - 1]
        # display counter just to show if loop counts up for longer time
        print("loopResponse is now " + loopResponse)
        if x == 1000:
            print("Warning: Maximal number of requests reached--> command not watched or incomplete!")
            loopResponse = "1"
        x = x + 1
        sleep(0.1)


# systerr checks for all known system errors at the device.
# The error memory contains all last errors meaning that you have
# to query SYST:ERR? as long as you get no error returned.
def systerr():
    loopResponse = "1"
    x = 1
    while loopResponse != "0":
        Request = NRT2.query("SYST:ERR?")
        print(Request)
        loopResponse = Request[:1]


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


# Check communication
def comcheck():
    # Just knock on the door to see if instrument is present
    idnResponse = NRT2.query("*IDN?")
    sleep(1)
    # Check for existing errors (should be 0 at this moment) by SYST:ERR?
    systerr()
    loopResponse = "1"
    print("Hello, I am " + idnResponse)


# Perform a reset and wait for completion
def reset():
    NRT2.write("*RST")
    sleep(2)
    # Check for existing errors (should be 0 at this moment) by SYST:ERR?
    systerr()


# Prepare measurement
def prepmeas():
    # Define measurement frequency - 1GHz
    NRT2.write("*CLS")
    NRT2.write("SENS1:FREQ 1 GHz;*OPC")
    esrcheck()
    # Set 1st and 2nd measurement function to
    # Forward Power, Reverse Power
    NRT2.write("*CLS")
    NRT2.write("CALC1:CHAN1:FEED1 'POW:FORW:AVER,POW:REV';*OPC")
    esrcheck()
    # Set power unit to dBm
    NRT2.write("*CLS")
    NRT2.write("UNIT1:POWER DBM;*OPC")
    errorcheck()


# Perform measurement
def meas():
    # Initiate trigger event and wait for completion through errorcheck
    NRT2.write("*CLS")
    NRT2.write("TRIGGER:IMM;*OPC")
    errorcheck()
    # Read the measurement data (two values in this case)
    data = NRT2.query("SENS1:DATA?;*OPC")
    print(data)


##
##-------------------------
## Main Program begins here
##-------------------------
##

comprep()
comcheck()
reset()
prepmeas()
meas()

close()

print("I'm done")
