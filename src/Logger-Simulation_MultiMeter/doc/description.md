# Logger (Simulation MultiMeter)

**Module**: Logger

## Description

A simulated multimeter for developing and testing Logger sequences without hardware. It reads simulated voltages
and currents on up to four channels. No instrument connection is required.

## Usage

1. Add the Logger module and select this *Simulation MultiMeter* driver.
2. Enter the channels to read in **Voltage Channels** and **Current Channels**, each a comma-separated list. At most
   four channels in total.
3. Run the sequence. The driver returns one value per channel.

## Parameters

- **Voltage Channels** — channels read as voltages, e.g. `1,2`.
- **Current Channels** — channels read as currents, e.g. `3,4`.
- **Noise level in %** — random noise added to every reading.

## Returns

- **Voltage CH<n>** (V) — channel number × 1 V plus noise.
- **Current CH<n>** (A) — channel number × 0.1 A plus noise.
