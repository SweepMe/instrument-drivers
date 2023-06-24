# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018 Axel Fischer (sweep-me.net)
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
# Device: EricssonF5521gw
# Maintainer: Axel Fischer


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)
    
        self.shortname = "GPS"
        
        
        self.variables =["Latitude", "Longitude", "Altitude", "Satellites" , "Horz Dilution"]
        self.units = ["deg", "deg", "m" , "", ""]
        self.plottype = [True, True, True, True, True]
        self.savetype = [True, True, True, True, True]
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = { "baudrate": 9600,
                                 "timeout": 1.0,
                                 "Exception": False,
                                 }
        

        
    # def get_GUIparameter(self, parameter = {}):
        
    def initialize(self):
        self.port.write("Init1 = AT*E2GPSCTL=1,3,1")
        self.port.write("AT*E2GPSNPD")
        
        self.port.write("cat")
        
    def call(self):
        i = 0
        while True:
            i+=1
            answer = self.port.read()
            if answer[0:6] == '$GPGGA':
                #print answer
                data = answer.split(',')
                time = data[1]
                latitude = data[2]
                longitude = data[4]
                Quality = data[6]
                Number_satellites = data[7]
                Horz_dilution = data[8]
                altitude = data[9]
                Height = data[10]
            
                try:
                    # print "Time: %2d:%2d:%2d" % (float(time[0:2])+2.0, float(time[2:4]), float(time[4:6]))
                    # print "Latitude:", latitude
                    # print "Longitude:", longitude
                    # print "Coordinates:", float(latitude[:-9]) + (float(latitude[-9:]) * 60.0)/3600.0, float(longitude[:-9]) + (float(longitude[-9:]) * 60.0)/3600.0
                    # print "Altitude:", altitude
                    # print "Satellites:", Number_satellites
                    # print "Dilution:", Horz_dilution
                    
                    return [float(latitude[:-9]) + (float(latitude[-9:]) * 60.0)/3600.0, float(longitude[:-9]) + (float(longitude[-9:]) * 60.0)/3600.0, float(altitude), int(Number_satellites), float(Horz_dilution)]

                    
                except:
                    pass
                    
            if i > 50:
                return [float('nan'), float('nan'), float('nan'), float('nan'), float('nan')]