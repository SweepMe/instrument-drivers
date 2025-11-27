# Agilent B1500A — Semiconductor Parameter Analyzer

This driver controls the Agilent B1500A for single measurements and synchronized list sweeps. It enables sourcing of voltage and current, measurement timing and list-sweep features used for multi‑channel experiments.

## Prerequisites
- Install Keysight IO Suite on the PC running SweepMe!. Keysight IO Suite 2025 is incompatible; the driver has been tested with Keysight IO Suite 2023 Update 1.
- The helper application `Start EasyExpert` must be running on the device. Minimize IO Control and close any active EasyExpert GUI instances to avoid resource conflicts.
- Ensure the correct GPIB/USB port is selected and the instrument is powered and addressed.

## List mode (synchronized multi‑channel sweeps)
- When using list mode, the device returns the programmed source values (not measured source values).
- A branch can contain multiple channels; if any channel in a branch uses list mode, the entire branch is treated as a list sweep.
- Single‑value channels inside a list branch produce lists where `start = stop = value`.
- All channels participating in the same list sweep must share the same list length, hold time and delay time.
- Timestamps are provided and are normalized relative to the list master channel.
- For longer measurements the default timeout may be insufficient. To increase the timeout, create a custom driver version and set, for example: `self.port_properties = {"timeout": 30}`
    
## Usage guidance
- Use list mode for synchronized, multi‑channel acquisitions (e.g. concurrent source/measure sequences).
- Use single measurement mode for isolated, on‑demand readings.
- Check range, compliance and averaging settings before starting a sweep to avoid measurement errors or instrument protection trips.