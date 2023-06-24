# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022-2023 SweepMe! GmbH (sweep-me.net)
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
# Type: SMU
# Device: Keithley 26xx

import numpy as np

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
            
        self.variables = ["Voltage", "Current"]
        self.units     = ["V", "A"]
        self.plottype  = [True, True]
        self.savetype  = [True, True]
        
        self.port_manager = True
        self.port_types = ['COM', 'GPIB', 'USB', 'TCPIP']
        self.port_properties = {"baudrate": 115200,
                                "EOL": "\n",
                                "timeout": 10,

                                # AF@04.08.20: delay maybe needed for TCPIP communication
                                # as it seems that some commands are lost
                                # "delay": 0.01,
                                }
                            
        self.port_identifications = ['Keithley Instruments,26', 'Keithley Instruments Inc., Model 26']

        self.pulse_mode = True

        # variable needed later to check whether at least one instance of this device class did already connect
        self.PortManager_registered = False

        self.prefix_conversion = {
                                "m": "e-3",
                                "µ": "e-6",
                                "n": "e-9",
                                "p": "e-12",
                                }

        self.current_ranges = ["Auto", "Limited 1A", "Limited 100mA", "Limited 10mA", "Limited 1mA", "Limited 100µA",
                               "Limited 10µA", "Limited 1µA", "Limited 100nA", "Limited 10nA", "Limited 1nA",
                               "Limited 100pA", "Fixed 1A", "Fixed 100mA", "Fixed 10mA", "Fixed 1mA", "Fixed 100µA",
                               "Fixed 10µA", "Fixed 1µA", "Fixed 100nA", "Fixed 10nA", "Fixed 1nA", "Fixed 100pA"]
        
    def set_GUIparameter(self):
        
        gui_parameter = {
                        "SweepMode": ["Voltage in V", "Current in A"],
                        
                        "Channel": ["Ch A", "Ch B"],
                        "4wire": False,
                        "RouteOut": ["Rear"],
                        "Speed": ["Fast", "Medium", "Slow"],
                        "Range": self.current_ranges,
                        "Average": 1,
                        "Compliance": 100e-6,
                        
                        "CheckPulse": False,
                        "PulseMeasTime": 200e-6,
                        "PulseOnTime": 200e-6,
                        "PulseOffTime": 200e-3,
                        "PulseOffLevel": 0.0,
                        }
                        
        return gui_parameter
        
    def get_GUIparameter(self, parameter={}):
        
        self.source = parameter['SweepMode']
        
        self.device = parameter['Device']
        self.channel = parameter['Channel']
        
        self.four_wire = parameter['4wire']
        self.route_out = parameter['RouteOut']
        self.protection = parameter['Compliance']
        self.speed = parameter['Speed']
        self.current_range = parameter['Range']
        
        self.current_autorange = True
        self.current_autorange_lowlimit = None
        
        if self.current_range.startswith("Limited"):
        
            self.current_autorange_lowlimit = None
            
            if self.current_range.startswith("Limited"):   
                self.current_autorange_lowlimit = self.current_range.split()[1]
                
                for conversion in self.prefix_conversion:
                    self.current_autorange_lowlimit = self.current_autorange_lowlimit.replace(
                        conversion,
                        self.prefix_conversion[conversion])
            
                self.current_autorange_lowlimit = float(self.current_autorange_lowlimit.replace("A", ""))
            
        elif self.current_range.startswith("Fixed"):
        
            self.current_autorange = False
            self.current_range_value = self.current_range.split()[1]
            
            for conversion in self.prefix_conversion:
                self.current_range_value = self.current_range_value.replace(
                    conversion,
                    self.prefix_conversion[conversion])
            
            self.current_range_value = float(self.current_range_value.replace("A", ""))
                
        self.average = int(parameter['Average'])
        
        self.pulse = parameter['CheckPulse']  
        self.pulse_meas_time = parameter['PulseMeasTime']
        self.ton = float(round(float(parameter["PulseOnTime"]), 6))
        self.toff = float(parameter["PulseOffTime"])
        self.pulseofflevel = parameter['PulseOffLevel']

        self.shortname = "Keithley26xx Ch %s" % self.device[-1]
        
        if self.channel[-1] == "A":
            self.smu_ab = "smua"
        elif self.channel[-1] == "B":
            self.smu_ab = "smub"
              
    def connect(self):   
        if self.port.port_properties["NrDevices"] == 1:
            self.port.port_properties.update({"Master": self.pulse})
            self.master = True
        else:
            self.master = False
            self.port.port_properties.update({"Slave": self.pulse})
            
        self.port.port.write_termination = "\n"
                                
    def initialize(self):              

        if self.ton < 200e-6:
            self.ton = 200e-6
        if self.toff < 200e-6:
            self.toff = 200e-3
        if self.toff > 3.0:
            self.toff = 3.0
            
        if self.smu_ab == "smua":
            self.tag = "1"
        else:
            self.tag = "2"
                               
        self.port.write(self.smu_ab + ".reset()")
        self.port.write("errorqueue.clear()")

        # Some devices have problems with this command, maybe because they are not the localnode
        # Should this driver get support for nodes in future, one could include it again.
        # self.port.write("localnode.autolinefreq = true")

        self.port.write(self.smu_ab + ".measure.autozero = " + self.smu_ab + ".AUTOZERO_ONCE")

    def deinitialize(self):
        self.rsen_off()
        self.port.write(self.smu_ab + ".measure.filter.count = 1")
        self.port.write(self.smu_ab + ".measure.filter.enable = " + self.smu_ab + ".FILTER_OFF")

    def configure(self):
    
        if not self.PortManager_registered:
            self.port.port_properties["NrDevices"] += 1
            self.PortManager_registered = True

        if self.port.port_properties["NrDevices"] == 1:
            self.port.port_properties.update({"Master": self.pulse})
            self.master = True
        else:
            self.master = False
            self.port.port_properties.update({"Slave": self.pulse})
                
        if self.pulse:
            self.port.write(self.smu_ab + ".source.autorangev  = " + self.smu_ab + ".AUTORANGE_OFF")
            self.port.write(self.smu_ab + ".source.autorangei  = " + self.smu_ab + ".AUTORANGE_OFF")
            self.port.write(self.smu_ab + ".measure.autorangev = " + self.smu_ab + ".AUTORANGE_OFF")
            self.port.write(self.smu_ab + ".measure.autorangei = " + self.smu_ab + ".AUTORANGE_OFF")

        else:
            if self.source.startswith("Voltage"):
                self.port.write(self.smu_ab + ".source.func = " + self.smu_ab + ".OUTPUT_DCVOLTS")
                self.port.write("display." + self.smu_ab + ".measure.func = display.MEASURE_DCAMPS")
                self.port.write(self.smu_ab + ".source.limiti = " + self.protection)

            elif self.source.startswith("Current"):
                self.port.write(self.smu_ab + ".source.func = " + self.smu_ab + ".OUTPUT_DCAMPS")
                self.port.write("display." + self.smu_ab + ".measure.func = display.MEASURE_DCVOLTS")
                self.port.write(self.smu_ab + ".source.limitv = " + self.protection)

            self.port.write(self.smu_ab + ".source.autorangev  = " + self.smu_ab + ".AUTORANGE_ON")
            self.port.write(self.smu_ab + ".measure.autorangev = " + self.smu_ab + ".AUTORANGE_ON")
            
            self.port.write(self.smu_ab + ".source.autorangei  = " + self.smu_ab + ".AUTORANGE_ON")
            
            if self.current_autorange:
                self.port.write(self.smu_ab + ".measure.autorangei = " + self.smu_ab + ".AUTORANGE_ON")
                if self.current_autorange_lowlimit is not None:
                    self.port.write(self.smu_ab + ".measure.lowrangei = %1.3e" % self.current_autorange_lowlimit)
            else:
                self.port.write(self.smu_ab + ".measure.autorangei = " + self.smu_ab + ".AUTORANGE_OFF")
                self.port.write(self.smu_ab + ".measure.rangei = %1.3e" % self.current_range_value)

        if self.four_wire:
            self.rsen_on()
        else:
            self.rsen_off()
   
        if self.speed == "Fast":
            self.nplc = 0.1
        if self.speed == "Medium":
            self.nplc = 1.0
        if self.speed == "Slow":
            self.nplc = 10.0

        if self.average > 1:
            self.port.write(self.smu_ab + ".measure.filter.count = %i" % self.average)
            self.port.write(self.smu_ab + ".measure.filter.enable = " + self.smu_ab + ".FILTER_ON")
            self.port.write(self.smu_ab + ".measure.filter.type = " + self.smu_ab + ".FILTER_REPEAT_AVG")
        else:
            self.port.write(self.smu_ab + ".measure.filter.count = 1")
            self.port.write(self.smu_ab + ".measure.filter.enable = " + self.smu_ab + ".FILTER_OFF")

        # speed of measurement Fast=0.01, Normal=1.0, Hi-Acc=10.0, Max=25.0, (1==20ms)
        self.port.write(self.smu_ab + ".measure.nplc = " + str(self.nplc))

    def unconfigure(self):
    
        if self.PortManager_registered:
            
            self.port.port_properties["NrDevices"] -= 1
            self.PortManager_registered = False
    
        if self.port.port_properties["NrDevices"] == 1:
            self.port.port_properties.update({"Master": False})
        else:
            self.port.port_properties.update({"Slave": False})

    def poweron(self):
        self.port.write(self.smu_ab + ".source.output = 1")
    
    def poweroff(self):
        self.port.write(self.smu_ab + ".source.output = 0")       

    def start(self):
        self.dualpulse = False
        if self.port.port_properties["NrDevices"] == 2:
            if self.port.port_properties["Master"] is True and self.port.port_properties["Slave"] is True:
                self.dualpulse = True

    def apply(self):
    
        self.value = str(self.value)

        if self.pulse:

            # converts the percentage value of self.speed into a corresponding speed value
            # multiplies by 50 because of line frequency
            self.nplc = self.ton * self.pulse_meas_time / 100.0 * 50.0
              
            if self.dualpulse:
            
                if self.smu_ab == "smub":
                    # prolongs SMUb on-time by 40 mus to ensure proper encapsulation of SMUa pulse in DualPulse-mode
                    self.ton_ = self.ton + 40e-6
                else:
                    self.ton_ = self.ton
                    
                if self.master:
                    self.port.average = self.average
                else:
                    self.average = self.port.average
                    
            else:
                self.ton_ = self.ton
                  
            self.port.write(self.smu_ab + ".nvbuffer1.clear()")
            self.port.write(self.smu_ab + ".nvbuffer1.appendmode = 1")
            self.port.write(self.smu_ab + ".measure.nplc = " + str(self.nplc))  # plc/50 ton*50/5
            self.port.write(self.smu_ab + ".nvbuffer1.collectsourcevalues = 1")  # plc/50 ton*50/5
                       
            if self.source.startswith("Voltage"):
                self.port.write(self.smu_ab + ".source.rangev = " + str(self.protection))
                # self.port.write(self.smu_ab + ".measure.rangev = " + str(self.protection))
                self.port.write(self.smu_ab + ".measure.rangei = " + str(self.protection))
                # self.port.write(self.smu_ab + ".source.rangei = "  + str(self.protection))
                
                self.port.write("print(ConfigPulseVMeasureI(" + self.smu_ab + "," + self.pulseofflevel + "," +
                                self.value + ", "+str(self.protection) + ", " + str(self.ton_) + ", " +
                                str(self.toff) + ", " + str(self.average) + ", " + self.smu_ab +
                                ".nvbuffer1, " + self.tag + "))")
                self.port.read()  # remove answer from buffer
                
            if self.source.startswith("Current"):
                self.port.write(self.smu_ab + ".source.rangei = " + str(self.protection))
                # self.port.write(self.smu_ab + ".measure.rangei = " + str(self.protection))
                self.port.write(self.smu_ab + ".measure.rangev = " + str(self.protection))
                # self.port.write(self.smu_ab + ".source.rangev = " + str(self.protection))

                self.port.write("print(ConfigPulseIMeasureV(" + self.smu_ab + "," + self.pulseofflevel + "," +
                                self.value + ", " + str(self.protection) + ", " + str(self.ton_) + ", " +
                                str(self.toff) + ", " + str(self.average) + "," + self.smu_ab + ".nvbuffer1, " +
                                self.tag + "))")
                self.port.read()  # remove answer from buffer
        else:
            if self.source.startswith("Voltage"):
                self.port.write(self.smu_ab + ".source.levelv = " + self.value)
            if self.source.startswith("Current"):
                self.port.write(self.smu_ab + ".source.leveli = " + self.value)

    def trigger_ready(self):
    
        if self.pulse:
            if self.dualpulse:
                if self.master:
                    # Pulse with tag1 = 2 has to be 40e-6 s longer than Pulse with tag2 = 1, equal toff,
                    # pulse of smub always encapsulate pulse of smua
                    self.port.write("print(InitiatePulseTestDual(2,1))")
             
            else:
                self.port.write("print(InitiatePulseTest(%s))" % self.tag)

    def measure(self):
    
        # read out answer caused by InitiatePulse in trigger()
        if self.pulse:
            if self.dualpulse:
                if self.master:
                    self.port.read()
                              
            else:
                self.port.read()

        if self.pulse:
            if self.dualpulse:
                if self.master:
                
                    # call values of smua and smub if dualpulse
                    self.port.write("printbuffer(1, " + str(self.average) + ", smua.nvbuffer1.readings)")
                    self.port.write("printbuffer(1, " + str(self.average) + ", smua.nvbuffer1.sourcevalues)")
                    self.port.write("printbuffer(1, " + str(self.average) + ", smub.nvbuffer1.readings)")
                    self.port.write("printbuffer(1, " + str(self.average) + ", smub.nvbuffer1.sourcevalues)")
               
            else:
                self.port.write("printbuffer(1, " + str(self.average) + ", " + self.smu_ab + ".nvbuffer1.readings)")
                self.port.write("printbuffer(1, " + str(self.average) + ", " + self.smu_ab + ".nvbuffer1.sourcevalues)")
        else:
            self.port.write("print("+self.smu_ab + ".measure.iv())")

    def call(self):
    
        if self.pulse:
        
            if self.dualpulse:
                
                if self.master:
                
                    # read all values of smua and smub if dualpulse
                    self.xa = list(map(float, self.port.read().replace("\n", "").split(",")))
                    self.ya = list(map(float, self.port.read().replace("\n", "").split(",")))
                    self.xb = list(map(float, self.port.read().replace("\n", "").split(",")))
                    self.yb = list(map(float, self.port.read().replace("\n", "").split(",")))
                    
                    # if master, write the values of slave to the port buffer object
                    if self.smu_ab == "smua":
                        self.y, self.x = self.ya, self.xa
                        self.port.buffer = self.yb, self.xb  # b readings, b sourcevalues
                    else:
                        self.y, self.x = self.yb, self.xb
                        self.port.buffer = self.ya, self.xa  # a readings, a sourcevalues
                   
                # if slave call the values from the port buffer object 
                else:
                    self.y, self.x = self.port.buffer
             
            else:
                # self.port.write("printbuffer(1, " + str(self.average) + ", " +
                # self.smu_ab + ".nvbuffer1.readings)")
                a = self.port.read()
                self.x = list(map(float, a.replace("\n", "").split(",")))
                
                # self.port.write("printbuffer(1, " + str(self.average) + ", " +
                # self.smu_ab + ".nvbuffer1.sourcevalues)")
                b = self.port.read()
                self.y = list(map(float, b.replace("\n", "").split(",")))

            # Depending on VOLT or CURR mode as source, voltage or current corresponds to .readings or .sourcevalues
            if self.source.startswith("Voltage"):  
                v = np.average(self.y)
                i = np.average(self.x)
            else:
                v = np.average(self.x)
                i = np.average(self.y)          
        
        else:
            a = self.port.read()
            i, v = list(map(float, a.split()))
             
        if v > 1e37 or i > 1e37:
            v = float('nan')
            i = float('nan')
             
        return v, i 
    
    def rsen_on(self):
        self.port.write(self.smu_ab + ".sense = " + self.smu_ab + ".SENSE_REMOTE")
    
    def rsen_off(self):
        self.port.write(self.smu_ab + ".sense = " + self.smu_ab + ".SENSE_LOCAL")

    # from here communication commands are wrapped into python convenience functions

    def reset(self):
        """Resets the device to default configuration"""
        self.port.write(self.smu_ab + ".reset()")
