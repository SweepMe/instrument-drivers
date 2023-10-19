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

# Contribution: We like to thank TU Dresden/Jörn Vahland for providing the initial version of this driver.


# SweepMe! device class
# Type: Logger
# Device: Inficon IC/5


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    '''
    <p>The Inficon&nbsp;IC/5 Thin Film Deposition Controller is a discontinued product. It is used to measure thin film thicknesses and deposition rates in vacuum chambers based on quartz crystal microbalances</p>
    <p><strong>Keywords:&nbsp;</strong>QCM, quartz crystal microbalance thickness, rate, IC/5</p>
    <p>&nbsp;</p>
    <p><strong>Communication:</strong></p>
    <ul>
    <li>Configure serial interface in 'Program' --> 'I/O' --> Remote Communication</li>
    <li>Baudrate: 9600</li>
    </ul>
    <p>&nbsp;</p>
    <p><strong>Known issues:</strong></p>
    <ul>
    <li>The driver is unable to reset thickness</li>
    </ul>
    <p>&nbsp;</p>
    <p><strong>Contribution:</strong></p>
    <p>We like to thank TU Dresden/J&ouml;rn Vahland for providing the initial version of this driver.</p>
    <p>&nbsp;</p>
    <p><strong>Manual:</strong>&nbsp;<a href="https://www.inficon.com/v1/attachment/f23367c6-34f1-446a-814a-8327045d0c59">https://www.inficon.com/v1/attachment/f23367c6-34f1-446a-814a-8327045d0c59</a></p>
    <p>&nbsp;</p>
    '''
    
    actions = ["reset_thickness"]
    
    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "IC/5"
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {    "timeout": 1,
                                    "baudrate": 9600,
                                    "bytesize": 8,
                                    "stopbits": 1,
                                    "EOL": chr(6),
                                    }
                   
        self.variables = ["Thickness", "Rate"]
        self.units = ["nm", "A/s"]        
                

    def set_GUIparameter(self):
        GUIparameter = {
                        "Reset thickness": True,
                        # "Reset time": True,
                        "Channel": ["1","2"],
                        }
        return GUIparameter
        
    def get_GUIparameter(self, parameter={}):
        self.init_reset_thickness = parameter["Reset thickness"]
        self.port_string = parameter["Port"]
        self.channel = parameter["Channel"]
        
    """ here semantic standard functions start """    
        
    def initialize(self):
        pass
    
        # model = self.get_model()
        # print(f"This is a: {model}")
         
        # readout = self.get_system_messags()
        # print(f"System Messages: {readout}")
        
    def configure(self):
    
        # This allows to start observing a running experiment without resetting the values
        if self.init_reset_thickness:
            self.reset_thickness()
            
    def call(self):
    
        d = self.get_thickness()
        r = self.get_rate()
        return [d,r]        


    ''' Functions that are introduced by this device class '''
    
    
    def get_model(self):
        """ read the model """
    
        self.port.write('H')  # send hello
        model = self.port.read()
        return model

    def get_system_messages(self):
        """ read system messages """
        
        self.port.write('SG 5')
        messages = self.port.read()
        return messages

    def get_thickness(self, channel = None):
        """ read thickness in nm for the given channel """
        
        if channel is None:
            channel = self.channel
        
        self.port.write("SL 3 %i" % int(channel)) # read thickness
        data = self.port.read()
        d = float(data)*100 # in nm
        return d
        
    def get_rate(self, channel = None):
        """ read rate in A/s for the given channel """
        
        if channel is None:
            channel = self.channel
        
        self.port.write("SL 1 %i" % int(channel)) # read rate
        data = self.port.read()
        r = float(data)
        return r
        
    def reset_thickness(self):
        """ resets the thickness 
            As it is unclear which layer is active in idle mode, we reset the first two layers.
        """
        
        self.port.write("RL 3 1") # reset thickness layer 1
        self.port.read()
        self.port.write("RL 3 2") # reset thickness layer 2
        self.port.read()