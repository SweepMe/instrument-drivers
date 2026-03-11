# Keysight B1500 Driver

## Description

This driver automates the waveform generation of WGFMU modules in the Keysight B1500 semiconductor parameter analyzer. 
It allows users to define custom pulse sequences and measurement events, which can be repeated for a specified number of 
times or duration.

## Requirements

Install the WGFMU istrument library https://www.keysight.com/us/en/lib/software-detail/driver/b1530a-wgfmu-instrument-library--sample-programs-2117445.html

## Usage

The driver requires a CSV file that defines the pulse sequence and measurement events.

### CSV File Format

The CSV file must follow this structure:

1. **Measurement Events Section** (one or more lines):
   - Header: `measure_start;points;interval in s;`
   - Data rows: `<start_time>;<num_points>;<interval>`
   - Example: `0;100;0.00001` (start at t=0s, capture 100 points, with 10µs intervals)

2. **Waveform Section**:
   - Header: `time in s;voltage in V`
   - Data rows: `<time_increment>;<voltage>`

3. Example:
    ```
   measure_start;points;interval in s;
   0.001;10;0.00001
   0.002;2;0.00001
   time in s;voltage in V
   0;0
   0.001;1
   0.001;1
   0.001;0
    ```

### Important Notes

- **First time increment**: Must be 0 for the initial point, representing the first timestamp of the sequence
- **Time values**: Represent increments (time since the last point), not absolute times
- **Time resolution**: 10ns minimum. Values below this will raise an error. Non-multiples of 10ns will be rounded
- **Measurement repetition**: Measurement events are repeated for each sequence repetition. For example, 3 measurement events with 2 repetitions results in 6 total measurements
- An example sequence file can be found in the driver folder

## Parameters

- **Channel and Slot**: The dropdown menu items are editable, choose the slot where the WGFMU module is installed and the channel to use for output

- **Amplitude in V / No scaling**: 
  - "Amplitude in V": Scales the maximum output voltage to the specified value
  - "No scaling": Uses the voltage values from the CSV file directly
  
- **Repetitions / Measurement time in s**:
  - "Repetitions": Repeat the sequence for the specified number of times
  - "Measurement time in s": Run the sequence continuously for the specified duration

## Returns

- **Timestamp** [s]: Time of each measurement point
- **Measured voltage** [V]: Voltage measured at each point
