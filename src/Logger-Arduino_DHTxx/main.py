# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018-2019 Axel Fischer (sweep-me.net)
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
# Device: Arduino DHT22


from EmptyDeviceClass import EmptyDevice
import time

class Device(EmptyDevice):

    description =   """
                    <p>First steps:</p>
                    <ul>
                    <li>This Device Class comes with an .ino file that must be uploaded to your Arduino using the Arduino IDE (<a href="https://www.arduino.cc">https://www.arduino.cc</a>).</li>
                    <li>You can find the right .ino file via the menu 'Modules&amp;Devices' -&gt; 'Configure' -&gt; navigate to Logger-Arduino_DHTxx -&gt; right-click on your activated version -&gt; Open folder</li>
                    <li>To connect to your Arduino, you need to install the Arduino driver that creates a COM port. Check whether the COM port can be seen in the Windows device manager.</li>
                    <li>Before you <strong>upload the .ino file</strong>, install the Adafruit library for DHT using the Arduino IDE.</li>
                    <li>In some cases, you need to remove the files DHT_U.h and DHT_U.cpp from the DHT library.</li>
                    <li>The .ino file is configured to connect to a DHT22. In case you have a DHT11, you have to change the variable&nbsp;DHTTYPE to 11 before your upload.</li>
                    <li>Default for connecting the DHT sensor is <strong>pin D2</strong>.</li>
                    </ul>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "Arduino DHTxx"
        
        self.variables = ["Humidity", "Temperature"]
        self.units = ["%", "C"]
        self.plottype = [True, True] # True to plot data
        self.savetype = [True, True]  # True to save data
        
        self.port_manager = True  
        self.port_types = ["COM"]
        self.port_properties = { "timeout":3,
                                 "EOL": "\n",
                                }
    
    def initialize(self):
        self.port.read() # read out the initialization string sent by the Arduino

    def measure(self):  
        self.port.write("Read?")

    def call(self):
        if self.port.read() == "Read?":
            pass
        else:
            pass # can be used to add some special routine if the Arduino does not answer
         
        answer = self.port.read()
        humidity, temperature = map(float, answer.split(","))
        return [humidity, temperature]
        
        