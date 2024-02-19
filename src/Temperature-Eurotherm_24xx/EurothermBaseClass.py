# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 - 2023 SweepMe! (sweep-me.net)
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
# Type: Temperature
# Device: Eurotherm BaseClass

from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

# shipped with libs folder for SweepMe! 1.5.5
# shipped with SweepMe! 1.5.6
import minimalmodbus

import time
import serial

from pysweepme.ErrorMessage import error, debug
from pysweepme.EmptyDeviceClass import EmptyDevice


class Eurotherm(EmptyDevice):

    """
    This driver is a base class for all Eurotherm drivers. Most registers are similar and in case they differ, they can be overwritten in the specific driver.

    The Eurotherm controller can have different ramp rate units while the module could also have different ramp rate units.
    To handle this, all conversion will be done via seconds.
    The user defined value is converted to temperature unit / s and then back to the unit of the instrument.
    A value of the instrument is converted to temperature unit / s and then back to the unit of the user.
    Therefore, two variables self.ramprate_conversion_instr und self.ramprate_conversion_user are defined which define
    the factor between the instrument or user unit to seconds.
    """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Eurotherm"
        
        self.port_types = ["COM"]

        # EI-Bisync default: 1 Start / 7 Data / Even parity / 1 Stop Bit / 9600
        self.default_port_properties_EI_Bisync = {
                                                     "timeout"  : 0.15,
                                                     "baudrate" : 9600,
                                                     "parity"   : "E",  # Even is default for EI-Bisync
                                                     "bytesize" : 7,
                                                     "stopbits" : 1,
                                                    }
                                                    
        # Modbus default: 1 Start / 8 Data / No Parity / 1 Stop Bit / 9600
        self.default_port_properties_Modbus = {
                                                     "timeout"  : 1,
                                                     "baudrate" : 9600,  # Default is 9600
                                                     "parity"   : "N",  # None,Even,Odd -> Default is None
                                                     "bytesize" : 8,
                                                     "stopbits" : 1,
                                                    }
                
        # Registers
        self.registers = {
                        # "<Name>" : (<Modbus  register>, <has digits>, <EI-Bisync mnemonic>)
                        
                        "Baudrate": (12548, 0, "h4"),  # Modbus only
                        "Parity": (12549, 0, "h5"),  # Modbus only
                        "Resolution": (12550, 0, "h6"),  # Modbus only
                        "DecimalPointPosition": (525, 0, "QD"),  # Modbus only needed, but can be called with EI-Bisync as well
                        
                        "LaFunc": (12355, 0, "k3"),
                        "LbFunc": (12419, 0, "l3"),
                        "ControlType": (512, 0, "Q0"),
                        "ControlAction": (7, 0, "CA"),
                        "PowerFeedbackEnable": (565, 0, "Pe"),
                        "ManualAutoTransferPDcontrol": (555, 0, "QQ"),

                        "Display": (106, 0, "WC"),
                        
                        "ProcessValue1": (1, 1, "PV"),
                        "ProcessValue2": (1 + 4*256, 1, "PV"),
                        
                        "SetPoint1": (2, 1, "SL"),
                        "SetPoint2": (2 + 4*256, 1, "SL"),
                        
                        "RemoteSetPoint1": (26, 1, "R1"),
                        "RemoteSetPoint2": (26 + 4*256, 1, "R1"),  # should be used if Temperature is changed very often.
                        
                        "LocalRemoteSetpointSelect1": (256+20, 0, "rE"),  # must be activated to use RemoteSetPoint1
                        "LocalRemoteSetpointSelect2": (256+20 + 4*256, 0, "rE"),
                        
                        # "MinimumSetPoint1": (),
                        # "MaximumSetPoint1": (),
                        
                        # "MinimumSetPoint2": (),
                        # "MaximumSetPoint2": (),
                        
                        "ManualOutput1": (3, 1, "OP"),
                        "ManualOutput2": (3 + 4*256, 1, "OP"),
                        
                        "WorkingOutput1": (4, 1, "WO"),
                        "WorkingOutput2": (4 + 4*256, 1, "WO"),
                        
                        "WorkingSetPoint1": (5, 1, "SP"),  # read-only
                        "WorkingSetPoint2": (5 + 4*256, 1, "SP"),  # read-only

                        "AutoTune1": (256+14, 0, "AT"),
                        "AutoTune2": (256+14 + 4*256, 0, "AT"),
                        
                        "ManualMode1": (256+17, 0, "mA"),
                        "ManualMode2": (256+17 + 4*256, 0, "mA"),

                        "SetPointRampRate1": (35, 1, "RR"),
                        "SetPointRampRate2": (35 + 4*256, 1, "RR"),
                                                
                        "ValvePosition": (53, 0, "VP"),
                        
                        "Pb1":  (6, 0, "XP"),
                        "ti1":  (8, 0, "TI"),
                        "td1":  (9, 0, "TD"),

                        "Pb2":  (6 + 4*256, 0, "XP"),
                        "ti2":  (8 + 4*256, 0, "TI"),
                        "td2":  (9 + 4*256, 0, "TD"),
                        
                        "CutBackLow1":  (17, 0, "LB"),
                        "CutBackHigh1": (18, 0, "HB"),
                        
                        "CutBackLow2":  (17 + 4*256, 0, "LB"),
                        "CutBackHigh2": (18 + 4*256, 0, "HB"),
                        
                        "OutputHigh1": (30, 1, "HO"),
                        "OutputLow1":  (31, 1, "LO"),
                        
                        "OutputHigh2": (30 + 4*256, 1, "HO"),
                        "OutputLow2":  (31 + 4*256, 1, "LO"),
                        
                        "SetpointHighLimit1": (111, 1, "HS"),
                        "SetpointLowLimit1":  (112, 1, "LS"),
                        
                        "SetpointHighLimit2": (111 + 4*256, 1, "HS"),
                        "SetpointLowLimit2":  (112 + 4*256, 1, "LS"),
                        
                        "Addr": (131, 0, "Ad"),
                        
                        "RampUnit": (8192 + 2, 0, "d0"),  # Program General Data register, maybe only 2400 series
            }

        self.channels_available = ["1"]
          
        self.STX = chr(0x02)  # STX Start of data in a message
        self.ETX = chr(0x03)  # ETX End of message
        self.EOT = chr(0x04)  # EOT End of transmission sequence
        self.ENQ = chr(0x05)  # ENQ Enquiry for a value
        self.ACK = chr(0x06)  # ACK Positive Acknowledge
        self.NAK = chr(0x15)  # NAK Negative Acknowledge
        
        self._digits = 0
    
    def set_GUIparameter(self):
        gui_parameter = {
                        # "Channel": ["Address %i" % (i+1) for i in range(247)], # Slave id of Modbus communication
                        
                        "SweepMode": ["Temperature", "Output in %", "None"],
                        "Channel": self.channels_available,
                        "TemperatureUnit": ["°C", "K", "°F"],
                        "ZeroPowerAfterSweep": True,
                        "Rate": "",  # empty means 'as is'
                        "OutputMax": "",  # empty means 'as is'
                        "IdleTemperature": "",
                        }
                        
        return gui_parameter
                                 
    def get_GUIparameter(self, parameter={}):

        self.channel = parameter["Channel"]
        self.sweepmode = parameter["SweepMode"]
        self.temperature_unit = parameter["TemperatureUnit"]
        
        if "Rate" in parameter:
            self.rate = parameter["Rate"]
        else: 
            self.rate = ""  # this will lead to doing nothing during 'configure'
            
        if "OutputMax" in parameter:
            self.output_max = parameter["OutputMax"]
        else:
            self.output_max = ""  # this will lead to doing nothing during 'configure'

        if "IdleTemperature" in parameter:
            self.idle_temperature = parameter["IdleTemperature"]
        else:
            self.idle_temperature = None
            debug("To support all functions of the Eurotherm driver, "
                  "please update to the latest version of the Temperature module.")

        self.variables = ["Temperature", "Output"]
        self.units = [self.temperature_unit, "%"]
        self.plottype = [True, True]
        self.savetype = [True, True]

        self.zeroOutputaftersweep = parameter["ZeroPowerAfterSweep"]

        self.port_string = parameter["Port"]
        
        # Check which communication is selected ##
        if ":" in self.port_string:
            self.port_string_splitted = self.port_string.split(":")
                        
        else:
            self.port_string_splitted = self.port_string, ""
            
        self.com_port, self.address = self.port_string_splitted

        self.rampunit_conversion_user = 60.0  # conversion from min to s

    def connect(self):

        self.comm_type = None
    
        if not self.com_port.startswith("COM"):
            self.stop_Measurement("Please select a valid COM port.")
            return False
        
        if self.address != "":
            
            if self.address.startswith("EI"):  # EI-Bisync
                        
                if not self.address[2:].isdigit():
                    self.stop_Measurement("Please add the Modbus address to the COM port "
                                          "using the following syntax 'COM1:{address}', "
                                          "e.g. 'COM1:3'. In case of EI-Bisync protocol use"
                                          " 'COM1:EI{address}', e.g 'COM1:EI3'.")
                    return False
            
                self.retries = 0
                address = "%02d" % int(self.address[2:])
                self.GID = address[0]
                self.UID = address[1]
                self.CHAN = self.channel if len(self.channels_available) > 1 else ""
                self.comm_type = "EI-Bisync"
                
                self.port = serial.Serial()
                self.port.port = self.com_port
                # self.port = serial.rs485.RS485(self.com_port)  # maybe needed to change the write method of pyserial for RS-485

                if self.port.isOpen():
                    self.port.close()
                
                self.port.open()
                               
                for key in self.default_port_properties_EI_Bisync:
                    if key not in self.port_properties:
                        self.port_properties[key] = self.default_port_properties_EI_Bisync[key]
                                        
                self.port.timeout = self.port_properties["timeout"]
                self.port.baudrate = self.port_properties["baudrate"]
                self.port.parity = self.port_properties["parity"]
                self.port.bytesize = self.port_properties["bytesize"]
                self.port.stopbits = self.port_properties["stopbits"]

                # once, added for testing purposes, might be helpful if something does not work
                # please uncomment "import serial.rs485" at the top of the file if you like to use it
                # self.port.rs485_mode = serial.rs485.RS485Settings(
                                                                    # rts_level_for_tx=True,
                                                                    # rts_level_for_rx=False,
                                                                    # loopback=False,
                                                                    # delay_before_tx=None,
                                                                    # delay_before_rx=None
                                                                    # )

                self.port.reset_input_buffer()
                self.port.reset_output_buffer()

            else:  # Modbus
                if not self.address.isdigit():
                    self.stop_Measurement("Please add the Modbus address to the COM port using the following syntax"
                                          " 'COM1:{address}', e.g. 'COM1:3'. In case of EI-Bisync protocol use"
                                          " 'COM1:EI{address}', e.g 'COM1:EI3'.")
                    return False
            
                self.port = minimalmodbus.Instrument(self.com_port, int(self.address), close_port_after_each_call=False, debug=False)
                self.comm_type = "Modbus"
                
                for key in self.default_port_properties_Modbus:
                    if key not in self.port_properties:
                        self.port_properties[key] = self.default_port_properties_Modbus[key]
                         
                # self.port.serial is the underlying pyserial COM port object of minimalmodbus
                self.port.serial.timeout = self.port_properties["timeout"]
                self.port.serial.baudrate = self.port_properties["baudrate"]
                self.port.serial.parity = self.port_properties["parity"]
                self.port.serial.bytesize = self.port_properties["bytesize"]
                self.port.serial.stopbits = self.port_properties["stopbits"]
                
        else:
            raise Exception("Please add the Modbus address to the COM port using the following syntax 'COM1:{address}', "
                            "e.g. 'COM1:3'. In case of EI-Bisync protocol use 'COM1:EI{address}', e.g 'COM1:EI3'.")

        # first communication must be always retrieving the resolution for Modbus #
        if self.comm_type == "Modbus":
            self._digits = self.get_decimal_positions()

        self.output_high = self.get_output_high()
        self.output_low = self.get_output_low()     
                    
    def disconnect(self):
        
        if self.comm_type == "Modbus":
            self.port.serial.close()  # here we close the serial port created by minimalmodbus
        elif self.comm_type == "EI-Bisync":
            self.port.close()
        
    def initialize(self):

        self.rampunit_conversion_instr = self.get_rampunit_conversion_to_s()
        # print("Eurotherm ramp unit conversion to s:", self.rampunit_conversion_instr)

    def deinitialize(self):
        pass

    def configure(self):
    
        # print("SPrr before:", self.get_setpoint_ramprate())
    
        # print(self.sweepmode)
            
        if self.sweepmode == "Temperature":
        
            self.set_automatic()
            
            if self.rate != "":
            
                rate_value = float(self.rate)
            
                if self.temperature_unit == "°F":
                    rate_value = 5/9*(rate_value - 32.0)
                    
                self.set_setpoint_ramprate(rate_value)
                
        elif self.sweepmode == "None":
            pass
            # self.set_output(0.0)
        else:
            self.set_manual()          

        if self.output_max != "":
            self.set_output_high(float(self.output_max))
            # print("Output max", self.get_output_high())
            
        # print("SPrr after:", self.get_setpoint_ramprate())
            
    def unconfigure(self):
    
        if self.zeroOutputaftersweep:
            self.set_manual()
            self.set_output_low(0.0)
            self.set_output(0.0)
             
        if self.idle_temperature != "" and not self.idle_temperature is None:
        
            if self.temperature_unit == "°C":
                value = float(self.idle_temperature)
                
            elif self.temperature_unit == "K":
                value = float(self.idle_temperature) - 273.15
                
            elif self.temperature_unit == "°F":
                value = 5/9*(float(self.idle_temperature) - 32.0)

            else:
                raise Exception("Unknown temperature unit '%s'" % self.temperature_unit)
           
            self.set_setpoint_temperature(value)
            
    def apply(self):
                  
        if self.sweepmode == "Temperature":
        
            if self.temperature_unit == "°C":
                pass
                
            elif self.temperature_unit == "K":
                self.value = self.value - 273.15
                
            elif self.temperature_unit == "°F":
                self.value = 5/9*(self.value - 32.0)
           
            self.set_setpoint_temperature(self.value)
            
        elif self.sweepmode == "Output in %":
            self.set_output(self.value)

    def measure(self):  
        pass

    def call(self):
    
        temp_real = self.get_process_temperature()
        #temp_set = self.get_setpoint_temperature()
        output = self.get_output()   
               
        return temp_real, output
    
    def finish(self):
        pass
        
    def measure_temperature(self):
        temperature = self.get_process_temperature()
        return temperature

    # here commands start that write to / read from certain registers #

    def get_rampunit_conversion_to_s(self):
        # the default value is 60.0 as we expect that standard unit is min
        # Each driver for a model with variable ramp rate unit can overwrite this function
        # to return a value that depends on the unit
        return 60.0
          
    def get_decimal_positions(self):
        """ get the number of decimal positions """
    
        resolution = self.get_resolution()            

        if resolution == 0:  # Full resolution is selected and we have to ask for the number of decimal point positions
            decimal_point_positions = self.get_decimalpoint_positions()
        elif resolution == 1:  # Integer resolution
            decimal_point_positions = 0
        else:
            raise ValueError(f"Unknown resolution returned with value {resolution}:")

        return decimal_point_positions
                
    def set_manual(self, state = True):
        """ set manual mode, default state is True. False can be used to unset manual = automatic """ 
    
        manual = self.get_manual()
        
        if state == (manual == 1):
            return # Nothing to do because the mode is already correct

        if state:
            self.write("ManualMode", 1)  # Manual on
            # self.write("Display", 2)
        else:
            self.write("ManualMode", 0)  # Manual off = auto
            # self.write("Display", 0)
            
    def get_manual(self):
        """ get manual mode """ 
    
        return self.read("ManualMode")  

    def set_automatic(self, state = True):
        """ set manual mode, default state is True. False can be used to unset automatic = manual """ 
            
        self.set_manual(not state)
            
    def set_display(self, state):

        # diSP Display
        # 0: Standard
        # 1: Load current
        # 2: Output power
        # 3: Program state
        # 5: Blank
        # 6: Valve position
        
        self.write("Display", state)

    def get_output(self):
                  
        return self.read("ManualOutput")
        
    def set_output(self, value):

        if value < self.output_low:
            debug("Output value (%1.1f%%) below Output low (%1.1f%%)" % (value, self.output_low))
            value = self.output_low
            
        elif value > self.output_high:
            debug("Output value (%1.1f%%) above Output high (%1.1f%%)" % (value, self.output_high))
            value = self.output_high

        self.write("ManualOutput", value)  # Modbus maybe needs to be signed
        
    def get_output_high(self):
        
        return self.read("OutputHigh") 
        
    def set_output_high(self, value):
    
        if value <= self.output_low:
            self.message_Box("OutputHigh value below OutputLow. Please change OutputLow first!)")
        elif value > 100.0:
            self.message_Box("OutputHigh value above 100% is not supported.")
        else:
            try:
                self.write("OutputHigh", value)
                self.output_high = value
            except:
                error("Failed to write OutputHigh")

    def get_output_low(self):
                    
        return self.read("OutputLow")
            
    def set_output_low(self, value):
        
        if value < 0.0:
            self.message_Box("OutputLow value below 0% is not supported.")
        elif value >= self.output_high:
            self.message_Box("OutputLow above OutputHigh. Please change OutputHigh first!")
        else:
        
            try:
                self.write("OutputLow", value)
                self.output_low = value
            except:
                error("Failed to write OutputLow")        
            
    def get_process_temperature(self):
        """ returns the process temperature depending on the selected temperature unit """
                    
        res = self.read("ProcessValue")
        
        # if res == 999.9:
            # res = float('nan')
            
        if self.temperature_unit == "°C":
            pass
        elif self.temperature_unit == "K":
            res = res + 273.15
        elif self.temperature_unit == "°F":
            res = (9.0/5*res)+32.0   
    
        return res

    def get_setpoint_temperature(self):
        """ returns the setpoint temperature in °C """
            
        return self.read("SetPoint")

    def set_setpoint_temperature(self, value):
        """ changes the setpoint temperature to given value """

        self.write("SetPoint", value)

    def get_setpoint_ramprate(self):
        """ returns the setpoint ramprate in °C per ramp unit """

        value = self.read("SetPointRampRate")
        value = float(value) / self.rampunit_conversion_instr * self.rampunit_conversion_user
        return value
             
    def set_setpoint_ramprate(self, value):
        """ changes the setpoint ramprate to given value in °C per ramp unit """

        value = float(value) * self.rampunit_conversion_instr / self.rampunit_conversion_user

        self.write("SetPointRampRate", value)
        
    def get_rampunit(self):
        """ read the ramp rate unit, as needed to correctly set the setpoint ramprate
        
        Returns:
            Integer
                0: Secs
                1: Mins
                2: Hours
        """
        
        return self.read("RampUnit")
        
    def get_resolution(self):
        """ returns an integer related to resolution """
        
        # 0: Full
        # 1: Integer
        
        return self.read("Resolution")
            
    def set_resolution(self, value):
        """ changes the integer value related to the resolution """
    
        # 0: Full
        # 1: Integer    
    
        self.write("Resolution", value)
        
    def get_decimalpoint_positions(self): 
        """ returns the number of decimal point positions """
    
        # 0: nnnn.
        # 1: nnn.n
        # 2: nn.nn

        return self.read("DecimalPointPosition")

    def read_all_registers(self):

        # Readout and print all known registers
        for key in self.registers:
            print(key, self.read(key))

        # Readout and print all first x registers
        x = 200
        for i in range(x):
            print("%i" % (i+1), self.port.read_register(i+1, 0))

    def get_digits(self, key):
        """ a function that can be overloaded by the drivers individual classes """
        
        return self._digits
  
    def write(self, key, value):
    
        if not key in self.registers:
            key = key + str(self.channel)  # we add the channel only if the parameter is not a general parameter
        
        digits  = self.registers[key][1]
        
        if self.comm_type == "Modbus":
        
            address = self.registers[key][0]
            
            if digits > 0:
                    
                if digits > 0:
                    digits = self.get_digits(key)
            
                value = round(float(value), digits)
                
            else:
                value = int(float(value))
                           
            try:
                self.port.write_register(address, value, digits)
            except:
                error("Error: Cannot write value '%s' to register '%s'" % (str(value), str(key)) )
        
        elif self.comm_type == "EI-Bisync":
        
            self.retries += 1
        
            # print()
            # print("EI-Bisync write:", key, self.retries)
            
            if self.port.in_waiting > 0:
                first_readout = self.port.read(self.port.in_waiting)
                # print("First readout", first_readout)
        
            C1, C2 = self.registers[key][2]

            # [EOT](GID)(GID)(UID)(UID)[STX](CHAN)(C1)(C2)<DATA>[ETX](BCC)
            
            DATA = str(round(value, digits))
            # print(DATA)
                        
            # self.CHAN = "1"            
            msg = self.EOT + self.GID + self.GID + self.UID + self.UID + self.STX + self.CHAN + C1 + C2 + DATA + self.ETX
                        
            # calculate checksum
            BCC = self.calculate_checksum(self.CHAN + C1 + C2 + DATA + self.ETX)
            msg += BCC

            self.port.write(msg.encode())
            
            answer = self.port.read(1).decode('latin-1')
            # print("First byte:", answer.encode('latin-1'))
            
            # this might be needed for RS485 adapters with FTDI chip that receive a \x00 after each message
            if answer == chr(0x00):
                answer = self.port.read(1).decode('latin-1')
                # print("Leading 0 byte:", answer.encode('latin-1'))
                                                 
            # print("Answer", repr(answer))
            
            # [ACK] or [NAK]
            if answer == self.ACK:
                self.retries = 0
                return True
            else:
                debug("Eurotherm was not able to set data '%s' for register '%s' during write" % (DATA, key))
                                        
                if self.retries < 30:
                    return self.write(key, value)
                else:
                    self.stop_Measurement("Eurotherm was not able to set data '%s' for register '%s' during write after 10 retries." % (DATA, key))
                    return False
                 
    def read(self, key):

        if key not in self.registers:
            key = key + str(self.channel)  # we add the channel only if the parameter is not a general parameter

        if self.comm_type == "Modbus":
        
            try:
                address = self.registers[key][0]
                digits  = self.registers[key][1]
                

                if digits > 0:
                    digits = self.get_digits(key)
                
                # read_register(registeraddress, number_of_decimals=0, functioncode=3, signed=False)
                res = self.port.read_register(address, digits, signed=True)
                
            except minimalmodbus.NoResponseError:
                raise Exception("Cannot read value from register '%s' because no response." % (str(key)))

            return res

        elif self.comm_type == "EI-Bisync":
        
            self.retries += 1
        
            # print()
            # print("EI-Bisync read:", key, self.retries)
            
            if self.port.in_waiting > 0:
                first_readout = self.port.read(self.port.in_waiting)
                # print("First readout", first_readout)
        
            C1, C2 = self.registers[key][2]
          
            # [EOT](GID)(GID)(UID)(UID)(CHAN)(C1)(C2)[ENQ]
            msg = self.EOT + self.GID + self.GID + self.UID + self.UID + self.CHAN + C1 + C2 + self.ENQ
            
            # print(msg.encode())

            self.port.write(msg.encode())

            # [STX](CHAN)(C1)(C2)<DATA>[ETX](BCC)
            answer = self.port.read(1).decode('latin-1')
            # print("First byte:", answer.encode('latin-1'))
            
            # this might be needed for RS485 adapters with FTDI chip that receive a \x00 after each message
            if answer == chr(0x00):
                answer = self.port.read(1).decode('latin-1')
                # print("Leading 0 byte:", answer.encode('latin-1'))
            if answer != self.STX:
                # print("Message before error:", self.port.read(20))
                # self.stop_Measurement("Eurotherm does not respond after query register '%s'. Please check the COM port and the EI-Bisync address." % key)
                debug("Eurotherm EI-Bisync communicaton: first character was '%s', but expected is STX character (0x02)" % answer)
                
                if self.retries < 30:  
                    return self.read(key)
                else:
                    raise Exception("Unable to read value for register '%s' after 30 retries." % key)
                
            else:
                if len(self.channels_available) > 1:
                    CHAN = self.port.read(1).decode('latin-1')
                C1 = self.port.read(1).decode('latin-1')
                C2 = self.port.read(1).decode('latin-1')
                
                data = ""
                i = 0
                while True:
                    i += 1
                    
                    answer = self.port.read(1).decode('latin-1')
                    
                    if answer == self.ETX:
                        break
                    else:
                        data += answer
                         
                    if i > 30:
                        if self.retries < 30:  
                            return self.read(key)
                        else:
                            raise Exception("Unable to read value for register '%s' after 30 retries." % key)

                BCC = self.port.read(1).decode('latin-1')
                
                # calculate checksum
                if len(self.channels_available) > 1:
                    BCC_calc = self.calculate_checksum(CHAN+C1+C2+data+self.ETX)
                else:
                    BCC_calc = self.calculate_checksum(C1+C2+data+self.ETX)
                                    
                # Let's readout trailing \x00 characters that might be detected by RS485 adapter with FTDI chip
                if self.port.in_waiting > 0:
                    readout = self.port.read(self.port.in_waiting)
                    # print("Final readout", readout)
                
                if BCC != BCC_calc:
                    debug("Checksum failed for Eurotherm message '%s'" % msg)
                    
                    if self.retries < 30:  
                        return self.read(key)
                    else:
                        self.stop_Measurement("Unable to read value for register '%s' after 30 retries." % key)
                        return False
                else:
                    self.retries = 0
                    return float(data)

    def calculate_checksum(self, input):
        
        checksum = ord(input[0])
           
        for x in input[1:]:
            checksum ^= ord(x)

        return chr(checksum)
