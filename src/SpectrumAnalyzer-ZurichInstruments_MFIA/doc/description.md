# Zurich Instruments MFIA FFT

Driver for the spectrum of the demodulator samples of a Zurich Instruments MFIA or MFLI, as shown in the "Spectrum"
tab of LabOne (zoom FFT). At each measurement point, the driver records the demodulator samples with the Data
Acquisition module of the LabOne API and returns the spectrum around the demodulation frequency.

The instrument is not addressed via a serial or GPIB port. The driver uses the LabOne API and lists the device IDs
(e.g. `dev1234`) that the LabOne Data Server can reach. LabOne must be installed and its Data Server must be running.
The driver runs with SweepMe! 1.6.1 or newer (Python 3.14, 64 bit).

## Parameters

| Field | Description |
| --- | --- |
| Center frequency in Hz | Frequency of the oscillator that the selected demodulator uses as reference. `As is` keeps the frequency set at the instrument, e.g. the test frequency of an impedance measurement. |
| Frequency span in Hz | Span of the spectrum. It equals the sample rate of the demodulator (`demods/n/rate`); the instrument rounds it to a rate it supports. |
| Demodulator | Demodulator whose samples are analyzed. The MFIA uses demodulator 1 for the impedance measurement. |
| FFT length | Number of points of the spectrum. The resolution is span / FFT length. |
| Window | Window function of the FFT (`fft/window`). |
| Averages | Number of spectra averaged per measurement point. |

The span and resolution that the instrument actually uses are written to the debug log (F2) when the run starts.

## Returned values

| Variable | Unit | Description |
| --- | --- | --- |
| Frequency | Hz | absolute frequency of each point, demodulation frequency plus the offset of the FFT bin |
| Amplitude | V | magnitude of the FFT of the complex demodulator output X + iY |

The amplitude is in the unit of the demodulator input: for a demodulator on the current input, the values are in A,
although the unit is labelled V.

## Notes

* The span is set through the demodulator sample rate. An LCRmeter driver on the same instrument sets the rate of
  demodulator 1 as well, so use the two drivers in different branches of the sequencer or let the FFT driver run last.
* The time per measurement point is about Averages x FFT length / span, e.g. 1 s for 1000 Hz span and FFT length
  1024 without averaging.

## Further reading

* MFIA user manual, Spectrum Analyzer tab:
  <https://docs.zhinst.com/mfia_user_manual/functional_description/spectrum_analyser.html>
* LabOne API, Data Acquisition module: <https://docs.zhinst.com/labone_api_user_manual/modules/daq/index.html>
