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


# SweepMe! driver
# * Module: Logger
# * Instrument: Keithley 6487


from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    description = """
        <p><strong>Usage:</strong></p>
        <ul>
        <li>Voltage source function: Input the voltage in V and select the voltage range and the current limit. To perform a
        voltage sweep, add a Sweep module, configure it, and copy and paste its parameter with brackets from parameter 
        window into the Voltage in V field (rf. <a href="https://wiki.sweep-me.net/wiki/Parameter_system">
        https://wiki.sweep-me.net/wiki/Parameter_system</a>).</li>
        <li>Interlock connection: The Model 6487 has a built-in interlock that works in conjunction with the voltage source. 
        The interlock prevents the voltage source from being placed in operate on the 50V and 
        500V ranges, and optionally on the 10V range, to assure safe operation. To enable the voltage source output,
        pins 1 and 2 of the INTERLOCK connector must be shorted together.</li>
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

        self.shortname = "Keithley 6487"
        self.variables = ["Current"]
        self.units = ["A"]

        self.port_manager = True

        self.port_types = ["COM", "GPIB"]

        self.port_properties = {
            'timeout': 10.0,
            'baudrate': 9600,
            'EOL': '\r',
        }

    def set_GUIparameter(self):

        GUIparameter = {
            "Use voltage source": True,
            "Source voltage in V": "0.0",
            "Source voltage range": ['10 V', '50 V', '500 V'],
            "Source current limit": ['25 µA', '250 µA', '2.5 mA', '25 mA'],
            "": None,
            "Rate": ['Fast', 'Medium', 'Slow'],
            "Current range": ['Auto', '20 mA', '2 mA', '200 µA', '20 µA', '2 µA', '200 nA', '20 nA', '2 nA'],
            "Average": 1,
            " ": None,
            "Autozero": True,
            "Perform zero check": True,
            "Use zero correction": True,
        }
        return GUIparameter

    def get_GUIparameter(self, parameter={}):

        self.use_voltage_source = parameter['Use voltage source']
        self.rate = parameter['Rate']
        self.current_range = parameter['Current range']

        self.source_voltage = parameter['Source voltage in V']
        self.source_voltage_range = parameter['Source voltage range']
        self.source_current_limit = parameter['Source current limit']

        self.average_count = int(parameter['Average'])

        self.use_autozero = parameter["Autozero"]
        self.perform_zero_check = parameter["Perform zero check"]
        self.use_zero_correction = parameter["Use zero correction"]

    def initialize(self):
        # called only once at the start of the measurement

        # self.port.write('*IDN?')
        # result = self.port.read()
        # print(result)

        # Parameter checking
        if self.average_count > 100:
            self.stop_Measurement("The number of averages must be equal or below 100.")
            return False

        if self.average_count < 1:
            self.stop_Measurement("The number of averages must be above 0.")
            return False

        self.port.write("*RST")
        # self.port.write(':ARM:COUN 1')

    def configure(self):

        # Filters
        self.port.write(':SENS:MED:STAT OFF')
        self.port.write(':SENS:AVER:ADV:STAT OFF')

        if self.average_count == 1:
            self.port.write(':SENS:AVER:STAT OFF')
        else:
            self.port.write(':SENS:AVER:STAT ON')
            self.port.write(':SENS:AVER:TCON REP')
            self.port.write(':SENS:AVER:COUN %i' % self.average_count)

        # Rate
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

        # Current range
        if self.current_range == 'Auto':
            self.port.write("CURR:RANG:AUTO ON")
        elif self.current_range.replace(" ", "") == '20mA':
            self.port.write("CURR:RANG 2e-2")
        elif self.current_range.replace(" ", "") == '2mA':
            self.port.write("CURR:RANG 2e-3")
        elif self.current_range.replace(" ", "") == '200µA':
            self.port.write("CURR:RANG 2e-4")
        elif self.current_range.replace(" ", "") == '20µA':
            self.port.write("CURR:RANG 2e-5")
        elif self.current_range.replace(" ", "") == '2µA':
            self.port.write("CURR:RANG 2e-6")
        elif self.current_range.replace(" ", "") == '200nA':
            self.port.write("CURR:RANG 2e-7")
        elif self.current_range.replace(" ", "") == '20nA':
            self.port.write("CURR:RANG 2e-8")
        elif self.current_range.replace(" ", "") == '2nA':
            self.port.write("CURR:RANG 2e-9")

        if self.use_voltage_source:
            # Source voltage range
            if self.source_voltage_range == '10 V':
                self.port.write("SOUR:VOLT:RANG 10")
            elif self.source_voltage_range == '50 V':
                self.port.write("SOUR:VOLT:RANG 50")
            elif self.source_voltage_range == '500 V':
                self.port.write("SOUR:VOLT:RANG 500")

            # Source current limit
            if self.source_current_limit == '25 µA':
                self.port.write("SOUR:VOLT:ILIM 2.5e-5")
            elif self.source_current_limit == '250 µA':
                self.port.write("SOUR:VOLT:ILIM 2.5e-4")
            elif self.source_current_limit == '2.5 mA':
                self.port.write("SOUR:VOLT:ILIM 2.5e-3")
            elif self.source_current_limit == '25 mA':
                if self.source_voltage_range == '10 V':
                    self.port.write("SOUR:VOLT:ILIM 2.5e-2")
                else:
                    raise Exception("Current limit 25 mA is only available for 10 V voltage range.")

            # Apply voltage
            if self.source_voltage != "":
                self.port.write("SOUR:VOLT %f" % float(self.source_voltage))
            else:
                raise Exception("No source voltage specified.")

    def poweron(self):
        if self.use_voltage_source:
            self.port.write("SOUR:VOLT:STAT ON")

    def reconfigure(self, parameters, keys):
        # only source voltage may be reconfigured
        if "Source voltage in V" in keys:
            voltage_value = float(parameters["Source voltage in V"])
            self.port.write("SOUR:VOLT %f" % voltage_value)

    def poweroff(self):
        if self.use_voltage_source:
            self.port.write("SOUR:VOLT:STAT OFF")

    def measure(self):
        self.port.write('READ?')

    def read_result(self):
        result = self.port.read()
        self.current = float(result[:result.find(',') - 1])

    def call(self):
        return [self.current]
    