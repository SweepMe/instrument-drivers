# Writing SweepMe! instrument drivers

This guide collects everything needed to write, review and contribute a SweepMe! instrument driver. It is written
for people and for AI agents alike: every rule has one home section, with the reason where it is not obvious, and
other sections refer to it; the examples are complete enough to copy. It covers SweepMe! 1.6.1.9 and pysweepme
1.6.1.5 (November 2026); where a rule depends on a version, the version is named.

How to read it:

- New to drivers: read sections 1 to 4, then 6, and come back to the rest when you need it.
- Converting or reviewing a driver: sections 7 (the Driver API) and 11 (checklists) are the reference.
- An AI agent writing a driver: the whole file is the specification; section 11 is what to verify before handing
  over.

Contents:

1. [The smallest driver, and what a driver is](#1-the-smallest-driver-and-what-a-driver-is)
2. [Files and folders](#2-files-and-folders)
3. [The `Device` class and `__init__`](#3-the-device-class-and-__init__)
4. [GUI parameters](#4-gui-parameters)
5. [The sequencer lifecycle](#5-the-sequencer-lifecycle)
6. [Talking to the instrument: ports](#6-talking-to-the-instrument-ports)
7. [Communication commands and the Driver API (`@command`)](#7-communication-commands-and-the-driver-api-command)
8. [Messages, errors, folders and configuration](#8-messages-errors-folders-and-configuration)
9. [Working from manuals; instrument behaviour that bites](#9-working-from-manuals-instrument-behaviour-that-bites)
10. [Code style, layout and conventions](#10-code-style-layout-and-conventions)
11. [Checklists](#11-checklists)
12. [Third-party libraries, `config.ini` and Python versions](#12-third-party-libraries-configini-and-python-versions)
13. [Testing and debugging](#13-testing-and-debugging)
14. [Contributing](#14-contributing)
15. [A complete example driver](#15-a-complete-example-driver)

---

## 1. The smallest driver, and what a driver is

A SweepMe! driver is a Python file, `main.py`, that defines a class `Device` inheriting from `EmptyDevice` of the
`pysweepme` package. SweepMe!'s sequencer calls a fixed set of methods on it, the *semantic functions* (`connect`,
`configure`, `apply`, `measure`, `call`, ...), in a defined order; the driver fills them with the commands of its
instrument. Everything is optional: `EmptyDevice` provides a default for every one of them, so even
`class Device(EmptyDevice): pass` loads. The smallest driver that runs in the sequencer has four lines of code:

```python
from pysweepme.EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):
    def call(self):
        return []
```

It measures nothing yet. A driver that returns one value needs the names of its values and a `call()` that returns
as many:

```python
from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):
    def __init__(self):
        super().__init__()
        self.shortname = "My meter"            # shown in the sequencer
        self.variables = ["Voltage"]           # the values call() returns
        self.units = ["V"]
        self.plottype = [True]
        self.savetype = [True]
        self.port_manager = True               # SweepMe! opens the port for you
        self.port_types = ["COM", "GPIB", "USB"]

    def call(self):
        return [float(self.port.query("MEAS:VOLT?"))]
```

Everything else in this guide makes a driver more complete: a GUI, a proper setup and teardown, declared commands
that SweepMe! can check and that AI agents can read. None of it is required to contribute a driver. Drivers written
today are more verbose than this because they are meant to be written and tested together with AI agents, for which
SweepMe!'s Instrument Control tool (SweepMe! Pro, since 1.6.1.9) is the recommended workbench. A driver with only
the semantic functions it needs is still a valid driver, and still welcome in this repository.

Where drivers live:

- SweepMe! ships drivers through its version manager (*Tools -> Version Manager*). Right-click a version and
  choose *Create custom version* to get an editable copy in the public SweepMe! folder (`CustomDevices`), which the
  version manager offers as origin "custom".
- To work with this repository directly: clone it, set the Windows environment variable `SWEEPME_DRIVERS_REPO` to
  its `src` folder, restart SweepMe!, and the version manager lists the repository drivers with the origin "repo".
- Outside SweepMe!, `pysweepme.get_driver("<DriverFolder>", "<path to the folder containing it>", "<port>")`
  loads a driver into any Python script (section 13).

Module categories: a driver belongs to one SweepMe! module (SMU, Logger, Switch, Temperature, LCRmeter, LockIn,
Spectrometer, Signal, Scope, NetworkAnalyzer, SpectrumAnalyzer, Monochromator, Robot, WaferProber, Camera, ...).
The module decides which GUI fields exist and which semantic functions are called, so choose it first (section 5.3).

---

## 2. Files and folders

A driver is a folder named `<Module>-<Manufacturer>_<Model>`, e.g. `SMU-Keithley_2400`, `LCRmeter-HP_4284A`,
`Logger-Keysight_344xxA`. The module name must be one of SweepMe!'s module types. A folder covering a model family
with one command set uses an `x` wildcard (`SMU-Keithley_26xx`) and gates model-only features on the `*IDN?` answer.

| File | Purpose |
|---|---|
| `main.py` | The driver: license header, `# SweepMe! driver / # * Module: ... / # * Instrument: ...` comment, then the code. pysweepme loads `main_<pyver>_<bits>.py` (e.g. `main_314_64.py`) instead when such a file exists for the running Python. |
| `license.txt` | The license, MIT whenever possible (section 14). |
| `doc/description.md` | User documentation shown behind the help icon in SweepMe!: supported models, wiring, quirks, limits, the communication commands. SweepMe! reads `doc/description.html`, then `doc/description.md`, then the legacy `description` class attribute. New and touched drivers use `doc/description.md` and no `description` attribute. |
| `config.ini` | SweepMe! metadata only: `[config] architecture = "3.14-64"` restricts the Python versions the driver runs on (section 12). No file means all. |
| `libraries/requirements.txt` + `libraries/libs_<pyver>_<bits>/` | Third-party packages not shipped with SweepMe!, built per Python version (section 12). Avoid in new drivers. |
| `<DriverFolder>.ini` | Template of a machine-specific configuration file (DLL paths, ...) the user copies to `CustomFiles` (section 8.4). |
| `examples/`, `tests/` | Optional pysweepme usage examples and tests. |
| `info.ini`, `run.ini` | Written by the upload server and by SweepMe!; gitignored. Never create, edit or commit them. `info.ini` carries a hash of the `.py` files, so a modified installed version is refused ("has been modified and will not be loaded" in the debug log): edit a custom version instead. |
| `<DriverFolder>.ino` | Arduino drivers ship their sketch under the folder's name; the version manager offers to open it in the Arduino IDE. |

A driver that depends on software that may not be redistributed (a closed vendor SDK, commands under NDA) cannot be
published here; contact contact@sweep-me.net for the alternatives.

A base class shared by several drivers (e.g. one for a family of data loggers) is copied into every driver folder,
because a driver folder must be complete on its own. A change to it is made in every copy, checked against every
driver that uses it, and the copies are compared afterwards (`md5sum src/*/<BaseClass>.py` shows one hash).

---

## 3. The `Device` class and `__init__`

```python
from __future__ import annotations

from typing import Any

from pysweepme.EmptyDeviceClass import EmptyDevice

# option -> instrument command; the GUI shows the keys, the code looks up the command
CURRENT_RANGES: dict[str, str] = {"Auto": "AUTO", "200 mA": "0.2", "20 mA": "0.02"}


class Device(EmptyDevice):
    """Driver for the <Manufacturer> <Model>."""

    def __init__(self) -> None:
        """Define the returned variables and the port."""
        super().__init__()

        self.shortname = "2400"                      # shown in the sequencer

        self.variables = ["Voltage", "Current"]      # what call() returns, in this order
        self.units = ["V", "A"]
        self.plottype = [True, True]                 # plotted in SweepMe!
        self.savetype = [True, True]                 # saved to the data file

        self.port_manager = True
        self.port_types = ["COM", "GPIB", "USB", "TCPIP"]
        self.port_properties = {"timeout": 5, "baudrate": 9600, "EOL": "\n"}

        # every attribute the driver uses later, with a type and a default
        self.gui_parameters: dict[str, Any] = {}
        self.sweep_mode: str = "None"
        self.voltage: float = float("nan")
        self.current: float = float("nan")
```

Rules:

- **Keep `__init__` light.** Instances are created and destroyed constantly: for every run, every GUI refresh, and
  just to read the metadata. Never load a DLL, open a connection or talk to hardware here; that belongs into
  `connect()` and `initialize()`.
- `super().__init__()` comes first.
- `variables`, `units`, `plottype` and `savetype` are lists of the same length, and `call()` returns exactly that
  many values. Variable names are Title Case, without underscores or commas (`"Voltage"`, `"Set Temperature"`);
  units are symbols (`"V"`, `"A"`, `"°C"`, `""`). They may be set again in `apply_gui_parameters()` when they
  depend on the user's selection (section 4).
- Option dictionaries map user-friendly keys to instrument spellings. They are constants at module level (section
  10.1). The GUI shows `list(CURRENT_RANGES)`; the code never builds a command from a GUI label.
- Initialise every attribute the driver uses with a type annotation and a default, so that teardown methods can run
  even when setup failed (section 5.2).
- `self.actions = ["go_home"]` (a class or instance attribute) releases methods to SweepMe!'s ActionManager, so that
  control-widget buttons, shortcuts, the Condition module and the remote interface can call them outside the
  lifecycle (section 5.6). This list is unrelated to the "run" commands of section 7.

The deprecated camelCase helpers (`write_Log`, `message_Box`, `message_Info`, `stop_Measurement`,
`set_GUIparameter`, `get_GUIparameter`) still exist as thin wrappers in pysweepme, but new code uses the lowercase
API; `find_Ports` and `get_Folder` were removed with SweepMe! 1.5.8 (`find_ports`, `get_folder`). When the wiki
and the pysweepme source disagree, the source (`EmptyDeviceClass.py`) wins.

---

## 4. GUI parameters

Two methods connect the driver to the module's GUI (SweepMe! 1.5.6.25 and newer; the legacy pair is
`set_GUIparameter()` / `get_GUIparameter()`):

```python
def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
    """Return the GUI fields with their defaults; may depend on the current selections."""
    mode = parameters.get("Mode", "Voltage DC")
    new_parameters: dict[str, Any] = {
        "SweepMode": ["None", "Voltage in V"],
        "Mode": list(self.modes.keys()),         # list -> dropdown, first entry is the default
        "Average": 1,                            # int -> spin box
        "Use trigger": False,                    # bool -> check box
    }
    if mode == "Voltage DC":
        new_parameters["Range"] = ["Auto", "10 V", "1 V"]   # shown only when relevant
    return new_parameters

def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
    """Store the user's selections. Called repeatedly, also with incomplete dicts."""
    self.gui_parameters = parameters
    self.port_string = parameters.get("Port", "")
    self.sweep_mode = parameters.get("SweepMode", "None")
    self.mode = parameters.get("Mode", "Voltage DC")
```

### 4.1 How the fields are built

The type of the default value selects the widget:

| Default value | Widget |
|---|---|
| `list` | dropdown, first element selected |
| `bool` | check box |
| `int` | spin box |
| `float` | double spin box |
| `str` | text field |
| `None` | bold separator label; `"": None` is an empty line |
| `pathlib.Path` | file or folder picker (a picked file cannot be cleared again; for an optional file pair a dropdown `None` / `From file` with the path field, shown only for `From file`) |
| a bound method | a push button that calls the method |

Reserved keys that the modules define and the driver only reads: `Port`, `Device`, `Label`, `Channel`,
`SweepMode`, `SweepValue`, `Calibration`, `Description`, `Comment`, `Parameters`, `Data`. Never define your own key
with one of these names, and never start a key with "Device". `Channel` given as a list enables multichannel
instruments sharing one port.

Logger, Switch and Robot build their whole parameter area from the driver's keys. The other modules show their
predefined fields and put every key they do not know into a "Parameters" box (Spectrometer since 1.5.8.5, Camera
since 1.5.6.18). Temperature has no such box: reuse an existing key there (a Temperature driver offers its modes
under `Sensor`).

### 4.2 SweepMode and labels

- A driver that sets a value lists the settable quantities under `"SweepMode"`, e.g.
  `["None", "Voltage in V", "Current in A"]`. The module's SweepValue field picks the source of the value; when it
  changes, SweepMe! sets `self.value` and calls `apply()`.
- A parameter carrying a physical quantity is labelled `<Quantity> in <unit>` ("Compliance in V", "Settling time
  in ms"), without parentheses. Keep labels short. `#` is the unit of a dimensionless index (a channel number).
- Signal generators pair a type dropdown with its value field (`PeriodFrequency` + `PeriodFrequencyValue`).
- Camera drivers return a file path (`variables = ["Image Path"]`, unit `""`), not pixels; the module recognises the
  image by the value being an existing file, not by the name.

### 4.3 Rules that prevent the classic bugs

- **Always `parameters.get(key, default)`, never `parameters[key]`.** Both methods are called repeatedly with
  incomplete dicts: `update_gui_parameters({})` must return only defaults, `apply_gui_parameters` may receive the
  previous driver's values first, and `pysweepme.get_driver()` without a port string passes no `Port`.
- **Never convert a GUI parameter in place** (`self.average = int(self.average)`). Several pysweepme entry points
  re-apply the parameter dict without calling `configure()` afterwards, which reverts a converted number to its
  original string; the `TypeError` then appears in `measure()` or `apply()`, long after setup succeeded. Keep the raw
  dict in `self.gui_parameters`, and write converted values to separate attributes from `configure()`, which also
  runs again when a `{...}` value changes mid-run (section 5.4); `initialize()` does not.
- **Stay compatible with saved sequences.** A saved `.seq`/`.set` file stores the GUI keys that existed when it was
  saved, so every new key needs a default. Match option strings through a lookup dict or `startswith()`, not by exact
  equality with the full label, so a label can be reworded later.
- **If the returned variables depend on the GUI**, set `self.variables`, `units`, `plottype` and `savetype` in
  `apply_gui_parameters()`: SweepMe! reads them right after a GUI change and before `connect()`; `configure()` is
  too late.
- **Validate in `configure()`, right after converting**, with a message for the user
  (`raise ValueError("Average must be at least 1, not 0.")`), not in the GUI methods and not in `initialize()`, so a
  value changed mid-run through `{...}` is checked too.
- **Buttons** (a bound method as default) are pressed on the existing device instance *without* a fresh
  `apply_gui_parameters()`, or on a temporary instance when none exists. The handler cannot rely on current GUI values
  such as the selected port; make it self-sufficient.
- **Dropdown to enum:** keep an explicit label-to-member dict (`self.sensors = {"Main": Sensor.MAIN, ...}`) that feeds
  the dropdown and resolves the selection. Do not derive members with `getattr(Enum, label.upper())`.
- **Optional modes:** one boolean attribute named after the mode (`self.pulse_mode = parameters.get("Pulse", False)`),
  and everything that is only meaningful in that mode under `if self.pulse_mode:`.

### 4.4 Calibration and correction files

Spectrometer, NetworkAnalyzer and similar modules offer a `Calibration` field whose choices come from the public
`CalibrationFiles` folder (`self.get_folder("CALIBRATIONS")`). Fill it in one of three ways: a `Calibration` list
returned with the GUI parameters; `get_calibrationfile_properties(port="")` returning
`(extensions_list, required_substrings_list)` so the module scans the folder (subfolders allowed); or
`find_calibrations()` returning a list of strings (called together with `connect`/`disconnect`). The selection arrives
under the `Calibration` key as a path relative to `CalibrationFiles`; prepend the folder yourself. For correction
files of your own, accept a free path rather than scanning a folder, ship an example file in `examples/`, and document
the required keys in `doc/description.md`.

---

## 5. The sequencer lifecycle

### 5.1 Order of calls

```
connect -> initialize                                   once per run
configure -> poweron -> signin                          on entering a branch of the sequencer
  per measurement point:
    start -> apply -> reach -> adapt -> adapt_ready -> trigger_ready
    -> measure -> request_result -> read_result -> process_data -> call -> finish
signout -> poweroff -> unconfigure -> deinitialize -> disconnect
```

- Each phase runs for all modules of a branch before the next phase starts. Every `measure()` of the branch runs
  before any `request_result()`, which lets several instruments measure at the same time.
- `signin` repeats for every new value of a module above (once per parameter variation); right before it,
  `reconfigure` runs if a `{...}` GUI value changed (section 5.4).
- `poweroff` and `unconfigure` run leaf to root, `deinitialize` and `disconnect` top to bottom in sequencer order.
  `signout` also runs when the user stops a run, lower modules first.
- `apply()` and `reach()` run only when the sweep value changed; the new value is in `self.value`. A float NaN is
  not applied. After `unconfigure` or at the start of a run, the next value is applied again even if unchanged.
- `process()` is meant for modules; a driver uses `process_data()`.

### 5.2 What belongs where

| Method | Runs | Put here |
|---|---|---|
| `connect()` / `disconnect()` | once per run, for all enabled modules, before anything else | open and close a connection the port manager does not handle (DLL, SDK, socket library). With the port manager the port is already open and cleared when `connect()` runs, and SweepMe! closes it after `disconnect()`, so `self.port` is still usable there and the driver never closes it. `connect()` closes what it opened itself before re-raising on failure. |
| `initialize()` / `deinitialize()` | once per run | identify the instrument (`*IDN?`), check the model, `self.port.clear()`, one-time instrument setup |
| `configure()` / `unconfigure()` | per use of the module in the sequencer (entering a branch), and again from `reconfigure()` | convert GUI parameters into typed attributes, validate them with user-readable errors, write the configuration to the instrument (mode, range, NPLC, compliance), restore display or local mode at the end |
| `reconfigure(parameters, keys)` | when a `{...}` GUI value changed mid-run | re-apply the changed values (section 5.4) |
| `poweron()` / `poweroff()` | after `configure`, before `unconfigure` | switch the output on and off (SMU, sources) |
| `signin()` / `signout()` | per parameter variation of modules above | rarely needed; wafer-prober contact, lock-in auto-phase |
| `start()` | per point | rarely needed; arming that must happen before any module applies a value |
| `apply()` | per point, when `self.value` changed | send the new sweep value: `self.set_voltage(float(self.value))` |
| `reach()` | after `apply` | wait until the setpoint is reached (temperature controllers, stages), checking `self.is_run_stopped()` |
| `adapt()` / `adapt_ready()` | per point | adapt to the new value (autorange, auto-phase) and wait for it |
| `trigger_ready()` | per point | arm the trigger, when the instrument needs it in a phase of its own |
| `measure()` | per point | trigger the measurement **and read its result** (`self.voltage = float(self.port.query("READ?"))`) |
| `request_result()` / `read_result()` | per point | split a slow acquisition: request in one phase, read in the next, when the instrument needs it; `request_result()` may block until a buffered sensor delivered |
| `process_data()` | per point | compute derived values |
| `call()` | per point | return the values of `self.variables`, in order; the only method a driver that returns values needs (the default returns NaN per variable) |
| `finish()` | per point | rarely needed; cleanup after a point |

Teardown runs even when setup failed: SweepMe! marks the driver connected before it calls `connect()`, so
`disconnect()`, `deinitialize()` and `unconfigure()` must tolerate missing attributes. Up to SweepMe! 1.6.1.7,
`poweroff`, `unconfigure` and `deinitialize` ran at the end of a run for every connected module even if their
counterpart never ran; from 1.6.1.8 they run only after it.

Rules:

- **Trigger and read in the same phase.** When trigger and read sit in different phases, several instances of the
  same driver on one port interleave and their replies collide. Split only when the instrument needs it.
- **Per-point methods run at every point of the branch.** A command that resets, re-arms or rebuilds instrument state
  (a trigger restart, a waveform rebuild) belongs in `configure()`, not in `start()` or `trigger_ready()`. Done per
  point it produces scrambled data rather than an error.
- **Long loops check `self.is_run_stopped()`** so the user can stop the run. (`is_run_aborted()` does not exist.)
- **Values arrive as strings** from a SweepBox, split at commas and line breaks only; `1;0;0` reaches `self.value` as
  the string `"1;0;0"`. Cast (`float(self.value)`) or parse in the driver.
- **`call()` returns** one value per entry of `self.variables`, as a list or tuple (a single variable may be
  returned directly; a driver without variables returns `None` or `[]`). A mismatch stops the run with "Mismatch
  between variables and values". Values are `int`, `float`, `str`, `bool`, `list` or `numpy.ndarray`; 0D values go
  into the main data file, 1D lists and arrays into a separate 1D data file per sequencer iteration; strings are
  stored unchanged. For sampled data return lists (`[time_list, data_list]`). Each measured value becomes a
  parameter `{<Label>_<Variable>_<Unit>}` for the fields of other modules.
- `initialize()` checks the instrument once per run. `configure()` converts, validates and writes the GUI values each
  time the module is used and after every `reconfigure()`, because a `{...}` value changed mid-run reaches the driver
  only there.

### 5.3 The module decides the lifecycle

Choose the module first, because it decides which methods are called and which GUI fields exist:

- **Logger:** measures only; no `SweepMode`. Measure-only instruments (power meters, polarimeters) are Loggers.
- **Switch:** sets one value through `apply()`. A source of a single quantity without measurement (a current source,
  a laser-diode driver with fixed compliance) is a Switch with a SweepMode such as `Current in A`.
- **Temperature:** sets a setpoint and needs `reach()`, which asks the instrument whether the setpoint is reached.
- **SMU:** only if the instrument sources V or I with a settable compliance **and** measures V and I; `poweron` and
  `poweroff` switch the output.
- A built-in bias used as a fixed condition (an electrometer's voltage source) stays in the Logger behind an optional
  "Use voltage source" check box.
- Whether the port manager is used depends on the instrument, not on the module.

What each module expects from its driver (GUI keys the module provides, methods it calls by name, what `call()`
must return). Keys not listed here land in the module's "Parameters" box where the module has one.

| Module | GUI keys the module provides | Module-specific contract |
|---|---|---|
| SMU | `SweepMode` (at least `"Voltage in V"` and `"Current in A"`), `RouteOut`, `Compliance`, `Speed`, `Range`, `RangeVoltage`, `Average`, `4wire`, pulse keys (`CheckPulse`, `PulseCount`, `PulseOnTime`, ...), list-sweep keys (`ListSweepCheck`, `ListSweepType`, `ListSweepStart`, `ListSweepEnd`, ...) | `"Voltage"` and `"Current"` as the first two variables whenever post-processing (resistance, conductance, power) is selected, else the run stops; `poweron`/`poweroff` switch the output |
| Logger | `Channel` (if the driver returns it), free custom keys | measure only, no `SweepMode`; the "Retrieve" button runs one point from `connect` to `disconnect` |
| Switch | `SweepMode`, `Channel`, free custom keys | sets one value through `apply()`; return the applied value in `call()` so it is recorded; the "Apply" button calls `connect`, `initialize`, `configure`, `poweron`, `signin`, `start`, `apply`, `disconnect` |
| Temperature | `TemperatureUnit` (list, mandatory), `SweepMode` (list, required if the instrument sets a temperature; a mode containing "Temperature" uses the sweep value as setpoint), `Channel`, `Sensor`, `Rate`, `HeaterRange`, `OutputMax`, `OutputMin`, `MeasureT`, `ZeroPowerAfterSweep`, `IdleTemperature` | first variable `"Temperature"`; either an own `reach()` or a `measure_temperature()` returning a float in the selected unit, which the module polls against the setpoint; the idle temperature is set in `unconfigure()` |
| LCRmeter | `SweepMode`, `StepMode`, `ValueTypeBias`, `ValueBias`, `Frequency`, `ValueTypeRMS`, `ValueRMS`, `OperatingMode` (`"R-X"`, `"Cp-D"`, ...), `Integration`, `Average`, `Range`, `Trigger`, `TriggerDelay`, `ALC`, `ExternalBias`, list-sweep keys | first three variables `"R"`, `"X"`, `"Frequency"` whenever post-processing is selected (the module derives Z, phase, Cp, Rp, Cs, Rs, ...) |
| Spectrometer | `Calibration`, `SweepMode` (`["None", "Integration time in s"]`), `IntegrationTime`, `Filter`, `Average`, `Shutter`, `Trigger`, `TriggerDelay`, `TriggerTimeout`, `IntegrationTimeAutomatic`, `IntegrationTimeMax`, `SaturationMinimum`, `SaturationMaximum`, reference and post-processing keys | `call()` returns wavelengths first, the spectrum second (`"Wavelength"` in nm, `"Intensity"` or `"Flux"`); `get_wavelengths()` returns the wavelength array (a module hook, section 7.7); optional `get_reference_spectrum()`; ports from `find_ports()` |
| Signal | `SweepMode`, `Channel`, `Waveform`, `PeriodFrequency` + `PeriodFrequencyValue`, `AmplitudeHiLevel` + `AmplitudeHiLevelValue`, `OffsetLoLevel` + `OffsetLoLevelValue`, `DelayPhase` + `DelayPhaseValue`, `DutyCyclePulseWidth` + `DutyCyclePulseWidthValue`, `OperationMode`, `Impedance`, `Trigger`, `ArbitraryWaveformFile`, ... | type/value pairs: the type key holds a list such as `["Frequency in Hz", "Period in s"]` |
| LockIn | `Channel`, `SweepMode`, `Source`, `OscillatorFrequency`, `OscillatorAmplitude`, `Input`, `Coupling`, `Ground`, `Gain`, `Sensitivity`, `TimeConstant`, `WaitTimeConstants`, `Reserve`, `Slope`, filters, `Channel1`, `Channel2` | typical variables Magnitude, Phase, Frequency, X, Y |
| Scope | trigger keys (`TriggerSource`, `TriggerLevel`, ...), `Acquisition`, `Average`, `SamplingRate`, `TimeRange`, `TimeRangeValue`, `VoltageRange`, per channel `Channel<i>`, `Channel<i>_Name`, `Channel<i>_Range`, `Channel<i>_Offset`, `Channel<i>_Impedance`, `Channel<i>_Coupling`, `Channel<i>_Probe` | returns `"Time"` and one trace per selected channel, named by `Channel<i>_Name`; offer an "As is" option in every dropdown |
| NetworkAnalyzer | `Calibration`, `Terminals`, `Sparameters`, `Average`, `SourcePower`, `SourceAttenuation`, `IFBandwidth`, `Correction`, `Trigger`, `FrequencyStart`, `FrequencyEnd`, `FrequencyStepPointsType`, `FrequencyStepPoints`, post-processing keys | returns the full S-parameter scan per point |
| SpectrumAnalyzer | `Frequency label 1` / `Frequency value 1`, `Frequency label 2` / `Frequency value 2`, `Reference level in dBm`, `Resolution bandwidth`, `Video bandwidth`, `Trace mode`, ... (keys with spaces) | variables `"Frequency"` in Hz and `"Power"` in dBm |
| Monochromator | `Wavelength`, `EndPosition`, `Input`, `Output`, `Filter`, `Grating`, `Lamp`, `SlitInput`, `SlitOutput`, `MotorPosition` | `go_home()` for the "Go home" button; filter and grating dependence on the wavelength as `1 <- 500 nm -> 3 <- 1000 nm -> 2` |
| Robot | `GoHomeStart`, `GoHomeEnd`, free custom keys | class attribute `axes`; `self.sweepvalues` in `apply()`; `go_home()` (section 5.7) |
| WaferProber | (probe plan from the driver) | `get_probeplan()`, `get_wafer_geometry()`, `get_contact_state()` are module hooks; `load_wafer`, `unload_wafer`, `step_to_die`, `step_to_subsite`, `contact`, `separate`, `get_current_wafer/die/subsite`; `self.sweepvalues` with `Wafer`, `Die`, `Subsite`; go to separation height in `signout()` |
| Camera | `SweepMode`, `Trigger`, `Gain`, `GainAuto`, `ExposureTime`, `ExposureAuto`, `PixelFormat`, `FileFormat`, image size and offset keys, ... | `call()` returns the image file path first; `self.tempfolder` is the folder to save into; ports from `find_ports()` |

The module's test buttons reuse the lifecycle: Switch and SMU "Apply" runs `connect` to `apply` and `disconnect`,
"Stop" runs the shutdown functions, Logger "Retrieve" and Camera "Test" run one complete point, Temperature "Set T"
and "Get T" run up to `apply()` or one point. A driver whose setup only works inside a full run breaks these buttons.

### 5.4 `reconfigure`

GUI values can reference other modules with the parameter syntax: `{<Label>_<Variable>_<Unit>}` for a measured
value (spaces become underscores, the unit is omitted when empty), `{<Label>_SweepValue}`, `{<Label>_SweepIndex}`,
`{<Label>_is_active}`, plus system keys such as `{filename}` or `{run_index}`. Sweep values are available to the
modules below before they are configured; measured values only after the point finished. When such a value changes
mid-run, SweepMe! calls `reconfigure(parameters, keys)` right before `signin()`. The pysweepme default re-applies all
GUI parameters and calls `configure()`. An override may apply only the changed `keys` (no auto-phase retrigger, only
the source voltage), but every varied value must still reach the instrument. When a module becomes active, changed
values are handed to the driver before `configure()`, so no `reconfigure` happens then.

### 5.5 Threads

SweepMe! calls the lifecycle methods one after another on its measurement thread, not on the GUI thread, and offers
no thread primitives. A driver that runs its own thread (a vendor asyncio or BLE loop, a push sensor) owns it: hand
data to `call()` under a `threading.Lock`, buffer every sample in the callback (bounded) instead of keeping only the
newest, and never call `message_info` or `message_box` from that thread.

### 5.6 `actions`: methods callable outside the lifecycle

Methods named in `self.actions` (or the class attribute `actions`) are registered with the ActionManager. Buttons of
control widgets, shortcuts, the Condition module and the remote interface can call them without any lifecycle:
outside a run on an instance that never connected, or during a run on the live device from another thread. Such a
method must check its own preconditions. Do not confuse this list with the "run" commands of the Driver API
(section 7.7): `actions` releases functions to SweepMe!'s ActionManager, a run command is a kind of communication
command.

### 5.7 Robot module contract

- The class attribute `axes` (a dict per axis, optional default `"Value"`) builds the axis rows of the module.
- Before `apply()` the module sets `self.sweepvalues = {axis: value}` with parameter syntax resolved; empty, `None`
  or NaN means "keep that axis".
- `go_home()` serves the "Go home" button and the `GoHomeStart` / `GoHomeEnd` check boxes.
- After a collision or a failed move the robot pauses where it is: a motion-error flag makes `deinitialize()` and
  `unconfigure()` skip "Go home at end", and "Go home" refuses while alarms are pending.
- Reference: `src/Robot-Simulation_Driver/main.py`.

---

## 6. Talking to the instrument: ports

### 6.1 The port manager

Set `self.port_manager = True` and `self.port_types` in `__init__`. SweepMe! then lists the matching resources in
the module's Port field, opens the port before `connect()`, hands it over as `self.port` and closes it after
`disconnect()`:

- `self.port.write(cmd)` appends the terminator; `self.port.read()` returns the stripped text of one message;
  `self.port.query(cmd)` is write and read in one call (prefer it over separate pairs); `self.port.clear()` clears
  the port. Raw I/O on every port type since pysweepme 1.6.1.4 (SweepMe! 1.6.1.8): `self.port.read_raw()` reads one
  message as bytes including its terminator, `self.port.read_bytes(count)` exactly `count` bytes (an incomplete
  message raises with the bytes received so far), `self.port.write_raw(data)` sends bytes unchanged without a
  terminator. On COM, `self.port.read(digits)` reads a fixed number of characters. PXI resources and GPIB through a
  Prologix controller have no raw I/O and raise `NotImplementedError`.
- The raw pyserial, pyvisa or socket object sits at `self.port.port`. Calls through it bypass pysweepme: no EOL
  handling, no debug log, invisible to the Port Terminal trace. Use it only where no wrapper exists (`read_stb()`);
  binary blocks are read with `read_bytes()` (section 6.3).
- An empty Port field stops the run before `connect()` with a message naming the module; most simulation drivers
  run with an empty port.
- Port types: `"COM"`, `"GPIB"`, `"USBTMC"` (alias `"USB"`), `"TCPIP"` (VISA), `"SOCKET"` (raw socket), `"ASRL"`
  (VISA serial), `"PXI"`. Prologix GPIB-USB adapters are built in over their COM port
  (`GPIB::<addr>::Prologix@COMx`) and need no VISA.
- All instances on one resource get the same cached port object (section 6.4).

Without the port manager (DLL, SDK, a library with its own transport), implement `find_ports() -> list[str]` so the
Port field offers something, open the connection in `connect()` and close it in `disconnect()`, and **always set a
timeout**: vendor helper modules often default to `timeout=None`, many instruments never answer an unsupported
command, and a driver without timeout then blocks forever and cannot even be stopped.

### 6.2 Port properties

`self.port_properties = {...}` in `__init__`; settings from SweepMe!'s port dialog override them. Reference:
the `PortProperties` TypedDict in pysweepme `Ports.py`.

| Key | Port types | Meaning |
|---|---|---|
| `timeout` | all | seconds, default 2 (VISA converts to ms; ASRL truncates to whole seconds) |
| `delay` | all but USBTMC | seconds enforced between writes |
| `rstrip` | all | strip the answer, default True |
| `clear` | all | clear the port after opening, default True |
| `debug` | all | log every write and read |
| `EOL`, `EOLwrite`, `EOLread` | COM | terminator, default `"\n"`; per direction |
| `baudrate` (9600), `bytesize`, `parity`, `stopbits`, `xonxoff`, `rtscts`, `dsrdtr`, `rts`, `dtr` | COM (`baudrate`, `bytesize`, `stopbits`, `parity` also ASRL) | serial settings |
| `encoding` | COM, SOCKET | default `"latin-1"` |
| `raw_write`, `raw_read` | COM | bytes instead of text |
| `Exception` | COM | default True: an empty read without EOL raises; False returns `''` |
| `GPIB_EOLwrite`, `GPIB_EOLread` | GPIB | terminators |
| `TCPIP_EOLwrite`, `TCPIP_EOLread` | TCPIP | terminators |
| `SOCKET_EOLwrite`, `SOCKET_EOLread`, `fixed_port` | SOCKET | terminators (default: none) and a fixed TCP port |

- A key that belongs to another port type is silently ignored, and an invented key (`TCPIP_timeout`) only logs a
  debug line. `None` keeps the VISA default. USBTMC, ASRL and PXI terminations are set on `self.port.port` if needed.
- VISA ports (GPIB, USBTMC, TCPIP, ASRL) raise `pyvisa.errors.VisaIOError` on timeout regardless of `Exception`.

### 6.3 Reads, timeouts and retries

- pysweepme's COM `read()` reads byte by byte until the EOL or until a single-byte read times out, and raises only
  on an empty answer. An EOL mismatch (the instrument sends CR, the driver expects LF) therefore costs one full
  timeout on *every* read while still returning the data. Detect it by timing ten `*IDN?` queries at a 1 s timeout;
  fix it with `port_properties["EOLread"] = "\r"` and document the required instrument setting.
- Fixed-length frames: `self.port.read_bytes(count)` with the exact reply length (a Modbus write reply is 8 bytes,
  not 32), or the whole timeout is waited out at every point.
- **Never re-send a query after a timeout.** Instruments queue commands while they measure and answer every copy
  once idle, so spare answers glue onto the next read. Send once, retry only the read (checking
  `is_run_stopped()`), accumulate partial reads, and `self.port.clear()` in `initialize()`.
- Binary blocks (`#<ndigits><length><payload>`): read them with `self.port.read_bytes()`, which ignores the
  terminator by default, on every port type: `read_bytes(2)` for `#<ndigits>`, `read_bytes(ndigits)` for the length,
  `read_bytes(length)` for the payload, then the trailing terminator. Never `read()` or `read_raw()`, which stop at
  the first 0x0A or 0x0D inside the payload.

  ```python
  self.port.write("CURV?")
  header = self.port.read_bytes(2)                    # b"#4"
  length = int(self.port.read_bytes(int(header[1:2])))
  payload = self.port.read_bytes(length)
  self.port.read_bytes(1)                             # the terminator "\n"
  ```

### 6.4 Several instances on one port

Channels of one instrument run as several driver instances on one physical port, all holding the same port object.
Coordinate through `self.device_communication`:

- One dict shared by all instances of all drivers, cleared at the start of each run. It can be indexed, never
  reassigned (the setter raises). Namespace the keys by the port string (`self.port_string = parameters.get("Port")`).
- The first instance to connect or initialize does the one-time setup and records it; later instances skip it.
- Instruments with one active function or channel (a multimeter's mode): store the active function under the port
  key, and in `measure()` re-send the instance's own function and settings when another instance changed them.
- Without the port manager, the first instance creates the connection object and stores it; `disconnect()` closes it
  only if the key still exists, then deletes the key.

Values that must survive across runs within a SweepMe! session (instances are destroyed after each run):
`self.store_parameter(key, value)` / `self.restore_parameter(key)` (an unset key returns `None`).

### 6.5 SCPI patterns

- **Probe commands on the real instrument** before writing the driver, with a small pysweepme or pyvisa script.
  Manuals are often wrong about reply formats (quoting, binary blocks, units). Probe an optional command by trying it
  once with a timeout, not by querying a firmware version, which may be unsupported too.
- **Error queue:** parse the leading integer of the `SYST:ERR?` reply and read until it is 0, with a bounded number of
  reads. Never string-compare the reply (`+0,"No error"`, `0, No error`, entries with timestamps all occur).
- **Root colon:** optional for subsystem commands, forbidden on IEEE 488.2 common commands (`*IDN?`, never `:*IDN?`).
- **Enum replies** may come double-quoted or in another case than the manual shows; strip quotes and normalise before
  comparing.
- **Stale setpoints:** a setpoint sent while an output is in another mode may be accepted silently and applied the
  moment the mode switches. Re-send or zero setpoints when the driver changes the mode.
- **Chained queries** (`;`-separated) are answered in order in one reply and cost one round trip instead of several.

### 6.6 GPIB adapters

SweepMe! lists GPIB instruments through VISA, so the adapter must appear in NI-VISA (NI-488.2 for NI adapters, a
vendor VISA passport otherwise); Prologix GPIB-USB works without VISA over its COM port (Prologix Ethernet is not
supported). On Windows 10/11 the Keithley KUSB-488 and KUSB-488A have no driver; KUSB-488B, NI GPIB-USB-HS/HS+,
Keysight 82357B, Prologix or RS-232 work. Do not install NI-488.2 on top of the Keithley driver.

---

## 7. Communication commands and the Driver API (`@command`)

### 7.1 Why

The semantic functions of section 5 are the steps of a measurement. The instrument commands they need, `set_voltage`,
`get_identification`, `set_output`, live in small public methods of their own, the *communication commands*. Each
wraps exactly one command of the instrument: it sends it and reads the answer, if there is one, also as one
`query()`. The semantic functions call them instead of writing raw commands again:

```python
def configure(self) -> None:
    """Set up the source before the sweep."""
    self.set_source_mode(self.channel, "FVMI")
    self.set_compliance(self.channel, self.compliance)

def apply(self) -> None:
    """Set the new sweep value."""
    self.set_voltage(self.channel, float(self.value))
```

Each instrument command then lives in one place, the driver reads as the steps of the measurement, and the same
methods serve a pysweepme script, the buttons of Instrument Control and the tools an AI agent gets. A fix to a
command reaches all of them.

The Driver API of pysweepme 1.6.1.4 and 1.6.1.5 (shipped with SweepMe! 1.6.1.9) adds a way to *declare* what a
command takes and answers, with standard Python annotations and one decorator, `@command`. Declared commands are
checked on every call, whoever calls them, and are described to SweepMe!, scripts and agents without guessing.

**Every layer is optional.** A driver is valid at every layer:

| Layer | What the driver has | What it gets |
|---|---|---|
| 0 | semantic functions only | runs in the sequencer |
| 1 | public wrapped commands | usable from scripts; offered in Instrument Control, with their kind guessed from the name (`get_`, `set_`, `is_`, `measure_`, `read_`, `fetch_`) |
| 2 | type hints, `Literal` choices and docstrings | typed tool schemas and dropdowns; works on every SweepMe! version |
| 3 | `Annotated` with `Unit`, `Label`, `Range`, `Selector` | units, display texts, bounds; quantities paired for plots and tiles |
| 4 | `@command` with `returns`, `reads`, `composite`, `warnings`, `kind` | every call checked, nothing guessed, warnings shown |

Write all of it for new and revised drivers, but **leave open what is unclear**: declare only what the manual or a
test on the instrument backs up. A wrong `Range` or `Literal` makes SweepMe! refuse a valid value, and only the
driver's author can lift it; a missing declaration costs nothing. Where it is unclear, leave it out and say so in the
docstring or in `doc/description.md`.

### 7.2 Types and a docstring on every command

```python
def get_voltage(self, channel: int) -> float:
    """Measure the voltage."""
```

- Parameter types (`float`, `int`, `bool`, `str`) become typed tool schemas and number fields.
- The return annotation says what the command is: `-> None` is called for its effect (a setter or a run command),
  anything else answers (a reader).
- **A setter returns nothing.** No success flag, no echo of the value, no raw instrument answer. If something is not
  OK, it raises. What the instrument accepted is read by a reader (`get_<quantity>_setpoint`). A command that sets and
  measures in one instrument command returns the measurement, and its name says so (`set_voltage_and_measure`).
- The first docstring line is the description shown in tool lists and tooltips: one sentence, what the command does.

### 7.3 Fixed choices: `Literal`

```python
from typing import Annotated, Literal

from pysweepme.commands import Range, Selector, command

SourceMode = Literal["FVMI", "FIMV"]
Channel = Annotated[int, Selector(), Range(1, 2)]  # a selector (7.8); the markers are explained in 7.4

@command
def set_source_mode(self, channel: Channel, source_mode: SourceMode) -> None:
    """Set the source mode: force voltage/measure current (FVMI) or the reverse (FIMV)."""
    self.port.write(f"SOUR{channel}:{source_mode} ENA")
```

- Use `Literal` for every parameter that takes only fixed strings the protocol requires: modes, named ranges,
  keywords. Write the exact spellings; `@command` matches exactly, without case folding, and suggests the near miss.
  Where the GUI offers other texts ("Sine" for `"SINE"`), the driver maps them with a dict.
- Not for numeric ranges (those are `Range`). Write the choices out; `Literal[SOME_TUPLE]` is rejected by type checkers
  and breaks at runtime.
- Never check with `mode in SourceMode` (a `TypeError` on Python 3.9, silently `False` on 3.14). `@command` does the
  check; the driver writes none of its own.
- Name the choices once as an alias when two or more commands take them.

### 7.4 Units, labels and ranges: `Annotated` on the value

```python
from typing import Annotated

import numpy as np
from pysweepme.commands import Elements, Label, Range, Selector, Unit, command

Volts = Annotated[float, Unit("V")]                          # label derived: "Voltage"
Amperes = Annotated[float, Unit("A")]
RfPower = Annotated[float, Unit("dBm"), Label("RF power")]   # label given where the derived one is wrong
DwellTime = Annotated[int, Unit("ms"), Range(1, 10000)]
Channel = Annotated[int, Selector(), Range(1, 2)]            # a selector, not a value (7.8)
Hertz = Annotated[float, Unit("Hz"), Label("Frequency")]
Frequencies = Annotated[np.ndarray, Elements(Hertz)]         # an array has no element type: Elements carries it


class Device(EmptyDevice):

    @command
    def set_voltage(self, channel: Channel, voltage: Annotated[Volts, Range(-20.0, 20.0)]) -> None:
        """Set the output voltage."""

    @command(returns=("voltage", "current"))
    def get_voltage_and_current(self, channel: Channel) -> tuple[Volts, Amperes]:
        """Measure voltage and current."""

    @command
    def set_dwell(self, channel: Channel, dwell: DwellTime) -> None:
        """Set the dwell time of a sweep step."""
```

Everything about a value is written on the value: on the parameter for what goes in, on the return annotation for
what comes back. Nothing about a single value goes into `@command`.

| Marker | Meaning |
|---|---|
| `Unit("V")` | the unit symbol of the value |
| `Label("RF power")` | display text where the one derived from the name is wrong (abbreviations); the name stays the identifier |
| `Range(min, max)` | inclusive bounds a parameter accepts; `None` for an open side (`Range(0, None)`). Refused outside, never clipped. Only on parameters: an answer is never refused |
| `Selector()` | the parameter addresses a part of the instrument (section 7.8) |
| `Elements(hint)` | the annotation of each element of a `np.ndarray`, which has no element type |

- Markers go on a single value, never on a list, tuple or array: `Annotated[list[float], Unit("V")]` is refused when
  the class is created. A sequence carries them through its element type (`list[Volts]`, `list[tuple[Hertz, Volts]]`),
  an array through `Elements`.
- **One alias per quantity**, used for the setter parameter and the readers' return annotation, so unit and label are
  written once. A setter adds its range on its parameter (`Annotated[Volts, Range(...)]`); nested `Annotated` flattens.
- A range describes the instrument model, true for every unit of it. What depends on the setup (the DUT's maximum
  voltage) belongs to the bench limits of Instrument Control, not into the driver. A range is binding: a bench cannot
  loosen it, so take it from the manual, and widen it in the driver if it turns out too tight.
- Per-model ranges in a driver serving several models, and a unit that depends on another argument (compliance in A
  or V by source mode), are not expressed yet; leave the `Range` out.
- Not in the docstring (`voltage: in V`) and not in the name (`voltage_V`).

**Every alias is defined in the driver itself.** pysweepme ships only the markers. Aliases are written above the
commands that use them, at module level between the imports and `class Device` (the usual place) or in the class body
before the commands; never below the class or inside a method, because the annotations are checked when the class is
created. CamelCase, named after what they hold (`Volts`, `SourceMode`, `VoltageRange`), one alias per meaning.

### 7.5 Quantities: what a command sets and reads

Instrument Control plots and shows in one Control-tab tile what was commanded, what was read back and what was
measured of the same quantity. The pairing comes from the names the driver declares:

- A setter sets the quantity named by its value parameter: `set_voltage(channel, voltage)` sets `voltage`. A setter
  taking several values sets several quantities (`set_pid(p_gain, integral_time, derivative_time)`). A selector is
  never a quantity; a fixed choice beside the values (`set_compliance(compliance, source_mode)`) qualifies the series
  (`compliance (source_mode=Current in A)`).
- A reader reads the quantities named in `@command(returns=...)`, in answer order: `returns=("voltage", "current")`.
  Every reader has `returns`, also a single-value one (`returns=("rf_power",)`); a tuple by convention (any sequence
  of names is accepted, a bare string is refused). Units and labels come from the return annotation, names from
  `returns`.
- A tuple of fixed length is several quantities, one per element; a `list`, `tuple[X, ...]` or `np.ndarray` is one
  quantity whose value is a series; a series of tuples is one series per member.
- Name a value parameter after what it sets, uniquely within the driver: `set_voltage_limit(channel, voltage_limit)`,
  not `(channel, voltage)`, or the limit lands in the voltage plot. **Never `value`, `val`, `state`, `mode`,
  `setting`, `enabled`, `on`, `x` or `v`**: `set_operation_mode(channel, operation_mode)`, `set_noise(noise: bool)`.
  An existing driver is renamed whenever it is touched.
- Never put the channel into a quantity name (`voltage`, not `voltage1`); the channel is a parameter of its own.
- One series per quantity *and arguments*: `get_voltage(pin="AIN0")` is the series `voltage (pin=AIN0)`. Use the same
  argument names in a setter and its read-back so they pair (`set_dac_voltage(channel, voltage)` /
  `get_dac_voltage(channel)`).
- What a command answers: numbers, text, bools, lists or arrays of them, and dicts of these. A camera frame is an
  `np.ndarray` with `Elements(Counts)`; a large one floods an agent's context, so a script reads and saves it. Binary
  data is never returned as `bytes`: the command saves it to the path it is given (`take_screenshot(path)`).

### 7.6 Readers: what they read, and recommended names

A reader reads one of four things, each landing in a different series of its quantity. The name is a recommendation
(in a declared driver names decide nothing); `reads=` is what counts:

| `reads=` | What | Recommended name |
|---|---|---|
| `"measurement"` (default) | a measurement started by the call | `get_<quantity>` (`measure_<quantity>` means the same) |
| `"last"` | the last measured value, without a new measurement | `fetch_<quantity>` |
| `"setpoint"` | a value a command can set, read back | `get_<quantity>_setpoint` where the quantity is also measured, else `get_<quantity>` / `is_<quantity>` |
| `"state"` | a status or identity no command sets | `get_<state>` / `is_<state>` |

- Setpoint or state is decided by whether a command can set the value: a generator's amplitude, a DAC voltage,
  four-wire sensing on or off are setpoints; a sweep status, an identity, a buffer size are states.
- `get_current` measures: after `set_voltage`, a user expects the measured current. `_setpoint` is needed only where
  the quantity is also measured; a setting never measured (`get_source_mode`, `is_output_on`) is read with plain
  `get_` / `is_` and `reads="setpoint"`.
- `get_voltage_setpoint` returns the quantity `voltage` (`returns=("voltage",)`, `-> Volts`): commanded, read-back and
  measured voltage are three series of one quantity.
- Starting a measurement without reading it is a run command (`trigger`), not a reader. Avoid `read_` in new names.
- An existing driver keeps its names (renaming breaks scripts) and declares `reads=` instead.

### 7.7 `@command`: declaring the commands

```python
Channel = Annotated[int, Selector(), Range(1, 2)]

@command
def set_voltage(self, channel: Channel, voltage: Annotated[Volts, Range(-20.0, 20.0)]) -> None:
    """Set the output voltage."""

@command(returns=("voltage", "current"))
def get_voltage_and_current(self, channel: Channel) -> tuple[Volts, Amperes]:
    """Measure voltage and current."""

@command(returns=("voltage",), reads="setpoint")
def get_voltage_setpoint(self, channel: Channel) -> Volts:
    """Read back the voltage setpoint."""

@command(warnings="Re-enumerates the USB device: the open port is lost.")
def reset(self) -> None:
    """Reset the instrument (*RST)."""
```

`@command` marks the method and checks every argument on every call, whoever calls it: a `Literal` choice is matched
exactly, a number choice may come as text (`"2"`) and a text choice as a number, text is converted to the annotated
`int`, `float` or `bool`, a `Range` is checked inclusively, and a wrong value raises a `ValueError` naming the command,
the parameter and what is allowed. The driver writes no check of its own for what the annotations say and keeps only
the checks annotations cannot express (a harmful combination of two parameters).

| Argument | Values | Meaning | Without it |
|---|---|---|---|
| (none) | bare `@command` | the method is a communication command; once one method has it, only decorated ones are | every public method is a command |
| `returns` | tuple of quantity names in answer order | the quantities the answer holds | required for every reader |
| `reads` | `"measurement"`, `"last"`, `"setpoint"`, `"state"` | what a reader reads | `"measurement"` |
| `composite` | `True`, `False` | a higher-level function covering several instrument commands (7.11) | `False` |
| `warnings` | a text, or a tuple of texts | side effects of a valid call that the name and docstring do not make expected (7.10) | none |
| `kind` | `"run"` | a run command whose parameters configure it (`start_stream(pins, scan_rate)`), which the signature alone would make a setter | kind follows from the signature |

**The three kinds of commands.** The signature decides, never the name:

| Kind | What the command does | Decided by | Examples |
|---|---|---|---|
| read | answers a value | a return annotation other than `None` | `get_voltage(channel) -> Volts` |
| set | changes a value that can be read back | `-> None` and at least one value parameter | `set_voltage(channel, voltage) -> None` |
| run | makes the instrument do something; takes no value and answers nothing | `-> None` and no value parameter, or `kind="run"` | `trigger() -> None`, `reset() -> None`, `enable_output(channel) -> None` (a selector is no value) |

The Control tab of Instrument Control offers each kind as its button (Read, Set, Run), and the kind decides how a call
is recorded: a set is the commanded value of its quantity, a run is no value. The word "run" is deliberate: `actions`
already means the list of methods a driver releases to the ActionManager (section 5.6), and a run command is something
else.

Rules:

- **All or nothing.** Once one method of the class (base classes included) carries `@command`, only decorated methods
  are commands. Undecorated public methods stay callable from scripts but are no longer offered as buttons or tools.
  Convert a driver in one pass.
- **Declare completely; nothing is guessed.** Every decorated method has a return annotation, every reader has
  `returns`; `returns` and `reads` are only for readers; `kind` only for run commands. A missing declaration raises
  when the driver loads (a `TypeError` naming the method, or a `ValueError` for a wrong `reads` or `kind` value), so
  an incomplete driver does not load.
- **Never decorate** semantic functions, the GUI methods, helpers, or a **module hook** (Spectrometer
  `get_wavelengths`, WaferProber `get_probeplan` and `get_wafer_geometry`, `find_calibrations`,
  `get_calibrationfile_properties`, `find_ports`): the module needs their exact return type. Mark a hook for the
  checker with `# check_driver: ignore DC004 - a hook of the <Module> module` above the `def`.
- `@command` is the outermost decorator; a plain instance method (`def name(self, ...)`): no `staticmethod`,
  `classmethod`, `property`, `*args` or `**kwargs` (take a list instead).
- A selector takes no default (7.8). An override of a command carries `@command` too.
- List elements are checked: in `list[X]`, `tuple[X, ...]` and `Sequence[X]` every element is checked and converted
  like a single `X`; a fixed-length tuple member by member.

Conversions `@command` performs:

| Annotation | Accepted and converted | Refused |
|---|---|---|
| `float` | numbers, numeric text (`"2.5"`) | `bool`, other text |
| `int` | whole numbers and their text (`"4"`, `4.0`) | `4.5`, `bool` |
| `bool` | `True`/`False`, `0`/`1`, text `true 1 on yes` / `false 0 off no` | anything else |
| `Literal[...]` | a choice exactly; a number choice also as text | another spelling (the error suggests the near miss) |
| `Range` | values within the inclusive bounds | outside, NaN; never clipped |
| `list[X]`, `tuple[X, ...]`, `Annotated[np.ndarray, Elements(X)]` | lists and tuples, each element checked; arrays checked and passed unchanged | text, a scalar |
| `X \| None` | `None` | |

An annotation that cannot be resolved is left out and not checked; the driver still loads.

### 7.8 Selectors: the part of the instrument a command addresses

A parameter that says *where* a command acts (a channel, a slot, a pin) is marked `Selector()` on its alias, and
every command acting on that part takes it under the same name and alias:

```python
Channel = Annotated[int, Selector(), Range(1, 2)]                       # sent in every command (SOUR2:VOLT)
Output = Annotated[
    Literal["+6V", "+25V", "-25V", "TRACK25V"],
    Selector(stateful=True, overlaps={"TRACK25V": ("+25V", "-25V")}),  # kept by the instrument (INST:SEL)
]
Pin = Annotated[str, Selector(overlaps="pin_overlaps")]                 # a method answers, by the connected model
```

- A selector is no value and no quantity: `set_voltage(channel, voltage)` sets the voltage. It takes no default; a call
  without it would silently address the default channel. It is a single value, never a list.
- **Only a marked parameter is a selector in a declared driver.** Nothing is guessed from a name, so a converted driver
  marks `channel` too: an unmarked `channel: int` under `@command` is a plain value, and the method becomes a setter of
  two values. (A driver without `@command` keeps the old rule: a parameter named `channel` is its one selector.)
- A command without a selector addresses everything above it: one without `channel` the whole module, one with no
  selector at all the whole instrument.
- Selecting the subunit is part of the one instrument command, not a second effect: an `INST:OUT<n>` sent in front of
  each command does not make the command `composite`.
- A range that differs per subunit is not expressed yet: `Range` holds the widest bound, the narrower one is a limit
  of the bench entry. Where the selector values depend on another selector (the channels of the module in a slot),
  `Range` or `Literal` is the union, and the instrument refuses the rest.
- **`stateful=True`** where the instrument keeps a selection (`INST:SEL P6V`, then `VOLT 5`): the driver selects in
  `apply_selectors(<selectors>)`, and `@command` calls it only when the selection changes. pysweepme remembers the
  selection per connection (the port with the port manager; a driver without it names its connection in
  `selection_scope()`, e.g. `("labjack", self.serial)`). A reset calls `self.forget_selections()`; `connect()` and
  `disconnect()` forget by themselves. No `set_channel` command. Selecting anywhere but in `apply_selectors` is a bug:
  the memory would not know it.
- **`overlaps=`** where values reach the same hardware (tracking driving both 25 V outputs; DIO4 = FIO4): a mapping,
  symmetric and not chained, or the name of a method answering it for the connected model (`None` before
  `connect()`). Instrument Control then refuses two bench entries on overlapping values. Leave it out where the manual
  does not say it.

The driver of the power supply above takes the stateful selector as `output: Output` in its commands
(`set_voltage(output, voltage)`), and `apply_selectors` takes it under the same name:

```python
# GUI and command names -> the instrument's spelling of INST:SEL
OUTPUT_NAMES = {"+6V": "P6V", "+25V": "P25V", "-25V": "N25V", "TRACK25V": "TRAC"}


def apply_selectors(self, output: Output) -> None:
    """Select the output the following commands act on."""
    self.port.write(f"INST:SEL {OUTPUT_NAMES[output]}")
```

### 7.9 On/off, run commands that produce something, status codes

- **On and off is one `bool` setter** named after what it switches, with its read-back: `set_output(channel,
  output: bool)` and `get_output(channel)` with `reads="setpoint"`, not a pair `enable_output` / `disable_output`.
  Instrument Control shows a `bool` setter as a switch and a pair as two Run buttons. A released pair stays (renaming
  breaks scripts) and gets `set_output` as a composite command beside it; the driver's own `poweron` / `poweroff`
  use it.
- **A run command answers nothing.** When it produces something the caller needs next (the scan rate a stream
  actually runs at, a file name), the driver keeps it and a reader hands it out with `reads="setpoint"`, raising a
  clear error when there is nothing to read yet. The kept value is initialised in `__init__`
  (`self._scan_rate: float | None = None`):

  ```python
  @command(kind="run")
  def start_stream(self, pins: list[str], scan_rate: Hertz) -> None:
      """Start streaming; get_stream_scan_rate answers the rate the device actually runs at."""
      self._scan_rate = float(self.sdk.start_stream(pins, scan_rate))

  @command(returns=("scan_rate",), reads="setpoint")
  def get_stream_scan_rate(self) -> Hertz:
      """Return the scan rate in Hz the last stream actually runs at."""
      if self._scan_rate is None:
          raise RuntimeError("No stream was started, call start_stream first")
      return self._scan_rate
  ```

- **Status codes are never returned.** A vendor library answering a code (0 done, 1 done outside the calibrated
  range, 2 invalid parameter, 38 busy): not done raises `CommandError(message, code=code)` from
  `pysweepme.commands`, with a message for the user and the code beside it (`error.code`); a passing state (busy) is
  waited out inside the command up to a timeout. Done with something to know: a `debug(text)` line from
  `pysweepme.ErrorMessage`, no exception, no return value.
- **Never clip.** A value outside what the instrument or the driver accepts raises (`ValueError` naming the value and
  the range, or `CommandError` with the code) and nothing is sent. Declare a `Range` or `Literal` where the bounds are
  fixed; check limits per subunit or model inside the command. Where the instrument clips by itself, refuse first if
  the driver knows the limit, else read back and raise on a difference.
- A status the instrument keeps (an error queue) is a reader with `reads="state"`.
- **Answers are plain Python types**: numbers, text, bools, lists, tuples, arrays and dicts of them. No ctypes or
  .NET objects, no vendor enums, no complex numbers (answer R and X, or magnitude and phase); a fixed tuple of arrays
  rather than nested dicts.
- **Bound every wait.** A long operation is split into a run command that starts it, a state reader that reports
  progress, and, if wanted, a composite that waits with a timeout and checks `is_run_stopped()`.
- A raw pass-through such as `send_command(command)` is `kind="run"`, or no command at all. A switch matrix sets
  crosspoints with `set_crosspoint(row, column, closed: bool)`.

### 7.10 Warnings: only what is unexpected

A warning is a known side effect of a valid call on this instrument model that is surprising and harmful: a range
command that drives the output to compliance, a reset that drops the USB connection, a mode change that switches the
output off for 100 ms, a command taking a `channel` that acts on all channels.

- No warning for what the command is for: `set_bias` applies a bias, `set_output(True)` switches the output on, a move
  moves, `reset()` resets, `set_temperature_setpoint` heats or cools.
- No warning for a caution that holds for every instrument of the kind ("a higher compliance lets more current
  flow"): what harms a DUT depends on the setup and belongs to the bench limits.
- Something expected but worth knowing goes into the docstring, not into `warnings`.
- A simulation driver harms nothing and carries no warnings.

Why so strict: a warning on every command says nothing, and the one that matters is lost among the others.

1. **Prevent what can be prevented** inside the command, before the instrument sees it:
   `if power > 20 and frequency > 1e9: raise ValueError("...")`.
2. **Declare what remains** with `@command(warnings=...)`: plain text, one string or a tuple with one string per
   warning. They are information; nothing is refused because of them. `@command` appends them to the docstring as a
   `Warnings:` section; do not write that section yourself.

Warnings are declared in `@command` and not in the docstring because they are data: `describe_commands` returns them
as a tuple, the Control tab shows them as a tooltip, an agent gets them as a list, and a composite inherits them.

### 7.11 Composite: higher-level functions

A public function that calls several commands and adds logic (a sequence, waits, loops, decisions), e.g.
`sweep_voltage(start, stop, steps)` or `zero_offset()`, is a higher-level function, not a communication command. It
talks to the instrument only through the commands it calls. If it is offered as a command too, it is declared with
`@command(composite=True)`, so an agent sees that one call runs several instrument commands.

- What makes a function composite is how many instrument commands it covers, not how it sends them. A composite may
  write to the port itself where that is the point (sending many settings first and reading the answers afterwards);
  say why in a short comment. Otherwise call the commands, so each instrument command lives in one place.
- A composite inherits the warnings of the commands it calls: `describe_commands` reads the `self.<command>(...)`
  calls from its code. Do not copy them. Its own `warnings` names only what it adds itself, above all raw port
  traffic the code cannot show.
- Selecting a subunit, reading an acknowledgement or the error status that belongs to a command, and one VISA `query`
  are all part of one plain command.

### 7.12 Imports and versions

```python
from __future__ import annotations

from typing import Annotated, Any, Literal

from pysweepme.commands import CommandError, Elements, Label, Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice
```

- Everything comes from `pysweepme.commands`; `from pysweepme import command` does not work. Import plainly, without a
  `try`/`except ImportError` fallback: on a SweepMe! whose pysweepme does not have the module, the driver does not load
  and the user updates.
- `Unit`, `Label`, `Range`, `Selector` and `@command` need pysweepme 1.6.1.4; `Elements` and `warnings=` need 1.6.1.5,
  which SweepMe! 1.6.1.9 ships; Python 3.10 or newer. Type hints, `Literal` and docstrings alone work on every version.
- A `config.ini` is not needed just because a driver imports `pysweepme.commands`: drivers are developed and tested
  for Python 3.14 only (section 12). Declare `architecture` only for vendored libraries, DLLs or a Python version the
  driver cannot run on.
- A wrong declaration stops the driver from loading, with a message in the debug log, e.g.
  `@command set_voltage: needs a return annotation, -> None for a setter or a run command.`,
  `@command get_voltage: a reader needs returns=(...) naming its answered values - a quantity such as
  returns=('voltage',), or for a state what it is, e.g. returns=('identification',) ...`,
  `@command reads must be one of measurement, last, setpoint, state, not 'setpoints'.`, or
  `@command set_voltage: the selector channel takes no default - a call that leaves it out would silently address
  whichever channel the default names.` A driver that does not load is reported only in the debug log and at run
  start, so read the log after every change.

### 7.13 How SweepMe! reads the declarations

`pysweepme.commands.describe_commands(device)` returns one `CommandSpec` per command (name, description, kind,
parameters with their `ValueSpec` of type, choices, unit, label, range and selector, `returns`, `reads`, `quantity`,
`warnings`, `composite`, `declared`). Instrument Control builds its tool descriptions, Control-tab tiles and limit
editors from it; a declared driver is described exactly, an undeclared one from its public methods and their names.
A driver never needs to call it, but a script can, to see what SweepMe! sees.

---

## 8. Messages, errors, folders and configuration

### 8.1 Telling the user something

| Call | Where it goes | Use it for |
|---|---|---|
| `self.message_log(msg)` | `temp_logbook.txt`, saved together with the measurement data | anything that should still be answerable months later; costs nothing and travels with the data |
| `self.message_info(msg)` | info box of the Measurement tab | the user needs to know now because it affects the result |
| `self.message_box(msg, blocking=False)` | popup | same, when it must not be missed |
| `self.message_balloon(msg)` | balloon notification | low-priority notice |
| `raise ValueError(msg)` (any exception) | stops the run, message and traceback shown to the user | only to **stop** a measurement; write the message for the user, with the value and the allowed range |
| `print()` | Debug widget (F2), transient | development aid only; its frequency in old drivers is a leftover |

`stop_measurement()` and `self.stopMeasurement = "..."` are deprecated: raise instead. Messages from a driver's own
thread must not use `message_info` or `message_box` (section 5.5).

### 8.2 Debugging helpers

- `from pysweepme.ErrorMessage import error, debug`: `error(msg)` prints with the last traceback, `debug(msg)` with a
  timestamp.
- `port_properties["debug"] = True` logs every port write and read; the Port Terminal of SweepMe! traces the managed
  port as well.
- The Debug widget (F2) shows every `print()` and every uncaught exception with its traceback; the same goes to
  `debug.log` in the public SweepMe! folder, overwritten at each start. `SweepMe!.exe -d` shows all debug messages.
- SweepMe! reloads a changed custom or repository `main.py` before each use, so a saved change takes effect at the
  next run or button press. Modules the driver imports from its own folder stay cached in `sys.modules`;
  `importlib.reload()` them at the top of `main.py` or restart SweepMe!. A new driver folder copied into
  `CustomDevices` is found through "Refresh versions" or after a restart.

### 8.3 Folders

`self.get_folder(key)` with `"SELF"` (the driver folder), `"TEMP"`, `"CUSTOMFILES"`, `"EXTLIBS"`, `"CALIBRATIONS"`,
`"PUBLIC"`.

### 8.4 Machine-specific configuration

Settings that differ per computer (a DLL or SDK path, a serial number) go into `<CUSTOMFILES>/<DriverFolder>.ini`,
read with `self.is_configfile()`, `self.get_configsections()`, `self.get_configoptions(section)` and
`self.get_config()`. Ship a template INI with the driver; users copy it through the version manager's context menu
"Copy configuration (.ini) file to 'CustomFiles'". `config.ini` is *not* for user settings (section 12).

---

## 9. Working from manuals; instrument behaviour that bites

Never invent commands. Beyond that:

- **Prefer the manufacturer's online manual** over a bundled PDF: the corrections are exactly the range limits and
  mode restrictions a driver encodes.
- **Do not "harmonise" asymmetric notes between sibling models**: two models of one family can genuinely differ.
  Verify each.
- **Firmware changes the command set.** Where several generations must be supported, note the minimum version per
  command in `doc/description.md`, and gate model-specific features on explicit checks in `initialize()`.
- **Document quirks, required cabling and hard limits in `doc/description.md`**, so the user meets them before the
  driver has to reject them.
- Specified output levels assume a specified load: a generator calibrated into 50 Ω reads higher into high impedance.
  Say so in the documentation before someone reports it as a bug.

Traps worth checking in every new driver:

- **A value node is often not an enable node.** A setpoint may be accepted silently and stay ineffective until a
  separate enable, apply or trigger command. Confirm that a write changed the instrument; the absence of an error
  proves nothing.
- **A range can clamp a setpoint silently, and the read-back shows the clamped value.** Set the range explicitly,
  before the setpoint, and compare the read-back with the request.
- **Commands overwrite each other, and the order matters.** Fix a deliberate write order and comment why.
- **`*RST` and preset commands reset more than they advertise.** If an option offers "keep as is", read the value
  back before the preset and restore it afterwards.
- **Convert documented sentinel values** (9.9e37 for overload) to `inf` or `nan` instead of passing them into the data.
- **Reject impossible values and combinations, never clip** (section 7.9).
- **Instruments with one active function** (a multimeter's mode) shared by several instances: re-send the own
  function before measuring when another instance changed it (section 6.4).

---

## 10. Code style, layout and conventions

### 10.1 Order within `main.py`

1. License header (MIT text, `Copyright (c) <first year>-<current year> SweepMe! GmbH (sweep-me.net)`, extended on
   every update; contributor credits stay), then the `# SweepMe! driver / # * Module: / # * Instrument:` comment.
2. Imports.
3. Aliases: `Literal` choices, `Annotated` units, labels, ranges, selectors; option dictionaries.
4. `class Device(EmptyDevice)` with a docstring (user docs go into `doc/description.md`).
5. `__init__`.
6. `update_gui_parameters`, `apply_gui_parameters`.
7. Semantic functions, each pair together and the pairs in this order: `connect`/`disconnect`,
   `initialize`/`deinitialize`, `configure`/`unconfigure` (`reconfigure` right after), `poweron`/`poweroff`,
   `signin`/`signout`; then the per-point functions in call order (`start`, `apply`, `reach`, `adapt`,
   `adapt_ready`, `trigger_ready`, `measure`, `request_result`, `read_result`, `process_data`, `call`, `finish`).
8. Communication commands (`get_identification`, `set_voltage`, ...), after a clearly separated comment line.
9. Helpers.

### 10.2 Style

- `from __future__ import annotations`, type hints on every method and attribute, Google-style docstrings on every
  method. The repository's `pyproject.toml` configures ruff (line length 120, nearly all rule sets) and black; new code
  passes `ruff check`, `black --check` and `mypy` (the message that pysweepme is untyped is baseline).
- f-strings, not `%`-formatting. `msg = "..."` then `raise ValueError(msg)`.
- English everywhere: code, comments, docstrings, documentation, commit messages. No running commentary comments.
- No personal data in code, comments or commit messages: this repository is public. Never copy names, e-mail
  addresses or organisations from bug reports.
- No `tests/` that mock `self.port` for new drivers: verify with ruff, black, mypy, the importability CI and the real
  instrument. Name hardware risks in the hand-over, never "not tested with hardware" in docs or code.

### 10.3 Naming and structure

- Driver folder: `<Module>-<Manufacturer>_<Model>`, `x` wildcard for a family (`Switch-Keithley_622x`). Favour
  findability over reuse: a combined instrument gets a driver named after its model, with a note on the shared command
  set in the header and in `doc/description.md`.
- GUI keys: Title Case, no underscores, space between number and unit ("200 mA"), `<Quantity> in <unit>`.
- Commands: `set_<quantity>`, `get_<quantity>`, `get_<quantity>_setpoint`, `fetch_<quantity>`, `is_<state>`; value
  parameters named after their quantity (section 7.5).
- Keep GUI options that the manual does not list when modernising an existing driver (the original author may have
  had an extended model); mention them in `doc/description.md`.
- Porting a contributed or vendor script: all communication through the port manager, no vendored libraries, commands
  ported close to the device-tested source (raise on out-of-range values, drop logging machinery, keep the
  behaviour), German text translated, docs moved to `doc/description.md`. A latent bug in the source is ported
  verbatim and flagged, not silently fixed, so the fix maps 1:1 to the validated reference.

### 10.4 Simulation drivers

The `*-Simulation_Driver` folders (and `SMU-Simulation_Diode`) run without hardware and are the reference for the
Driver API: every one declares its commands with `@command`. They stay short example drivers (around 100 lines),
expose only GUI parameters that affect the simulation, and have a deterministic mode ("No Noise" or a noise level of
0) for reproducibility tests. Being test drivers, their commands may change freely between releases; only their
semantic functions must keep working. Use them to test sequences, Instrument Control and this guide's rules without an
instrument.

---

## 11. Checklists

### 11.1 Every driver

- `__init__` is lightweight: no DLLs, no connections, every attribute typed with a default
- `variables`, `units`, `plottype`, `savetype` have equal length and `call()` returns that many values
- modern GUI API (`update_gui_parameters` / `apply_gui_parameters`); every parameter read uses `.get()` with a
  default; new keys default so existing sequences still load
- no GUI parameter converted in place; converted values live in separate attributes written from `configure()`
- GUI values validated in `configure()`, right after converting, with `raise ValueError(msg)` and a user-readable
  message
- no deprecated calls: `stopMeasurement`, `stop_measurement`, `get_GUIparameter`, `find_Ports`, `get_Folder`,
  `write_Log`, `message_Box`, `message_Info`, `is_run_aborted`
- long loops abortable through `is_run_stopped()`
- trigger and read in the same phase; no state-rebuilding command inside a per-point method
- teardown tolerates a failed setup
- all communication through the port manager, or a raw connection with a timeout
- instrument commands verified against the current manual (or the instrument); model-specific differences checked in
  `initialize()`
- quirks, cabling and limits documented in `doc/description.md`; no `description` attribute in `main.py`
- `license.txt` and the header carry the same copyright line; no personal data anywhere
- `ruff check`, `black --check` and `mypy` pass

### 11.2 Communication commands

- each communication command wraps exactly one instrument command; functions that combine commands call them and,
  if offered, carry `composite=True`
- the semantic functions call the wrapped commands; no raw instrument command that a wrapper already covers
- every wrapped command has full type hints, a return annotation and a one-line docstring
- setters and run commands return nothing: no success flag, no echoed value, no raw answer; errors raise; what a run
  command produces is read with a getter (`reads="setpoint"`); a run command with parameters is `kind="run"`
- every fixed-string parameter is a `Literal`; no own check of what the annotations already say; no import fallback
- every physical quantity has a unit through one alias per quantity, on the setter parameter and the readers' return
  annotation; `Label` only where the derived label is wrong
- setter parameters carry a `Range` where the manual states the bounds for every supported model; nothing about a
  single value in `@command`
- all aliases defined in the driver, above the commands that use them
- every selector (channel, slot, pin) is marked `Selector()`, `channel` included; no default on a selector
- every value parameter is named after its quantity, uniquely within the driver; no channel in quantity names; never
  `value`, `state`, `mode`, `enabled`, ...
- on/off is one `bool` setter with its read-back
- module hooks stay undecorated with their return types, marked `# check_driver: ignore DC004`
- readers declare `reads=` where they do not measure (setpoint read-backs!)
- a driver using `@command` decorates every wrapped command and nothing else; every reader has `returns`
- a status code is never returned: not done raises `CommandError(..., code=...)`; done with a remark writes `debug()`
- harmful combinations are refused in the command; `warnings=` only for side effects the name and docstring do not
  make expected; a composite does not copy the warnings of what it calls
- `tools/check_driver.py src/<DriverFolder>` reports nothing (section 13)

---

## 12. Third-party libraries, `config.ini` and Python versions

SweepMe! 1.5.6 to 1.5.8 run Python 3.9 (1.5.5 ran 3.6), SweepMe! 1.6.1 and newer run Python 3.14. Drivers are
developed and tested for Python 3.14 (64 bit) only; the CI and `tox` run nothing else. Existing `libs_39_*` folders
and `3.9` flags stay for users of SweepMe! 1.5.x, but are no longer built or extended.

### 12.1 Policy

- **New drivers vendor nothing**: port the needed commands into `main.py` and accept some duplication between sibling
  drivers. If a package is unavoidable, it must be MIT-licensed (or compatibly licensed, section 14).
- Vendored packages go into `libraries/libs_314_64` (the pattern is `libs_<pyver>_<bits>`; older drivers also carry
  `libs_39_32` and `libs_39_64` for SweepMe! 1.5.x), built from `libraries/requirements.txt` with the LibraryBuilder
  (from the sweep-me.net dashboard): it needs Python 3.14 installed, excludes the packages SweepMe! already ships,
  writes a `LICENSE_<package>.txt` per package next to `requirements.txt`, and does not overwrite an existing `libs_`
  folder. Review packages whose license it could not determine. Users who run a driver in their own Python install
  the requirements themselves.
- `libraries/libs_common` holds only version-independent pure-Python source, never `.dll`, `.pyd` or `dist-info`. It
  is prepended to `sys.path` *first*, so a stale copy shadows the versioned folder. Some drivers keep an almost empty
  `libs_common` on purpose, to suppress the fallback to a legacy `libs/` folder; do not delete it.
- Vendored packages must accept the versions of the packages SweepMe! ships (pymodbus, numpy, ...). Vendor the
  newest version compatible with Python 3.14; when updating a driver whose package no longer supports 3.9, drop
  `libs_39_*` and declare `architecture = "3.14-64"` (12.2).
- A vendored package shadows SweepMe!'s bundled copy process-wide once the driver loads.
- DLLs must be 64-bit (`WinError 193` otherwise). Put them into the driver folder (added to `PATH` automatically)
  or the public `ExternalLibraries` folder. A C DLL loads with `ctypes` (set `restype` and `argtypes`), a .NET
  assembly with `import clr; clr.AddReference("Name")`, whose assembly name may differ from the import name.

### 12.2 `config.ini`

```ini
[config]
; <reason for the restriction>
architecture = "3.14-64"
```

- Flags: `any`, `any-64`, `3.14-any`, `3.14-64`, `3.9-64`, `3.6-32`, as a quoted comma-separated list. No file means
  all architectures. Comments start with `;`.
- A driver whose list lacks the running architecture is silently excluded from the driver list and the version
  manager. When a driver "does not show up", check `config.ini` first.
- Deprecating a driver for a Python version touches only this file.

### 12.3 Migration notes for Python 3.14

- `imp` is gone; drivers that load a sibling `.py` use `from pysweepme import load_source` (pysweepme 1.6.1.x,
  Python 3.10+) and declare `architecture = "3.14-64"`.
- "bad magic number" on loading means a vendored `.pyc` comes from another Python (3.6: `3\r\r\n`, 3.9: `a\r\r\n`,
  3.14: `2b 0e 0d 0a`).
- Vendored or contributed source files must be UTF-8 (ideally ASCII); a cp1252 quote fails on a fresh checkout while a
  stale `__pycache__` hides it locally.

---

## 13. Testing and debugging

- **In SweepMe!:** create a custom version or load the repository through `SWEEPME_DRIVERS_REPO` (section 1), build a
  sequence (Loop -> MakeFile -> the module), and watch the Debug widget (F2) and the Port Terminal.
- **Standalone with pysweepme:**

  ```python
  import pysweepme

  driver = pysweepme.get_driver("SMU-Keithley_2400", r"C:\path\to\instrument-drivers\src", "GPIB0::24::INSTR")
  driver.connect()
  driver.initialize()
  print(driver.get_identification())
  driver.set_voltage(1.0)
  driver.disconnect()
  ```

  pysweepme must run on a Python that matches SweepMe!'s (3.14 for 1.6.1). With the port manager the port is opened
  and attached by `get_driver`, but `connect()` must still be called. `folder=None` loads the version selected in
  SweepMe!'s version manager (pysweepme 1.6.1.3 and newer). Convenience wrappers for scripts: `set_parameters({...})`
  (the driver's GUI keys plus `Port`, `Label`, `Channel`, `Device`), `get_parameters()`, `write(value)` (runs
  `start`, `apply`, `reach`), `read()` (runs `adapt` through `call` and returns the values), `get_variables()`,
  `get_units()`. `get_driver` without a port string passes no `Port`; a `KeyError: 'Port'` then means the import
  itself succeeded. Set the environment variable `SWEEPME_DEBUGMODE=True` to see debug-only messages.
- **With Instrument Control (SweepMe! Pro):** put the driver on a bench and let an agent, or yourself in the Control
  tab, call every command. The instrument description shows each command as `declared` with its units, ranges,
  choices and warnings; bench limits, `Range` and in-command checks each refuse their case. This is the recommended
  way to test a declared driver.
- **`tools/check_driver.py`** in this repository reads a driver's source (it imports no driver, so vendor libraries
  are not needed) and reports where it departs from sections 7 and 10, as a work list with codes `DC000` to `DC020`:
  a command parameter without a type annotation or a command without a return annotation or docstring, a parameter
  compared with fixed strings instead of a `Literal`, an undecorated public method in a converted driver, a setter
  that returns a value, a reader without `returns`, a command calling commands without `composite=True`, a composite
  that sends raw commands without a comment, two setters sharing a value-parameter name, a check of what the
  annotation already says, a `Warnings:` section written by hand, a semantic function sending a command a wrapper
  covers, the semantic functions out of order or a pair split, markers written inline instead of in an alias, a
  legacy `description` attribute, and generic value-parameter names. `warning` marks what is most likely wrong,
  `hint` what is worth a look; a driver stays valid with any of them. A deliberate finding is accepted with
  `# check_driver: ignore DC0xx - <why>` on or above the line. Run it on every driver you touch:

  ```
  python tools/check_driver.py src/<DriverFolder>
  python tools/check_driver.py src --json > findings.json
  ```
- **Lint:** `ruff check src/`, `black --check src/`, `mypy src/` from the repository root; `black src/` then
  `ruff check --fix src/` to format.
- **Importability CI:** every pull request runs `tests/importability/import_driver.py` for the changed drivers on
  Python 3.14 with the pinned pysweepme; drivers that need vendor software are listed in `SKIPPED_DRIVERS`. Test in a
  clean environment: a vendor SDK installed on the development PC masks vendored-library failures.
- **Refactoring without hardware:** load the old driver from `git HEAD` and the new one, run both through the full
  lifecycle against a fake port that feeds the replies, and diff the sent command sequences and the returned values.
  This is a one-off comparison in a scratch script, not a `tests/` suite to commit (section 10.2).
- **Streaming hardware:** judge sustainability only over windows longer than the buffer-fill time; the device's
  overflow error is the arbiter.

---

## 14. Contributing

- Drivers are contributed through a pull request to `main` or by e-mail to contact@sweep-me.net; a contribution
  agreement is needed before pull-request access, and an employer may have to agree as well. Contributors are named
  unless they ask otherwise.
- **Licensing:** MIT whenever possible, so that the driver landscape stays uniform and compatible with proprietary
  vendor libraries. The MIT text with the copyright line stands as a comment header in every own code file and in
  `license.txt` next to `main.py`; `license.txt` holds the driver's license only, never a third party's. A driver
  based on another MIT driver keeps the original copyright line as a second line and names the original authors.
  Third-party packages keep their own license in their own folder (the LibraryBuilder writes `LICENSE_<package>.txt`):
  permissive and weak-copyleft licenses (MIT, BSD, PSF, Apache, LGPL) are fine with the license file included; GPL
  code is not accepted, because the driver would become GPL; a commercial or unknown license needs the holder's
  written permission to redistribute and publish, else the driver does not ship the package, tells the user how to
  obtain it, and checks for it in `__init__`. Drivers whose command set is not publicly available need the
  manufacturer's permission. Code copied from other repositories or forums with an inventive step is marked with a
  comment and its license checked; better, rewrite it. Details: the wiki's "License Guide for Drivers".
- **Branches and commits:** branch from `origin/main`; drivers of one project share one branch; commit messages like
  `fix(<DriverFolder>): <description>`; before pushing, fold follow-up edits so there is one commit per driver, and a
  PR touching many drivers gets one commit per mechanical change type. Keep tracker or status documents out of the
  history.
- **Hand-over:** name what was tested on hardware and what was not, model-specific assumptions, and open questions.
- **Documentation:** `doc/description.md` with supported models, usage, wiring, quirks and the communication
  commands; no claims about untested models on the public web page.

---

## 15. A complete example driver

A temperature controller, written at every layer of the Driver API: GUI parameters, the semantic functions it needs,
and declared communication commands that the semantic functions call. The instrument commands are placeholders;
take the real ones from the manual. The same example is what SweepMe!'s MCP server hands to an AI agent with
`agent_help('drivers')`; the simulation drivers in `src/` are complete, runnable examples at the same level.

```python
# <MIT license header, see section 10.1>
#
# SweepMe! driver
# * Module: Temperature
# * Instrument: <Manufacturer> <Model>

from __future__ import annotations

from typing import Annotated, Any, Literal

from pysweepme.commands import Range, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice

Celsius = Annotated[float, Unit("°C")]
Sensor = Literal["PT100", "Type K"]


class Device(EmptyDevice):
    """Driver for the <Manufacturer> <Model> temperature controller."""

    def __init__(self) -> None:
        """Set the return values and the port."""
        super().__init__()
        self.shortname = "<Model>"
        self.variables = ["Temperature", "Setpoint"]
        self.units = ["°C", "°C"]
        self.plottype = [True, True]
        self.savetype = [True, True]
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {"timeout": 5, "baudrate": 9600}
        self.sweep_mode: str = "None"

    def update_gui_parameters(self, parameters: dict[str, Any]) -> dict[str, Any]:
        """Return the GUI fields."""
        return {"SweepMode": ["None", "Temperature"], "TemperatureUnit": ["°C"]}

    def apply_gui_parameters(self, parameters: dict[str, Any]) -> None:
        """Keep the selection."""
        self.sweep_mode = parameters.get("SweepMode", "None")

    # Semantic functions: undecorated, they call the commands.
    def poweron(self) -> None:
        """Switch the heater on for the run."""
        self.set_heater(True)

    def poweroff(self) -> None:
        """Switch the heater off."""
        self.set_heater(False)

    def apply(self) -> None:
        """Set the new sweep value."""
        self.set_temperature(float(self.value))

    def call(self) -> list[float]:
        """Return one value per variable."""
        return [self.get_temperature(), self.get_temperature_setpoint()]

    # A hook of the Temperature module, which polls it until the setpoint is reached: undecorated, not a command.
    # check_driver: ignore DC004 - a hook of the Temperature module
    def measure_temperature(self) -> float:
        """Return the temperature in the selected unit for the module's reach check."""
        return self.get_temperature()

    # Communication commands (placeholder instrument commands: take the real ones from the manual).
    @command
    def set_temperature(self, temperature: Annotated[Celsius, Range(-50.0, 200.0)]) -> None:
        """Set the target temperature."""
        self.port.write(f"TEMP {temperature}")

    @command(returns=("temperature",), reads="setpoint")
    def get_temperature_setpoint(self) -> Celsius:
        """Return the target temperature."""
        return float(self.port.query("TEMP?"))

    @command(returns=("temperature",))
    def get_temperature(self) -> Celsius:
        """Measure the temperature."""
        return float(self.port.query("MEAS:TEMP?"))

    @command
    def set_heater(self, heater: bool) -> None:
        """Switch the heater on or off."""
        self.port.write("HEAT ON" if heater else "HEAT OFF")

    @command(returns=("heater",), reads="setpoint")
    def get_heater(self) -> bool:
        """Return whether the heater is on."""
        return self.port.query("HEAT?").strip() == "ON"

    @command
    def set_sensor(self, sensor: Sensor) -> None:
        """Select the sensor type."""
        self.port.write(f"SENS {sensor}")

    @command(returns=("sensor",), reads="setpoint")
    def get_sensor(self) -> Sensor:
        """Return the sensor type."""
        return self.port.query("SENS?").strip()  # type: ignore[return-value]  # one of Sensor

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return the instrument's identification."""
        return self.port.query("*IDN?").strip()
```

What the example shows:

- `temperature` is one quantity: `set_temperature` sets it, `get_temperature` measures it,
  `get_temperature_setpoint` reads it back. All three share the alias `Celsius`, so the unit is written once, and the
  Control tab shows them in one tile.
- `set_heater(heater: bool)` with `get_heater` is the one-switch pattern; `poweron`/`poweroff` call it.
- `Sensor` is a `Literal` alias, used by the setter and its read-back; `@command` refuses any other text.
- `measure_temperature` is a hook the Temperature module calls by name for its "Reach Temperature" check; it stays
  undecorated and calls the command.
- `get_identification` is a state reader. There are no run commands and no warnings, because nothing here is
  surprising.
- The user documentation for this driver goes into `doc/description.md` in its folder, not into the code.
