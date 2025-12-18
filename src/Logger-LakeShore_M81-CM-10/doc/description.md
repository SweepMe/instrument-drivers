# CM-10 module of LakeShore M81:
- Log current using the VM-10 module of the LakeShore M81 Synchronous Source Measurement System.
- Three physical measurement channels (M1, M2 and M3) are available at the M81. Connect your CM-10 module to one of them.
- Select the corresponding channel number in SweepMe!

## CM-10 Lock-In Mode

In lock-in mode, the CM-10 performs **phase-sensitive AC current detection** at a defined reference frequency.  
Instead of returning a single amplitude value, the module outputs **two components**:

- **X** - the in-phase current (aligned with the reference)
- **Y** - the quadrature current (90 degree out of phase)

Together, these form the full AC response vector.  
Amplitude and phase can be derived as:

- R = sqrt(X^2 + Y^2)
- phi = arctan2(Y, X)

Consequently, the measurement result is a tuple (X, Y). SweepMe will output two plottable variables X and Y.

### Reference frequency for Lock-In Mode
- The CM-10 lock-in mode only works when a **source module of the M81 is generating an AC output**.
- The lock-in frequency = the source's AC output frequency.
- You do not set the lock-in frequency on the CM-10.
- If no AC source is active, Lock-In measurements at the CM-10 will return zero or noise.