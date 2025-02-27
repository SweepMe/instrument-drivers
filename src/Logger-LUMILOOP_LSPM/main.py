# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024-2025 SweepMe! GmbH (sweep-me.net)
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
# * Instrument: LUMILOOP LSPM


# TODO: How to distinguish between LSPM1.x and LSPM2.x, e.g. when they have same serial number

import numpy as np
import time

from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug


class Device(EmptyDevice):

    description = """
<h3>LUMILOOP LSPM power meter</h3>
<p>This SweepMe! driver communicates with a LSPM power meter from LUMILOOP. If you need support for a LSProbe please let us know and we can create a new instrument driver.<br /><br />The driver was created with&nbsp;TCP server version 20240718.<br /></p>
<p><strong>Communication</strong></p>
<ul>
<li>First, install the LUMILOOP application. You can find all downloads here:<br /><a href="https://lumiloop.de/support/documents-and-downloads/">https://lumiloop.de/support/documents-and-downloads/</a></li>
<li>Next, please copy your calibration files to the cal folder of the LUMILOOP application, for example.<br />C:\Program Files (x86)\LUMILOOP\cal\lspm<br />The calibration files should match your LSPM version and serial number. For example, the folder of your calibration files could have the name&nbsp;2v0sn11 if you use version 2.0 and have a device with serial number 11.</li>
<li>Start the LUMILOOP TCP server. It should indicate that calibration files have been found.</li>
<li>You can run the LUMILOOP GUI application to check the connection to the device. The LUMILOOP GUI application also allows to create a virtual device. Please note that a virtual device must be registered with a serial number for which calibration files are available.</li>
<li>The SweepMe! driver communicates with&nbsp;the LUMILOOP TCP server which must always be running.</li>
<li>Register a VISA resource using a raw socket port. This can be done for example with NI MAX that comes with the installation of the NI VISA runtime. If you have a different VISA runtime installed, there will be other tools to register a TCPIP resource. A valid resource would be:<br />TCPIP0::127.0.0.1::10001::SOCKET<br />where port 10001 is typically used for LSPM devices and 127.0.0.1 is the localhost IP that must be used if SweepMe! and the LUMILOOP TCP server run on the same computer.</li>
<li>Enter the serial number of your device into the Parameters section of the driver.<br /><br /></li>
</ul>
<p><strong>Usage</strong></p>
<ul>
<li>Operation modes are described in the User manual. Mode 1 is a convenience mode that automatically switches between the two detectors at the crossover frequency, typically recommeded if you like to span a large range of frequencies.</li>
<li>The power meter needs to know at which frequency the detected signal is working. Therefore, the compensation frquency must be entered. This frequency is the frequency at which the frequency dependent calibration correction is applied. In case you are sweeping the frequency, you can use the Parameter syntax {...} to handover a value from another module, e.g. the sweep value of a signal generator being a frequency.</li>
<li>Select the channels that should be read out.</li>
<li>The crossover frequency is the one at which the detector is switched in mode 1.</li>
</ul>
<p>&nbsp;</p>
<p><strong>Known issues</strong></p>
<ul>
<li>Both, LSPM 1.0 and LSPM2.0 devices, work with the same SweepMe! instrument driver, but can have the same serial number. So far, the SweepMe! driver does not handle this very rare case. Please contact us in case you have this issue.&nbsp;</li>
</ul>
<p>&nbsp;</p>
    """

    def __init__(self):
        super().__init__()

        self.shortname = "LSPM"

        self.port_manager = True
        self.port_types = ["TCPIP"]  # could be extended to SOCKET to circumvent use of VISA runtime

        self.port_properties = {
            "TCPIP_EOLwrite": "\n",
            "TCPIP_EOLread": "\n",
            "timeout": 2,
        }

        self._verbose_mode = False

    def set_GUIparameter(self):

        gui_parameter = {
            "Serial number": "",  # could be also changed to serial number for correct identification
            "Channel 1": True,
            "Channel 2": False,
            "Channel 3": False,
            "Compensation frequency in Hz": "1e9",
            "Mode": ["0", "1", "2", "3"],
            "Crossover frequency in Hz (Mode 1)": "1e9",
            # "Automatic video bandwidth": True,
            # "Video bandwidth in Hz": "3e6",
        }

        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.sn = parameter.get("Serial number", "-1")
        self.channels = {}
        for i in range(1, 4):
            self.channels[i] = parameter[f"Channel {i}"]
        self.all_channel_indices = [i-1 for i in self.channels if self.channels[i]]

        self.variables = [f"Power {i}" for i in self.channels if self.channels[i]]
        self.units = ["dBm" for i in self.channels if self.channels[i]]
        self.plottype = [True for i in self.channels if self.channels[i]]
        self.savetype = [True for i in self.channels if self.channels[i]]

        self.mode = int(parameter["Mode"])
        self.frequency = float(parameter["Compensation frequency in Hz"])
        self.lhfrequency = float(parameter["Crossover frequency in Hz (Mode 1)"])
        # self.automatic_video_bandwidth = parameter["Automatic video bandwidth"]
        # self.video_bandwidth = float(parameter["Video bandwidth in Hz"])

    def initialize(self):

        if self.sn in ["", "-1"]:
            msg = "Please enter a valid serial number."
            raise Exception(msg)
        self.sn = int(self.sn)

        identifier = self.get_identification()
        # print("Identifier:", identifier)

        self.clear()

        stb = self.get_status_byte()
        # print("STB:", stb)

        opc = self.is_operation_complete()
        # print("OPC:", opc)

        count_meters = self.get_meter_count()  # works, but maybe needs latest TCP server
        # print("Number of power meters:", count_meters)

        self.port.write(f":MPM:SER {self.sn}, {self.sn}")
        self.pm_index = self.sn

        def print_model_infos(pm_index):
            print()
            print(f"Properties of Power meter {pm_index}:")
            print("  Version:", self.get_meter_version(pm_index))
            print("  Model:", self.get_meter_model(pm_index))
            print("  Firmware:", self.get_meter_firmware(pm_index))
            print("  SN:", self.get_meter_serial_number(pm_index))
            print("  Maker:", self.get_meter_maker(pm_index))
            print("  Meter ready:", self.get_meter_ready(pm_index))
            print("  Cold temperature in °C:", self.get_cold_temperature(pm_index))
            print("  Hot temperature in °C:", self.get_hot_temperature(pm_index))
            # print("  Channels:", self.get_meter_channels(pm_index))  # cannot be used if meter is not ready
            print()

        if self._verbose_mode:
            print_model_infos(self.pm_index)

        # Waiting until system ready (e.g. temperature has reached)
        ready = self.is_system_ready(self.pm_index)
        # print("Ready:", ready)
        if not ready:
            msg = ("LUMILOOP LSPM: System not ready. Waiting until temperature has reached."
                   "The measurement starts once the temperature is ok.\n"
                   "You can close this message box now.")
            debug(msg)
            self.message_box(msg, blocking=False)

            while True:
                time.sleep(0.5)
                if self.is_run_stopped():
                    return None
                ready = self.is_system_ready(self.pm_index)
                # print("Ready:", ready)
                if ready:
                    break

        # Meter ready check
        meter_ready = self.get_meter_ready(self.pm_index)
        # print("Meter ready:", meter_ready)
        if not meter_ready:
            msg = ("Meter is not ready. This can happen if parameters are not set correctly in a previous run. "
                   "Please check with LUMILOOP GUI application whether parameters like crossover frequency or "
                   "compensation frequency are in the correct range.")
            raise Exception(msg)

        # Channel check
        number_channels = self.get_meter_channels(self.pm_index)
        for i in self.channels:
            if self.channels[i] and i > number_channels:
                msg = f"LSPM has only {number_channels} channels. Please uncheck channel {i}."
                raise Exception(msg)

        self.check_for_error()

    def deinitialize(self):
        self.check_for_error()

    def configure(self):

        # Mode
        self.set_system_mode(self.pm_index, self.mode)
        mode = self.get_system_mode(self.pm_index)
        if mode != self.mode:
            msg = "Unable to set mode.\n"
            msg += f"Set mode: {self.mode}, Get mode: {mode}"
            raise Exception(msg)

        self.max_frequency = self.get_maximum_frequency(self.pm_index)
        self.min_frequency = self.get_minimum_frequency(self.pm_index)

        if self.frequency < self.min_frequency:
            msg = "Selected compensation frequency below calibration range."
            raise Exception(msg)

        if self.frequency > self.max_frequency:
            msg = "Selected compensation frequency above calibration range."
            raise Exception(msg)

        # Compensation Frequency
        self.set_frequency(self.pm_index, self.frequency)
        frequency = self.get_frequency(self.pm_index)
        if abs(frequency - self.frequency)/self.frequency > 1e-6:

            msg = "Unable to set compensation frequency.\n"
            msg += f"Set Compensation frequency in Hz: {self.frequency}, Get Compensation frequency in Hz: {frequency}"
            raise Exception(msg)

        self.check_for_error()

        if mode == 1:
            # Low-high crossover frequency
            old_frequency = self.get_LHfrequency(self.pm_index)
            self.set_LHfrequency(self.pm_index, self.lhfrequency)
            frequency = self.get_LHfrequency(self.pm_index)
            if abs(frequency - self.lhfrequency) / self.lhfrequency > 1e-6:
                msg = "Unable to set crossover frequency.\n"
                msg += f"Set Crossover frequency in Hz: {self.lhfrequency}, Get Crossover frequency in Hz: {frequency}"
                raise Exception(msg)

            # if the meter is not ready after changing the crossover frequency, an exception is raised
            # and the old crossover frequency is restored.
            meter_ready = self.get_meter_ready(self.pm_index)
            if not meter_ready:
                self.set_LHfrequency(self.pm_index, old_frequency)
                msg = "Unable to set crossover frequency"
                raise Exception(msg)

        # Automatic video bandwidth
        self.set_automatic_video_bandwidth(self.pm_index, True)

        # Triggering
        # can be implemented here

        # Sweep times
        # can be implemented here

        self.check_for_error()

    def reconfigure(self, parameters, keys):

        # Compensation Frequency
        if "Compensation frequency in Hz" in keys:
            new_frequency = float(parameters["Compensation frequency in Hz"])
            self.set_frequency(self.pm_index, new_frequency)
            frequency = self.get_frequency(self.pm_index)
            if abs(frequency - new_frequency) / new_frequency > 1e-6:
                msg = "Unable to set compensation frequency.\n"
                msg += f"Set Compensation frequency in Hz: {new_frequency}, Get Compensation frequency in Hz: {frequency}"
                raise Exception(msg)

            self.check_for_error()

    def measure(self):
        self.results = self.get_meter_power(self.pm_index)  # retrieves all power values from 1st device

    def call(self):

        return list(np.array(self.results)[self.all_channel_indices])

    """ LUMILOOP LSPM specific functions """

    def check_for_error(self):
        """Check for errors and raise an exception if any are found."""

        errors = self.get_all_errors()
        for msg in errors:
            debug(msg)
        if len(errors) > 0:
            msg = errors[0]
            raise Exception(msg)

    def get_all_errors(self):
        """Get all errors from the error queue."""
        errors = []
        while True:
            msg = self.get_error()
            if "No error" in msg:
                break
            errors.append(msg)
        return errors

    def get_identification(self):
        """Get the identification string of the device."""
        self.port.write("*IDN?")
        answer = self.port.read()
        return answer

    def reset(self):
        """ not supported yet """
        self.port.write("*RST")

    def clear(self):
        """Clear the error queue."""
        self.port.write("*CLS")

    def get_status_byte(self):
        """Get the status byte of the device."""
        self.port.write("*STB?")
        answer = self.port.read()
        return int(answer)

    def is_operation_complete(self):
        """Check if the operation is complete."""
        self.port.write("*OPC?")
        answer = self.port.read()
        return int(answer)

    def is_system_ready(self, index: int):
        """Check if the system is ready."""
        self.port.write(f":SYST:RDY? {index}")
        answer = self.port.read()
        return bool(int(answer))

    def get_error(self):
        """Get the last error message."""
        self.port.write(":SYST:ERR?")
        answer = self.port.read()
        return answer

    def get_error_count(self):
        """Get the number of errors in the error queue."""
        self.port.write(":SYST:ERR:COUN?")
        answer = self.port.read()
        return int(answer)

    def get_meter_count(self):
        """Get the number of power meters."""
        self.port.write(":SYST:COU?")
        answer = self.port.read()
        return int(answer)

    def get_meter_serial_number(self, index: int):
        """Get the serial number of the power meter."""
        self.port.write(f":MEAS:SER? {index}")
        answer = self.port.read()
        return int(answer)

    def get_meter_maker(self, index: int):
        """Get the maker of the power meter."""
        self.port.write(f":SYST:MAK? {index}")
        answer = self.port.read()
        return answer

    def get_meter_model(self, index: int):
        """Get the model of the power meter."""
        self.port.write(f":SYST:DEV? {index}")
        answer = self.port.read()
        return answer

    def get_meter_version(self, index: int):
        """Get the version of the power meter."""
        self.port.write(f":SYST:VERS? {index}")
        answer = self.port.read()
        return answer

    def get_meter_firmware(self, index: int):
        """Get the firmware of the power meter."""
        self.port.write(f":SYST:FVERS? {index}")
        answer = self.port.read()
        return answer

    def get_meter_mode(self, index: int):
        """Get the mode of the power meter."""
        self.port.write(f":MEAS:MOD? {index}")
        answer = self.port.read()
        return int(answer)

    def get_meter_ready(self, index: int):
        """Check if the power meter is ready."""
        self.port.write(f":MEAS:RDY? {index}")
        answer = self.port.read()
        return bool(int(answer))

    def get_meter_power(self, index: int):
        """Get the power values of all channels."""
        self.port.write(f":MEAS:ALL? {index}")
        answer = self.port.read()
        return list(map(float, answer.split(",")))

    def get_meter_channels(self, index: int):
        """Get the number of channels of the power meter."""
        self.port.write(f"SYST:CHAN? {index}")
        answer = self.port.read()
        return int(answer)

    def set_system_mode(self, index: int, mode: int):
        """Set the system mode of the power meter."""
        self.port.write(f":SYST:MOD {mode}, {index}")

    def get_system_mode(self, index: int):
        """Get the system mode of the power meter."""
        self.port.write(f":SYST:MOD? {index}")
        answer = self.port.read()
        return int(answer)

    def set_frequency(self, index: int, frequency: float):
        """Set the compensation frequency of the power meter."""
        self.port.write(f":SYST:FREQ {frequency}, {index}")

    def get_frequency(self, index: int):
        """Get the compensation frequency of the power meter."""
        self.port.write(f":SYST:FREQ? {index}")
        answer = self.port.read()
        return float(answer)

    def get_minimum_frequency(self, index: int):
        """Get the minimum frequency of the power meter."""
        self.port.write(f":SYST:FREQ:MIN? {index}")
        answer = self.port.read()
        return float(answer)

    def get_maximum_frequency(self, index: int):
        """Get the maximum frequency of the power meter."""
        self.port.write(f":SYST:FREQ:MAX? {index}")
        answer = self.port.read()
        return float(answer)

    def set_LHfrequency(self, index: int, frequency: float):
        """Set the low-high crossover frequency of the power meter."""
        self.port.write(f":SYST:LHF {frequency}, {index}")

    def get_LHfrequency(self, index: int):
        """Get the low-high crossover frequency of the power meter."""
        self.port.write(f":SYST:LHF? {index}")
        answer = self.port.read()
        return float(answer)

    def get_cold_temperature(self, index: int):
        """Get the cold temperature of the power meter."""
        self.port.write(f":MEAS:TC? {index}")
        answer = self.port.read()
        return float(answer)

    def get_hot_temperature(self, index: int):
        """Get the hot temperature of the power meter."""
        self.port.write(f":MEAS:TH? {index}")
        answer = self.port.read()
        return float(answer)

    def set_automatic_video_bandwidth(self, index: int, state: bool):
        """Set the automatic video bandwidth of the power meter."""
        self.port.write(f":MEAS:AUTOVBW {int(state)}, {index}")

    def is_automatic_video_bandwidth(self, index: int):
        """Check if the automatic video bandwidth is enabled."""
        self.port.write(f":MEAS:AUTOVBW? {index}")
        answer = self.port.read()
        return int(answer)

    def set_video_bandwidth(self, index: int, frequency: float):
        """Set the video bandwidth of the power meter."""
        self.port.write(f":MEAS:VBW {frequency}, {index}")

    def get_video_bandwidth(self, index: int):
        """Get the video bandwidth of the power meter."""
        self.port.write(f":MEAS:VBW? {index}")
        answer = self.port.read()
        return float(answer)
