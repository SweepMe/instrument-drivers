# Logger HighFinesse WS-6

This driver reads wavelength, frequency, and optical unit temperature from a HighFinesse WS-6 wavelength meter.

---

### Requirements:

- The HighFinesse wavelength meter software must be installed and running. The driver talks to the running
  server application, it does not access the device directly.
- The driver loads `wlmData.dll`, which the HighFinesse installer places into the Windows `System32` folder
  (and, on 64-bit Windows, the 32-bit version into `SysWOW64`).
- The bitness of SweepMe! and of the loaded DLL must match, and client and server DLL must have the same
  version stamp apart from the 32/64-bit indicator, e.g. `[7.32.2.23]` works together with `[7.64.2.23]`,
  but not with `[7.32.2.22]`.
- The instrument is not accessed through a communication port, so no port has to be selected.

**Finding the right DLL:** the bitness is the second field of the DLL version stamp, which is shown in the
Details tab of the file properties in the Windows Explorer: `7.64.…` is 64-bit, `7.32.…` is 32-bit. Do not
rely on the folder names of the HighFinesse installation — a folder can contain DLLs of both bitnesses.
Loading a DLL of the wrong bitness fails with Windows error 193, "%1 is not a valid Win32 application".

**Configuring the DLL path:** is described in the wiki https://wiki.sweep-me.net/wiki/Configuration_File

---

### Usage:

- Start the HighFinesse software before the run. The driver checks that a server application is running and
  raises an error otherwise.
- The measurement mode of the server application is started during initialization and stopped at the end of
  the run.
- If the wavelength meter cannot calculate a value, for example because there is no signal or the signal is
  out of range, the driver returns `nan` and prints the reason to the Debug widget (F2). `nan` values are not
  drawn in the plot, so a missing value does not pull the curve down to zero.

---

### Parameters:

The driver has no GUI parameters. The only setting, the path to `wlmData.dll`, belongs to the computer rather
than to a measurement and is therefore taken from a config file.

By default the driver loads `wlmData.dll` by its file name, so Windows resolves it from the system folders.
This is the recommended setup and needs no config file.

To use a specific DLL, get the config file that is shipped with this driver into the `CustomFiles` folder of
your public SweepMe! folder: Tools -> Modules & Devices -> right-click on the version number of this driver ->
copy configuration file to public folder. Then edit `Logger-HighFinesse_WS-6.ini` there and set:

```ini
[DLL]
path = C:\Program Files\HighFinesse\Wavelength Meter WS6 1234\Projects\64\wlmData.dll
```

The driver only reads the file from `CustomFiles`. The copy inside the driver folder is the template and has
no effect, so it is not overwritten when the driver is updated.

---

### Note on the DLL declarations:

The driver calls `wlmData.dll` directly through `ctypes` instead of shipping the HighFinesse Python header
files `wlmData.py` and `wlmConst.py`. The argument and return types are therefore declared in the driver
itself, in `define_dll_signatures()`. This is not optional: `ctypes` assumes a C `int` return value for every
function, so without an explicit `restype` of `c_double` the wavelength, frequency, and temperature functions
would return meaningless numbers. The constants of `wlmConst.py` that the driver needs are listed at the top
of `main.py` with a reference to the manual chapter they come from.

---

### Measurement Output:

- **Wavelength**: Vacuum wavelength of the last measurement shot in nm.
- **Frequency**: Vacuum frequency of the last measurement shot in THz.
- **Temperature**: Temperature inside the optical unit in °C.

---

### Known limitations:

- Only the first signal is read. Wavelength meters with a multi-channel switch or the double pulse option
  would need the `GetWavelengthNum` and `GetFrequencyNum` functions instead.
- Linewidth, pressure, and interferometer pattern data are not exposed.
