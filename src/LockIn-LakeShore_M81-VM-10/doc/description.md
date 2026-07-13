# Lock-In driver for the VM-10 module of the LakeShore M81-SSM

- Performs phase-sensitive (lock-in) voltage measurements using the VM-10 voltage measure module of the LakeShore M81 Synchronous Source Measure System.
- Three physical measure channels (M1, M2, M3) are available on the M81. Connect your VM-10 module to one of them and select the corresponding channel in SweepMe!.
- For plain DC/AC voltage measurements without lock-in detection, use the Logger driver "Logger-LakeShore_M81-VM-10" instead.

## Returned variables

- **X** - in-phase voltage component (aligned with the reference), in V
- **Y** - quadrature voltage component (90° out of phase), in V
- **Magnitude** - R = sqrt(X² + Y²), in V
- **Phase** - phase angle θ of the signal relative to the reference, in degrees
- **Frequency** - the detected reference frequency, in Hz
- **Lock-In DC** - DC component of the input signal, in V (only measured when the "High pass digital filter" is ON, otherwise NaN)

Special values: **+inf** indicates a range overload, **NaN** indicates that the PLL is unlocked or the value is not available. Choose a larger range (or Auto) on overload.

## Reference source

- The lock-in detects signals coherent with the selected reference. Choose the M81 source channel (S1, S2, S3) that excites your sample, or "Reference In" for the external BNC reference input.
- The lock-in frequency is defined by the reference; it is not set on the VM-10 itself. If no AC source is active, lock-in readings will return zero or noise.
- The "Lock-In harmonic" allows detection at integer multiples of the reference frequency (e.g. 2 for second-harmonic detection). Harmonic × reference frequency must not exceed 100 kHz.

## Measurement procedure

The driver requests all lock-in values (X, Y, R, θ, frequency) with a single synchronized `FETCh:MULTiple` query together with the instrument's settling flag. If the instrument reports that the measurement is still settling (e.g. after a range change or a new source value), the driver keeps polling until the value is settled or the port timeout (15 s) is exceeded.

- **WaitTimeConstants = "Auto"** (recommended): the driver relies on the instrument's settling flag alone.
- **WaitTimeConstants = number**: the driver additionally waits this number of time constants before every measurement point. Use this when you sweep a source parameter and want a defined extra settle time, e.g. 5–10 time constants for 0.1 % settling (see the table in the M81 manual, section "Choosing Lock-In Filter Settings").

## Output filters

Two output filters act on the phase-sensitive detector (PSD) output:

- **Traditional low pass filter (IIR)**: configured via "TimeConstant" (0.0001 s to 10,000 s) and "Slope" (6/12/18/24 dB/oct). Longer time constants and steeper slopes reduce the equivalent noise bandwidth at the cost of longer settling. Enter a number to enable it, or select "Traditional low pass output filter OFF" to disable it.
- **Averaging filter (FIR)**: a moving average over N cycles of the reference frequency, set via "Averaging reference cycles" (0 = off). It strongly rejects the carrier and its harmonics. Note that at low reference frequencies N cycles can take a long time (N / f_ref seconds).

At least one output filter should be enabled for a meaningful lock-in measurement. A good starting point is a time constant of 0.1 s with 12 dB/oct plus 10 averaging reference cycles.

## Sensitivity (input range)

- Ranges: 10 V, 1 V, 100 mV, 10 mV, or Auto. The lowest usable range gives the best performance. The VM-10 features seamless range transitions.
- Restriction: the 10 V and 1 V ranges are not available while the analog input filter is enabled with optimization "Highest reserve". The driver raises an error for this combination.
- "Frequency range threshold factor" (0.0–1.0): during autorange, a range is chosen such that the signal frequency does not exceed this fraction of the range's -3 dB bandwidth.

## Input configuration and coupling

- **Input**: "A-B" (differential), "A" (single-ended vs. measure ground), or "Ground" (input internally grounded, e.g. for offset checks).
- **Coupling**: DC or AC. AC coupling engages a 0.16 Hz high pass and blocks DC signals; note that the input bias current then causes a small DC offset.

## Analog input filter ("Reserve")

The VM-10 contains hardware high pass and low pass filters (corner frequencies 10 Hz to 10 kHz, 6 or 12 dB/oct) in front of the amplifier chain. They are enabled by selecting a filter optimization:

- **Lowest noise**: gain before the filters; best noise, but large interferers can cause overloads.
- **Highest reserve**: all gain after the filters; tolerates the largest interference at the cost of higher noise (10 V and 1 V ranges unavailable).
- **None**: analog input filter off.

Note: the datasheet also lists 30 kHz corner frequencies, but the remote interface manual only documents corner frequencies up to 10 kHz, so this driver offers up to 10 kHz.

## Digital high pass filter and reference phase

- **High pass digital filter** (Filter1): removes the DC component before the PSD and enables the "Lock-In DC" measurement. Recommended ON.
- **Reference phase shift**: "Auto" lets the instrument set the phase so that the present, settled signal appears at θ = 0°; "As is" keeps the phase that was set on the instrument before the run started (the driver reads it back before the module preset and restores it afterwards); a numeric value (-360° to +360°) sets it explicitly. "Auto" is executed once during configuration — the reference must already be active and the signal settled at that moment for a correct result.

## Sweep modes

- **Sensitivity in V**: sweep the input range (accepts 10, 1, 0.1, 0.01 or the corresponding labels).
- **Time constant in s**: sweep the IIR output filter time constant.
