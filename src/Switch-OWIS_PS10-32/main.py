# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2018 Axel Fischer (sweep-me.net)
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
# Type: Switch
# Device: OWIS PS10-32

"""
Features:<br>
The offset value is substracted from the Sweep value.<br>
<br>
CAN-Bus:<br>
Master uses CAN-OUT.<br>
SLAVE uses CAN-IN to connect to master and CAN-OUT to next slave.<br>
Switch on the slaves first and the master at the end.<br>
Use an unconnected COM port adapter at CAN-IN of the master.<br>
"""

import time
from collections import OrderedDict

from ErrorMessage import error

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "OWIS PS10-32"
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {"EOL" : "\r",
                                "timeout": 3,
                                "baudrate": 9600,
                                "delay": 0.04, # PS10-32 needs about 40 ms to process commands
                                }
                                
                                
        self.variables = ["Position"]
        self.units = ["steps"]
        self.plottype = [True]
        self.savetype = [True]
       
       
        self.time_max_moving = 200 #sec

        
    def set_GUIparameter(self):
        
        GUIparameter =  {
                        "SweepMode" : ["Position"],
                        "Mode": ["Translation", "Rotation"],
                        "Motor type": ["1 - Step motor"], # "0 - DC Brush"
                        "Controller": ["Master"] + ["Slave%02d" % id for id in range(100)],
                        # "Calibration [mm/step] or [°/step]": 1.0,
                        "Home @ start" : True, 
                        "Limit, min": 0,
                        "Limit, max": 1950000,
                        "offset": 0,
                        }
        
        return GUIparameter
        
    def get_GUIparameter(self, parameter = {}):
        
        self.offset = int(parameter["offset"])
        self.homeposition = parameter["Home @ start"]
        self.motortype = parameter["Motor type"][0]
        self.sweepmode = parameter["SweepMode"]
        self.sweepvalue = parameter["SweepValue"]
        self.limitmin = int(float(parameter["Limit, min"]))
        self.limitmax = int(float(parameter["Limit, max"]))
        self.controller = parameter["Controller"]
                    

    def connect(self):
    
        self.slaveID = ""
    
        # give an answer with clear meessage
        self.port.write("TERM=1")
        
        # Command end is CR \r
        self.port.write("COMEND=0")
        
        
        # ask for SlaveID
        if self.controller == "Master":
            self.slaveID = self.query("SLAVEID")
        else:
            self.slaveID = self.controller[-2:]
                            
                     
    def initialize(self):
        
        # needed later in configure to go only once to home position
        self.home_found = False
        
        self.query("VERSION")
                
        # MOTYPE1=1 (step motor)
        self.write("MOTYPE1=%s" % self.motortype)
        
        # Reference position
        self.write("RMK1=0001")
        
        # defines the signal of the reference positions
        self.write("RPL1=1111")
              
        #All limit switches are used
        self.write("SMK1=1111")

        #Polarity SPL
        self.write("SPL1=1111")

        #        self.query(slaveID, "SMK1")
        #        self.query(slaveID, "SPL1")
        
        self.write("ABSOL1")

        #        self.query(slaveID, "MODE1")
        #        
        #        self.query(slaveID, "PVEL1")
        #        self.query(slaveID, "FVEL1")
        #        self.query(slaveID, "ACC1")
        #        self.query(slaveID, "MCSTP1")
        #        self.query(slaveID, "DRICUR1")
        #        self.query(slaveID, "HOLCUR1")
        #        self.query(slaveID, "ATOT1")
        #        self.query(slaveID, "FKP1")
        #        self.query(slaveID, "FKD1")
        #        self.query(slaveID, "FKI1")
        #        self.query(slaveID, "FIL1")
        #        self.query(slaveID, "FST1")
        #        self.query(slaveID, "FDT1")
        #        self.query(slaveID, "MXPOSERR1")
        #        self.query(slaveID, "MAXOUT1")
        #        self.query(slaveID, "AMPPWMF1")
        #        self.query(slaveID, "PHINTIM1")
        
        # one can save parameters to the EEPROM but it is not needed because all parameters are restored anyway
        # self.write("SAVEPARA")
        
        self.write("INIT1")
        
        # move back if move previously into a physical limit control
        self.write("EFREE1")

        #self.calibrate()
                
        self.write("MOFF1")
        

    def deinitialize(self): 
        self.write("MOFF1") 
        
    def configure(self):
    
        # position limit control is switched on for max position and min position
        self.write("LMK1=11")
        self.write("SLMIN1=" + str(self.limitmin))
        self.write("SLMAX1=" + str(self.limitmax))
    
        if self.homeposition and not self.home_found:
            self.write("MON1")
            self.write("REF1=2")
              
                
    def poweron(self):
    
        if self.homeposition and not self.home_found:
            self.reach()
            self.write("MOFF1")
            self.write("CNT1=0")
            self.home_found = True
        
            
    def apply(self):
    
        self.write("MON1")
        
        self.value =  int(float(self.value)) - self.offset
        
        if self.value < self.limitmin:
            self.value = self.limitmin
        
        if self.value > self.limitmax:
            self.value = self.limitmax
            
        self.write("PSET1=%i" % self.value)
        
        self.write("PGO1")
                
        
    def reach(self):
    
        """
        „I“ = Achse nicht initialisiert
        „O“ = Achse stromlos in Ruhe
        „R“ = Achse bestromt in Ruhe
        „T“ = Achse positioniert im Trapez-Profil
        „V“ = Achse arbeitet im Geschwindigkeitsmodus
        „P“ = Achse fährt auf Referenzposition
        „F“ = Achse fährt einen Endschalter frei
        „L“ = Achse stromlos nachdem sie auf Limitschalter
        (MINSTOP, MAXSTOP) gefahren ist
        „B“ = Achse wird gestoppt nachdem sie auf einen Bremsschalter
        (MINDEC, MAXDEC) gefahren ist
        „A“ = Achse stromlos nach Endstufen-Fehler
        „M“ = Achse stromlos nach Motion-Controller-Fehler
        „Z“ = Achse stromlos nach Timeout-Fehler
        „H“ = Phaseninitialisierung aktiv (Schrittmotor-Achse)
        „U“ = Achse nicht freigegeben
        „E“ = Achse stromlos nach Bewegungsfehler
        „?“ = Fehler, unbekannter Achsenstatus
        """
       
        time_ref =  time.perf_counter()
        
        
        while True:
        
            status = self.query("ASTAT1")
            
            if status == "O":
                break
            
            if status == "R":
                break
                
            elif status == "T":
                pass
                
            elif status == "P":
                pass
                                
            elif status == "L":
                break
                
            if time.perf_counter() - time_ref > self.time_max_moving:
                self.write("STOP1")
                break
                        
        self.write("MOFF1")    
            
    def measure(self):
        # get actual position
        self.write("?CNT1")
        
    def read_result(self):
        self.current_position = int(self.port.read())
            
    def call(self):
        return self.current_position
        
    """--------------- non-SweepMe! functions start here ------------------------------------------------------------"""    
        

    def query(self, query, slave = -1):
    
        if slave == -1:
            slave = self.slaveID

        
        if slave != "": 
            slave = str(slave).zfill(2)
        self.port.write(slave+"?"+query)
        answer = self.port.read()
        return(answer)
        
    def write(self, msg):
        slave = self.slaveID
        
        if slave != "": 
            slave = str(slave).zfill(2)
        self.port.write(slave+msg)
        
        try:
            if not msg.startswith("?"):
                answer = self.query("MSG")
                if not answer.startswith("00"):
                    print("Write:", msg, answer)
        except:
            error()
          
