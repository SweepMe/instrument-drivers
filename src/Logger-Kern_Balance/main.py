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
        self.port_types = ["COM", "SOCKET"]
        self.port_properties = {
            "baudrate": 9600,
            "EOL": "\r\n",  # terminator is CR/LF
            "parity": "N",
            "timeout": 0.1,  # short timeout for quick protocol check in 'connect' method
            "SOCKET_EOLwrite": "\r\n",
            "SOCKET_EOLread": "\r\n",
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
            # In SweepMe! <1.5.7.6, the port was automatically closed after the exception. Therefore, we open it again.
            # Although not necessary in the new SweepMe! version, it remains here for backwards compatibility.
            if not self.port.port_properties["open"]:
                self.port.open()

    def initialize(self) -> None:

        # The next two commands remain as comment for later use and optional testing.
        # In a next revision, they can be moved to own functions wrapping the communication commands

        # if self.protocol == "KCP":
            # self.port.write("@") # cancel all operations and reset to state after switching on
            # answer = self.port.read()
            # print("Response on @:", answer)
        
        # if self.protocol == "KCP":
            # query list of implemented commands, this might be useful to check whether the balance supports all
            # commands used in this driver.
            # However, command I0 returns multiple lines that need to be correctly processed.
            # self.port.write("I0")
            # answer = self.port.read()
            # print(f"Command: {answer}")
        
        if self.protocol == "KCP":
            self.port.write("I5")
            answer = self.port.read()  # queries the SW identification number
            # print(f"SW identification number: {answer}")

        if self.protocol == "KCP":
            self.port.write(f"U {self.mode_str}")
            answer = self.port.read()
            # print(f"Unit: {answer}")

    def configure(self) -> None:

        if self.do_initial_tare:
            self.tare()
            time.sleep(0.5)
            
        if self.do_initial_zero:
            self.zero()
        else:
            # if there is no zero we will just subtract 0.0 all the time during read_result for tws protocol
            self.weight_initial_g = 0.0
            self.weight_initial = 0.0

        if self.do_flow_calculation:
            self.weight_last_g = self.get_weight_g(stable=False)[0]
            if self.mode_str == "kg":
                self.weight_last = self.weight_last_g / 1000.0
            elif self.mode_str == "g":
                self.weight_last = self.weight_last_g 
                
            if self.protocol == "tws" and self.do_initial_zero:
                self.weight_last = self.weight_last - self.weight_initial
            self.time_last = time.perf_counter()

    def adapt(self) -> None:

        # we use adapt to stabilize the weight before measurement is requested
        # this way, the time between request and read is minimized and the time stamp of the Time module matches better
        # This solution is not perfect, as the weight might still change between adapt and measure, and additional
        # stabilization time be needed during read_result if the weight is not stable yet.
        if self.is_read_stabilized:
            self.get_weight_g(stable=True)

    def measure(self) -> None:

        self.request_weight()

    def read_result(self) -> None:

        weight_g, is_stable, is_overload = self.read_weight_g(stable=self.is_read_stabilized)

        # software zeroing for tws protocol
        if self.protocol == "tws":
            weight_g = weight_g - self.weight_initial

        # convert to selected weight unit
        weight = weight_g / 1000.0 if self.mode_str == "kg" else weight_g

        self.results = [weight, is_stable, is_overload]

        # Flow calculation in the selected weight and time unit
        if self.do_flow_calculation:
            now = time.perf_counter()

            flow = (weight - self.weight_last) / (now - self.time_last) if now - self.time_last > 0.0 else float("nan")
            
            if self.time_unit == "s":
                pass
            elif self.time_unit == "min":
                flow = flow*60
            elif self.time_unit == "h":
                flow = flow*3600
            
            self.weight_last = weight
            self.time_last = now
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
            self.port.read()
        elif self.protocol == "tws":
            # the old protocol has no zero, so we just reset the initial weight
            self.weight_initial_g = self.get_weight_g(stable=True)
            if self.mode_str == "kg":
                self.weight_initial = self.weight_initial_g / 1000.0
            elif self.mode_str == "g":
                self.weight_initial = self.weight_initial_g

    def get_weight_immediately_g(self):

        self.request_weight()
        weight, is_stable, is_overload = self.read_weight_g(stable=False)
        return weight, is_stable, is_overload

    def get_weight_g(self,stable=False):

        self.request_weight()
        weight, is_stable, is_overload = self.read_weight_g(stable)
        return weight, is_stable, is_overload

    def request_weight(self):

        # we do not use the stable commands here, as we iterate in read_weight_g until stable
        if self.protocol == "KCP":
            self.port.write("SI")

        elif self.protocol == "tws":
            self.port.write("w")

    def read_weight_g(self, stable=False):

        answer = self.port.read()

        if self.protocol == "KCP":

            is_overload = None  # not supported right now for KCP
            vals = answer.split()
            is_stable = (vals[1] == "S")

            if vals[0] != "S":
                msg = f"Queried weight has wrong prefix: '{vals[0]}'."
                raise Exception(msg)

            if vals[1] not in ["S", "D"]:
                msg = f"Queried weight has wrong status: '{vals[1]}'."
                raise Exception(msg)

            if stable:
                while not is_stable and not self.is_run_stopped():
                    self.port.write("SI")
                    answer = self.port.read()
                    vals = answer.split()
                    is_stable = (vals[1] == "S")

            weight = float(vals[2])
            unit = vals[3]

            if unit == "kg":
                weight = weight * 1000.0

            return weight, is_stable, is_overload

        elif self.protocol == "tws":
            # to keep timeouts below 1s, we read weight immediately and wait until result is stable

            answer = self.port.read()
            is_stable = "g" in answer
            is_overload = "=Overload=" in answer

            if stable:
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
                except:
                    msg = f"Unable to interprete weight: '{repr(answer)}'"
                    raise ValueError(msg)

                if "kg" in answer:
                    weight = weight * 1000.0

            return weight, is_stable, is_overload

        raise ValueError("Unknown protocol.")
