# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
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
# Type: Logger
# Device: Yoctopuce Yocto-Relay


from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()

from pysweepme.ErrorMessage import error, debug

from yoctopuce.yocto_api import *
from yoctopuce.yocto_relay import *

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description =   """
                    https://www.yoctopuce.com/EN/doc/reference/yoctolib-python-EN.html<br>
                    <br>
                    The device always starts in the off state (0).
                    
                    Accepted values are int, float and bool, and strings if they can be converted to a number.
                    Everything equal or above 1 is interpreted on (1). all other values result in off (0)
                    
                    """
                    
    actions = ["switch_on", "switch_off"]

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Yocto-Relay" # short name will be shown in the sequencer


    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        GUIparameter = {
                        "SweepMode": ["State"],
                        "Channel": ["1", "2"],
                        }

        return GUIparameter
        
       
    def get_GUIparameter(self, parameter):
        
        self.channel = parameter["Channel"]
        
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        
        self.variables.append("State%s" % self.channel)
        self.units.append("")
        self.plottype.append(True)
        self.savetype.append(True)
            
        self.port_serial = parameter["Port"]
      
    def find_Ports(self):
    
        errmsg = YRefParam()

        # print(YAPI)
        # print(errmsg)
        
        # Setup the API to use local USB devices
        if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
            self.stop_Measurement("Error in connecting to Yoctopuce %s" % self.shortname + errmsg.value)
            return []
        
        ports = []
        
        YAPI.UpdateDeviceList()
        
        # find all devices
        sensor = YRelay.FirstRelay()
        
        if sensor is None:
            self.stop_Measurement("No Yoctopuce %s connected." % self.shortname)
            return ports
        else:
        
            # retrieve module serial or friendly name
            # serial = sensor.get_module().get_serialNumber()     
            serial = sensor.get_module().get_friendlyName()    
            
            ports.append(serial)
        
            sensor = sensor.nextRelay()
            
            while not sensor is None:
                
                # retrieve module serial or friendly name
                # serial = sensor.get_module().get_serialNumber()     
                serial = sensor.get_module().get_friendlyName()   

                if not serial in ports:
                    ports.append(serial)
                
                sensor = sensor.nextRelay()
                
        YAPI.UnregisterHub("usb")
        
        ## frees memory, but no further functions can be used
        YAPI.FreeAPI()

        return ports
            
        
        
    def connect(self):

        ## initialize the API. However, it is anyway done during 'RegisterHub'
        # YAPI.InitAPI("usb")
        
        errmsg=YRefParam()
        if YAPI.RegisterHub("usb", errmsg)!= YAPI.SUCCESS:
            self.stop_Measurement("Error when connecting to Yoctopuce %s: " % self.shortname + errmsg.value)
            return False
            
        self.relay = YRelay.FindRelay(self.port_serial + '.relay%s' % self.channel)

        if not (self.relay.isOnline()): 
            self.stop_Measurement("Device is not online.")
            return False
            
    
    def disconnect(self):
        
        YAPI.UnregisterHub("usb")
        
        ## frees memory, but no further functions can be used
        YAPI.FreeAPI()
            
            
    def initialize(self):
        self.switch_off()


    def deinitialize(self):
        self.switch_off()    
        
    def unconfigure(self):
        pass
    
    
    def apply(self):
    
        try:

            state = int(float(self.value))  # automatically handles bool as well
            
            if state >= 1:
                self.switch_on()
            else:
               self.switch_off()
                
        except:
            error()
            self.switch_off()
        
    

    def call(self):

        return self.state
        
        
    """ setter/getter functions """
    
    def switch_off(self):
    
        if self.relay.isOnline():
            self.relay.set_state(YRelay.STATE_A)
            self.state = 0
        
            return True
            
        return False
    
    def switch_on(self):
    
        if self.relay.isOnline():
            self.relay.set_state(YRelay.STATE_B)
            self.state = 1
            
            return True
            
        return False
    
    
        
