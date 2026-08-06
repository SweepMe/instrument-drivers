# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022, 2024, 2026 SweepMe! GmbH (sweep-me.net)
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

# SweepMe! device class
# Type: Scope
# Device: Red pitaya STEMlab

from __future__ import annotations

import time
from typing import Any

import numpy as np

from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()

import redpitaya_scpi as scpi
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    """Driver for the fast analog inputs of Red Pitaya STEMlab boards."""

    def __init__(self) -> None:
        EmptyDevice.__init__(self)

        self.shortname = "STEMlab"

        self.commands = {
            "Channel 1": "CH1",
            "Channel 2": "CH2",
            "External": "EXT",
            "Software": "EXT",
            "Signal": "AWG",
            "Now": "NOW",
            "None": "DISABLED",
            "Rising": "_PE",
            "Falling": "_NE",
            "High voltage": "HV",
            "Low voltage": "LV",
            "Averaged decimation on": "ON",
            "Averaged decimation off": "OFF",
        }

        # Trigger sources that do not depend on a signal edge and therefore have no slope, level
        # or hysteresis. "None" disables the trigger completely and makes the acquisition wait
        # forever, "Now" triggers immediately and is the right choice for a free running signal.
        self.edgeless_triggers = ("NOW", "DISABLED")

        self.max_time = 10.0

        # Connection
        self.port: Any = None
        self.ip_address: str = ""

        # GUI parameters, exactly as they arrive from the GUI
        self.gui_parameters: dict[str, Any] = {}

        self.sweepmode: str = "None"
        self.triggermode: str = "Now"
        self.triggercoupling: str = "DC"
        self.triggerslope: str = "Rising"
        self.triggerlevel: str | float = 0.0
        self.triggerdelay: str | float = 0.0
        self.triggertimeout: str | float = 5.0
        self.triggerhysteresis: str | float = 0.0
        self.timerange: str | float = "131 µs"
        self.timeoffsetvalue: str | float = 0.0
        self.acquisiton: str = "Averaged decimation on"
        self.averages: str | int = 1
        self.samplingratetype: str = "Samples"
        self.samples: str | int = 16384

        self.channels: list[int] = []
        self.channel_names: dict[int, str] = {}
        self.channel_ranges: dict[int, str] = {}
        self.channel_offsets: dict[int, float] = {}

        # Values derived during configure
        self.samplerate: float = 125e6
        self.real_samplerate: float = 125e6
        self.buffersize: int = 16384
        self.decimation: int = 1
        self.read_samples: int = 16384
        self.triggersource: str = "NOW"
        self.triggerdelaysamples: int = 0

        # Timeout in s for receiving an answer from the SCPI server
        self.port_timeout: float = 5.0

        # Instrument capabilities, determined during the run
        self.has_fill_query: bool = True

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI fields, depending on the selected trigger source and channels.

        The level, slope and hysteresis fields are only shown for trigger sources that react to a
        signal edge. The name, range and offset of a channel are only shown if that channel is
        enabled.
        """
        new_parameters: dict[str, Any] = {
            "SweepMode": ["None", "Time range in s", "Trigger delay in s"],
            # "Now" triggers immediately without an edge condition and is the right choice to
            # read back a continuously running signal.
            "TriggerSource": [
                "Now",
                "Channel 1",
                "Channel 2",
                "External",
                "Software",
                "Signal",
                "None",
            ],
            "TriggerTimeout": 5.0,
            "TriggerDelay": 0.0,
        }

        trigger_source = self.commands.get(
            parameters.get("TriggerSource", "Now"), "NOW"
        )
        if trigger_source not in self.edgeless_triggers:
            new_parameters["TriggerSlope"] = ["Rising", "Falling"]
            new_parameters["TriggerCoupling"] = ["DC"]
            new_parameters["TriggerLevel"] = 0
            new_parameters["TriggerHysteresis"] = 0.0

        new_parameters[" "] = None  # empty line
        new_parameters["Acquisition"] = [
            "Averaged decimation on",
            "Averaged decimation off",
        ]
        new_parameters["Average"] = [
            "1",
            "2",
            "4",
            "8",
            "16",
            "32",
            "64",
            "128",
            "256",
            "512",
            "1024",
        ]
        new_parameters["SamplingRateType"] = ["Samples"]
        new_parameters["SamplingRate"] = [
            "16384",
            "8192",
            "4096",
            "2048",
            "1024",
            "512",
            "256",
        ]

        new_parameters["TimeRange"] = ["Time range in s:"]
        new_parameters["TimeRangeValue"] = [
            "131 µs",
            "262 µs",
            "524 µs",
            "1.04 ms",
            "2.09 ms",
            "4.19 ms",
            "8.38 ms",
            "16.7 ms",
            "33.5 ms",
            "67.1 ms",
            "134 ms",
            "268 ms",
            "536 ms",
            "1.07 s",
            "2.14 s",
            "4.29 s",
            "8.60 s",
        ]
        new_parameters["TimeOffsetValue"] = 0.0

        # Channel specific GUI parameters
        for i in (1, 2):
            new_parameters[f"  Channel {i}"] = None  # empty line
            new_parameters[f"Channel{i}"] = False
            if parameters.get(f"Channel{i}", False):
                new_parameters[f"Channel{i}_Name"] = f"Ch{i}"
                new_parameters[f"Channel{i}_Range"] = ["Low voltage", "High voltage"]
                new_parameters[f"Channel{i}_Offset"] = "0.0"

        return new_parameters

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the user selections and derive the returned variables.

        The values are only kept as they arrive from the GUI. They are converted to numbers in
        'convert_gui_parameters', which is called from 'configure', because this function can be
        called with incomplete or empty values while the user is still editing the fields.

        The raw values are deliberately kept in a separate dictionary instead of being converted
        in place. SweepMe! may call this function again after 'configure', which would otherwise
        silently replace the converted numbers by the original strings.
        """
        self.gui_parameters = dict(parameters)

        self.sweepmode = parameters.get("SweepMode", "None")
        self.ip_address = parameters.get("Port", "")

        # Channels and returned variables. These are needed before 'configure' is called and
        # require no conversion.
        self.channels = [i for i in (1, 2) if parameters.get(f"Channel{i}", False)]
        self.channel_names = {
            i: parameters.get(f"Channel{i}_Name", f"Ch{i}") for i in self.channels
        }

        self.variables = ["Time"]
        self.units = ["s"]
        self.plottype = [True]  # True to plot data
        self.savetype = [True]  # True to save data

        for i in self.channels:
            self.variables.append(
                f"{self.commands[f'Channel {i}']} {self.channel_names[i]}"
            )
            self.units.append("V")
            self.plottype.append(True)
            self.savetype.append(True)

    def connect(self):
        # port_timeout is used here to avoid that an unanswered query blocks the driver forever,
        # which can happen if the instrument runs an ecosystem that does not know a command. The timeout
        # applies to each received chunk, not to the entire answer, so reading a full data buffer
        # is not affected.
        self.port = scpi.scpi(self.ip_address, timeout=self.port_timeout)

        self.port.write = self.port.tx_txt  # wrap write-scpi command
        self.port.read = self.port.rx_txt  # wrap read-scpi command

        # identification = self.get_identification()
        # print("Identification", identification)

        # system_version = self.get_system_version()
        # print("System version:", system_version)

    def initialize(self):
        pass

    def configure(self):
        # general settings

        self.convert_gui_parameters()

        # 'ACQ:TRig:FILL?' is only available since StemLab OS 2.00. Whether the instrument supports it is
        # found out on the first use in 'wait_for_buffer'.
        self.has_fill_query = True

        self.reset_acquisition()  # Reset Device

        self.port.write("ACQ:DATA:UNITS VOLTS")  # set Units

        self.port.write("ACQ:BUF:SIZE?")  # get buffersize from device
        self.buffersize = int(self.port.read())
        self.samplerate = 125e6  # sampling rate

        if self.triggermode == "Software":
            self.averages = 1  # no averages in Software synchronization

        for i in self.channels:  # set Gain for channels
            self.port.write(
                "ACQ:SOUR{0}:GAIN {1}".format(i, self.commands[self.channel_ranges[i]])
            )

        # time settings
        self.time_settings()
        if self.triggertimeout < (self.buffersize * self.decimation / self.samplerate):
            print(
                "Trigger timeout is to short! This causes trigger issues. Please increase the trigger timeout."
            )

        # trigger settings
        self.trigger_settings()

        # send settings to RedPitaya
        self.send_settings()

        # print settings
        # self.settings_status()

    def apply(self):
        if self.sweepmode == "Time range in s":
            self.timerange = self.value
            self.time_settings()
            self.send_settings()

        elif self.sweepmode == "Trigger delay in s":
            self.triggerdelay = self.value
            self.trigger_settings()
            self.send_settings()

    def measure(self):
        # creating data list
        self.channel_data = [None for i in self.channels]

        for avg in range(self.averages):
            # trigger settings
            self.trigger_settings()

            # send settings to RedPitaya
            self.send_settings()

            # print settings
            # self.settings_status()

            self.start_acquisition()
            self.starttime = time.time()  # set starttime, required for filling buffer

            # Arm the trigger. This must happen after 'ACQ:START', see 'arm_trigger'.
            self.arm_trigger()

            self.wait_for_trigger()

            self.wait_for_buffer()

            self.read_data()  # reading data

            self.stop_acquisition()

        for i in range(len(self.channels)):  # average data and add offsets
            self.channel_data[i] /= self.averages
            self.channel_data[i] += self.channel_offsets[self.channels[i]]

        self.stop_acquisition()

        # specify time values
        self.time_values = (
            np.linspace(
                0, self.read_samples / self.real_samplerate, len(self.channel_data[0])
            )
            + self.triggerdelay
            + self.timeoffsetvalue
        )

    def call(self):
        return [self.time_values] + self.channel_data

    # Functions

    def convert_gui_parameters(self) -> None:
        """Convert the stored GUI parameters to numbers and check them for valid values.

        This is done here and not in 'apply_gui_parameters' because that function can be called
        with incomplete or empty fields while the user is still editing them. It reads from
        'self.gui_parameters' and writes to separate attributes, so that a later call of
        'apply_gui_parameters' cannot revert the converted values back to strings.
        """
        parameters = self.gui_parameters

        # Selections that need no conversion
        self.triggermode = parameters.get("TriggerSource", "Now")
        self.triggercoupling = parameters.get("TriggerCoupling", "DC")
        self.triggerslope = parameters.get("TriggerSlope", "Rising")
        self.acquisiton = parameters.get("Acquisition", "Averaged decimation on")
        self.samplingratetype = parameters.get("SamplingRateType", "Samples")
        self.timerange = parameters.get("TimeRangeValue", "131 µs")
        self.channel_ranges = {
            i: parameters.get(f"Channel{i}_Range", "Low voltage") for i in self.channels
        }

        try:
            self.triggerlevel = float(parameters.get("TriggerLevel", 0))
            self.triggerdelay = float(parameters.get("TriggerDelay", 0.0))
            self.triggertimeout = float(parameters.get("TriggerTimeout", 5.0))
            self.triggerhysteresis = float(parameters.get("TriggerHysteresis", 0.0))
            self.timeoffsetvalue = float(parameters.get("TimeOffsetValue", 0.0))
            self.averages = int(parameters.get("Average", 1))
            self.samples = int(parameters.get("SamplingRate", 16384))
            self.channel_offsets = {
                i: float(parameters.get(f"Channel{i}_Offset", 0.0))
                for i in self.channels
            }
        except ValueError:
            msg = "Red Pitaya STEMlab: Please enter numeric values into all number fields."
            raise ValueError(msg)

        if not self.channels:
            msg = "Red Pitaya STEMlab: Please enable at least one channel."
            raise ValueError(msg)

        if self.triggermode not in self.commands:
            msg = (
                f"Red Pitaya STEMlab: Unknown trigger source '{self.triggermode}'. "
                "Please select a valid trigger source."
            )
            raise ValueError(msg)

        if self.averages < 1:
            msg = "Red Pitaya STEMlab: The number of averages must be at least 1."
            raise ValueError(msg)

        if self.triggertimeout <= 0.0:
            msg = "Red Pitaya STEMlab: The trigger timeout must be larger than 0 s."
            raise ValueError(msg)

        if self.commands[self.triggermode] == "DISABLED":
            msg = (
                "Red Pitaya STEMlab: The trigger source 'None' disables the trigger, so the "
                "acquisition never completes and runs into the trigger timeout.\n"
                "Please use 'Now' to acquire immediately, or a channel trigger to acquire on "
                "a signal edge."
            )
            raise ValueError(msg)

    def wait_for_trigger(self) -> None:
        """Wait until the trigger condition is met."""
        while True:
            if self.get_trigger_status() == "TD":
                self.starttime = time.time()
                return

            if time.time() - self.starttime > self.triggertimeout:
                msg = (
                    "Red Pitaya Scope Trigger timeout!\n"
                    "No trigger event was detected within {0} s. Please check the trigger "
                    "source, level and slope, or use the trigger source 'Now'.".format(
                        self.triggertimeout
                    )
                )
                raise Exception(msg)

            if self.is_run_stopped():
                return

    def wait_for_buffer(self) -> None:
        """Wait until the data buffer is completely filled after the trigger event.

        The trigger is positioned in the middle of the data buffer, so after the trigger event
        the second half of the buffer still has to be recorded. Reading earlier returns samples
        from the previous acquisition for that part of the trace.

        'ACQ:TRig:FILL?' requires OS 2.00 or higher. Older ecosystems do not know the command and
        may not answer it at all. The command is therefore tried once and, if the instrument does
        not answer it or answers something unexpected, it is not used again for the rest of the
        run. Without the query the driver waits for the time the remaining samples need, which
        works on every version.
        """
        # time the second half of the buffer needs to be recorded
        fill_time = 0.5 * self.buffersize / self.real_samplerate

        while self.has_fill_query:
            try:
                self.port.write("ACQ:TRig:FILL?")
                answer = self.port.read().strip()
            except OSError:
                # no answer within the port timeout, the command is not supported
                self.has_fill_query = False
                self.clear_port()
                self.write_Log(
                    "Red Pitaya Scope: 'ACQ:TRig:FILL?' is not supported by this "
                    "instrument, waiting for the calculated buffer fill time instead."
                )
                break

            if answer == "1":
                return

            if answer not in ("0", "1"):
                self.has_fill_query = False
                self.write_Log(
                    "Red Pitaya Scope: 'ACQ:TRig:FILL?' answered {0!r}, waiting for "
                    "the calculated buffer fill time instead.".format(answer)
                )
                break

            if time.time() - self.starttime > fill_time + self.triggertimeout:
                msg = (
                    "Red Pitaya Scope: The data buffer was not filled within {0:.1f} s after "
                    "the trigger event.".format(fill_time + self.triggertimeout)
                )
                raise Exception(msg)

            if self.is_run_stopped():
                return

        time.sleep(max(fill_time - (time.time() - self.starttime), 0))

    def clear_port(self) -> None:
        """Discard data that is still waiting in the receive buffer.

        Needed after a command was not answered in time, so that a late answer is not read as the
        answer to the next command.
        """
        connection = self.port._socket
        timeout = connection.gettimeout()
        connection.settimeout(0.1)
        try:
            while connection.recv(4096):
                pass
        except OSError:
            pass
        finally:
            connection.settimeout(timeout)

    def read_data(self):
        for i in range(len(self.channels)):
            self.port.write(
                "ACQ:SOUR{0}:DATA:OLD:N? {1}".format(
                    self.channels[i], self.read_samples
                )
            )
            self.buffer = self.port.read()
            try:
                self.data = list(
                    map(float, self.buffer.strip("{}\n\r").replace("  ", "").split(","))
                )
            except:
                self.data = list(
                    map(
                        float,
                        self.buffer.strip("{}ERR!\n\r").replace("  ", "").split(","),
                    )
                )
                print("Error in Readout!")
            if self.channel_data[i] is None:
                self.channel_data[i] = np.array(self.data)
            else:
                self.channel_data[i] += np.array(self.data)

    def trigger_settings(self):
        # create trigger command
        self.triggersource = self.commands[self.triggermode]
        if self.triggersource not in self.edgeless_triggers:
            self.triggersource += self.commands[self.triggerslope]

        self.triggerdelaysamples = int(
            self.triggerdelay * self.real_samplerate + self.buffersize * 0.5
        )

    def time_settings(self):
        # calculates decimation and read samples parameters
        if isinstance(self.timerange, str):
            try:
                self.timerange = float(
                    self.timerange.replace("ms", "e-3")
                    .replace("µs", "e-6")
                    .replace("ns", "e-9")
                    .replace("us", "e-6")
                    .replace("s", "")
                    .replace(" ", "")
                )
            except:
                print("Please enter a number for time range. Time range is set to 8.6s")
                self.timerange = 8.6

        # calculate decimation factor based on time range
        self.decimation = 2 ** (
            int(
                2
                + np.log((self.timerange * self.samplerate) / self.samples)
                / (np.log(2))
            )
            - 1
        )

        # set upper limit for decimation
        if self.decimation > 2**16:
            self.decimation = 2**16

        # samples per second
        self.real_samplerate = self.samplerate / self.decimation

        # calculate samples to read
        self.read_samples = 2 + int(self.timerange * self.real_samplerate)

        # upper limit for samples to read
        if self.read_samples > self.buffersize:
            self.read_samples = self.buffersize

    def send_settings(self):
        """Send the acquisition settings.

        The trigger source is deliberately not sent here. It arms the trigger and must be sent
        after 'ACQ:START', see 'arm_trigger'.
        """
        self.port.write("ACQ:DEC {0}".format(self.decimation))  # set decimation
        self.port.write(
            "ACQ:AVG {0}".format(self.commands[self.acquisiton])
        )  # set decimation average

        if self.triggersource not in self.edgeless_triggers:
            self.port.write(
                "ACQ:TRIG:LEV {0}".format(self.triggerlevel)
            )  # set trigger level
            self.port.write(
                "ACQ:TRIG:HYST {0}".format(self.triggerhysteresis)
            )  # set trigger hysteresis
            self.port.write(
                "ACQ:TRIG:DLY {0}".format(self.triggerdelaysamples)
            )  # set trigger delay

    def arm_trigger(self):
        """Set the trigger source, which arms the trigger.

        This must happen after 'ACQ:START'. The manufacturer's acquisition example states
        "Trigger source command must be set after ACQ:START". Arming while the acquisition is
        stopped is lost, which makes every acquisition after the first one run into the trigger
        timeout.
        """
        self.port.write("ACQ:TRIG {}".format(self.triggersource))

    def settings_status(self):
        self.port.write("ACQ:DATA:UNITS?")  # Data units
        print("Data Units:", self.port.read())
        self.port.write("ACQ:DEC?")  # Decimation
        print("Decimation:", self.port.read())
        self.port.write("ACQ:AVG?")  # Decimation averaging
        print("Averaging:", self.port.read())
        self.port.write("ACQ:TRIG:LEV?")  # Trigger Level
        print("Trigger Level:", self.port.read())
        self.port.write("ACQ:TRIG:HYST?")  # Trigger Hysteresis
        print("Trigger Hysteresis:", self.port.read())
        self.port.write("ACQ:TRIG:DLY?")  # Trigger Delay
        print("Trigger Delay:", self.port.read())
        self.port.write("ACQ:SOUR1:GAIN?")  # Channel 1 Gain
        print("Channel 1 Gain:", self.port.read())
        self.port.write("ACQ:SOUR2:GAIN?")  # Channel 2 Gain
        print("Channel 2 Gain:", self.port.read())
        self.port.write("ACQ:TRIG:STAT?")  # Trigger status
        print("Trigger Status:", self.port.read())

    def get_identification(self):
        self.port.write("*IDN?")
        return self.port.read()

    def get_system_version(self):
        self.port.write("SYST:VERS?")
        return self.port.read()

    def start_acquisition(self):
        self.port.write("ACQ:START")

    def stop_acquisition(self):
        self.port.write("ACQ:STOP")

    def reset_acquisition(self):
        self.port.write("ACQ:RST")

    def get_trigger_status(self):
        """Returns the trigger status.

        Returns:
            status:
                -> "WAIT" if not trigger is received yet
                -> "TD" if the measurement was triggered
        """

        self.port.write("ACQ:TRIG:STAT?")
        return self.port.read()

    def set_average(self, state):
        self.port.write("ACQ:AVG %s" % str(state))

    def get_average(self):
        self.port.write("ACQ:AVG?")
        return self.port.read()
