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
# Type: Switch
# Device: Midi output

import os

import numpy as np

from FolderManager import addFolderToPATH
addFolderToPATH()

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
# pygame (incl. its PortMidi binding pygame.midi) is loaded from the libs folder of this Device Class
import pygame.midi

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
                  <p>Note must be an integer between 0 and 127</p>

                  <p>You might not hear a sound when testing using the Apply-Button, as the Test mode disconnects
                  from the device immediately after applying the value.</p>
                  """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "Midi output"

        self.variables = ["Note"]
        self.units = [""]
        self.plottype = [True]
        self.savetype = [True]

    def set_GUIparameter(self):

        GUIparameter = {
                        "SweepMode": ["Note"],
                        "Channel": 0,
                        "Velocity": "32",
                        "Time in s": "1.0",
                        }

        return GUIparameter

    def get_GUIparameter(self, parameter):
        self.port_string = parameter["Port"]

        self.channel = int(parameter["Channel"])
        self.velocity = int(float(parameter["Velocity"]))
        self.playtime = float(parameter["Time in s"])

    @staticmethod
    def _ensure_init():
        if not pygame.midi.get_init():
            pygame.midi.init()

    @staticmethod
    def _device_name(index):
        name = pygame.midi.get_device_info(index)[1]
        if isinstance(name, bytes):
            name = name.decode(errors="replace")
        return name

    def _find_device_id(self, name, is_input):
        for i in range(pygame.midi.get_count()):
            info = pygame.midi.get_device_info(i)
            is_in, is_out = info[2], info[3]
            if self._device_name(i) == name and ((is_input and is_in) or (not is_input and is_out)):
                return i
        return None

    def find_Ports(self):
        self._ensure_init()
        return [self._device_name(i) for i in range(pygame.midi.get_count())
                if pygame.midi.get_device_info(i)[3]]  # output devices

    def connect(self):
        self._ensure_init()
        device_id = self._find_device_id(self.port_string, is_input=False)
        if device_id is None:
            raise Exception("Unable to find output port. Please use button 'Find Ports' and select one of the available ports.")
        self.midiout = pygame.midi.Output(device_id)

    def disconnect(self):
        self.midiout.close()
        pygame.midi.quit()

    def initialize(self):
        self.last_note = float('nan')

    def deinitialize(self):
        # all notes off + reset all controllers on every channel (replaces mido's panic())
        for channel in range(16):
            self.midiout.write_short(0xB0 + channel, 123, 0)  # all notes off
            self.midiout.write_short(0xB0 + channel, 121, 0)  # reset all controllers

    def apply(self):

        note = int(np.clip(float(self.value), 0, 127))

        self.midiout.note_on(note, self.velocity, self.channel)

        self.last_note = note

    def call(self):

        return self.last_note
