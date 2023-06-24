# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2019 Axel Fischer (sweep-me.net)
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
# Device: phyphox


# import python module here as usual
import requests
from collections import OrderedDict

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!

class Device(EmptyDevice):

    description =   """
                    <p><strong>Requirements:</strong></p>
                    <ul>
                    <li>install the phyphox app on your smartphone</li>
                    <li>start the app and choose an experiment</li>
                    <li><strong>allow remote control</strong> via the menu of the experiment</li>
                    <li>your computer must be in the <strong>same wifi</strong> as your smartphone</li>
                    <li>enter the IP address, as shown in the phyphox app, into the 'Port' field</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>The selected measurement must correspond to the selected sensor measurement in phyphox</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Link:</strong></p>
                    <ul>
                    <li>official webpage:&nbsp;<a href="https://phyphox.org/">phyphox.org</a></li>
                    </ul>
                    """
                    

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "phyphox" # short name will be shown in the sequencer
            
        self.timeout = 4 # in seconds
        
        self.measurements = OrderedDict([
                                          ("Acceleration", [
                                                            ("acc_time", "Time", "s"),
                                                            ("accX", "Acceleration x", "m/s^2"),
                                                            ("accY", "Acceleration y", "m/s^2"),
                                                            ("accZ", "Acceleration z", "m/s^2"),
                                                            ("acc", "Acceleration abs.", "m/s^2"),
                                                            ]),
                                                            
                                          ("Magnetic field", [
                                                                ("mag_time", "Time", "s"),
                                                                ("magX", "Magnetic field x", "µT"),
                                                                ("magY", "Magnetic field x", "µT"),
                                                                ("magZ", "Magnetic field x", "µT"), 
                                                                ("mag", "Magnetic field abs.", "µT"),
                                                                ]),
                                                                                                          
                                          ("Gyroscope", [
                                                            ("gyr_time", "Time", "s"),
                                                            ("gyrX", "Gyroscope x", "rad/s"),
                                                            ("gyrY", "Gyroscope y", "rad/s"),
                                                            ("gyrZ", "Gyroscope z", "rad/s"),
                                                            ("gyr", "Gyroscope abs.", "rad/s"),
                                                            ]),
                                                            
                                          ("GPS", [
                                                    ("t", "Time", "s"),
                                                    ("lat", "Latitude", "°"),
                                                    ("lon", "Longitude", "°"),
                                                    ("z", "Altitude", "°"),
                                                    ("zwgs84", "Altitude WGS84", "m"),
                                                    ("v", "Speed", "m/s"),
                                                    ("dir", "Direction", "°"),
                                                    ("dist", "Distance", "m"),
                                                    ("satellites", "Sattelites", ""),
                                                    ("status", "Status", ""),
                                                    ("accuracy", "Accuracy", "°"),
                                                    ("zAccurary", "Accuracy z", "m"),
                                                    ]),
                                                    
                                          ("Pressure", [
                                                         ("p_time", "Time", "s"), 
                                                         ("pressure", "Pressure", "hPa"),
                                                         ]),
                                                         
                                          ("Light", [
                                                         ("illum_time", "Time", "s"), 
                                                         ("illum", "Illumination", "lx"),
                                                         ]),
                                                         
                                        ])

                                        
        # commands can be found here: https://github.com/Staacks/phyphox-experiments                                
                                                    

            
    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        
        GUIparameter = {
                        "Port": "192.168.0.x:8080",
                        "Measurement": list(self.measurements.keys()),
                        }

        return GUIparameter
        
    def get_GUIparameter(self, parameter):
        
        ### get a value of a GUI item that was created by set_GUIparameter()
        self.address = parameter["Port"]
        if not self.address.startswith("http://"):
            self.address = "http://" + self.address
            

        self.topics = [i[0] for i in self.measurements[parameter["Measurement"]]]
        
        self.variables = [i[1] for i in self.measurements[parameter["Measurement"]]]
        
        self.units = [i[2] for i in self.measurements[parameter["Measurement"]]]
        
        self.plottype = [True] * len(self.topics)
        self.savetype = [True] * len(self.topics)
        

    def initialize(self):
        
        url = self.address + "/control?cmd=start"
        ret = requests.get(url=url, timeout=self.timeout).json()
        # print(ret)
        
        
        url = self.address + "/get?" + ("&".join(self.topics))
        data = requests.get(url=url, timeout=self.timeout).json()
        # print(data)

        measuring = data["status"]["measuring"]
        timedRun = data["status"]["timedRun"]
        countDown = data["status"]["countDown"]

        # if measuring == False:
            # self.stop_Measurement("Measurement aborted as phyphox does not acquire data")

        # if timedRun == True:
            # self.stop_Measurement("Measurement aborted as timed measurements are not supported yet.")


    def deinitialize(self):
        url = self.address + "/control?cmd=stop"
        ret = requests.get(url=url, timeout=self.timeout).json()
        # print(ret)
                
    def measure(self):

        url = self.address + "/get?" + ("&".join(self.topics))
        data = requests.get(url=url, timeout=self.timeout).json()
        # print(data)
        
        measuring = data["status"]["measuring"]
        timedRun = data["status"]["timedRun"]
        countDown = data["status"]["countDown"]
        
        self.return_data = []
        
        for topic in self.topics:
            
            if measuring == False:
                self.return_data.append(float('nan'))
            else:
                if topic in data["buffer"]:
                    self.return_data.append(data["buffer"][topic]["buffer"][-1])
                else:
                    self.return_data.append(float('nan'))
    
    def call(self):
    
        return self.return_data
        