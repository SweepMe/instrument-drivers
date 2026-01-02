# Lock-In driver for CM-10 module of LakeShore M81:
- Log current using the VM-10 module of the LakeShore M81 Synchronous Source Measurement System.
- Three physical measurement channels (M1, M2 and M3) are available at the M81. Connect your CM-10 module to one of them.
- Select the corresponding channel number in SweepMe!

## CM-10 Lock-In Mode

In lock-in mode, the CM-10 performs **phase-sensitive AC current detection** at a defined reference frequency.  
Instead of returning a single amplitude value, the module outputs **two components** of the response vector
and **four additional parameters**:

- **X** - the in-phase current (aligned with the reference)
- **Y** - the quadrature current (90 degree out of phase)

- **R** - the magnitude of the signal
- **Phase** - the phase angle in degrees
- **Frequency** - the lock-in frequency
- **Lock-in DC** - the detected DC component of the signal (only available when 'High pass digital filter' is ON.)

### Reference frequency for Lock-In Mode
- The CM-10 lock-in mode only works when a **source module of the M81 is generating an AC output**
or an external reference signal is provided.
- The lock-in frequency = the reference's AC output frequency.
- You do not set the lock-in frequency on the CM-10.
- If no AC source is active, Lock-In measurements at the CM-10 will return zero or noise.