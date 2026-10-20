# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
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
# Device: Winsound

"""
smallest tone: 37 Hz<br>
highest tone: 32767 Hz<br>
Adjust length of tone with duration.<br>
"""

import winsound  # part of the Python standard library on Windows

from EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):
    
        EmptyDevice.__init__(self)

        self.shortname = "Winsound"
        
        self.variables = ["Note"]
        self.units = ["Hz"]
        
        # self.c_scale = [264, 297, 330, 352, 396, 440, 495, 528, 594, 660, 704, 792, 880, 990, 1056, 1192] 

    def set_GUIparameter(self):
        
        GUIparameter = {
                        "SweepMode" : ["Note in Hz"],
                        "Duration in s": 0.25,
                        }               
        return GUIparameter
        
    def get_GUIparameter(self, parameter):
        
        self.duration = int(float(parameter["Duration in s"])*1000)
        
    def configure(self): 
        self.note = float('nan')
        self.c_note = float('nan')
        
    def apply(self):
    
        self.note = int(self.value)

        if self.note < 37:
            self.note = 37
         
        if self.note > 32767:
            self.note = 32767

        # self.c_note = min(self.c_scale, key=lambda x:abs(x-self.note))
        self.play_note(self.note, self.duration)
        
    def call(self):
        return self.note
        
    # --- communication commands ---------------------------------------------

    def play_note(self, note: int, duration: int) -> None:
        """Play a tone of `note` Hz (37 to 32767) for `duration` milliseconds.

        Blocks until the tone has ended.
        """
        note = int(float(note))
        duration = int(float(duration))
        if not 37 <= note <= 32767:
            msg = f"note must be between 37 and 32767 Hz, got {note}."
            raise ValueError(msg)
        if duration < 0:
            msg = f"duration must not be negative, got {duration} ms."
            raise ValueError(msg)
        winsound.Beep(note, duration)

    def message_beep(self, sound: str = "OK") -> None:
        """Play a Windows system sound: OK, Asterisk, Exclamation, Hand or Question.

        Returns at once; the sound plays in the background.
        """
        kinds = {
            "ok": winsound.MB_OK,
            "asterisk": winsound.MB_ICONASTERISK,
            "exclamation": winsound.MB_ICONEXCLAMATION,
            "hand": winsound.MB_ICONHAND,
            "question": winsound.MB_ICONQUESTION,
        }
        key = str(sound).strip().lower()
        if key not in kinds:
            msg = f"sound must be one of OK, Asterisk, Exclamation, Hand, Question, got '{sound}'."
            raise ValueError(msg)
        winsound.MessageBeep(kinds[key])

