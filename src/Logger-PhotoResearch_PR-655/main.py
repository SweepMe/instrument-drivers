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

# Parts of this code are based on the file pr.py from Pyschopy package
# https://github.com/psychopy/psychopy/blob/release/psychopy/hardware/pr.py
# Permission to use this file in this driver has been granted by Jonathan Peirce
# in January 2021 if this driver is released under MIT license.


# SweepMe! driver
# Type: Logger
# Device: Photo Research PR-655


from ErrorMessage import error, debug # comes with pysweepme

from EmptyDeviceClass import EmptyDevice # comes with pysweepme

import numpy as np
import time

class Device(EmptyDevice):


    description =   """
                    <p>This driver is compatible with PR-655 and PR-670 SpectraScan</p>
                    <p>&nbsp;</p>
                    <p><strong>Communication:</strong></p>
                    <ul>
                    <li>Driver uses a default baudrate of 112500.</li>
                    <li>Make sure the PR-655 is not in PR-650 legacy mode</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Select the measurement options that should be retrieved for each measurement.</li>
                    <li>If "Luminance" is returned by several measurement options, it will be returned only once.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Measurement options:</strong></p>
                    <ul>
                    <li>CIE 1931 xy -&gt; returns "Luminance", "CIE 1931 x", "CIE 1931 y"</li>
                    <li>CIE 1931 Tristimulus -&gt; returns&nbsp;"Tristim 1", "Tristim 2", "Tristim 3"</li>
                    <li>CIE 1976 uv -&gt; returns "Luminance",&nbsp;"CIE 1976 u", "CIE 1976 v"</li>
                    <li>Color temperature -&gt; "Luminance",&nbsp;"Color temperature", "Color deviation CIE 1976"</li>
                    <li>Spectrum -&gt;&nbsp;"Peak wavelength", "Integrated power", "Integrated photons", "Wavelength", "Intensity"</li>
                    <li>CIE 1960 xy -&gt; "Luminance", "CIE 1960 x", "CIE 1960 y"</li>
                    </ul>
                    <p>&nbsp;</p>
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "PR-655" # short name will be shown in the sequencer
 
        self.port_manager = True 
           
        self.port_types = ["COM"]
        
        self.port_properties = {
                                  "timeout": 5,
                                  "baudrate": 115200,  #9600
                                  "parity": "N",
                                  "stopbits": 1,
                                  "EOLwrite": '',  # we don't use a terminator for sending characters as this handled in send_message method
                                  "EOLread": '\r\n',
                                  "delay": 0.1, # we might have to add a delay for the PR-650 
                                }
            

        self.model = None  # get this from the device later
        
        self._last_results = {}

        # 1 status, units, Photometric brightness, CIE 1931 x,y 
        self._last_results["Luminance"]  = None
        self._last_results["CIE 1931 x"] = None
        self._last_results["CIE 1931 y"] = None    
        
        # 2 status, units, CIE 1931 Tristimulus Values
        self._last_results["Tristim 1"]  = None
        self._last_results["Tristim 2"]  = None
        self._last_results["Tristim 3"]  = None
        
        # 3 status, units, Photometric brightness, CIE 1976 u’, v’ 
        self._last_results["Luminance"]  = None
        self._last_results["CIE 1976 u"] = None
        self._last_results["CIE 1976 v"] = None 
        
        # 4 status, units, Photometric brightness, Correlated Color Temperature, Deviation from Planck's Locus in 1960 u,v units
        self._last_results["Luminance"]  = None
        self._last_results["Color temperature"] = None
        self._last_results["Color deviation CIE 1976"] = None
        
        # 5 status, units, Peak Wavelength, Integrated Power, Integrated Photon, WL, Spectral Data at each WL
        self._last_results["Peak wavelength"]  = None
        self._last_results["Integrated power"] = None
        self._last_results["Integrated photons"] = None
        self._last_results["Wavelength"] = None
        self._last_results["Intensity"] = None
        
        # 6 status, units, Photometric brightness, CIE 1931 x, y, CIE 1976 u’, v’ 
        self._last_results["Luminance"]  = None
        self._last_results["CIE 1931 x"] = None
        self._last_results["CIE 1931 y"] = None    
        self._last_results["CIE 1976 u"] = None
        self._last_results["CIE 1976 v"] = None 
        
        # 7 status, units, Photometric brightness, CIE 1960 x, y 
        self._last_results["Luminance"]  = None
        self._last_results["CIE 1960 x"] = None
        self._last_results["CIE 1960 y"] = None 
           
    def set_GUIparameter(self):
    
        GUIparameter = {
        
                        "Exposure time in ms": "100",
                        "Average": "1",
                        "CIE observer in °": ["2", "10"],
                        
                        "": None,  # empty line
                        "Measurement": None,
                        
                        "CIE 1931 xy": True,
                        "CIE 1931 Tristimulus": False,
                        "CIE 1976 uv": False,
                        "Color temperature": False,
                        "Spectrum": True,
                        "CIE 1960 xy": False

                        }

        return GUIparameter

    def get_GUIparameter(self, parameter):

        self.exposure_time_ms = int(float((parameter["Exposure time in ms"])))
        self.average = int(float(parameter["Average"]))
        self.CIE_observer = int(parameter["CIE observer in °"])
        
        # self.port_properties["Timeout"] = max(10, self.exposure_time_ms/1000.0 * self.average + 5)  # Timeout depends on exposure time and averages, but is at least 10 s
        
        self.take_CIE1931xy = parameter["CIE 1931 xy"]
        self.take_tristim = parameter["CIE 1931 Tristimulus"]
        self.take_CIE1976uv = parameter["CIE 1976 uv"]
        self.take_color_temperature = parameter["Color temperature"]
        self.take_spectrum = parameter["Spectrum"]
        self.take_CIE1960xy = parameter["CIE 1960 xy"]
                        
        self.variables = []
        self.units = []
        self.plottype = []
        self.savetype = []
        
        
        if self.take_CIE1931xy:
            
            self.variables += ["Luminance", "CIE 1931 x", "CIE 1931 y"]
            self.units += ["cd/m²", "", ""]
            self.plottype += [True, True, True]
            self.savetype += [True, True, True]
            
        if self.take_tristim:
        
            self.variables += ["Tristim 1", "Tristim 2", "Tristim 3"]
            self.units += ["", "", ""]
            self.plottype += [True, True, True]
            self.savetype += [True, True, True]
            
        if self.take_CIE1976uv:
        
            if not "Luminance" in self.variables:
                self.variables += ["Luminance"]
                self.units += ["cd/m²"]
                self.plottype += [True]
                self.savetype += [True]
        
            self.variables += ["CIE 1976 u", "CIE 1976 v"]
            self.units += ["", ""]
            self.plottype += [True, True]
            self.savetype += [True, True]
            
        if self.take_color_temperature:
        
            if not "Luminance" in self.variables:
                self.variables += ["Luminance"]
                self.units += ["cd/m²"]
                self.plottype += [True]
                self.savetype += [True]
        
            self.variables += ["Color temperature", "Color deviation CIE 1976"]
            self.units += ["K", ""]
            self.plottype += [True, True]
            self.savetype += [True, True]
                
        if self.take_spectrum:
        
            self.variables += ["Peak wavelength", "Integrated power", "Integrated photons", "Wavelength", "Intensity"]
            self.units += ["nm", "W", "", "nm", "cd"]
            self.plottype += [True, True, True, True, True]
            self.savetype += [True, True, True, True, True]
            
        if self.take_CIE1960xy:
        
            if not "Luminance" in self.variables:
                self.variables += ["Luminance"]
                self.units += ["cd/m²"]
                self.plottype += [True]
                self.savetype += [True]
            
            self.variables += ["CIE 1960 x", "CIE 1960 y"]
            self.units += ["", ""]
            self.plottype += [True, True]
            self.savetype += [True, True]

        
    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
            
        self.start_remote_mode()
    
        self.model = self.get_model()
        
        if not self.model:
            raise Exception("Unable to retrieve the model name")
        else:
            print("PR-600 model:", self.model)
            
        # if self.model == "PR-650":    
            ##set command to make sure using right units etc...
            # reply = self.send_message('s01,,,,,,01,1')
            
        # fw_version = self.get_software_version()
        # print("Firmware version:", fw_version)
        
        self.set_photometric_units(1)  # Metric (SI) units

    def initialize(self):
        pass
    
    def deinitialize(self):
        self.end_remote_mode()
        
    def configure(self):
    
        # Exposure time
        self.set_exposure_time(self.exposure_time_ms)
    
        # Average
        self.set_average(self.average)
        
        # CIE observer
        self.set_CIE_observer(self.CIE_observer)
        
                                
    def measure(self):
        self.take_measurement()
        
    def request_result(self):
        """ 'request_result' can be used to ask an instrument to send data """
        pass
        
    def read_result(self):
    
        # The get_functions used here populate self._last_results which is used
        # in 'call' to create the list of returned variables
    
        self.results = []

        # CIE1931xy
        if self.take_CIE1931xy:
            self.get_last_CIE1931xy()
            
        # Tristim
        if self.take_tristim:
            self.get_last_tristim()
            
        # CIE1976uv
        if self.take_CIE1976uv:
            self.get_last_CIE1976uv()
            
        # Color temperature
        if self.take_color_temperature:
            self.get_last_color_temperature()

        # Spectrum
        if self.take_spectrum:
            self.get_last_spectrum()

        # CIE1960xy
        if self.take_CIE1960xy:
            CIEuv = self.get_last_CIE1960xy()
        
       
    def call(self):
     
        results = []
        for var in self.variables:
            if var in self._last_results:
                results.append(self._last_results[var])
        
        return results
   
       
    def send_message(self, message, timeout=1.0):
        """Send a command to the photometer and wait an allotted
        timeout for a response (Timeout should be long for low
        light measurements)
        """

        # self.port.port.reset_input_buffer()

        # Method 1
        for char in message:
            self.port.write(char)
            self.port.port.flush()   
        self.port.write('\r')

        # time.sleep(0.1)  # PR650 gets upset if hurried!

        # get feedback (within timeout limit)
        self.port.port.timeout = timeout

        if message in ('D5', 'M5'): # we need a spectrum which will have multiple lines
            
            w = []  # Wavelengths
            p = []  # Power values
        
            reply = []
            reply += self.port.read().split(",")  # reading the first line with the error code and some parameters

            # Reading the spectra
            for i in range(101):
                vals = self.port.read().split(",")
                w.append(float(vals[0]))
                p.append(float(vals[1]))
                
            reply.append(np.asarray(w))
            reply.append(np.asarray(p))
            
        else:
            reply = self.port.read()
            
                
        return reply


    def start_remote_mode(self):
        """Sets the instrument into remote mode
        """
        reply = self.send_message('PHOTO', timeout=10.0)
        
        return reply
        
    def end_remote_mode(self):
        """Puts the instrument back into normal mode
        """
        self.port.write('Q')
        
    def get_serial_number(self):
        """Returns the serial number
        """
        reply = self.send_message('D110')  # returns errCode, message
        return reply.split(',')[-1]  # last element

    def get_model(self):
        """Returns the model (e.g. 'PR-655' or 'PR-670')
        """
        reply = self.send_message('D111')  # returns errCode, message
        return reply.split(',')[-1]  # last element
        
    def get_software_version(self):
        """Returns the Software/firmware version
        """
        reply = self.send_message('D114')  # returns errCode, message
        return reply.split(',')[-1]  # last element


    def set_exposure_time(self, value):
        """Sets the exposure time in ms
        """
        
        value = int(value)
        
        if self.model == "PR-650" and value > 6000:  # model PR-650 
            value = 6000 
        elif self.model == "PR-670" and value > 30000:  # model PR-670
            value = 30000  
        elif value < 6:
            value = 6
        
        reply = self.send_message('SE%i' % value)  
        return reply
        
        
    def set_sensitivity_mode(self, mode):
        """Sets the sensitivity mode (PR-670 only)
        """
        
        reply = self.send_message('SH%i' % int(mode))  
        return reply
        
    def set_average(self, value):
        """Sets the number of cycles for averaging
        """
        
        value = int(value)
        
        if value > 99:
            value = 99
        elif value < 1:
            value = 1
        
        reply = self.send_message('SN%i' % value)  
        return reply
        
    def set_CIE_observer(self, value):
        """Sets the CIE observer mode
            2: 2°
            10: 10°
        """
                
        value = int(value)
        
        if value == 2:
            pass
        elif value == 10:
            pass
        else:
            raise Exception("CIE observer value must be 2 for 2° or 10 for 10°")
        
        reply = self.send_message('SO%i' % value)  
        return reply
        
        
    def set_photometric_units(self, mode):
        """Sets photometric units
            0 = English
            1 = Metric (SI)
        """

        reply = self.send_message('SU%i' % int(mode))  
        return reply

    def set_backlight_level(self, value):
        """Sets LCD backlight level
           Value in % ranging from 0 to 100
        """
        
        value = int(value)
        
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        
        reply = self.send_message('B%i' % value)
        
    
    def take_measurement(self, timeOut=30.0):

        """Trigger a measurement
        """


        # remains here for creating PR650 driver later
        """
        if self.type == "PR650":
            

            reply = self.send_message('m0', timeOut)  # measure and hold data
            # using the hold data method the PR650 we can get interogate it
            # several times for a single measurement

            if reply == self.codes['OK']:
                raw = self.send_message('d2')
                xyz = raw.split(',')  # parse into words
                lastQual = str(xyz[0])
                if self.codes[lastQual] == 'OK':
                    self.lastLum = float(xyz[3])
                else:
                    self.lastLum = float('nan')
        """

        reply = self.send_message('M0', timeout=30)

       
        
    def get_CIE1931xy(self, cmd="M1"):
        """trigger a measurement and return CIE1931 x,y coords
        
        Results:
            float: Luminance in cd/m²
            float: CIE 1931 x
            float: CIE 1931 y
        """
        
        result = self.send_message(cmd, timeout=30)
        values = list(map(float, result.split(',')[2:]))
        self._last_results["Luminance"]  = values[0]
        self._last_results["CIE 1931 x"] = values[1]
        self._last_results["CIE 1931 y"] = values[2]
        return values

    def get_last_CIE1931xy(self):
        """Fetches the last CIE 1931 x,y coords

        Results:
            float: Luminance in cd/m²
            float: CIE 1931 x
            float: CIE 1931 y
        """
     
        return self.get_CIE1931xy(cmd="D1")
        
           
    def get_tristim(self, cmd = 'M2'):
        """trigger a measurement and return CIE 1931 Tristimulus values

        :returns:
            list: status, units, Tristimulus Values
        """

        result = self.send_message(cmd, timeout=30)
        values = list(map(float, result.split(',')[2:]))
        self._last_results["Tristim 1"] = values[0]
        self._last_results["Tristim 2"] = values[1]
        self._last_results["Tristim 3"] = values[2]
        return values
        
    def get_last_tristim(self):
        """Fetches the last CIE 1931 Tristimulus values

        :returns:
            list: status, units, Tristimulus Values
        """
        return self.get_tristim(cmd='D2')
        
        
    def get_CIE1976uv(self, cmd='M3'):
        """trigger a measurement and return CIE1976 u,v coords
        
        Results:
            float: Luminance in cd/m²
            float: CIE 1976 u
            float: CIE 1976 v
        """
        
        result = self.send_message(cmd, timeout=30)
        values = list(map(float, result.split(',')[2:]))
        self._last_results["Luminance"]  = values[0]
        self._last_results["CIE 1976 u"] = values[1]
        self._last_results["CIE 1976 v"] = values[2]
        return values

    def get_last_CIE1976uv(self):
        """Fetches the last CIE 1976 u,v coords

        :returns:
            list: status, units, Photometric brightness, u, v
        """
        return self.get_CIE1976uv(cmd='D3')
        
        
    def get_color_temperature(self, cmd='M4'):
        """trigger a measurement and return color temperature
        
        Results:
            float: Luminance in cd/m²
            float: Color temperature in K
            float: Color deviation from Planckian locus in CIE 1976 u
            float: Color deviation from Planckian locus in CIE 1976 v 
        """

        result = self.send_message(cmd, timeout=30)
        values = list(map(float, result.split(',')[2:]))
        self._last_results["Luminance"] = values[0]
        self._last_results["Color temperature"] = values[1]
        self._last_results["Color deviation CIE 1976"] = values[2]
        return values
      
    def get_last_color_temperature(self):
        """Fetches the color temperature and other parameters

        Results:
            float: Luminance in cd/m²
            float: Color temperature in K
            float: Color deviation from Planckian locus in CIE 1976 u
            float: Color deviation from Planckian locus in CIE 1976 v 
        """
        return self.get_color_temperature(cmd='D4')
        
        
                 
    def get_spectrum(self, cmd='M5'):
        """Convenience function to trigger a measurement and
        return the current power spectrum
        
        If you need to retrieve multiple values, it is more efficient to use
        take_measurement and then call get_last... functions
        """
        
        # if self.model == "PR650":
            # raw = self.send_message('d5')
        
        result = self.send_message(cmd, timeout = 30)[2:]  # return first values as string, and spectra is already correctly formatted
        self._last_results["Peak wavelength"] = float(result[0])
        self._last_results["Integrated power"] = float(result[1])
        self._last_results["Integrated photons"] = float(result[2])
        self._last_results["Wavelength"] = result[3]
        self._last_results["Intensity"] = result[4]
        return [self._last_results["Peak wavelength"], self._last_results["Integrated power"], self._last_results["Integrated photons"], self._last_results["Wavelength"], self._last_results["Intensity"]]
              
        
    def get_last_spectrum(self):
        """Retrieves the spectrum from the last call to ``.measure()``
        """
        
        return self.get_spectrum(cmd='D5')
        
    
    def get_CIE1960xy(self, cmd='M7'):
        """trigger a measurement and return CIE1960 x,y coords
        
        Results:
            float: Luminance in cd/m²
            float: CIE 1960 x
            float: CIE 1960 y
        """
        
        result = self.send_message(cmd, timeout=30)
        values = list(map(float, result.split(',')[2:]))
        self._last_results["Luminance"] = values[0]
        self._last_results["CIE 1960 x"] = values[1]
        self._last_results["CIE 1960 y"] = values[2]
        return values
        
            
       
    def get_last_CIE1960xy(self):
        """Fetches the last CIE 1960 x,y coords

        Results:
            float: Luminance in cd/m²
            float: CIE 1960 x
            float: CIE 1960 y
        """
        return self.get_CIE1960xy(cmd='D7')


    def parse_spectrum_output(self, rawStr):
        """Parses the strings from the PR650 as received after sending
        the command 'd5'.
        The input argument "rawStr" can be the output from a single
        phosphor spectrum measurement or a list of 3 such measurements
        [rawR, rawG, rawB].
        """

        if len(rawStr) == 3:
            RGB = True
            rawR = rawStr[0][2:]
            rawG = rawStr[1][2:]
            rawB = rawStr[2][2:]
            nPoints = len(rawR)
        else:
            RGB = False
            nPoints = len(rawStr)
            raw = rawStr[2:]

        nm = []
        if RGB:
            power = [[], [], []]
            for n in range(nPoints):
                # each entry in list is a string like this:
                thisNm, thisR = rawR[n].split(',')
                thisR = thisR.replace('\r\n', '')
                thisNm, thisG = rawG[n].split(',')
                thisG = thisG.replace('\r\n', '')
                thisNm, thisB = rawB[n].split(',')
                thisB = thisB.replace('\r\n', '')
                exec('nm.append(%s)' % thisNm)
                exec('power[0].append(%s)' % thisR)
                exec('power[1].append(%s)' % thisG)
                exec('power[2].append(%s)' % thisB)
        else:
            power = []
            for n, point in enumerate(rawStr):
                # each entry in list is a string like this:
                thisNm, thisPower = point.split(',')
                nm.append(thisNm)
                power.append(thisPower.replace('\r\n', ''))

        return np.asarray(nm), np.asarray(power)
        





"""
Data Code Description 
0 status (Write to disk most recent, unsaved, measurement) 
1 status, units, Photometric brightness, CIE 1931 x,y 
2 status, units, CIE 1931 Tristimulus Values 
3 status, units, Photometric brightness, CIE 1976 u’, v’ 
4 status, units, Photometric brightness, Correlated Color Temperature, Deviation from Planck's Locus in 1960 u,v units 
5 status, units, Peak Wavelength, Integrated Power, Integrated Photon, WL, Spectral Data at each WL 
6 status, units, Photometric brightness, CIE 1931 x, y, CIE 1976 u’, v’ 
7 status, units, Photometric brightness, CIE 1960 x, y 
8 status, Raw (uncorrected) light per pixel 
9 status, Raw (uncorrected) Dark Current per pixel 
11 status, units, Scotopic Brightness 
12 status, units, Photometric brightness, CIE 1931 x, y, CIE 1960u, v 
13 status, Gain description, exposure time in milliseconds 
14 status, Sync mode description, sync period in milliseconds 
110 status, Instrument Serial Number 
111 status, Instrument Name 
112 status, Number of Accessories, Number of Apertures 
114 status, Software Version 
116 status, Accessory List 
117 status, Aperture List 
120 status, Hardware configuration 
401 status, Number of stored measurements in RAM 
402 status, Directory of stored measurements in RAM 
411 status, List of files in SD Card and number of stored measurements per file. 
412 filename ,status, Directory of stored measurements in file "filename" in SD card. 
502 status, Current System Timing & Environment Info. 
503 status, Stored System Timing & Environment Info. 
601 status, Current Setup Report – comma delimited 
602 status, Current Setup Report, Verbose
"""
