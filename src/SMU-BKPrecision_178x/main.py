# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 SweepMe! GmbH
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

# This driver makes use of code from the file "libq1785b.py" that is part of the
# package "1785B_Series" released by B&K Precision on github:
# https://github.com/BKPrecisionCorp/1785B_Series
# The package and its license can be found in the lib folder of this driver.

# Contribution: We like to thank GRIP Molecular Technologies, Inc/John Myers-Bangsund, Ph.D. for providing the initial version of this driver.


# SweepMe! device class
# Type: SMU
# Device: BK Precision 178x


import time
from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description = """
                  Maximum voltage can be set via the front panel menu of the instrument
                  """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "BK-Precision 178x"
        
        # BK Precision specific variables
        self.debug = 0  # Set to 1 to see dumps of commands and responses
        self.length_packet = 26  # Number of bytes in a packet
        self.convert_current = 1e3  # Convert current in A to 1 mA
        self.convert_voltage = 1e3  # Convert voltage in V to mV
        self.convert_power   = 1e3  # Convert power in W to mW
        
        # Number of settings storage registers
        self.lowest_register  = 1
        self.highest_register = 25
        self.voltage_correction = 0.0  # Fixed voltage offset which may be instrument dependent
        self.settle_time_s = 0.0
        
        # Sweep-Me variables
        self.variables = ["Voltage", "Current"]
        self.units     = ["V", "A"]
        self.plottype  = [True, True] # True to plot data
        self.savetype  = [True, True] # True to save data
        
        self.port_manager = True
        self.port_types = ['COM']
        self.port_properties = {    "baudrate": 38400,
                                    "EOL": "",
                                    "raw_write": True,
                                    "timeout": 5,
                                    #"write_timeout": 5,
                                    # "delay": 0.01,  # AF@04.08.20: maybe needed for TCPIP communication as it seems that some commands are lost
                                }
                                
        self.port_identifications = ['']
        
    def set_GUIparameter(self):
        GUIparameter = {
                        "SweepMode": ["Voltage in V", "Current in A"],
                        "Compliance": 3,
                       }
        return GUIparameter
        
    def get_GUIparameter(self, parameter={}):
        self.source = parameter['SweepMode']
        self.compliance = float(parameter["Compliance"])

    def connect(self):
        pass

    def initialize(self):
        self.address=0
        self.set_remote_mode(True)
        '''
        The initialization code used by the BK Precision example is as follows:
        def Initialize(self, com_port, baudrate, address=0):
            self.port = serial.Serial(com_port-1, baudrate)
            self.address = address
        I think this is handled internally in SweepMe, so nothing needs to be done here
        '''
        
    def configure(self):
    
        if self.source == "Voltage in V":
            self.set_output_voltage(0)
            self.set_output_current(self.compliance)
        elif self.source == "Current in A":
            self.set_output_voltage(self.compliance)
            self.set_output_current(0)
                    
        self.set_output_voltage(0) # Set voltage to zero initially
        
    def unconfigure(self):
        self.set_output_voltage(0) # Leave voltage at 0 when done with measurement
        
    def deinitialize(self):
        pass
                
    def poweron(self):
        self.set_output_state(True)
        
    def poweroff(self):
        self.set_output_state(False)
                
    def apply(self):
        self.value = float(self.value)
        if self.source == "Voltage in V":
            self.set_output_voltage(self.value+self.voltage_correction)
        elif self.source == "Current in A":
            self.set_output_current(self.value)
            
    def reach(self):
        time.sleep(self.settle_time_s)
    
    def measure(self):
        self.reading = self.get_readings()
        
    def call(self):
        return self.reading['V'], self.reading['I']

    '''
    The below commands are taken from BK Precision's example python driver, with
    a few small modifications.
    '''
    def csum(self,command):
        checksum = 0
        for i in range(25):
            checksum = checksum + command[i]
        return (0xFF & checksum)

    def write_command(self,command):
        command[0] = 0xAA
        command[25] = self.csum(command)
        self.port.write(bytes(command)) # alternative: self.port.port.write(command)
        resp = self.port.read_raw(26) # alternative: resp = self.port.port.read(26)
        if resp[2] == 0x12:
            if resp[3] == 0x80:
                """Success"""
                return
            elif resp[3] == 0x90:
                raise Exception('Checksum Error')
            elif resp[3] == 0xA0:
                raise Exception('Parameter Incorrect')
            elif resp[3] == 0xB0:
                raise Exception('Unrecognized Command')
            elif resp[3] == 0xC0:
                raise Exception('Invalid Command')

            # print("Command Sent:\t\t",end=' ')
            self.printCmd(command)

            # print("Reponse Received:\t",end=' ')
            self.printCmd(resp)
        else:
            return resp

    def printCmd(self,buff):
        x = " "
        for y in range(len(buff)):
            x+=" "
            x+=hex(buff[y]).replace('0x','')
        # print(x)

    def set_remote_mode(self,state):
        """Remote Mode"""
        cmd = [0] * 26
        cmd[2] = 0x20
        if bool(state):
            cmd[3] = 1
        else:
            cmd[3] = 0
        self.write_command(cmd)

    def set_output_state(self,state):
        """Input On. state = True or False"""
        cmd = [0] * 26
        cmd[2] = 0x21
        if bool(state):
            cmd[3] = 1
        else:
            cmd[3] = 0
        self.write_command(cmd)

    def set_max_voltage(self, voltage):
        value = int(voltage * 1000)
        """Set Max Voltage"""
        cmd = [0] * 26
        cmd[2] = 0x22
        cmd[3] = value & 0xFF
        cmd[4] = (value >> 8) & 0xFF
        cmd[5] = (value >> 16) & 0xFF
        cmd[6] = (value >> 24) & 0xFF
        self.write_command(cmd)

    def set_output_voltage(self,voltage):
        """Set Voltage"""
        value = int(voltage * 1000)
        cmd = [0] * 26
        cmd[2] = 0x23
        cmd[3] = value & 0xFF
        cmd[4] = (value >> 8) & 0xFF
        cmd[5] = (value >> 16) & 0xFF
        cmd[6] = (value >> 24) & 0xFF
        self.write_command(cmd)

    def set_output_current(self,current):
        """Set max input current: %f & current"""
        value = int(current * 1000)
        cmd = [0] * 26
        cmd[2] = 0x24
        cmd[3] = value & 0xFF
        cmd[4] = (value >> 8) & 0xFF
        self.write_command(cmd)

    def setCommAddress(self,addr):
        """."""
        cmd = [0] * 26
        cmd[2] = 0x25
        cmd[3] = addr & 0xFF
        resp = self.write_command(cmd)

    def get_readings(self):
        """Read Voltage and Current settings and readings"""
        """Returns dictionary of values"""
        cmd = [0] * 26
        cmd[2] = 0x26
        resp = self.write_command(cmd)
        vals = {}
        vals['I'] = (resp[3]+(resp[4]<<8))/1000
        vals['V'] = (resp[5]+(resp[6]<<8)+(resp[7]<<16)+(resp[8]<<24))/1000
        vals['output'] = resp[9] & 0x01
        vals['overheat'] = resp[9] & 0x02
        mode = ''
        if (resp[9] & 0x0C)>>2 == 1:
            mode = 'CV'
        elif (resp[9] & 0x0C)>>2 == 2:
            mode = 'CC'
        else:
            mode = 'UNREG'
        vals['mode'] = mode
        vals['fanSpeed'] = (resp[9]>>4)&0x07
        vals['remoteCtl'] = (resp[9]&0x80)>>7
        vals['C_set'] = (resp[10]+(resp[11]<<8))/1000
        vals['V_max'] = (resp[12]+(resp[13]<<8)+(resp[14]<<16)+(resp[15]<<24))/1000
        vals['V_set'] = (resp[16]+(resp[17]<<8)+(resp[18]<<16)+(resp[19]<<24))/1000
        return vals

    def readID(self):
        """ID info - returns dict"""
        cmd = [0] * 26
        cmd[2] = 0x31
        resp = self.write_command(cmd)
        vals = {}
        mod = ''
        for i in range(3,6,1):
            mod = mod + chr(resp[i])
        vals['model'] = mod
        vals['sw'] = resp[8]+(resp[9]<<8)
        sn = ''
        for i in range(10,19,1):
            sn = sn + chr(resp[i])
        vals['sn'] = sn
        return vals

    def restoreFactoryCal(self):
        """Restore factory calibration values"""
        cmd = [0] * 26
        cmd[2] = 0x32
        self.write_command(cmd)

    def enableLocalKey(self,state):
        """Enable/Disable Local key (7) with bool value (True/False)"""
        cmd = [0] * 26
        cmd[2] = 0x37
        if bool(state):
            cmd[3] = 1
        else:
            cmd[3] = 0
        self.write_command(cmd)
