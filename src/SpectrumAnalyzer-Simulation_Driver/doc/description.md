# SpectrumAnalyzer (Simulation Driver)

**Module**: SpectrumAnalyzer

## Description

A simulated spectrum analyzer for developing and testing SpectrumAnalyzer sequences without hardware. It returns a
trace with three Gaussian peaks over the selected frequency range. No instrument connection is required.

## Usage

1. Add the SpectrumAnalyzer module and select this *Simulation Driver*.
2. Choose the simulation mode in the **Port** field (see below).
3. Set the frequency range and the reference level, then run the sequence.

## Parameters

- **Port** — selects the simulation mode:
  - `Port 1: Simulated Spectrum` — three Gaussian peaks with additive random noise.
  - `Port 2: No Noise` — the same spectrum without noise, for reproducible tests.

## Returns

- **Frequency** (Hz) — the frequencies of the trace.
- **Power** (dBm) — the power at each frequency.
