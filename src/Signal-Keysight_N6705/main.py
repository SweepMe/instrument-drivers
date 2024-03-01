# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2022 Gennaro Tortone (Istituto Nazionale di Fisica Nucleare - Sezione di Napoli - tortone@na.infn.it)
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
# Type: Signal
# Device: Keysight N6705

from EmptyDeviceClass import EmptyDevice
from ErrorMessage import debug


class Device(EmptyDevice):

    description =   """
                        Keysight N6705
                        DC power analyzer
                    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.port_manager = True
        self.port_types = ["TCPIP", "GPIB"]
        self.port_properties = {
            "EOL": "\n",
        }

        self.PERIOD = "Period in s"
        self.FREQUENCY = "Frequency in Hz"
        self.AMPLITUDE = "Amplitude in V"
        self.HILEVEL = "High level in V"
        self.OFFSET = "Offset in V"
        self.LOLEVEL = "Low level in V"
        self.PHASE = "Phase in deg"
        self.DELAY = "Delay in s"
        self.DUTYCYCLE = "Duty cycle in %"
        self.PULSEWIDTH = "Pulse width in s"
        self.RISETIME = "RiseTime"
        self.FALLTIME = "FallTime"
        #
        self.NSTEPS = "Number of steps"
        self.TCONSTANT = "Time constant"
        #
        self.ENDTIME = "End time in s"          # not available on GUI

        self.waveforms = dict()
        # Sine
        self.waveforms['Sine'] = dict()
        self.waveforms['Sine']['label'] = "SIN"
        self.waveforms['Sine'][self.FREQUENCY] = dict({"command": "FREQ", "unit": "Hz"})
        self.waveforms['Sine'][self.AMPLITUDE] = dict({"command": "AMPL", "unit": "V"})
        self.waveforms['Sine'][self.OFFSET] = dict({"command": "OFFSET", "unit": "V"})
        # Step
        self.waveforms['Step'] = dict()
        self.waveforms['Step']['label'] = "STEP"
        self.waveforms['Step'][self.DELAY] = dict({"command": "START:TIME", "unit": "s"})
        self.waveforms['Step'][self.LOLEVEL] = dict({"command": "START:LEVEL", "unit": "V"})
        self.waveforms['Step'][self.HILEVEL] = dict({"command": "END:LEVEL", "unit": "V"})
        # Ramp
        self.waveforms['Ramp'] = dict()
        self.waveforms['Ramp']['label'] = "RAMP"
        self.waveforms['Ramp'][self.DELAY] = dict({"command": "START:TIME", "unit": "s"})
        self.waveforms['Ramp'][self.LOLEVEL] = dict({"command": "START:LEVEL", "unit": "V"})
        self.waveforms['Ramp'][self.RISETIME] = dict({"command": "RTIME", "unit": "s"})
        self.waveforms['Ramp'][self.ENDTIME] = dict({"command": "END:TIME", "unit": "s"})
        self.waveforms['Ramp'][self.HILEVEL] = dict({"command": "END:LEVEL", "unit": "V"})
        # Staircase
        self.waveforms['Staircase'] = dict()
        self.waveforms['Staircase']['label'] = "STAIRCASE"
        self.waveforms['Staircase'][self.DELAY] = dict({"command": "START:TIME", "unit": "s"})
        self.waveforms['Staircase'][self.LOLEVEL] = dict({"command": "START:LEVEL", "unit": "V"})
        self.waveforms['Staircase'][self.RISETIME] = dict({"command": "TIME", "unit": "s"})
        self.waveforms['Staircase'][self.NSTEPS] = dict({"command": "NSTEPS", "unit": "num"})
        self.waveforms['Staircase'][self.ENDTIME] = dict({"command": "END:TIME", "unit": "s"})
        self.waveforms['Staircase'][self.HILEVEL] = dict({"command": "END:LEVEL", "unit": "V"})
        # Pulse
        self.waveforms['Pulse'] = dict()
        self.waveforms['Pulse']['label'] = "PULSE"
        self.waveforms['Pulse'][self.DELAY] = dict({"command": "START:TIME", "unit": "s"})
        self.waveforms['Pulse'][self.LOLEVEL] = dict({"command": "START:LEVEL", "unit": "V"})
        self.waveforms['Pulse'][self.PULSEWIDTH] = dict({"command": "TOP:TIME", "unit": "s"})
        self.waveforms['Pulse'][self.HILEVEL] = dict({"command": "TOP:LEVEL", "unit": "V"})
        self.waveforms['Pulse'][self.ENDTIME] = dict({"command": "END:TIME", "unit": "s"})
        # Trapezoid
        self.waveforms['Trapezoid'] = dict()
        self.waveforms['Trapezoid']['label'] = "TRAPEZOID"
        self.waveforms['Trapezoid'][self.DELAY] = dict({"command": "START:TIME", "unit": "s"})
        self.waveforms['Trapezoid'][self.LOLEVEL] = dict({"command": "START:LEVEL", "unit": "V"})
        self.waveforms['Trapezoid'][self.RISETIME] = dict({"command": "RTIME", "unit": "s"})
        self.waveforms['Trapezoid'][self.PULSEWIDTH] = dict({"command": "TOP:TIME", "unit": "s"})
        self.waveforms['Trapezoid'][self.HILEVEL] = dict({"command": "TOP:LEVEL", "unit": "V"})
        self.waveforms['Trapezoid'][self.FALLTIME] = dict({"command": "FTIME", "unit": "s"})
        self.waveforms['Trapezoid'][self.ENDTIME] = dict({"command": "END:TIME", "unit": "s"})
        # Exponential
        self.waveforms['Exponential'] = dict()
        self.waveforms['Exponential']['label'] = "EXP"
        self.waveforms['Exponential'][self.DELAY] = dict({"command": "START:TIME", "unit": "s"})
        self.waveforms['Exponential'][self.LOLEVEL] = dict({"command": "START:LEVEL", "unit": "V"})
        self.waveforms['Exponential'][self.RISETIME] = dict({"command": "TIME", "unit": "s"})
        self.waveforms['Exponential'][self.TCONSTANT] = dict({"command": "TCONSTANT", "unit": "s"})
        self.waveforms['Exponential'][self.HILEVEL] = dict({"command": "END:LEVEL", "unit": "V"})

    def set_GUIparameter(self):
        GUIparameter = {
            "SweepMode": [self.PERIOD, self.FREQUENCY, self.AMPLITUDE, self.HILEVEL, self.OFFSET,  self.LOLEVEL, self.PHASE, \
                self.DELAY, self.DUTYCYCLE, self.PULSEWIDTH, self.RISETIME, self.FALLTIME, self.NSTEPS,  self.TCONSTANT, "None"],
            "Channel": ["1", "2", "3", "4"],
            "Waveform": list(self.waveforms.keys()),
            "PeriodFrequency": [self.PERIOD, self.FREQUENCY],
            "AmplitudeHiLevel": [self.AMPLITUDE, self.HILEVEL],
            "OffsetLoLevel": [self.OFFSET, self.LOLEVEL],
            "DelayPhase": [self.PHASE, self.DELAY],
            "DutyCyclePulseWidth": [self.DUTYCYCLE, self.PULSEWIDTH, self.NSTEPS, self.TCONSTANT],
            "PeriodFrequencyValue": 2,
            "AmplitudeHiLevelValue": 1.0,
            "OffsetLoLevelValue": 0.0,
            "DelayPhaseValue": 10,
            "DutyCyclePulseWidthValue": 5,
            self.RISETIME: 1,
            self.FALLTIME: 1
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):
        self.sweep_mode = parameter['SweepMode'] 
        self.waveform = parameter['Waveform']
        
        self.periodfrequency          = parameter['PeriodFrequency' ]
        self.periodfrequencyvalue     = float(parameter['PeriodFrequencyValue'])
        self.amplitudehilevel         = parameter['AmplitudeHiLevel']
        self.amplitudehilevelvalue    = float(parameter['AmplitudeHiLevelValue'])
        self.offsetlolevel            = parameter['OffsetLoLevel']
        self.offsetlolevelvalue       = float(parameter['OffsetLoLevelValue'])
        self.delayphase               = parameter['DelayPhase']
        self.delayphasevalue          = float(parameter['DelayPhaseValue'])
        self.dutycyclepulsewidth      = parameter['DutyCyclePulseWidth']
        self.dutycyclepulsewidthvalue = float(parameter['DutyCyclePulseWidthValue'])
        self.risetime                 = float(parameter['RiseTime'])
        self.falltime                 = float(parameter['FallTime'])

        self.device = parameter['Device']
        self.channel = parameter['Channel']
        self.shortname = "Keysight N6705 CH" + self.channel

        self.variables = ['Voltage in V', 'Current in A']
        self.units = ['V', 'A']
        self.plottype = [True, True]
        self.savetype = [True, True]
        
    def initialize(self):

        # once at the beginning of the measurement
        self.port.write("*RST")

    def deinitialize(self):
        pass

    def poweron(self):
        # TODO: include current operation mode
        self.port.write(f"VOLT:MODE ARB, (@{self.channel})")
        self.port.write(f"ARB:FUNC:TYPE VOLT, (@{self.channel})")
        self.port.write(f"ARB:FUNC:SHAPE {self.waveforms[self.waveform]['label']}, (@{self.channel})")
        # TODO: number of signal repetitions
        self.port.write(f"ARB:COUNT INF, (@{self.channel})")
        self.port.write(f"TRIG:ARB:SOURCE IMM")
        self.port.write(f"OUTP ON, (@{self.channel})")
        self.port.write(f"INIT:TRAN (@{self.channel})")

    def poweroff(self):
        self.port.write(f"OUTP OFF, (@{self.channel})")
        self.port.write(f"ABORT:TRAN (@{self.channel})")

    def set_parameter(self, param, value):
        arb_prefix = f"ARB:VOLTAGE:{self.waveforms[self.waveform]['label']}"
        if self.waveforms[self.waveform].get(param, False):
            self.port.write(f"{arb_prefix}:{self.waveforms[self.waveform][param]['command']} {value}, (@{self.channel}); *WAI")
            return True
        else: return False

    def configure(self):
        if self.waveform == 'Sine':
            self.set_sine_params()
        elif self.waveform == 'Step':
            self.set_step_params()
        elif self.waveform == 'Ramp':
            self.set_ramp_params()
        elif self.waveform == 'Staircase':
            self.set_staircase_params()
        elif self.waveform == 'Pulse':
            self.set_pulse_params()
        elif self.waveform == 'Trapezoid':
            self.set_trapezoid_params()
        elif self.waveform == 'Exponential':
            self.set_exponential_params()
            
    def apply(self):
        if self.sweep_mode == 'None':
            pass
        else:
            self.update_sweep_params(self.value)
            self.port.write(f"ABORT:TRAN (@{self.channel}); *WAI")  # wait for pending abort                       
            self.configure()                                        # reconfigure waveform
            self.port.write(f"INIT:TRAN (@{self.channel})")

    def measure(self):
        # default read voltage and current
        self.port.write(f"MEAS:VOLT? (@{self.channel})")
        self.port.write(f"MEAS:CURR? (@{self.channel})")

    def call(self):
        retarr = []
        retarr.append(float(self.port.read()))      # voltage
        retarr.append(float(self.port.read()))      # current
        
        return retarr

    # convenience functions

    def update_sweep_params(self, value):
        if self.sweep_mode == self.PERIOD or self.sweep_mode == self.FREQUENCY:
            self.periodfrequencyvalue = value
        elif self.sweep_mode == self.AMPLITUDE or self.sweep_mode == self.HILEVEL:
            self.amplitudehilevelvalue = value
        elif self.sweep_mode == self.OFFSET or self.sweep_mode == self.LOLEVEL:
            self.offsetlolevelvalue = value
        elif self.sweep_mode == self.PHASE or self.sweep_mode == self.DELAY:
            self.delayphasevalue = value
        elif self.sweep_mode == self.DUTYCYCLE or self.sweep_mode == self.PULSEWIDTH:
            self.dutycyclepulsewidthvalue = value
        elif self.sweep_mode == self.RISETIME:
            self.risetime = value
        elif self.sweep_mode == self.FALLTIME:
            self.falltime = value
        elif self.sweep_mode == self.NSTEPS:
            None    # fixme
        elif self.sweep_mode == self.TCONSTANT:
            None    # fixme

    # STEP

    def get_step_params(self):
        self.delay = self.delayphasevalue

        # lolevel and offset have same meaning
        self.lolevel = self.offsetlolevelvalue

        if self.amplitudehilevel == self.AMPLITUDE:
            # hilevel = amplitude + lolevel
            self.hilevel = self.amplitudehilevelvalue + self.lolevel
        else:
            self.hilevel = self.amplitudehilevelvalue

        return { self.DELAY: self.delay, self.LOLEVEL: self.lolevel, self.HILEVEL: self.hilevel }

    def set_step_params(self):
        params = self.get_step_params()
        self.set_parameter(self.DELAY, params[self.DELAY])
        self.set_parameter(self.LOLEVEL, params[self.LOLEVEL])
        self.set_parameter(self.HILEVEL, params[self.HILEVEL])

    # RAMP

    def get_ramp_params(self):
        if self.periodfrequency == self.PERIOD:
            self.period = self.periodfrequencyvalue
        else:
            self.period = float(1/self.periodfrequencyvalue)

        if self.delayphase == self.DELAY:
            self.delay = self.delayphasevalue
        else:
            # delay = period * phase / 360
            self.delay = float(self.period * self.delayphasevalue / 360)

        # lolevel and offset have same meaning
        self.lolevel = self.offsetlolevelvalue

        if self.amplitudehilevel == self.AMPLITUDE:
            # hilevel = amplitude + lolevel
            self.hilevel = self.amplitudehilevelvalue + self.lolevel
        else:
            self.hilevel = self.amplitudehilevelvalue

        self.endtime = self.period - self.risetime - self.delay

        return { self.DELAY: self.delay, self.RISETIME: self.risetime, self.ENDTIME: self.endtime, self.LOLEVEL: self.lolevel, self.HILEVEL: self.hilevel, self.PERIOD: self.period }

    def set_ramp_params(self):
        params = self.get_ramp_params()
        self.set_parameter(self.DELAY, params[self.DELAY])
        self.set_parameter(self.RISETIME, params[self.RISETIME])
        self.set_parameter(self.ENDTIME, params[self.ENDTIME])
        self.set_parameter(self.LOLEVEL, params[self.LOLEVEL])
        self.set_parameter(self.HILEVEL, params[self.HILEVEL])

    # STAIRCASE

    def get_staircase_params(self):
        params = self.get_ramp_params()
        self.nsteps = self.dutycyclepulsewidthvalue
        params.update({self.NSTEPS: self.nsteps})
        return params

    def set_staircase_params(self):
        params = self.get_staircase_params()
        self.set_parameter(self.DELAY, params[self.DELAY])
        self.set_parameter(self.RISETIME, params[self.RISETIME])
        self.set_parameter(self.ENDTIME, params[self.ENDTIME])
        self.set_parameter(self.LOLEVEL, params[self.LOLEVEL])
        self.set_parameter(self.HILEVEL, params[self.HILEVEL])
        self.set_parameter(self.NSTEPS, params[self.NSTEPS])
    
    # SINE 

    def get_sine_params(self):
        if self.periodfrequency == self.PERIOD:
            self.frequency = 1 / self.periodfrequencyvalue
        else:
            self.frequency = self.periodfrequencyvalue

        if self.offsetlolevel == self.OFFSET:
            self.offset = self.offsetlolevelvalue
            if self.amplitudehilevel == self.AMPLITUDE:
                self.amplitude = self.amplitudehilevelvalue
            else: # self.amplitudehilevel == self.HILEVEL
                # amplitude = hilevel - offset
                self.amplitude = self.amplitudehilevelvalue - self.offset

        else: # self.offsetlolevel == self.LOLEVEL:
            if self.amplitudehilevel == self.AMPLITUDE:
                self.amplitude = self.amplitudehilevelvalue
                # offset = lolevel + amplitude
                self.offset = self.offsetlolevelvalue + self.amplitudehilevelvalue
            else:   # self.amplitudehilevel == self.HILEVEL
                # amplitude - (hilevel - lolevel) / 2
                self.amplitude = (self.amplitudehilevelvalue - self.offsetlolevelvalue) / 2
                # offset = lolevel + ((hilevel - lolevel) / 2)
                self.offset = self.offsetlolevelvalue + ((self.amplitudehilevelvalue - self.offsetlolevelvalue) / 2)

        return { self.FREQUENCY: self.frequency, self.AMPLITUDE: self.amplitude, self.OFFSET: self.offset }

    def set_sine_params(self):
        params = self.get_sine_params()
        self.set_parameter(self.FREQUENCY, params[self.FREQUENCY])
        self.set_parameter(self.AMPLITUDE, params[self.AMPLITUDE])
        self.set_parameter(self.OFFSET, params[self.OFFSET])

    # PULSE

    def get_pulse_params(self):
        params = self.get_ramp_params()
        # remove parameters not used
        params.pop(self.RISETIME)
        params.pop(self.ENDTIME)
        
        if self.dutycyclepulsewidth == self.PULSEWIDTH:
            self.pulsewidth = self.dutycyclepulsewidthvalue
        elif self.dutycyclepulsewidth == self.DUTYCYCLE:
            # pulsewidth = dutycycle / 100 * period
            self.pulsewidth = self.dutycyclepulsewidthvalue / 100 * params[self.PERIOD]
        
        self.endtime = params[self.PERIOD] - self.pulsewidth - params[self.DELAY]
        
        params.update({self.PULSEWIDTH: self.pulsewidth})
        params.update({self.ENDTIME: self.endtime})

        return params

    def set_pulse_params(self):
        params = self.get_pulse_params()
        self.set_parameter(self.DELAY, params[self.DELAY])
        self.set_parameter(self.LOLEVEL, params[self.LOLEVEL])
        self.set_parameter(self.HILEVEL, params[self.HILEVEL])
        self.set_parameter(self.PULSEWIDTH, params[self.PULSEWIDTH])
        self.set_parameter(self.ENDTIME, params[self.ENDTIME])

    # TRAPEZOID

    def get_trapezoid_params(self):
        params = self.get_pulse_params()

        self.endtime = params[self.PERIOD] - self.risetime - params[self.PULSEWIDTH] - self.falltime
        params.update({self.RISETIME: self.risetime})
        params.update({self.FALLTIME: self.falltime})
        params.update({self.ENDTIME: self.endtime})

        return params

    def set_trapezoid_params(self):
        params = self.get_trapezoid_params()
        self.set_parameter(self.DELAY, params[self.DELAY])
        self.set_parameter(self.LOLEVEL, params[self.LOLEVEL])
        self.set_parameter(self.RISETIME, params[self.RISETIME])
        self.set_parameter(self.HILEVEL, params[self.HILEVEL])
        self.set_parameter(self.PULSEWIDTH, params[self.PULSEWIDTH])
        self.set_parameter(self.FALLTIME, params[self.FALLTIME])
        self.set_parameter(self.ENDTIME, params[self.ENDTIME])

    # EXPONENTIAL

    def get_exponential_params(self):
        params = self.get_ramp_params()
        # remove parameters not used
        params.pop(self.ENDTIME)

        self.tconstant = self.dutycyclepulsewidthvalue
        params.update({self.TCONSTANT: self.tconstant})

        return params

    def set_exponential_params(self):
        params = self.get_exponential_params()
        self.set_parameter(self.DELAY, params[self.DELAY])
        self.set_parameter(self.LOLEVEL, params[self.LOLEVEL])
        self.set_parameter(self.RISETIME, params[self.RISETIME])
        self.set_parameter(self.HILEVEL, params[self.HILEVEL])
        self.set_parameter(self.TCONSTANT, params[self.TCONSTANT])
