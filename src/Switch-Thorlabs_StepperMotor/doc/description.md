# Thorlabs Stepper Motor

This driver controls Thorlabs stepper motor controller modules (e.g. **MST601**) that are housed in a **Thorlabs Modular
Rack** (MMR60x series) via the **Kinesis** motion control software. It moves the attached linear stage or actuator to
absolute or relative positions in millimetres and returns the current position as a measurement variable.

---

## Requirements

- **Thorlabs Kinesis** must be installed. The driver expects the default installation folder:
  - 64-bit SweepMe!: `C:\Program Files\Thorlabs\Kinesis`
  - 32-bit SweepMe!: `C:\Program Files (x86)\Thorlabs\Kinesis`

  The bitness of the installed Kinesis version must match the bitness of SweepMe!. If the .NET dlls cannot be loaded,
  the driver stays silent until you press *Find Ports* or start a run, and then raises an `ImportError`.
- **Kinesis must be closed** while the driver is used. Kinesis and SweepMe! cannot hold the device at the same time.
- The rack must be connected via USB and powered on.
- No additional Python packages have to be installed; the driver uses the .NET interface via `pythonnet`, which ships
  with SweepMe!.

---

## Setup in SweepMe!

1. Close Kinesis.
2. Add the driver to the sequencer and press **Find Ports**. The driver lists the serial numbers of all devices that
   Kinesis reports — this includes non-stepper devices, so pick the serial number of your rack.
3. Select the **Channel** (bay) in which the stepper module is installed.
4. Set **Max Velocity** and **Acceleration**, and choose a **SweepMode**.

If no device is found, the port list shows `No devices found!`. Starting a run with this entry raises an error.

---

## Parameters

- **Port**: serial number of the modular rack.
- **Channel**: bay number of the stepper module inside the rack (default `1`). Each bay is addressed by its own driver
  instance; several instances may share the same rack (see *Multiple instances*).
- **SweepMode**: what the sweep value means.
  - **Position** — the sweep value is an absolute target position in mm. The motor moves to that position.
  - **Relative Position** — the sweep value is a distance in mm relative to the current position. A positive value moves
    forward, a negative value moves backward.
  - **None** — no movement is performed. The driver only reads back the current position.
- **Max Velocity in mm/s**: maximum travel velocity. This value is also used to estimate the movement timeout, so it
  must be set (see *Known issues*).
- **Acceleration in mm/s²**: acceleration used for the moves. Leave empty to keep the value currently stored in the
  device.
- **Timeout in s**: timeout for the **homing** operation (default `60`). It does **not** limit normal moves — those use
  an automatically calculated timeout (see *Timeouts*).
- **Simulation Mode**: starts the Kinesis simulation manager so that virtual devices created in the *Kinesis Simulator*
  can be used without hardware. Enable the checkbox first, then press **Find Ports** so that the simulated devices show
  up in the port list.
- **Home at start**: performs a homing move when the sequencer branch is entered, before the first position is applied.
- **Home velocity**: only shown when *Home at start* is enabled. Velocity used for the homing move in mm/s.

---

## Returned variables

| Variable   | Unit | Description                                        |
|------------|------|----------------------------------------------------|
| `Position` | mm   | Position read back from the controller after the move. |

---

## Behaviour during a run

- **connect()** — opens the rack, waits for the settings to be initialized, starts the status polling loop (250 ms) and
  enables the channel. If the first connection attempt times out, the driver retries once.
- **configure()** — loads the motor configuration, applies *Max Velocity* / *Acceleration* and, if enabled, performs the
  homing move. `configure()` runs every time the sequencer branch is entered, so homing is repeated on each entry.
- **apply()** — starts the move and returns immediately. The move is issued as a **non-blocking** Kinesis command with a
  completion callback, so other drivers in the same sequencer step can act while the stage is still travelling.
- **reach()** — waits until the controller reports that the motion has finished, or until the calculated timeout
  expires. Stopping the run aborts the wait.
- **adapt()** — repeats a relative move that SweepMe! would otherwise skip. SweepMe! only calls `apply()` when the sweep
  value has changed; for relative movements the same value has to be applied again, for instance when a sequence with a
  constant step size is repeated in several cycles. The driver detects this case and performs the move in `adapt()`.
- **call()** — reads back and returns the current position in mm.
- **disconnect()** — stops polling and disconnects the rack.

---

## Timeouts

There are two independent timeouts:

- **Homing** uses the *Timeout in s* parameter.
- **Moves** use a timeout that the driver calculates from the travel distance and *Max Velocity*:

  ```
  timeout = max(60 s, 2 × distance / max_velocity)
  ```

  The result overwrites the *Timeout in s* value for the remainder of the run. There is therefore no way to shorten the
  movement timeout below 60 s via the GUI.

If the target position is not reached in time, the driver raises a `TimeoutError` and the measurement stops.

---

## Multiple instances

Several driver instances can address the same rack — for example one instance per bay, or the same module used in
different branches of the sequencer. The connection objects are shared through SweepMe!'s `device_communication`
dictionary using the key `Thorlabs stepper <serial number><channel>`. The first instance opens the connection, all
further instances reuse it, and the connection is closed once at the end of the run.

---

## Known issues

- **Max Velocity must not be empty.** Although *Acceleration* may be left empty to keep the device setting, an empty
  *Max Velocity* makes the timeout calculation fail with a `ValueError` at the first move. Always enter a value.
- **Kinesis running in parallel.** If Kinesis is open, connecting fails or the device behaves erratically. Close Kinesis
  completely, including any tray icon, before starting a run.
- **Simulation mode leaks into the device list.** Once simulation mode has been switched on, the Kinesis device list
  keeps reporting simulated devices even after simulation mode has been switched off again. Restart SweepMe! to get a
  clean device list.
- **Reconnecting after a disconnect.** Reconnecting to the same rack shortly after it has been disconnected can fail on
  the Kinesis side. If a run does not start after a previous run was stopped, wait a moment and try again, or restart
  SweepMe!.
- **Device not found.** Verify in the Kinesis *Device Manager* that the rack and the module are recognized by the
  system, then close Kinesis again.
