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
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug


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

        # The board is addressed through its SCPI server, a plain TCP socket that terminates
        # every line with CR LF. The port manager opens it, so the generator driver of the same
        # board shares the connection. The port is entered as 'ip:5000'.
        self.port_manager = True
        self.port_types = ["SOCKET"]
        self.port_properties = {
            "SOCKET_EOLwrite": "\r\n",
            "SOCKET_EOLread": "\r\n",
            # A timeout is essential: without it a command the instrument does not know is never
            # answered and the driver would wait forever, with no error and no way to stop the
            # run. It bounds the whole answer, a full 16384-sample data buffer included.
            "timeout": 5,
            "fixed_port": 5000,  # the SCPI server always listens on 5000
        }

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

        new_parameters["Acquisition"] = [
            "Averaged decimation on",
            "Averaged decimation off",
        ]
        new_parameters["Average"] = 1
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

        new_parameters["TimeRange"] = ["Time range:"]
        new_parameters[
            "TimeRangeValue"
        ] = [  # user can enter time range in s, ms, µs, ns
            "131 µs",
        ]
        new_parameters["TimeOffsetValue"] = 0.0

        # Channel specific GUI parameters
        for i in (1, 2):
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
        """Check that the SCPI server answers.

        The socket itself is opened by the port manager, which hands over no port at all when the
        board cannot be reached. Querying '*IDN?' here makes a stopped SCPI server fail at
        connect, with a message, instead of on the first command of the run.
        """
        hint = (
            "Start the SCPI server on the board (web interface -> Development -> SCPI server) "
            "and enter the port as 'ip:5000'."
        )
        if self.port is None:
            msg = f"Scope-RedPitaya_STEMlab: The connection to the board could not be opened. {hint}"
            raise ConnectionError(msg)
        try:
            self.get_identification()
        except (OSError, TimeoutError) as e:
            msg = (
                f"Scope-RedPitaya_STEMlab: No SCPI server answers at "
                f"{self.port.port_properties['ID']}. {hint} Error is: {e}."
            )
            raise ConnectionError(msg) from e

    def configure(self):
        # general settings

        self.convert_gui_parameters()

        # 'ACQ:TRig:FILL?' is only available since StemLab OS 2.00. Whether the instrument supports it is
        # found out on the first use in '_wait_for_buffer'.
        self.has_fill_query = True

        self.reset_acquisition()  # Reset Device

        self.set_data_units("VOLTS")

        self.buffersize = self.get_buffer_size()
        self.samplerate = 125e6  # sampling rate

        if self.triggermode == "Software":
            self.averages = 1  # no averages in Software synchronization

        for i in self.channels:  # set Gain for channels
            self.set_gain(i, self.commands[self.channel_ranges[i]])

        # time settings
        self._time_settings()
        if self.triggertimeout < (self.buffersize * self.decimation / self.samplerate):
            debug(
                "Scope-RedPitaya_STEMlab: The trigger timeout is too short. This can cause trigger "
                "issues. Please increase the trigger timeout to more than the time range."
            )

        # trigger settings
        self._trigger_settings()

        # send settings to RedPitaya
        self._send_settings()

    def apply(self):
        value = float(self.value)

        if self.sweepmode == "Time range in s":
            self.timerange = value
            self._time_settings()
            self._send_settings()

        elif self.sweepmode == "Trigger delay in s":
            self.triggerdelay = value
            self._trigger_settings()
            self._send_settings()

    def measure(self):
        # creating data list
        self.channel_data = [None for i in self.channels]

        # trigger settings
        self._trigger_settings()

        # send settings to RedPitaya
        self._send_settings()

        for avg in range(self.averages):
            self.start_acquisition()
            self.starttime = time.time()  # set starttime, required for filling buffer

            try:
                # Arm the trigger. This must happen after 'ACQ:START', see 'set_trigger_source'.
                self.set_trigger_source(self.triggersource)
                self._wait_for_trigger()
                self._wait_for_buffer()
                if self.is_run_stopped():  # Do not read data if the run stopped.
                    return
                self._acquire_channel_data()  # reading data
            finally:  # Stop the acquisition even if an error occured
                try:
                    self.stop_acquisition()
                except OSError:
                    # never mask the exception that is already propagating
                    debug("Scope-RedPitaya_STEMlab: could not stop the acquisition.")

        for i in range(len(self.channels)):  # average data and add offsets
            self.channel_data[i] /= self.averages
            self.channel_data[i] += self.channel_offsets[self.channels[i]]

        # specify time values
        # The axis is derived from the number of samples that were actually received and from the
        # sample period, not from an endpoint. 'np.linspace' includes its endpoint, so spanning
        # N samples over N/real_samplerate would spread them with a period of
        # 1/real_samplerate * N/(N-1), stretching every trace by one sample period in total.
        self.time_values = (
            np.arange(len(self.channel_data[0])) / self.real_samplerate
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
            msg = "Scope-RedPitaya_STEMlab: Please enter numeric values into all number fields."
            raise ValueError(msg)

        if not self.channels:
            msg = "Scope-RedPitaya_STEMlab: Please enable at least one channel."
            raise ValueError(msg)

        if self.triggermode not in self.commands:
            msg = (
                f"Scope-RedPitaya_STEMlab: Unknown trigger source '{self.triggermode}'. "
                "Please select a valid trigger source."
            )
            raise ValueError(msg)

        if self.averages < 1:
            msg = "Scope-RedPitaya_STEMlab: The number of averages must be at least 1."
            raise ValueError(msg)

        if self.triggertimeout <= 0.0:
            msg = (
                "Scope-RedPitaya_STEMlab: The trigger timeout must be larger than 0 s."
            )
            raise ValueError(msg)

        if self.commands[self.triggermode] == "DISABLED":
            msg = (
                "Scope-RedPitaya_STEMlab: The trigger source 'None' disables the trigger, so the "
                "acquisition never completes and runs into the trigger timeout.\n"
                "Please use 'Now' to acquire immediately, or a channel trigger to acquire on "
                "a signal edge."
            )
            raise ValueError(msg)

    # -- GUI-driven helpers -----------------------------------------------------
    # They derive the instrument values from the GUI selections and send them through the
    # communication commands below.

    def _wait_for_trigger(self) -> None:
        """Wait until the trigger condition is met."""
        while True:
            if self.get_trigger_status() == "TD":
                self.starttime = time.time()
                return

            if time.time() - self.starttime > self.triggertimeout:
                msg = (
                    "Scope-RedPitaya_STEMlab: Trigger timeout!\n"
                    "No trigger event was detected within {0} s. Please check the trigger "
                    "source, level and slope, or use the trigger source 'Now'.".format(
                        self.triggertimeout
                    )
                )
                raise Exception(msg)

            if self.is_run_stopped():
                return

    def _wait_for_buffer(self) -> None:
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
            if self.is_run_stopped():
                return

            try:
                answer = self.port.query("ACQ:TRig:FILL?").strip()
            except OSError:
                # no answer within the port timeout (a TimeoutError is an OSError), so the
                # command is not supported. A late answer must not be read as the answer to the
                # next command, hence the clear.
                self.has_fill_query = False
                self.port.clear()
                debug(
                    "Scope-RedPitaya_STEMlab: 'ACQ:TRig:FILL?' is not supported by this "
                    "instrument, waiting for the calculated buffer fill time instead."
                )
                break

            if answer == "1":
                return

            if answer not in ("0", "1"):
                self.has_fill_query = False
                debug(
                    "Scope-RedPitaya_STEMlab: 'ACQ:TRig:FILL?' answered {0!r}, waiting for "
                    "the calculated buffer fill time instead.".format(answer)
                )
                break

            if time.time() - self.starttime > fill_time + self.triggertimeout:
                msg = (
                    "Scope-RedPitaya_STEMlab: The data buffer was not filled within {0:.1f} s after "
                    "the trigger event.".format(fill_time + self.triggertimeout)
                )
                raise Exception(msg)

        time.sleep(max(fill_time - (time.time() - self.starttime), 0))

    def _acquire_channel_data(self) -> None:
        """Read the acquired data of all enabled channels and add it to the channel data.

        The oldest samples of the data buffer are requested for each enabled channel. The values
        are accumulated in 'self.channel_data', so that 'measure' can call this function once per
        average and divide by the number of averages afterwards. On the first call the
        accumulator is still None and is initialised with the first trace.
        """
        for i in range(len(self.channels)):
            data = np.array(self.get_data(self.channels[i], self.read_samples))
            if self.channel_data[i] is None:
                self.channel_data[i] = data
            else:
                self.channel_data[i] += data

    def _trigger_settings(self) -> None:
        # create trigger command
        self.triggersource = self.commands[self.triggermode]
        if self.triggersource not in self.edgeless_triggers:
            self.triggersource += self.commands[self.triggerslope]

        self.triggerdelaysamples = int(
            self.triggerdelay * self.real_samplerate + self.buffersize * 0.5
        )

    def _time_settings(self) -> None:
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
                debug(
                    "Scope-RedPitaya_STEMlab: '{0}' is not a valid time range. Please enter a "
                    "number, optionally with a unit like s, ms, µs or ns. The time range is set "
                    "to 8.6 s instead.".format(self.timerange)
                )
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

    def _send_settings(self) -> None:
        """Send the acquisition settings.

        The trigger source is deliberately not sent here. It arms the trigger and must be sent
        after 'ACQ:START', see 'set_trigger_source'.
        """
        self.set_decimation(self.decimation)
        self.set_averaging(self.commands[self.acquisiton] == "ON")

        if self.triggersource not in self.edgeless_triggers:
            self.set_trigger_level(self.triggerlevel)
            self.set_trigger_hysteresis(self.triggerhysteresis)

        # The trigger delay is sent for every trigger source, also for the edgeless ones. It
        # positions the data buffer relative to the trigger event ("pre-trigger vs post-trigger
        # data") and is therefore meaningful for "Now" as well, which has no level or slope.
        # Skipping it here would leave the instrument at its previous delay while the driver still
        # shifts the returned time axis by the configured value.
        self.set_trigger_delay(self.triggerdelaysamples)

    @staticmethod
    def _parse_data(answer: str, channel: int) -> list[float]:
        """Turn the '{v1,v2,...}' answer of a data query into a list of floats.

        If the answer cannot be parsed as numbers, it is parsed again after stripping an 'ERR!'
        marker, and a message is written to the debug log, so a single faulty readout does not
        abort a measurement.
        """
        try:
            return list(map(float, answer.strip("{}\n\r").replace("  ", "").split(",")))
        except ValueError:
            data = list(map(float, answer.strip("{}ERR!\n\r").replace("  ", "").split(",")))
            debug(
                "Scope-RedPitaya_STEMlab: Error while reading the data of channel "
                "{0}.".format(channel)
            )
            return data

    # -- Communication commands -------------------------------------------------
    # One SCPI command each, with explicit arguments, so that a pysweepme script or an agent can
    # address every property of the acquisition directly. 'channel' is the input, 1 or 2. The
    # SCPI server does not acknowledge set commands, so a set does not read back.
    #
    # One acquisition by hand: start_acquisition(), set_trigger_source("NOW") - the trigger is
    # armed by that command and only after ACQ:START -, poll get_trigger_status() until "TD",
    # poll get_buffer_filled() until True (OS 2.x), then get_data(channel, samples) and
    # stop_acquisition(). The trigger sits in the middle of the buffer.
    # Reference:
    # https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/command_list/commands-acq.html

    def reset_acquisition(self) -> None:
        """Stop the acquisition and reset all acquisition parameters to their defaults ('ACQ:RST')."""
        self.port.write("ACQ:RST")

    def start_acquisition(self) -> None:
        """Start the acquisition ('ACQ:START'); the trigger is armed separately."""
        self.port.write("ACQ:START")

    def stop_acquisition(self) -> None:
        """Stop the acquisition ('ACQ:STOP')."""
        self.port.write("ACQ:STOP")

    def set_decimation(self, decimation: int) -> None:
        """Set the decimation, a power of two from 1 to 65536 ('ACQ:DEC').

        The sample rate is 125 MHz / decimation; the 16384-sample buffer then spans
        16384 * decimation / 125 MHz.
        """
        self.port.write("ACQ:DEC {0}".format(int(decimation)))

    def get_decimation(self) -> int:
        """Return the decimation."""
        return int(self.port.query("ACQ:DEC?"))

    def set_averaging(self, enabled: bool) -> None:
        """Switch averaging of the decimated samples on or off ('ACQ:AVG')."""
        self.port.write("ACQ:AVG {0}".format("ON" if enabled else "OFF"))

    def get_averaging(self) -> bool:
        """Return whether the decimated samples are averaged."""
        return self.port.query("ACQ:AVG?").strip().upper() in ("ON", "1")

    def set_data_units(self, units: str) -> None:
        """Set the units of the returned data: VOLTS or RAW (ADC counts) ('ACQ:DATA:UNITS')."""
        self.port.write("ACQ:DATA:UNITS {0}".format(str(units).upper()))

    def get_data_units(self) -> str:
        """Return the units of the returned data, 'VOLTS' or 'RAW'."""
        return self.port.query("ACQ:DATA:UNITS?")

    def get_buffer_size(self) -> int:
        """Return the size of the data buffer in samples ('ACQ:BUF:SIZE?')."""
        return int(self.port.query("ACQ:BUF:SIZE?"))

    def set_gain(self, channel: int, gain: str) -> None:
        """Select the input range an input is calibrated for: LV (+/- 1 V) or HV (+/- 20 V).

        ('ACQ:SOUR<n>:GAIN'.) On a STEMlab this switches nothing in hardware - the range is set
        by the jumper behind the SMA connector - it only selects the calibration used to convert
        ADC counts into volts. The GUI names "Low voltage"/"High voltage" are accepted as well.
        """
        gain = self.commands.get(gain, str(gain).upper())
        self.port.write("ACQ:SOUR{0}:GAIN {1}".format(channel, gain))

    def get_gain(self, channel: int) -> str:
        """Return the input range setting of an input, 'LV' or 'HV'."""
        return self.port.query("ACQ:SOUR{0}:GAIN?".format(channel))

    def set_trigger_source(self, source: str) -> None:
        """Set the trigger source, which arms the trigger ('ACQ:TRIG').

        Sources: DISABLED, NOW, CH1_PE, CH1_NE, CH2_PE, CH2_NE, EXT_PE, EXT_NE, AWG_PE, AWG_NE.
        This must happen after start_acquisition(). The manufacturer's acquisition example states
        "Trigger source command must be set after ACQ:START". Arming while the acquisition is
        stopped is lost, which makes every acquisition after the first one run into the trigger
        timeout.
        """
        self.port.write("ACQ:TRIG {0}".format(str(source).upper()))

    def get_trigger_status(self) -> str:
        """Return the trigger status: 'WAIT' until the trigger fires, 'TD' afterwards."""
        return self.port.query("ACQ:TRIG:STAT?")

    def set_trigger_level(self, level: float) -> None:
        """Set the trigger level in V ('ACQ:TRIG:LEV')."""
        self.port.write("ACQ:TRIG:LEV {0}".format(float(level)))

    def get_trigger_level(self) -> float:
        """Return the trigger level in V."""
        return float(self.port.query("ACQ:TRIG:LEV?"))

    def set_trigger_hysteresis(self, hysteresis: float) -> None:
        """Set the trigger hysteresis in V ('ACQ:TRIG:HYST')."""
        self.port.write("ACQ:TRIG:HYST {0}".format(float(hysteresis)))

    def get_trigger_hysteresis(self) -> float:
        """Return the trigger hysteresis in V."""
        return float(self.port.query("ACQ:TRIG:HYST?"))

    def set_trigger_delay(self, samples: int) -> None:
        """Set the trigger delay in samples ('ACQ:TRIG:DLY').

        It positions the buffer relative to the trigger event: 0 puts the trigger in the middle
        (8192 samples before, 8192 after), half the buffer size puts it at the start.
        """
        self.port.write("ACQ:TRIG:DLY {0}".format(int(samples)))

    def get_trigger_delay(self) -> int:
        """Return the trigger delay in samples."""
        return int(self.port.query("ACQ:TRIG:DLY?"))

    def get_buffer_filled(self) -> bool:
        """Return whether the buffer has been filled after the trigger event ('ACQ:TRig:FILL?', OS 2.00 and up)."""
        return self.port.query("ACQ:TRig:FILL?").strip() == "1"

    def get_trigger_position(self) -> int:
        """Return the buffer position of the trigger event ('ACQ:TPOS?')."""
        return int(self.port.query("ACQ:TPOS?"))

    def get_write_position(self) -> int:
        """Return the current write position in the buffer ('ACQ:WPOS?')."""
        return int(self.port.query("ACQ:WPOS?"))

    def get_data(self, channel: int, samples: int) -> list:
        """Return the oldest 'samples' samples of an input's buffer ('ACQ:SOUR<n>:DATA:OLD:N?').

        This is the trace from the start of the buffer, i.e. what an acquisition recorded; in
        the units selected with set_data_units.
        """
        answer = self.port.query("ACQ:SOUR{0}:DATA:OLD:N? {1}".format(channel, int(samples)))
        return self._parse_data(answer, channel)

    def get_latest_data(self, channel: int, samples: int) -> list:
        """Return the newest 'samples' samples of an input's buffer ('ACQ:SOUR<n>:DATA:LAT:N?')."""
        answer = self.port.query("ACQ:SOUR{0}:DATA:LAT:N? {1}".format(channel, int(samples)))
        return self._parse_data(answer, channel)

    def get_buffer(self, channel: int) -> list:
        """Return the whole buffer of an input ('ACQ:SOUR<n>:DATA?'), 16384 samples."""
        answer = self.port.query("ACQ:SOUR{0}:DATA?".format(channel))
        return self._parse_data(answer, channel)

    def get_settings(self) -> dict:
        """Return the current acquisition settings as a dictionary."""
        return {
            "data_units": self.get_data_units(),
            "buffer_size": self.get_buffer_size(),
            "decimation": self.get_decimation(),
            "averaging": self.get_averaging(),
            "trigger_level": self.get_trigger_level(),
            "trigger_hysteresis": self.get_trigger_hysteresis(),
            "trigger_delay": self.get_trigger_delay(),
            "trigger_status": self.get_trigger_status(),
            "gain_1": self.get_gain(1),
            "gain_2": self.get_gain(2),
        }

    def get_identification(self) -> str:
        """Return the '*IDN?' string of the board."""
        return self.port.query("*IDN?")

    def get_system_version(self) -> str:
        return self.port.query("SYST:VERS?")
