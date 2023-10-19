# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018, 2020 Axel Fischer (sweep-me.net)
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
# Device: Time


import time
import datetime

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    description =   """
                    <p><strong>Variables:</strong></p>
                    <ul>
                    <li>Seconds in s</li>
                    <li>Minutes in min</li>
                    <li>Hours in h</li>
                    <li>Days in d</li>
                    <li>Clock in format 'hh:mm:ss'</li>
                    <li>Date in format 'yyyy/mm/dd'</li>
                    <li>Timestamp is a datetime timestamp</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Zero time on: </strong></p>
                    <ul>
                    <li>initialize: once at the beginning</li>
                    <li>confgure: when entering a branch&nbsp;</li>
                    <li>signin: for each higher variation/repetition in the sequencer</li>
                    </ul>
                    """
                    
    actions = ["zero_time"]  # these functions will be available to be called

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "Time"
        
        self.starttime = time.perf_counter()  # to define it, will be overwritten during the measurement
        
    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Seconds": True,
                        "Minutes": True,
                        "Hours": True,
                        "Days": False,
                        "Clock": False,
                        "Date": False,
                        "Timestamp": True,
                        
                        "Zero time on": ["initialize", "configure", "signin"],
                        }
                        
        return GUIparameter
               
    def get_GUIparameter(self, parameters):

        self.pars = parameters
        
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        
        if self.pars["Seconds"]:
            self.variables.append("Time")
            self.units.append("s")
            self.plottype.append(True)
            self.savetype.append(True)
            
        if self.pars["Minutes"]:    
            self.variables.append("Time")
            self.units.append("min")
            self.plottype.append(True)
            self.savetype.append(True)
        
        if self.pars["Hours"]:
            self.variables.append("Time")
            self.units.append("h")
            self.plottype.append(True)
            self.savetype.append(True)
            
        if self.pars["Days"]:
            self.variables.append("Days")
            self.units.append("d")
            self.plottype.append(True)
            self.savetype.append(True)
        
        if self.pars["Clock"]:
            self.variables.append("Clock")
            self.units.append("")
            self.plottype.append(False)
            self.savetype.append(True)
            
        if self.pars["Date"]:    
            self.variables.append("Date")
            self.units.append("")
            self.plottype.append(False)
            self.savetype.append(True)
        
        if self.pars["Timestamp"]: 
            self.variables.append("Timestamp")
            self.units.append("")
            self.plottype.append(False)
            self.savetype.append(True)
        
 
    def initialize(self):
        if self.pars["Zero time on"] == "initialize":
            self.zero_time()
            
    def configure(self):
        if self.pars["Zero time on"] == "configure":
            self.zero_time()
            
    def signin(self):
        if self.pars["Zero time on"] == "signin":
            self.zero_time()
               
    def call(self):
    
        values = []
       
        duration = time.perf_counter() - self.starttime
        
        if self.pars["Seconds"]:
            seconds = duration
            values.append(seconds)
            
        if self.pars["Minutes"]:    
            minutes = duration / 60.0
            values.append(minutes)
        
        if self.pars["Hours"]:
            hours = duration / 3600.0
            values.append(hours)
            
        if self.pars["Days"]:    
            days = duration / 3600.0 / 24.0
            values.append(days)
            
        
        now = time.localtime()
        
        if self.pars["Clock"]:
            clock = "\'%02d:%02d:%02d\'" % (now[3],now[4],now[5])
            values.append(clock)
            
        if self.pars["Date"]:    
            date = "%04d/%02d/%02d" % (now[0],now[1],now[2])
            values.append(date)
        
        if self.pars["Timestamp"]: 
            timestamp = datetime.datetime.now()
            values.append(timestamp)
            
        
        return values

    
    def zero_time(self):
        self.starttime = time.perf_counter()
        