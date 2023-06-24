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

# Contribution: We like to thank TU Dresden/Toni Bärschneider for providing the initial version of this driver.

# Acknowledgement: We like to thank PyroScience GmbH for providing the package "FireSting3.py".

# SweepMe! device class
# Type: Logger
# Device: PyroScience FireSting-O2

from FolderManager import addFolderToPATH
addFolderToPATH()


# import python module here as usual
from FireSting3 import FireSting
import numpy as np

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice  # Class comes with SweepMe!


class Device(EmptyDevice):

    description =   """
                    This driver only supports PyroScience devices with firmware < 4.0 (FireStingO2 and Piccolo)
                    
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Select the channels to be activated.</li>
                    <li>Insert channel parameters for the selected channels</li>
                    <li>For devices with only 1 or 2 channels, other channels must be deselected.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Contribution:</strong></p>
                    <p>We like to thank TU Dresden/Toni B&auml;rschneider for providing the initial version of this driver.</p>
                    <p>&nbsp;</p>
                    <p><strong>Acknowledgement:</strong></p>
                    <p>We like to thank PyroScience GmbH for providing the package "FireSting3.py".</p>
                    <p>&nbsp;</p>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "FireSting-O2"  # short name will be shown in the sequencer
        
        # This driver uses the PortManager only to find ports uses the FireSting3 package to create the ports 
        self.port_types = ["COM"]

        self.possible_intensities = np.array([10, 15, 20, 30, 40, 60, 80, 100])
        self.possible_amplifications = np.array([80, 200, 400])
        self.possible_frequencies = np.arange(32000)+1
        self.possible_measure_time = np.arange(200)+1

    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        
        GUIparameter = {
                        }
        for i in range(1, 5):
            GUIparameter["Channel {}".format(i)] = False        
            GUIparameter["Channel {} Name".format(i)] = "Ch%i" % i
            GUIparameter["Channel {} Intensity in %".format(i)] = 20
            GUIparameter["Channel {} Measure time in ms".format(i)] = 100
            GUIparameter["Channel {} Frequency in Hz".format(i)] = 470
            GUIparameter["Channel {} Ampflification".format(i)] = 100
            GUIparameter["Channel {} Temperature in °C".format(i)] = -300 
            GUIparameter["Channel {} Pressure in bar".format(i)] = "-1"
            GUIparameter["Channel {} Salinity in g/L".format(i)] = 0
            GUIparameter[" " * i] = None
        
        return GUIparameter

    def get_GUIparameter(self, parameter):
        
        self.port_string = parameter["Port"]

        # List of selected channel indices
        self.channels = []
        for i in range(1, 5):
            if parameter["Channel {}".format(i)]:
                self.channels.append(i)
        # print(self.channels)
        
        self.measurement_data = {
                                "time": "s",
                                "dPhi": "deg",
                                "status": "str",
                                "umolar": "uM",
                                "mbar": "mbar",
                                "airSat": "%",
                                "percentO2": "%",
                                "pressure": "mbar",
                                "sample_temperature": "°C",
                                "humidity": "%RH",
                                "signal_intensity": "mV",
                                "ambient_light": "mV",
                                "device_temperature": "°C",
                                "led_intensity": "%",
                                "measure_time": "ms",
                                "amplification": "",
                                "frequency": "Hz",
                                "temperature_setting": "°C",
                                "salinity_setting": "g/L",
                                "pressure_setting": "mbar"
                                }
        
        self.channel_names = {}
        self.channel_intensities = {}
        self.channel_meas_times = {}
        self.channel_frequencies = {}
        self.channel_amplifications = {}
        self.channel_temperatures = {}
        self.channel_pressures = {}
        self.channel_salinities = {}

        self.variables = []
        self.units = []
        self.plottype = []  # True to plot data
        self.savetype = []  # True to save data
        
        for i in self.channels:
            self.channel_names[i] = parameter["Channel {} Name".format(i)]
            self.channel_intensities[i] = int(parameter["Channel {} Intensity in %".format(i)])
            self.channel_meas_times[i] = float(parameter["Channel {} Measure time in ms".format(i)])
            self.channel_frequencies[i] = int(parameter["Channel {} Frequency in Hz".format(i)])
            self.channel_amplifications[i] = int(parameter["Channel {} Ampflification".format(i)])
            self.channel_temperatures[i] = float(parameter["Channel {} Temperature in °C".format(i)])
            self.channel_pressures[i] = float(parameter["Channel {} Pressure in bar".format(i)]) if parameter["Channel {} Pressure in bar".format(i)] != "nan" else float(-1)
            self.channel_salinities[i] = float(parameter["Channel {} Salinity in g/L".format(i)])
         
            for key in self.measurement_data:
                self.variables.append(parameter["Channel {} Name".format(i)] + " " + key)
                self.units.append(self.measurement_data[key])
                self.plottype.append(True)
                self.savetype.append(True)
    
    """ Here, semantic standard functions start """
        
    def connect(self):
        
        # print(self.port_string)
        self.firesting = FireSting(self.port_string)  # Comment: It would be nice if we could handover the port to fs in order to use the PortManager

    def disconnect(self):
        pass

    def initialize(self):
        
        # Check whether device has selected channel
        for ch in self.channels:
            if not ch in self.firesting.channels:
                raise Exception("Channel %i cannot be found. Please deselect and try again" % ch)

    def deinitialize(self):        
        self.firesting.disconnect()

    def configure(self):
    
        # Switching on the channels
        for i in self.firesting.channels:
            if i in self.channels:
                self.firesting.channels[i].active = True
            else:
                self.firesting.channels[i].active = False
           
        # previous code:   
        # for i in (np.arange(len(self.channels))+1):
            # self.firesting.channels[i].active = True
    
        for ch in self.channels:
            self.firesting.channels[ch].intensity = int(self.possible_values(self.possible_intensities, self.channel_intensities[ch]))
            self.firesting.channels[ch].measure_time = int(self.possible_values(self.possible_measure_time, self.channel_meas_times[ch]))
            self.firesting.channels[ch].frequency = int(self.possible_values(self.possible_frequencies, self.channel_frequencies[ch]))
            self.firesting.channels[ch].amplification = int(self.possible_values(self.possible_amplifications, self.channel_amplifications[ch]))
            self.firesting.channels[ch].temperature = self.channel_temperatures[ch]
            self.firesting.channels[ch].pressure = self.channel_pressures[ch]
            self.firesting.channels[ch].salinity = self.channel_salinities[ch]
        
    def unconfigure(self):
        # Switching off the channel
        for i in self.firesting.channels:
            self.firesting.channels[i].active = False

    def measure(self):
    
        self.channel_data = []
        self.results = self.firesting.measure()
        # print(self.results)
        
        for ch in self.channels:
            channel_dict = self.results[ch]
            for key in self.measurement_data:
                self.channel_data.append(channel_dict[key])
                         
    def call(self):
           
        return self.channel_data

    """ Here, convenience functions start """

    @staticmethod
    def possible_values(possible, value):
        return possible[np.argmin(np.abs(possible-value))]
