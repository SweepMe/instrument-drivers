import ctypes as c

from .error_codes import ERROR_CODES

_dll_path = r"C:\s4200\sys\bin\lptlib.dll"
_dll = None

DEBUG_MODE = True

"""
Arguments are used as defined in the Keithley LPT lib documentation.
However, if they are camel case, they have been pythonized, by writing them
lower cases and inserting underscores, e.g. 'StartPercent' becomes 'start_percent'.
In case the argument is 'range', it is changed to 'range_'
"""


# ### UTILITY FUNCTIONS


class K4200Error(Exception):
    """wrapped error."""


def make_char_pointer(string: str):
    """Make a char pointer from a python string
    to be used without c.byref.
    """
    bytes_ = string.encode("ascii")
    return c.c_char_p(bytes_)


def make_double_array(len_: int, values: list | None = None):
    """Makes a c double array who's values can be set as v[0] = 1 etc
    values = [] makes an empty array of length len_
    if values is not empty please set len_ appropriately.
    """
    if values:
        return (c.c_double * int(len_))(*values)
    else:
        return (c.c_double * int(len_))()


def make_double_array_pointer(len_: int, values: list | None = None):
    """Make an array pointer
    values = [] makes an empty array pointer.
    """
    array = (c.c_double * int(len_))(*values) if values else (c.c_double * int(len_))()
    return c.cast(array, c.POINTER(c.c_double))


def make_int_array_pointer(len_: int, values: list | None = None):
    """Make an array pointer
    values = [] makes an empty array pointer.
    """
    array = (c.c_int32 * int(len_))(*values) if values else (c.c_int32 * int(len_))()
    return c.cast(array, c.POINTER(c.c_int32))


def create_string_buffer(string: str, size=128):
    """Make a char bufferr from a python string
    to be used with c.byref.
    """
    return c.create_string_buffer(string.encode("ascii"), size=size)


def set_library_path(path):
    """Change the library default path."""
    global _dll_path
    _dll_path = path


def get_error(error_code: c.c_int32, *args):
    """Get the error codes if there was an error
    There is some unclear Keithley magic with filling the place holders available for some
    error codes.
    """
    error_code = int(error_code)
    if error_code == 0:
        return

    if DEBUG_MODE:
        print("error #: ", error_code)

    error_string = ERROR_CODES[error_code]

    if DEBUG_MODE:
        print("error message: ", error_string)

    place_holders = error_string.count("%")
    if len(args) == place_holders:
        raise K4200Error(error_string % args)
    else:
        raise K4200Error(error_string)


def initialize():
    """Load the library with ctypes."""
    global _dll
    _dll = c.WinDLL(_dll_path)

    _dll.tstsel.argtypes = (c.c_int32,)

    _dll.getinstid.argtypes = (c.POINTER(c.c_char), c.POINTER(c.c_int32))
    _dll.getinstid.restype = c.c_int32



# ### LIBRARY FUNCTIONS


def tstsel(id_: int):
    """Select test station."""
    err = _dll.tstsel(c.c_int32(id_))  # equiv to c_long
    get_error(err)


def tstdsl():
    """Deselect test station."""
    err = _dll.tstdsl()
    get_error(err)


def devint():
    """Reset all active instruments in the system to their default states."""
    err = _dll.devint()
    get_error(err)


def getinstid(id_string: str):
    """Return the id for a desired card."""
    # option 1
    chars_p = make_char_pointer(id_string)
    # option 2
    c_instr_id = c.c_int32()
    err = _dll.getinstid(chars_p, c.byref(c_instr_id))
    get_error(err)
    return int(c_instr_id.value)


def setmode(instr_id: int, param: int, value):
    err = _dll.setmode(c.c_int32(instr_id), c.c_long(param), c.c_double(value))
    get_error(err)


def setauto(instr_id: int):
    """re-enable autoranging and cancel any previous rangeX command for the specified instrument."""
    err = _dll.setauto(c.c_int32(instr_id))
    get_error(err)


def limitv(instr_id: int, limit_val: float):
    """Set current limit."""
    err = _dll.limitv(c.c_int32(instr_id), c.c_double(limit_val))
    get_error(err)


def limiti(instr_id: int, limit_val: float):
    """Set voltage limit."""
    err = _dll.limiti(c.c_int32(instr_id), c.c_double(limit_val))
    get_error(err)


def rangev(instr_id: int, range_: float):
    """Select a voltage range and prevent the selected instrument from autoranging."""
    err = _dll.rangev(c.c_int32(instr_id), c.c_double(range_))
    get_error(err)


def rangei(instr_id: int, range_: float):
    """Select a current range and prevent the selected instrument from autoranging."""
    err = _dll.rangei(c.c_int32(instr_id), c.c_double(range_))
    get_error(err)


def lorangev(instr_id: int, index: float):
    """Define the bottom voltage autorange limit."""
    err = _dll.lorangev(c.c_int32(instr_id), c.c_double(index))
    get_error(err)


def lorangei(instr_id: int, index: float):
    """Define the bottom current autorange limit."""
    err = _dll.lorangei(c.c_int32(instr_id), c.c_double(index))
    get_error(err)


def forcev(instr_id: int, value: float):
    """Program a sourcing instrument to generate a voltage at a specific level."""
    err = _dll.forcev(c.c_int32(instr_id), c.c_double(value))
    get_error(err)


def forcei(instr_id: int, value: float):
    """Program a sourcing instrument to generate a current at a specific level."""
    err = _dll.forcei(c.c_int32(instr_id), c.c_double(value))
    get_error(err)


def intgv(instr_id: int) -> float:
    """Measure current."""
    meas_value = c.c_double()
    err = _dll.intgv(c.c_int32(instr_id), c.byref(meas_value))
    get_error(err)
    return float(meas_value.value)


def intgi(instr_id: int) -> float:
    """Measure current."""
    meas_value = c.c_double()
    err = _dll.intgi(c.c_int32(instr_id), c.byref(meas_value))
    get_error(err)
    return float(meas_value.value)


def measi(instr_id):
    c_instr_id = c.c_int32(instr_id)
    meas_result = c.c_double()
    err = _dll.measi(c_instr_id, c.byref(meas_result))
    get_error(err)
    return float(meas_result.value)


def measv(instr_id):
    c_instr_id = c.c_int32(instr_id)
    meas_result = c.c_double()
    err = _dll.measv(c_instr_id, c.byref(meas_result))
    get_error(err)
    return float(meas_result.value)


def meast(instr_id):
    c_instr_id = c.c_int32(instr_id)
    meas_result = c.c_double()
    err = _dll.meast(c_instr_id, c.byref(meas_result))
    get_error(err)
    return float(meas_result.value)


def measf(instr_id):
    c_instr_id = c.c_int32(instr_id)
    meas_result = c.c_double()
    err = _dll.measf(c_instr_id, c.byref(meas_result))
    get_error(err)
    return float(meas_result.value)


def measz(instr_id):
    c_instr_id = c.c_int32(instr_id)
    meas_result = c.c_double()
    err = _dll.measz(c_instr_id, c.byref(meas_result))
    get_error(err)
    return float(meas_result.value)


# ### PG2


def arb_array(instr_id: int, chan: int, time_per_point: float, voltages: list, name: str):
    """Define a full arb waveform and name the file."""
    voltages_array_p = make_double_array_pointer(len(voltages), voltages)
    len_c = c.c_int32(len(voltages))
    c_name_p = make_char_pointer(name)

    err = _dll.arb_array(
        c.c_int32(instr_id), c.c_int32(chan), c.c_double(time_per_point), len_c, voltages_array_p, c_name_p,
    )
    get_error(err)


def arb_file(instr_id: int, chan: int, name):
    """Load a waveform from an existing full arb waveform file."""
    c_name_p = make_char_pointer(name)

    err = _dll.arb_file(c.c_int32(instr_id), c.c_int32(chan), c_name_p)
    get_error(err)


def getstatus(instr_id: int, parameter: int):
    result = c.c_double()

    err = _dll.getstatus(c.c_int32(instr_id), c.c_int32(parameter), c.byref(result))
    get_error(err)

    return float(result.value)


def pg2_init(instr_id: int, mode_id: int):
    """Reset the pulse card to specified pulse mode & mode defaults
    mode ids: 0 standard, 1: segment arb 2: full arb.
    """
    err = _dll.pg2_init(c.c_int32(instr_id), c.c_int32(mode_id))
    get_error(err)


def pulse_burst_count(instr_id: int, chan: int, count: int):
    """Set the number of pulses to output during a burst sequence."""
    err = _dll.pulse_burst_count(c.c_int32(instr_id), c.c_int32(chan), c.c_uint32(count))  # manual wants unsigned!
    get_error(err)


def pulse_current_limit(instr_id: int, chan: int, ilimit: float):
    """Set the current limit for the pulse card."""
    err = _dll.pulse_current_limit(c.c_int32(instr_id), c.c_int32(chan), c.c_double(ilimit))
    get_error(err)


def pulse_dc_output(instr_id: int, chan: int, dcvalue: float):
    """Select dc output mode and set voltage level
    WARNING: this sets the channel voltage value when it is turned on (using pulse_output).
     If the output is already enabled, the voltage level change is immediate, before the pulsing is
    started with a pulse_trig command.
    """
    err = _dll.pulse_dc_output(c.c_int32(instr_id), c.c_int32(chan), c.c_double(dcvalue))
    get_error(err)


def pulse_delay(instr_id: int, chan: int, delay: float):
    """Set s the delay time from the trigger to when the pulse output starts."""
    err = _dll.pulse_delay(c.c_int32(instr_id), c.c_int32(chan), c.c_double(delay))
    get_error(err)


def pulse_fall(instr_id: int, chan: int, fallt: float):
    """Set the fall transition time for the pulse output."""
    err = _dll.pulse_fall(c.c_int32(instr_id), c.c_int32(chan), c.c_double(fallt))
    get_error(err)


def pulse_halt(instr_id: int):
    """Stop all pulse output from the pulse card."""
    err = _dll.pulse_halt(c.c_int32(instr_id))
    get_error(err)


def pulse_init(instr_id: int):
    """Reset card to defaults of currently selected pulse mode."""
    err = _dll.pulse_init(c.c_int32(instr_id))
    get_error(err)


def pulse_load(instr_id: int, chan: int, load: float):
    """Sets the output impedance for the DUT load."""
    err = _dll.pulse_load(c.c_int32(instr_id), c.c_int32(chan), c.c_double(load))

    get_error(err)


def pulse_output(instr_id: int, chan: int, out_state: bool):
    """Sets pulse card output to on or off."""
    err = _dll.pulse_output(c.c_int32(instr_id), c.c_int32(chan), c.c_int32(out_state))
    get_error(err)


def pulse_output_mode(instr_id: int, chan: int, mode: int):
    """Set the output mode to NORMAL (0) or COMPLEMENT (1)
    For complement the high and low levels are swapped.
    """
    err = _dll.pulse_output_mode(c.c_int32(instr_id), c.c_int32(chan), c.c_int32(mode))
    get_error(err)


def pulse_period(instr_id: int, chan: int, period: float):
    """Pulse period in s."""
    err = _dll.pulse_period(c.c_int32(instr_id), c.c_double(period))
    get_error(err)


def pulse_range(instr_id: int, chan: int, range_: float):
    """Sets the voltage range for low v (fast speed)/ high v (low speed)
    v_range = 5 or 20.
    """
    err = _dll.pulse_range(c.c_int32(instr_id), c.c_int32(chan), c.c_double(range_))
    get_error(err)


def pulse_rise(instr_id: int, chan: int, riset: float):
    """Set the rise transition time for the pulse."""
    err = _dll.pulse_rise(c.c_int32(instr_id), c.c_int32(chan), c.c_double(riset))

    get_error(err)


def pulse_ssrc(instr_id: int, chan: int, state: bool, ctrl: int):
    """Set the high-endurance output relay (HEOR) for the PGU channel.
    control_mode (ctrl): 0 -> auto, 1 -> manual (state), 3 -> trig out.
    """
    err = _dll.pulse_ssrc(
        c.c_int32(instr_id),
        c.c_int32(chan),
        c.c_int32(state),
        c.c_int32(ctrl),
    )
    get_error(err)


def pulse_trig(instr_id: int, mode: int):
    """Set the trigger mode for the pulse output."""
    err = _dll.pulse_trig(
        c.c_int32(instr_id),
        c.c_int32(mode),
    )
    get_error(err)


def pulse_trig_output(instr_id: int, state: bool):
    """Set the output trigger on or off."""
    err = _dll.pulse_trig_output(
        c.c_int32(instr_id),
        c.c_int32(state),
    )
    get_error(err)


def pulse_trig_polarity(instr_id: int, polarity: int):
    """Set the polarity of the outpiut trig card."""
    err = _dll.pulse_trig_polarity(
        c.c_int32(instr_id),
        c.c_int32(polarity),
    )
    get_error(err)


def pulse_trig_source(instr_id: int, source: int):
    """Set trigger source
    0: software
    1: ext rising (initial only)
    2: ext falling (initial only)
    3: ext rising (per pulse)
    4: ext falling (per pulse)
    5: internal trig bus.
    """
    err = _dll.pulse_trig_source(
        c.c_int32(instr_id),
        c.c_int32(source),
    )
    get_error(err)


def pulse_vhigh(instr_id: int, chan: int, level: float):
    """Set the pulse voltage high level
    WARNING: this sets the channel voltage value when it is turned on (using pulse_output).
     If the output is already enabled, the voltage level change is immediate, before the pulsing is
    started with a pulse_trig command.
    """
    err = _dll.pulse_vhigh(c.c_int32(instr_id), c.c_int32(chan), c.c_double(level))
    get_error(err)


def pulse_vlow(instr_id: int, chan: int, level: float):
    """Set the pulse voltage low level
    WARNING: this sets the channel voltage value when it is turned on (using pulse_output).
     If the output is already enabled, the voltage level change is immediate, before the pulsing is
    started with a pulse_trig command.
    """
    err = _dll.pulse_vlow(c.c_int32(instr_id), c.c_int32(chan), c.c_double(level))
    get_error(err)


def pulse_width(instr_id: int, chan: int, width: float):
    """Aset the output pulse width in s."""
    err = _dll.pulse_width(c.c_int32(instr_id), c.c_int32(chan), c.c_double(width))
    get_error(err)


def seg_arb_define(
    instr_id: int,
    chan: int,
    num_segments: int,
    start_values: list,
    stop_values: list,
    time_values: list,
    trig_values: list,
    outp_relay_values: list,
):
    start_values_p = make_double_array_pointer(start_values)
    stop_values_p = make_double_array_pointer(stop_values)
    time_values_p = make_double_array_pointer(time_values)
    trig_values_p = make_int_array_pointer(trig_values)
    outp_relay_values_p = make_int_array_pointer(outp_relay_values)

    err = _dll.seg_arb_define(
        c.c_int32(instr_id),
        c.c_int32(chan),
        c.c_int32(num_segments),
        start_values_p,
        stop_values_p,
        time_values_p,
        trig_values_p,
        outp_relay_values_p,
    )
    get_error(err)


def seg_arb_file(instr_id: int, chan: int, waveform_fname: str):
    fname_c_p = make_char_pointer(waveform_fname)
    err = _dll.seg_arb_file(c.c_int32(instr_id), c.c_int32(chan), fname_c_p)
    get_error(err)


# ### PULSE


def rpm_config(instr_id: int, chan: int, modifier: int, modify_value: int):
    """Send switching commands to the 4225-RPM. Modifier is KI_RPM_PATHWAY."""
    err = _dll.rpm_config(c.c_int32(instr_id), c.c_int32(chan), c.c_int32(modifier), c.c_int32(modify_value))
    get_error(err)


def dev_abort():
    """Abort a pulse started with pulse exec (non-blocking). NB no card ID."""
    err = _dll.dev_abort()
    get_error(err)


def pulse_exec(pulse_mode: bool) -> int:
    """Execute a pulse in basic/advanced mode."""
    err = _dll.pulse_exec(c.c_int32(pulse_mode))
    get_error(err)


def pulse_exec_status() -> tuple[int, float]:
    """To check the pulse status during a while pulse exec loop."""
    elapsed_time = c.c_double()
    status = _dll.pulse_exec_status(c.byref(elapsed_time))
    return int(status), float(elapsed_time.value)


def pulse_fetch(instr_id: int, chan: int, start_index: int, stop_index: int) -> tuple[dict, float, float, float]:
    """This command retrieves enabled test data and temporarily stores it in the data buffer.

    When using pulse_fetch to retrieve data, you need to pause the program to allow time for the
    buffer to fill. You can use the sleep command to pause for a specified time, or you can use the
    pulse_exec_status command in a while loop to wait until the test is completed.
    """
    status = c.c_int32()

    # THESE MIGH NEED TO BE ARRAYS!
    # make_double_array + by_ref or make_double_array_pointer and no by ref

    buffer_size = stop_index - start_index

    meas_v = make_double_array(buffer_size)
    meas_i = make_double_array(buffer_size)
    timestamp = make_double_array(buffer_size)

    err = _dll.pulse_fetch(
        c.c_int32(instr_id),
        c.c_int32(chan),
        c.c_int32(start_index),
        c.c_int32(stop_index),
        c.byref(meas_v),
        c.byref(meas_i),
        c.byref(timestamp),
        c.byref(status),
    )
    get_error(err)

    status = int(status.value)

    if DEBUG_MODE:
        print("Status", status)

    meas_v = [meas_v[i] for i in range(buffer_size)]
    meas_i = [meas_i[i] for i in range(buffer_size)]
    timestamp = [timestamp[i] for i in range(buffer_size)]

    status = decode_pulse_status(status)
    # now needs to be decoded from binary into a list of statuses (13 long)

    return status, timestamp, meas_v, meas_i


def pulse_meas_wfm(
    instr_id: int,
    chan: int,
    acquire_type: bool,
    acquire_meas_V: bool,
    acquire_meas_I: bool,
    aquire_time_stamp: bool,
    load_line_effect_comp: bool,
):
    "Configures waveform measurements."
    acquire_type = c.c_int32(acquire_type)
    acquire_meas_V = c.c_int32(acquire_meas_V)
    acquire_meas_I = c.c_int32(acquire_meas_I)
    aquire_time_stamp = c.c_int32(aquire_time_stamp)
    load_line_effect_comp = c.c_int32(load_line_effect_comp)

    err = _dll.pulse_meas_wfm(
        c.c_int32(instr_id),
        c.c_int32(chan),
        acquire_type,
        acquire_meas_V,
        acquire_meas_I,
        aquire_time_stamp,
        load_line_effect_comp,
    )
    get_error(err)


def pulse_ranges(
    instr_id: int,
    chan: int,
    v_src_range: float,
    v_range_type: int,
    v_range: float,
    i_range_type: int,
    i_range: float,
):
    """Set the voltage pulse range and voltage/current measure ranges
    - Range types: Auto 0, Limited auto: 1, Fixed: 2
    - V src ranges: 5 or 20 (into 50 Ω), 10 or 40 (into 1 MΩ)
    - current ranges available depend on the source range and whether the system includes a
    4225-RPM. see manual.
    """
    v_src_range = c.c_double(v_src_range) if v_src_range else None
    v_range = c.c_double(v_range) if v_range else None
    i_range = c.c_double(i_range) if i_range else None

    err = _dll.pulse_ranges(
        c.c_int32(instr_id),
        c.c_int32(chan),
        v_src_range,
        c.c_int32(v_range_type),
        v_range,
        c.c_int32(i_range_type),
        i_range,
    )
    get_error(err)


def pulse_chan_status(instr_id: int, chan: int) -> int:
    """Determine how many readings are stored in the data buffer."""
    buffersize = c.c_int32()
    err = _dll.pulse_chan_status(c.c_int32(instr_id), c.c_int32(chan), c.byref(buffersize))
    get_error(err)

    return int(buffersize.value)


def pulse_conncomp(instr_id: int, chan: int, comp_type: int, comp: int):
    """enable/disable compensation
    - comp_type : 1 short, 2 delay
    - comp: 0: Disabled, 1: default, 2: default with PMU and RPM 3: custom.
    """
    err = _dll.pulse_conncomp(c.c_int32(instr_id), c.c_int32(chan), c.c_int32(comp_type), c.c_int32(comp))
    get_error(err)


def pulse_float(instr_id: int, chan: int, state: bool):
    """Set the state of the floating relay for the given pulse instrument."""
    err = _dll.pulse_float(c.c_int32(instr_id), c.c_int32(chan), c.c_int32(state))
    get_error(err)


def pulse_limits(instr_id: int, chan: int, v_limit: float, i_limit: float, power_limit: float):
    """Sets the pulse measure I/V limits."""
    v_limit = c.c_double(v_limit) if v_limit else None
    i_limit = c.c_double(i_limit) if i_limit else None
    power_limit = c.c_double(power_limit) if power_limit else None

    err = _dll.pulse_limits(c.c_int32(instr_id), c.c_int32(chan), v_limit, i_limit, power_limit)
    get_error(err)


def pulse_meas_sm(
    instr_id: int,
    chan: int,
    acquire_type: int,
    acquire_meas_V_amp: bool,
    acquire_meas_V_base: bool,
    acquire_meas_I_amp: bool,
    aquire_meas_I_base: bool,
    aquire_time_stamp: bool,
    load_line_effect_comp: bool,
):
    """Configures spot mean measurement. See lpt docu.
    Params:
        acquire_type: 0=discrete, 1=average.
    """
    acquire_type = c.c_int32(acquire_type)
    chan = c.c_int32(chan)
    acquire_meas_V_amp = c.c_int32(acquire_meas_V_amp)
    acquire_meas_V_base = c.c_int32(acquire_meas_V_base)
    acquire_meas_I_amp = c.c_int32(acquire_meas_I_amp)
    aquire_meas_I_base = c.c_int32(aquire_meas_I_base)
    aquire_time_stamp = c.c_int32(aquire_time_stamp)
    load_line_effect_comp = c.c_int32(load_line_effect_comp)

    err = _dll.pulse_meas_sm(
        c.c_int32(instr_id),
        chan,
        acquire_type,
        acquire_meas_V_amp,
        acquire_meas_V_base,
        acquire_meas_I_amp,
        aquire_meas_I_base,
        aquire_time_stamp,
        load_line_effect_comp,
    )
    get_error(err)


def pulse_meas_timing(instr_id: int, chan: int, start_percent: float, stop_percent: float, num_pulses: int):
    """Set the measurements windows. see lpt manual."""
    err = _dll.pulse_meas_timing(
        c.c_int32(instr_id), c.c_int32(chan), c.c_double(start_percent), c.c_double(stop_percent), c.c_int32(num_pulses),
    )
    get_error(err)


def pulse_meas_rt(
    instr_id: int, chan: int, v_meas_name: str, i_meas_name: str, timestamp_meas_name: str, status_meas_name: str,
):
    """Configures channel to return pulse source and measure data in pseudo real time.
    As measurements are performed, the data is automatically placed in the Clarius Analyze sheet.
    """
    v_meas_name = make_char_pointer(v_meas_name)
    i_meas_name = make_char_pointer(i_meas_name)
    timestamp_meas_name = make_char_pointer(timestamp_meas_name)
    status_meas_name = make_char_pointer(status_meas_name)

    err = _dll.pulse_meas_rt(
        c.c_int32(instr_id), c.c_int32(chan), v_meas_name, i_meas_name, timestamp_meas_name, status_meas_name,
    )
    get_error(err)


def pulse_sample_rate(instr_id: int, sample_rate: float):
    """Set the measurement sample rate."""
    err = _dll.pulse_sample_rate(c.c_int32(instr_id), c.c_double(sample_rate))
    get_error(err)


def pulse_remove(instr_id: int, chan: int, voltage_to_output: float, output_relay_state: bool):
    """Remove a pulse channel from the test."""
    err = _dll.pulse_remove(
        c.c_int32(instr_id), c.c_int32(chan), c.c_double(voltage_to_output), c.c_int32(output_relay_state),
    )
    get_error(err)


def pulse_source_timing(instr_id: int, chan: int, period: float, delay: float, width: float, rise: float, fall: float):
    """Set the pulse period, width, fall time, rise time and delay time."""
    period = c.c_double(period) if period else None
    delay = c.c_double(delay) if delay else None
    width = c.c_double(width) if width else None
    rise = c.c_double(rise) if rise else None
    fall = c.c_double(fall) if fall else None

    err = _dll.pulse_source_timing(c.c_int32(instr_id), c.c_int32(chan), period, delay, width, rise, fall)
    get_error(err)


def pulse_step_linear(instr_id: int, chan: int, step_type: int, start: float, stop: float, step: float):
    """Configure the pulse stepping type
    -Step type:
        PULSE_AMPLITUDE_SP: Sweeps pulse voltage amplitude
        PULSE_BASE_SP: Sweeps base voltage level
        PULSE_DC_SP: Sweeps dc voltage level
        PULSE_PERIOD_SP: Sweeps pulse period
        PULSE_RISE_SP: Sweeps pulse rise time
        PULSE_FALL_SP: Sweeps pulse fall time
        PULSE_WIDTH_SP: Sweeps full-width half-maximum pulse width
        PULSE_DUAL_BASE_SP: Dual sweeps base voltage level
        PULSE_DUAL_AMPLITUDE_SP: Dual sweeps pulse voltage amplitude
        PULSE_DUAL_DC_SP: Dual sweeps dc voltage level.
    """
    err = _dll.pulse_step_linear(
        c.c_int32(instr_id),
        c.c_int32(chan),
        c.c_int32(step_type),
        c.c_double(start),
        c.c_double(stop),
        c.c_double(step),
    )
    get_error(err)


def pulse_train(instr_id: int, chan: int, v_base: float, v_amplitude: float):
    """ """
    v_base = c.c_double(v_base) if v_base else None
    v_amplitude = c.c_double(v_amplitude) if v_amplitude else None

    err = _dll.pulse_train(c.c_int32(instr_id), c.c_int32(chan))
    get_error(err)


def pulse_sweep_linear(instr_id: int, chan: int, sweep_type: int, start: float, stop: float, step: float):
    """Configure sweeping type."""
    err = _dll.pulse_sweep_linear(
        c.c_int32(instr_id),
        c.c_int32(chan),
        c.c_int32(sweep_type),
        c.c_double(start),
        c.c_double(stop),
        c.c_double(step),
    )
    get_error(err)


def seg_arb_sequence(
    instr_id: int,
    chan: int,
    sequence_id: int,
    num_segments,
    start_voltages: list[float],
    stop_voltages: list[float],
    times: list[float],
    trigger_values: list[bool],
    SSRs: list[int],
    meas_types: list[float],
    meas_starts: list[float],
    meas_stops: list[float],
):
    """Define the parameters for a segment arbitrary waveform pulse-measure sequence
    - sequence_id: unique id to identify sequence
    - see docu.
    """
    # NB: YOU MIGHT NEED TO TRY WITHOUT POINTERS

    sequence_id = c.c_int32(sequence_id)
    num_segments = c.c_int32(num_segments)
    start_voltages = make_double_array_pointer(len(start_voltages), start_voltages)
    stop_voltages = make_double_array_pointer(len(stop_voltages), stop_voltages)
    times = make_double_array_pointer(len(times), times)
    trigger_values = make_int_array_pointer(len(trigger_values), trigger_values)
    SSRs = make_int_array_pointer(len(SSRs), SSRs)
    meas_types = make_double_array_pointer(len(meas_types), meas_types)
    meas_starts = make_double_array_pointer(len(meas_starts), meas_starts)
    meas_stops = make_double_array_pointer(len(meas_stops), meas_stops)

    err = _dll.seg_arb_sequence(
        c.c_int32(instr_id),
        c.c_int32(chan),
        sequence_id,
        num_segments,
        start_voltages,
        stop_voltages,
        times,
        trigger_values,
        SSRs,
        meas_types,
        meas_starts,
        meas_stops,
    )
    get_error(err)


def seg_arb_waveform(
    instr_id: int, chan: int, num_sequences: int, sequence_ids: list[int], seq_loop_counts: list[float],
):
    """Create a waveform from segments."""
    sequence_ids = make_int_array_pointer(len(sequence_ids), sequence_ids)
    seq_loop_counts = make_double_array_pointer(len(seq_loop_counts), seq_loop_counts)

    err = _dll.seg_arb_waveform(
        c.c_int32(instr_id), c.c_int32(chan), c.c_int32(num_sequences), sequence_ids, seq_loop_counts,
    )
    get_error(err)


def decode_pulse_status(status_bits: int) -> dict:
    """Decode the pulse status, see Status-code bit map for pulse_fetch in LPT manual."""
    bit_lengths = {
        "channel": 2,
        "voltage range": 2,
        "current range": 4,
        "V meas overflow": 2,
        "I meas overflow": 2,
        "thresholds": 4,
        "Measurement type": 4,
        "reserved 1": 4,
        "RPM mode": 4,
        "LLEC status": 1,
        "LLEC enabled": 1,
        "sweep skipped": 1,
        "reserved 2": 1,
    }
    status = {k: None for k in bit_lengths}
    shift = 0
    for cat, bit_len in bit_lengths.items():
        mask = int("1" * bit_len, 2)  # number of bits to select
        status[cat] = status_bits >> shift & mask
        shift += bit_len

    current_ranges = {
        0: "100 nA (RPM only)",
        1: "1 µA (RPM only)",
        2: "10 µA (RPM only)",
        3: "100 µA",
        4: "1 mA (RPM only)",
        5: "10 mA",
        6: "200 mA",
        7: "800 mA",
    }
    over_flows = {
        0: "No overflow",
        1: "Negative overflow",
        2: "Positive overflow",
    }
    limits = {
        0: "None",
        1: "Source compliance",
        2: "Current threshold reached or surpassed",
        4: "Voltage threshold reached or surpassed",
        8: "Power threshold reached or surpassed",
    }
    meas_types = {0: "?", 1: "Spot", 2: "Waveform", 3: "?"}

    status["current range"] = current_ranges[status["current range"]]
    status["V meas overflow"] = over_flows[status["V meas overflow"]]
    status["I meas overflow"] = over_flows[status["I meas overflow"]]
    status["thresholds"] = limits[status["thresholds"]]
    status["Measurement type"] = meas_types[status["Measurement type"]]

    return status
