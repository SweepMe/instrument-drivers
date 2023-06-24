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


# SweepMe! device class
# Type: Logger
# Device: Inficon XTM2


from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    '''
    <p><strong>Setup:</strong></p>
    <p>start XTM2 with pressed 0, then type =1, baud =3, IEEE does not matter</p>
    <p>&nbsp;</p>
    <p><strong>Comments:</strong></p>
    <ul>
    <li>Film number is read only once, so please do not change the film during run</li>
    <li>Xtal life is defined as 100% = fresh, 0% =&nbsp; dead in order to synchronize the definition with other QCM device classes.&nbsp;</li>
    </ul>
    '''
    
    actions = ["reset_thickness", "reset_timer"]
    
    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "XTM2"
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {    "timeout": 1,
                                    "baudrate": 9600,
                                    "bytesize": 8,
                                    "stopbits": 1,
                                    "EOL": chr(6),
                                    }
                   
        self.variables = ["Thickness", "Rate", "Tooling", "Density", "Xtal life"]
        self.units = ["nm", "A/s", "%", "g/cm^3", "%"]        
                

    def set_GUIparameter(self):
        GUIparameter = {
                        "Reset thickness": True,
                        # "Reset time": True,
                        "Channel": ["As is"] + ["%i" %i for i in range(1,10,1)],
                        "Set density": False,
                        "Density in g/cm³": "1.3",
                        "Set tooling": False,
                        "Tooling in %": "100.0",
                        }
        return GUIparameter
        
    def get_GUIparameter(self, parameter={}):
        self.port_string = parameter["Port"]
        self.init_reset_thickness = parameter["Reset thickness"]
        
        self.film = parameter["Channel"]
        
        self.set_density = parameter["Set density"]
        self.density = parameter["Density in g/cm³"]
        
        self.set_tooling = parameter["Set tooling"]
        self.tooling = parameter["Tooling in %"]
        
    """ here semantic standard functions start """    
        
    def initialize(self):
    
        self.port.write('H') # send hello
        model = self.port.read()
        
        # if not model.startswith("XTM/2"):
            # self.stopMeasurement = "XTM/2 is not properly connected."
        
    def configure(self):
    
        # This allows to start observing a running experiment without resetting the values
        if self.init_reset_thickness:
            self.reset_thickness()
 
    
        # get the active film
        # active film should not be changed during run
        if self.film != "As is":
            self.set_active_film(self.film)
 
        self.active_film = self.get_active_film()

        if self.set_density:
            self.set_film_density(self.active_film, self.density)
            
        if self.set_tooling:
            self.set_film_tooling(self.active_film, self.tooling)
                
                
    def call(self):
    
        d = self.get_thickness()
        r = self.get_rate()
        tooling = self.get_film_tooling(self.active_film)
        density = self.get_film_density(self.active_film)
        xtal = self.get_xtal()
        
        return [d, r, tooling, density, xtal]


    ''' Functions that are introduced by this device class '''

    def get_active_film(self):
        """ get the active film number as string """
    
        self.port.write("Q 6")
        film = self.port.read()
        return film
        
    def set_active_film(self, film):
        """ set the film """
        
        self.port.write(f"U 6 {str(film)}")
        film = self.port.read()
        
    def open_shutter(self):
        """ set thickness to zero """
         
        self.port.write("R0") 
        self.port.read(1)
        
        
    def close_shutter(self):
        """ set thickness to zero """
         
        self.port.write("R1") 
        self.port.read(1)

    def reset_thickness(self):
        """ set thickness to zero """
         
        self.port.write("R4")     # reset thickness
        self.port.read(1)
        
        
    def reset_timer(self):
        """ set timer to zero """
        
        self.port.write("R5")     # reset timer
        self.port.read(1)

    def get_thickness(self):
        """ read thickness in nm """
        
        self.port.write("S2") # read thickness
        data = self.port.read()
        d = float(data)*100 # in nm
        return d
        
    def get_rate(self):
        """ read rate in A/s """
        
        self.port.write("S1") # read rate
        data = self.port.read()
        r = float(data)
        return r
    
    
    def get_xtal(self):
        """ read xtal life in % where 100 % is fresh and 0% is dead """
    
        self.port.write("S5")
        data = self.port.read()
        xtal = 100 - float(data) # we use Xtal life with 100 % is fresh to have same behavior across all QCM device classes
        return xtal
        
            
    def get_film_tooling(self, film):
        """ read tooling in % of given film """
        
        # Commands only accessible via Query command need currently active film
        self.port.write("Q 0 " + str(film))
        data = self.port.read()
        tooling = float(data)
        return tooling
        
    def set_film_tooling(self, film, value):
        """ set tooling in % of given film """
        
        # Commands only accessible via Update command need currently active film
        self.port.write(f"U 0 {str(film)} {str(value)}")
        data = self.port.read()

        
    def get_film_density(self, film):
        """ read density in g/cm^3 of given film """
    
        # Commands only accessible via Query command need currently active film
        self.port.write("Q 3 " + str(film))
        data = self.port.read()
        density = float(data)
        return density
        
        
    def set_film_density(self, film, value):
        """ set density in g/cm³ of given film """
        
        # Commands only accessible via Update command need currently active film
        self.port.write(f"U 3 {str(film)} {str(value)}")
        data = self.port.read()