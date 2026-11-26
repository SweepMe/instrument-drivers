# WaferProber (Simulation Driver)

**Module**: WaferProber

## Description

A simulated wafer prober for developing and testing WaferProber sequences without hardware. It offers a probe plan
of three wafers, the dies of a round 150 mm wafer with a die pitch of 10 mm, and two subsites, and it reports the
wafer geometry to the Map tab. No instrument connection is required.

## Usage

1. Add the WaferProber module and select this *Simulation Driver*.
2. Press **Update** to load the probe plan and the wafer geometry.
3. Select wafers, dies and subsites in the tables and run the sequence.

## Parameters

- **Port** — any of the offered numbers; the simulation does not use it.

## Returns

- **Wafer**, **Die** (`column,row`), **Die X** and **Die Y** (the die as integers, for heat maps), **Subsite** and
  **Skip** (always False).

## Behaviour

- Loading another wafer separates the probes; a sweep that was in contact contacts again on the new wafer.
- The dies are counted from the wafer centre, so the module's origin setting is left as the user set it.

## Communication commands

Usable from Instrument Control and pysweepme scripts without a sequence: `load_wafer`, `unload_wafer`,
`step_to_die`, `step_to_subsite`, `contact`, `separate`, `get_current_wafer`, `get_current_die`,
`get_current_subsite` and `get_status`.
