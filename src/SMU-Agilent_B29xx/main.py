# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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
# Type: SMU
# Device: Agilent 29xx


from __future__ import annotations

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        super().__init__()

        self.shortname = "Agilent B29xx"

        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]  # True to plot data
        self.savetype = [True, True]  # True to save data

        self.port_manager = True
        self.port_types = ["USB", "GPIB"]

        self.port_properties = {
            # "timeout": 10,
        }

        self.commands = {
            "Voltage [V]": "VOLT",  # deprecated, remains for compatibility
            "Current [A]": "CURR",  # deprecated, remains for compatibility
            "Voltage in V": "VOLT",
            "Current in A": "CURR",
        }

        self.pulse_mode = True  # enables pulsed signal option in GUI

    def set_GUIparameter(self):

        GUIparameter = {
            "SweepMode": ["Voltage in V", "Current in A"],
            "Channel": ["CH1", "CH2"],
            "4wire": False,
            # "RouteOut": ["Front", "Rear"],
            "Speed": ["Very Fast: 0.01NPLC", "Fast: 0.1NPLC", "Medium: 1NPLC", "Slow: 10NPLC"],
            # NPLCs included to transparently allow for user based measurement time estimations
            "Compliance": 100e-6,
            "CheckPulse": False,
            # "PulseMeasStart_in_s": 750e-6, #for use on the B2902B, defined as the delay for measurement start after pulse release;variable not yet implemented
            "PulseOnTime": 1e-3,  # for use on the B2902B, defined as the pulse width time
            "PulseDelay": 0,  # for use on the B2902B, defined as the delay time prior to pulse
            "PulseOffLevel": 0.0,  # bias voltage during pulse-off
            # "Average": 1, # not yet supported
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):
        self.four_wire = parameter['4wire']
        # self.route_out = parameter['RouteOut']
        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']

        self.speed = parameter['Speed']

        # not yet supported
        # self.average = int(parameter['Average'])
        #
        # if self.average < 1:
        #     self.average = 1
        # if self.average > 100:
        #     self.average = 100

        self.device = parameter['Device']
        self.channel = str(parameter['Channel'])[-1]

        self.pulse = parameter['CheckPulse']  # check in GUI is pulse option has been selected
        # self.pulse_meas_time_in_s = parameter['PulseMeasStart_in_s'] #for use on the B2902B, defined as the delay for measurement start after pulse release; variable not yet implemented
        self.ton = float(
            round(float(parameter["PulseOnTime"]), 6))  # for use on the B2902B, defined as the pulse width time
        self.toff = float(parameter["PulseDelay"])  # for use on the B2902B, defined as the delay time prior to pulse
        self.pulseofflevel = parameter['PulseOffLevel']  # bias voltage during pulse-off

    def initialize(self):
        # once at the beginning of the measurement

        # if float(self.pulse_meas_time_in_s) < 750e-6: #variable not yet implemented
        #    raise Exception("High voltage pulses can take as much as 750us to ramp up, measurement might start too early.\nPlease increase pulse measurement (start-)time or modify driver source code after validating your usecase with an Oscillopscope.")
        if float(self.ton) < 1e-3:
            raise Exception(
                "Measurement at 0.01 NPLC requires at least 200us@50Hz PLC, pulse measurement start time is set to 750us minimum.\nThrefore, shortest pulse width is restricted to 1ms to ensure proper measurement at long ramp-up times of high current and voltage values.")

        self.port.write("*RST")

        self.port.write("SYST:BEEP:STAT OFF")  # control-Beep off

        self.port.write(":SYST:LFR 50")  # LineFrequency = 50 Hz

    def configure(self):

        if self.source.startswith("Voltage"):
            self.port.write(":SOUR%s:FUNC:MODE VOLT" % self.channel)
            # sourcemode = Voltage
            self.port.write(":SOUR%s:VOLT:MODE FIX" % self.channel)
            # sourcemode fix
            self.port.write(":SENS%s:FUNC \"CURR\"" % self.channel)
            # measurement mode
            self.port.write(":SENS%s:CURR:PROT %s" % (self.channel, self.protection))
            # Protection with Imax
            self.port.write(":SENS%s:CURR:RANG:AUTO ON" % self.channel)
            # Autorange for current measurement
            self.port.write(":SOUR%s:CURR:RANG:AUTO ON" % self.channel)
            # Autorange for current output


        elif self.source.startswith("Current"):
            self.port.write(":SOUR%s:FUNC:MODE CURR" % self.channel)
            # sourcemode = Voltage
            self.port.write(":SOUR%s:CURR:MODE FIX" % self.channel)
            # sourcemode fix
            self.port.write(":SENS%s:FUNC \"VOLT\"" % self.channel)
            # measurement mode
            self.port.write(":SENS%s:VOLT:PROT %s" % (self.channel, self.protection))
            # Protection with Imax
            self.port.write(":SENS%s:VOLT:RANG:AUTO ON" % self.channel)
            # Autorange for voltage measurement
            self.port.write(":SOUR%s:VOLT:RANG:AUTO ON" % self.channel)
            # Autorange for voltage output

        if self.speed.startswith("Very Fast"):  # newly impplemented to allow for measurements during fast pulses
            self.nplc = "0.01"
        elif self.speed.startswith("Fast"):
            self.nplc = "0.1"
        elif self.speed.startswith("Medium"):
            self.nplc = "1.0"
        elif self.speed.startswith("Slow"):
            self.nplc = "10.0"

        self.port.write(":SENS%s:CURR:NPLC %s" % (self.channel, self.nplc))
        self.port.write(":SENS%s:VOLT:NPLC %s" % (self.channel, self.nplc))

        self.port.write(":SENS%s:CURR:RANG:AUTO:MODE RES" % self.channel)

        # 4-wire sense
        if self.four_wire:
            self.port.write("SENS:REM ON")
        else:
            self.port.write("SENS:REM OFF")

        # Averaging is not yet supported but the below code might help to implement
        """
        # averaging
        self.port.write(":SENS:AVER:TCON REP")   # repeatedly take average
        if self.average > 1:
            self.port.write(":SENS:AVER ON") 
            self.port.write(":SENSe:AVER:COUN %i" % self.average)   # repeatedly take average
        else:
            self.port.write(":SENS:AVER OFF")
            self.port.write(":SENSe:AVER:COUN 1")  
        """

        if self.pulse:
            self.port.write(":FUNC PULS")  # switch to pulse output instead of "DC"
            self.port.write(":PULS:WIDT %s" % self.ton)  # pulse width time
            self.port.write(":PULS:DEL %s" % self.toff)  # delay prior to pulse
            self.port.write(
                ":SOUR%s:FUNC:TRIG:CONT OFF" % self.channel)  # switch off continuous operation of internal trigger
            self.port.write(":SOUR%s:WAIT ON" % self.channel)  # enables to wait for any change of amplitude past pulse
            self.port.write(
                ":SENS%s:WAIT ON" % self.channel)  # enables wait time for start of measurement defined by delay
            self.port.write(":TRIG%s:TRAN:DEL MIN" % self.channel)  # trigger delay hardcoded to 0s
            self.port.write(
                ":TRIG%s:ACQ:DEL 750e-6" % self.channel)  # delay of measurement after pulse release is triggered; takes care of ramp-up
            self.port.write(":TRIG%s:ALL:COUN 1" % self.channel)  # sets trigger count, 1 for single pulse
            self.port.write(":TRIG%s:LXI:LAN:DIS:ALL" % self.channel)  # disable LXI triggering
            self.port.write(":TRIG%s:ALL:SOUR AINT" % self.channel)  # enable internal trigger
            self.port.write(
                ":TRIG%s:ALL:TIM MIN" % self.channel)  # set trigger daly to minimum; not to be mixed up with pulse delay
            self.port.write(":FORM:ELEM:SENS VOLT,CURR,TIME,STAT,SOUR")  # defining the measurement out sizes
            self.port.write(":SYST:TIME:TIM:COUN:RES:AUTO ON")  # activates a counter timer reset
        else:
            self.port.write(":FUNC DC")  # std DC output

        self.port.write(":OUTP%s:LOW GRO" % self.channel)  # FLOating or GROunded GND terminal

    def deinitialize(self):
        if self.four_wire:
            self.port.write("SYST:REM OFF")

        self.port.write(":SENS%s:CURR:NPLC 1" % self.channel)
        self.port.write(":SENS%s:VOLT:NPLC 1" % self.channel)

        # self.port.write(":SENS:AVER OFF")
        # self.port.write(":SENSe:AVER:COUN 1")

    def poweron(self):
        self.port.write(":OUTP%s ON" % self.channel)

    def poweroff(self):
        self.port.write(":OUTP%s OFF" % self.channel)

    def apply(self):

        if self.pulse:
            if self.source.startswith("Voltage"):

                if self.value > 200:
                    raise Exception("Voltage exceeding 200 V maximum pulse capability of device")
                if self.value < -200:
                    raise Exception("Voltage exceeding -200 V maximum pulse capability of device")

                if float(self.protection) > 10.5:
                    raise Exception("Compliance above maximum pulse limit of 3.03 A")
                if float(self.protection) < -10.5:
                    raise Exception("Compliance below maximum pulse limit of -3.03 A")

                if float(self.protection) > 1.515 and self.value > 6:
                    raise Exception("Compliance above maximum limit of 1.515 A for voltages pulses above 6 V")
                if float(self.protection) < -1.515 and self.value < -6:
                    raise Exception("Compliance below maximum limit of -1.515 A for voltages pulses below -6 V")

            if self.source.startswith("Current"):

                if self.value > 10.5:
                    raise Exception("Compliance above maximum pulse limit of 3.03 A")
                if self.value < -10.5:
                    raise Exception("Compliance below maximum pulse limit of -3.03 A")

                if float(self.protection) > 200:
                    raise Exception("Voltage exceeding 200 V maximum pulse capability of device")
                if float(self.protection) < -200:
                    raise Exception("Voltage exceeding -200 V maximum pulse capability of device")

                if float(self.protection) > 6 and self.value > 1.515:
                    raise Exception("Compliance above maximum limit of 6 V for pulse currents above 1.515 A")
                if float(self.protection) < -6 and self.value < -1.515:
                    raise Exception("Compliance below maximum limit of -6 V for pulse currents below -1.515 A")

        else:
            if self.source.startswith("Voltage"):

                if self.value > 210:
                    raise Exception("Voltage exceeding 210 V maximum capability of device")
                if self.value < -210:
                    raise Exception("Voltage exceeding -210 V maximum capability of device")

                if float(self.protection) > 3.03:
                    raise Exception("Compliance above maximum limit of 3.03 A")
                if float(self.protection) < -3.03:
                    raise Exception("Compliance below maximum limit of -3.03 A")

                if float(self.protection) > 1.515 and self.value > 6:
                    raise Exception("Compliance above maximum limit of 1.515 A for voltages above 6 V")
                if float(self.protection) < -1.515 and self.value < -6:
                    raise Exception("Compliance below maximum limit of -1.515 A for voltages below -6 V")

                if float(self.protection) > 0.105 and self.value > 21:
                    raise Exception("Compliance above maximum limit of 0.105 A for voltages above 21 V")
                if float(self.protection) < -0.105 and self.value < -21:
                    raise Exception("Compliance below maximum limit of -0.105 A for voltages below -21 V")

            if self.source.startswith("Current"):

                if self.value > 3.03:
                    raise Exception("Voltage exceeding 3.03 A maximum capability of device")
                if self.value < -3.03:
                    raise Exception("Voltage exceeding -3.03 A maximum capability of device")

                if float(self.protection) > 210:
                    raise Exception("Compliance above maximum limit of 210 V")
                if float(self.protection) < -210:
                    raise Exception("Compliance below maximum limit of -210 V")

                if float(self.protection) > 21 and self.value > 0.105:
                    raise Exception("Compliance above maximum limit of 21 V for currents above 0.105 A")
                if float(self.protection) < -21 and self.value < -0.105:
                    raise Exception("Compliance below maximum limit of -21 V for currents below -0.105 A")

                if float(self.protection) > 6 and self.value > 1.515:
                    raise Exception("Compliance above maximum limit of 6 V for currents above 1.515 A")
                if float(self.protection) < -6 and self.value < -1.515:
                    raise Exception("Compliance below maximum limit of -6 V for currents above -1.515 A")

        value = str("{:.4E}".format(self.value))  # makes sure that self.value fits into SCPI command in terms of length
        if self.pulse:
            self.port.write(":SOUR%s:%s %s" % (
            self.channel, self.commands[self.source], self.pulseofflevel))  # get channel ready at specified values
            self.port.write(
                ":SOUR%s:%s:TRIG %s" % (self.channel, self.commands[self.source], value))  # arming the pulse trigger
            self.port.write(":INIT (@%s)" % self.channel)  # releasing the pulse trigger
        else:
            self.port.write(
                ":SOUR%s:%s %s" % (self.channel, self.commands[self.source], value))  # set output to specified values

    def call(self):

        if self.pulse:
            self.port.write(
                ":FETC:ARR? (@%s)" % self.channel)  # get measured values taken during pulse release out of the memory
        else:
            self.port.write(":MEAS? (@%s)" % self.channel)  # taking a measurement during constant DC output

        answer = self.port.read()

        values = answer.split(",")

        voltage = float(values[0])
        current = float(values[1])

        return [voltage, current]

    # here functions wrapping communication commands start

    def enable_output_protection(self, state: str | bool) -> None:
        """Enables  over voltage / over current protection.

        If the SMU hits the compliance the output will be switched off. This features is a safety feature to prevent
        further voltage or current being applied to the device under test.

        The output protection does not change whether the compliance is active.

        The default after a reset (*RST) of the device is OFF.
        """
        if state is True or state == "ON":
            state = "ON"
        elif state is False or state == "OFF":
            state = "OFF"
        else:
            msg = "State '%s' unknown and cannot be handled." % str(state)
            raise Exception(msg)

        self.port.write(f":OUTP{self.channel}:PROT {state}")