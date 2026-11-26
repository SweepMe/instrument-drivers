# Logger (PC CPU and Memory usage)

**Module**: Logger

## Description

Logs how busy the PC is: the CPU usage, the memory usage, the usage of drive C: and the share of the memory that
SweepMe! itself uses. Useful to find out whether a long measurement is slowed down by the PC or leaks memory.

## Requirements

- No instrument and no extra libraries (psutil ships with SweepMe!).

## Usage

Add the Logger module and select this driver. It has no parameters.

## Returns

- **CPU usage** (%): CPU usage of the whole PC since the previous point; the first point of a run can be 0.
- **Memory usage** (%): share of the physical memory in use.
- **Disk (C:) usage** (%): share of drive C: in use.
- **SweepMe! memory usage** (%): share of the physical memory used by the SweepMe! process.

## Communication commands

- `get_cpu_usage()`, `get_memory_usage()`, `get_disk_usage()`, `get_process_memory_usage()`: return the values
  above in %.
