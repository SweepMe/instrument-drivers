# Thorlabs PAX1000

Driver for the Thorlabs PAX1000 compact polarimeter (PAX1000VIS, PAX1000IR1, PAX1000IR2).

The PAX1000 measures the state of polarization with a rotating quarter waveplate: the waveplate
modulates the incoming polarization, a fixed linear polarizer turns that into an amplitude modulation,
and an FFT of the photodiode current yields the polarization parameters. One measurement always covers
a whole number of waveplate half turns.

## Requirements

* A VISA runtime, so that the polarimeter is available as a USBTMC instrument. The polarimeter must
  show up as "USB Test and Measurement Device" in the Windows device manager.
* The Thorlabs PAX1000 software package is **not** required. This driver talks SCPI directly and does
  not use the TLPAX instrument driver DLL, so it works with 32-bit and 64-bit SweepMe! alike.
* The supplied DS15 power supply is needed for basic scan rates above 100 1/s. On USB power alone the
  waveplate speed is limited, and the driver will silently use the reduced maximum.

## Parameters

| Parameter | Meaning |
| --- | --- |
| Wavelength in nm | Wavelength used by the instrument to calculate the measurement data. It is checked against the wavelength range of the connected model and an out-of-range value raises an error. |
| Measurement mode | Number of waveplate revolutions per measurement and number of FFT points. More revolutions and more points increase accuracy and reduce speed. |
| Basic scan rate in 1/s | Waveplate half turns per second. "Maximum" and "Minimum" use the limits the instrument reports for the selected mode and the connected power supply. |
| Power range | "Auto" keeps auto ranging active, "Auto once" ranges a single time and then holds the range, "Manual" sets a fixed range. |
| Power range in dBm | Highest expected input power. Only shown for a manual power range. |
| Wait for new scan | Poll until the instrument has finished a scan that was not reported before. Switch it off to always take the most recent scan, which is faster but can repeat a value. |
| Averages | Number of scans per measurement point. |
| Keep motor running between branches | Leave the waveplate spinning when a sequencer branch ends, which avoids the spin-up time when the branch is entered again. |
| Power unit | Unit of all reported optical powers. |
| Non-normalized Stokes vector | Additionally report S0 to S3. |
| Scan diagnostics | Additionally report revolution time, misalignment and the waveplate counter. |

## Returned variables

Always: Azimuth, Ellipticity, DOP, DOLP, DOCP, Power, Polarized power, Unpolarized power, s1, s2, s3.

Optional: S0, S1, S2, S3 and the three diagnostic values.

The instrument itself reports azimuth, ellipticity, degree of polarization and total power. Everything
else is derived, in the same way the Thorlabs software does it:

* `s1 = cos(2η)·cos(2θ)`, `s2 = cos(2η)·sin(2θ)`, `s3 = sin(2η)` with azimuth θ and ellipticity η
* `DOLP = DOP·√(s1² + s2²)` and `DOCP = DOP·|s3|`
* `P_polarized = P·DOP` and `P_unpolarized = P·(1 − DOP)`
* `S0 = P` and `Si = P·DOP·si`

Note that s1, s2 and s3 form a **unit** vector; they describe the direction of the state of
polarization on the Poincaré sphere only. The degree of polarization is a separate value, which is why
DOLP, DOCP and the non-normalized Stokes parameters carry DOP as an extra factor.

With averaging switched on, the mean is taken over the Stokes vector and not over the angles, because
averaging azimuth values across the wrap-around would be wrong. Azimuth and ellipticity are calculated
back from the averaged vector.

## Alignment

The accuracy depends strongly on the beam hitting the waveplate centred and perpendicular. A tilted
beam adds odd harmonics that the FFT model does not expect. Use the alignment aid of the Thorlabs
software once when setting up, and enable "Scan diagnostics" here to keep an eye on the misalignment
value during a measurement.

Further points from the manual worth knowing: the specified accuracy applies after a warm-up time of
15 minutes, and the polarization specifications hold between −40 dBm and +3 dBm even though the
dynamic range reaches from −60 dBm to +10 dBm.

## Known issues

The response of the `SENS:DATA:LAT?` query is not part of the public Thorlabs documentation. The
number of fields and the positions of azimuth, ellipticity and degree of polarization are established,
but the positions of optical power, revolution time and misalignment within the record were derived
from the Thorlabs instrument driver rather than measured. Run `examples/probe_scan_record.py` once
against your instrument to confirm them; if a value does not behave as labelled, adjust the `IDX_`
constants at the top of `main.py`.
