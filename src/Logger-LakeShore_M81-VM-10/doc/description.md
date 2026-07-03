# Logger driver for the VM-10 module of the LakeShore M81-SSM

- Logs DC and AC voltages using the VM-10 voltage measure module of the LakeShore M81 Synchronous Source Measure System.
- Three physical measure channels (M1, M2, M3) are available on the M81. Connect your VM-10 module to one of them and select the corresponding channel in SweepMe!.
- For phase-sensitive detection at a reference frequency, use the LockIn driver "LockIn-LakeShore_M81-VM-10" instead.

## Modes and returned variables

- **DC mode**: returns **Voltage DC** in V, averaged over the configured averaging time.
- **AC mode**: returns **Voltage RMS** (total RMS including AC and DC components within the observation window) and **Voltage DC**, both in V. With "Include peak values" enabled, it additionally returns **Voltage Positive Peak**, **Voltage Negative Peak**, and **Voltage Peak-Peak**. All values of one measurement point stem from a single, time-synchronized acquisition.

Special values: **+inf** indicates a range overload, **NaN** indicates that the value is invalid or still settling. Choose a larger range (or Auto) on overload.

## Averaging time

The averaging time is set in number of power line cycles (NPLC, 0.01 to 600). The M81 detects the line frequency automatically. For the best rejection of line-related interference, use an integer number of NPLC. Each measurement point waits for settling plus the averaging time, so large NPLC values slow down the acquisition accordingly.

## Range

- Ranges: 10 V, 1 V, 100 mV, 10 mV, or Auto. The lowest usable range gives the best performance. The VM-10 features seamless range transitions.
- Restriction: the 10 V and 1 V ranges are not available while the analog input filter is enabled with optimization "Highest reserve". The driver raises an error for this combination.
- "Frequency range threshold factor" (0.0–1.0): during autorange with AC signals, a range is chosen such that the signal frequency does not exceed this fraction of the range's -3 dB bandwidth.

## Input configuration and coupling

- **Input configuration**: "A-B" (differential), "A" (single-ended vs. measure ground), or "Ground" (input internally grounded, e.g. for offset checks).
- **Coupling**: DC or AC. AC coupling engages a 0.16 Hz high pass and blocks DC signals; the driver therefore rejects AC coupling in DC mode. Note that with AC coupling the input bias current causes a small DC offset.

## Analog input filter

The VM-10 contains hardware high pass and low pass filters (corner frequencies 10 Hz to 10 kHz, 6 or 12 dB/oct) in front of the amplifier chain, useful for rejecting large interfering signals:

- **Lowest noise**: gain before the filters; best noise, but large interferers can cause overloads.
- **Highest reserve**: all gain after the filters; tolerates the largest interference at the cost of higher noise (10 V and 1 V ranges unavailable).

The high pass filter is only offered in AC mode, since it would remove the DC component in DC mode.

Note: the datasheet also lists 30 kHz corner frequencies, but the remote interface manual only documents corner frequencies up to 10 kHz, so this driver offers up to 10 kHz.
