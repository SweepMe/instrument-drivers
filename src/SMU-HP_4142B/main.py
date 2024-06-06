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


# SweepMe! driver
# * Module: SMU
# * Instrument: HP 4142B


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data
        
        self.port_manager = True
        self.port_types = ['GPIB']
        self.port_properties = {    
            "timeout": 5,
        }

        self.current_ranges = {
            "Auto": "0",
            "1 pA limited auto": "8",
            "10 pA limited auto": "9",
            "100 pA limited auto": "10",
            "1 nA limited auto": "11",
            "10 nA limited auto": "12",
            "100 nA limited auto": "13",
            "1 μA limited auto": "14",
            "10 μA limited auto": "15",
            "100 μA limited auto": "16",
            "1 mA limited auto": "17",
            "10 mA limited auto": "18",
            "100 mA limited auto": "19",
            "1 A limited auto": "20",
        }

    def set_GUIparameter(self):
        
        GUIparameter = {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": ["CH1", "CH2", "CH3", "CH4", "CH5", "CH6"],
            "RouteOut": ["Rear"],
            # "Speed": ["Fast", "Medium", "Slow"],
            "Range": list(self.current_ranges.keys()),
            "Compliance": 100e-6,
            "Average": 1,
        }
                        
        return GUIparameter

    def get_GUIparameter(self, parameter={}):

        self.route_out = parameter['RouteOut']
        self.source = parameter['SweepMode']
        self.port_string = parameter['Port']

        self.irange = self.current_ranges[parameter['Range']]
        
        self.protection = parameter['Compliance']
        # self.speed = parameter['Speed']
        
        self.average = int(parameter['Average'])
        
        self.channel = parameter['Channel'][-1]
        
        self.shortname = "HP4142B CH%s" % self.channel
        
        # voltage autoranging 
        self.vrange = "0"

    def initialize(self):
    
        unique_DC_port_string = "HP4142B_" + self.port_string

        # initialize commands only need to be sent once, so we check here whether another instance of the same
        # driver AND same port did it already. If not, this instance is the first and has to do it.
        if unique_DC_port_string not in self.device_communication:
        
            self.port.write("*IDN?") # identification
            identifier = self.port.read()
            # print("Identifier:", identifier)
            
            self.port.write("*RST")  # reset to initial settings
                       
            self.port.write("BC")  # buffer clear
            
            self.port.write("FMT 2")  # use to change the output format
         
            # if initialize commands have been sent, we can add the unique_DC_port_string to the dictionary that
            # is seen by all drivers
            self.device_communication[unique_DC_port_string] = True
          
    def configure(self):
    
        # The command CN has to be sent at the beginning as it resets certain parameters
        # If the command CN would be used later, e.g. during 'poweron', it would overwrite parameters that are
        # defined during 'configure'
        self.port.write("CN " + self.channel) # switches the channel on
    
        """
        if self.speed == "Fast": # 1 Short (0.1 PLC) preconfigured selection Fast
            self.port.write("AIT 0,0,1")
            self.port.write("AAD %s,0" % self.channel)
        elif self.speed == "Medium": # 2 Medium (1.0 PLC) preconfigured selection Normal
            self.port.write("AIT 1,0,1")
            self.port.write("AAD %s,1" % self.channel)
        elif self.speed == "Slow": # 3 Long (10 PLC) preconfigured selection Quiet
            self.port.write("AIT 1,2,10")
            self.port.write("AAD %s,1" % self.channel)
        """
        
        #command syntax for DV and DI slightly different than B1500     
        if self.source.startswith("Voltage"):
            self.port.write("DV " + self.channel + "," + self.vrange + "," + "0.0" + "," + self.protection + ", 0")

        if self.source.startswith("Current"):
            self.port.write("DI " + self.channel + "," + self.irange + "," + "0.0" + "," + self.protection + ", 0")

        #RI and RV #comments to adjust the range, autorange is default
        
        self.port.write("AV %i" % self.average)

        # *LRN? is a function to ask for current status of certain parameters,
        # 0 = output on or off
        # self.port.write("*LRN? 0")
        # print(self.port.read())
        
    def unconfigure(self):
        self.port.write("IN" + self.channel)
        # resets to zero volt
        # self.port.write("DZ")

    def poweron(self):
        pass
        # In a previous version, the CN command was sent here. However, this leads to a reset of all parameters
        # previously changed during 'configure'
        # Therefore, the CN command should not be used here, but has been moved to the beginning of 'configure'
    
    def poweroff(self):
        self.port.write("CL " + self.channel)  # switches the channel off
      
    def apply(self):

        value = str(self.value)
        
        if self.source.startswith("Voltage"):
            self.port.write("DV " + self.channel + "," + self.vrange + "," + value)

        if self.source.startswith("Current"):
            self.port.write("DI " + self.channel + "," + self.irange + "," + value)

    def measure(self):
        self.port.write("TI" + self.channel + ",0")      
        self.port.write("TV" + self.channel + ",0")  
        
    def call(self):
        
        answer = self.port.read()
        # print("Current:", answer)
        
        # If NAI comes first, we have to strip it. Please toggle the lines, if needed.
        i = float(answer)
        # i = float(answer[3:])
        
        answer = self.port.read()
        # print("Voltage:", answer)
        
        # If NAV comes first, we have to strip it. Please toggle the lines, if needed.
        v = float(answer)
        # v = float(answer[3:])
    
        return [v,i]

    """
    Enables channels CN [chnum ... [,chnum] ... ]
    Disables channels CL [chnum ... [,chnum] ... ]
    Sets filter ON/OFF [FL] mode[,chnum ... [,chnum] ... ]
    Sets series resistor ON/OFF [SSR] chnum,mode
    Sets integration time
    (Agilent B1500 can use
    AAD/AIT instead of AV.)
    [AV] number[,mode]
    [AAD] chnum[,type]
    [AIT] type,mode[,N]
    Forces constant voltage DV chnum,range,output
    [,comp[,polarity[,crange]]]
    Forces constant current DI
    Sets voltage measurement
    range
    [RV] chnum,range
    Sets current measurement
    range
    [RI] chnum,range
    [RM] chnum,mode[,rate]
    Sets measurement mode MM 1,chnum[,chnum ... [,chnum] ... ]
    Sets SMU operation mode [CMM] chnum,mode
    Executes measurement XE
    """