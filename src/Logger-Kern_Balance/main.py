# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021, 2025 SweepMe! GmbH (sweep-me.net)
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


# SweepMe! instrument driver
# * Module: Logger
# * Instrument: Kern Balance


from pysweepme.ErrorMessage import error, debug
from pysweepme.EmptyDeviceClass import EmptyDevice

import time


class Device(EmptyDevice):

    actions = ["tare", "zero"]

    def __init__(self):
        EmptyDevice.__init__(self)

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
                                "baudrate": 9600,
                                "EOL": "\r\n",  # terminator is CR/LF
                                "parity": "N",
                                "timeout": 0.1,
                                }
                                
        self.shortname = "Kern Balance"
            
    def update_gui_parameters(self, parameters):
    
        gui_parameter = {
                        "Weight unit": ["g", "kg"],
                        "": None,  # empty line
                        "Read stabilized": False,
                        "Initial tare": False,
                        "Initial zero": False,
                        " ": None,  # empty line
                        "Flow calculation": False,
                        }
                        
        if "Flow calculation" in parameters and parameters["Flow calculation"]:
            gui_parameter["Time unit"] = ["s", "min", "h"]

        return gui_parameter

    def apply_gui_parameters(self, parameter):

        self.is_read_stabilized = parameter["Read stabilized"]
        self.do_initial_zero = parameter["Initial zero"]
        self.do_initial_tare = parameter["Initial tare"]
        self.mode_str = parameter["Weight unit"]
        self.unit_str = parameter["Weight unit"].split(" ")[-1]
        self.variable_str = parameter["Weight unit"].split(" ")[0]
        
        self.variables = ["Weight", "Stable", "Overload"]  # define as many variables you need
        self.units = [self.unit_str, "", ""]
        self.plottype = [True, True, True]  # True to plot data, corresponding to self.variables
        self.savetype = [True, True, True]  # True to save data, corresponding to self.variables
        
        self.do_flow_calculation = parameter["Flow calculation"]
        self.time_unit = parameter.get("Time unit", "")
        
        if self.do_flow_calculation:
            self.variables.append("Flow")
            self.units.append(self.unit_str + "/" + self.time_unit)
            self.plottype.append(True)
            self.savetype.append(True)

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self) -> None:

        # figure out which protocol is used
        try:
            self.port.write("I5")  # queries the SW identification number
            answer = self.port.read()
            # TODO: check whether answer is valid for KCP
            self.protocol = "KCP"  # Kern Communication Protocol
        except:  # TODO: catch specific exception
            self.protocol = "tws"  # t, w, and s are the only three commands that the older protocol supports
            # if it fails to use the first command, we will proceed with tws command set
            if not self.port.port_properties["open"]:
                self.port.open()

    def initialize(self) -> None:
    
        # if self.protocol == "KCP":
            # self.port.write("@") # cancel all operations and reset to state after switching on
            # answer = self.port.read()
            # print("Response on @:", answer)
        
        # if self.protocol == "KCP":
            # not used because I0 returns multiple lines
            # self.port.write("I0")
            # answer = self.port.read() # query list of implemented commands, this might be useful later to check whether the balance can be used with this driver.
            # print("SW identification number:", answer)
        
        if self.protocol == "KCP":
            self.port.write("I5")
            answer = self.port.read()  # queries the SW identification number
            # print("SW identification number:", answer)

        if self.protocol == "KCP":
            self.port.write(f"U {self.unit_str}")
            answer = self.port.read()
            # print("Unit:    ", answer)

    def configure(self) -> None:

        if self.do_initial_tare:
            self.tare()
            time.sleep(0.5)
            
        if self.do_initial_zero:
            if self.protocol == "KCP":
                self.port.write("Z")
                self.port.read()
            elif self.protocol == "tws":
            
                if self.is_read_stabilized:
                    self.weight_initial_g = self.get_weight_stable_g()
                else:
                    self.weight_initial_g = self.get_weight_immediately_g()
                    
                if self.mode_str == "kg":
                    self.weight_initial = self.weight_initial_g / 1000.0
                elif self.mode_str == "g":
                    self.weight_initial = self.weight_initial_g

        if self.do_flow_calculation:
            self.weight_last_g = self.get_weight_immediately_g()
            if self.mode_str == "kg":
                self.weight_last = self.weight_last_g / 1000.0
            elif self.mode_str == "g":
                self.weight_last = self.weight_last_g 
                
            if self.protocol == "tws" and self.do_initial_zero:
                self.weight_last = self.weight_last - self.weight_initial
            self.time_last = time.perf_counter()

    def measure(self) -> None:

        if self.protocol == "KCP":
            self.port.write("SI")
                
        if self.protocol == "tws":
            self.port.write("w")

    def read_result(self) -> None:

        # default value
        weight = float('nan')

        answer = self.port.read()

        if self.protocol == "KCP":
        
            is_overload = False  # not supported right now for KCP
        
            vals = answer.split()
            is_stable = (vals[1] == "S")
        
            if self.is_read_stabilized:
                while not is_stable and not self.is_run_stopped():
                    self.port.write("SI")
                    answer = self.port.read()
                    vals = answer.split()
                    is_stable = (vals[1] == "S")

            if vals[0] != "S":
                msg = "Queried weight has wrong prefix."
                raise Exception(msg)

            if vals[1] not in ["S", "D"]:
                msg = "Queried weight has wrong status."
                raise Exception(msg)

            weight = float(vals[2])
            unit = vals[3]

            if unit != self.unit_str:
                msg = "Queried weight has wrong unit."
                raise Exception(msg)

        elif self.protocol == "tws":
            
            is_stable = "g" in answer

            if self.is_read_stabilized:
                while not is_stable and not self.is_run_stopped():
                    self.port.write("w")
                    answer = self.port.read()
                    is_stable = "g" in answer

            is_overload = "=Overload=" in answer

            if is_overload:
                weight = float('nan')
            else:
                try:
                    answer = answer[2:].replace(" ", "").replace("g", "")
                    weight = float(answer)
                    
                    if "kg" in answer:
                        if self.mode_str == "kg":
                            pass
                        elif self.mode_str == "g":
                            weight = weight * 1000.0
                    else:
                        if self.mode_str == "kg":
                            weight = weight / 1000.0
                        elif self.mode_str == "g":
                            pass
                except:
                    raise ValueError(f"Unable to interprete weight: '{repr(answer)}'")
                    
                if self.do_initial_zero:
                    weight = weight - self.weight_initial
                    
        if self.do_flow_calculation:
            now = time.perf_counter()

            if (now - self.time_last) > 0.0:
                flow = (weight - self.weight_last) / (now - self.time_last)
            else:
                flow = float('nan')
            
            if self.time_unit == "s":
                pass
            elif self.time_unit == "min":
                flow = flow*60
            elif self.time_unit == "h":
                flow = flow*3600
            
            self.weight_last = weight
            self.time_last = time.perf_counter()
        
        self.results = [weight, is_stable, is_overload]
        
        if self.do_flow_calculation:
            self.results.append(flow)

    def call(self) -> None:
        return self.results

    def tare(self) -> None:
        """Tares the balance (with load)."""
        if self.protocol == "KCP":
            self.port.write("T")
            self.port.read()

        elif self.protocol == "tws":
            self.port.write("t")

    def zero(self) -> None:
        """Sets the balance to zero (without load)."""
        if self.protocol == "KCP":
            self.port.write("Z")
        elif self.protocol == "tws":
            raise NotImplementedError("Zeroing not supported in tws protocol.")

    def get_weight_immediately_g(self):

        if self.protocol == "KCP":
            self.port.write("SI")
            answer = self.port.read()
            vals = answer.split()
            is_stable = (vals[1] == "S")

            if vals[0] != "S":
                msg = "Queried weight has wrong prefix."
                raise Exception(msg)

            if vals[1] not in ["S", "D"]:
                msg = "Queried weight has wrong status."
                raise Exception(msg)

            weight = float(vals[2])
            unit = vals[3]

            return weight

        elif self.protocol == "tws":
            self.port.write("w")
            answer = self.port.read()
            answer = answer[2:].replace(" ", "").replace("g", "")
            weight = float(answer)
        
            return weight

    def get_weight_stable_g(self):

        if self.protocol == "KCP":
            self.port.write("S")
            answer = self.port.read()

            vals = answer.split()
            is_stable = (vals[1] == "S")

            if vals[0] != "S":
                msg = "Queried weight has wrong prefix."
                raise Exception(msg)

            if vals[1] not in ["S", "D"]:
                msg = "Queried weight has wrong status."
                raise Exception(msg)

            weight = float(vals[2])
            unit = vals[3]

            return weight
            
        elif self.protocol == "tws":
            # to keep timeouts below 1s, we read weight immediately and wait until result is stable
        
            self.port.write("w")
            answer = self.port.read()        
            is_stable = "g" in answer

            while not is_stable and not self.is_run_stopped():
                self.port.write("w")
                answer = self.port.read()
                is_stable = "g" in answer
            
            answer = answer[2:].replace(" ", "").replace("g", "")
            weight = float(answer)
            return weight
