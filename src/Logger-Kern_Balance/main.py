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


class Device(EmptyDevice):

    description =   """
                    <p>
                      The driver supports all balances, scales, and terminals from
                      Kern&amp;Sohn that use the KERN communicaton protocol (KCP).
                    </p>
                    <p>
                      <br />
                      <strong>Models:</strong> KIB-TM, KFB-TM, KFN
                    </p>
                    <p>
                      &nbsp;
                    </p>
                    <p>
                      <strong>Communication:</strong>
                    </p>
                    <ul>
                      <li>Use baudrate 9600, 8 databits, 1 stopbit
                      </li>
                      <li>Go to instrument menu "P9 Prt“ -&gt; „oPt“ -&gt; ModE" and
                      select "KCP"
                      </li>
                    </ul>
                    <p>
                      &nbsp;
                    </p>
                    <p>
                      <strong>Usage:</strong>
                    </p>
                    <ul>
                      <li>Select the mode to select also the unit.
                      </li>
                      <li>The option "Read stabilized" must be checked if the returned
                      value is always a stabilized value. Otherwise the current value
                      will be returned.
                      </li>
                      <li>The option "Initial tare" triggers the tare function at the
                      beginning of a run, e.g. to substract a start weight.
                      </li>
                      <li>The option "Initial zero" triggers the zero function at the
                      beginning of a run in order to create a new zero reference level.
                      </li>
                    </ul>
                    """

    actions = ["tare", "zero"]

    def __init__(self):
        EmptyDevice.__init__(self)

        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
                                "baudrate": 9600,
                                "EOL": "\r\n",  # terminator is CR/LF
                                "parity": "N",
                                "timeout": 10,
                                }
            
    def set_GUIparameter(self):
    
        gui_parameter = {
                        "Mode": ["Weight in kg", "Weight in g"],
                        "": None,  # empty line
                        "Read stabilized": False,
                        "Initial zero": False,
                        "Initial tare": False,
                        # " ": None,  # empty line
                        # "Flow calculation": False,
                        # "Time unit": ["s", "min", "h"],
                        }

        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.is_read_stabilized = parameter["Read stabilized"]
        self.do_initial_zero = parameter["Initial zero"]
        self.do_initial_tare = parameter["Initial tare"]
        self.unit_str = parameter["Mode"].split(" ")[-1]
        self.variable_str = parameter["Mode"].split(" ")[0]

        self.shortname = "Balance"
        self.variables = [self.variable_str, "stable"]  # define as many variables you need
        self.units = [self.unit_str, ""]
        self.plottype = [True, True]  # True to plot data, corresponding to self.variables
        self.savetype = [True, True]  # True to save data, corresponding to self.variables

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def connect(self):
        # figure out which protocol is used
        try:
            self.port.write("I5")  # queries the SW identification number
            answer = self.port.read()
            self.protocol = "KCP"  # Kern Communication Protocol
        except:
            self.protocol = "tws"  # t, w, and s are the only three commands that the older protocol supports

    def initialize(self):
    
        #self.port.write("@") # cancel all operations and reset to state after switching on
        #answer = self.port.read()
        #print("Response on @:", answer)
        
        # not used because I0 returns multiple lines
        # self.port.write("I0")
        # answer = self.port.read() # query list of implemented commands, this might be useful later to check whether the balance can be used with this driver.
        # print("SW identification number:", answer)
        
        self.port.write("I5")
        answer = self.port.read()  # queries the SW identification number
        # print("SW identification number:", answer)

        if self.protocol == "KCP":
            self.port.write("U %s" % self.unit_str)
            answer = self.port.read()
            # print("Unit:    ", answer)

    def configure(self):

        if self.do_initial_zero:
            if self.protocol == "KCP":
                self.port.write("Z")
                answer = self.port.read()

        if self.do_initial_tare:
            self.tare()

        # if self.do_flow_calculation:
            # self.reference_weight = self.get_weight_immediately()
            # self.reference_time = time.perf_counter()

    def measure(self):

        if self.protocol == "KCP":
            if self.is_read_stabilized:
                self.port.write("S")  # send stable value
            else:
                self.port.write("SI")  # = Send Immediately (can be also unstable value)

    def read_result(self):

        # default value
        weight = float('nan')

        answer = self.port.read()

        if self.protocol == "KCP":

            vals = answer.split()

            if vals[0] != "S":
                msg = "Queried weight has wrong prefix."
                raise Exception(msg)

            if vals[1] not in ["S", "D"]:
                msg = "Queried weight has wrong status."
                raise Exception(msg)

            self.is_stable = (vals[1] == "S")

            weight = float(vals[2])
            unit = vals[3]

            if unit != self.unit_str:
                msg = "Queried weight has wrong unit."
                raise Exception(msg)

        elif self.protocol == "tws":

            # Unclear whether balance returns whether value is stabilized so we use the information from

            self.is_stable = self.is_read_stabilized

            try:
                weight = float(answer.split("g")[0].replace(" ", ""))

                if "kg" in answer:
                    if self.mode_str == "Weight in kg":
                        pass
                    elif self.mode_str == "Weight in g":
                        weight = weight * 1000.0

                else:
                    if self.mode_str == "Weight in kg":
                        weight = weight / 1000.0
                    elif self.mode_str == "Weight in g":
                        pass
            except:
                raise Exception("Unable to query weight.")

        self.weight = weight

    def call(self):

        return [self.weight, self.is_stable]

    def tare(self):
        if self.protocol == "KCP":
            self.port.write("T")
            answer = self.port.read()

        elif self.protocol == "tws":
            self.port.write("t")
            answer = self.port.read()

    def zero(self):
        self.port.write("Z")
        answer = self.port.read()

    def get_weight_immediately(self):

        if self.protocol == "KCP":
            self.port.write("SI")
            answer = self.port.read()

        elif self.protocol == "tws":
            self.port.write("w")
            answer = self.port.read()

    def get_weight_stable(self):

        if self.protocol == "KCP":
            self.port.write("S")
            answer = self.port.read()
        elif self.protocol == "tws":
            self.port.write("s")
            answer = self.port.read()

    def read_weight(self):

        answer = self.port.read()