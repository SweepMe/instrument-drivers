# python
import ctypes
import struct
import sys
import os

dll_path = r'C:\Windows\System32\wgfmu.dll'  # alternative path: r'C:\Windows\SysWOW64\wgfmu.dll' (32 Bit)
_dll = ctypes.WinDLL(dll_path)


def make_char_pointer(string: str) -> ctypes.c_char_p:
    """Make a char pointer from a python string to be used without c.byref."""
    bytes_ = string.encode("ascii")
    return ctypes.c_char_p(bytes_)


def clear() -> None:
    """Clears all waveform patterns and sequences."""
    _dll.WGFMU_clear()


def create_pattern(pattern_name: str, initial_voltage: float) -> None:
    """Creates a waveform pattern with the given name and initial voltage."""
    _dll.WGFMU_createPattern(
        make_char_pointer(pattern_name),
        ctypes.c_double(initial_voltage),
    )


def get_pattern_force_value_size(pattern_name: str) -> int:
    """Gets the size of the force value array for the given pattern.

    Example function
    """
    # TODO: not working yet
    c_size = ctypes.c_int32()
    _dll.WGFMU_getPatternForceValueSize(
        make_char_pointer(pattern_name),
        c_size,
    )
    return int(c_size.value)

# Example 1
# Offline commands
clear()
create_pattern("pulse", 0)  # 0 ms, 0 V
print(get_pattern_force_value_size("pulse"))



# client.WGFMU_addVector("pulse", 0.0001, 1)  # 0.1 ms, 1 V
# client.WGFMU_addVector("pulse", 0.0004, 1)  # 0.5 ms, 1 V
# client.WGFMU_addVector("pulse", 0.0001, 0)  # 0.6 ms, 0 V
# client.WGFMU_addVector("pulse", 0.0004, 0)  # 1.0 ms, 0 V
# client.WGFMU_addSequence(101, "pulse", 10)  # 10 pulse output
