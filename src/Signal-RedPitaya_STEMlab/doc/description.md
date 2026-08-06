# Signal-RedPitaya_STEMlab

Driver for the fast analog outputs (OUT1, OUT2) of Red Pitaya STEMlab boards, controlled via the
SCPI server over Ethernet.

## Setup

1. Start the SCPI server on the Red Pitaya (web interface -> Development -> SCPI server, or
   `systemctl start redpitaya_scpi` on the board).
2. Enter the IP address of the board as the port, e.g. `192.168.178.xxx`.

## Known behavior

- **Output range**: the sum of the one-way amplitude and the absolute offset must not exceed
  +/- 1 V (+/- 2 V / +/- 10 V at Hi-Z for SIGNALlab). Values above this limit are clipped by the
  driver and a message box informs the user once per run. For example, amplitude 1 V combined with
  offset 1 V results in amplitude 1 V and offset 0 V.
- **Frequency range**: 1 Hz to 50 MHz, board dependent.
- **Trigger sources**: the SCPI server accepts `INT`, `EXT_PE`, `EXT_NE` and `GATED`. The GUI
  option "Immediately" uses the internal trigger source and sends the software trigger directly.
- **Arbitrary waveform**: the file selected under "ArbitraryWaveformFile" should contain exactly
  16384 samples normalized to the range -1 to 1. With fewer samples the output frequency is
  higher than the configured one.
- **The generation is started once in `configure`**, not per measurement point.
  `SOUR<n>:TRIG:INT` resets the FPGA and restarts the signal from its start phase, so sending it
  repeatedly would chop a continuous signal into fragments. During a sweep it is only re-sent
  where the instrument rebuilds the signal anyway: for frequency/period (`SOUR<n>:FREQ:FIX`) and
  for phase/delay. Amplitude and offset are applied by the FPGA without a restart, so an
  amplitude or offset sweep does not interrupt the running waveform.
- **Output load**: the outputs are calibrated for a 50 Ohm load. Measured with a high-impedance
  instrument (e.g. an SMU sourcing 0 A), the observed amplitude is noticeably larger than the
  configured one.
- **Operation mode**: only "Continuous" and "Burst" exist. The "Stream" option of earlier driver
  versions was never supported by the SCPI server; settings that still contain it raise a
  message asking to select a valid mode.
- The GUI is dynamic: duty cycle, arbitrary waveform file, and the burst fields only appear when
  the corresponding waveform or operation mode is selected.

## Requirements

- Every command used by this driver, including `SOUR<n>:TRIG:INT`, is listed in the Red Pitaya
  command reference as available since ecosystem 1.04-18. Red Pitaya's own documentation does not
  cover older ecosystems.
- Tested on OS 2.x (STEMlab 125-14) and on OS 0.98 (STEMlab 125-10).
- `SOUR<n>:TRIG:INT` is required since OS 2.00, where `OUTPUT<n>:STATE ON` only applies the
  initial voltage (`SOUR<n>:INITValue`, 0 V by default) to the output and does not start the
  signal. On OS 1.04, where enabling the output already started the generation, the additional
  command only restarts the signal from its start phase, which is harmless and makes the start
  phase deterministic.
- Board models: works with all boards that provide fast analog outputs, including the
  discontinued STEMlab 125-10. Not applicable to the STEMlab 125-14 4-Input, which has no fast
  analog outputs.
- Settings from older driver versions that use the operation mode "Stream" have to be changed to
  "Continuous" or "Burst". "Stream" was never a valid value of `SOUR<n>:BURS:STAT`.


## Reference

Red Pitaya SCPI command list:
https://redpitaya.readthedocs.io/en/latest/appsFeatures/remoteControl/command_list/commands-gen.html
