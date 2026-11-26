# Logger (PC Time)

**Module**: Logger

## Description

Returns the time elapsed since a chosen step of the run, the clock time and the date of the PC, and a timestamp.

## Requirements

- No instrument and no extra libraries.

## Usage

1. Add the Logger module and select this driver.
2. Check the values to return.
3. Choose with **Zero time on** when the elapsed time starts at zero.

## Parameters

- **Seconds**, **Minutes**, **Hours**, **Days**, **Clock**, **Date**, **Timestamp**: check boxes for the returned
  values.
- **Zero time on**:
  - `initialize`: once at the start of the run.
  - `configure`: each time the run enters the branch of the module.
  - `signin`: for each variation or repetition of the modules above.

## Returns

In this order, if checked:

- **Time** (s), **Time** (min), **Time** (h): elapsed time.
- **Days** (d): elapsed time in days.
- **Clock**: clock time as `'hh:mm:ss'`, with the quotes.
- **Date**: date as `yyyy/mm/dd`.
- **Timestamp**: date and time of the PC.

## Communication commands

- `zero_time()`: reset the elapsed time to zero. It is also offered as action, e.g. for a button.
