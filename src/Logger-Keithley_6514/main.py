# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)

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


# SweepMe! device class
# Type: Logger
# Device: Keithley 6514

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):

    """
    The driver supports the SCPI command set. It is simplistic driver to call currents.
    """

    description = """
                    <p>This is a simplistic driver to read currents.&nbsp;Reading of voltage, resistance, or charge can be added on request.&nbsp;</p>
                    <p>&nbsp;</p>
                    <p><strong>Communication:</strong></p>
                    <ul>
                    <li>In order to use GPIB or RS-232, you need to enable the protocol using the instruments menu.</li>
                    <li>GPIB factory default address: 14</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>The option 'Rate' can be used to change the NPLC being 0.1 (Fast), 1.0 (Medium), and 10.0 (Slow)</li>
                    <li>'Average' can be used to set the number of values the instrument takes before returning the averaged value.</li>
                    <li>Adjust the option 'Line frequency in Hz' to the frequency of your countries power line frequency.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Manual:</strong></p>
                    <p><a href="https://download.tek.com/manual/6514-901-01(D-May2003)(Instruction).pdf">https://download.tek.com/manual/6514-901-01(D-May2003)(Instruction).pdf</a></p>
                  """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "Keithley 6514"
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
                        "Range": ["Auto"],
                        "Rate": ['Fast', 'Medium', 'Slow'],
                        "Average": 1,
                        "Line frequency in Hz": ["50", "60"],
                        # "Autozero": True,
                        # "Perform zero check": True,
                        # "Use zero correction": True,
                        }
        return gui_parameter

    def get_GUIparameter(self, parameter={}):

        self.range = parameter['Range']
        self.rate = parameter['Rate']
        self.line_frequency = parameter['Line frequency in Hz']
        self.average_count = int(parameter['Average'])

        self.mode = "CURR"

    def initialize(self):

        identification = self.get_identification()
        print("Identification:", identification)

        self.reset()

        self.set_line_frequency(self.line_frequency)

    def configure(self):

        # Measurement mode
        self.port.write(":CONF:%s" % self.mode)
        # self.port.write(":SENS:FUNC:%s" % self.mode)

        # Filters
        self.port.write(':SENS:MED:STAT OFF')  # Median filter off

        if self.average_count == 1:
            self.port.write(':SENS:AVER:STAT OFF')
        else:
            self.port.write(':SENS:AVER:STAT ON')
            self.port.write(':SENS:AVER:TCON REP')
            self.port.write(':SENS:AVER:COUN %i' % self.average_count)

        # Rate
        if self.rate == 'Fast':
            self.port.write(':SENS:%s:NPLC 0.1' % self.mode)
        elif self.rate == 'Medium':
            self.port.write(':SENS:%s:NPLC 1' % self.mode)
        elif self.rate == 'Slow':
            self.port.write(':SENS:%s:NPLC 10' % self.mode)

        """
        # Zero check
        if self.perform_zero_check:
            self.port.write(":SENS:%s:RANG:AUTO OFF" % self.mode)

            # step: change to 2nA range
            self.port.write(":SENS:%s:RANG 2e-9" % self.mode)

            self.port.write(':SYST:ZCH:STAT ON')
            self.port.write('INIT')
            self.port.write(':SYST:ZCOR:ACQ')  # Acquire zero correct value.

        self.port.write(':SYST:ZCH:STAT OFF')

        # Zero correction
        # If user needs zero correction on we have to switch it on
        if self.use_zero_correction:
            self.port.write(':SYST:ZCOR ON')
        else:
            self.port.write(':SYST:ZCOR OFF')

        # Autozero
        if self.use_autozero:
            self.port.write("SYST:AZER ON")
        else:
            self.port.write("SYST:AZER OFF")
        """

        # Range
        if self.range == 'Auto':
            self.port.write(":SENS:%s:RANG:AUTO ON" % self.mode)
        # elif self.Range.replace(" ", "") == '20mA':
        #     self.port.write(":SENS:CURR:RANG 2e-2")
        # elif self.Range.replace(" ", "") == '2mA':
        #     self.port.write(":SENS:CURR:RANG 2e-3")
        # elif self.Range.replace(" ", "") == '200µA':
        #     self.port.write(":SENS:CURR:RANG 2e-4")
        # elif self.Range.replace(" ", "") == '20µA':
        #     self.port.write(":SENS:CURR:RANG 2e-5")
        # elif self.Range.replace(" ", "") == '2µA':
        #     self.port.write(":SENS:CURR:RANG 2e-6")
        # elif self.Range.replace(" ", "") == '200nA':
        #     self.port.write(":SENS:CURR:RANG 2e-7")
        # elif self.Range.replace(" ", "") == '20nA':
        #     self.port.write(":SENS:CURR:RANG 2e-8")
        # elif self.Range.replace(" ", "") == '2nA':
        #     self.port.write(":SENS:CURR:RANG 2e-9")

        # if self.read_error_count() > 0:
            # print("Errors after configure:", self.read_all_errors())

    def measure(self):
        # self.port.write('INITiate')
        # self.port.write('ABORt')
        
        # self.port.write(':ARM:COUNt?')

        # self.port.write(':CONFigure:CURRent:DC')
        # self.port.write(':SENSe:DATA:LATest')
        
        self.port.write('READ?')
        
    def read_result(self):
        
        result = self.port.read()
        # print("Result:", result)
        # Reading, Timestamp, Status
        self.measured_value = float(result.split(',')[0])

    def call(self):
        return [self.measured_value]

    """ Here, python functions start that wrap the communication commands """

    def get_identification(self):

        self.port.write("*IDN?")
        return self.port.read()

    def reset(self):

        self.port.write("*RST")

    def set_line_frequency(self, frequency):

        self.port.write(":SYST:LFR %i" % int(frequency))

    def set_nplc(self, nplc):

        nplc = float(nplc)
        nplc = max(nplc, 0.01)
        nplc = min(nplc, 10.0)

        self.port.write(":SENS:%s:NPLC %1.2f" % (self.mode, nplc))

    def read_error(self):

        self.write("SYST:ERR?")
        return self.port.read()

    def read_error_count(self):

        self.write("SYST:ERR:COUN?")
        return int(self.port.read())

    def read_all_errors(self):

        self.write("SYST:ERR:ALL?")
        return self.port.read()
