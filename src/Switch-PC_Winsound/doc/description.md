# Switch (PC Winsound)

**Module**: Switch

## Description

Plays each sweep value as a sine tone with soft edges on the speakers of the PC, e.g. to signal the progress of a
measurement acoustically.

## Requirements

- Windows. No instrument and no extra libraries.

## Usage

1. Add the Switch module and select this driver; the **SweepMode** is `Note in Hz`.
2. Sweep the frequency: 20 Hz to 20000 Hz, or 0 for a rest. A value outside stops the run with an error.
3. Set the length of each tone with **Duration in s** (0 to 60 s; 0 plays nothing).

The tone blocks the run until it has ended.

## Parameters

- **Duration in s**: length of each tone.

## Returns

- **Note** (Hz): the frequency that was played.

## Communication commands

- `play_note(note, duration)`: a square-wave beep of 37 to 32767 Hz for `duration` ms (Windows `Beep`).
- `play_melody(notes, durations, volume, fade_ms)`: a melody of sine tones (20 Hz to 20 kHz, 0 for a rest) with
  durations in ms, at most 60 s in total; `volume` 0 to 1.
- `message_beep(sound)`: a Windows system sound, `OK`, `Asterisk`, `Exclamation`, `Hand` or `Question`; returns at
  once.
