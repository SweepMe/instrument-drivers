# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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


# SweepMe! driver
# * Module: SMU
# * Instrument: aSpectSystems idSMU modules

import time
from pysweepme.EmptyDeviceClass import EmptyDevice

from pysweepme import FolderManager as FoMa
FoMa.addFolderToPATH()

from aspectdeviceengine.enginecore import IdSmuService, IdSmuServiceRunner, IdSmuBoardModel


class Device(EmptyDevice):

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "idSMUx"
        
        self.variables = ["Voltage", "Current"]
        self.units = ["V", "A"]
        self.plottype = [True, True]
        self.savetype = [True, True]

    def find_ports(self):

        srunner = IdSmuServiceRunner()
        print(srunner)
        service = srunner.get_idsmu_service()
        print(service)
        board = service.get_first_board()
        print(board)

        srunner.shutdown()

        ports = []

        return ports

    def set_GUIparameter(self):
        
        gui_parameter = {
            "SweepMode": ["Voltage in V", "Current in A"],
            "RouteOut": ["Front"],
            "Compliance": 0.1,
        }
                        
        return gui_parameter
                                 
    def get_GUIparameter(self, parameter={}):
        self.source = parameter['SweepMode']
        self.protection = parameter['Compliance']

    def connect(self):
        self.srunner = IdSmuServiceRunner()
        print(self.srunner)
        self.service = self.srunner.get_idsmu_service()
        print(self.service)

    def disconnect(self):
        self.srunner.shutdown()

    def initialize(self):
        pass

    def configure(self):
        pass
           
    def deinitialize(self):
        pass

    def poweron(self):
        pass
        
    def poweroff(self):
        pass
                 
    def apply(self):
        pass
         
    def measure(self):
        self.i = 0
        self.v = 1

    def call(self):
        return [self.v, self.i]