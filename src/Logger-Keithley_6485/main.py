# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2021 SweepMe! GmbH

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Contribution: We like to thank Shayan Miri A. S. for providing the initial version of this driver.


# SweepMe! device class
# Type: Logger
# Device: Keithley 6485

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!
# If you like to see the source code of EmptyDevice, take a look at the pysweepme package that contains this file

class Device(EmptyDevice):

    description =   """
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Autozero: Switches autozero on or off. Autozero leads to an internal correction regarding temperature shifts. However, it slows down readings.</li>
                    <li>Perform zero check: If checked, a zero check is performed in the 2 nA range that sets the value for the offset correction that can be used checking "Use zero correction".</li>
                    <li>Use zero correction: Must be checked, if the offset correction should be applied that was found using "Perform zero check".</li>
                    </ul>
                    <p><strong>Known issues:</strong></p>
                    <ul>
                    <li>A manually acquired correction value cannot be used in the measurement as the instrument is reset during initialization which overwrites the value.&nbsp;</li>
                    </ul>
                    <p><strong>Range Overflow:</strong></p>
                    <ul>
                    <li>If the measured current exceeds the manually selected range, the instrument will return a value of +9.91e37 and the message "OVERFLOW" will be shown on its display.&nbsp;</li>
                    </ul>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "Keithley 6485"  # short name will be shown in the sequencer
        self.variables = ["Current"]  # define as many variables you need
        self.units = ["A"]  # make sure that you have as many units as you have variables
        
        self.port_manager = True 
           
        self.port_types = ["COM", "GPIB"]

        self.port_properties = {'timeout':10.0,
                                'baudrate':9600,
                                'EOL':'\r',
                                }
            
            
    def set_GUIparameter(self):
                
        GUIparameter = {
                        "Rate": ['Fast', 'Medium', 'Slow'],
                        "Range": ['Auto', '20 mA', '2 mA', '200 µA', '20 µA', '2 µA', '200 nA', '20 nA', '2 nA'],
                        "Average": 1,
                        "": None,
                        "Autozero": True,
                        "Perform zero check": True,
                        "Use zero correction": True,
                        }
        return GUIparameter

    def get_GUIparameter(self, parameter = {}):
        
        self.rate = parameter['Rate']
        self.Range = parameter['Range']
        
        self.average_count = int(parameter['Average'])
        
        self.use_autozero = parameter["Autozero"]
        self.perform_zero_check = parameter["Perform zero check"]
        self.use_zero_correction = parameter["Use zero correction"]
        

    def initialize(self):
        # called only once at the start of the measurement
        
        # self.port.write('*IDN?')
        # result = self.port.read()
        # print(result)
        
        ## Parameter checking
        if self.average_count > 100:
            self.stop_Measurement("The number of averages must be equal or below 100.")
            return False
        
        if self.average_count < 1:
            self.stop_Measurement("The number of averages must be above 0.")
            return False

        self.port.write("*RST")
        # self.port.write(':ARM:COUN 1')
        
    def configure(self):
    
        ## Filters
        self.port.write(':SENS:MED:STAT OFF')
        self.port.write(':SENS:AVER:ADV:STAT OFF')
        
        if self.average_count == 1:
            self.port.write(':SENS:AVER:STAT OFF')
        else:
            self.port.write(':SENS:AVER:STAT ON')
            self.port.write(':SENS:AVER:TCON REP')
            self.port.write(':SENS:AVER:COUN %i' % self.average_count)
     
        ## Rate
        if self.rate == 'Fast':
            self.port.write('CURR:NPLC 0.1')
        elif self.rate == 'Medium':
            self.port.write('CURR:NPLC 1')
        elif self.rate == 'Slow':
            self.port.write('CURR:NPLC 5')
        
        
        # Zero check
        if self.perform_zero_check:
        
            self.port.write("CURR:RANG:AUTO OFF")
        
            # step: change to 2nA range
            self.port.write("CURR:RANG 2e-9")
        
            self.port.write(':SYST:ZCH:STAT ON') 
            self.port.write('INIT')
            self.port.write(':SYST:ZCOR:ACQ')  # Acquire zero correct value.
        
        self.port.write(':SYST:ZCH:STAT OFF')
            
        ## Zero correction      
        # If user needs zero correction on we have to switch it on    
        if self.use_zero_correction:    
           self.port.write(':SYST:ZCOR ON')
        else:
           self.port.write(':SYST:ZCOR OFF')
           
        ## Autozero
        if self.use_autozero:
            self.port.write("SYST:AZER ON")
        else:
            self.port.write("SYST:AZER OFF")

        ## Range
        if self.Range == 'Auto':
            self.port.write("CURR:RANG:AUTO ON")
        elif self.Range.replace(" ", "") == '20mA':
            self.port.write("CURR:RANG 2e-2")
        elif self.Range.replace(" ", "") == '2mA':
            self.port.write("CURR:RANG 2e-3")
        elif self.Range.replace(" ", "") == '200µA':
            self.port.write("CURR:RANG 2e-4")
        elif self.Range.replace(" ", "") == '20µA':
            self.port.write("CURR:RANG 2e-5")
        elif self.Range.replace(" ", "") == '2µA':
            self.port.write("CURR:RANG 2e-6")
        elif self.Range.replace(" ", "") == '200nA':
            self.port.write("CURR:RANG 2e-7")
        elif self.Range.replace(" ", "") == '20nA':
            self.port.write("CURR:RANG 2e-8")
        elif self.Range.replace(" ", "") == '2nA':
            self.port.write("CURR:RANG 2e-9")

    def measure(self):
        # self.port.write('INITiate')
        # self.port.write('ABORt')
        
        # self.port.write(':ARM:COUNt?')
        
        
        # self.port.write(':CONFigure:CURRent:DC')
        # self.port.write(':SENSe:DATA:LATest')
        
        self.port.write('READ?')
        
    def read_result(self):
        
        result = self.port.read()
        self.current = float(result[:result.find(',')-1])

    def call(self):
      
        return [self.current]