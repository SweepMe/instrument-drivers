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

import array
import io
import math
import sys
import wave
import winsound  # part of the Python standard library on Windows

from EmptyDeviceClass import EmptyDevice

SAMPLE_RATE = 44100  # Hz, for the synthesized melodies of play_melody
MAX_MELODY_S = 60  # longest melody play_melody synthesizes, to bound memory and blocking time


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

    def play_melody(
        self, notes: list, durations: list, volume: float = 0.3, fade_ms: float = 15,
    ) -> None:
        """Play a melody of sine tones with soft edges, as one continuous sound.

        `notes` are frequencies in Hz (20 to 20000, 0 for a rest), `durations` the
        length of each note in milliseconds. Every note fades in and out over
        `fade_ms`, so there are no clicks and repeated notes stay separate.
        `volume` is 0 to 1. Unlike play_note (winsound.Beep, a hard-edged square
        wave) the melody is synthesized and played with winsound.PlaySound.
        Blocks until the melody has ended; at most 60 s.
        """
        notes = [float(n) for n in notes]
        durations = [float(d) for d in durations]
        volume = float(volume)
        fade_ms = float(fade_ms)
        if len(notes) != len(durations):
            msg = f"notes and durations must have the same length, got {len(notes)} and {len(durations)}."
            raise ValueError(msg)
        if not notes:
            msg = "notes must not be empty."
            raise ValueError(msg)
        for note in notes:
            if note != 0 and not 20 <= note <= 20000:
                msg = f"every note must be 0 (rest) or between 20 and 20000 Hz, got {note}."
                raise ValueError(msg)
        if min(durations) <= 0:
            msg = f"every duration must be positive, got {min(durations)} ms."
            raise ValueError(msg)
        if sum(durations) > MAX_MELODY_S * 1000:
            msg = f"the melody lasts {sum(durations) / 1000:.1f} s, at most {MAX_MELODY_S} s are allowed."
            raise ValueError(msg)
        if not 0 <= volume <= 1:
            msg = f"volume must be between 0 and 1, got {volume}."
            raise ValueError(msg)
        if fade_ms < 0:
            msg = f"fade_ms must not be negative, got {fade_ms}."
            raise ValueError(msg)

        peak = volume * 32767
        samples = array.array("h")
        for note, duration in zip(notes, durations):
            n = int(round(duration / 1000 * SAMPLE_RATE))
            if note == 0:
                samples.extend([0] * n)
                continue
            fade = min(int(fade_ms / 1000 * SAMPLE_RATE), n // 2)
            step = 2 * math.pi * note / SAMPLE_RATE
            for k in range(n):
                # raised-cosine fade in and out, so the note starts and ends at zero
                if k < fade:
                    envelope = 0.5 - 0.5 * math.cos(math.pi * k / fade)
                elif k >= n - fade:
                    envelope = 0.5 - 0.5 * math.cos(math.pi * (n - 1 - k) / fade)
                else:
                    envelope = 1.0
                samples.append(int(peak * envelope * math.sin(step * k)))
        if sys.byteorder == "big":
            samples.byteswap()  # WAV data is little-endian

        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(SAMPLE_RATE)
            wav.writeframes(samples.tobytes())
        winsound.PlaySound(buffer.getvalue(), winsound.SND_MEMORY)

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

