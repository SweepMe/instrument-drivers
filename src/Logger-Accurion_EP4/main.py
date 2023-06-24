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

# The file "ipconnection.py" in the libs folder was provided by Accurion GmbH and is not part of above license.

# SweepMe! device class
# Type: Logger
# Device: Accurion ep4

from FolderManager import addFolderToPATH
addFolderToPATH()

import ipconnection

import time
import os

from ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!
# If you like to see the source code of EmptyDevice, take a look at the pysweepme package that contains this file

class Device(EmptyDevice):

    description =   """
                    <h3>Accurion ep4</h3>
                    <p>This is a driver that basically triggers the start of a new measurement and waits until the measurement is finished. The driver returns the file path of the saved file so that further scripts can be used to process the data. The parameter "File suffix" is used to add a user-defined string to each file name. By using the parameter syntax {...} one can change the suffix for each variation of the sequencer.</p>
                    <p><strong>Port</strong></p>
                    <p>Standard connection is to 127.0.0.1:55200 which is the localhost, i.e. SweepMe! must run on the same computer on which the control software of the ep4 runs.</p>
                    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = "ep4" # short name will be shown in the sequencer
        self.variables = ["File path"] # define as many variables you need
        self.units = [""] # make sure that you have as many units as you have variables
        self.plottype = [True]   # True to plot data, corresponding to self.variables
        self.savetype = [True]   # True to save data, corresponding to self.variables
        
            
    def set_GUIparameter(self):

        GUIparameter = {
                        "Port": "127.0.0.1:55200",
                        "File suffix": "_myparameter",
                        }
                        
        return GUIparameter

    def get_GUIparameter(self, parameter):

        self.file_suffix = parameter["File suffix"]
        
        self.port_string = parameter["Port"]
        self.ip_address = self.port_string.split(":")[0].strip()

        if ":" in self.port_string:
            self.ip_port = int(self.port_string.split(":")[1].strip())
            if self.ip_port == "":
                self.ip_port = "127.0.0.1" # localhost
        else:
            self.ip_port = 55200

    def connect(self):

        self.result_ds_instance = None
        self.ep4 = ipconnection.IPConnection(self.ip_address, self.ip_port)
            
    def disconnect(self):

        # if self.result_ds_instance is not None:
            # self.ep4._call_object('__SUPER__', '__destroy_object__', result_ds_instance)
            
        self.ep4.close()

    def reconfigure(self, parameters, keys):
        """ 'reconfigure' is called whenever parameters of the GUI change by using the {...}-parameter system """
        
        if "File suffix" in keys:
            self.file_suffix = parameters["File suffix"]
        
        # print()
        # print("reconfigure")
        # print("Parameters:", parameters)
        # print("Changed keys:", keys)
        

    def measure(self):
        
        self.ep4.__set_sample_dialog_prompt__()
        self.ep4.__measurement_start__()
        
        interval = 1.0
        # now we have to wait until the measurement finishes
        while True: 
            if not self.ep4.__measurement_query_state__():
                print('Measurement finished... continue now')
                break
            print('Waiting until measurement is finished...')
            time.sleep(interval)
            
        self.result_ds_file = self.ep4.__measurement_save_result__(False)
        
        # here we rename all files by adding the suffix 
        filename = self.result_ds_file.rstrip(".ds.dat")
        self.result_ds_file_renamed = filename + self.file_suffix + ".ds.dat"
        
        
        for ext in [".ds.dat", ".dsinfo.xml", ".ds.png"]:
            os.rename(filename + ext, filename + self.file_suffix + ext)

        
        # print(self.result_ds_file)
		

    def call(self):
   
        return self.result_ds_file_renamed
