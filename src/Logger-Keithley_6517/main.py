# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)

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

# Contribution: We like to thank TU Dresden/Jacob Hille for providing the initial version of this driver.


# SweepMe! device class
# Type: Logger
# Device: Keithley 6517B

from pysweepme.ErrorMessage import error, debug
from pysweepme.EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):

    """
    The driver supports the SCPI command set. It is simplistic driver to call currents.
    """

    description = """
                    <p>This is a simplistic driver to read currents.&nbsp;Other functions can be added on request.</p>
                    <p>&nbsp;</p>
                    <p><strong>Communication:</strong></p>
                    <ul>
                    <li>In order to use GPIB or RS-232, you need to enable the protocol using the instruments menu.</li>
                    <li>GPIB factory default address: 14</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>'Range' can be used to set the upper limit of the expected current measurements. Default is Auto.</li>
                    <li>The option 'Rate' can be used to change the NPLC being 0.01 (Very Fast), 0.1 (Fast), 1.0 (Medium) and 10.0 (Slow)</li>
                    <li>'Average' can be used to set the number of values the instrument takes before returning the averaged value.</li>
                    <li>'Source voltage in V' can be used to set the value of your voltage for SVMI. Can be set between 0 V and 1000 V\n 
                    Resolution for voltages lower than 100 V is 5 mV for voltages greater than 100 V it's 50 mV.</li>
                    <li> "Source voltage limit in V" manually sets the upper limit for the source voltage.</li>
                    <li>Adjust the option 'Line sync' to enable/disable the line sync to your countries power line frequency.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>User's Manual:</strong></p>
                    <p><a href="https://download.tek.com/manual/6517B-900-01B_August_2022_User.pdf">https://download.tek.com/manual/6517B-900-01B_August_2022_User.pdf</a></p>
                    <p><strong>Reference Manual:</strong></p>
                    <p><a href="https://download.tek.com/manual/6517B-901-01E_Aug_2022_Ref.pdf">https://download.tek.com/manual/6517B-901-01E_Aug_2022_Ref.pdf</a></p>
                  """

    def __init__(self):
        EmptyDevice.__init__(self)
        self.shortname = "Keithley 6517B"
        self.variables = ["Current"]
        self.units = ["A"]
        
        self.port_manager = True 
           
        self.port_types = ["GPIB", "COM"]
        
        self.port_properties = {'timeout': 10.0,
                                'baudrate': 9600,
                                'EOL': '\r',
                                }

    def set_GUIparameter(self):
                
        gui_parameter = {
            "Range": [
                "Auto",
                "20 mA",
                "2 mA",
                "200 µA",
                "20 µA",
                "2 µA",
                "200 nA",
                "20 nA",
                "2 nA",
                "200 pA",
                "20 pA",
                "2 pA",
                "200 fA",
                "20 fA",
                "2 fA",
                ],
            "Rate": ['Very Fast', 'Fast', 'Medium', 'Slow'],
            "Average": 1,
            "Source voltage in V": "0.0",
            "Source voltage limit in V": 5.000,
            "Source voltage connection": ["V-SOURCE HI and INPUT HI", "V-SOURCE HI and V-SOURCE LO"],
            "Line sync": True,
            "Perform zero check": False,
            "Use zero correction": False,
            }
        return gui_parameter

    def get_GUIparameter(self, parameter={}):
        self.range = parameter['Range']
        self.rate = parameter['Rate']
        self.average_count = int(parameter['Average'])
        
        if parameter['Source Voltage in V'] == "":
            self.source_voltage = 0.0
        else:
            self.source_voltage = float(parameter['Source voltage in V'])
        self.source_voltage_limit = float(parameter['Source voltage limit in V'])
        self.source_voltage_connection = parameter['Source voltage connection']
        self.line_sync = parameter['Line sync']
        self.perform_zero_check = parameter['Perform zero check']
        self.use_zero_correction = parameter['Use zero correction']
        
        self.mode = "CURR"

    def initialize(self):
    
        # identification = self.get_identification()
        # print("Identification:", identification)

        self.reset()

        self.set_line_sync(self.line_sync)
        
        # Stopping the measurement in case the voltage is set higher than the limit
        if self.source_voltage > self.source_voltage_limit:
            raise Exception(f"Your source voltage value is too high, "
                            f"must be lower than source voltage limit ({self.source_voltage_limit}V)")
        
    def configure(self):

        # Measurement mode
        self.port.write(":CONF:%s" % self.mode)
        
        # Filters
        self.port.write(":SENS:%s:MED:STAT OFF" % self.mode)  # Median filter off
        
        # Averaging method
        if self.average_count == 1:
            self.port.write(":SENS:%s:AVER:STAT OFF" % self.mode)
        else:
            self.port.write(':SENS:%s:AVER:STAT ON' % self.mode)
            self.port.write(':SENS:%s:AVER:TCON REP' % self.mode)
            self.port.write(':SENS:%s:AVER:COUN %i' % (self.mode, self.average_count))

        # Rate
        if self.rate == 'Very Fast':
            self.port.write(':SENS:%s:NPLC 0.01' % self.mode)
        elif self.rate == 'Fast':
            self.port.write(':SENS:%s:NPLC 0.1' % self.mode)
        elif self.rate == 'Medium':
            self.port.write(':SENS:%s:NPLC 1' % self.mode)
        elif self.rate == 'Slow':
            self.port.write(':SENS:%s:NPLC 10' % self.mode)

        # Zero check
        if self.perform_zero_check:
            self.port.write(":SENS:%s:RANG:AUTO OFF" % self.mode)
            
            # Change to 20 pA range
            self.port.write(":SENS:%s:RANG 20E-12" % self.mode)
                      
            self.port.write(':SYST:ZCH ON')
            
            self.port.write(':INIT')
            
        self.port.write(':SYST:ZCH OFF')

        # Zero correction
        if self.use_zero_correction:
            self.port.write(':SYST:ZCOR ON')
        else:
            self.port.write(':SYST:ZCOR OFF')
        
        # Range
        self.range = self.replace_units(self.range)
        if self.range == 'Auto':
            self.port.write(":SENS:%s:RANG:AUTO ON" % self.mode)
        else:
            self.range = self.range.replace("A", "")
            self.port.write("SENS:%s:RANG %s" % (self.mode, self.range))

        # Source Voltage Measure Current        
        self.port.write(":SOUR:VOLT:LIM:STAT ON")
        # Set voltage limit 
        self.port.write(":SOUR:VOLT:LIM %f" % self.source_voltage_limit)
        self.port.write(":SOUR:VOLT %f" % self.source_voltage)
        if self.source_voltage_connection == "V-SOURCE HI and INPUT HI":
            self.port.write(":SOUR:VOLT:MCON ON")

        # Checking for errors occuring during initialize and config
        while True:
            next_error = self.read_error()
            if next_error == '0,"No Error"':
                break
            print(next_error)
            
    def reconfigure(self, parameter={}, keys=[]):

        if 'Source voltage in V' in keys:
            if parameter['Source voltage in V'] == "":
                self.source_voltage = 0.0
            else:
                self.source_voltage = float(parameter['Source voltage in V'])

            self.port.write(":SOUR:VOLT %f" % self.source_voltage)
            self.port.write(":OUTP:STAT ON")

    def poweron(self):
        # Maybe always ON here
        if self.source_voltage != 0:
            self.port.write(":OUTP:STAT ON")

    def poweroff(self):
        self.port.write(":OUTP:STAT OFF")

    def measure(self):
        self.port.write('READ?')
                
    def read_result(self):
        
        result = self.port.read()
        # print("Result:", result)
        # Reading, Timestamp, Status
        
        self.measured_value = float(result.split(",")[0].rstrip("ABCDEFGHIJKLMNOPQRSTUVWXYZ"))

    def call(self):
        return [self.measured_value]

    """ Here, convenience function start """

    @staticmethod
    def replace_units(value: str):

        value = value.replace(" ", "")\
            .replace("f", "e-15")\
            .replace("p", "e-12")\
            .replace("n", "e-9")\
            .replace("µ", "e-6")\
            .replace("m", "e-3")\

        return value

    """ Here, python functions start that wrap the communication commands """

    def get_identification(self):

        self.port.write("*IDN?")
        return self.port.read()

    def reset(self):

        self.port.write("*RST")

    def set_line_sync(self, state):

        state = "ON" if state else "OFF"
        self.port.write(f":SYST:LSYN:STAT {state}")
    
    def read_error(self):

        self.port.write("SYST:ERR?")
        return self.port.read()
