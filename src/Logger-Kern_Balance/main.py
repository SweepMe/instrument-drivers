# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2021 SweepMe! GmbH
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
# Type: Logger
# Device: Kern Balance


from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!
# If you like to see the source code of EmptyDevice, take a look at the pysweepme package that contains this file

class Device(EmptyDevice):

    ## here you can add html formatted description to your device class that is shown by modules like 'Logger' or 'Switch' that have a description field.
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
        
        
        ### use/uncomment the next line to use the port manager
        self.port_manager = True 
           
        ### use/uncomment the next line to let SweepMe! search for ports of these types. Also works if self.port_manager is False or commented.
        self.port_types = ["COM"]
        
        self.port_properties = {
                                "baudrate": 9600,
                                "EOL": "\r\n", # terminator is CR/LF
                                "parity": "N",
                                "timeout": 10,
                                }
            
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "Mode": ["Weight in kg", "Weight in g"],
                        "": None, # empty line
                        "Read stabilized": False,
                        "Initial zero": False,
                        "Initial tare": False,
                        }

        
        return GUIparameter

    def get_GUIparameter(self, parameter):

        self.is_read_stabilied = parameter["Read stabilized"]
        self.do_initial_zero = parameter["Initial zero"]
        self.do_initial_tare = parameter["Initial tare"]
        self.unit_str = parameter["Mode"].split(" ")[-1]
        self.variable_str = parameter["Mode"].split(" ")[0]


        self.shortname = "Balance" # short name will be shown in the sequencer
        self.variables = [self.variable_str, "stable"] # define as many variables you need
        self.units = [self.unit_str, ""]
        self.plottype = [True, True]   # True to plot data, corresponding to self.variables
        self.savetype = [True, True]   # True to save data, corresponding to self.variables
        
        

    """ here, semantic standard functions start that are called by SweepMe! during a measurement """

    def initialize(self):
    
        #self.port.write("@") # cancel all operations and reset to state after switching on
        #answer = self.port.read()
        #print("Response on @:", answer)
        
        ## not used because I0 returns multiple lines
        # self.port.write("I0")
        # answer = self.port.read() # query list of implemented commands, this might be useful later to check whether the balance can be used with this driver.
        # print("SW identification number:", answer)
        
        self.port.write("I5")
        answer = self.port.read() # queries the SW identification number
        # print("SW identification number:", answer)
        
        if self.do_initial_zero:
            self.port.write("Z")
            answer = self.port.read()
            
        if self.do_initial_tare:
            self.port.write("T")
            answer = self.port.read()    
            
        self.port.write("U %s" % self.unit_str)
        answer = self.port.read()
        # print("Unit:    ", answer)
               
     
    def measure(self):
        
        if self.is_read_stabilied:
            self.port.write("S") # send stable value
        else:
            self.port.write("SI") # = Send Immediately (can be also unstable value)
        
    def read_result(self):
        
        weight = float('nan') # default value that will be overwritten, whenever the balance responds with a correct value
        
        answer = self.port.read()
        # print("My answer=", answer)
        
        vals = answer.split() # split must have no argument as this automatically removed multiple spaces
        # print("vals: ", vals)
        
        if vals[0] != "S":
            self.stop_measurement("Response to weight query incorrect.")
            return False
        else:
            if not vals[1] in ["S", "D"]: 
                self.stop_measurement("Unable to query weight.")
                return False
                
            else:
                self.is_stable = (vals[1] == "S")

                weight = float(vals[2])
                unit = vals[3]

                if unit != self.unit_str:
                    self.stop_measurement("Queried weight has wrong unit.")
                    return False
                
        self.weight = weight # todo: do some processing here to get a float value in kg
        

    def call(self):

        return [self.weight, self.is_stable]
        
        
    def tare(self):
        self.port.write("T")
        answer = self.port.read()  
        
    def zero(self):
        self.port.write("Z")
        answer = self.port.read()

             