# Signal (Simulation Driver)

**Module**: Signal

## Description

A simulated signal generator for developing and testing Signal sequences without hardware. It returns the set
frequency and amplitude together with three periods of the simulated waveform. No instrument connection is required.

When a `Scope-Simulation_Driver` runs in the same sequence, it shows the simulated signal on its channel 1.

## Usage

1. Add the Signal module and select this *Simulation Driver*.
2. Choose the waveform and set frequency or period, amplitude, offset and delay or phase.
3. Optionally sweep one of them with **SweepMode**, then run the sequence.

## Parameters

- **SweepMode** — `None`, `Frequency in Hz`, `Period in s`, `Amplitude in V`, `Phase in deg` or `Delay in s`.
- **Waveform** — `Sine`, `Square`, `Triangle` or `Sawtooth`.
- **PeriodFrequency** — `Frequency in Hz` or `Period in s`; the value must be greater than 0.
- **AmplitudeHiLevel** — `Amplitude in V`.
- **OffsetLoLevel** — `Offset in V`.
- **DelayPhase** — `Delay in s` or `Phase in deg`; a positive delay shifts the waveform to later times, a positive
  phase to earlier times.

## Returns

- **Frequency** (Hz) and **Amplitude** (V) — the values in use.
- **Simulated Timestamps** (s) and **Simulated Signal** (V) — 100 points spanning three periods of the waveform.

## Communication commands

Usable from Instrument Control and pysweepme scripts without a sequence: `set_waveform`, `set_frequency`,
`set_amplitude`, `set_offset`, `set_delay`, `get_settings` and `sample_signal`, which returns the waveform at a given
number of points over a given duration.

## Scripting with pysweepme

`set_parameters()` applies **SweepMode** and **Waveform** at once. The values of **PeriodFrequency**,
**AmplitudeHiLevel**, **OffsetLoLevel** and **DelayPhase** are converted and checked only by `configure()`, as in
a SweepMe! run, and the generated signal keeps its previous frequency, amplitude, offset and delay until it runs.
Call it before measuring:

```python
import pysweepme

driver = pysweepme.get_driver("Signal-Simulation_Driver", r"<instrument-drivers>\src", "")
driver.set_parameters({"Waveform": "Square", "PeriodFrequencyValue": 1e3, "AmplitudeHiLevelValue": 2.0})
driver.connect()
try:
    driver.initialize()
    driver.configure()  # applies frequency, amplitude, offset and delay
    print(driver.read())
finally:
    driver.disconnect()
```

`disconnect()` removes the signal shared with a simulated oscilloscope, so a later `Scope-Simulation_Driver` in
the same Python process shows its own waveform again. The communication commands (`set_waveform`,
`set_frequency`, `set_amplitude`, ...) take effect at once, without `configure()`.
