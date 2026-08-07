# Thorlabs LTS

This driver controls **Thorlabs LTS long travel stages** (LTS150 and LTS300, including the metric `/M` variants) via the
**Kinesis** motion control software. These stages have the stepper motor controller built in and are connected directly
over USB — no separate rack or controller module is required. The driver moves the stage to absolute or relative
positions in millimetres and returns the current position as a measurement variable.

---

## Requirements

- **Thorlabs Kinesis** must be installed. The driver expects the default installation folder:
  - 64-bit SweepMe!: `C:\Program Files\Thorlabs\Kinesis`
  - 32-bit SweepMe!: `C:\Program Files (x86)\Thorlabs\Kinesis`

  The bitness of the installed Kinesis version must match the bitness of SweepMe!. If the .NET dlls cannot be loaded,
  the driver stays silent until you press *Find Ports* or start a run, and then raises an `ImportError`.
- **Kinesis must be closed** while the driver is used. Kinesis and SweepMe! cannot hold the stage at the same time.
- The stage must be connected via USB and powered on.
- No additional Python packages have to be installed; the driver uses the .NET interface via `pythonnet`, which ships
  with SweepMe!.

---

## Setup in SweepMe!

1. Close Kinesis.
2. Add the driver to the sequencer and press **Find Ports**. The driver lists the serial numbers of all devices that
   Kinesis reports — this includes non-LTS devices, so pick the serial number of your stage.
3. Choose a **SweepMode**, set the **Velocity**, and decide whether the stage should be homed at the start.

If no device is found, the port list shows `No devices found!`. Starting a run with this entry raises an error.

---

## Parameters

- **Port**: serial number of the LTS stage.
- **SweepMode**: what the sweep value means.
  - **Absolute position in mm** — the sweep value is the target position. The stage moves to that position.
  - **Relative position in mm** — the sweep value is a distance relative to the current position. A positive value moves
    forward, a negative value moves backward. The driver reads the current position, adds the sweep value and moves to
    the resulting absolute position. A move that would end at a negative position is rejected with an error.
- **Velocity in mm/s**: maximum travel velocity (default `10.0`). This value is also used to estimate the movement
  timeout, and it is currently used for the homing move as well (see *Known issues*).
- **Home at start**: performs a homing move when the sequencer branch is entered, before the first position is applied.
  Enabled by default.
- **Home velocity in mm/s**: only shown when *Home at start* is enabled. **Currently without effect** — see
  *Known issues*.

---

## Returned variables

| Variable   | Unit | Description                                             |
|------------|------|---------------------------------------------------------|
| `Position` | mm   | Position read back from the stage after the move.        |

---

## Behaviour during a run

- **connect()** — verifies that the selected serial number is in the Kinesis device list, creates the stage object and
  connects to it. If the device reports that it is not ready yet, the driver retries for up to 10 s.
- **initialize()** — waits for the device settings to be initialized, starts the status polling loop (250 ms), enables
  the device and loads the motor configuration.
- **configure()** — applies the *Velocity* and, if enabled, performs the homing move with a fixed 60 s timeout.
  `configure()` runs every time the sequencer branch is entered, so homing is repeated on each entry.
- **apply()** — starts the move and returns immediately. The move is issued as a **non-blocking** Kinesis command with a
  completion callback, so other drivers in the same sequencer step can act while the stage is still travelling.
- **reach()** — waits until the stage reports that the motion has finished. Stopping the run aborts the wait.
- **adapt()** — repeats a relative move that SweepMe! would otherwise skip. SweepMe! only calls `apply()` when the sweep
  value has changed; for relative movements the same value has to be applied again, for instance when a sequence with a
  constant step size is repeated in several cycles. The driver detects this case and performs the move in `adapt()`.
- **call()** — reads back and returns the current position in mm.
- **poweroff()** — stops any ongoing stage movement immediately when the sequencer branch is left.
- **disconnect()** — stops polling and disconnects the stage.

---

## Timeouts

The driver has no timeout parameter in the GUI. Two timeouts are applied internally:

- **Homing** uses a fixed timeout of 60 s.
- **Moves** use a timeout calculated from the travel distance and the *Velocity*:

  ```
  timeout = max(60 s, 2 × distance / velocity)
  ```

  Note that this calculated timeout is currently not enforced as intended — see *Known issues*. If a move never
  completes, stop the run manually.

---

## Known issues

- **One driver instance per stage.** Unlike the *Thorlabs Stepper Motor* driver, this driver does not share its
  connection between driver instances. Do not add the same stage twice to the sequencer.
- **Upper travel limit is not checked.** Relative moves are only checked against a lower limit of 0 mm. A target beyond
  the travel range of the stage is passed to Kinesis, which will reject or clip it.
- **Kinesis running in parallel.** If Kinesis is open, connecting fails or the stage behaves erratically. Close Kinesis
  completely, including any tray icon, before starting a run.
- **Device not found.** Verify in the Kinesis *Device Manager* that the stage is recognized by the system, then close
  Kinesis again.
