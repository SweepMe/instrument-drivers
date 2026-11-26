# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2021-2026 SweepMe! GmbH (sweep-me.net)
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
# * Module: Switch
# * Instrument: PC Winsound

"""SweepMe! driver that plays the sweep value as a tone."""

from __future__ import annotations

import array
import io
import math
import sys
import wave
import winsound  # part of the Python standard library on Windows
from typing import Annotated, Any, Literal

from pysweepme import EmptyDevice
from pysweepme.commands import Range, Unit, command

SAMPLE_RATE = 44100  # Hz, for the synthesized melodies of play_melody
MAX_MELODY_S = 60  # longest melody play_melody synthesizes, to bound memory and blocking time
MIN_MELODY_NOTE_HZ = 20  # lowest note of play_melody besides 0 for a rest
MAX_MELODY_NOTE_HZ = 20000  # highest note of play_melody

Hertz = Annotated[float, Unit("Hz")]
Milliseconds = Annotated[float, Unit("ms")]
BeepNote = Annotated[int, Unit("Hz"), Range(37, 32767)]  # the range of winsound.Beep
MelodyNote = Annotated[Hertz, Range(0, MAX_MELODY_NOTE_HZ)]
SystemSound = Literal["OK", "Asterisk", "Exclamation", "Hand", "Question"]

SYSTEM_SOUNDS: dict[str, int] = {
    "OK": winsound.MB_OK,
    "Asterisk": winsound.MB_ICONASTERISK,
    "Exclamation": winsound.MB_ICONEXCLAMATION,
    "Hand": winsound.MB_ICONHAND,
    "Question": winsound.MB_ICONQUESTION,
}


class Device(EmptyDevice):
    """Driver that plays each sweep value as a sine tone with soft edges."""

    def __init__(self) -> None:
        """Define the returned variables."""
        super().__init__()

        self.shortname = "Winsound"

        self.variables = ["Note"]
        self.units = ["Hz"]
        self.plottype = [True]
        self.savetype = [True]

        self.gui_parameters: dict[str, Any] = {}
        self.duration_ms: float = 250.0
        self.note: float = float("nan")

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:  # noqa: ARG002
        """Return the GUI fields with their defaults."""
        return {
            "SweepMode": ["Note in Hz"],
            "Duration in s": 0.25,
        }

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Store the selections."""
        self.gui_parameters = parameters

    def configure(self) -> None:
        """Convert and check the duration of a tone."""
        duration = self.gui_parameters.get("Duration in s", 0.25)
        try:
            duration_s = float(duration)
        except ValueError:
            msg = f"Duration in s must be a number, not '{duration}'."
            raise ValueError(msg) from None
        if not 0 <= duration_s <= MAX_MELODY_S:
            msg = f"Duration in s must be between 0 and {MAX_MELODY_S} s, not {duration_s}."
            raise ValueError(msg)
        self.duration_ms = int(duration_s * 1000)
        self.note = float("nan")

    def apply(self) -> None:
        """Play the sweep value as a tone of the set duration; a duration of 0 plays nothing."""
        note = float(self.value)
        # checked before the conversion to int, which would turn -0.5 into a rest or 20000.5 into 20000
        if note != 0 and not MIN_MELODY_NOTE_HZ <= note <= MAX_MELODY_NOTE_HZ:
            msg = f"Note must be 0 (rest) or between {MIN_MELODY_NOTE_HZ} and {MAX_MELODY_NOTE_HZ} Hz, not {note}."
            raise ValueError(msg)
        self.note = int(note)
        if self.duration_ms > 0:
            self.play_melody([self.note], [self.duration_ms])

    def call(self) -> float:
        """Return the note that was played."""
        return self.note

    # --- communication commands ---------------------------------------------

    @command(kind="run")
    def play_note(self, note: BeepNote, duration: Annotated[Milliseconds, Range(0, None)]) -> None:
        """Play a square-wave beep of the given frequency and duration; blocks until it has ended."""
        winsound.Beep(int(note), int(duration))

    @command(kind="run")
    def play_melody(
        self,
        notes: list[MelodyNote],
        durations: list[Annotated[Milliseconds, Range(0, MAX_MELODY_S * 1000)]],
        volume: Annotated[float, Range(0, 1)] = 0.3,
        fade_ms: Annotated[Milliseconds, Range(0, None)] = 15,
    ) -> None:
        """Play a melody of sine tones with soft edges as one sound; blocks until it has ended, at most 60 s.

        `notes` are frequencies (20 Hz to 20 kHz, 0 for a rest), `durations` the length of each note. Every note
        fades in and out over `fade_ms`, so there are no clicks and repeated notes stay separate. `volume` is 0 to 1.
        Unlike play_note (winsound.Beep, a hard-edged square wave) the melody is synthesized and played with
        winsound.PlaySound.
        """
        self._check_melody(notes, durations)

        peak = volume * 32767
        samples = array.array("h")
        for note, duration in zip(notes, durations, strict=True):
            n = round(duration / 1000 * SAMPLE_RATE)
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

    @command(kind="run")
    def message_beep(self, sound: SystemSound = "OK") -> None:
        """Play a Windows system sound; returns at once while the sound plays in the background."""
        winsound.MessageBeep(SYSTEM_SOUNDS[sound])

    # --- helpers --------------------------------------------------------------

    @staticmethod
    def _check_melody(notes: list[float], durations: list[float]) -> None:
        """Raise on what the annotations of play_melody cannot express."""
        if len(notes) != len(durations):
            msg = f"notes and durations must have the same length, got {len(notes)} and {len(durations)}."
            raise ValueError(msg)
        if not notes:
            msg = "notes must not be empty."
            raise ValueError(msg)
        for note in notes:
            if 0 < note < MIN_MELODY_NOTE_HZ:
                msg = (
                    f"every note must be 0 (rest) or between {MIN_MELODY_NOTE_HZ} and {MAX_MELODY_NOTE_HZ} Hz, "
                    f"got {note}."
                )
                raise ValueError(msg)
        if min(durations) <= 0:
            msg = f"every duration must be positive, got {min(durations)} ms."
            raise ValueError(msg)
        if sum(durations) > MAX_MELODY_S * 1000:
            msg = f"the melody lasts {sum(durations) / 1000:.1f} s, at most {MAX_MELODY_S} s are allowed."
            raise ValueError(msg)
