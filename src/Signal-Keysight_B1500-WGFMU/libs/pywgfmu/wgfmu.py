# python
from __future__ import annotations

import ctypes
import time
from enum import Enum

dll_path = r"C:\Windows\System32\wgfmu.dll"  # alternative path: r'C:\Windows\SysWOW64\wgfmu.dll' (32 Bit)
_dll: ctypes.WinDLL


# DLL Loading and Helper Functions

def load_dll() -> None:
    """Load the library with ctypes."""
    global _dll
    _dll = ctypes.WinDLL(dll_path)

def make_char_pointer(string: str) -> ctypes.Array[ctypes.c_char]:
    """Return a ctypes buffer suitable for passing as a C `char *`.

    The returned buffer object keeps the bytes alive while referenced.
    """
    return ctypes.create_string_buffer(string.encode("ascii"))


def make_generic_array(len_: int, values_list: list[float|int|str] | None = None, data_type=ctypes.c_double):
    """Makes a c_array of data_types. The array values are 0 if no values_list is specified
    if values is not empty a length len_ is to be given.
    """
    if values_list:
        if not len_:
            len_ = len(values_list)
        return (data_type * int(len_))(*values_list)
    else:
        return (data_type * int(len_))()


def make_double_array(values: list[float] | None = None, len_: int = 0):
    """Makes a c_double array. The array values are 0 if no values list is specified
    - if values is not empty a length len_ is to be specified.
    """
    if isinstance(values, list):
        len_ = len(values)
        return make_generic_array(len_, values_list=values, data_type=ctypes.c_double)

    return make_generic_array(len_, data_type=ctypes.c_double)


# Initialization functions

def open_session(address: str) -> None:
    """Connect the instrument library to the device.

    Args:
        address: The VISA address of the device, e.g., 'GPIB0::16::INSTR'
    """
    status = _dll.WGFMU_openSession(make_char_pointer(address))
    if status != 0:
        pass
        # TODO: handle error here



def close_session() -> None:
    """Disconnect the instrument library from the device."""
    _dll.WGFMU_closeSession()


def initialize() -> None:
    """Reset all WGFMU channels, but keep software setup information."""
    _dll.WGFMU_initialize()


# Connect/Disconnect

def connect(channel: int) -> None:
    """Enables the specified channel and the RSU conected to the WGFMU."""
    # TODO returned is the error, e.g. -9. add error handling
    # should use get_error_summary to get the error string, not just convert the integer to string
    # because we are missing the parameter for which function the error occurred
    ret = _dll.WGFMU_connect(ctypes.c_int32(channel))

def disconnect(channel: int) -> None:
    """Disables the specified channel and the RSU conected to the WGFMU."""
    _dll.WGFMU_disconnect(ctypes.c_int32(channel))

# Error Handling


def get_error_summary() -> str:
    """Read all error messages from the error queue and return them as a single string."""
    error_size = get_error_summary_size()
    if error_size == 0:
        return ""

    c_errors = ctypes.create_string_buffer(error_size)
    _dll.WGFMU_getErrorSummary(
        ctypes.byref(c_errors),
        ctypes.byref(ctypes.c_int32(error_size)),
    )
    return c_errors.value.decode("ascii")


def get_error_summary_size() -> int:
    """Gets the size of the error summary string."""
    c_size = ctypes.c_int32()
    _dll.WGFMU_getErrorSummarySize(
        ctypes.byref(c_size),
    )
    return int(c_size.value)




# Channel Setup

def create_channel_id(slot: int, channel: int) -> int:
    """Create the channel ID needed for communication from the WGFMU hardware slot."""
    return slot * 100 + channel


def get_channel_ids() -> list[int]:
    """Get a list of all connected WGFMU channel IDs."""
    number_of_channels = get_channel_id_size()
    if number_of_channels == 0:
        return []
    c_channel_list = make_generic_array(number_of_channels, data_type=ctypes.c_int32)

    c_num = ctypes.c_int32(number_of_channels)
    _dll.WGFMU_getChannelIds(
        c_channel_list,
        ctypes.byref(c_num),
    )

    channel_ids = []
    for i in range(number_of_channels):
        channel_id = int(c_channel_list[i])
        channel_ids.append(channel_id)

    return channel_ids


def get_channel_id_size() -> int:
    """Gets the number of connected WGFMU channels."""
    c_size = ctypes.c_int32()
    _dll.WGFMU_getChannelIdSize(
        ctypes.byref(c_size),
    )
    return int(c_size.value)


class OperationMode(Enum):
    """Operation modes for the WGFMU."""
    DC = 2000
    FASTIV = 2001
    PG = 2002
    SMU = 2003


def set_operation_mode(channel: int, mode: OperationMode) -> None:
    """Set the operation mode for the specified channel."""
    _dll.WGFMU_setOperationMode(
        ctypes.c_int32(channel),
        ctypes.c_int32(mode.value),
    )



def set_measure_event(pattern: str, event: str, start_time: float, points: int, interval: float, average: float, mode: str = "averaged") -> None:
    """Defines a measurement event for a waveform pattern.

    start_time, interval, and average are rounded to the nearest multiple of 10ns.

    Args:
        pattern: The name of the waveform pattern.
        event: The name of the measurement event, can be used to add additional conditions.
        start_time: The time in seconds when the measurement event starts.
        points: The number of measurements to be taken.
        interval: The time in seconds between measurements. 10ns resolution.
        average: Averaging time in seconds. 0 = no averaging. The device will measure every 5ns and return the average. Do not exceed the interval time.
        mode: The measurement mode (e.g., voltage, current).
    """
    if start_time < 0:
        raise ValueError("start_time must be non-negative")
    if points < 1:
        raise ValueError("points must be at least 1")
    max_interval = 1.34217728
    if interval < 1e-8 or interval > max_interval:
        raise ValueError(f"interval must be between 10ns and {max_interval}s")

    max_average = 0.020971512  # 20.971512 ms
    if average < 0 or average > max_average:
        raise ValueError(f"average must be between 0 and {max_average}s")
    if average > interval:
        raise ValueError("average time must be less than interval time")

    mode_int = 12000 if mode.lower().startswith("average") else 12001  # raw

    _dll.WGFMU_setMeasureEvent(
        make_char_pointer(pattern),
        make_char_pointer(event),
        ctypes.c_double(start_time),
        ctypes.c_int32(points),
        ctypes.c_double(interval),
        ctypes.c_double(average),
        ctypes.c_int32(mode_int),
    )



# Pattern Creation


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


def get_pattern_force_value_size(pattern: str) -> int:
    """Gets the size of the force value array for the given pattern."""
    c_size = ctypes.c_int32()
    _dll.WGFMU_getPatternForceValueSize(
        make_char_pointer(pattern),
        ctypes.byref(c_size),
    )
    return int(c_size.value)


def get_pattern_force_values(pattern: str, index: int = 0, length: int = 0) -> tuple[list[float], list[float]]:
    """Gets the time and force value arrays for the given pattern."""
    if length == 0:
        length = get_pattern_force_value_size(pattern) - index
    if length <= 0:
        return [], []

    c_times = make_double_array(len_=length)
    c_values = make_double_array(len_=length)

    _dll.WGFMU_getPatternForceValues(
        make_char_pointer(pattern_name),
        ctypes.c_int32(index),
        ctypes.byref(ctypes.c_int32(length)),
        c_times,
        c_values,
    )

    times = [float(c_times[i]) for i in range(length)]
    values = [float(c_values[i]) for i in range(length)]
    return times, values


def add_sequence(channel: int, pattern_name: str, count: int) -> None:
    """Create a sequence of count * pattern_name and append it to the last point of the channels sequence."""
    max_count = 1099511627776  # 2^40
    if count < 1 or count > max_count:
        raise ValueError(f"Invalid count: {count}. Count must be between 1 and {max_count}.")

    _dll.WGFMU_addSequence(
        ctypes.c_int32(channel),
        make_char_pointer(pattern_name),
        ctypes.c_double(count),
    )


def clear() -> None:
    """Clears all waveform patterns and sequences."""
    _dll.WGFMU_clear()




# Measurement and Execution


def set_timeout(timeout_ms: int) -> None:
    """Set the communication timeout in milliseconds."""
    _dll.WGFMU_setTimeout(ctypes.c_int32(timeout_ms))


def execute() -> None:
    """Runs the seuencer of all enabled WGFMU channels in Fast IV or PG mode.

    Calls set_operation_mode, set_force_voltage_range, set_measure_current_range, set_measure_voltage_range, set_measure_mode.
    """
    _dll.WGFMU_execute()


def wait_until_completed() -> None:
    """Waits until all connected WGFMU channels in the Fast IV mode or the PG mode are in the ready to read data status."""
    _dll.WGFMU_waitUntilCompleted()


class ChannelStatus(Enum):
    """Channel status codes for the WGFMU."""
    COMPLETED = 10000  # sequences completed and data ready to read
    DONE = 10001  # sequences completed
    RUNNING = 10002
    ABORT_COMPLETED = 10003  # sequences aborted and data ready to read
    ABORTED = 10004  # sequences aborted
    ILLEGAL = 10005  # illegal state
    IDLE = 10006  # idle state


def get_channel_status(channel: int) -> tuple[ChannelStatus, int, int]:
    """Gets the status of the specified channel.

    Returns:
        status: The current status of the channel (e.g., idle, running).
        elapsed_time: The elapsed time in seconds since the channel started operation.
        estimated_total_time: The estimated total time in seconds for the channel's operation to complete.
    """
    c_status = ctypes.c_int32()
    c_elapsed_time = ctypes.c_double()
    c_estimated_total_time = ctypes.c_double()
    _dll.WGFMU_getChannelStatus(
        ctypes.c_int32(channel),
        ctypes.byref(c_status),
        ctypes.byref(c_elapsed_time),
        ctypes.byref(c_estimated_total_time),
    )

    # handle status
    status_int = int(c_status.value)
    try:
        status = ChannelStatus(status_int)
    except ValueError:
        status = ChannelStatus.ILLEGAL

    return status, int(c_elapsed_time.value), int(c_estimated_total_time.value)


def is_measure_enabled(channel: int) -> bool:
    """Check if measurement is enabled for the specified channel."""
    c_enabled = ctypes.c_int32()
    _dll.WGFMU_isMeasureEnabled(
        ctypes.c_int32(channel),
        ctypes.byref(c_enabled),
    )
    status = int(c_enabled.value)
    return status == 7001  # 7000 = disabled, 7001 = enabled


def get_measure_value_size(channel: int) -> tuple[int, int]:
    """Get number of completed measurement points and total number of measurement points."""
    c_completed_points = ctypes.c_int32()
    c_total_points = ctypes.c_int32()
    _dll.WGFMU_getMeasureValueSize(
        ctypes.c_int32(channel),
        ctypes.byref(c_completed_points),
        ctypes.byref(c_total_points),
    )
    return int(c_completed_points.value), int(c_total_points.value)


def get_measure_value(channel: int, index: int) -> tuple[float, float]:
    """Returns measurement data (time and value) for the specified point."""
    c_time = ctypes.c_double()
    c_value = ctypes.c_double()
    _dll.WGFMU_getMeasureValue(
        ctypes.c_int32(channel),
        ctypes.c_int32(index),
        ctypes.byref(c_time),
        ctypes.byref(c_value),
    )
    return float(c_time.value), float(c_value.value)


def get_measure_values(channel: int, start_index: int, count: int) -> tuple[list[float], list[float]]:
    """Returns measurement data (time and value) for multiple points."""
    if count < 1:
        raise ValueError("count must be at least 1")
    if start_index < 0:
        raise ValueError("start_index must be non-negative")

    c_times = make_double_array(len_=count)
    c_values = make_double_array(len_=count)

    # _dll.WGFMU_getMeasureValues.argtypes = [
    #     ctypes.c_int32, ctypes.c_int32, ctypes.c_int32,
    #     ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_double)
    # ]
    time.sleep(5)

    status = _dll.WGFMU_getMeasureValues(
        ctypes.c_int32(channel),
        ctypes.c_int32(start_index),
        ctypes.byref(ctypes.c_int32(count)),
        # c_times,
        # c_values,
        ctypes.byref(c_times),
        ctypes.byref(c_values),
    )

    # if the DLL returns an error code, surface it
    if isinstance(status, int) and status != 0:
        raise OSError(f"WGFMU_getMeasureValues returned error code {status}")

    times = [float(c_times[i]) for i in range(count)]
    values = [float(c_values[i]) for i in range(count)]

    return times, values



if __name__ == "__main__":
    CHANNEL = 101
    # Example 1
    # Offline commands
    load_dll()
    clear()

    # create pattern
    pattern_name = "pulse"
    create_pattern(pattern_name, 0.0)

    # Rectangular Pulse
    add_vector(pattern_name, 0.0001, 1.0)
    add_vector(pattern_name, 0.0004, 1.0)
    add_vector(pattern_name, 0.0001, 0)
    add_vector(pattern_name, 0.0004, 0)

    # Repeat 10 times
    add_sequence(CHANNEL, pattern_name, 10)
    print("Force values:", get_pattern_force_values(pattern_name))

    # Online commands
    open_session("GPIB0::16::INSTR")
    initialize()
    set_operation_mode(CHANNEL, OperationMode.FASTIV)
    connect(CHANNEL)

    set_measure_event(
        pattern_name,
        "evt",
        0,
        100,
        0.00001,
        0,
        "average"
    )

    # status = get_channel_status(CHANNEL)
    # print(status)
    # print(f"Measure enabled: {is_measure_enabled(CHANNEL)}")

    execute()

    wait_until_completed()

    completed_points, total_points = get_measure_value_size(CHANNEL)
    print(f"Completed points: {completed_points}, Total points: {total_points}")

    # readout data
    # timestamps, measured_values = [], []
    # for index in range(completed_points):
    #     timestamp, measured_value = get_measure_value(CHANNEL, index)
    #     timestamps.append(timestamp)
    #     measured_values.append(measured_value)
    #     # print(f"Point {index}: Time = {timestamp:.8f} s, Value = {measured_value:.6f} V")
    #     # if index > 3:
    #     #     break
    # print(len(timestamps), len(measured_values))
    print(get_error_summary())
    timestamps, measured_values = get_measure_values(CHANNEL, 0, 5)
    for i in range(4):
        print(f"Point {i}: Time = {timestamps[i]:.8f} s, Value = {measured_values[i]:.6f} V")
    print(get_error_summary())

    initialize()
    disconnect(CHANNEL)
    close_session()
