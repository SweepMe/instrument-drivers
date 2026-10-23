# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2020 - 2021 Axel Fischer (sweep-me.net)
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
# Type: LCRmeter
# Device: ZurichInstruments MFIA

import numpy as np

from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()  # needed to import zhinst from libs folder of this device class

from zhinst import ziPython as ziP
__api_level__ = 6 #developed on 6

from collections import OrderedDict

import time

from pysweepme.ErrorMessage import error

from pysweepme.EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "MFIA"

        self.variables = ["R", "X", "Frequency", "Voltage bias"]
        self.units     = ["Ohm", "Ohm", "Hz", "V"]
        self.plottype  = [True, True, True, True] # True to plot data
        self.savetype  = [True, True, True, True] # True to save data

        self.timeout_autorange = 20 # in s
        self.sampling_rate = 10.0 # in 1/s

        # Sources that can supply the DC bias across the device under test, see doc/description.md
        # "Internal":         internal bias source of the instrument, nodes /imps/0/bias/*
        # "Aux Output (cable to Aux In 1)": DC level of an Auxiliary Output, added to the Signal Output
        # "External":         bias is supplied by another instrument, this driver does not change any bias node
        self.bias_sources = ["Internal", "Aux Output (cable to Aux In 1)", "External"]
        self.aux_outputs = ["1", "2", "3", "4"]

        self.bias_source = "Internal"
        self.aux_output_index = 0  # zero-based index of the Auxiliary Output used as bias source

        # Output voltage ranges of the Signal Output in V. The range must cover drive amplitude plus DC bias,
        # otherwise the instrument clamps the bias silently, e.g. to +/-1 V in the 1 V range.
        self.output_ranges = [0.01, 0.1, 1.0, 10.0]
        self.output_range = None  # output range in V set during the current run, None if not yet set

        self.bias_tolerance = 1e-3  # in V, maximum deviation of the bias read back from the requested bias

    def find_Ports(self):
        '''use ZI api to find IDs of all devices it can access - USB comm requires driver install'''

        dev_explorer = ziP.ziDiscovery()
        devs = dev_explorer.findAll()

        return devs

    def set_GUIparameter(self):

        GUIparameter = {


            "SweepMode": ["None", "Frequency in Hz", "Voltage bias in V", "Current bias in A"],
            "StepMode": ["None", "Frequency in Hz", "Voltage bias in V", "Current bias in A"],

            "ValueTypeRMS": ["Voltage RMS in V:", "Current RMS in A:"],
            "ValueRMS": 0.02,

            "ValueTypeBias": ["Voltage bias in V:" , "Current bias in A:"],
            "ValueBias": 0.0,

            "BiasSource": self.bias_sources,
            "BiasAuxOutput": self.aux_outputs,

            "Frequency": 1000.0,

            "OperatingMode": ["4-Terminal", "2-Terminal"],


            "Average": ["1", "2", "4", "8", "16", "32", "64"],
            # "ALC": ["On", "Off"],
            "Integration": ["Short -> medium precision", "Medium -> high precision ", "Long -> very high precision"],

            # "Trigger": ["Internal", "External"],
        }


        return GUIparameter

    def get_GUIparameter(self, parameter = {}):

        self.devID = str(parameter["Port"]).lower()

        self.sweepmode = parameter['SweepMode']
        self.stepmode = parameter['StepMode']

        self.ValueTypeRMS = parameter['ValueTypeRMS']
        self.ValueRMS = float(parameter['ValueRMS'])

        self.ValueTypeBias = parameter['ValueTypeBias']
        self.ValueBias = float(parameter['ValueBias'])

        # .get() with defaults so that settings saved before these fields existed still load
        self.bias_source = parameter.get('BiasSource', "Internal")
        self.aux_output_index = int(parameter.get('BiasAuxOutput', "1")) - 1

        # self.ALC = parameter['ALC']
        self.integration = parameter['Integration']
        self.average = int(parameter['Average'])
        self.frequency = float(parameter['Frequency'])

        self.OperatingMode = 0 if parameter['OperatingMode'] == "4-Terminal" else 1

        # self.trigger_type = parameter["Trigger"]



    def connect(self):
        dev_explorer = ziP.ziDiscovery()
        dev_explorer.find(self.devID)
        cpars = dev_explorer.get(self.devID)
        if cpars ['apilevel'] != __api_level__:
            print("MFIA warning: api level %s does not match driver level %s" % (cpars['apilevel'], __api_level__))

        # The zhinst-core library shipped with the driver rarely has exactly the version of the LabOne installation
        # on the user's computer, and the Data Server refuses the connection in that case unless mismatches are
        # allowed explicitly.
        try:
            self.daq = ziP.ziDAQServer(cpars['serveraddress'], cpars['serverport'], cpars['apilevel'],
                                       allow_version_mismatch=True)
        except TypeError:
            # old ziPython versions (Python 3.6, 32 bit) do not know the argument 'allow_version_mismatch'
            self.daq = ziP.ziDAQServer(cpars['serveraddress'], cpars['serverport'], cpars['apilevel'])
        self.daq.connectDevice(self.devID, cpars['interfaces'][0]) #blocking

        self.polling_topic = '/%s/imps/0/sample' % (self.devID)


    def disconnect(self):
        if self.daq:
            self.daq.disconnectDevice(self.devID)

    def initialize(self):

        imp_index = 0
        self.curr_index = self.daq.getInt("/%s/imps/%d/current/inputselect" % (self.devID, imp_index))
        self.volt_index = self.daq.getInt("/%s/imps/%d/voltage/inputselect" % (self.devID, imp_index))


    def configure(self):

        self.check_bias_configuration()

        self.output_range = None  # the output range is chosen anew for each configure

        retries = 5
        for i in range(retries):
            if self.subscribe_polling_topic():
                break # we can go ahead if the subscribing worked

            if i == retries-1: # If there was no success, we stop the measurement at the last retry
                self.stop_Measurement("Unable to subscribe to topic during configure with %i retries" % retries)
                return False


        # we first collect all settings in a list and send it at the end set them at the end of this function
        settings = []



        # integration and average
        if self.integration.startswith("Short"):
            settings += [
                ['/%s/system/impedance/precision' % (self.devID), 0],
            ]
        elif self.integration.startswith("Medium"):
            settings += [
                ['/%s/system/impedance/precision' % (self.devID), 1],
            ]
        elif self.integration.startswith("Long"):
            settings += [
                ['/%s/system/impedance/precision' % (self.devID), 2],
            ]



        # Cable correction
        settings += [
            ['/%s/system/impedance/calib/cablelength' % (self.devID), 0],  # cable length correction switched off, feature can be added/changed later
        ]
        #
        #      #ALC
        #      settings += [
        #                      ['/%s/????' % (self.devID), 1],
        #                  ]



        settings += [
            ['/%s/imps/0/enable' % (self.devID), 1],                        # enable impedance measurement, necessary if MFLI is used or if it was disabled beforehand.
            ['/%s/imps/0/mode' % (self.devID), self.OperatingMode],         # 4-Terminal (0) or 2-Terminal (1)
            ['/%s/imps/0/auto/inputrange' % (self.devID), 1],               # inputrange is dynamically adjusted for best measurements

            ['/%s/demods/0/rate' % (self.devID), self.sampling_rate],       # Sampling rate in 1/s

            ['/%s/imps/0/auto/bw' % (self.devID), 1],                       # automatic bw
            ['/%s/imps/0/freq' % (self.devID), self.frequency],             # oscillator frequency
        ]

        # The output range must be set before amplitude and bias, as both are clamped to the active range
        settings += self.get_output_range_settings(self.ValueBias)

        settings += [
            ['/%s/imps/0/auto/output' % (self.devID), 0],                   # drive amplitude set manually, otherwise the instrument overwrites it
            ['/%s/imps/0/output/amplitude' % (self.devID), self.ValueRMS],  # oscillator signal
        ]

        # DC bias, the nodes depend on the bias source selected by the user
        settings += self.get_bias_setup_settings()
        settings += self.get_bias_value_settings(self.ValueBias)





        #      # trigger
        #      if self.trigger_type == "Internal":
        #          settings += [
        #                          ['/%s/????' % (self.devID), 1],
        #                      ]
        #      elif self.trigger_type == "External":
        #          settings += [
        #                          ['/%s/????' % (self.devID), 1],
        #                      ]
        #      else:
        #          settings += [
        #                          ['/%s/????' % (self.devID), 1],
        #                      ]


        self.daq.set(settings)
        self.daq.sync()

        self.verify_bias_value(self.ValueBias)

        self.time_constant = self.daq.getDouble('/%s/demods/0/timeconstant' % self.devID)


    def unconfigure(self):

        self.daq.unsubscribe('*')  # unsubscribing all topics

        settings = [
            ['/%s/imps/0/output/amplitude' % (self.devID), 0.02], # oscillator signal back to small value
        ]

        settings += self.get_bias_reset_settings()  # bias back to 0 V and bias source switched off

        self.daq.set(settings)
        self.daq.sync()

    def poweron(self):


        settings = [
            ['/%s/imps/0/output/on' % (self.devID), 1],        # output on
        ]

        self.daq.set(settings)
        self.daq.sync()


    def poweroff(self):

        settings = [
            ['/%s/imps/0/output/on' % (self.devID), 0],        # output off
        ]

        self.daq.set(settings)
        self.daq.sync()


    def apply(self):

        settings = []
        bias_value = None  # new DC bias in V, None if the bias does not change

        if self.sweepmode != "None":

            self.sweepvalue = float(self.value)

            if self.sweepmode.startswith("Frequency"):

                settings += [
                    ['/%s/imps/0/freq' % (self.devID), self.sweepvalue],
                ]

                self.frequency = self.sweepvalue

                if "bias" in self.stepmode:

                    self.stepvalue = float(self.stepvalue)

                    bias_value = self.stepvalue

            else:

                bias_value = self.sweepvalue

                if self.stepmode.startswith("Frequency"):
                    self.stepvalue = float(self.stepvalue)

                    settings += [
                        ['/%s/imps/0/freq' % (self.devID), self.stepvalue],
                    ]

                    self.frequency = self.stepvalue

        if bias_value is not None:
            # the output range must be widened before the bias is written, otherwise the bias is clamped
            settings += self.get_output_range_settings(bias_value)
            settings += self.get_bias_value_settings(bias_value)

        if len(settings) > 0:
            self.daq.set(settings)
            self.daq.sync()

            if bias_value is not None:
                self.verify_bias_value(bias_value)

            self.time_constant = self.daq.getDouble('/%s/demods/0/timeconstant' % self.devID)

            # print("Time constant:", self.time_constant)

    def adapt(self):

        ## 1. we make sure the range is correct
        ## even if 'apply' is not called, external changes might necessitate to trigger autorange again
        trigger_auto_ranging = [
            ["/%s/currins/%d/autorange" % (self.devID, self.curr_index), 1],
            ["/%s/sigins/%d/autorange" % (self.devID, self.volt_index), 1],
        ]

        self.daq.set(trigger_auto_ranging)

        t_start = time.time()

        finished = False

        while not finished:
            time.sleep(0.01) # to proceed as soon as possible if autoranging has finished
            currins_autorange = self.daq.getInt("/%s/currins/%d/autorange" % (self.devID, self.curr_index))
            sigins_autorange = self.daq.getInt("/%s/sigins/%d/autorange" % (self.devID, self.volt_index))

            # We are finished when both nodes have been set back to 0 by the device.
            finished = (currins_autorange == 0) and (sigins_autorange == 0)

            if time.time() - t_start > self.timeout_autorange:
                self.stop_Measurement("Unable to autorange before timeout.")
                return False

        ## 2. We poll a new value to make sure new values have been arrived
        self.daq.sync() #  needed to empty the buffer

        poll_length = 0.01  # in s, we poll quickly as we want to know when the first value is available
        poll_timeout = 5000  # in ms, in case there is no value, we wait 5000 ms to wait for a new value
        poll_flags = 0
        poll_return_flat_dict = True
        data = self.daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)

        ## 3. after a new value can be polled, we have to wait for the settling time to have good values in 'measure'
        time.sleep(16.0 * self.time_constant)

    def measure(self):

        self.daq.sync() #  needed to empty the buffer, as we don't want to have values from the settling process

        poll_length = (self.average+0.1)/self.sampling_rate # we poll as many values as needed to do the average. 0.1 is added to make sure we have exactly the number of values for averaging or even one more.
        poll_timeout = 10000  # [ms] # in case there is no value, we wait 10000 ms to wait for a new value
        poll_flags = 0
        poll_return_flat_dict = True
        data = self.daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)

        Z = np.mean(data[self.polling_topic]['z']) # we take the average of all polled values

        self.R = Z.real
        self.X = Z.imag
        self.F = np.mean(data[self.polling_topic]['frequency']) # we take the last frequency value
        self.Bias = self.get_bias_value()


    def call(self):
        return [self.R, self.X, self.F, self.Bias]


    """ convenience functions """

    def check_bias_configuration(self):
        """Check whether the requested bias can be applied by the selected bias source.

        None of the bias sources of this instrument can source a current, and an external bias source
        cannot be swept by this driver.
        """

        bias_is_used = self.bias_source != "External" or "bias" in self.sweepmode or "bias" in self.stepmode

        if not bias_is_used:
            return

        bias_types = [self.ValueTypeBias]
        if "bias" in self.sweepmode:
            bias_types.append(self.sweepmode)
        if "bias" in self.stepmode:
            bias_types.append(self.stepmode)

        if any(bias_type.startswith("Current") for bias_type in bias_types):
            raise ValueError("The Zurich Instruments MFIA driver can only apply a voltage bias. "
                             "Please select 'Voltage bias in V' instead of 'Current bias in A'.")

        if self.bias_source == "External" and ("bias" in self.sweepmode or "bias" in self.stepmode):
            raise ValueError("The bias source 'External' means that the bias is applied by another instrument, "
                             "so this driver cannot sweep it. Please choose the bias source 'Internal' or "
                             "'Aux Output (cable to Aux In 1)', or sweep the bias with the driver of the "
                             "biasing instrument.")

    def get_bias_setup_settings(self):
        """Return the settings that switch on the selected bias source. Sent once during 'configure'."""

        if self.bias_source == "Internal":
            return [
                # the bias value alone has no effect, the bias source must be enabled explicitly
                ['/%s/imps/0/bias/enable' % (self.devID), 1],
            ]

        if self.bias_source.startswith("Aux Output"):
            return [
                # the Auxiliary Output must output a static level, otherwise a signal is added to the bias
                ['/%s/auxouts/%d/outputselect' % (self.devID, self.aux_output_index), -1],  # -1 = Manual
                ['/%s/auxouts/%d/preoffset' % (self.devID, self.aux_output_index), 0.0],
                ['/%s/auxouts/%d/scale' % (self.devID, self.aux_output_index), 1.0],
                # adds the signal that is present at Aux Input 1 to the Signal Output
                ['/%s/sigouts/0/add' % (self.devID), 1],
            ]

        return []  # "External", the bias is applied by another instrument

    def get_bias_value_settings(self, value):
        """Return the settings that apply the bias 'value' in V using the selected bias source."""

        if self.bias_source == "Internal":
            return [
                ['/%s/imps/0/bias/value' % (self.devID), float(value)],
            ]

        if self.bias_source.startswith("Aux Output"):
            return [
                ['/%s/auxouts/%d/offset' % (self.devID, self.aux_output_index), float(value)],
            ]

        return []  # "External", the bias is applied by another instrument

    def get_bias_reset_settings(self):
        """Return the settings that set the bias back to 0 V and switch the bias source off."""

        if self.bias_source == "Internal":
            return [
                ['/%s/imps/0/bias/value' % (self.devID), 0.0],
                ['/%s/imps/0/bias/enable' % (self.devID), 0],
            ]

        if self.bias_source.startswith("Aux Output"):
            return [
                ['/%s/auxouts/%d/offset' % (self.devID, self.aux_output_index), 0.0],
                ['/%s/sigouts/0/add' % (self.devID), 0],
            ]

        return []  # "External", the bias is applied by another instrument

    def get_bias_value(self):
        """Return the DC bias in V that is currently set at the selected bias source."""

        if self.bias_source == "Internal":
            return self.daq.getDouble('/%s/imps/0/bias/value' % (self.devID))

        if self.bias_source.startswith("Aux Output"):
            return self.daq.getDouble('/%s/auxouts/%d/offset' % (self.devID, self.aux_output_index))

        return float('nan')  # "External", the applied bias is unknown to this driver

    def get_output_range_settings(self, bias):
        """Return the setting that selects an output range wide enough for drive amplitude plus DC bias 'bias' in V.

        The bias of the sources "Internal" and "Aux Output" is added as an offset to the Signal Output, and the
        output range must cover the sum of drive amplitude and offset. If the range is too small, the instrument
        clamps the bias without any error, e.g. to +/-1 V in the 1 V range.

        The range is only increased within a run, so that a bias sweep does not switch the output back and forth.
        An empty list is returned if the active range is already sufficient.
        """

        # The drive amplitude is treated as RMS value, so its peak value is used as worst case.
        required_voltage = 2 ** 0.5 * abs(self.ValueRMS)
        if self.bias_source != "External":
            required_voltage += abs(float(bias))

        if required_voltage > self.output_ranges[-1]:
            msg = ("The MFIA cannot apply a DC bias of %s V together with a drive amplitude of %s V, as the sum "
                   "exceeds the largest output range of %s V. Please reduce bias or drive amplitude, or use an "
                   "external bias tee." % (bias, self.ValueRMS, self.output_ranges[-1]))
            raise ValueError(msg)

        new_range = min(output_range for output_range in self.output_ranges if output_range >= required_voltage)

        if self.output_range is not None and new_range <= self.output_range:
            return []

        self.output_range = new_range

        return [
            ['/%s/imps/0/output/range' % (self.devID), new_range],
        ]

    def verify_bias_value(self, bias):
        """Check that the instrument really applies the requested DC bias 'bias' in V.

        The instrument does not report an error for a bias outside its limits, it clamps the value instead.
        Without this check, the measurement would continue at a wrong bias.
        """

        if self.bias_source == "External":
            return

        applied_bias = self.get_bias_value()

        if abs(applied_bias - float(bias)) > self.bias_tolerance:
            msg = ("The MFIA did not apply the requested DC bias of %s V, it reports %s V instead. The bias is "
                   "limited by the output range and, in 4-Terminal mode, by the common mode input range of about "
                   "+/-3 V. Please use 2-Terminal mode or an external bias tee for larger bias voltages."
                   % (bias, applied_bias))
            raise ValueError(msg)

    def subscribe_polling_topic(self):
        """ subscribe to the polling topic """

        try:
            # self.daq.getAsEvent(self.polling_topic)
            self.daq.subscribe(self.polling_topic)
            return True
        except:
            error("Unable to subscribe polling topic of Zurich Instrument MFIA") # prints the error message
            return False