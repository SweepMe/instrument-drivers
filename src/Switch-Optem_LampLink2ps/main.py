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
# * Module: Switch
# * Instrument: Optem LampLink2ps


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
        <h3>Optem LampLink2ps</h3>
        The driver switches the lamp on when the module is part of the active branch.
        When the module is no more part of the active branch, it is switched off.
        
        If the control mode "Brightness" is used, please enter a number in the field "Brightness in %".
        If the control mode "Preset" is used, please enter an index in the field "Preset".
    """
                  
    actions = ["switch_off", "switch_on"]

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "LampLink"
        
        self.variables = ["Brightness"]
        self.units = ["%"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data
                  
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "baudrate": 9600,
            "timeout": 1,
            "EOL": "\r\n",
        }

    def set_GUIparameter(self):
        
        GUIparameter = {
            "SweepMode": ["None"],
            "Mode": ["Brightness", "Preset"],
            "Brightness in %": "0.0",
            "Preset": 1,
        }
                        
        return GUIparameter
    
    def get_GUIparameter(self, parameter={}):

        self.control_mode = parameter["Mode"]
        self.brightness_val = float(parameter["Brightness in %"])
        self.preset_val = parameter["Preset"]
        
    def configure(self):
        self.switch_on()
        
    def unconfigure(self):
        self.switch_off()
        
    def call(self):
    
        return [self.value]
        
    # wrapped commands
    
    def query_zoom(self):
    
        self.port.write("QZ")
        ret = self.port.read()
        return float(ret.split(" ")[1])
        
    def set_brightness(self, brightness):
    
        self.port.write("MB A%i" % int(brightness))
        ret = self.port.read()
        
    def get_brightness(self):
    
        self.port.write("QB")
        ret = self.port.read()
        return float(ret.split(" ")[1])
        
    def set_preset(self, preset):
    
        self.port.write("MB %i" % int(preset))
        ret = self.port.read()
        
    def switch_off(self):
        
        self.set_brightness(0.0)
        
    def switch_on(self):
    
        if self.control_mode == "Brightness":
            self.set_brightness(self.brightness_val)
        elif self.control_mode == "Preset":
            self.set_preset(self.preset_val)
        else:
            msg = "Undefined control mode"
            raise Exception(msg)