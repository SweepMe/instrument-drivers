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
# Type: Switch
# Device: Arduino StepMotor

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description =   """
                    int dirA = 2;<br>
                    int dirB = 8;<br>
                    int pwmA = 3;<br>
                    int pwmB = 9;<br>
                    """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Arduino StepMotor"
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "EOL": "\n",
            "timeout": 10,  # long timeout to ensure that even larger step procedures can be done
            }

        self.actual_position = 0
        self.actual_value = 0.0
        
        self.commands = {
                        "Angle in deg": 360,
                        "Motor position in steps": 200,
                        }
        
    def set_GUIparameter(self):
        
        GUIparameter =  {
                        "SweepMode" : ["Angle in deg", "Motor position in steps"],
                        "Speed in RPMs": 100,
                        "Steps per round": ["200", "100", "2048"],
                        "Go to start afterwards": True,
                        }
                        
        return GUIparameter
        
    def get_GUIparameter(self, parameter={}):
        
        self.sweepmode = parameter["SweepMode"]
        
        self.variables = [self.sweepmode.split(" [")[0]]
        self.units = [self.sweepmode.split(" [")[-1][:-1]]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data
        
        self.speed = int(parameter["Speed in RPMs"])
        self.steps_per_round = int(parameter["Steps per round"])

        if self.sweepmode == "Angle in deg":
            self.conversion_factor = 360
        else:
            self.conversion_factor = self.steps_per_round 

    def initialize(self):
        # waits for message sent by Arduino upon initialization
        print(self.port.read())
        
    def configure(self):
    
        self.port.write("Speed=%i" % self.speed)
        self.port.read()
        
        self.port.write("Type=%i" % self.steps_per_round)
        self.port.read()

    def apply(self):
        steps_to_go = int(float(self.value) / self.conversion_factor * self.steps_per_round) - self.actual_position
        
        if steps_to_go != 0:
            
            self.port.write("Step=%i" % steps_to_go)
            print(self.port.read())  # read out correct detection of steps to move
            
            print(self.port.read())  # read out the new position that has been set
            self.actual_position += steps_to_go
            
    def call(self):
        return [self.value]
