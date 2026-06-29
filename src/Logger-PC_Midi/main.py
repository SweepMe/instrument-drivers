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
# Type: Logger
# Device: Midi input


import os

from FolderManager import addFolderToPATH
addFolderToPATH()

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
# pygame (incl. its PortMidi binding pygame.midi) is loaded from the libs folder of this Device Class
import pygame.midi

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
                  Captures Event, Key, and Value.
                  Returns the last known event, key, and value at each measurement point.
                  """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "Midi input"

        self.variables = ["Event", "Key", "Value"]
        self.units = ["", "", ""]
        self.plottype = [True, True, True]  # True to plot data
        self.savetype = [True, True, True]  # True to save data

    def get_GUIparameter(self, parameter):
        self.port_string = parameter["Port"]

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
                if pygame.midi.get_device_info(i)[2]]  # input devices

    def connect(self):
        self._ensure_init()
        device_id = self._find_device_id(self.port_string, is_input=True)
        if device_id is None:
            raise Exception("Unable to find input port. Please use button 'Find Ports' and select one of the available ports.")
        self.inport = pygame.midi.Input(device_id)

    def initialize(self):
        self.answer = [float('nan'), float('nan'), float('nan')]

    def disconnect(self):
        self.inport.close()
        pygame.midi.quit()

    def call(self):
        # Drain all pending events and keep the most recent message (status, data1, data2).
        last_event = None
        while self.inport.poll():
            events = self.inport.read(1024)
            if events:
                last_event = events[-1]

        if last_event is not None:
            data = last_event[0]  # [status, data1, data2, data3]
            self.answer = [data[0], data[1], data[2]]

        return self.answer
