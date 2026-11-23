# Logger (PC Screenshot)

**Module**: Logger

## Description

Saves a screenshot of a monitor, or of a region of it, as PNG file at every point and returns the path of the file.
Useful to document the screen of another program during a measurement.

## Requirements

- Windows. The driver ships the package `mss` for Python 3.14 (64 bit); it runs in SweepMe! 1.6.1 and newer.

## Usage

1. Add the Logger module and select this driver.
2. Choose the **Monitor**: 1 is the primary monitor, 2 the next one, 0 the whole virtual screen spanning all
   monitors.
3. Leave **x1**, **y1**, **x2** and **y2** empty for the whole monitor, or enter the corners of a region in pixels of
   the monitor, with the origin in its upper left corner. The region must lie inside the monitor.

## Parameters

- **x1**, **y1**, **x2**, **y2**: region in px; empty means the edge of the monitor.
- **Monitor**: number of the monitor.
- **File suffix**: part of the file name, after the module label; may be empty.

## Returns

- **Path**: path of the screenshot in the temporary folder of the run, `temp_<label>_<suffix>_<number>.png`. A file
  of an earlier run with the same name is replaced.

## Notes

- Up to 2026, the region was taken from the whole virtual screen whatever monitor was chosen; it now lies on the chosen
  monitor. For monitor 1 nothing changes.

## Communication commands

- `get_monitors()`: geometry of all monitors (left, top, width, height); index 0 is the whole virtual screen.
- `get_screen_size(monitor)`: width and height of a monitor in px.
- `take_screenshot(path, monitor, x1, y1, x2, y2)`: save a screenshot of a region as PNG at `path`, which must be
  absolute, end with `.png`, lie in an existing folder and not exist yet; it never overwrites a file. x2 = y2 = 0
  takes the whole monitor.

`monitor` must always be given, e.g. `get_screen_size(1)` or `take_screenshot(path, 1)` for the primary monitor. It
selects the part of the PC a command acts on, and such a selector has no default in the driver API, so that a call
never addresses a monitor by accident. Earlier versions of these two commands used monitor 1 when it was left out.
