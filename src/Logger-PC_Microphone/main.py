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

import os
import wave

import numpy as np

import FolderManager
FolderManager.addFolderToPATH()
# sounddevice (PortAudio) is loaded from the libs_common folder of this Device Class
import sounddevice as sd

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        super().__init__()

        self.shortname = "Microphone"

        self.variables = ["Volume"]
        self.units = [""]
        self.plottype = [True]  # define if it can be plotted
        self.savetype = [False]  # define if it can be saved

        self.CHUNK = 1024
        self.CHANNELS = 2
        self.RATE = 44100
        self.RECORD_SECONDS = 0.03

    def set_GUIparameter(self):

        GUIparameter = {
                        "Channels": 2,
                        "Duration": 0.5,
                        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):

        self.port = parameter["Port"]

        if "Duration" in parameter:
            self.RECORD_SECONDS = float(parameter["Duration"])

        self.CHANNELS = int(parameter.get("Channels", 2))

    def find_Ports(self):
        mics = []
        for index, device in enumerate(sd.query_devices()):
            if device["max_input_channels"] > 0:
                mics.append("%i - %s" % (index, device["name"]))

        return mics

    def initialize(self):

        self.count = 0

        index_pos = self.port.find(" - ")
        self.dev_index = int(self.port[:index_pos])

        self.wave_output_filename = self.get_folder("TEMP") + os.sep + "mic%i_%s.wav"

    def start(self):
        self.count += 1
        self.stream = sd.InputStream(
            samplerate=self.RATE,
            channels=self.CHANNELS,
            dtype="int16",
            blocksize=self.CHUNK,
            device=self.dev_index,
        )
        self.stream.start()

    def measure(self):
        # frames are (CHUNK, CHANNELS) int16 numpy arrays
        self.frames = []

        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data, _overflowed = self.stream.read(self.CHUNK)
            self.frames.append(data)

        # RMS of the last snippet -> volume (replaces the removed stdlib 'audioop.rms')
        last = self.frames[-1].astype(np.float64)
        self.rms = float(np.sqrt(np.mean(last ** 2)))

    def call(self):
        self.stream.stop()
        self.stream.close()

        return [self.rms]

    def finish(self):
        wf = wave.open(self.wave_output_filename % (self.dev_index, self.count), 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(2)  # int16 -> 2 bytes per sample
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frame.tobytes() for frame in self.frames))
        wf.close()

    def connect(self):
        pass

    def poweron(self):
        pass

    def apply(self):
        pass

    def deinitialize(self):
        pass

    def poweroff(self):
        pass

    def disconnect(self):
        pass
