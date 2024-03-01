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
# Type: Logger
# Device: Microphone


"""
This Device Class is an example how to interact with a microphone.
Duration is the time per waveform snippet that is used to calculate the rms value.
"""

import os, sys
import time

import FolderManager
FolderManager.addFolderToPATH()
# needed to load pyaudio libraray from libs folder of this DC
import pyaudio
import wave
import audioop

from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):

    def __init__(self):
    
        super().__init__()

        self.shortname = "Microphone"
        
        self.variables = ["Volume"]
        self.units = [""]
        self.plottype = [True] # define if it can be plotted
        self.savetype = [False] # define if it can be plotted

        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.RECORD_SECONDS = 0.03
        self.WAVE_OUTPUT_FILENAME = self.tempfolder + os.sep + "mic%i_%s.wav"
        
    def set_GUIparameter(self):
    
        GUIparameter = {
                        "Channels": 2,
                        "Duration": 0.5,
                        }
                        
        return GUIparameter
                        

    def get_GUIparameter(self, parameter = {}):
       
        self.port = parameter["Port"]
        
        if "Duration" in parameter:
            self.RECORD_SECONDS = float(parameter["Duration"])

        self.CHANNELS = int(parameter.get("Channels", 2))
         
    def find_Ports(self):
        mics = []
        self.p = pyaudio.PyAudio()
        info = self.p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
            if (self.p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                mics.append("%i - "%i + self.p.get_device_info_by_host_api_device_index(0, i).get('name'))
                    
        return mics
       
    def initialize(self):
    
        self.count = 0
    
        self.p = pyaudio.PyAudio()
        index_pos = self.port.find(" - ")
        self.dev_index =  int(self.port[:index_pos])
               
    def poweron(self):
        pass

    def connect(self):
        pass          
        
    def start(self):
        self.count += 1
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
            input_device_index = self.dev_index
            )
     
    def apply(self):
        pass
             
    def measure(self):
        self.frames = []

        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = self.stream.read(self.CHUNK)
            self.frames.append(data)
        
        self.rms = audioop.rms(self.frames[-1], 2)    # calculation of the volume
            
    def call(self):
        self.stream.stop_stream()
        self.stream.close()
        
        return [self.rms]    
        
    def finish(self):
        wf = wave.open(self.WAVE_OUTPUT_FILENAME %(self.dev_index, self.count), 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        
    def deinitialize(self):
        self.p.terminate()
       
    def poweroff(self):
        pass

    def disconnect(self):
        pass
