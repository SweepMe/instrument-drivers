# Switch (PC Variable Wait)

**Module**: Switch

## Description

Adds a wait time that is swept like any other value, e.g. to vary the hold time of a measurement.

## Requirements

- No instrument and no extra libraries.

## Usage

Add the Switch module, select this driver and choose the **SweepMode**:

- `Hold in s`: waits the sweep value after all modules of the branch applied and reached their values.
- `Delay in s`: waits until the sweep value passed since the previous point of this module started. If measuring the
  point took longer anyway, it continues at once, so a delay adds no time then.

Sequences saved with the earlier labels `Hold [s]` and `Delay [s]` keep working. A wait ends early when the run is
stopped. Negative wait times stop the run with an error.

## Returns

- **Hold time** or **Delay time** (s), after the SweepMode: the wait time of the point.
