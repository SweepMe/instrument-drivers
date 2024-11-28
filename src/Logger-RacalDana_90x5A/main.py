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


# SweepMe! driver
# * Module: Logger
# * Instrument: Racal-Dana 9015A/9035A Counter


from pysweepme.EmptyDeviceClass import EmptyDevice
import time


class Device(EmptyDevice):
    description = """<p><strong>Racal-Dana 9000A Series Frequency Counter.</strong></p>
                     <p>Supports both models <strong>9015A</strong> and <strong>9035A</strong>. For models 90x5<strong>-11A</strong>, pulse measurement is implemented.</p>
                     <p><strong>100-500 MHz</strong> measurement only on <strong>Channel C</strong> and exclusively on <strong>9035</strong> models. 
                     The <strong>9015</strong> lacks the corresponding prescaler card, Channel C is left unused here, Channel A and B are limited to <strong>0-100 MHz</strong> for all models.</p>
                     <p>Operating modes that lack a channel specifier can either be used on Channel A or in conjunction with Channel B, depending on the channel setup, but never on Channel B alone (see manual for more details).</p>
                     <p>The <strong>invert option</strong> offers an <strong>additional benefit</strong> besides the quick inversion of the test result, as decribed in the manual (quote): 
                     for <strong>low frequency measurements (below 10 kHz) more resolution can be obtained in a reasonable time</strong> by measuring the period of the signal and deriving the reciprocal via invert function.
                     For e.g. 1 kHz, the remainders will be displayed with 5 digits instead of just 2.</p>

                    """

    def __init__(self):
        EmptyDevice.__init__(self)

        self.shortname = "RD90x5A"

        self.port_manager = True
        self.port_types = ["GPIB"]

        self.port_properties = {
            # timeout should be set to slightly above maximum gate time of 10s to cover all usecases
            "timeout": 13,
            # needed for data retrieving as values are seperated by Carrier Return and Line Feed
            "GPIB_EOLread": "\r\n",
        }

        # this dictionary connects modes to commands. The modes will be displayed to the user in the field 'Mode'
        self.modes = {
            "Frequency Channel A": "F0",
            "Frequency Channel C": "F1",
            "Period Channel A": "F2",
            "Period Average Channel A": "F3",
            "Time Interval": "F4",
            "Time Interval Average": "F5",
            "Totalizer": "F6",
            "Ratio Channel A & B": "F7",
            "Pulse Rise Time": "F4M0",
            "Pulse Fall Time": "F4M1",
            "Pulse Width": "F4M2",
            "Average Pulse Rise Time": "F5M0",
            "Average Pulse Fall Time": "F5M1",
            "Average Pulse Width": "F5M2",
        }
        

        # this dictionary sets the unit of each mode
        self.mode_units = {
            "Frequency Channel A": "Hz",
            "Frequency Channel C": "Hz",
            "Period Channel A": "s",
            "Period Average Channel A": "s",
            "Time Interval": "s",
            "Time Interval Average": "s",
            "Totalizer": "",
            "Ratio Channel A & B": "A/B",
            "Pulse Rise Time": "s",
            "Pulse Fall Time": "s",
            "Pulse Width": "s",
            "Average Pulse Rise Time": "s",
            "Average Pulse Fall Time": "s",
            "Average Pulse Width": "s",
        }
        
        # this dictionary sets the unit of each mode with the invert-function selected
        self.mode_units_inverted = {
            "Frequency Channel A": "s",
            "Frequency Channel C": "s",
            "Period Channel A": "Hz",
            "Period Average Channel A": "Hz",
            "Time Interval": "Hz",
            "Time Interval Average": "Hz",
            "Totalizer": "",
            "Ratio Channel A & B": "B/A",
            "Pulse Rise Time": "1/s",
            "Pulse Fall Time": "1/s",
            "Pulse Width": "Hz",
            "Average Pulse Rise Time": "1/s",
            "Average Pulse Fall Time": "1/s",
            "Average Pulse Width": "Hz",
        }
        
        # this dictionary sets the gate/time multiplier for the timebase
        self.multipliers = {
            "As is": "As is",
            "1e+08 (only for Ratio)": "G+8",
            "1e+07 (T.I.Av., P.Av., Ratio)": "G+7",
            "1e+06 (T.I.Av., P.Av., Ratio)": "G+6",
            "1e+05 (T.I.Av., P.Av., Ratio)": "G+5",
            "1e+04 (T.I.Av., P.Av., Ratio)": "G+4",
            "1e+03 (T.I.Av., P.Av., Ratio)": "G+3",
            "1e+02 (T.I.Av., P.Av., Ratio)": "G+2",
            "1e+01 (Freq., T.I.Av., P.Av., Ratio)": "G+1",
            "1e+00 (Freq., T.I.Av., P.Av.)": "G0",
            "1e-01 (Freq., T.I., P.)": "G-1",
            "1e-02 (Freq., T.I., P.)": "G-2",
            "1e-03 (Freq., T.I., P.)": "G-3",
            "1e-04 (Freq., T.I., P.)": "G-4",
            "1e-05 (Freq., T.I., P.)": "G-5",
            "1e-06 (Freq., T.I., P.)": "G-6",
            "1e-07 (T.I., P.)": "G-7",
            "1e-08 (T.I., P.)": "G-8",
        }
        
        # input configuration
        self.inputconfigs = {
            "Channel A & B seperate": "C0",
            "Channel A & B common": "C1",
            "Test with internal 10 MHz clock": "C2",
        }

        # channel A slope and coupling
        self.slopes_a = {
            "Ch. A pos. slope, DC coupled": "A+D",
            "Ch. A neg. slope, DC coupled": "A-D",
            "Ch. A pos. slope, AC coupled": "A+A",
            "Ch. A neg. slope, AC coupled": "A-A",
        }

        # channel B slope and coupling
        self.slopes_b = {
            "Ch. B pos. slope, DC coupled": "B+D",
            "Ch. B neg. slope, DC coupled": "B-D",
            "Ch. B pos. slope, AC coupled": "B+A",
            "Ch. B neg. slope, AC coupled": "B-A",
        }
        
        # trigger mode channel A
        self.triggermodes_a = {
            "Ch. A, AUTO trigger level at start": "auto",
            "Ch. A, AUTO trigger level before each measurement": "aeach",
            "Ch. A, MANUAL trigger level": "man",
        }
        
        # trigger mode channel B
        self.triggermodes_b = {
            "Ch. B, AUTO trigger level at start": "auto",
            "Ch. B, AUTO trigger level before each measurement": "aeach",
            "Ch. B, MANUAL trigger level": "man",
        }
        
        # minimum auto trigger speed
        self.triggerspeeds = {
            "Standard: 400 Hz Minimum": "T0",
            "Lower: 75 Hz Minimum": "T1",
            "Lowest: 40 Hz Minimum": "T2",
            "Highest: 2 kHz Minimum": "T3",
        }
        
        # input impedance channel A
        self.inputimps_a = {
            "Ch. A 1 MOhm": "E0",
            "Ch. A 50 Ohm 5 V_max (Opt. 06PA only)": "E1",
        }
        
        # input impedance channel B
        self.inputimps_b = {
            "Ch. B 1 MOhm": "E0",
            "Ch. B 50 Ohm 5 V_max (Opt. 06PA only)": "E1",
        }
        
        # display behaviour
        self.displaystates = {
            "No display (fastest reading rate)": "D0",
            "After successful transfer": "D1",
            "Immediately after measurement": "D2",
        }
        


    def set_GUIparameter(self):
        return {
            "Mode": list(self.modes.keys()),
            "Gate/Timer Multiplier": list(self.multipliers.keys()),
            "Input Config": list(self.inputconfigs.keys()),
            "Slope and Coupling Ch. A": list(self.slopes_a.keys()),
            "Slope and Coupling Ch. B": list(self.slopes_b.keys()),
            "Inverting result 1/x": ["Off", "On"],
            "Totalizer Time Period (s)": "1",
            "Trigger Mode Ch. A": list(self.triggermodes_a.keys()),
            "Trigger Mode Ch. B": list(self.triggermodes_b.keys()),
            "Trigger Level Ch. A Voltage (if MANUAL)": "0",
            "Trigger Level Ch. B Voltage (if MANUAL)": "0",
            "Minimum Trigger Speed": list(self.triggerspeeds.keys()),
            "Input Impedance Ch. A": list(self.inputimps_a.keys()),
            "Input Impedance Ch. B": list(self.inputimps_b.keys()),
            "Show results on instrument display": list(self.displaystates.keys()),
            "Overflow handling": ["Set result to 1E+09", "Raise error message"],
        }

    def get_GUIparameter(self, parameter: dict):
        self.mode = parameter["Mode"]
        self.multiplier = parameter ["Gate/Timer Multiplier"]
        self.inputconfig = parameter["Input Config"]
        self.slope_a = parameter["Slope and Coupling Ch. A"]
        self.slope_b = parameter["Slope and Coupling Ch. B"]
        self.invert = parameter["Inverting result 1/x"]
        self.totaltime = int(parameter["Totalizer Time Period (s)"])
        self.triggermode_a = parameter["Trigger Mode Ch. A"]
        self.triggermode_b = parameter["Trigger Mode Ch. B"]
        self.triggerlevel_a = float(parameter ["Trigger Level Ch. A Voltage (if MANUAL)"])
        self.triggerlevel_b = float(parameter ["Trigger Level Ch. B Voltage (if MANUAL)"])
        self.triggerspeed = parameter["Minimum Trigger Speed"]
        self.displaystate = parameter["Show results on instrument display"]
        self.overflowhandling = parameter["Overflow handling"]

        self.port_string = parameter["Port"]

        # here, the variables and units are defined, based on the selection of the user
        # we have as many variables as channels are selected
        if self.invert == "On":
            # if the invert option is selected, we add the channel name to each variable, e.g "Frequency Channel A", plus the "inverted" appendix
            self.variables = [x + " (inverted)" for x in [self.mode]]
            # we add the corresponding units to the measured values in an inverted form
            self.units = [self.mode_units_inverted[self.mode]]
        else:
            # we add the channel name to each variable, e.g "Frequency Channel A"
            self.variables = [self.mode]
            # we add the corresponding units to the measured values
            self.units = [self.mode_units[self.mode]]

        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

    def initialize(self):
        # reset instrument
        self.port.write("R")

    def configure(self):
        # operation mode
        self.port.write("%s" % self.modes[self.mode])
        
        # gate/time multiplier
        self.port.write("%s" % self.multipliers[self.multiplier])
        
        # input configuration
        self.port.write("%s" % self.inputconfigs[self.inputconfig])
        
        # slope and coupling for Channel A and B
        self.port.write("%s" % self.slopes_a[self.slope_a])
        self.port.write("%s" % self.slopes_b[self.slope_b])

        # Minimum trigger speed/frequency
        self.port.write("%s" % self.triggerspeeds[self.triggerspeed])

        ### trigger mode CHANNEL A
        # setting manual trigger level on Channel A and formating it for GPIB command compatibility
        if self.triggermodes_a[self.triggermode_a] == "man":
            if self.triggerlevel_a >= -3.2 and self.triggerlevel_a <= +3.19:
                #force into floating point format with x.xx for GPIB command compatibility
                triglev = f'{self.triggerlevel_a:1.2f}'
            elif self.triggerlevel_a >= -32.0 and self.triggerlevel_a <= +31.9:
                #force into floating point format with xx.x for GPIB command compatibility
                triglev = f'{self.triggerlevel_a:2.1f}'
            elif self.triggerlevel_a >= -320 and self.triggerlevel_a <= +319:
                #force into floating point format with xxx for GPIB command compatibility
                triglev = f'{self.triggerlevel_a:3.0f}'
            elif self.triggerlevel_a < -320 and self.triggerlevel_a > +319:
                msg = "Trigger level needs to be higher than or equal to -320 V and lower than or equal to +319 V maximum."
                raise Exception(msg)
            # send trigger level command to instrument
            self.port.write("LA%s" % triglev)
        else:
            # configure instrument for automatic trigger level detection
            self.port.write("LAA")
            
        #### trigger mode CHANNEL B
        # setting manual trigger level on Channel B and formating it for GPIB command compatibility
        if self.triggermodes_b[self.triggermode_b] == "man":
            if self.triggerlevel_b >= -3.2 and self.triggerlevel_b <= +3.19:
                #force into floating point format with x.xx for GPIB command compatibility
                triglev = f'{self.triggerlevel_b:1.2f}'
            elif self.triggerlevel_b >= -32.0 and self.triggerlevel_b <= +31.9:
                #force into floating point format with xx.x for GPIB command compatibility
                triglev = f'{self.triggerlevel_b:2.1f}'
            elif self.triggerlevel_b >= -320 and self.triggerlevel_b <= +319:
                #force into floating point format with xxx for GPIB command compatibility
                triglev = f'{self.triggerlevel_b:3.0f}'
            elif self.triggerlevel_b < -320 and self.triggerlevel_b > +319:
                msg = "Trigger level needs to be higher than or equal to -320 V and lower than or equal to +319 V maximum."
                raise Exception(msg)
            # send trigger level command to instrument
            self.port.write("LB%s" % triglev)
        else:
            # configure instrument for automatic trigger level detection
            self.port.write("LBA")
        
        # Inverting of result 1/x
        if self.invert == "On":
            self.port.write("I")
            
        # use of display on instrument for showing measurement results
        self.port.write("%s" % self.displaystates[self.displaystate])
        
        ### here we are building the command for making a measurement 
        ### so that we do not have to go through an additional IF statement each time
        ### for running the trigger auto level commands seperately
        
        # if triggermode is set to "aeach", auto triggerlevel (LAA/LAB) is done prior to each measurement (J2)
        if self.triggermodes_a[self.triggermode_a] == "aeach" and self.triggermodes_b[self.triggermode_b] == "aeach":
            self.measurecmd = "LAALBAJ2"
        elif self.triggermodes_a[self.triggermode_a] == "aeach":
            self.measurecmd = "LAAJ2"
        elif self.triggermodes_b[self.triggermode_b] == "aeach":
            self.measurecmd = "LBAJ2"
        else:
            self.measurecmd = "J2"

    def unconfigure(self):
        pass

    def measure(self):
        # in totalizer mode, wait totalizer time period between start and stop of measurement
        if self.mode == "Totalizer":
            # starts measurement procedure
            self.port.write("J2S")
            # waits for time specified in GUI
            time.sleep(self.totaltime)
            # stop measurement
            self.port.write("S")
        else:
            #perform measurement (for all other modes except totalizer)
            self.port.write(self.measurecmd)
        
        self.data = self.port.read()
        
        ### catch data overflow (which is indicated by an capital "O" at the beginning of the result data stream)
        ### and the measurement result of 0 Hz because this is transfered by the instrument as an empty result
        
        ### by integrating both cases into one command, there is just one instead of two IF statement being processed
        ### every time a measurement is taken, saving processing time by scrificing some in the rare case of such an exception
        if self.data.startswith ("O") or self.data == "":
            # adjust 0Hz result because if the measured frequency is exactly 0 Hz, transmitted result is empty
            if self.data == "":
                self.data = 0
            # no need for checking if self.data starts with capital O because SweepMe would not have arrived at this point without
            else:
                if self.overflowhandling.startswith("Set result to"):
                    # in case of overflow, set outlier outside maximum frequency of instrument
                    self.data = "1E+09"
                else:
                    # in case of overflow, raise exception
                    msg = "Result Value Overflow recorded!"
                    raise Exception(msg)
        
    def call(self):
        # hand over measurement results to program
        return [float(self.data)]
