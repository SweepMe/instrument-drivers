# Keithley 4200-SCS

This driver only supports creating pulses in continuous mode.

## Setup

This driver can be used in two different ways:
- With the LPTlib server: Run the server on the device and connect via ethernet. The LPTlib server application and the corresponding manual can be found here: https://sweep-me.net/dashboard (SweepMe! account required).
- Running SweepMe! directly on the device: This requires the LPTlib server as well, but we can use localhost as the ip address. Set IP = localhost in 4200-Server.ini.
- KXCI communication via GPIB is not supported yet.
