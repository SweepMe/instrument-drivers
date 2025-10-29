# Keithley 4200-SCS

## Setup

This driver can be used in three different ways:
- Using the KXCI software running on the device and a GPIB connection.
- Using the LPTlib server application running on the device and a TCP/IP connection. Download from https://sweep-me.net/dashboard (SweepMe account required). Setup as described in the LPTlib manual.
- Running SweepMe! directly on the device. This requires the lptlib server to be running, but we can use localhost as the ip address. Set IP = localhost in 4200-Server.ini.
Please note that for the KXCI mode, some features like Pulse Mode, List Mode, and fast acquisition are not supported yet.

## Parameters

- Current range: Limited: Sets the lowest current range of the SMU to be used when measuring with auto range to save time. Current range denotes the measurement range. The source range is set to auto by default.
- Speed/Integration: Sets the integration time to NPLC (Power Line Cycles) or to a predefined speed setting very fast (0.01 NPLC), Fast (0.1 NPLC), Medium (1 NPLC), or Slow (10 NPLC). Custom speed requires delay factor, filter factor, and A/D aperture time to be set. See the manual for more information.

## List Mode

- Activate Sweep value: List sweep
- List sweep parameters: choose a linear or logarithmic created list, or a custom list
- For fast measurement, use fixed current range
- It is possible to synchronize multiple SMU channels in list mode. However, currently only one channel can run a list, while the others can only source a single voltage or current.
- If list mode is activated for one channel, all other channels in the same branch will return list results as well. Only the main channel will return timestamps and zeroes time stamps
- delay: can either be a single value (The constant delay in seconds between each sourcing step and the measurement of a list sweep) or a list, which has to be the same length as the list sweep to set an individual delay for each step.