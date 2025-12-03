# python
from __future__ import annotations

import ctypes
import struct
import sys
import os

dll_path = r'C:\Windows\System32\wgfmu.dll'  # alternative path: r'C:\Windows\SysWOW64\wgfmu.dll' (32 Bit)
_dll = ctypes.WinDLL(dll_path)


def make_char_pointer(string: str) -> ctypes.Array[ctypes.c_char]:
    """Return a ctypes buffer suitable for passing as a C `char *`.

    The returned buffer object keeps the bytes alive while referenced.
    """
    return ctypes.create_string_buffer(string.encode("ascii"))


def clear() -> None:
    """Clears all waveform patterns and sequences."""
    _dll.WGFMU_clear()


def create_pattern(pattern_name: str, initial_voltage: float) -> None:
    """Creates a waveform pattern with the given name and initial voltage."""
    _dll.WGFMU_createPattern(
        make_char_pointer(pattern_name),
        ctypes.c_double(initial_voltage),
    )


def add_vector(pattern_name: str, time_value: float, voltage: float) -> None:
    """Adds a vector to the specified waveform pattern.

    Args:
        pattern_name: The name of the waveform pattern.
        time_value: Incremental time value in seconds (time since last point), rounded to multiples of 10ns.
        voltage: Output voltage in volts.
    """
    if time_value < 1e-8 or time_value > 10995:
        raise ValueError("time_value must be between 10ns and 10995s")

    _dll.WGFMU_addVector(
        make_char_pointer(pattern_name),
        ctypes.c_double(time_value),
        ctypes.c_double(voltage),
    )


def make_generic_array(len_: int, values_list: list | None = None, data_type=ctypes.c_double):
    """Makes a c_array of data_types. The array values are 0 if no values_list is specified
    if values is not empty a length len_ is to be given.
    """
    if values_list:
        if not len_:
            len_ = len(values_list)
        return (data_type * int(len_))(*values_list)
    else:
        return (data_type * int(len_))()


def make_double_array(values: list[float] | None = None):
    """Makes a c_double array. The array values are 0 if no values list is specified
    - if values is not empty a length len_ is to be specified.
    """
    return make_generic_array(len(values), values, ctypes.c_double)


def add_vector_array(pattern_name: str, time_values: list[float], voltage_values: list[float]) -> None:
    """Adds multiple vectors to the specified waveform pattern.

    Args:
        pattern_name: The name of the waveform pattern.
        time_values: List of incremental time values in seconds (time since last point), rounded to multiples of 10ns.
        voltage_values: List of output voltages in volts.
    """
    if len(time_values) != len(voltage_values):
        raise ValueError("time_values and voltage_values must have the same length")

    num_points = len(time_values)

    _dll.WGFMU_addVectors(
        make_char_pointer(pattern_name),
        make_double_array(time_values),
        make_double_array(voltage_values),
        ctypes.c_int32(num_points),
    )


def get_pattern_force_value_size(pattern_name: str) -> int:
    """Gets the size of the force value array for the given pattern."""
    c_size = ctypes.c_int32()
    _dll.WGFMU_getPatternForceValueSize(
        make_char_pointer(pattern_name),
        ctypes.byref(c_size),
    )
    return int(c_size.value)

# Example 1
# Offline commands
clear()
my_pattern = "pulse"
create_pattern(my_pattern, 0)  # 0 ms, 0 V
add_vector(my_pattern, 0.001, 1)  # 1 ms, 1 V
add_vector(my_pattern, 0.001, 0)  # 2 ms, 0 V
add_vector_array(my_pattern, [0.001, 0.001, 0.001], [1, 0, 1])  # 3 ms, 1 V; 4 ms, 0 V; 5 ms, 1 V
ret = get_pattern_force_value_size(my_pattern)
print(ret)


# client.WGFMU_addVector("pulse", 0.0001, 1)  # 0.1 ms, 1 V
# client.WGFMU_addVector("pulse", 0.0004, 1)  # 0.5 ms, 1 V
# client.WGFMU_addVector("pulse", 0.0001, 0)  # 0.6 ms, 0 V
# client.WGFMU_addVector("pulse", 0.0004, 0)  # 1.0 ms, 0 V
# client.WGFMU_addSequence(101, "pulse", 10)  # 10 pulse output
