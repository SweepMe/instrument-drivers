# The MIT License (MIT)
#
# Copyright (c) 2016 Charles Armstrap <charles@armstrap.org>
# If you like this library, consider donating to: https://bit.ly/armstrap-opensource-dev
# Anything helps.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
from ctypes import c_bool, c_size_t, c_double, c_uint8, c_uint16, c_int32, c_uint32, c_int64, c_uint64, c_char_p, c_wchar, c_wchar_p, Structure, c_int, cdll, byref
from enum import IntEnum

NIVB_LIBRARY_VERSION = 302039040 # 18.0.0f0, is found in nivirtualbench.h

if sys.maxsize > 2**32:
    c_sysint = c_int64
else:
    c_sysint = c_int


class Language(IntEnum):
    CURRENT_THREAD_LOCALE = 0
    ENGLISH = 1033
    FRENCH = 1036
    GERMAN = 1031
    JAPANESE = 1041
    KOREAN = 1042
    SIMPLIFIED_CHINESE = 2052
    def __str__(self):
        return self.name.replace("_", " ").title()

class Edge(IntEnum):
    RISING = 0
    FALLING = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class EdgeWithEither(IntEnum):
    RISING = 0
    FALLING = 1
    EITHER = 2
    def __str__(self):
        return self.name.replace("_", " ").title()

class ClockPhase(IntEnum):
    FIRST_EDGE = 0
    SECOND_EDGE = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class Polarity(IntEnum):
    IDLE_LOW = 0
    IDLE_HIGH = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class Waveform(IntEnum):
    SINE = 0
    SQUARE = 1
    TRIANGLE = 2
    DC = 3
    def __str__(self):
        return self.name.replace("_", " ").title()

class CalibrationAction(IntEnum):
    COMMIT = 0
    CANCEL = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class DigitalSignalSource(IntEnum):
    FGEN_START = 0
    MSO_TRIGGER = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class FGenWaveformMode(IntEnum):
    STANDARD = 0
    ARBITRARY = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class FGenGenerationStatus(IntEnum):
    RUNNING = 0
    STOPPED = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoProbeAttenuation(IntEnum):
    ATTENUATION_1X = 1
    ATTENUATION_10X = 10
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoCoupling(IntEnum):
    AC = 0
    DC = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoSamplingMode(IntEnum):
    SAMPLE = 0
    PEAK_DETECT = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoDigitalSampleRateControl(IntEnum):
    AUTOMATIC = 0
    MANUAL = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoBufferControl(IntEnum):
    AUTOMATIC = 0
    MANUAL = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoTriggerInstance(IntEnum):
    A = 0
    B = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoTriggerType(IntEnum):
    IMMEDIATE = 0
    ANALOG_EDGE = 1
    DIGITAL_EDGE = 2
    DIGITAL_PATTERN = 3
    DIGITAL_GLITCH = 4
    ANALOG_PULSEWIDTH = 5
    DIGITAL_PULSEWIDTH = 6
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoAcquisitionStatus(IntEnum):
    STOPPED = 0
    RUNNING = 1
    TRIGGERED = 2
    ACQUISITION_COMPLETE = 3
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoTriggerReason(IntEnum):
    NORMAL = 0
    FORCED = 1
    AUTO = 2
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoComparisonMode(IntEnum):
    GREATER_THAN_UPPER_LIMIT = 0
    LESS_THAN_LOWER_LIMIT = 1
    INSIDE_LIMITS = 2
    OUTSIDE_LIMITS = 3
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoTriggerPolarity(IntEnum):
    POSITIVE = 0
    NEGATIVE = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class MsoInputImpedance(IntEnum):
    ONE_MEGA_OHM = 0
    FIFTY_OHMS = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class DmmFunction(IntEnum):
    DC_VOLTS = 0
    AC_VOLTS = 1
    DC_CURRENT = 2
    AC_CURRENT = 3
    RESISTANCE = 4
    DIODE = 5
    def __str__(self):
        return self.name.replace("_", " ").title()

class DmmCurrentTerminal(IntEnum):
    LOW = 0
    HIGH = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class DmmInputResistance(IntEnum):
    TEN_MEGA_OHM = 0
    TEN_GIGA_OHM = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class PsState(IntEnum):
    CONSTANT_CURRENT = 0
    CONSTANT_VOLTAGE = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class PsCalType(IntEnum):
    VOLTAGE = 0
    CURRENT = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class I2cAddressSize(IntEnum):
    SEVEN_BITS = 0
    TEN_BITS = 1
    def __str__(self):
        return self.name.replace("_", " ").title()

class I2cClockRate(IntEnum):
    ONE_HUNDRED_KHZ = 0
    FOUR_HUNDRED_KHZ = 1
    ONE_MHZ = 2
    def __str__(self):
        return self.name.replace("_", " ").title()

class Status(IntEnum):
    SUCCESS = 0
    ERROR_CAL_FUNCTION_NOT_SUPPORTED = -375995
    ERROR_INPUT_TERMINATION_OVERLOADED = -375993
    ERROR_ARB_CLIPPING = -375992
    ERROR_INVALID_OPERATION_FOR_MULTIPLE_CHANS_EDGE_TRIGGER = -375991
    ERROR_I2C_ARB_LOST = -375990
    ERROR_I2C_NAK = -375989
    ERROR_I2C_TIMEOUT = -375988
    ERROR_UNKNOWN_DEVICE_PID_OR_VID = -375987
    ERROR_CANNOT_START_TRANSFER_WHILE_IN_PROGRESS = -375986
    ERROR_INVALID_POINTER = -375985
    ERROR_INVALID_FRAME_SIZE = -375984
    ERROR_INVALID_NEXT_CAL_DATE = -375983
    ERROR_SET_NEXT_CAL_DATE_WITH_LAST_CAL_DATE = -375982
    ERROR_LAST_CAL_DATE_BLANK = -375981
    ERROR_DEVICE_NOT_IN_STORAGE = -375980
    ERROR_DEVICE_DID_NOT_REBOOT = -375979
    ERROR_INVALID_CONFIGURATION_FILE_WRONG_MODEL = -375978
    ERROR_INVALID_DEVICE_NAME_HAS_ALL_NUMBERS = -375977
    ERROR_HOSTNAME_RESOLUTION_TIMEOUT = -375976
    ERROR_HOSTNAME_RESOLUTION_FAILURE = -375975
    ERROR_DIGITAL_INITIALIZATION_FAILED = -375974
    ERROR_FIRMWARE_IS_TOO_NEW = -375971
    ERROR_FIRMWARE_IS_TOO_OLD = -375970
    ERROR_INVALID_METHOD = -375969
    ERROR_OVER_TEMP = -375968
    ERROR_INVALID_DEVICE_NAME = -375967
    ERROR_FGEN_OVERVOLTAGE = -375966
    ERROR_CANNOT_RENAME_DEVICE_BECAUSE_NAME_IN_USE = -375965
    ERROR_DEVICE_WITH_SAME_NAME_ALREADY_EXISTS = -375964
    ERROR_INTERNAL_STORAGE_FAILURE = -375963
    ERROR_LA_ACQUISITION_LENGTH = -375962
    ERROR_SCOPE_ACQUISITION_LENGTH = -375961
    ERROR_CANNOT_DELETE_USB = -375960
    ERROR_INVALID_NETWORK_PATH_SYNTAX = -375959
    ERROR_CANNOT_RUN_WHEN_NO_CHANNELS_ENABLED = -375958
    ERROR_TRIGGER_PATTERN_SIZE = -375957
    ERROR_TRANSPORT_TIMEOUT = -375956
    ERROR_PS_CURRENT_CAL_NEEDS_SHORT_CIRCUIT = -375955
    ERROR_PS_VOLTAGE_CAL_NEEDS_OPEN_CIRCUIT = -375954
    ERROR_HARDWARE_FAULT = -375950
    ERROR_NO_PERMISSION_FOR_OPERATION_WHEN_NOT_LOGGED_IN = -375949
    ERROR_NO_PERMISSION_FOR_OPERATION = -375948
    ERROR_AUTHENTICATION_FAILURE = -375947
    ERROR_AUTHENTICATION_CREDENTIALS_INVALID = -375946
    ERROR_PS_READ_WHEN_DISABLED = -375945
    ERROR_DEVICE_IS_NOT_AUTHENTIC = -375944
    ERROR_CALIBRATION_SIGNAL_INVALID = -375943
    ERROR_INVALID_CALIBRATION_ORDER = -375942
    ERROR_UNKNOWN_DEVICE = -375941
    ERROR_CAL_FAILED = -375940
    ERROR_NOT_ENOUGH_CAL_REF_POINTS = -375939
    ERROR_NO_CAL_REF_POINT = -375938
    ERROR_INVALID_CAL_REF_POINT = -375937
    ERROR_PS_INITIALIZATIONFAILED = -375936
    ERROR_FGEN_INITIALIZATION_FAILED = -375935
    ERROR_SCOPE_INITIALIZATION_FAILED = -375934
    ERROR_DMM_INITIALIZATION_FAILED = -375933
    ERROR_CONFIG_DATA_IS_CORRUPT = -375932
    ERROR_PNG_FILE_DOES_NOT_CONTAIN_CONFIGURATION_DATA = -375931
    ERROR_PNG_FILE_IS_CORRUPT = -375930
    ERROR_NO_PERMISSION_TO_WRITE_FILE = -375929
    ERROR_NO_PERMISSION_TO_READ_FILE = -375928
    ERROR_FILE_IO_ERROR = -375927
    ERROR_NO_SPACE_LEFT_ON_DEVICE = -375926
    ERROR_INVALID_FILENAME = -375925
    ERROR_UNKNOWN_CONFIGURATION_FILE_FORMAT = -375924
    ERROR_CALIBRATION_CORRUPT = -375923
    ERROR_INVALID_CALIBRATION_PASSWORD = -375922
    ERROR_TOO_MANY_SAVED_CONFIGURATIONS = -375921
    ERROR_CONFIGURATION_NAME_IS_TOO_LONG = -375920
    ERROR_SAVED_CONFIGURATION_DATA_IS_TOO_LARGE = -375919
    ERROR_SAVED_CONFIGURATION_ALREADY_EXISTS = -375918
    ERROR_SAVED_CONFIGURATION_DOES_NOT_EXIST = -375917
    ERROR_INVALID_CONFIGURATION_FILE_FORMAT = -375916
    ERROR_INVALID_OPERATION_FOR_MULTIPLE_CHANS = -375914
    ERROR_CANNOT_FORCE_TRIGGER_WHEN_STOPPED = -375913
    ERROR_ONLY_ONE_CHANNEL_VALID_FOR_RATE = -375912
    ERROR_MULTIPLE_TRIGGER_SOURCES = -375911
    ERROR_TRIGGER_CHANNELS_NOT_ENABLED = -375910
    ERROR_CANNOT_READ_WHEN_STOPPED = -375909
    ERROR_NOT_CONNECTED = -375908
    ERROR_CANNOT_CHANGE_CONFIG_WHILE_RUNNING = -375907
    ERROR_INVALID_SESSION = -375906
    ERROR_INVALID_CHANNEL_NAME = -375905
    ERROR_DIG_NUM_LINES_DOESNT_MATCH_DATA = -375904
    ERROR_RESERVATION_FAILED = -375903
    ERROR_INVALID_CONFIGURATION = -375902
    ERROR_OUT_OF_MEMORY = -375901
    ERROR_INTERNAL = -375900
    WARNING_CAPI_HEADER_OUT_OF_DATE = 374310
    WARNING_NOT_ENOUGH_MEMORY = 374309
    WARNING_DEVICE_NAME_USED_AS_HOSTNAME = 374308
    WARNING_DMM_HARDWARE_OVERRANGE = 374307
    WARNING_DEVICE_DIFFERENT_FROM_EXPECTED = 374306
    WARNING_DEVICE_HAS_BEEN_RENAMED = 374305
    WARNING_NO_SIGNAL_SUITABLE_FOR_SAMPLE_RATE_IN_AUTO_SETUP = 374304
    WARNING_NO_SIGNALS_FOUND_FOR_AUTO_SETUP = 374303
    WARNING_IMPORT_ARB_MODE = 374302
    WARNING_DMM_OVERRANGE = 374301
    WARNING_ARB_CLIPPING = 374300
    def __str__(self):
        return self.name.replace("_", " ").title()

class Timestamp(Structure):
    _fields_ = [("t1", c_uint32),
                ("t2", c_uint32),
                ("t3", c_uint32),
                ("t4", c_uint32)]

class PyVirtualBenchException(Exception):
    def __init__(self, status, nilcicapi, library_handle):
        self.status = status
        self.nilcicapi = nilcicapi
        self.library_handle = library_handle
        self.language = Language.CURRENT_THREAD_LOCALE

    def __str__(self):
        descr_size = c_size_t(0)
        extended_err_size = c_size_t(0)

        self.nilcicapi.niVB_GetErrorDescriptionW(self.library_handle, self.status, self.language, None, 0, byref(descr_size))
        descr_buffer = (c_wchar * descr_size.value)()
        self.nilcicapi.niVB_GetErrorDescriptionW(self.library_handle, self.status, self.language, byref(descr_buffer), descr_size.value, None)

        self.nilcicapi.niVB_GetExtendedErrorInformationW(self.library_handle, self.language, None, 0, byref(extended_err_size))
        extended_err_buffer = (c_wchar * extended_err_size.value)()
        self.nilcicapi.niVB_GetExtendedErrorInformationW(self.library_handle, self.language, byref(extended_err_buffer), extended_err_size.value, None)
        return descr_buffer.value + "\n" + extended_err_buffer.value

class PyVirtualBench:
    '''VirtualBench is a hardware device sold by National Instruments (NI) which
       integrates a mixed-signal oscilloscope, function generator, digital
       multimeter, programmable DC power supply, and digital I/O intoa single
       form-factor device.  As of version 1.1.0, NI released a C-API to allows
       anyone to communicate directly with the device.  This class simply wraps
       that C-API, allowing us to control the device from python.
    '''

    def __init__(self, device_name = ''):
        ''' Initialize the VirtualBench library.  This must be called at least
            once for the application. The 'version' parameter must be set to the
            NIVB_LIBRARY_VERSION constant.
        '''
        self.device_name = device_name
        self.nilcicapi = cdll.LoadLibrary("nilcicapi")
        self.library_handle = c_sysint(0)
        status = self.nilcicapi.niVB_Initialize(NIVB_LIBRARY_VERSION, byref(self.library_handle))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

    def release(self):
        ''' Finalize the VirtualBench library.
        '''
        status = self.nilcicapi.niVB_Finalize(self.library_handle)
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        self.library_handle = None

    def get_library_version(self):
        ''' Return the version of the VirtualBench runtime library.
        '''
        version = c_uint32(0)
        status = self.nilcicapi.niVB_GetLibraryVersion(byref(version))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return version.value

    def convert_timestamp_to_values(self, timestamp):
        ''' Converts a timestamp to seconds and fractional seconds.
        '''
        seconds_since_1970 = c_int64(0)
        fractional_seconds = c_double(0)
        status = self.nilcicapi.niVB_ConvertTimestampToValues(timestamp, byref(seconds_since_1970), byref(fractional_seconds))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return seconds_since_1970.value, fractional_seconds.value

    def convert_values_to_timestamp(self, seconds_since_1970, fractional_seconds):
        ''' Converts seconds and fractional seconds to a timestamp.
        '''
        timestamp = Timestamp(0, 0, 0, 0)
        status = self.nilcicapi.niVB_ConvertValuesToTimestamp(c_int64(seconds_since_1970), c_double(fractional_seconds), byref(timestamp))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return timestamp

    def add_network_device(self, ip_or_hostname, timeout_in_ms):
        ''' Adds a networked device to the system.
        '''
        device_name_size_out = c_size_t(0)
        status = self.nilcicapi.niVB_AddNetworkDeviceW(self.library_handle, c_wchar_p(ip_or_hostname), c_int32(timeout_in_ms), None, c_size_t(0), byref(device_name_size_out))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        device_name_size = c_size_t(device_name_size_out.value)
        device_name = (c_wchar * device_name_size)()
        status = self.nilcicapi.niVB_AddNetworkDeviceW(self.library_handle, c_wchar_p(ip_or_hostname), c_int32(timeout_in_ms), byref(device_name), c_size_t(device_name_size), byref(device_name_size_out))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return device_name.value

    def remove_device(self, device_name = ''):
        ''' Removes a device from the system. The device must not be connected
            via USB to be removed.
        '''
        local_device_name = device_name if device_name else self.device_name
        status = self.nilcicapi.niVB_RemoveDeviceW(self.library_handle, c_wchar_p(local_device_name))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

    def collapse_channel_string(self, names_in):
        ''' Collapses a channel string into a comma and colon-delimited
            equivalent.
        '''
        names_out_size_out = c_size_t(0)
        status = self.nilcicapi.niVB_CollapseChannelStringW(self.library_handle, c_wchar_p(names_in), None, c_size_t(0), byref(names_out_size_out), None)
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        names_out_size = names_out_size_out.value
        names_out = (c_wchar * names_out_size)()
        number_of_channels = c_size_t(0)
        status = self.nilcicapi.niVB_CollapseChannelStringW(self.library_handle, c_wchar_p(names_in), byref(names_out), c_size_t(names_out_size), None, byref(number_of_channels))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return names_out.value, number_of_channels.value

    def expand_channel_string(self, names_in):
        ''' Expands a channel string into a comma-delimited (no colon)
            equivalent.
        '''
        names_out_size_out = c_size_t(0)
        status = self.nilcicapi.niVB_ExpandChannelStringW(self.library_handle, c_wchar_p(names_in), None, c_size_t(0), byref(names_out_size_out), None)
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        names_out_size = names_out_size_out.value
        names_out = (c_wchar * names_out_size)()
        number_of_channels = c_size_t(0)
        status = self.nilcicapi.niVB_ExpandChannelStringW(self.library_handle, c_wchar_p(names_in), byref(names_out), c_size_t(names_out_size), None, byref(number_of_channels))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return names_out.value, number_of_channels.value

    def login(self, device_name = '', username = 'admin', password = ''):
        ''' Attempts to log in to a networked device. Logging in to a device grants
            access to the permissions set for the specified user in NI Web-Based
            Monitoring and Configuration.
        '''
        local_device_name = device_name if device_name else self.device_name
        status = self.nilcicapi.niVB_LogInW(self.library_handle, c_wchar_p(local_device_name), c_wchar_p(username), c_wchar_p(password))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

    def logout(self, device_name = ''):
        ''' Logs out of a networked device that you are logged in to. Logging out of a
            device revokes access to the permissions set for the specified user in NI
            Web-Based Monitoring and Configuration.
        '''
        local_device_name = device_name if device_name else self.device_name
        status = self.nilcicapi.niVB_LogOutW(self.library_handle, c_wchar_p(device_name))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

    def set_calibration_information(self, calibration_date, calibration_interval, device_name = '', password = ''):
        ''' Sets calibration information for the specified device.
        '''
        local_device_name = device_name if device_name else self.device_name
        status = self.nilcicapi.niVB_Cal_SetCalibrationInformationW(self.library_handle, c_wchar_p(local_device_name), Timestamp(calibration_date), c_int32(calibration_interval), c_wchar_p(password))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

    def set_calibration_password(self, current_password, new_password, device_name = ''):
        ''' Sets a new calibration password for the specified device. This
            method requires the current password for the device, and returns an
            error if the specified password is incorrect.
        '''
        local_device_name = device_name if device_name else self.device_name
        status = self.nilcicapi.niVB_Cal_SetCalibrationPasswordW(self.library_handle, c_wchar_p(local_device_name), c_wchar_p(current_password), c_wchar_p(new_password))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

    def get_calibration_information(self, device_name = ''):
        ''' Returns calibration information for the specified device, including
            the last calibration date and calibration interval.
        '''
        local_device_name = device_name if device_name else self.device_name
        calibration_date = Timestamp(0, 0, 0, 0)
        recommended_calibration_interval = c_int32(0)
        calibration_interval = c_int32(0)
        status = self.nilcicapi.niVB_Cal_GetCalibrationInformationW(self.library_handle, c_wchar_p(local_device_name), byref(calibration_date), byref(recommended_calibration_interval), byref(calibration_interval))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return calibration_date, recommended_calibration_interval.value, calibration_interval.value

#------------------------------------------------------------------------------

    def acquire_digital_input_output(self, lines, reset = True):
        ''' Establishes communication with the device. This method should be
            called once per session.
            lines requires full name specification e.g. 'VB8012-xxxxxxx/dig/0:7'

            You can individually configure each line as an input or output. Each
            of these lines has a 10 kΩ pull-down resistor when used for GPIO.
            Outputs can be driven high to 3.3 V or low to ground.

            Exported signal output—Each line can export the MSO Trigger or FGEN
            Start signal. When importing a trigger, the mixed signal
            oscilloscope (MSO) can display the signal present on the digital
            I/O connector as a digital channel as well as use it as a trigger
            for the acquisition. When exporting a trigger, these options are a
            vailable:

            * A pulse is sent every time the function generator (FGEN) begins a
              new period of the signal being generated.
            * A pulse is sent every time the MSO triggers.
            * A pulse is sent at the frequency of the 60 Hz/50 Hz AC line.
        '''
        return self.DigitalInputOutput(self, lines, reset)

    class DigitalInputOutput(object):
        def __init__(self, outer, lines, reset):
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.lines = lines
            self.instrument_handle = c_sysint(0)
            # only lines for writing need to be initialized, read is possible with library handle only
            status = self.nilcicapi.niVB_Dig_InitializeW(self.library_handle, c_wchar_p(self.lines), c_bool(reset), byref(self.instrument_handle))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self):
            ''' Stops the session and deallocates any resources acquired during
                the session. If output is enabled on any channels, they remain
                in their current state and continue to output data.
            '''
            status = self.nilcicapi.niVB_Dig_Close(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def tristate_lines(self, lines):
            ''' Sets all specified lines to a high-impedance state.
            '''
            status = self.nilcicapi.niVB_Dig_TristateLinesW(self.instrument_handle, c_wchar_p(lines))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def export_signal(self, line, digitalSignalSource):
            ''' Exports a signal to the specified line.
                digitalSignalSource: 0 for FGEN Start or 1 for MSO trigger.
            '''
            status = self.nilcicapi.niVB_Dig_ExportSignalW(self.instrument_handle, c_wchar_p(line), c_int32(digitalSignalSource))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def query_line_configuration(self):
            ''' Indicates the current line configurations. Tristate Lines,
                Static Lines, and Export Lines contain comma-separated range_data
                and/or colon-delimited lists of all lines specified in Dig
                Initialize
            '''
            tristate_lines_size_out = c_size_t(0)
            static_lines_size_out = c_size_t(0)
            export_lines_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_Dig_QueryLineConfigurationW(self.instrument_handle, None, c_size_t(0), byref(tristate_lines_size_out), None, c_size_t(0), byref(static_lines_size_out), None, c_size_t(0), byref(export_lines_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

            tristate_lines_size = tristate_lines_size_out.value
            static_lines_size = static_lines_size_out.value
            export_lines_size = export_lines_size_out.value
            tristate_lines = (c_wchar * tristate_lines_size)()
            static_lines = (c_wchar * static_lines_size)()
            export_lines = (c_wchar * export_lines_size)()

            status = self.nilcicapi.niVB_Dig_QueryLineConfigurationW(self.instrument_handle, byref(tristate_lines), c_size_t(tristate_lines_size), byref(tristate_lines_size_out), byref(static_lines), c_size_t(static_lines_size), byref(static_lines_size_out), byref(export_lines), c_size_t(export_lines_size), byref(export_lines_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return tristate_lines.value, static_lines.value, export_lines.value

        def query_export_signal(self, line):
            ''' Indicates the signal being exported on the specified line. Use
                Dig Query Line Configuration to check the state of a line.
            '''
            signal = c_int32(0) # DigitalSignalSource
            status = self.nilcicapi.niVB_Dig_QueryExportSignalW(self.instrument_handle, c_wchar_p(line), byref(signal))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return DigitalSignalSource(signal.value)

        def write(self, lines, data):
            ''' Writes data to the specified lines.
            '''
            local_data = ((c_bool) * len(data))(*data)
            status = self.nilcicapi.niVB_Dig_WriteW(self.instrument_handle, c_wchar_p(lines), local_data, c_size_t(len(local_data)))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def read(self, lines):
            ''' Reads the current state of the specified lines.
                lines requires full name specification e.g. 'VB8012-xxxxxxx/dig/0:7'
                since instrument_handle is not required (only library_handle)
            '''
            data_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_Dig_ReadW(self.library_handle, c_wchar_p(lines), None, c_size_t(0), byref(data_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            data_out = []
            data_size = data_size_out.value
            data = (c_bool * data_size)()
            status = self.nilcicapi.niVB_Dig_ReadW(self.library_handle, c_wchar_p(lines), data, c_size_t(data_size), byref(data_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            for i in range(data_size_out.value): data_out.append(data[i])
            return data_out

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
                the device and driver software to a known state.
            '''
            status = self.nilcicapi.niVB_Dig_ResetInstrument(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

#------------------------------------------------------------------------------

    def acquire_function_generator(self, device_name = '', reset = True):
        ''' Establishes communication with the device. This method should be
            called once per session.
        '''
        return self.FunctionGenerator(self, device_name, reset)

    class FunctionGenerator(object):
        def __init__(self, outer, device_name, reset):
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.device_name = device_name if device_name else outer.device_name
            self.instrument_handle = c_sysint(0)
            status = self.nilcicapi.niVB_FGEN_InitializeW(self.library_handle, c_wchar_p(self.device_name), c_bool(reset), byref(self.instrument_handle))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self):
            ''' Stops the session and deallocates any resources acquired during
                the session. If output is enabled on any channels, they remain
                in their current state and continue to output data.
            '''
            status = self.nilcicapi.niVB_FGEN_Close(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def configure_standard_waveform(self, waveform_function, amplitude, dc_offset, frequency, duty_cycle):
            ''' Configures the instrument to output a standard waveform.
            '''
            status = self.nilcicapi.niVB_FGEN_ConfigureStandardWaveform(self.instrument_handle, c_int32(waveform_function), c_double(amplitude), c_double(dc_offset), c_double(frequency), c_double(duty_cycle))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_arbitrary_waveform(self, waveform, sample_period):
            ''' Configures the instrument to output a waveform. The waveform is
                output either after the end of the current waveform if output
                is enabled, or immediately after output is enabled.
            '''
            waveform_size = len(waveform)
            waveform = (c_double * waveform_size)(*waveform)
            status = self.nilcicapi.niVB_FGEN_ConfigureArbitraryWaveform(self.instrument_handle, waveform, c_size_t(waveform_size), c_double(sample_period))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_arbitrary_waveform_gain_and_offset(self, gain, dc_offset):
            ''' Configures the instrument to output an arbitrary waveform with a
                specified gain and offset value. The waveform is output either
                after the end of the current waveform if output is enabled, or
                immediately after output is enabled.
            '''
            status = self.nilcicapi.niVB_FGEN_ConfigureArbitraryWaveformGainAndOffset(self.instrument_handle, c_double(gain), c_double(dc_offset))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def enable_filter(self, enable_filter):
            ''' Enables or disables the filter on the instrument.
            '''
            status = self.nilcicapi.niVB_FGEN_EnableFilter(self.instrument_handle, c_bool(enable_filter))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def query_waveform_mode(self):
            ''' Indicates whether the waveform output by the instrument is a
                standard or arbitrary waveform.
            '''
            waveform_mode = c_int32(0) # FGenWaveformMode
            status = self.nilcicapi.niVB_FGEN_QueryWaveformMode(self.instrument_handle, byref(waveform_mode))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return FGenWaveformMode(waveform_mode.value)

        def query_standard_waveform(self):
            ''' Returns the settings for a standard waveform generation.
            '''
            waveform_function = c_int32(0) # Waveform
            amplitude = c_double(0)
            dc_offset = c_double(0)
            frequency = c_double(0)
            duty_cycle = c_double(0)
            status = self.nilcicapi.niVB_FGEN_QueryStandardWaveform(self.instrument_handle, byref(waveform_function), byref(amplitude), byref(dc_offset), byref(frequency), byref(duty_cycle))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return Waveform(waveform_function.value), amplitude.value, dc_offset.value, frequency.value, duty_cycle.value

        def query_arbitrary_waveform(self):
            ''' Returns the settings for arbitrary waveform generation.
            '''
            sample_rate = c_double(0)
            status = self.nilcicapi.niVB_FGEN_QueryArbitraryWaveform(self.instrument_handle, byref(sample_rate))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return sample_rate.value

        def query_arbitrary_waveform_gain_and_offset(self):
            ''' Returns the settings for arbitrary waveform generation that
                includes gain and offset settings.
            '''
            gain = c_double(0)
            offset = c_double(0)
            status = self.nilcicapi.niVB_FGEN_QueryArbitraryWaveformGainAndOffset(self.instrument_handle, byref(gain), byref(offset))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return gain.value, offset.value

        def query_filter(self):
            ''' Indicates whether the filter is enabled on the instrument.
            '''
            filter_enabled = c_bool(0)
            status = self.nilcicapi.niVB_FGEN_QueryFilter(self.instrument_handle, byref(filter_enabled))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return filter_enabled.value

        def query_generation_status(self):
            ''' Returns the status of waveform generation on the instrument.
            '''
            generation_status = c_int32(0) # FgenGenerationStatus
            status = self.nilcicapi.niVB_FGEN_QueryGenerationStatus(self.instrument_handle, byref(generation_status))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return FGenGenerationStatus(generation_status.value)

        def run(self):
            ''' Transitions the session from the Stopped state to the Running
                state.
            '''
            status = self.nilcicapi.niVB_FGEN_Run(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def self_calibrate(self):
            '''Performs offset nulling calibration on the device. You must run FGEN
               Initialize prior to running this method.
            '''
            status = self.nilcicapi.niVB_FGEN_SelfCalibrate(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def stop(self):
            ''' Transitions the acquisition from either the Triggered or Running
                state to the Stopped state.
            '''
            status = self.nilcicapi.niVB_FGEN_Stop(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
                the device and driver software to a known state.
            '''
            status = self.nilcicapi.niVB_FGEN_ResetInstrument(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def export_configuration(self, configuration_filename):
            ''' Exports a configuration file for use with the function
                generator.
            '''
            status = self.nilcicapi.niVB_FGEN_ExportConfigurationW(self.instrument_handle, c_wchar_p(configuration_filename))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def import_configuration(self, configuration_filename):
            ''' Imports a configuration file for use with the function
                generator. You can import PNG files exported from the
                VirtualBench Application or files created from FGEN Export
                Configuration.
            '''
            status = self.nilcicapi.niVB_FGEN_ImportConfigurationW(self.instrument_handle, c_wchar_p(configuration_filename))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

#------------------------------------------------------------------------------

    def get_function_generator_calibration_adjustment_information(self, device_name = ''):
        ''' Returns instrument information from the last successful calibration
            adjustment.
        '''
        local_device_name = device_name if device_name else self.device_name
        adjustment_date = Timestamp(0, 0, 0, 0)
        adjustment_temperature = c_double(0)
        status = self.nilcicapi.niVB_FGEN_GetCalibrationAdjustmentInformationW(self.library_handle, c_wchar_p(local_device_name), byref(adjustment_date), byref(adjustment_temperature))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return adjustment_date, adjustment_temperature.value

    def acquire_function_generator_calibration(self, device_name = '', password = ''):
        ''' Opens a calibration session with the instrument. The instrument is
            reset upon successful completion of this method. This method returns
            an error if the instrument is reserved or if Password is incorrect.
        '''
        return self.FunctionGeneratorCalibration(self, device_name, password)

    class FunctionGeneratorCalibration(object):
        def __init__(self, outer, device_name, password):
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.device_name = device_name if device_name else outer.device_name
            self.instrument_handle = c_sysint(0)
            status = self.nilcicapi.niVB_FGEN_InitializeCalibrationW(self.library_handle, c_wchar_p(self.device_name), c_wchar_p(password), byref(self.instrument_handle))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self, calibration_action = CalibrationAction.COMMIT):
            ''' Closes the calibration session, then resets the device.
            '''
            status = self.nilcicapi.niVB_FGEN_CloseCalibration(self.instrument_handle, c_int32(calibration_action))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def setup_offset_calibration(self, enable_filter):
            ''' Configures the instrument to output the offset values of the
                function generator.
            '''
            status = self.nilcicapi.niVB_FGEN_SetupOffsetCalibration(self.instrument_handle, c_bool(enable_filter))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def adjust_offset_calibration(self, reference_value):
            ''' Stores a measured reference value to the instrument and
                associates that value with the adjustment point and filter
                values previously configured with FGEN Setup Offset Calibration.
                You must run FGEN Setup Offset Calibration prior to running
                this method.
            '''
            calibration_done = c_bool(0)
            status = self.nilcicapi.niVB_FGEN_AdjustOffsetCalibration(self.instrument_handle, c_double(reference_value), byref(calibration_done))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return calibration_done.value

        def get_gain_calibration_adjustment_points(self):
            ''' Returns the adjustment points and filter configurations needed
                to sweep the instrument for adjustment.
            '''
            enable_filter_out = []
            enable_filter_size_out = c_size_t(0)
            adjustment_point_out = []
            adjustment_point_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_FGEN_GetGainCalibrationAdjustmentPoints(self.instrument_handle, None, c_size_t(0), byref(enable_filter_size_out), None, c_size_t(0), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            enable_filter_size = c_size_t(enable_filter_size_out.value)
            adjustment_point_size = c_size_t(adjustment_point_size_out.value)
            enable_filter = (c_bool * enable_filter_size)()
            adjustment_point = (c_double * adjustment_point_size)()
            status = self.nilcicapi.niVB_FGEN_GetGainCalibrationAdjustmentPoints(self.instrument_handle, byref(enable_filter), c_size_t(enable_filter_size), byref(enable_filter_size_out), byref(adjustment_point), c_size_t(adjustment_point_size), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            for i in range(enable_filter_size.value): enable_filter_out.append(enable_filter[i])
            for i in range(adjustment_point_size.value): adjustment_point_out.append(adjustment_point[i])
            return enable_filter_out, adjustment_point_out

        def setup_gain_calibration(self, enable_filter, adjustment_point):
            ''' Configures the instrument to output the values returned by FGEN
                Get Calibration Adjustment Points.
            '''
            status = self.nilcicapi.niVB_FGEN_SetupGainCalibration(self.instrument_handle, c_bool(enable_filter), c_double(adjustment_point))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def adjust_gain_calibration(self, reference_value):
            ''' Stores a measured reference value to the instrument and
                associates that value with the adjustment point and filter
                values previously configured with FGEN Setup Gain Calibration.
                You must run FGEN Setup Gain Calibration prior to running this
                method.
            '''
            status = self.nilcicapi.niVB_FGEN_AdjustGainCalibration(self.instrument_handle, c_double(reference_value))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

#------------------------------------------------------------------------------

    def acquire_mixed_signal_oscilloscope(self, device_name = '', reset = True):
        ''' Establishes communication with the device. This method should be
            called once per session.
        '''
        return self.MixedSignalOscilloscope(self, device_name, reset)

    class MixedSignalOscilloscope(object):
        def __init__(self, outer, device_name, reset):
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.device_name = device_name if device_name else outer.device_name
            self.instrument_handle = c_sysint(0)
            status = self.nilcicapi.niVB_MSO_InitializeW(self.library_handle, c_wchar_p(self.device_name), c_bool(reset), byref(self.instrument_handle))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self):
            ''' Removes the session and deallocates any resources acquired
                during the session. If output is enabled on any channels, they
                remain in their current state.
            '''
            status = self.nilcicapi.niVB_MSO_Close(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def auto_setup(self):
            ''' Automatically configures the instrument.
            '''
            status = self.nilcicapi.niVB_MSO_Autosetup(self.instrument_handle)
            if (status != Status.SUCCESS and status <= 0):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_analog_channel(self, channel, enable_channel, vertical_range, vertical_offset, probe_attenuation, vertical_coupling):
            ''' Configures the settings of the specified analog channel.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureAnalogChannelW(self.instrument_handle, c_wchar_p(channel), c_bool(enable_channel), c_double(vertical_range), c_double(vertical_offset), c_int32(probe_attenuation), c_int32(vertical_coupling))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_analog_channel_characteristics(self, channel, input_impedance, bandwidth_limit):
            ''' Configures the properties that control the electrical
                characteristics of the specified channel.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureAnalogChannelCharacteristicsW(self.instrument_handle, c_wchar_p(channel), c_int32(input_impedance), c_double(bandwidth_limit))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def enable_digital_channels(self, channel, enable_channel):
            ''' Enables or disables the specified digital channels.
            '''
            status = self.nilcicapi.niVB_MSO_EnableDigitalChannelsW(self.instrument_handle, c_wchar_p(channel), c_bool(enable_channel))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_digital_threshold(self, threshold):
            ''' Configures the threshold level for logic analyzer lines.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureDigitalThreshold(self.instrument_handle, c_double(threshold))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_timing(self, sample_rate, acquisition_time, pretrigger_time, sampling_mode):
            ''' Configures the basic timing settings of the instrument.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureTiming(self.instrument_handle, c_double(sample_rate), c_double(acquisition_time), c_double(pretrigger_time), c_int32(sampling_mode))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_advanced_digital_timing(self, digital_sample_rate_control, digital_sample_rate, buffer_control, buffer_pretrigger_percent):
            ''' Configures the rate and buffer settings of the logic analyzer.
                This method allows for more advanced configuration options than
                MSO Configure Timing.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureAdvancedDigitalTiming(self.instrument_handle, c_int32(digital_sample_rate_control), c_double(digital_sample_rate), c_int32(buffer_control), c_double(buffer_pretrigger_percent))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_state_mode(self, enable, clock_channel, clock_edge):
            ''' Configures how to clock data on the logic analyzer channels that
                are enabled.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureStateModeW(self.instrument_handle, c_bool(enable), c_wchar_p(clock_channel), c_int32(clock_edge))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_immediate_trigger(self):
            ''' Configures a trigger to immediately activate on the specified
                channels after the pretrigger time has expired.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureImmediateTrigger(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_analog_edge_trigger(self, trigger_source, trigger_slope, trigger_level, trigger_hysteresis, trigger_instance):
            ''' Configures a trigger to activate on the specified source when
                the analog edge reaches the specified levels.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureAnalogEdgeTriggerW(self.instrument_handle, c_wchar_p(trigger_source), c_int32(trigger_slope), c_double(trigger_level), c_double(trigger_hysteresis), c_int32(trigger_instance))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_digital_edge_trigger(self, trigger_source, trigger_slope, trigger_instance):
            ''' Configures a trigger to activate on the specified source when
                the digital edge reaches the specified levels.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureDigitalEdgeTriggerW(self.instrument_handle, c_wchar_p(trigger_source), c_int32(trigger_slope), c_int32(trigger_instance))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_digital_pattern_trigger(self, trigger_source, trigger_pattern, trigger_instance):
            ''' Configures a trigger to activate on the specified channels when
                a digital pattern is matched. A trigger is produced when every
                level (high/low) requirement specified in Trigger Pattern is
                met, and when at least one toggling (toggle/fall/rise)
                requirement is met. If no toggling requirements are set, then
                only the level requirements must be met to produce a trigger.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureDigitalPatternTriggerW(self.instrument_handle, c_wchar_p(trigger_source), c_wchar_p(trigger_pattern), c_int32(trigger_instance))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_digital_glitch_trigger(self, trigger_source, trigger_instance):
            ''' Configures a trigger to activate on the specified channels when
                a digital glitch occurs. A glitch occurs when a channel in
                Trigger Source toggles between two edges of the sample clock,
                but has the same state for both samples. This may happen when
                the sampling rate is less than 1 GHz.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureDigitalGlitchTriggerW(self.instrument_handle, c_wchar_p(trigger_source), c_int32(trigger_instance))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_analog_pulse_width_trigger(self, trigger_source, trigger_polarity, trigger_level, comparison_mode, lower_limit, upper_limit, trigger_instance):
            ''' Configures a trigger to activate on the specified source when the analog
                edge reaches the specified levels within a specified window of time.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureAnalogPulseWidthTriggerW(self.instrument_handle, c_wchar_p(trigger_source), c_int32(trigger_polarity), c_double(trigger_level), c_int32(comparison_mode), c_double(lower_limit), c_double(upper_limit), c_int32(trigger_instance))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_digital_pulse_width_trigger(self, trigger_source, trigger_polarity, comparison_mode, lower_limit, upper_limit, trigger_instance):
            ''' Configures a trigger to activate on the specified source when the digital
                edge reaches the specified levels within a specified window of time.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureDigitalPulseWidthTriggerW(self.instrument_handle, c_wchar_p(trigger_source), c_int32(trigger_polarity), c_int32(comparison_mode), c_double(lower_limit), c_double(upper_limit), c_int32(trigger_instance))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_trigger_delay(self, trigger_delay):
            ''' Configures the amount of time to wait after a trigger condition
                is met before triggering.
            '''
            status = self.nilcicapi.niVB_MSO_ConfigureTriggerDelay(self.instrument_handle, c_double(trigger_delay))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def query_analog_channel(self, channel):
            ''' Indicates the vertical configuration of the specified channel.
            '''
            channel_enabled = c_bool(0)
            vertical_range = c_double(0)
            vertical_offset = c_double(0)
            probe_attenuation = c_int32(0)
            vertical_coupling = c_int32(0)
            status = self.nilcicapi.niVB_MSO_QueryAnalogChannelW(self.instrument_handle, c_wchar_p(channel), byref(channel_enabled), byref(vertical_range), byref(vertical_offset), byref(probe_attenuation), byref(vertical_coupling))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return channel_enabled.value, vertical_range.value, vertical_offset.value, MsoProbeAttenuation(probe_attenuation.value), MsoCoupling(vertical_coupling.value)

        def query_enabled_analog_channels(self):
            ''' No documentation
            '''
            channels_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_MSO_QueryEnabledAnalogChannelsW(self.instrument_handle, None, c_size_t(0), byref(channels_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            channels_size = channels_size_out.value
            channels = (c_wchar * channels_size)()
            status = self.nilcicapi.niVB_MSO_QueryEnabledAnalogChannelsW(self.instrument_handle, byref(channels), c_size_t(channels_size), byref(channels_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return channels.value

        def query_analog_channel_characteristics(self, channel):
            ''' Indicates the properties that control the electrical characteristics of the specified channel.
                This method returns an error if too much power is applied to the channel.
            '''
            input_impedance = c_int32(0)
            bandwidth_limit = c_double(0)
            status = self.nilcicapi.niVB_MSO_QueryAnalogChannelCharacteristicsW(self.instrument_handle, c_wchar_p(channel), byref(input_impedance), byref(bandwidth_limit))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return MsoInputImpedance(input_impedance.value), bandwidth_limit.value

        def query_digital_channel(self):
            ''' Indicates whether the specified digital channel is enabled.
            '''
            channel_enabled = c_bool(0)
            status = self.nilcicapi.niVB_MSO_QueryDigitalChannelW(self.instrument_handle, c_wchar_p(channel), byref(channel_enabled))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return channel_enabled.value

        def query_enabled_digital_channels(self):
            ''' No documentation
            '''
            channels_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_MSO_QueryEnabledDigitalChannelsW(self.instrument_handle, None, c_size_t(0), byref(channels_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            channels_size = channels_size_out.value
            channels = (c_wchar * channels_size)()
            status = self.nilcicapi.niVB_MSO_QueryEnabledDigitalChannelsW(self.instrument_handle, byref(channels), c_size_t(channels_size), byref(channels_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return channels.value

        def query_digital_threshold(self):
            ''' Indicates the threshold configuration of the logic analyzer
                channels.
            '''
            threshold = c_double(0)
            status = self.nilcicapi.niVB_MSO_QueryDigitalThreshold(self.instrument_handle, byref(threshold))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return threshold.value

        def query_timing(self):
            ''' Indicates the timing configuration of the MSO.
            '''
            sample_rate = c_double(0)
            acquisition_time = c_double(0)
            pretrigger_time = c_double(0)
            sampling_mode = c_int32(0) # MsoSamplingMode
            status = self.nilcicapi.niVB_MSO_QueryTiming(self.instrument_handle, byref(sample_rate), byref(acquisition_time), byref(pretrigger_time), byref(sampling_mode))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return sample_rate.value, acquisition_time.value, pretrigger_time.value, MsoSamplingMode(sampling_mode.value)

        def query_advanced_digital_timing(self):
            ''' Indicates the buffer configuration of the logic analyzer.
            '''
            digital_sample_rate_control = c_int32(0) # MsoDigitalSampleRateControl
            digital_sample_rate = c_double(0)
            buffer_control = c_int32(0) # MsoBufferControl
            buffer_pretrigger_percent = c_double(0)
            status = self.nilcicapi.niVB_MSO_QueryAdvancedDigitalTiming(self.instrument_handle, byref(digital_sample_rate_control), byref(digital_sample_rate), byref(buffer_control), byref(buffer_pretrigger_percent))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return MsoDigitalSampleRateControl(digital_sample_rate_control.value), digital_sample_rate.value, MsoBufferControl(buffer_control.value), buffer_pretrigger_percent.value

        def query_state_mode(self, clockChannelSize):
            ''' Indicates the clock configuration of the logic analyzer.
            '''
            clock_channel_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_MSO_QueryStateModeW(self.instrument_handle, None,  None, c_size_t(0), byref(clock_channel_size_out), None)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            state_mode_enabled = c_bool(0)
            clock_channel_size = c_size_t(clock_channel_size_out.value)
            clock_channel = (c_wchar * clock_channel_size.value)()
            clock_edge = c_int32(0) # EdgeWithEither
            status = self.nilcicapi.niVB_MSO_QueryStateModeW(self.instrument_handle, byref(state_mode_enabled),  byref(clock_channel), c_size_t(clock_channel_size), byref(clock_channel_size_out), byref(clock_edge))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return state_mode_enabled.value, clock_channel.value, EdgeWithEither(clock_edge.value)

        def query_trigger_type(self, trigger_instance):
            ''' Indicates the trigger type of the specified instance.
            '''
            trigger_type = c_int32(0) # MsoTriggerType
            status = self.nilcicapi.niVB_MSO_QueryTriggerType(self.instrument_handle, c_int32(trigger_instance), byref(trigger_type))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return MsoTriggerType(trigger_type.value)

        def query_analog_edge_trigger(self, trigger_instance):
            ''' Indicates the analog edge trigger configuration of the specified
                instance.
            '''
            trigger_source_size_out = c_size_t(0)
            trigger_slope = c_int32(0) # EdgeWithEither
            trigger_level = c_double(0)
            trigger_hysteresis = c_double(0)
            status = self.nilcicapi.niVB_MSO_QueryAnalogEdgeTriggerW(self.instrument_handle, c_int32(trigger_instance), None, c_size_t(0), byref(trigger_source_size_out), byref(trigger_slope), byref(trigger_level), byref(trigger_hysteresis))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            trigger_source_size = trigger_source_size_out.value
            trigger_source = (c_wchar * trigger_source_size)()
            status = self.nilcicapi.niVB_MSO_QueryAnalogEdgeTriggerW(self.instrument_handle, c_int32(trigger_instance), byref(trigger_source), c_size_t(trigger_source_size), byref(trigger_source_size_out), byref(trigger_slope), byref(trigger_level), byref(trigger_hysteresis))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return trigger_source.value, EdgeWithEither(trigger_slope.value), trigger_level.value, trigger_hysteresis.value

        def query_digital_edge_trigger(self, trigger_instance):
            ''' Indicates the digital trigger configuration of the specified
                instance.
            '''
            trigger_source_size_out = c_size_t(0)
            trigger_slope = c_int32(0) # EdgeWithEither
            status = self.nilcicapi.niVB_MSO_QueryDigitalEdgeTriggerW(self.instrument_handle, c_int32(trigger_instance), None, c_size_t(0), byref(trigger_source_size_out), byref(trigger_slope))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            trigger_source_size = trigger_source_size_out.value
            trigger_source = (c_wchar * trigger_source_size)()
            status = self.nilcicapi.niVB_MSO_QueryDigitalEdgeTriggerW(self.instrument_handle, c_int32(trigger_instance), byref(trigger_source), c_size_t(trigger_source_size), byref(trigger_source_size_out), byref(trigger_slope))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return trigger_source.value, EdgeWithEither(trigger_slope.value)

        def query_digital_pattern_trigger(self, trigger_instance):
            ''' Indicates the digital pattern trigger configuration of the
                specified instance. A trigger is produced when every level
                (high/low) requirement specified in Trigger Pattern is met, and
                when at least one toggling (toggle/fall/rise) requirement is
                met. If no toggling requirements are set, then only the level
                requirements must be met to produce a trigger.
            '''
            trigger_source_size_out = c_size_t(0)
            trigger_pattern_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_MSO_QueryDigitalPatternTriggerW(self.instrument_handle, c_int32(trigger_instance), None, c_size_t(0), byref(trigger_source_size_out), None, c_size_t(0), byref(trigger_pattern_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            trigger_source_size = trigger_source_size_out.value
            trigger_source = (c_wchar * trigger_source_size)()
            trigger_pattern_size = trigger_pattern_size_out.value
            trigger_pattern = (c_wchar * trigger_pattern_size)()
            status = self.nilcicapi.niVB_MSO_QueryDigitalPatternTriggerW(self.instrument_handle, c_int32(trigger_instance), byref(trigger_source), c_size_t(trigger_source_size), byref(trigger_source_size_out), byref(trigger_pattern), c_size_t(trigger_pattern_size), byref(trigger_pattern_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return trigger_source.value, trigger_pattern.value

        def query_digital_glitch_trigger(self, trigger_instance):
            ''' Indicates the digital glitch trigger configuration of the
                specified instance. A glitch occurs when a channel in Trigger
                Source toggles between two edges of the sample clock. This may
                happen when the sampling rate is less than 1 GHz.
            '''
            trigger_source_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_MSO_QueryDigitalGlitchTriggerW(self.instrument_handle, c_int32(trigger_instance), None, c_size_t(0), byref(trigger_source_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            trigger_source_size = trigger_source_size_out.value
            trigger_source = (c_wchar * trigger_source_size)()
            status = self.nilcicapi.niVB_MSO_QueryDigitalGlitchTriggerW(self.instrument_handle, c_int32(trigger_instance), byref(trigger_source), c_size_t(trigger_source_size), byref(trigger_source_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return trigger_source.value

        def query_trigger_delay(self):
            ''' Indicates the trigger delay setting of the MSO.
            '''
            trigger_delay = c_double(0)
            status = self.nilcicapi.niVB_MSO_QueryTriggerDelay(self.instrument_handle, byref(trigger_delay))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return trigger_delay.value

        def query_analog_pulse_width_trigger(self, trigger_instance):
            ''' Indicates the analog pulse width trigger configuration of the specified
                instance.
            '''
            trigger_source_size_out = c_size_t(0)
            trigger_polarity = c_int32(0)
            trigger_level = c_double(0)
            comparison_mode = c_int32(0)
            lower_limit = c_double(0)
            upper_limit = c_double(0)
            status = self.nilcicapi.niVB_MSO_QueryAnalogPulseWidthTriggerW(self.instrument_handle, c_int32(trigger_instance), None, c_size_t(0), byref(trigger_source_size_out), byref(trigger_polarity), byref(trigger_level), byref(comparison_mode), byref(lower_limit), byref(upper_limit))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            trigger_source_size = trigger_source_size_out.value
            trigger_source = (c_wchar * trigger_source_size)()
            status = self.nilcicapi.niVB_MSO_QueryAnalogPulseWidthTriggerW(self.instrument_handle, c_int32(trigger_instance), byref(trigger_source), c_size_t(trigger_source_size), byref(trigger_source_size_out), byref(trigger_polarity), byref(trigger_level), byref(comparison_mode), byref(lower_limit), byref(upper_limit))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return trigger_source.value, MsoTriggerPolarity(trigger_polarity.value), trigger_level.value, MsoComparisonMode(comparison_mode.value), lower_limit.value, upper_limit.value

        def query_digital_pulse_width_trigger(self, trigger_instance):
            ''' Indicates the digital pulse width trigger configuration of the specified
                instance.
            '''
            trigger_source_size_out = c_size_t(0)
            trigger_polarity = c_int32(0)
            trigger_level = c_double(0)
            comparison_mode = c_int32(0)
            lower_limit = c_double(0)
            upper_limit = c_double(0)
            status = self.nilcicapi.niVB_MSO_QueryDigitalPulseWidthTriggerW(self.instrument_handle, c_int32(trigger_instance), None, c_size_t(0), byref(trigger_source_size_out), byref(trigger_polarity), byref(comparison_mode), byref(lower_limit), byref(upper_limit))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            trigger_source_size = trigger_source_size_out.value
            trigger_source = (c_wchar * trigger_source_size)()
            status = self.nilcicapi.niVB_MSO_QueryDigitalPulseWidthTriggerW(self.instrument_handle, c_int32(trigger_instance), byref(trigger_source), c_size_t(trigger_source_size), byref(trigger_source_size_out), byref(trigger_polarity), byref(comparison_mode), byref(lower_limit), byref(upper_limit))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return trigger_source.value, MsoTriggerPolarity(trigger_polarity.value), MsoComparisonMode(comparison_mode.value), lower_limit.value, upper_limit.value

        def query_acquisition_status(self):
            ''' Returns the status of a completed or ongoing acquisition.
            '''
            acquisition_status = c_int32(0) # MsoAcquisitionStatus
            status = self.nilcicapi.niVB_MSO_QueryAcquisitionStatus(self.instrument_handle, byref(acquisition_status))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return MsoAcquisitionStatus(acquisition_status.value)

        def run(self, autoTrigger = True):
            ''' Transitions the acquisition from the Stopped state to the
                Running state. If the current state is Triggered, the
                acquisition is first transitioned to the Stopped state before
                transitioning to the Running state. This method returns an
                error if too much power is applied to any enabled channel.
            '''
            status = self.nilcicapi.niVB_MSO_Run(self.instrument_handle, c_bool(autoTrigger))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def force_trigger(self):
            ''' Causes a software-timed trigger to occur after the pretrigger
                time has expired.
            '''
            status = self.nilcicapi.niVB_MSO_ForceTrigger(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def stop(self):
            ''' Transitions the acquisition from either the Triggered or Running
                state to the Stopped state.
            '''
            status = self.nilcicapi.niVB_MSO_Stop(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def read_analog(self, data_size):
            ''' Transfers data from the instrument as long as the acquisition
                state is Acquisition Complete. If the state is either Running or
                Triggered, this method will wait until the state transitions to
                Acquisition Complete. If the state is Stopped, this method
                returns an error.
            '''
            data = (c_double * data_size)()
            data_size_out = c_size_t(0)
            data_stride = c_size_t(0)
            initial_timestamp = Timestamp(0, 0, 0, 0)
            trigger_timestamp = Timestamp(0, 0, 0, 0)
            trigger_reason = c_int32(0) # MsoTriggerReason
            status = self.nilcicapi.niVB_MSO_ReadAnalog(self.instrument_handle,
                                                        byref(data), c_size_t(data_size), byref(data_size_out),
                                                        byref(data_stride), byref(initial_timestamp), byref(trigger_timestamp), byref(trigger_reason))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return data.value, data_stride.value, initial_timestamp, trigger_timestamp, MsoTriggerReason(trigger_reason.value)

        def read_digital_u64(self, data_size, sample_timestamps_size):
            ''' Transfers data from the instrument as long as the acquisition
                state is Acquisition Complete. If the state is either Running or
                Triggered, this method will wait until the state transitions to
                Acquisition Complete. If the state is Stopped, this method
                returns an error.
            '''
            data = (c_uint64 * data_size)()
            data_size_out = c_size_t(0)
            sampleTimestamps = (c_int32 * sample_timestamps_size)()
            sampleTimestampsSizeOut = c_size_t(0)
            initial_timestamp = Timestamp(0, 0, 0, 0)
            trigger_timestamp = Timestamp(0, 0, 0, 0)
            trigger_reason = c_int32(0) # MsoTriggerReason
            status = self.nilcicapi.niVB_MSO_ReadDigitalU64(self.instrument_handle, byref(data),
                                                            c_size_t(data_size), byref(data_size_out),
                                                            byref(sampleTimestamps), c_size_t(sample_timestamps_size), byref(sampleTimestampsSizeOut),
                                                            byref(initial_timestamp), byref(trigger_timestamp), byref(trigger_reason))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return data.value, sampleTimestamps.value, initial_timestamp, trigger_timestamp, MsoTriggerReason(trigger_reason.value)

        def read_analog_digital_u64(self):
            ''' Transfers data from the instrument as long as the acquisition
                state is Acquisition Complete. If the state is either Running or
                Triggered, this method will wait until the state transitions to
                Acquisition Complete. If the state is Stopped, this method
                returns an error.
            '''
            analog_data_size_out = c_size_t(0)
            digital_data_size_out = c_size_t(0)
            digital_timestamps_size_out = c_size_t(0)

            status = self.nilcicapi.niVB_MSO_ReadAnalogDigitalU64(
                    self.instrument_handle,         # niVB_MSO_InstrumentHandle instrumentHandle
                    None,                           # double* analogData
                    c_size_t(0),                    # size_t analogDataSize
                    byref(analog_data_size_out),    # size_t* analogDataSizeOut
                    None,                           # size_t* analogDataStride
                    None,                           # niVB_Timestamp* analogInitialTimestamp
                    None,                           # uint64_t* digitalData
                    c_size_t(0),                    # size_t digitalDataSize
                    byref(digital_data_size_out),   # size_t* digitalDataSizeOut
                    None,                           # uint32_t* digitalSampleTimestamps
                    c_size_t(0),                    # size_t digitalSampleTimestampsSize
                    byref(digital_timestamps_size_out), # size_t* digitalSampleTimestampsSizeOut
                    None,                           # niVB_Timestamp* digitalInitialTimestamp
                    None,                           # niVB_Timestamp* trigger_timestamp
                    None)                           # niVB_MSO_TriggerReason* trigger_reason
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

            analog_data_size = analog_data_size_out.value
            digital_data_size = digital_data_size_out.value
            digital_timestamps_size = digital_timestamps_size_out.value

            analog_data_out = []
            digital_data_out = []
            digital_timestamps_out = []

            analog_data = (c_double * analog_data_size)()
            digital_data = (c_uint64 * digital_data_size)()
            digital_timestamps = (c_uint32 * digital_timestamps_size)()

            analog_data_stride = c_size_t(0)
            analog_t0 = Timestamp(0, 0, 0, 0)
            digital_t0 = Timestamp(0, 0, 0, 0)
            trigger_timestamp = Timestamp(0, 0, 0, 0)
            trigger_reason = c_int32(0) # MsoTriggerReason

            status = self.nilcicapi.niVB_MSO_ReadAnalogDigitalU64(
                    self.instrument_handle,           # niVB_MSO_InstrumentHandle instrumentHandle
                    byref(analog_data),               # double* analogData
                    c_size_t(analog_data_size),       # size_t analogDataSize
                    None,                             # size_t* analog_data_size_out
                    byref(analog_data_stride),        # size_t* analogDataStride
                    byref(analog_t0),                 # niVB_Timestamp* analogInitialTimestamp
                    byref(digital_data),              # uint64_t* digitalData
                    c_size_t(digital_data_size),      # size_t digitalDataSize
                    None,                             # size_t* digital_data_size_out
                    byref(digital_timestamps),        # uint32_t* digitalSampleTimestamps
                    c_size_t(digital_timestamps_size),# size_t digitalSampleTimestampsSize
                    None,                             # size_t* digitalSampleTimestampsSizeOut
                    byref(digital_t0),                # niVB_Timestamp* digitalInitialTimestamp
                    byref(trigger_timestamp),         # niVB_Timestamp* trigger_timestamp
                    byref(trigger_reason))            # niVB_MSO_TriggerReason* trigger_reason
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            for i in range(analog_data_size): analog_data_out.append(analog_data[i])
            for i in range(digital_data_size): digital_data_out.append(digital_data[i])
            for i in range(digital_timestamps_size): digital_timestamps_out.append(digital_timestamps[i])
            return analog_data_out, analog_data_stride.value, analog_t0, digital_data_out, digital_timestamps_out, digital_t0, trigger_timestamp, MsoTriggerReason(trigger_reason.value)

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
                the device and driver software to a known state.
            '''
            status = self.nilcicapi.niVB_MSO_ResetInstrument(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def export_configuration(self, configuration_filename):
            ''' Exports a configuration file for use with the MSO.
            '''
            status = self.nilcicapi.niVB_MSO_ExportConfigurationW(self.instrument_handle, c_wchar_p(configuration_filename))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def import_configuration(self, configuration_filename):
            ''' Imports a configuration file for use with the MSO. You can
                import PNG files exported from the VirtualBench Application or
                files created from MSO Export Configuration.
            '''
            status = self.nilcicapi.niVB_MSO_ImportConfigurationW(self.instrument_handle, c_wchar_p(configuration_filename))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

#------------------------------------------------------------------------------

    def get_mixed_signal_oscilloscope_calibration_adjustment_information(self, device_name = ''):
        ''' Returns instrument information from the last successful calibration
            adjustment.
        '''
        local_device_name = device_name if device_name else self.device_name
        adjustment_date = Timestamp(0, 0, 0, 0)
        adjustment_temperature = c_double(0)
        status = self.nilcicapi.niVB_MSO_GetCalibrationAdjustmentInformationW(self.library_handle, c_wchar_p(local_device_name), byref(adjustment_date), byref(adjustment_temperature))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return adjustment_date, adjustment_temperature.value

    def acquire_mixed_signal_oscilloscope_calibration(self, device_name = '', password = ''):
        ''' Opens a calibration session with the instrument. The instrument is
            reset upon successful completion of this method. This method returns
            an error if the instrument is reserved or if Password is incorrect.
        '''
        return self.MixedSignalOscilloscopeCalibration(self, device_name, password)

    class MixedSignalOscilloscopeCalibration(object):
        def __init__(self, outer, device_name, password):
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.device_name = device_name if device_name else outer.device_name
            self.instrument_handle = c_sysint(0)
            status = self.nilcicapi.niVB_MSO_InitializeCalibrationW(self.library_handle, c_wchar_p(self.device_name), c_wchar_p(password), self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self, calibration_action = CalibrationAction.COMMIT):
            ''' Closes the calibration session, then resets the device.
            '''
            status = self.nilcicapi.niVB_MSO_CloseCalibration(self.instrument_handle, c_int32(calibration_action))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def adjust_offset_calibration(self, channel):
            ''' Grounds the input to the specified Channel. You must run this
                method as the first step of adjustment.
            '''
            status = self.nilcicapi.niVB_MSO_AdjustOffsetCalibrationW(self.instrument_handle, c_wchar_p(channel))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def get_compensator_attenuation_calibration_adjustment_points(self):
            ''' Returns the configuration values necessary for MSO Adjust
                Compensator Attenuation. Each element of the Range, Amplitude,
                and Frequency arrays correspond to each other.
            '''
            range_data_size_out = c_size_t(0)
            amplitude_size_out = c_size_t(0)
            frequency_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_MSO_GetCompensatorAttenuationCalibrationAdjustmentPoints(self.instrument_handle, None, c_size_t(0), byref(range_data_size_out), None, c_size_t(0), byref(amplitude_size_out), None, c_size_t(0), byref(frequency_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            range_data_size = c_size_t(range_data_size_out.value)
            amplitude_size = c_size_t(amplitude_size_out.value)
            frequency_size = c_size_t(frequency_size_out.value)

            range_data_out = []
            amplitude_out = []
            frequency_out = []

            range_data = (c_double * range_data_size)()
            amplitude = (c_double * amplitude_size)()
            frequency = (c_double * frequency_size)()

            status = self.nilcicapi.niVB_MSO_GetCompensatorAttenuationCalibrationAdjustmentPoints(self.instrument_handle, byref(range_data), c_size_t(range_data_size), byref(range_data_size_out), byref(amplitude), c_size_t(amplitude_size), byref(amplitude_size_out), byref(frequency), c_size_t(frequency_size), byref(frequency_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            for i in range(range_data_size_out.value): range_data_out.append(range_data[i])
            for i in range(amplitude_size_out.value): amplitude_out.append(amplitude[i])
            for i in range(frequency_size_out.value): frequency_out.append(frequency[i])
            return range_data_out, amplitude_out, frequency_out

        def adjust_compensator_attenuation_calibration(self, channel, range_data, amplitude, frequency):
            ''' Adjusts the compensator attenuation using the values from MSO
                Get Compensator Attenuation Adjustment Points.
            '''
            status = self.nilcicapi.niVB_MSO_AdjustCompensatorAttenuationCalibrationW(self.instrument_handle, c_wchar_p(channel), c_double(range_data), c_double(amplitude), c_double(frequency))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def get_range_calibration_adjustment_points(self):
            ''' Returns the adjustment points and range_data values needed to sweep
                the instrument for adjustment.
            '''
            range_data_size_out = c_size_t(0)
            adjustment_point_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_MSO_GetRangeCalibrationAdjustmentPoints(self.instrument_handle, None, c_size_t(0), byref(range_data_size_out), None, c_size_t(0), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            range_data_size = c_size_t(range_data_size_out.value)
            adjustment_point_size = c_size_t(adjustment_point_size_out.value)
            range_data = (c_double * range_data_size)()
            adjustment_point = (c_double * adjustment_point_size)()
            status = self.nilcicapi.niVB_MSO_GetRangeCalibrationAdjustmentPoints(self.instrument_handle, byref(range_data), c_size_t(range_data_size), byref(range_data_size_out), byref(adjustment_point), c_size_t(adjustment_point_size), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return range_data.value, adjustment_point.value

        def adjust_range_calibration(self, channel, range_data, adjustment_point):
            ''' Adjusts the range_data calibration using the values returned by MSO
                Get Range Adjustment Points. This method returns an error if it
                is run before MSO Adjust Compensator Attenuation.
            '''
            status = self.nilcicapi.niVB_MSO_AdjustRangeCalibrationW(self.instrument_handle, c_wchar_p(channel), c_double(range_data), c_double(adjustment_point))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def get_offset_dac_calibration_adjustment_points(self):
            ''' Returns the adjustment point and range_data values necessary for MSO
                Adjust Offset DAC Calibration. Each element of the Range and
                Adjustment Point arrays correspond to each other.
            '''
            range_data_size_out = c_size_t(0)
            adjustment_point_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_MSO_GetOffsetDACCalibrationAdjustmentPoints(self.instrument_handle, None, c_size_t(0), byref(range_data_size_out), None, c_size_t(0), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            range_data_size = c_size_t(range_data_size_out.value)
            range_data = (c_double * range_data_size)()
            adjustment_point_size = c_size_t(adjustment_point_size_out.value)
            adjustment_point = (c_double * adjustment_point_size)()
            status = self.nilcicapi.niVB_MSO_GetOffsetDACCalibrationAdjustmentPoints(self.instrument_handle, byref(range_data), c_size_t(range_data_size), byref(range_data_size_out), byref(adjustment_point), c_size_t(adjustment_point_size), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return range_data.value, adjustment_point.value

        def adjust_offset_dac_calibration(self, channel, range_data, adjustment_point):
            ''' Configures the instrument on the specified channel using the
                values obtained by MSO Get Offset DAC Calibration Adjustment
                Points. This method returns an error if it is run before MSO
                Adjust Offset Calibration.
            '''
            status = self.nilcicapi.niVB_MSO_AdjustOffsetDACCalibrationW(self.instrument_handle, c_wchar_p(channel), c_double(range_data), c_double(adjustment_point))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

#------------------------------------------------------------------------------

    def acquire_digital_multimeter(self, device_name = '', reset = True):
        ''' Establishes communication with the device. This method should be
            called once per session.
        '''
        return self.DigitalMultimeter(self, device_name, reset)

    class DigitalMultimeter(object):
        def __init__(self, outer, device_name, reset):
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.device_name = device_name if device_name else outer.device_name
            self.instrument_handle = c_sysint(0)
            status = self.nilcicapi.niVB_DMM_InitializeW(self.library_handle, c_wchar_p(self.device_name), c_bool(reset), byref(self.instrument_handle))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self):
            ''' Stops the session and deallocates any resources acquired during
                the session.
            '''
            status = self.nilcicapi.niVB_DMM_Close(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def configure_measurement(self, dmm_function, auto_range = True, manual_range = 1.0):
            ''' Configures the instrument to take a DMM measurement.
            '''
            status = self.nilcicapi.niVB_DMM_ConfigureMeasurement(self.instrument_handle, c_int32(dmm_function), c_int32(auto_range), c_double(manual_range))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_dc_voltage(self, dmm_input_resistance):
            ''' Configures DC voltage measurement specifications for the DMM.
            '''
            status = self.nilcicapi.niVB_DMM_ConfigureDCVoltage(self.instrument_handle, c_int32(dmm_input_resistance))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_dc_current(self, auto_range_terminal):
            ''' Configures DC current measurement specifications for the DMM.
            '''
            status = self.nilcicapi.niVB_DMM_ConfigureDCCurrent(self.instrument_handle, c_int32(auto_range_terminal))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_ac_current(self, auto_range_terminal):
            ''' Configures AC current measurement specifications for the DMM.
            '''
            status = self.nilcicapi.niVB_DMM_ConfigureACCurrent(self.instrument_handle, c_int32(auto_range_terminal))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def query_measurement(self, dmm_function):
            ''' Indicates the measurement settings for the instrument.
            '''
            auto_range = c_bool(0)
            range_data = c_double(0)
            status = self.nilcicapi.niVB_DMM_QueryMeasurement(self.instrument_handle, c_int32(dmm_function), byref(auto_range), byref(range_data))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return auto_range.value, range_data.value

        def query_dc_voltage(self):
            ''' Indicates the settings for a DC voltage measurement.
            '''
            dmm_input_resistance = c_int32(0) # DmmInputResistance
            status = self.nilcicapi.niVB_DMM_QueryDCVoltage(self.instrument_handle, byref(dmm_input_resistance))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return DmmInputResistance(dmm_input_resistance.value)

        def query_dc_current(self):
            ''' Indicates the settings for a DC current measurement.
            '''
            auto_range_dmm_current_terminal = c_int32(0) # DmmCurrentTerminal
            status = self.nilcicapi.niVB_DMM_QueryDCCurrent(self.instrument_handle, byref(auto_range_dmm_current_terminal))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return DmmCurrentTerminal(auto_range_dmm_current_terminal.value)

        def query_ac_current(self):
            ''' Indicates the settings for a AC current measurement.
            '''
            auto_range_dmm_current_terminal = c_int32(0) # DmmCurrentTerminal
            status = self.nilcicapi.niVB_DMM_QueryACCurrent(self.instrument_handle, byref(auto_range_dmm_current_terminal))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return DmmCurrentTerminal(auto_range_dmm_current_terminal.value)

        def read(self):
            ''' Reads the data from the instrument.
            '''
            measurement = c_double(0)
            status = self.nilcicapi.niVB_DMM_Read(self.instrument_handle, byref(measurement))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return measurement.value

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
                the device and driver software to a known state.
            '''
            status = self.nilcicapi.niVB_DMM_ResetInstrument(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def export_configuration(self, configuration_filename):
            ''' Exports a configuration file for use with the DMM.
            '''
            status = self.nilcicapi.niVB_DMM_ExportConfigurationW(self.instrument_handle, configuration_filename)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def import_configuration(self, configuration_filename):
            ''' Imports a configuration file for use with the DMM. You can
                import PNG files exported from the VirtualBench Application or
                files created from DMM Export Configuration.
            '''
            status = self.nilcicapi.niVB_DMM_ImportConfigurationW(self.instrument_handle, configuration_filename)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

#------------------------------------------------------------------------------

    def get_digital_multimeter_calibration_adjustment_information(self, device_name = ''):
        ''' Returns instrument information from the last successful calibration
            adjustment.
        '''
        local_device_name = device_name if device_name else self.device_name
        adjustment_date = Timestamp()
        adjustment_temperature = c_double(0)
        status = self.nilcicapi.niVB_DMM_GetCalibrationAdjustmentInformationW(self.library_handle, c_wchar_p(local_device_name), byref(adjustment_date), byref(adjustment_temperature))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return adjustment_date, adjustment_temperature.value

    def acquire_digital_multimeter_calibration(self, device_name = '', password = ''):
        ''' Opens a calibration session with the instrument. The instrument is
            reset upon successful completion of this method. This method returns
            an error if the instrument is reserved or if Password is incorrect.
        '''
        return self.DigitalMultimeterCalibration(self, device_name, password)

    class DigitalMultimeterCalibration(object):
        def __init__(self, outer, device_name, password):
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.device_name = device_name if device_name else outer.device_name
            self.instrument_handle = c_sysint(0)
            status = self.nilcicapi.niVB_DMM_InitializeCalibrationW(self.library_handle, c_wchar_p(self.device_name), c_wchar_p(password), self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self, calibration_action = CalibrationAction.COMMIT):
            ''' Closes the calibration session, then resets the device.
            '''
            status = self.nilcicapi.niVB_DMM_CloseCalibration(self.instrument_handle, calibration_action)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def get_dc_voltage_calibration_adjustment_points(self):
            ''' Returns the adjustment point and range configurations needed to
                sweep the DMM for DC voltage adjustment.
            '''
            range_data_size_out = c_size_t(0)
            adjustment_point_size_out =  c_size_t(0)
            status = self.nilcicapi.niVB_DMM_GetDCVoltageCalibrationAdjustmentPoints(self.instrument_handle, None, c_size_t(0), byref(range_data_size_out), None, c_size_t(0), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            range_data_size = c_size_t(range_data_size_out.value)
            range_data = (c_double * range_data_size)()
            adjustment_point_size = c_size_t(adjustment_point_size_out.value)
            adjustment_point = (c_double * adjustment_point_size)()
            status = self.nilcicapi.niVB_DMM_GetDCVoltageCalibrationAdjustmentPoints(self.instrument_handle, byref(range_data), c_size_t(range_data_size), byref(range_data_size_out), byref(adjustment_point), c_size_t(adjustment_point_size), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return range_data.value, adjustment_point.value

        def adjust_dc_voltage_calibration(self, range_data, adjustment_point):
            ''' Measures and stores the reference value for the specified
                Adjustment Point and Range with the DMM. Specify these values in
                the order returned by DMM  Get DC Voltage Calibration Adjustment
                Points.
            '''
            status = self.nilcicapi.niVB_DMM_AdjustDCVoltageCalibration(self.instrument_handle, c_double(range_data), c_double(adjustment_point))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def get_ac_voltage_calibration_adjustment_points(self):
            ''' Returns the adjustment point and range configurations needed to
                sweep the DMM for AC voltage adjustment.
            '''
            range_data_size_out = c_size_t(0)
            adjustment_point_size_out = c_size_t(0)
            frequency_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_DMM_GetACVoltageCalibrationAdjustmentPoints(self.instrument_handle, None, c_size_t(0), byref(range_data_size_out), None, c_size_t(0), byref(adjustment_point_size_out), None, c_size_t(0), byref(frequency_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            range_data_size = c_size_t(range_data_size_out.value)
            range_data = (c_double * range_data_size)()
            adjustment_point_size = c_size_t(adjustment_point_size_out.value)
            adjustment_point = (c_double * adjustment_point_size)()
            frequency_size = c_size_t(frequency_size_out.value)
            frequency = (c_double * frequency_size)()
            status = self.nilcicapi.niVB_DMM_GetACVoltageCalibrationAdjustmentPoints(self.instrument_handle, byref(range_data), c_size_t(range_data_size), byref(range_data_size_out), byref(adjustment_point), c_size_t(adjustment_point_size), byref(adjustment_point_size_out), byref(frequency), c_size_t(frequency_size), byref(frequency_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return range_data.value, adjustment_point.value, frequency.value

        def adjust_ac_voltage_calibration(self, range_data, adjustment_point, frequency):
            ''' Measures and stores the reference value for the specified
                Adjustment Point, Range, and Frequency with the DMM. Specify
                these values in the order returned by DMM Get AC Voltage
                Calibration Adjustment Points. This method returns an error if
                it is run before DMM Adjust Resistance Calibration.
            '''
            status = self.nilcicapi.niVB_DMM_AdjustACVoltageCalibration(self.instrument_handle, c_double(range_data), c_double(adjustment_point), c_double(frequency))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def get_current_calibration_adjustionment_points(self):
            ''' Returns the adjustment point and range_data configurations needed to
                sweep the DMM for current adjustment.
            '''
            range_data_size_out = c_size_t(0)
            adjustment_point_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_DMM_GetCurrentCalibrationAdjustmentPoints(self.instrument_handle, None, c_size_t(0), byref(range_data_size_out), None, c_size_t(0), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            range_data_size = c_size_t(range_data_size_out.value)
            range_data = (c_double * range_data_size)()
            adjustment_point_size = c_size_t(adjustment_point_size_out.value)
            adjustment_point = (c_double * adjustment_point_size)()
            status = self.nilcicapi.niVB_DMM_GetCurrentCalibrationAdjustmentPoints(self.instrument_handle, byref(range_data), c_size_t(range_data_size), byref(range_data_size_out), byref(adjustment_point), c_size_t(adjustment_point_size), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return range_data.value, adjustment_point.value

        def adjust_current_calibration(self, range_data, adjustment_point):
            ''' Measures and stores the reference value for the specified
                Adjustment Point and Range with the DMM. Specify these values in
                the order returned by DMM Get Current Calibration Adjustment
                Points. This method returns an error if it is run before DMM
                Adjust AC Voltage Calibration.
            '''
            status = self.nilcicapi.niVB_DMM_AdjustCurrentCalibration(self.instrument_handle, c_double(range_data), c_double(adjustment_point))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def get_resistance_calibration_adjustment_points(self):
            ''' Returns the adjustment point and range_data configurations needed to
                sweep the DMM for resistance adjustment.
            '''
            range_data_size_out = c_size_t(0)
            adjustment_point_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_DMM_GetResistanceCalibrationAdjustmentPoints(self.instrument_handle, None, c_size_t(0), byref(range_data_size_out), None, c_size_t(0), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            range_data_size = c_size_t(range_data_size_out.value)
            range_data = (c_double * range_data_size)()
            adjustment_point_size = c_size_t(adjustment_point_size_out.value)
            adjustment_point = (c_double * adjustment_point_size)()
            status = self.nilcicapi.niVB_DMM_GetResistanceCalibrationAdjustmentPoints(self.instrument_handle, byref(range_data), c_size_t(range_data_size), byref(range_data_size_out), byref(adjustment_point), c_size_t(adjustment_point_size), byref(adjustment_point_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return range_data.value, adjustment_point.value

        def setup_resistance_calibration(self, range_data):
            ''' Configures the DMM to use the specified resistance range_data and
                places the DMM in resistance mode.
            '''
            status = self.nilcicapi.niVB_DMM_SetupResistanceCalibration(self.instrument_handle, c_double(range_data))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def adjust_resistance_calibration(self, adjustment_point):
            ''' Measures and stores the reference value for the specified
                Adjustment Point with the DMM. Specify these values in the order
                returned by DMM Get Resistance Calibration Adjustment Points.
                This method returns an error if it is run before DMM Setup
                Resistance Calibration.
            '''
            status = self.nilcicapi.niVB_DMM_AdjustResistanceCalibration(self.instrument_handle, c_double(adjustment_point))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

#------------------------------------------------------------------------------

    def acquire_power_supply(self, device_name = '', reset = True):
        ''' Establishes communication with the power supply device. This method
            should be called once per session.
        '''
        return self.PowerSupply(self, device_name, reset)

    class PowerSupply(object):
        def __init__(self, outer, device_name, reset):
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.device_name = device_name if device_name else outer.device_name
            self.instrument_handle = c_sysint(0)
            status = self.nilcicapi.niVB_PS_InitializeW(self.library_handle, c_wchar_p(self.device_name), c_bool(reset), byref(self.instrument_handle))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self):
            ''' Stops the session and deallocates any resources acquired during
                the session. If output is enabled on any channels, they remain
                in their current state and continue to output data.
            '''
            status = self.nilcicapi.niVB_PS_Close(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def configure_voltage_output(self, channel, voltage_level, current_limit):
            ''' Configures a voltage output on the specified channel. This
                method should be called once for every channel you want to
                configure to output voltage.
            '''
            status = self.nilcicapi.niVB_PS_ConfigureVoltageOutputW(self.instrument_handle, channel, c_double(voltage_level), c_double(current_limit))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def configure_current_output(self, channel, current_level, voltage_limit):
            ''' Configures a current output on the specified channel. This
                method should be called once for every channel you want to
                configure to output current.
            '''
            status = self.nilcicapi.niVB_PS_ConfigureCurrentOutputW(self.instrument_handle, channel, c_double(current_level), c_double(voltage_limit))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def enable_tracking(self, enable_tracking):
            ''' Enables or disables tracking between the positive and negative
                25V channels. If enabled, any configuration change on the
                positive 25V channel is mirrored to the negative 25V channel,
                and any writes to the negative 25V channel are ignored.
            '''
            status = self.nilcicapi.niVB_PS_EnableTracking(self.instrument_handle, c_bool(enable_tracking))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def enable_all_outputs(self, enable_outputs):
            ''' Enables or disables all outputs on all channels of the
                instrument.
            '''
            status = self.nilcicapi.niVB_PS_EnableAllOutputs(self.instrument_handle, c_bool(enable_outputs))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def query_voltage_output(self, channel):
            ''' Indicates the voltage output settings on the specified channel.
            '''
            voltage_level = c_double(0)
            current_limit = c_double(0)
            status = self.nilcicapi.niVB_PS_QueryVoltageOutputW(self.instrument_handle, channel, byref(voltage_level), byref(current_limit))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return voltage_level.value, current_limit.value

        def query_current_output(self, channel):
            ''' Indicates the current output settings on the specified channel.
            '''
            current_level = c_double(0)
            voltage_limit = c_double(0)
            status = self.nilcicapi.niVB_PS_QueryCurrentOutputW(self.instrument_handle, channel, byref(current_level), byref(voltage_limit))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return current_level.value, voltage_limit.value

        def query_outputs_enabled(self):
            ''' Indicates whether the outputs are enabled for the instrument.
            '''
            outputs_enabled = c_bool(0)
            status = self.nilcicapi.niVB_PS_QueryOutputsEnabled(self.instrument_handle, byref(outputs_enabled))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return outputs_enabled.value

        def query_tracking(self):
            ''' Indicates whether voltage tracking is enabled on the instrument.
            '''
            tracking_enabled = c_bool(0)
            status = self.nilcicapi.niVB_PS_QueryTracking(self.instrument_handle, byref(tracking_enabled))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return tracking_enabled.value

        def read_output(self, channel):
            ''' Reads the voltage and current levels of the specified channel.
            '''
            actual_voltage_level = c_double(0)
            actual_current_level = c_double(0)
            ps_state = c_int32(0) # PsState
            status = self.nilcicapi.niVB_PS_ReadOutputW(self.instrument_handle, channel, byref(actual_voltage_level), byref(actual_current_level), byref(ps_state))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return actual_voltage_level.value, actual_current_level.value, PsState(ps_state.value)

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
                the device and driver software to a known state.
            '''
            status = self.nilcicapi.niVB_PS_ResetInstrument(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def export_configuration(self, configuration_filename):
            ''' Exports a configuration file for use with the power supply.
            '''
            status = self.nilcicapi.niVB_PS_ExportConfigurationW(self.instrument_handle, configuration_filename)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def import_configuration(self, configuration_filename):
            ''' Imports a configuration file for use with the power supply. You
                can import PNG files exported from the VirtualBench Application
                or files created from PS Export Configuration.
            '''
            status = self.nilcicapi.niVB_PS_ImportConfigurationW(self.instrument_handle, configuration_filename)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

#------------------------------------------------------------------------------

    def get_power_supply_calibration_adjustment_information(self, device_name = ''):
        ''' Returns instrument information from the last successful calibration
            adjustment.
        '''
        local_device_name = device_name if device_name else self.device_name
        adjustment_date = Timestamp()
        adjustment_temperature = c_double(0)
        status = self.nilcicapi.niVB_PS_GetCalibrationAdjustmentInformationW(self.library_handle, c_wchar_p(local_device_name),  byref(adjustment_date),  byref(adjustment_temperature))
        if (status != Status.SUCCESS):
            raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        return adjustment_date, adjustment_temperature.value

    def acquire_power_supply_calibration(self, device_name = '', ps_cal_type = PsCalType.VOLTAGE, password = ''):
        ''' Opens a calibration session with the instrument. The instrument is
            reset upon successful completion of this method. This method returns
            an error if the instrument is reserved or if Password is incorrect.
        '''
        return self.PowerSupplyCalibration(self, device_name, ps_cal_type, password)

    class PowerSupplyCalibration(object):
        def __init__(self, outer, device_name, ps_cal_type, password):
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.device_name = device_name if device_name else outer.device_name
            self.instrument_handle = c_sysint(0)
            status = self.nilcicapi.niVB_PS_InitializeCalibration(self.library_handle, c_wchar_p(self.device_name), c_int32(ps_cal_type), c_wchar_p(password), self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self, calibration_action = CalibrationAction.COMMIT):
            ''' Closes the calibration session, then resets the device.
            '''
            status = self.nilcicapi.niVB_PS_CloseCalibration(self.instrument_handle, c_int32(calibration_action))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def get_adjustment_points(self, channel):
            ''' Returns the adjustment points needed to sweep the instrument for
                adjustment on the specified Channel.
            '''
            adjustment_points_size_out = c_size_t(0)
            status = self.nilcicapi.niVB_PS_GetAdjustmentPointsW(self.instrument_handle, c_wchar_p(channel), None, c_size_t(0), byref(adjustment_points_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            adjustment_points_size = c_size_t(adjustment_points_size_out.value)
            adjustment_points = (c_double * adjustment_points_size)()
            status = self.nilcicapi.niVB_PS_GetAdjustmentPointsW(self.instrument_handle, c_wchar_p(channel), byref(adjustment_points), c_size_t(adjustment_points_size), byref(adjustment_points_size_out))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return adjustment_points.value;

        def set_adjustment_point(self, channel, adjustment_point):
            ''' Sets the calibration adjustment point for the specified Channel.
            '''
            status = self.nilcicapi.niVB_PS_SetAdjustmentPointW(self.instrument_handle, c_wchar_p(channel), c_double(adjustment_point))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def measure_adjustment_point(self, channel, reference_value):
            ''' Measures the adjustment points for the specified Channel given a
                measured Reference Value.
            '''
            status = self.nilcicapi.niVB_PS_MeasureAdjustmentPointW(self.instrument_handle, c_wchar_p(channel), c_double(reference_value))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

#------------------------------------------------------------------------------

    def acquire_serial_peripheral_interface(self, bus, reset = True):
        ''' Creates and returns a new VirtualBench SPI session on the SPI engine
            for the device. The session is used in all subsequent VirtualBench
            SPI method calls. This method should be called once per session.

            SPI bus mastering—You can use VirtualBench’s digital I/O to
            interface to serial peripherals. When you configure a SPI bus, a set
            of lines are reserved for the bus and each line's direction is
            automatically configured.

            spi/0 bus
            dig/0: Clock output
            dig/1: MOSI (Master Out Slave In)
            dig/2: MISO (Master In Slave Out)
            dig/3: CS (Chip Select) output
        '''
        return self.SerialPeripheralInterface(self, bus, reset)

    class SerialPeripheralInterface(object):
        def __init__(self, outer, bus, reset):
            self.bus = bus
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.instrument_handle = c_sysint(0)
            status = self.nilcicapi.niVB_SPI_InitializeW(self.library_handle, c_wchar_p(self.bus), c_bool(reset), byref(self.instrument_handle))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self):
            ''' Closes the session specified in Instrument Handle In.
            '''
            status = self.nilcicapi.niVB_SPI_Close(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def configure_bus(self, clock_rate, clock_polarity, clock_phase, chip_select_polarity):
            ''' Configures the basic parameters of the SPI engine.
            '''
            status = self.nilcicapi.niVB_SPI_ConfigureBus(self.instrument_handle, c_double(clock_rate), c_int32(clock_polarity), c_int32(clock_phase), c_int32(chip_select_polarity))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def query_bus_configuration(self):
            ''' Indicates the current basic configuration of the SPI engine.
            '''
            clock_rate = c_double(0)
            clock_polarity = c_int32(0) # Polarity
            clock_phase = c_int32(0) # ClockPhase
            chip_select_polarity = c_int32(0) # Polarity
            status = self.nilcicapi.niVB_SPI_QueryBusConfiguration(self.instrument_handle, byref(clock_rate), byref(clock_polarity), byref(clock_phase), byref(chip_select_polarity))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return clock_rate.value, Polarity(clock_polarity.value), ClockPhase(clock_phase.value), Polarity(chip_select_polarity.value)

        def write_read(self, write_data, bytes_per_frame, read_data_size):
            ''' Completes a transaction on the bus by writing the provided data
                to MOSI and returning the data read on MISO.
            '''
            read_data_out = []
            read_data = (c_uint8 * read_data_size)()
            local_write_data = (c_uint8 * len(write_data))(*write_data)
            status = self.nilcicapi.niVB_SPI_WriteRead(self.instrument_handle, local_write_data, c_size_t(len(local_write_data)), c_int32(bytes_per_frame), byref(read_data), c_size_t(read_data_size))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            for i in range(read_data_size): read_data_out.append(read_data[i])
            return read_data_out

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
                the device and driver software to a known state.
            '''
            status = self.nilcicapi.niVB_SPI_ResetInstrument(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def export_configuration(self, configuration_filename):
            ''' Exports the current configuration of the instrument to a file.
            '''
            status = self.nilcicapi.niVB_SPI_ExportConfigurationW(self.instrument_handle, c_wchar_p(configuration_filename))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def import_configuration(self, configuration_filename):
            ''' Imports a configuration file for use with the SPI engine. You
                can import PNG files exported from the VirtualBench Application
                or files created from SPI Export Configuration.
            '''
            status = self.nilcicapi.niVB_SPI_ImportConfigurationW(self.instrument_handle, c_wchar_p(configuration_filename))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

#------------------------------------------------------------------------------

    def acquire_inter_integrated_circuit(self, bus, reset = True):
        ''' Creates and returns a new VirtualBench I2C session on the I2C engine
            for the device. The session is used in all subsequent VirtualBench
            I2C method calls. This method should be called once per session.

            You can use VirtualBench to master an I2C (Inter-Integrated Circuit)
            bus. When you configure an I2C bus, a set of lines are reserved for
            the bus and each line's direction is automatically configured. By
            default, all the GPIO lines have a 10 kΩ pull-down resistor
            connected. When used in I2C mode, they can be configured to have a
            pull-up instead. On the VB-8012, this pull-up has a value of 10 kΩ.
            On the VB-8034/8054, it is a value of 1.5 kΩ.

            i2c/0 bus
            dig/6: SCL (Serial Clock) output
            dig/7: SDA (Serial Data) input/output
        '''
        return self.InterIntegratedCircuit(self, bus, reset)

    class InterIntegratedCircuit(object):
        def __init__(self, outer, bus, reset):
            self.bus = bus
            self.nilcicapi =  outer.nilcicapi
            self.library_handle = outer.library_handle
            self.instrument_handle = c_sysint(0)
            status = self.nilcicapi.niVB_I2C_InitializeW(self.library_handle, c_wchar_p(self.bus), c_bool(reset), byref(self.instrument_handle))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def release(self):
            ''' Closes the session specified in Instrument Handle In.
            '''
            status = self.nilcicapi.niVB_I2C_Close(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            self.instrument_handle = c_sysint(0)

        def configure_bus(self, i2c_clock_rate, address, ic2_address_size, enable_pullups):
            ''' Configures the basic parameters of the I2C engine.
            '''
            status = self.nilcicapi.niVB_I2C_ConfigureBus(self.instrument_handle, c_int32(i2c_clock_rate), c_uint16(address), c_int32(ic2_address_size), c_bool(enable_pullups))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def query_bus_configuration(self):
            ''' Indicates the current basic configuration of the I2C engine.
            '''
            clock_rate = c_int32(0) # I2cClockRate
            address = c_uint16(0)
            address_size = c_int32(0) # I2cAddressSize
            pullups_enabled = c_bool(0)
            status = self.nilcicapi.niVB_I2C_QueryBusConfiguration(self.instrument_handle, byref(clock_rate), byref(address), byref(address_size), byref(pullups_enabled))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return I2cClockRate(clock_rate.value), address.value, I2cAddressSize(address_size.value), pullups_enabled.value

        def read(self, timeout_in_secs, read_data_size):
            ''' Completes a read transaction on the bus.
            '''
            read_data_out = []
            read_data = (c_uint8 * read_data_size)()
            status = self.nilcicapi.niVB_I2C_Read(self.instrument_handle, c_double(timeout_in_secs), byref(read_data), c_size_t(read_data_size))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            for i in range(read_data_size): read_data_out.append(read_data[i])
            return read_data_out

        def write(self, write_data, timeout_in_secs):
            ''' Completes a write transaction on the bus.
            '''
            number_of_bytes_written = c_int32(0) # Why does nivirtualbench.h (the file installed by National Instruments) not use size_t here?
            write_data_len = c_size_t(len(write_data))
            local_write_data = (c_uint8 * write_data_len.value)(*write_data)

            status = self.nilcicapi.niVB_I2C_Write(self.instrument_handle, byref(local_write_data), write_data_len, c_double(timeout_in_secs), byref(number_of_bytes_written))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            return number_of_bytes_written.value

        def write_read(self, write_data, timeout_in_secs, read_data_size):
            ''' Performs a write followed by read (combined format) on an I2C
                slave device.
            '''
            read_data_out = []
            number_of_bytes_written = c_int32(0)
            read_data = (c_uint8 * read_data_size)()
            write_data_len = c_size_t(len(write_data))
            local_write_data = (c_uint8 * write_data_len.value)(*write_data)

            status = self.nilcicapi.niVB_I2C_WriteRead(self.instrument_handle, byref(local_write_data), write_data_len, c_double(timeout_in_secs), byref(number_of_bytes_written), byref(read_data), c_size_t(read_data_size))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
            for i in range(read_data_size): read_data_out.append(read_data[i])
            return read_data_out, number_of_bytes_written.value

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
                the device and driver software to a known state.
            '''
            status = self.nilcicapi.niVB_I2C_ResetInstrument(self.instrument_handle)
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def export_configuration(self, configuration_filename):
            ''' Exports the current configuration of the instrument to a file.
            '''
            status = self.nilcicapi.niVB_I2C_ExportConfigurationW(self.instrument_handle, c_wchar_p(configuration_filename))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)

        def import_configuration(self, configuration_filename):
            ''' Imports a configuration file for use with the I2C engine. You
                can import PNG files exported from the VirtualBench Application
                or files created from I2C Export Configuration.
            '''
            status = self.nilcicapi.niVB_I2C_ImportConfigurationW(self.instrument_handle, c_wchar_p(configuration_filename))
            if (status != Status.SUCCESS):
                raise PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
