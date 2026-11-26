# Keithley 4200-SCS

## Setup

This driver can be used in three different ways:
- With KXCI: Start KXCI on the 4200 and connect via GPIB.
- With the LPTlib server: Run the server on the device and connect via ethernet. The LPTlib server application and the corresponding manual can be found here: https://sweep-me.net/dashboard (SweepMe! account required).
- Running SweepMe! directly on the device: This requires the LPTlib server as well, but we can use localhost as the ip address. Set IP = localhost in 4200-Server.ini.

Please note that for the KXCI mode, some features like Pulse Mode and fast acquisition are not supported yet.

## Parameters

- Current range: Limited: Sets the lowest current range of the SMU to be used when measuring with auto range to save time. Current range denotes the measurement range. The source range is set to auto by default. In KXCI mode, a current source with a Fixed range also sources on that range, so that it does not drop to its lowest range at 0 A.
- Speed/Integration: Sets the integration time to NPLC (Power Line Cycles) or to a predefined speed setting very fast (0.01 NPLC), Fast (0.1 NPLC), Medium (1 NPLC), or Slow (10 NPLC). Custom speed requires delay factor, filter factor, and A/D aperture time to be set. See the manual for more information.

## Compliance warning

In KXCI mode, the driver writes a warning to the Debug widget at every measurement point at which the SMU channel is in compliance. To turn it off, set `WARN_ON_COMPLIANCE = False` at the top of `main.py`.

## List Mode

- Activate Sweep value: List sweep
- List sweep parameters: choose a linear or logarithmic created list, or a custom list
- For fast measurement, use fixed current range
- It is possible to synchronize multiple SMU channels in list mode. However, currently only one channel can run a list, while the others can only source a single voltage or current.
- If list mode is activated for one channel, all other channels in the same branch will return list results as well. Only the main channel will return timestamps and zeroes time stamps
- delay: can either be a single value (The constant delay in seconds between each sourcing step and the measurement of a list sweep) or a list, which has to be the same length as the list sweep to set an individual delay for each step.

### List mode via KXCI

List sweeps also work via KXCI (GPIB or TCPIP). The driver then runs them in the KXCI system mode (commands `VL`/`IL`) and switches back to user mode for the next branch. The differences to the LPTlib server:

- At most 4096 points per list.
- The delay is one value for all points, from 0 to 6.553 s. A list of delays is not supported.
- All installed SMUs take part in a KXCI test: SMUs that are not used in the branch of the list sweep are switched off.
- At most 6 quantities are measured. With up to 3 channels, voltage and current of every channel are measured. With 4 channels, the measured quantity of every channel (the current of a voltage source, the voltage of a current source) is measured, and the sourced quantity of some channels is returned as its set value.
- A current source with a Fixed range sources on that range, otherwise with auto range.