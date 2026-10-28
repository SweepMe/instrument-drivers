# Rohde & Schwarz NGx

Driver for the Rohde & Schwarz NGx power supplies and source measure units (NGE, NGL, NGM, NGP, NGU).

## Usage

- The default channel is 1. The rear terminal also works with this channel. Do not change it unless you need it.
- The USB protocol needs to be set to TMC manually from the front panel. The setting can be found under
  "USB Class" in the "Network Connections" dialog.
- To use 4-wire sensing, connect the sense terminals of the instrument to your circuit; the instrument then
  switches to 4-wire mode by itself.
- An output delivers only when it is armed (`set_output_on`) and the output generation is on
  (`set_generation_on`). The output generation acts on every armed output at once, so switching it off in one
  SweepMe! module also stops the other channels of the same instrument.

## Channels

The instrument keeps the selected output (`INST:OUT<n>`), and every command acts on the output selected last. Each
command of the driver therefore takes its `channel`, and the driver selects the output only when it differs from
the one selected last. Several modules or scripts on one instrument share that knowledge through the port.

- The NGU series has one output and does not understand `INST:OUT`: channel 1 is the only channel there.
- A change made at the front panel, or a raw `INST:OUT` sent past the driver, is not noticed: the next command may
  then act on the wrong output. `reset_instrument` makes the driver select again.
- `set_channel(channel)` is kept for existing scripts, but is no longer needed.

## Parameters

- **Speed** sets the integration time in power line cycles (NPLC). The values are known for the NGU series only
  (0, 5, 10, 50, 100); the other models are not checked yet.
