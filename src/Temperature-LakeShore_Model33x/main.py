# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)
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
# Type: Temperature
# Device: Lake Shore Model 33x


from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description  = """
                       change communication interface to either RS-232 or GPIB at the temperature controller 
                   """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "Lake Shore 33x"
        
        self.port_manager = True
        self.port_types = ["COM", "GPIB"]
        
        self.port_properties = { "timeout": 1,
                                 "EOL": "\r\n",
                                 "baudrate": 57600,
                                 "bytesize": 7,
                                 "stopbits": 1,
                                 "parity": "O",
                                 "delay": 0.01,  # needed to avoid problems with reading temperature
                                }

        self.heater_ranges = {
            "Off": 0,
            "Low": 1,
            "Medium": 2,
            "High": 3,
            "On": 1,
            "Zones": None,  # no heater range but user can specify to use Zones instead of heater range
        }
              
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "SweepMode": ["None", "Temperature", "Output in %"],  # "Output in %"
                        "Channel": [1, 2, 3, 4],
                        "TemperatureUnit": ["K", "°C", "°F"],
                        "Sensor": ["A", "B", "C", "D"],
                        "HeaterRange": list(self.heater_ranges.keys()),
                        "ZeroPowerAfterSweep": True,
                        "IdleTemperature": "",
                        # "MeasureT": True,
                        "Rate": "",
                        }
                       
        return GUIparameter
                   
    def get_GUIparameter(self, parameter={}):
        # print(parameter)

        if not "HeaterRange" in parameter:
            raise Exception("Please update to the latest Temperature module to use this driver as"
                            " new user interface options are needed")
                
        self.measureT = parameter["MeasureT"]
        self.reachT = parameter["ReachT"]
        # self.setT = parameter["SetT"]
        
        self.sweep_mode = parameter["SweepMode"]
        self.channel = parameter["Channel"]

        self.temperature_unit = parameter["TemperatureUnit"]
        self.sensor = parameter["Sensor"]
        self.ramprate = parameter["Rate"]
        self.heater_range = parameter["HeaterRange"]
        
        self.zero_power_afterwards = parameter["ZeroPowerAfterSweep"]
        self.idle_temperature = parameter["IdleTemperature"]
        
        self.variables = ["Temperature", "Power"]
        self.units =     [self.temperature_unit, "%"]
        self.plottype =  [True, True]  # True to plot data
        self.savetype =  [True, True]  # True to save data

    """ semantic standard functions start here """    
        
    def connect(self):
        pass

    def initialize(self):
           
        self.port.write("*IDN?")
        identification = self.port.read()
        # print("Identification:", identification)

        # Readout all zones
        # for i in range(1,11):
        #     print("Channel %s Zone %i:" % (self.channel, i) , self.get_zone(self.channel, i))

    def deinitialize(self):
        
        if self.zero_power_afterwards:
            outputmode = 0  # Off
            powerup_enable = 0
            # self.set_heater_output_mode(self.channel, outputmode, self.sensor, powerup_enable)
            # self.set_manual_output(self.channel, 0.0)
            self.set_heater_range(self.channel, 0)  # Off

        if self.idle_temperature != "":
            self.set_temperature(self.channel, float(self.idle_temperature))
            
    def configure(self):

        # Range
        if not self.heater_ranges[self.heater_range] is None:
            self.set_heater_range(self.channel, self.heater_ranges[self.heater_range])

        # Output mode
        if self.sweep_mode.startswith("Temperature"):
        
            # Ramp
            if self.ramprate == "":
                self.set_setpoint_ramp_parameter(self.channel, 0, 0.0)
            else:
                self.set_setpoint_ramp_parameter(self.channel, 1, self.ramprate)
                
            if self.heater_ranges[self.heater_range] is None:
                heater_range = 1  # Low
                self.set_heater_range(self.channel, heater_range)  # needed to switch on output in Zones mode
                outputmode = 2  # Zones
            else:
                outputmode = 1  # Closed-loop
                
            powerup_enable = 0
            self.set_heater_output_mode(self.channel, outputmode, self.sensor, powerup_enable)

        elif self.sweep_mode.startswith("Output"):
            outputmode = 3  # Open-loop
            powerup_enable = 0
            self.set_heater_output_mode(self.channel, outputmode, self.sensor, powerup_enable)

        else:
            pass

    def unconfigure(self):
    
        if self.zero_power_afterwards:
            outputmode = 0  # Off
            powerup_enable = 0
            # self.set_heater_output_mode(self.channel, outputmode, self.sensor, powerup_enable)
            # self.set_manual_output(self.channel, 0.0)
            self.set_heater_range(self.channel, 0)  # Off

        if self.idle_temperature != "":
            self.set_temperature(self.channel, float(self.idle_temperature))

    def apply(self):

        self.value = float(self.value)

        if self.sweep_mode == "Temperature":
        
            self.value = float(self.value)

            if self.temperature_unit == "K":         
                pass
            elif self.temperature_unit == "°C":
                # convert setvalue from °C to K
                self.value = float(self.value) + 273.15
            elif self.temperature_unit == "°F":
                # convert setvalue from °F to K
                self.value = 5/9*(float(self.value + 273.15) - 32.0)
         
            self.set_temperature(self.channel, self.value)

        elif self.sweep_mode == "Output in %":
            self.set_manual_output(self.channel, self.value)

    def read_result(self):

        self.temperature_measured = self.get_temperature(self.sensor)
        self.output_power = self.get_heater_output(self.channel)

    def call(self):
        
        return [self.temperature_measured, self.output_power]

    """ button related functions start here """
    
    def measure_temperature(self):
        """ used by reach functionality """

        temperature = self.get_temperature(self.channel)
        
        return temperature

    """ setter/getter functions start here """

    def get_identification(self):

        self.port.write("*IDN?")
        return self.port.read()

    def reset(self):
        self.port.write("*RST")

    def clear(self):

        self.port.write("*CLS")

    def get_temperature(self, input):

        temperature = self.get_temperature_kelvin(input)

        # conversion to selected temperature unit
        if self.temperature_unit == "K":
            pass

        elif self.temperature_unit == "°C":
            # convert temperature from K to °C
            temperature = float(temperature) - 273.15

        elif self.temperature_unit == "°F":
            # convert temperature from K into °F
            temperature = (9.0 / 5 * (float(temperature) - 273.15)) + 32.0

        return temperature

    def get_temperature_kelvin(self, input):

        inputs_dict = {
            "1": "A",
            "2": "B",
            "3": "C",
            "4": "D",
        }

        if str(input) in inputs_dict:
            input = inputs_dict[str(input)]

        self.port.write("KRDG? %s" % str(input))
        answer = self.port.read()

        # this is needed as sometimes accidentally a ";" is returned
        # in this case we read the temperature again
        if answer == ";":
            self.port.write("KRDG? %s" % str(input))
            answer = self.port.read()

        return float(answer)

    def get_temperature_celsius(self, input):

        inputs_dict = {
            "1": "A",
            "2": "B",
            "3": "C",
            "4": "D",
        }

        if str(input) in inputs_dict:
            input = inputs_dict[str(input)]

        self.port.write("CRDG? %s" % str(input))
        answer = self.port.read()

        # this is needed as sometimes accidentally a ";" is returned
        # in this case we read the temperature again
        if answer == ";":
            self.port.write("CRDG? %s" % str(input))
            answer = self.port.read()
        
        return float(answer)

    def set_temperature(self, output, temperature):

        self.port.write("SETP %i %1.3f" % (int(output), float(temperature)))

    def get_temperature_setpoint(self, output, temperature):

        self.port.write("SETP? %i" % (int(output)))
        answer = self.port.read()
        return float(answer)

    def set_manual_output(self, output, power):

        self.port.write("MOUT %i %1.2f" % (int(output), float(power)))

    def get_manual_output(self, output):

        self.port.write("MOUT? %i" % (int(output)))
        answer = self.port.read()
        return float(answer)

    def get_heater_output(self, output):

        self.port.write("HTR? %i" % (int(output)))
        answer = self.port.read()
        return float(answer)

    def set_heater_range(self, output, heater_range):
        """
        Args:
            output: output number (int)
            heater_range: range number (int)
                For outputs 1 and 2: 0 = Off, 1 = Low, 2 = Medium, 3 = High
                For outputs 3 and 4: 0 = Off, 1 = On

        Returns:

        """

        self.port.write("RANGE %i,%i" % (int(output), int(heater_range)))

    def get_heater_range(self, output):

        self.port.write("RANGE? %i" % (int(output)))
        answer = self.port.read()
        return int(answer)

    def set_heater_output_mode(self, output, mode, input, powerup_enable):
        """
        Args:
            output: output number (int)
            mode:
                0 = Off
                1 = Closed Loop PID
                2 = Zone
                3 = Open Loop
                4 = Monitor Out
                5 = Warmup Supply
            input:
            powerup_enable:

        Returns:

        """

        inputs_dict = {
            "A": 1,
            "B": 2,
            "C": 3,
            "D": 4,
        }

        # Sensor input is "A", "B", "C", "D" and must be changed to integer
        if input in inputs_dict:
            input = inputs_dict[input]

        self.port.write("OUTMODE %i,%i,%i,%i" % (int(output), int(mode), int(input), int(powerup_enable)))

    def get_heater_output_mode(self, output):

        """

        Args:
            output:

        Returns:
            int: mode
            int: input
            int: powerup enable
        """

        self.port.write("OUTMODE? %i" % (int(output)))
        answer = self.port.read()
        return list(map(int, answer.split(",")))

    def set_setpoint_ramp_parameter(self, output, ramp_enable, ramprate):

        self.port.write("RAMP %i,%i,%1.2f" % (int(output), int(ramp_enable), float(ramprate)))

    def get_setpoint_ramp_parameter(self, output):

        self.port.write("RAMP? %i" % int(output))
        answer = self.port.read()
        return float(answer.split(",")[1])

    def set_heater_pid(self, output, p, i, d):
        
        self.port.write("PID %i,%1.3f,%1.3f,%1.3f" % (int(output), float(p), float(i), float(d)))

    def get_heater_pid(self, output):

        self.port.write("PID? %i" % (int(output)))
        answer = self.port.read()
        return list(map(answer.split(",")))

    def set_autotune(self, output, mode):

        """

        Args:
            output: output channel
            mode:  0 = P only, 1 = P and I, 2 = P, I, and D.

        Returns:
            None
        """

        self.port.write("ATUNE %i,%i" % (int(output), int(mode)))

    def get_tuning_control_status(self):

        self.port.write("TUNEST?")
        answer = self.port.read()
        return answer.split(",")

    def get_zone(self, output, zone):

        self.port.write("ZONE? %i,%i" % (int(output), int(zone)))
        answer = self.port.read()
        return answer
