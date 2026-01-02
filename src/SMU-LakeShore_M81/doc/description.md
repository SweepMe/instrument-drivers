# SMU module (VS-10 + CM-10) for LakeShore M81

- This driver implements a combined Source-Measure Unit (SMU) using a VS-10 voltage source module paired with a CM-10 current measurement module inside the LakeShore M81 Synchronous Source/Measure System.
- Please note: There is a dedicated SMU hardware-module available for the M81 called "SMU-10". This driver is not suitable for that device.

## Idea of this combined SMU driver
- Use this driver as a **shortcut**, if you want to measure relatively simple DC **IV-curves**.
- Advanced IV-curves with AC-voltage shapes and lock-in functionality can be created by combining the VS-10 Switch driver and the CM-10 Logger driver. 

## Usage
1. Select Source Channel (S1..S3) and Measure Channel (M1..M3).
2. Select Sweep value source
3. Set compliance, ranges and integration speed

## Limitiations
- Pulsed measurements and List sweeps are not available for the Lakeshore M81