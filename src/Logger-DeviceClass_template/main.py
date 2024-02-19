# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# SweepMe! device class
# * Type: Logger
# * Device: Template


### !!! Change the above license to your case and needs. !!!
### Although the above MIT license states that you have to add it to copies,
### we do not insist in that. Please feel free to not add the MIT license of this file.

### Each device class must have a name like: "<Module>-<Manufacturer>_<Model>".


### New drivers can also be created as a service.
### Please write to "contact@sweep-me.net" if you need a new driver of if you need support with creating one.


### import further python module here as usual, many packages come with SweepMe!,
### all other have to be shipped with the device class
import pathlib
import random

### If you like to see the source code of EmptyDevice, take a look at the pysweepme package that contains this file
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug, error

### use the next two lines to add the folder of this device class to the PATH variable
# from FolderManager import addFolderToPATH
# addFolderToPATH()
### if you use 'addFolderToPATH', you can now important packages that are shipped with your device class


class Device(EmptyDevice):
    ### here you can add html formatted description to your device class
    ### that is shown by modules like 'Logger' or 'Switch' that have a description field.
    description = """
                    <h3>Template for a Logger Device Class</h3>
                    <p>---Modify this description text later to guide your users---</p>
                    <p>This example shows:</p>
                    <ul>
                    <li>how to define variable and units</li>
                    <li>how to define plottype and savetype</li>
                    <li>all functions that can be used are called</li>
                    <li>how to create your own GUI</li>
                    <li>how to interact with the GUI by using using set_GUIparameter and get_GUIparameter</li>
                    <li>how to use the port manager or to create your own port objects</li>
                    <li>how to use html text to create this description, e.g. by using a free online html editor</li>
                    </ul>
                    <p>&nbsp;</p>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "Template"  # short name will be shown in the sequencer
        self.variables = ["Variable1", "Variable2", "Variable3", "Variable4"]  # define as many variables you need
        self.units = ["Unit1", "Unit2", "Unit3", "Unit4"]  # make sure that you have as many units as you have variables
        self.plottype = [True, True, False, False]  # True to plot data, corresponding to self.variables
        self.savetype = [True, False, True, False]  # True to save data, corresponding to self.variables

        ### use/uncomment the next line to use the port manager
        # self.port_manager = True

        ### use/uncomment the next line to let SweepMe! search for ports of types supported by your instrument
        ### Also works if self.port_manager is False or commented.
        # self.port_types = ["COM", "GPIB", "USB", "TCPIP"]

        ### use/uncomment the next lines to change port properties,
        ### you can find all keys here: https://wiki.sweep-me.net/wiki/Port_manager#Port_properties
        # self.port_properties = {
        #                           "timeout": 1,
        #                           "baudrate": 9600,
        #                           "EOL": '\n',
        #                         }

    def set_GUIparameter(self):
        # add keys and values to generate GUI elements in the Parameters-Box
        # If you use this template to create a driver for modules other than Logger or Switch,
        # you need to use fixed keys that are defined for each module.

        GUIparameter = {
            "String": "test",
            # Boolean creates a CheckBox
            "Check": True,
            # List of strings creates a ComboBox
            "Combo": ["Choice%i" % i for i in range(5)],
            # an empty line
            "": None,
            # a bold section label
            "Section": None,
            # an int creates a LineEdit which only accepts integers
            "Int": 0,
            # a float creates a LineEdit which only accepts floats including 'e' for exponent
            "Float": 1.1,
            # a Path-object of the pathlib module creates a button to open a QFileDialog
            "Data path": pathlib.Path(),
        }

        ### Caution:
        ### Make sure that you do not use special strings
        ### such as 'Port', 'Comment', 'Device', 'Data', 'Description', or 'Parameters'
        ### These strings have special meaning and should not be overwritten.

        return GUIparameter

    def get_GUIparameter(self, parameter):
        ### see all available keys you get from the GUI
        # debug(parameter)

        ### get a value of a GUI item that was created by set_GUIparameter()
        # debug(parameter["String"])
        # debug(parameter["Check"])
        # debug(parameter["Combo"])
        # debug(parameter["Int"])
        # debug(parameter["Float"])
        # debug(parameter["Data path"])

        ### the port selected by the user is readout here and saved in a variable
        ### that can be later used to open the correct port
        self.port_string = parameter["Port"]  # use this string to open the right port object later during 'connect'
        # debug("Selected port", self.port_string)

    def find_ports(self):
        """This function is called whenever the user presses 'Find ports' button.

        No need to use, if you search for ports using self.port_types in __init__
        Function can be removed if not needed.
        """
        debug("find_ports")

        ### if you do not use the port manager you can use this function
        ### to return a list of strings with possible port items

        ### the next lines are an example how to find ports yourself
        import pyvisa

        try:
            # if your dll is not found and you would like to try a different path use:
            # rm = visa.ResourceManager("C:\\Windows\\System32\\visa32.dll")
            rm = pyvisa.ResourceManager()

            debug("ResourceManager:", rm)

            resources = rm.list_resources()

            # lets inform the user if there is no port
            if len(resources) == 0:
                resources = ["No visa resources found!"]

            debug("Found resources:", resources)

            return resources

        except:
            error("Cannot load visa runtime")

            return ["Port1", "Port2"]

    ### --------------------------------------------------------------------------------------------
    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    ### all functions are overridden functions that are called by SweepMe!
    ### remove those function that you do not needed

    def connect(self):
        ### called only once at the start of the measurement
        ### this function 'connect' is typically not needed if the port manager is activated
        
        print()
        debug("->connect")

        ### if you do not use the port manager you can also create your own port objects
        # rm = visa.ResourceManager()
        # self.instrument = rm.open_resource(self.port_string)
        # debug("Instrument identification:", self.instrument.query('*IDN?'))

        ### of course you can use any other library to open your ports, e.g. pyserial
        ### just use 'find_Ports' to find all possible ports and then open them here
        ### based on the string 'self.port_string' that is created during 'get_GUIparameter'

    def disconnect(self):
        # called only once at the end of the measurement
        debug("->disconnect")

    def initialize(self):
        # called only once at the start of the measurement
        debug("->initialize")

        # debug("-> Tempfolder:", self.get_folder("TEMP"))  # the folder in which all data is saved before saving
        # debug("-> External libs:", self.get_folder("EXTLIBS"))  # the folder in which all data is saved before saving
        # debug("-> Custom files:", self.get_folder("CUSTOMFILES"))  # the folder in which all data is saved before saving
        # debug("-> Driver folder:", self.get_folder("SELF"))  # the folder where this file is in

        # In 'initialize' you can check whether the user input is valid.
        # If not you can abort the run by throwing an exception as shown in the lines below
        # msg = "Value of ... not valid. Please use ..."
        # raise Exception(msg)

    def deinitialize(self):
        # called only once at the end of the measurement
        debug("->deinitialize")

    def configure(self):
        # called if the measurement procedure enters a branch of the sequencer
        # and the module has not been used in the previous branch
        debug("->  configure")

    def unconfigure(self):
        # called if the measurement procedure leaves a branch of the sequencer
        # and the module is not used in the next branch
        debug("->  unconfigure")

    def signin(self):
        # called if the variation of the module that is loading this device class starts
        debug("->  signin")

    def signout(self):
        # called if the variation of the module that is loading this device class ends
        debug("->  signout")
        
    def reconfigure(self, parameters, keys):
        """'reconfigure' is called whenever parameters of the GUI change by using the {...}-parameter system."""
        debug("->  reconfigure")
        # debug("->  Parameters:", parameters)
        # debug("->  Changed keys:", keys)

        ### The following two lines are the default behavior that is used by EmptyDevice
        ### if you do not override 'reconfigure'
        # self.get_GUIparameter(parameters)
        # self.configure()
        
    def poweron(self):
        # called if the measurement procedure enters a branch of the sequencer
        # and the module has not been used in the previous branch
        debug("->  poweron")

    def poweroff(self):
        # called if the measurement procedure leaves a branch of the sequencer
        # and the module is not used in the next branch
        debug("->  poweroff")

    ###------------------------------------------------------------------
    """ the following functions are called for each measurement point """

    ### these functions can be used to organize the sequence of all instruments
    ### that are part of one branch of the sequencer
    ### each function is called for all devices and then the next function is processed
    ### remove functions that are not needed

    def start(self):
        """'start' can be used to do some first steps before the acquisition of a measurement point starts."""
        debug("->    start")

    def apply(self):
        """'apply' is used to set the new setvalue that is always available as 'self.value'."""
        # apply is not called in the module 'Logger' as logger cannot apply any value,
        # but it can be used in all other modules that have varying sweep values
        # apply is only called if the setvalue ("Sweep value") has changed
        debug("->    apply")

        # debug("->    New value to apply:", self.value)
        # self.value is a variable created by SweepMe! and stores the latest sweep value that should be applied
        # It can be any object. Please make sure to to test the type
        # and change it to the format you need before you send it to a device.

    def reach(self):
        """'reach' can be added to make sure the latest setvalue applied during 'apply' is reached."""
        # only called if 'apply' has been called beforehand
        debug("->    reach")

    def adapt(self):
        """'adapt' can be used to adapt an instrument to a new situation after other instruments got a new setvalue."""
        debug("->    adapt")

    def adapt_ready(self):
        """'adapt_ready' can be used to make sure that a procedure started in 'adapt' is finished.

        Thus, multiple instrument can start an adapt-procedure simultaneously.
        """
        debug("->    adapt_ready")

    def trigger_ready(self):
        debug("->    trigger_ready")

    def measure(self):
        """'measure' should be used to trigger the acquisition of new data.

        If all drivers use this function for this purpose, the data acquisition can start almost simultaneously.
        """
        debug("->    measure")

    def request_result(self):
        """'request_result' can be used to ask an instrument to send data."""
        debug("->    request_result")

    def read_result(self):
        """'read_result' can be used get the data from a buffer that was requested during 'request_result'."""
        debug("->    read_result")

    def process_data(self):
        """'process_data' can be used for some evaluation of the data before it is returned."""
        debug("->    process_data")

    def call(self):
        """'call' is a mandatory function that must be used to return as many values as defined in self.variables.

        This function can only be omitted if no variables are defined in self.variables.
        """
        # most import function:
        # return exactly the number of values that have been defined by self.variables and self.units
        debug("->    call")

        value1 = random.random()
        value2 = random.random() ** 2
        value3 = random.random() ** 3
        value4 = random.random() ** 4

        return [value1, value2, value3, value4]

    def finish(self):
        """'finish' can be used to do some final steps after the acquisition of a measurement point."""
        debug("->    finish")
