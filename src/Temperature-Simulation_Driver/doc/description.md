# Temperature (Simulation Driver)

**Module**: Temperature

## Description

A simulated temperature controller for developing and testing Temperature sequences without hardware. After a new
setpoint, the temperature moves towards it while it is read. No instrument connection is required.

Every instance with the same **Port** value shares one simulated controller, so several Temperature modules can
watch the same temperature.

## Usage

1. Add the Temperature module and select this *Simulation Driver*.
2. Choose the **Sensor** mode and set **SweepMode** to `Temperature` to sweep the setpoint.
3. Run the sequence. The module waits until the temperature reaches each setpoint.

## Parameters

- **SweepMode** — `None` or `Temperature`; with `Temperature`, the sweep value is the setpoint in °C.
- **TemperatureUnit** — `°C`.
- **Port** — any text; instances with the same text share one simulated controller (default `0`).
- **Sensor** — `Realistic`: the temperature settles exponentially with a time constant of 5 s, with measurement
  noise. `No Noise`: the temperature starts at 25 °C at the start of each run and ramps linearly at 0.5 K/s without
  noise, for reproducible tests.

## Returns

- **Temperature** (°C).

## Communication commands

Usable from Instrument Control and pysweepme scripts without a sequence: `set_temperature_setpoint` /
`get_temperature_setpoint`, `get_temperature` and `set_sensor_mode` / `get_sensor_mode`.
