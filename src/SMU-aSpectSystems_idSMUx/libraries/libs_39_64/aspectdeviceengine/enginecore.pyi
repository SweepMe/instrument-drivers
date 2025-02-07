from __future__ import annotations
import numpy
import typing
__all__ = ['AD5522ChannelModel', 'AD5560ChannelModel', 'AnalogChannelModel', 'At', 'ChannelResult', 'CommandReply', 'CommandReplyFuture', 'CommandReplyList', 'CurrentRange', 'Device', 'DeviceList', 'DeviceModel', 'DeviceResult', 'DoubleList', 'DpsCurrentRange', 'FirmwareVersion', 'FunctionGeneratorResult', 'FunctionGeneratorType', 'IdSmu1DeviceModel', 'IdSmu2DeviceModel', 'IdSmuBoardModel', 'IdSmuDeviceModel', 'IdSmuService', 'IdSmuServiceRunner', 'IdSmuSettingsService', 'IdqTable', 'IdqTableCell', 'IdqTableGroup', 'IdqTableRow', 'IdqTableRows', 'Iloc', 'ListSweep', 'ListSweepChannelConfiguration', 'LogLevel', 'LogService', 'MapOfStringVectors', 'MeasurementMode', 'ParamterChangedObserverProxy', 'ReadAdcCommandIdSmuResult', 'ReadWriteFpgaIdSmuResult', 'Result', 'RowFilter', 'SequencingCommandResult', 'SmuCurrentRange', 'StringList', 'StringTable', 'check_future_is_ready', 'generate_function_generator_data', 'get_build_number', 'get_git_version']
class AD5522ChannelModel(AnalogChannelModel):
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def measure_current(self) -> float:
        """
                 Property that returns the measured current at the channel output (sample count is 16)
        
                 Returns
                 -------
                 float
                      The measured current in the unit of ampere [A]
        """
    def measure_currents(self, repetitions: int) -> numpy.ndarray[numpy.float64]:
        """
                 Measures the currents at the channel output (sample count is 16)
        
                 Parameters
                 ----------
                 repetitions : int
                      The number of repetitions of the measurement
        
                 Returns
                 -------
                 ndarray
                      The measured currents in the unit of ampere [A]
        """
    def measure_voltage(self) -> float:
        """
                 Measures the voltage at the channel output (sample count is 16)
        
                 Returns
                 -------
                 float
                      The measured voltage in the unit of volt [V]
        """
    def measure_voltages(self, arg0: int) -> list[float]:
        """
                 Measures the voltages at the channel output (sample count is 16)
        
                 Parameters
                 ----------
                 repetitions : int
                      The number of repetitions of the measurement
        
                 Returns
                 -------
                 List[float]
                      The measured currents in the unit of volt [V]
        """
    def set_clamp_high_value(self, clamp_high_value: float) -> int:
        """
                 Sets the channel clamp high value
        
                 Parameters
                 ----------
                 clamp_high_value : float
                      The clamp value in the unit depending on the output force mode ampere [A] if voltage is forced, else volt [V]
        """
    def set_clamp_low_value(self, clamp_low_value: float) -> int:
        """
                 Sets the channel clamp low value
        
                 Parameters
                 ----------
                 clamp_low_value : float
                      The clamp value in the unit depending on the output force mode ampere [A] if voltage is forced, else volt [V]
        """
    def set_current(self, voltage: float) -> None:
        """
                 Sets the channel output current
        
                 Parameters
                 ----------
                 current : float
                      The current in the the unit of ampere  [A]
        """
    def set_name(self, name: str) -> None:
        """
                 Sets the channel name
        
                 Parameters
                 ----------
                 name : str
                      The name of the channel
        """
    def set_voltage(self, voltage: float) -> None:
        """
                 Sets the channel output voltage
        
                 Parameters
                 ----------
                 voltage : float
                      The voltage in the unit of volt [V]
        """
    @property
    def autorange(self) -> bool:
        """
                 Property that gets/sets the state of the channels automatic current range functionality
        
                 Parameters
                 ----------
                 enable : bool
                      If set to true, the autoranging is enabled
        
                 Returns
                 -------
                 bool
                      The state of the auto range enabled state
        """
    @autorange.setter
    def autorange(self, arg1: bool) -> None:
        ...
    @property
    def autorange_measurement_count(self) -> int:
        """
                 Property that gets/sets the effective number of measurements for autoranging, default is 100
        
                 Parameters
                 ----------
                 autorange_measurement_count : int
                      Number of measurements
        
                 Returns
                 -------
                 int
                      The number of measurements
        """
    @autorange_measurement_count.setter
    def autorange_measurement_count(self, arg1: int) -> None:
        ...
    @property
    def autorange_post_switch_delay(self) -> int:
        """
                  Property that gets/sets the delay after switching the range in autorange mode, default is 0ms
        
                 Parameters
                 ----------
                 autorange_post_switch_delay : int
                      Delay in ms
        
                 Returns
                 -------
                 int
                      The delay in ms
        """
    @autorange_post_switch_delay.setter
    def autorange_post_switch_delay(self, arg1: int) -> None:
        ...
    @property
    def clamp_enabled(self) -> bool:
        """
                 Property that gets/sets the channel clamp enable state
        
                 Parameters
                 ----------
                 clamp_enabled : bool
        
                 Returns
                 -------
                 bool
                      The clamp enable state
        """
    @clamp_enabled.setter
    def clamp_enabled(self, arg1: bool) -> None:
        ...
    @property
    def clamp_high_value(self) -> float:
        """
                 Property that gets/sets the channel clamp high value
        
                 Parameters
                 ----------
                 clamp_high_value : float
                      The clamp value in the unit depending on the output force mode ampere [A] if voltage is forced, else volt [V]
        
                 Returns
                 -------
                 float
                      The clamp value in the unit depending on the output force mode ampere [A] if voltage is forced, else volt [V]
        """
    @clamp_high_value.setter
    def clamp_high_value(self, arg1: float) -> int:
        ...
    @property
    def clamp_low_value(self) -> float:
        """
                 Property that gets/sets the channel clamp low value
        
                 Parameters
                 ----------
                 clamp_low_value : float
                      The clamp value in the unit depending on the output force mode ampere [A] if voltage is forced, else volt [V]
        
                 Returns
                 -------
                 float
                      The clamp value in the unit depending on the output force mode ampere [A] if voltage is forced, else volt [V]
        """
    @clamp_low_value.setter
    def clamp_low_value(self, arg1: float) -> int:
        ...
    @property
    def current(self) -> float:
        """
                 Property that measures/sets the channel output current
        
                 Parameters
                 ----------
                 current : float
                      The current in the unit of ampere [A]
        
                 Returns
                 -------
                 float
                      The measured current in the unit of ampere [A]
        """
    @current.setter
    def current(self, arg1: float) -> None:
        ...
    @property
    def current_range(self) -> SmuCurrentRange:
        """
                 Property that gets/sets the channel current reange
        
                 Parameters
                 ----------
                 current_range : SmuCurrentRange
                      The current range
        
                 Returns
                 -------
                 SmuCurrentRange
                      The currently applied current range
        """
    @current_range.setter
    def current_range(self, arg1: SmuCurrentRange) -> None:
        ...
    @property
    def enabled(self) -> bool:
        """
                 Property that gets/sets the channel enabled state
        
                 Parameters
                 ----------
                 enabled : bool
                      True to enable the channel, false to disable the channel
        
                 Returns
                 -------
                 bool
                      The enabled state of the channel
        """
    @enabled.setter
    def enabled(self, arg1: bool) -> None:
        ...
    @property
    def hardware_id(self) -> str:
        """
                 Property that gets the channel id
        
                 Returns
                 -------
                 str
                      The id of the channel
        """
    @property
    def name(self) -> str:
        """
                 Property that gets/sets the channel name
        
                 Parameters
                 ----------
                 name : 
                      True to enable the channel, false to disable the channel
        
                 Returns
                 -------
                 str
                      The name of the channel
        """
    @name.setter
    def name(self, arg1: str) -> None:
        ...
    @property
    def output_ranges(self) -> list[float]:
        """
                 Property that gets the channel min/max output voltage and current
        
                 Returns
                 -------
                 List[float]
                      A list containing the values [Vmin, Vmax, Imin, Imax]
        """
    @property
    def sample_count(self) -> int:
        """
                 Property that gets/sets the number of samples per measurement
        
                 Parameters
                 ----------
                 sample_count : int
                      Number of samples per measurements
        
                 Returns
                 -------
                 int
                      The number of samples per measurement
        """
    @sample_count.setter
    def sample_count(self, arg1: int) -> None:
        ...
    @property
    def voltage(self) -> float:
        """
                 Property that measures/sets the channel output voltage
        
                 Parameters
                 ----------
                 voltage : float
                      The voltage in unit of volt [V]
        
                 Returns
                 -------
                 float
                      The measured voltage in the unit of volt [V]
        """
    @voltage.setter
    def voltage(self, arg1: float) -> None:
        ...
class AD5560ChannelModel(AnalogChannelModel):
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def measure_current(self) -> float:
        """
                 Measures the current at the channel output (sample count is 16)
        
                 Returns
                 -------
                 float
                      The measured current in the unit of ampere [A]
        """
    def measure_currents(self, arg0: int) -> list[float]:
        """
                 Measures the currents at the channel output (sample count is 16)
        
                 Parameters
                 ----------
                 repetitions : int
                      The number of repetitions of the measurement
        
                 Returns
                 -------
                 List[float]
                      The measured currents in the unit of ampere [A]
        """
    def measure_voltage(self) -> float:
        """
                 Measures the voltage at the channel output (sample count is 16)
        
                 Returns
                 -------
                 float
                      The measured voltage in the unit of volt [V]
        """
    def measure_voltages(self, arg0: int) -> list[float]:
        """
                 Measures the voltages at the channel output (sample count is 16)
        
                 Parameters
                 ----------
                 repetitions : int
                      The number of repetitions of the measurement
        
                 Returns
                 -------
                 List[float]
                      The measured currents in the unit of volt [V]
        """
    def set_clamp_high_value(self, clamp_high_value: float) -> int:
        """
                 Sets the channel clamp high value
        
                 Parameters
                 ----------
                 clamp_high_value : float
                      The clamp value in the unit of ampere [A]
        """
    def set_clamp_low_value(self, clamp_low_value: float) -> int:
        """
                 Sets the channel clamp low value
        
                 Parameters
                 ----------
                 clamp_low_value : float
                      The clamp value in the unit of ampere [A]
        """
    def set_name(self, name: str) -> None:
        """
                 Sets the channel name
        
                 Parameters
                 ----------
                 name : str
                      The name of the channel
        """
    def set_voltage(self, voltage: float) -> None:
        """
                 Sets the channel output voltage
        
                 Parameters
                 ----------
                 voltage : float
                      The voltage in the unit of volt [V]
        """
    @property
    def autorange(self) -> bool:
        """
                 Property that gets/sets the state of the channels automatic current range functionality
        
                 Parameters
                 ----------
                 enable : bool
                      If set to true, the autoranging is enabled
        
                 Returns
                 -------
                 bool
                      The state of the auto range enabled state
        """
    @autorange.setter
    def autorange(self, arg1: bool) -> None:
        ...
    @property
    def autorange_measurement_count(self) -> int:
        """
                 Property that gets/sets the effective number of measurements for autoranging, default is 100
        
                 Parameters
                 ----------
                 autorange_measurement_count : int
                      Number of measurements
        
                 Returns
                 -------
                 int
                      The number of measurements
        """
    @autorange_measurement_count.setter
    def autorange_measurement_count(self, arg1: int) -> None:
        ...
    @property
    def autorange_post_switch_delay(self) -> int:
        """
                  Property that gets/sets the delay after switching the range in autorange mode, default is 0ms
        
                 Parameters
                 ----------
                 autorange_post_switch_delay : int
                      Delay in ms
        
                 Returns
                 -------
                 int
                      The delay in ms
        """
    @autorange_post_switch_delay.setter
    def autorange_post_switch_delay(self, arg1: int) -> None:
        ...
    @property
    def clamp_enabled(self) -> bool:
        """
                 Property that gets/sets the channel clamp enable state
        
                 Parameters
                 ----------
                 clamp_enabled : bool
        
                 Returns
                 -------
                 bool
                      The clamp enable state
        """
    @clamp_enabled.setter
    def clamp_enabled(self, arg1: bool) -> None:
        ...
    @property
    def clamp_low_value(self) -> float:
        """
                 Property that gets/sets the channel clamp low value
        
                 Parameters
                 ----------
                 clamp_low_value : float
                      The clamp value in the unit of ampere [A]
        
                 Returns
                 -------
                 float
                      The clamp value in the unit of ampere [A]
        """
    @clamp_low_value.setter
    def clamp_low_value(self, arg1: float) -> int:
        ...
    @property
    def current(self) -> float:
        """
                 Property that returns the measured current at the channel output (sample count is 16)
        
                 Returns
                 -------
                 float
                      The measured current in the unit of ampere [A]
        """
    @property
    def current_range(self) -> DpsCurrentRange:
        """
                 Property that gets/sets the channel current reange
        
                 Parameters
                 ----------
                 current_range : DpsCurrentRange
                      The current range
        
                 Returns
                 -------
                 DpsCurrentRange
                      The currently applied current range
        """
    @current_range.setter
    def current_range(self, arg1: DpsCurrentRange) -> None:
        ...
    @property
    def enabled(self) -> bool:
        """
                 Property that gets/sets the channel enabled state
        
                 Parameters
                 ----------
                 enabled : bool
                      True to enable the channel, false to disable the channel
        
                 Returns
                 -------
                 bool
                      The enabled state of the channel
        """
    @enabled.setter
    def enabled(self, arg1: bool) -> None:
        ...
    @property
    def hardware_id(self) -> str:
        """
                 Property that gets the channel id
        
                 Returns
                 -------
                 str
                      The id of the channel
        """
    @property
    def name(self) -> str:
        """
                 Property that gets/sets the channel name
        
                 Parameters
                 ----------
                 name : 
                      The name of the channel
        
                 Returns
                 -------
                 str
                      The name of the channel
        """
    @name.setter
    def name(self, arg1: str) -> None:
        ...
    @property
    def output_ranges(self) -> list[float]:
        """
                 Property that gets the channel min/max output voltage and current
        
                 Returns
                 -------
                 List[float]
                      A list containing the values [Vmin, Vmax, Imin, Imax]
        """
    @property
    def sample_count(self) -> int:
        """
                 Property that gets/sets the number of samples per measurement
        
                 Parameters
                 ----------
                 sample_count : int
                      Number of samples per measurements
        
                 Returns
                 -------
                 int
                      The number of samples per measurement
        """
    @sample_count.setter
    def sample_count(self, arg1: int) -> None:
        ...
    @property
    def voltage(self) -> float:
        """
                 Property that measures/sets the channel output voltage
        
                 Parameters
                 ----------
                 voltage : float
                      The voltage in unit of volt [V]
        
                 Returns
                 -------
                 float
                      The measured voltage in the unit of volt [V]
        """
    @voltage.setter
    def voltage(self, arg1: float) -> None:
        ...
class AnalogChannelModel:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class At:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __getitem__(self, arg0: tuple[int, str]) -> str | None:
        ...
    def __setitem__(self, arg0: tuple[int, str], arg1: str) -> None:
        ...
class ChannelResult:
    """
    
             The result of a ReadAdcCommandIdSmu
        
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def get_values(self) -> list[float]:
        """
                 Returns the measurement values for a channel
        
                 Returns
                 -------
                 DoubleList
                      A DoubleList object
        """
    @property
    def values(self) -> numpy.ndarray[numpy.float64]:
        """
                 Returns the measurement values for a channel
        
                 Returns
                 -------
                 ndarray
        """
class CommandReply:
    """
    
             The aspect device engine is a command driven framework. 
             This is the base class of all command replies (and results).
             The reply can be an error or a result.
        
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def is_error(self) -> bool:
        """
                 Indicates whether the response is a command error
        
                 Returns
                 -------
                 bool
        """
    def is_result(self) -> bool:
        """
                 Indicates whether the response is an command result
        
                 Returns
                 -------
                 bool
        """
    def to_json(self) -> str:
        """
                 Returns the reply as a JSON string
        
                 Returns
                 -------
                 str
        """
class CommandReplyFuture:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def get(self) -> CommandReply:
        ...
class CommandReplyList:
    """
    List of command replies.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self: list[CommandReply]) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self: list[CommandReply], x: CommandReply) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self: list[CommandReply], arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self: list[CommandReply], arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self: list[CommandReply], arg0: list[CommandReply]) -> bool:
        ...
    @typing.overload
    def __getitem__(self: list[CommandReply], s: slice) -> list[CommandReply]:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self: list[CommandReply], arg0: int) -> CommandReply:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: list[CommandReply]) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self: list[CommandReply]) -> typing.Iterator[CommandReply]:
        ...
    def __len__(self: list[CommandReply]) -> int:
        ...
    def __ne__(self: list[CommandReply], arg0: list[CommandReply]) -> bool:
        ...
    def __repr__(self: list[CommandReply]) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self: list[CommandReply], arg0: int, arg1: CommandReply) -> None:
        ...
    @typing.overload
    def __setitem__(self: list[CommandReply], arg0: slice, arg1: list[CommandReply]) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self: list[CommandReply], x: CommandReply) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self: list[CommandReply]) -> None:
        """
        Clear the contents
        """
    def count(self: list[CommandReply], x: CommandReply) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self: list[CommandReply], L: list[CommandReply]) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self: list[CommandReply], L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self: list[CommandReply], i: int, x: CommandReply) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self: list[CommandReply]) -> CommandReply:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self: list[CommandReply], i: int) -> CommandReply:
        """
        Remove and return the item at index ``i``
        """
    def remove(self: list[CommandReply], x: CommandReply) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class CurrentRange:
    """
    Members:
    
      Range_5uA
    
      Range_20uA_SMU
    
      Range_200uA_SMU
    
      Range_2mA_SMU
    
      Range_70mA_SMU
    
      Range_25uA_DPS
    
      Range_250uA_DPS
    
      Range_2500uA_DPS
    
      Range_25mA_DPS
    
      Range_500mA_DPS
    
      Range_1200mA_DPS
    """
    Range_1200mA_DPS: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_1200mA_DPS: 150>
    Range_200uA_SMU: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_200uA_SMU: 30>
    Range_20uA_SMU: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_20uA_SMU: 20>
    Range_2500uA_DPS: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_2500uA_DPS: 120>
    Range_250uA_DPS: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_250uA_DPS: 110>
    Range_25mA_DPS: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_25mA_DPS: 130>
    Range_25uA_DPS: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_25uA_DPS: 100>
    Range_2mA_SMU: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_2mA_SMU: 40>
    Range_500mA_DPS: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_500mA_DPS: 140>
    Range_5uA: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_5uA: 10>
    Range_70mA_SMU: typing.ClassVar[CurrentRange]  # value = <CurrentRange.Range_70mA_SMU: 50>
    __members__: typing.ClassVar[dict[str, CurrentRange]]  # value = {'Range_5uA': <CurrentRange.Range_5uA: 10>, 'Range_20uA_SMU': <CurrentRange.Range_20uA_SMU: 20>, 'Range_200uA_SMU': <CurrentRange.Range_200uA_SMU: 30>, 'Range_2mA_SMU': <CurrentRange.Range_2mA_SMU: 40>, 'Range_70mA_SMU': <CurrentRange.Range_70mA_SMU: 50>, 'Range_25uA_DPS': <CurrentRange.Range_25uA_DPS: 100>, 'Range_250uA_DPS': <CurrentRange.Range_250uA_DPS: 110>, 'Range_2500uA_DPS': <CurrentRange.Range_2500uA_DPS: 120>, 'Range_25mA_DPS': <CurrentRange.Range_25mA_DPS: 130>, 'Range_500mA_DPS': <CurrentRange.Range_500mA_DPS: 140>, 'Range_1200mA_DPS': <CurrentRange.Range_1200mA_DPS: 150>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Device:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def get_firmware_version(self) -> FirmwareVersion:
        ...
    def get_id(self) -> str:
        ...
class DeviceList:
    """
    List of devices.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self: list[Device]) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self: list[Device], x: Device) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self: list[Device], arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self: list[Device], arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self: list[Device], arg0: list[Device]) -> bool:
        ...
    @typing.overload
    def __getitem__(self: list[Device], s: slice) -> list[Device]:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self: list[Device], arg0: int) -> Device:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: list[Device]) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self: list[Device]) -> typing.Iterator[Device]:
        ...
    def __len__(self: list[Device]) -> int:
        ...
    def __ne__(self: list[Device], arg0: list[Device]) -> bool:
        ...
    def __repr__(self: list[Device]) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self: list[Device], arg0: int, arg1: Device) -> None:
        ...
    @typing.overload
    def __setitem__(self: list[Device], arg0: slice, arg1: list[Device]) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self: list[Device], x: Device) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self: list[Device]) -> None:
        """
        Clear the contents
        """
    def count(self: list[Device], x: Device) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self: list[Device], L: list[Device]) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self: list[Device], L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self: list[Device], i: int, x: Device) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self: list[Device]) -> Device:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self: list[Device], i: int) -> Device:
        """
        Remove and return the item at index ``i``
        """
    def remove(self: list[Device], x: Device) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class DeviceModel:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class DeviceResult(CommandReply):
    """
    
             The result of a device detection command.
        
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def get_devices(self) -> list[Device]:
        ...
class DoubleList:
    """
    List of doubles.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: float) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: DoubleList) -> bool:
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> DoubleList:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> float:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: DoubleList) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[float]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: DoubleList) -> bool:
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: float) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: DoubleList) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: float) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: float) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: DoubleList) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: float) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> float:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> float:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: float) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class DpsCurrentRange:
    """
    Members:
    
      Range_25uA
    
      Range_250uA
    
      Range_2500uA
    
      Range_25mA
    
      Range_500mA
    
      Range_1200mA
    """
    Range_1200mA: typing.ClassVar[DpsCurrentRange]  # value = <DpsCurrentRange.Range_1200mA: 6>
    Range_2500uA: typing.ClassVar[DpsCurrentRange]  # value = <DpsCurrentRange.Range_2500uA: 3>
    Range_250uA: typing.ClassVar[DpsCurrentRange]  # value = <DpsCurrentRange.Range_250uA: 2>
    Range_25mA: typing.ClassVar[DpsCurrentRange]  # value = <DpsCurrentRange.Range_25mA: 4>
    Range_25uA: typing.ClassVar[DpsCurrentRange]  # value = <DpsCurrentRange.Range_25uA: 1>
    Range_500mA: typing.ClassVar[DpsCurrentRange]  # value = <DpsCurrentRange.Range_500mA: 5>
    __members__: typing.ClassVar[dict[str, DpsCurrentRange]]  # value = {'Range_25uA': <DpsCurrentRange.Range_25uA: 1>, 'Range_250uA': <DpsCurrentRange.Range_250uA: 2>, 'Range_2500uA': <DpsCurrentRange.Range_2500uA: 3>, 'Range_25mA': <DpsCurrentRange.Range_25mA: 4>, 'Range_500mA': <DpsCurrentRange.Range_500mA: 5>, 'Range_1200mA': <DpsCurrentRange.Range_1200mA: 6>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class FirmwareVersion:
    """
    
             Firmware version of a device detected by the engine.
        
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def to_hex_string(self) -> str:
        ...
class FunctionGeneratorResult:
    measurement_values: list[float]
    time_codes: list[float]
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class FunctionGeneratorType:
    """
    Members:
    
      sawtooth
    
      sinus
    
      square
    
      triangle
    
      ramp
    """
    __members__: typing.ClassVar[dict[str, FunctionGeneratorType]]  # value = {'sawtooth': <FunctionGeneratorType.sawtooth: 1>, 'sinus': <FunctionGeneratorType.sinus: 2>, 'square': <FunctionGeneratorType.square: 3>, 'triangle': <FunctionGeneratorType.triangle: 0>, 'ramp': <FunctionGeneratorType.ramp: 4>}
    ramp: typing.ClassVar[FunctionGeneratorType]  # value = <FunctionGeneratorType.ramp: 4>
    sawtooth: typing.ClassVar[FunctionGeneratorType]  # value = <FunctionGeneratorType.sawtooth: 1>
    sinus: typing.ClassVar[FunctionGeneratorType]  # value = <FunctionGeneratorType.sinus: 2>
    square: typing.ClassVar[FunctionGeneratorType]  # value = <FunctionGeneratorType.square: 3>
    triangle: typing.ClassVar[FunctionGeneratorType]  # value = <FunctionGeneratorType.triangle: 0>
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class IdSmu1DeviceModel(IdSmuDeviceModel):
    """
    
             IdSmuDeviceModel class that contains idSmu1 specific methods and properties.
    
        
    """
    class Dps:
        """
        
                 DPS object for quick access to the dps
        
            
        """
        class Channels:
            """
            
                     DPS channels object for quick access to the dps channels with the bracket operator []
            
                
            """
            @staticmethod
            def _pybind11_conduit_v1_(*args, **kwargs):
                ...
            @typing.overload
            def __getitem__(self, arg0: str) -> AD5560ChannelModel:
                ...
            @typing.overload
            def __getitem__(self, arg0: int) -> AD5560ChannelModel:
                ...
            def as_list(self) -> list[AD5560ChannelModel]:
                ...
        @staticmethod
        def _pybind11_conduit_v1_(*args, **kwargs):
            ...
        @property
        def channels(self) -> IdSmu1DeviceModel.Dps.Channels:
            """
                     Returns an object for quick access to the dps channels with the bracket operator []
            
                     Returns
                     -------
                     object
                          The channels object
            """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @property
    def dps(self) -> IdSmu1DeviceModel.Dps:
        """
                 Returns an object for quick access to the dps (analog device model of dps based idSmu)
        
                 Returns
                 -------
                 object
                      dps object
        """
class IdSmu2DeviceModel(IdSmuDeviceModel):
    """
    
             IdSmuDeviceModel class that contains idSmu2 specific methods and properties.
        
    """
    class Smu:
        """
        
                 SMU object for quick access to the smu
        
            
        """
        class Channels:
            @staticmethod
            def _pybind11_conduit_v1_(*args, **kwargs):
                ...
            @typing.overload
            def __getitem__(self, arg0: str) -> AD5522ChannelModel:
                ...
            @typing.overload
            def __getitem__(self, arg0: int) -> AD5522ChannelModel:
                ...
            def as_list(self) -> list[AD5522ChannelModel]:
                ...
        @staticmethod
        def _pybind11_conduit_v1_(*args, **kwargs):
            ...
        @property
        def channels(self) -> IdSmu2DeviceModel.Smu.Channels:
            """
                     Returns an object for quick access to the smu channels with the bracket operator []
            
                     Returns
                     -------
                     object
                          The channels object
            """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @property
    def smu(self) -> IdSmu2DeviceModel.Smu:
        """
                 Returns an object for quick access to the smu (analog device model of smu based idSmu)
        
                 Returns
                 -------
                 object
                      smu object
        """
class IdSmuBoardModel:
    """
    
             Container and controller vor idSmu modules and channels
        
    """
    class IdSmu1Modules:
        """
        
                 This class represents all idSmu1 (DPS) modules on the board
            
        """
        @staticmethod
        def _pybind11_conduit_v1_(*args, **kwargs):
            ...
        def __getitem__(self, arg0: str) -> IdSmu1DeviceModel:
            ...
        def as_list(self) -> list[IdSmu1DeviceModel]:
            ...
    class IdSmu2Modules:
        """
        
                 This class represents all idSmu2 (SMU) modules on the board
            
        """
        @staticmethod
        def _pybind11_conduit_v1_(*args, **kwargs):
            ...
        def __getitem__(self, arg0: str) -> IdSmu2DeviceModel:
            ...
        def as_list(self) -> list[IdSmu2DeviceModel]:
            """
                     Returns the force values that are used by the function_generator method
            
                     Returns
                     -------
                     List[IdSmu2DeviceModel]
                          A list of IdSmu2DeviceModel objects
            """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def contains_device(self, device_id: str) -> bool:
        """
                 Returns true if the device with the given hardware-id is located on the board
        
                 Parameters
                 ----------
                 device_id : str
                      The hardware-id of the device
            
                 Returns
                 -------
                 bool
                      The board address
        """
    def enable_autorange(self, enable: bool, channel_names: list[str]) -> None:
        """
                 Enables or disables the autoranging for channel(s)
        
                 Parameters
                 ----------
                 enable : bool
                      Enables or disables the autoranging for the channel(s)
                 channel_names : list
                      Name of the channels for which the value should be set
        """
    def enable_timecode(self, device_name: str) -> None:
        """
                 Enables the time code controller to genarte time stamps (for measurements)
        
                 Parameters
                 ----------
                 device_name : str
                      Name of or id of the device
        """
    def function_generator(self, device_id: str, channel_number: int, min_value: float, max_value: float, step_size: float, step_delay_in_microseconds: int, function_generator_type: FunctionGeneratorType) -> None:
        """
                 Initialize all installed idSMU devices on the board
        
                 Parameters
                 ----------
                 device_id : str
                      DeviceId
                 channel_number : int
                      Channel number
                 min_value : float
                      Minimum in generated function
                 max_value : float
                      Maximum in generated function
                 step_size : float
                      Voltage step
                 step_delay_in_microseconds : int
                      Delay between two steps
                 function_generator_type : FunctionGeneratorType
                      The type of the function generator
        """
    def get_address(self) -> str:
        """
                 Returns the board address
                 
                 Returns
                 -------
                 str
                      The board address
        """
    def get_all_device_hardware_ids(self) -> list[str]:
        """
                 Returns the device ids on the board
                 
                 Returns
                 -------
                 List[str]
                      The list of device-ids
        """
    def get_all_hardware_ids(self) -> list[str]:
        """
                 Returns the device ids on the board
                 
                 Returns
                 -------
                 List[str]
                      The list of device-ids
        """
    def get_channel_name(self, channel_id: str) -> str:
        """
                 Returns the name of the channel with the given channel id
        
                 Parameters
                 ----------
                 channel_id : str
                      Id or name of the channel
        
                 Returns
                 -------
                 str
                      The channel name
        """
    def get_clamp_high_value(self, channel_name: str) -> float:
        """
                Returns the analog clamp high value of the channel with the given id 
        
                Parameters
                ----------
                channel_name : str
                    Id or name of the channel
        
                 Returns
                 -------
                 float
                      The analog clamp high value
        """
    def get_clamp_low_value(self, channel_name: str) -> float:
        """
                Returns the analog clamp low value of the channel with the given id 
        
                Parameters
                ----------
                channel_name : str
                    Id or name of the channel
        
                 Returns
                 -------
                 float
                      The analog clamp low value
        """
    def get_current_range(self, channel_name: str) -> CurrentRange:
        """
                 Returns the current range of a channel
        
                 Parameters
                 ----------
                 channel_name : str
                      Names or Id or name of the channel for which the current range should be returned
        
                 Returns
                 -------
                 CurrentRange
        """
    def get_device_model(self, device_id: str) -> IdSmuDeviceModel:
        """
                 Returns the IdSmuDeviceModel the given id
        
                 Parameters
                 ----------
                 device_id : str
                      Id of the device
        
                 Returns
                 -------
                 IdSmuDeviceModel
                      The IdSmuDeviceModel
        """
    def get_device_power_options(self, device_id: str) -> list[bool]:
        """
                 Returns the state of the power options for the device with the given id
        
                 Parameters
                 ----------
                 device_id : str
                      The id of the device
        
                 Returns
                 -------
                 List[bool]
                      A list of boolean flags in the order ExternalPowerEnabled  (+ for DPS: HighCurrentEnabled)
        """
    def get_enable_INT10K(self, device_id: str) -> bool:
        """
                 Returns the enabled state of the internal 10K resistor
        
                 Parameters
                 ----------
                 device_id : str
                      The id of the device
        
                 Returns
                 -------
                 bool
                      Enabled state of the internal 10k resistor
        """
    def get_enable_channel(self, channel_name: str) -> bool:
        """
                Returns the enabled state of the channel with the given id
        
                Parameters
                ----------
                channel_name : str
                    Id or name of the channel
        
                 Returns
                 -------
                 bool
                      Returns true if the channel is enabled
        """
    def get_enable_clamps(self, channel_name: str) -> bool:
        """
                Returns the clamps enabled state of the channel with the given id
        
                Parameters
                ----------
                channel_name : str
                    Id or name of the channel
        
                 Returns
                 -------
                 bool
                      True if the channel clamps are enabled
        """
    def get_function_generator_results(self, device_id: str, channel_number: int) -> FunctionGeneratorResult:
        """
                 Initialize all installed idSMU devices on the board
        
                 Parameters
                 ----------
                 device_id : str
                      DeviceId
                 channel_number : int
                      Channel number
                 Returns
                 -------
                 FunctionGeneratorResult
                      FunctionGeneratorResult instance 
        """
    def get_immediate_mode(self) -> bool:
        """
                 Returns the state of the immediate mode.
        
                 Returns
                 -------
                 bool
        """
    def get_initialize_devices_results(self) -> list[CommandReply]:
        """
                 Prints information about the detected idSMU devices to the standard output (console)
        """
    def get_measure_channels_results(self) -> list[CommandReply]:
        """
                 Returns a list of results of measurements since tha last measure_channels command (or replies in case of an error)
                 This methods waits until all measurements have been completed, including any triggered measurements. 
                 Important note: If one of the measurements is waiting for a trigger, this method blocks until the triggered measurement is completed.
        
                 Returns
                 -------
                 List[CommandReply]
                      A list of CommandReply object
        """
    def get_measurement_channel_result(self, channel_name: str) -> ChannelResult:
        """
                 Gets the measured values for a channel. This is only valid if the result was stored for a previous async measurement command (not waited for the command result)
        
                 Parameters
                 ----------
                 channel_name : str
                      Name of the channel
        
                 Returns
                 -------
                 ChannelResult
                      A ChannelResult object.
        """
    def get_measurement_results_for_channel(self, channel_name: str) -> CommandReply:
        """
                 Gets the command result of all channel measurements of the device the given channel belongs to. 
                 This is only valid if the result was stored for a previous async measurement command (not waited for the command result)
        
                 Parameters
                 ----------
                 channel_name : str
                      Name of the channel
        
                 Returns
                 -------
                 CommandReply
                      A command reply which is of type ReadAdcCommandIdSmuResult in case of success.
        """
    def get_number_of_devices(self) -> int:
        """
                 Returns the number of detected idSMU devices
                 
                 Returns
                 -------
                 int
                      Number of detected idSMU devices
        """
    def get_output_force_ranges_for_channel(self, channel_name: str) -> list[float]:
        """
                 Returns the output force ranges for the channel with the given channel id
        
                 Parameters
                 ----------
                 channel_name : str
                      Id or name of the channel
        
                 Returns
                 -------
                 List[float]
                      The output force ranges in the order Vmin, Vman and (if force current mode is available) Imin,Imax
        """
    def get_output_force_value(self, channel_name: str) -> float:
        """
                 Returns the output force value for the channel with the given channel id
        
                 Parameters
                 ----------
                 channel_name : str
                      Id or name of the channel
        
                 Returns
                 -------
                 float
                      The output force value
        """
    def get_slots(self) -> list[IdSmuDeviceModel]:
        """
                 Returns a list of IdSmuDeviceModel in the order of the slots of the board
                 
                 Returns
                 -------
                 List[IdSmuDeviceModel]
                      The list of the IdSmuDeviceModel
        """
    def get_valid_range_for_channel_parameter(self, parameter_name: str, channel_Name: str) -> list[str]:
        """
                Returns the range of the given parameter as a list of strings
        
                Parameters
                ----------
                parameter_name : str
                    Name of the parameter
                channel_name : str
                    Id or name of the channel
        
                 Returns
                 -------
                 List[str]
                      The range as a list of strings
        """
    @typing.overload
    def initialize_devices(self, wait_for_result: bool, device_names: list[str] = []) -> list[CommandReply]:
        """
                 Initialize all installed idSMU devices on the board
        
                 Parameters
                 ----------
                 wait_for_result : bool
                      If set, the method waits until the all devices are initialized. If disabled, the method returns after the command was queued
        
                 device_names : List[str]
                      Optional list of ids of devices to initialize. If the list is left empty, all devices are initialized
        
                 Returns
                 -------
                 List[CommandReply]
                      A list of CommandReply objects  
        """
    @typing.overload
    def initialize_devices(self, wait_for_result: bool, parameter_setting: IdqTable, adapt_board_addresses: bool) -> list[CommandReply]:
        """
                 Initialize all installed idSMU devices on the board
        
                 Parameters
                 ----------
                 wait_for_result : bool
                      If set, the method waits until the all devices are initialized. If disabled, the method returns after the command was queued
                 parameter_setting : ParameterSetting
                      The settings used for the power options and naming of devices and channels.
                 adapt_board_addresses : bool
        
                 Returns
                 -------
                 List[CommandReply]
                      A list of CommandReply objects  
        """
    def is_autorange_enabled(self, channel_name: str) -> float:
        """
                 Returns true if the autorange for the addressed channel is enabled
        
                 Parameters
                 ----------
                 channel_name : str
                      Name of the channel for which the value should be retrieved
        
                 Returns
                 -------
                 bool
                      True if the autoranging is enabled
        """
    def is_board_initialized(self) -> bool:
        """
                 Returns true if all devices on the board are initialized
                 
                 Returns
                 -------
                 bool
        """
    def is_device_initialized(self, device_id: str) -> bool:
        """
                 Returns the initialized state of the device with the given id
        
                 Parameters
                 ----------
                 device_id : str
                      Id of the device
        
                 Returns
                 -------
                 bool
                      True if the device with the given id is initialized 
        """
    def measure_channels(self, wait_for_result: bool, sample_count: int, repetitions: int, channel_names: list[str], wait_for_trigger: bool = False) -> list[CommandReply]:
        """
                 Measures the voltage, current or temperature, depending on the adjusted MeasurementMode
        
                 Parameters
                 ----------
                 wait_for_result : bool
                      If set, the method waits until the result for all measurements are present. If disabled, the method returns after the command was queued
                 sample_count : int
                      Sample count per measurement. Valid values are 1,2,4,8 ... 2^31 (2 to the power of x)
                 repetitions : int
                      Number of measurements
                 channel_names : list
                      Names of the devices for which the internal 10K resistor should be enabled or disabled
                 wait_for_trigger : bool
                      If true, the measurement is executed with the next hardware trigger signal
        
                 Returns
                 -------
                 List[CommandReply]
                      A list of CommandReply object
        """
    def print_channel_registers(self, channel_name: str) -> None:
        """
                 Prints information about the channel register of the given channel
        
                 Parameters
                 ----------
                 channel_name : str
                      Name of the channel which the register state(s) should be printed
        """
    def print_device_information(self) -> str:
        """
                 Prints information about the detected idSMU devices to the standard output (console)
        """
    def print_uncommited_registers(self) -> None:
        """
                 Prints information about the registers that are set in the model but not committed to the hardware, yet.
        """
    def read_eeprom(self, eeprom_address: int, device_id: str) -> int:
        """
                 Reads from a EEPROM address
        
                 Parameters
                 ----------
                 eeprom_address : int
        
                 device_id : str
        
                 Returns
                 -------
                 int
                      The rgister value written, -1 if an error occured
        """
    def read_fpga(self, register_address: int, device_id: str) -> int:
        """
                 Writes to a FPGA register
        
                 Parameters
                 ----------
                 register_address : int
        
                 device_id : str
        
                 Returns
                 -------
                 int
                      The rgister value written, -1 if an error occured
        """
    def read_status(self, register_address: int, device_id: str) -> int:
        """
                 Reads a status register
        
                 Parameters
                 ----------
                 register_address : int
        
                 device_id : str
        
                 Returns
                 -------
                 int
                      The register value
        """
    def read_status_registers(self, register_addresses: list[int], device_id: str) -> list[int]:
        """
                 Reads status registers
        
                 Parameters
                 ----------
                 register_addresses : List[int]
        
                 device_id : str
        
                 Returns
                 -------
                 List[int]
                      The register values
        """
    def set_analog_device_parameters_from_strings(self, resource_id: str, parameter_names: list[str], parameter_values: list[str]) -> None:
        """
                Sets a parameter of a device or channel by a string value
        
                Parameters
                ----------
                resource_id : str
                    id of the device or channel
                parameter_names : list
                    Names of the parameters
                parameter_values : list
                    Values of the parameters as strings
        """
    def set_channel_name(self, channel_id: str, channel_name: str) -> None:
        """
                 Sets the name/alias for the channel with the given id
        
                 Parameters
                 ----------
                 device_id : str
                      Id of the device
                 channel_name : str
                      New name/alias of the channel
        """
    def set_clamps_low_and_high_values(self, clamp_low_value: float, clamp_high_value: float, channel_names: list[str]) -> None:
        """
                 Set the values of the channel(s) clamps
        
                 Parameters
                 ----------
                 clamp_low_value : clamp_low_value
                      Value for the lower clamp
                 clamp_high_value : clamp_high_value
                      Value for the higher clamp
                 channel_names : list
                      Names of the channels for which the clamp values should be set
        
                 Returns
                 -------
        """
    def set_current_ranges(self, current_range: CurrentRange, channel_names: list[str]) -> None:
        """
                 Sets the current range of a channel
        
                 Parameters
                 ----------
                 current_range : CurrentRange
                      The current range. There are different current ranges available depending on the device type (DPS and SMU)
                 channel_names : list
                      Names of the channels for which the value should be set
        
                 Returns
                 -------
        """
    def set_currents(self, current: float, channel_names: list[str]) -> None:
        """
                 Set the output current for channel(s)
        
                 Parameters
                 ----------
                 current : float
                      The current in the unit of ampere [A]
                 channel_names : list
                      Name of the channels for which the value should be set
        """
    def set_device_name(self, device_id: str, device_name: str) -> None:
        """
                 Sets the name/alias for the device with the given id
        
                 Parameters
                 ----------
                 device_id : str
                      Id of the device
                 device_name : str
                      New name/alias of the device
        """
    def set_device_power_options(self, enable_external_power: bool, enable_high_current: bool, device_id: str) -> None:
        """
                 Sets the state of the power options for the device with the given id
        
                 Parameters
                 ----------
                 enable_external_power : bool
                      enables external power
                 enable_high_current : bool
                      enables high current
                 device_id : str
                      The id of the device
                 Returns
                 -------
        """
    def set_enable_INT10K(self, enable_INT10k: bool, device_names: list[str]) -> None:
        """
                 Enables or disables the internal 10K resistor of the device(s)
        
                 Parameters
                 ----------
                 enable_INT10k : bool
                      Enables or disables the internal 10K resistor
                 device_names : list
                      Names of the devices for which the internal 10K resistor should be enabled or disabled
        
                 Returns
                 -------
        """
    def set_enable_channels(self, enable_channels: bool, channel_names: list[str]) -> None:
        """
                 Enables or disables channel(s)
        
                 Parameters
                 ----------
                 enable_channels : bool
                      Enables or disables the channel
                 channel_names : list
                      Name of the channels for which the value should be set
        """
    def set_enable_clamps(self, enable_clamps: bool, channel_names: list[str]) -> None:
        """
                 Enables or disables channel(s) clamp
        
                 Parameters
                 ----------
                 enable_clamps : bool
                      Enable or disables the channel clamp
                 channel_names : list
                      Names of the channels for which the value should be set
        
                 Returns
                 -------
        """
    def set_immediate_mode(self, enabled: bool) -> None:
        """
                 Enables or disables the immediate mode. If enabled, all methods that alter the device state are immediately written to the hardware
        
                 Parameters
                 ----------
                 enable : bool
                      If set, the immediate mode is enabled
        """
    def set_measurement_modes(self, measurement_mode: MeasurementMode, channel_names: list[str]) -> None:
        """
                 Sets the measurement mode of a channel
        
                 Parameters
                 ----------
                 measurement_mode : MeasurementMode
                      The measurement mode
                 channel_names : list
                      Names of the channels for which the value should be set
        
                 Returns
                 -------
        """
    def set_output_force_values(self, output_force_value: float, channel_names: list[str]) -> None:
        """
                 Sets the output force value for channels
        
                 Parameters
                 ----------
                 output_force_value : float
                      The value to force at the channel output(s)
                 channel_names : list
                      Names of the channels for which the value should be set
        
                 Returns
                 -------
        """
    def set_voltages(self, voltage: float, channel_names: list[str]) -> None:
        """
                 Set the output voltage for channel(s)
        
                 Parameters
                 ----------
                 voltage : float
                      The voltage in the unit of volt [V]
                 channel_names : list
                      Name of the channels for which the value should be set
        """
    def stringify_analog_channel_parameter(self, parameter_name: str, channel_name: str) -> str:
        """
                Returns the value of the given parameter as string
        
                Parameters
                ----------
                parameter_name : str
                    Name of the parameter
                channel_name : str
                    Id or name of the channel
         
                 Returns
                 -------
                 str
                      The parameter value as string
        """
    def write_eeprom(self, eeprom_address: int, eeprom_value: int, device_id: str) -> CommandReply:
        """
                 Writes to a EEPROM address
        
                 Parameters
                 ----------
                 eeprom_address : int
        
                 eeprom_value : int
        
                 device_id : str
        
                 Returns
                 -------
                 int
                      The rgister value written, -1 if an error occured
        """
    def write_fpga(self, register_address: int, register_value: int, device_id: str) -> int:
        """
                 Writes to a FPGA register
        
                 Parameters
                 ----------
                 register_address : int
        
                 register_value : int
        
                 device_id : str
        
                 Returns
                 -------
                 int
                      The rgister value written, -1 if an error occured
        """
    def write_fpga_with_mask(self, register_address: int, register_value: int, mask: int, device_id: str) -> int:
        """
                 Writes to a FPGA register
        
                 Parameters
                 ----------
                 register_address : int
        
                 register_value : int
        
                 mask : int
        
                 device_id : str
        
                 Returns
                 -------
                 int
                      The rgister value written, -1 if an error occured
        """
    def write_uncommited_settings(self, wait_for_result: bool) -> SequencingCommandResult:
        """
                 Writes all uncommited settings to the hardware
        
                 Parameters
                 ----------
                 wait_for_result : bool
                      If set, the method waits until the result for all measurements are present. If disabled, the method returns after the command was queued
        
                 Returns
                 -------
                 CommandReply
                      A CommandReply object
        """
    def write_uncommited_settings_for_device(self, wait_for_result: bool, device_id: str) -> CommandReply:
        """
                 Writes all uncommited settings for the device to the hardware
        
                 Parameters
                 ----------
                 wait_for_result : bool
                      If set, the method waits until the result for all measurements are present. If disabled, the method returns after the command was queued
                 device_id : str
                      The id of the device
        
                 Returns
                 -------
                 CommandReply
                      A CommandReply object
        """
    @property
    def channel_information(self) -> str:
        """
                 Prints information about the channels of the detected idSMU devices to the standard output (console)
        """
    @property
    def device_information(self) -> str:
        """
                 Prints information about the detected idSMU devices to the standard output (console)
        """
    @property
    def idSmu1Modules(self) -> IdSmuBoardModel.IdSmu1Modules:
        ...
    @property
    def idSmu2Modules(self) -> IdSmuBoardModel.IdSmu2Modules:
        ...
class IdSmuDeviceModel:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def get_firmware_version(self) -> str:
        """
                 Returns the firmware version of this device
                 
                 Returns
                 -------
                 str
                      The firmware version
        """
    def get_hardware_id(self) -> str:
        """
                 Returns the hardware id of this device in the format Mx.Sy (Motherboard.Slot - Format)
                 
                 Returns
                 -------
                 str
                      The hardware id
        """
    def measure_channels(self, sample_count: int, repetitions: int, channel_numbers: list[int], wait_for_trigger: bool = False) -> CommandReplyFuture:
        """
                 Performs a measurement command on the listed channels
        
                 Parameters
                 ----------
                 sample_count : int
                      The number of samples for the measurement
              
                 repetitions : int
                      The number repetitions of the measurement
        
                 channel_numbers : List[int]
                      The channel numbers of the channels to measure
        
                 wait_for_trigger : bool
                      If true, the measurement is executed with the next hardware trigger signal
        
                 Returns
                 -------
                 CommandReplyFuture
                      A CommandReplyFuture
        """
    @typing.overload
    def measure_channels_async(self, sample_count: int, repetitions: int, channel_numbers: list[int], wait_for_trigger: bool) -> CommandReplyFuture:
        """
                 Performs a measurement command on the listed channels. The method as "measure_channels", except the GIL scope is released in this version
        
                 Parameters
                 ----------
                 sample_count : int
                      The number of samples for the measurement
              
                 repetitions : int
                      The number repetitions of the measurement
        
                 channel_numbers : List[int]
                      The channel numbers of the channels to measure
        
                 wait_for_trigger : bool
                      If true, the measurement is executed with the next hardware trigger signal
        
                 Returns
                 -------
                 CommandReplyFuture
                      A CommandReplyFuture 
        """
    @typing.overload
    def measure_channels_async(self, sample_count: int, repetitions: int, channel_numbers: list[str], wait_for_trigger: bool) -> CommandReplyFuture:
        """
                 Performs a measurement command on the listed channels. The method as "measure_channels", except the GIL scope is released in this version
        
                 Parameters
                 ----------
                 sample_count : int
                      The number of samples for the measurement
              
                 repetitions : int
                      The number repetitions of the measurement
        
                 channel_numbers : List[int]
                      The channel numbers of the channels to measure
        
                 wait_for_trigger : bool
                      If true, the measurement is executed with the next hardware trigger signal
        
                 Returns
                 -------
                 CommandReplyFuture
                      A CommandReplyFuture 
        """
    @property
    def channel_ids(self) -> list[str]:
        """
                 Returns a list of all channel-ids (hardware-ids) in the format Mx.Sy.Cz (Motherboard.Slot.Channel - Format)
                 Returns
                 -------
                 List[str]
                      The list of the channel-ids
        """
    @property
    def hardware_id(self) -> str:
        """
                 Returns the hardware id of this device in the format Mx.Sy (Motherboard.Slot - Format)
                 
                 Returns
                 -------
                 str
                      The hardware id
        """
    @property
    def name(self) -> str:
        """
                 Property that gets/sets the device name
        
                 Parameters
                 ----------
                 name : 
                      The device name
        
                 Returns
                 -------
                 str
                      The name of the channel
        """
    @name.setter
    def name(self, arg1: str) -> None:
        ...
class IdSmuService:
    """
    
             Service class that detects and manages idSmu hardware.
    
        
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def detect_and_initialize_devices(self) -> list[CommandReply]:
        """
                 Tries to detect and initialize all installed idSMU devices. Default values for the power settings are taken.
                 If control over the power settings is required, the 2-step procedure of detecting and initializing a board must be executed manually
        
                 Returns
                 -------
                 List[CommandReply]
                      A list of CommandReply objects  
        """
    def detect_and_initialize_devices_with_setting(self, setting_name: str, adapt_board_addresses: bool) -> list[CommandReply]:
        """
                 Tries to detect and initialize all installed idSMU devices
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of the settings used for the power options and naming of devices and channels.
                 adapt_board_addresses : bool
        
                 Returns
                 -------
                 List[CommandReply]
                      A list of CommandReply objects  
        """
    def detect_devices(self) -> CommandReply:
        """
                 Tries to detect and initialize all installed idSMU devices
                 
                 Returns
                 -------
                 CommandReply
                      A CommandReply object
        """
    def devices_are_detected(self) -> bool:
        """
                 Flag that indicates that a device detection was successfull
                 
                 Returns
                 -------
                 bool
                      True if devices were detected
        """
    def get_board(self, board_address: str) -> IdSmuBoardModel:
        """
                 Returns the board model with the given address
        
                 Parameters
                 ----------
                 board_address : str
                      Address of the board
        
                 Returns
                 -------
                 IdsmuBoardModel
                      An IdsmuBoardModel object
        """
    def get_board_addresses(self) -> list[str]:
        """
                 Returns the addresses of all detected boards
                 
                 Returns
                 -------
                 List[str]
                      Addresses of all detected boards
        """
    def get_first_board(self) -> IdSmuBoardModel:
        """
                 Returns the first board of all detected idSMU boards
                 
                 Returns
                 -------
                 IdsmuBoardModel
                      An IdsmuBoardModel object
        """
    def get_number_of_boards(self) -> int:
        """
                 Returns the number of detected idSMU boards
                 
                 Returns
                 -------
                 int
                      Number of detected idSMU boards
        """
    def get_settings_service(self) -> IdSmuSettingsService:
        """
                 Returns an instance of IdSmuSettingsService object
                
                 Returns
                 -------
                 IdSmuSettingsService
                      An instance of IdSmuSettingsService object
        """
    @typing.overload
    def initialize_board(self, board_address: str, setting_name: str, adapt_board_addresses: bool) -> list[CommandReply]:
        """
                 Tries to initialize the board with the give address
        
                 Parameters
                 ----------
                 board_address : str
                      Enables the external power option.
                 setting_name : str
                      The name of the settings used for the power options and naming of devices and channels.
                 adapt_board_addresses : bool
        
                 Returns
                 -------
                 List[CommandReply]
                      A list of CommandReply objects  
        """
    @typing.overload
    def initialize_board(self, board_address: str) -> list[CommandReply]:
        """
                 Tries to initialize the board with the give address
        
                 Parameters
                 ----------
                 board_address : str
                      The board address in the format Mx, where x is an integer
        
                 Returns
                 -------
                 List[CommandReply]
                      A list of CommandReply objects  
        """
    def print_device_information(self) -> str:
        """
                 Returns information of detected devices as printable table
                 
                 Returns
                 -------
                 str
        """
    def print_fpga_register(self, register_address: int) -> str:
        """
                 Returns the fpga register values of all detected devices as printable table
        
                 Parameters
                 ----------
                 register_address : int
                      Address of the fpga register
        
        
                 Returns
                 -------
                 str
        """
    def print_status_register(self, register_address: int) -> str:
        """
                 Returns the status register values of all detected devices as printable table
        
                 Parameters
                 ----------
                 register_address : int
                      Address of the status register
        
        
                 Returns
                 -------
                 str
        """
    def shutdown_devices(self) -> list[CommandReply]:
        """
                 Tries to deinitialize all detected devices
        
                 Returns
                 -------
                 List[CommandReply]
                      A list of CommandReply objects  
        """
class IdSmuServiceRunner:
    """
    
             Simplifies the starting of idSmu services and controls their lifetime.
        
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, log_level: int = 0, worker_thread_count: int = 4) -> None:
        ...
    def get_idsmu_service(self) -> IdSmuService:
        ...
    def shutdown(self) -> None:
        ...
    @property
    def log_service(self) -> LogService:
        ...
class IdSmuSettingsService:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def apply_parameter_setting(self, parameter_setting: IdqTable, board_address: str, filtered: bool, table_group_name: str | None) -> int:
        """
                 Applies the given setting to the hardware models
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of a loaded setting (IdqTable)
        
                 board_address : str
                      The address of the board
        
                 filtered : bool
                      If this flag is set, the parameters are taken from the filtered version of the table
        
                 table_group_name : str
                      Optional table group name if only a group should be applied
        
                 Returns
                 -------
                 ParameterSetting
                      A parameter setting object with the given name
        """
    @typing.overload
    def apply_parameter_setting(self, setting_name: str, board_address: str, filtered: bool, table_group_name: str | None) -> int:
        """
                 Applies the parameters in a table to a idSMU board
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of a loaded setting (IdqTable)
        
                 board_address : str
                      The address of the board
        
                 filtered : bool
                      If this flag is set, the parameters are taken from the filtered version of the table
        
                 table_group_name : str
                      Optional table group name
        
                 Returns
                 -------
                 int
                      The number of resources the settings were applied to
        """
    def apply_parameter_settings_at_column_values(self, setting_name: str, board_address: str, column_name: str, column_values: list[str], filtered: bool, table_group_name: str | None) -> int:
        """
                 Applies the parameters in a table to a idSMU board
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of a loaded setting (IdqTable)
        
                 board_address : str
                      The address of the board
        
                 column_name : str
                      The name of the column to search for value(s)
        
                 column_values : List[str]
                      One or more values to search for in the selected column
        
                 filtered : bool
                      If this flag is set, the parameters are taken from the filtered version of the table
        
                 table_group_name : str
                      Optional table group name
        
                 Returns
                 -------
                 int
                      The number of resources the settings were applied to
        """
    def bake_filter_into_table(self, setting_name: str) -> None:
        """
                 Replaces the table/setting with its filtered version
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of the setting
        """
    def export_settings_to_csv(self, file_path: str, setting_names: list[str], append_to_file: bool) -> str | None:
        """
                 Exports setting(s) to csv
        
                 Parameters
                 ----------
                 file_path : str
                      Path to the csv file
        
                 setting_names : List[str]
                      List of names of the settings to export
        
                 append_to_file : bool
                      If true, appends the exported settings to the existing file
        
                 Returns
                 -------
                 str
                      Returns an error message if an error occured, else none
        """
    def export_settings_to_xlsx(self, file_path: str, setting_names: list[str]) -> str | None:
        """
                 Exports parameter setting table(s) to excel (xlsx format)
        
                 Parameters
                 ----------
                 file_path : str
                      Path to the xlsx file
        
                 setting_names : List[str]
                      List of names of the parameter table settings to export
        
                 Returns
                 -------
                 str
                      Returns an error message if an error occured, else none
        """
    def filter_columns(self, setting_name: str, column_names: list[str]) -> IdqTable:
        """
                 Filters columns and returns a new IdqTable object containing this columns only
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of the setting to apply the filter to
                 column_names : List[str]
                      The names of the columns to filter out
        
                 Returns
                 -------
                 IdqTable
                      Returns a new IdqTable object
        """
    def filter_rows(self, setting_name: str, column_name: str, filter_value: str, exact_match: bool) -> IdqTable:
        """
                 Filters rows by the given filter_values and returns a new IdqTable object containing this rows only
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of the setting to apply the filter to
                 column : str
                      The name of the column to apply the filter to
                 filter_value : str
                      Each row in the given column is checked against the filter_value and selected if the string in the filter_value is conatained in the cell
                 exact_match : bool
                      If enabled a whole word is searched
        
                 Returns
                 -------
                 IdqTable
                      Returns a new IdqTable object
        """
    def get_merged_column_names(self, setting_name: str) -> list[str]:
        """
                 Returns the unique headers of all groups as list of strings
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of the setting to apply the filter to
        
                 Returns
                 -------
                 List[str]
                      Returns the headers as  list of strings
        """
    def get_parameter_setting(self, setting_name: str) -> IdqTable:
        """
                 Returns a IdqTable object.
        
                 Parameters
                 ----------
                 setting_name : str
                      Name of the parameter setting
        
                 Returns
                 -------
                 IdqTable
                      A IdqTable object with the given name
        """
    def get_parameter_settings_for_board(self, board_address: str, group_by: str = 'Type') -> IdqTable:
        """
                 Returns the parameters settings for the give board address
        
                 Parameters
                 ----------
                 board_address : str
                      A board address in the format Mx, where x is a number between 1 and 32
                 group_by : bool
                      The column used to group the parameter tables
        
                 Returns
                 -------
                 IdqTable
                      A IdqTable object
        """
    def get_parameter_settings_names(self) -> list[str]:
        """
                 Returns a list containing the names of all loaded settings
        
                 Returns
                 -------
                 List[str]
                      A list containing the names of all loaded settings
        """
    def group_setting(self, setting_name: str, group_by: str) -> IdqTable:
        """
                 Groups the given setting in groups of the unique values of the given column
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of the setting to apply the filter to
                 group_by : List[str]
                      The name of the column to use for the grouping
        
                 Returns
                 -------
                 IdqTable
                      Returns a new IdqTable object
        """
    def import_settings_from_csv(self, file_path: str) -> str | None:
        """
                 Imports settings from CSV
        
                 Parameters
                 ----------
                 file_path : str
                      Path to the csv file
                 Returns
                 -------
                 str
                      Returns an error message if an error occured, else none
        """
    @typing.overload
    def import_settings_from_xlsx(self, file_path: str) -> str | None:
        """
                 Imports settings from exel (xlsx format)
        
                 Parameters
                 ----------
                 file_path : str
                      Path to the xlsx file
                 Returns
                 -------
                 str
                      Returns an error message if an error occured, else none
        """
    @typing.overload
    def import_settings_from_xlsx(self, file_path: str) -> str | None:
        """
                 Enables or disables channel(s)
        
                 Parameters
                 ----------
                 file_path : str
                      Path to the csv settings file
                 delimiter : str
                      Delimiter (only a single character is allowed)
        
                 Returns
                 -------
                 str
                      Returns an error message if an error occured, else none
        """
    def print_settings(self, setting_name: str, filtered: bool = False, column_information: bool = False, max_columns: int = -1) -> str:
        """
                 Prints the setting / board to the console
        
                 Parameters
                 ----------
                 setting_name : str
                      Name of the setting
                 filtered : bool
                      If true, prints the setting with applied filteres
                 column_information : bool
                      Printss additional column information
        """
    def refresh_table(self, table_name: str) -> bool:
        """
                 Refreshes a table. If the table represents a board state this table is updated.
        
                 Parameters
                 ----------
                 table_name : str
                      Name of the table
        
                 Returns
                 -------
                 bool
                      Returns false if the table does not exist, else true
        """
    def refresh_table_row(self, table_name: str, column_name: str, column_value: str) -> tuple[str, int]:
        """
                 Refreshes a table row. The row is found by a given value in a given column(name)
        
                 Parameters
                 ----------
                 table_name : str
                      Name of the table
                 column_name : str
                      Name of the column
                 column_value : str
                      Value in the column to search for
                 Returns
                 -------
                 Tuple
                      Returns tuple of the group name and the row within the grup where the setting was found
        """
    def remove_parameter_setting(self, setting_name: str) -> bool:
        """
                 Removes a setting from the service setting storage
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of the setting
        """
    def search_and_replace(self, setting_name: str, search_term: str, replace_term: str) -> IdqTable:
        """
                 Replaces all occurences of a string in the parameter setting table
        
                 Parameters
                 ----------
                 setting_name : str
                      The name of the paramter setting table
                 search_term : str
                      The search query value
                 replace_term : str
                      The value for the replacement
        
                 Returns
                 -------
                 IdqTable
                      Returns the same paramter setting table with the replacements 
        """
class IdqTable:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __getitem__(self, arg0: int) -> IdqTableGroup:
        ...
    def filter_columns(self, column_names: list[str]) -> IdqTable:
        """
                 Filters columns and returns a new IdqTable object containing this columns only
        
                 Parameters
                 ----------
                 column_names : List[str]
                      The names of the columns to filter out
        
                 Returns
                 -------
                 IdqTable
                      Returns a new IdqTable object
        """
    def filter_rows(self, column_name: str, filter_value: str, exact_match: bool) -> IdqTable:
        """
                 Filters rows by the given filter_values and returns a new IdqTable object containing this rows only
        
                 Parameters
                 ----------
                 column_name : str
                      The name of the column to apply the filter to
                 filter_value : str
                      Each row in the given column   is checked against the filter_value and selected if the string in the filter_value is conatained in the cell
                 exact_match : bool
                      If enabled a whole word is searched
                 Returns
                 -------
                 IdqTable
                      Returns a new IdqTable object
        """
    def get_column_filter(self) -> list[str]:
        """
                 Returns the list of column names that are applied as column filter
        
                 Returns
                 -------
                 List[str]
                      Returns a list of strings of column names
        """
    def get_file_path(self) -> str | None:
        """
                Returns the path of the file the table was imported from, if available
        
                Returns
                -------
                str
                    Returns a path or none
        """
    def get_filtered_table(self) -> IdqTable:
        """
                 Returns the filtered table
        
                 Returns
                 -------
                 IdqTable
        """
    def get_grouped_by(self) -> str:
        """
                 Returns the name of the column the table is grouped by
        
                 Returns
                 -------
                 str
                      Returns the name of the column the table is grouped by
        """
    def get_merged_column_names(self) -> list[str]:
        """
                Returns the unique headers of all groups as list of strings
        
                Returns
                -------
                List[str]
                    Returns the headers as  list of strings
        """
    def get_name(self) -> str:
        """
                Returns the table name
        
                Returns
                -------
                str
                    Returns the table name
        """
    def get_row_filters(self) -> list[RowFilter]:
        """
                 Returns the list of row filters applied to that table
        
                 Returns
                 -------
                 List[RowFilter]
                      Returns a list of RowFilter objects
        """
    def get_table_group(self, group_name: str) -> IdqTableGroup:
        """
                 Return the table group with the given name
        
                 Parameters
                 ----------
                 group_name : str
                      The name of the table group
        
                 Returns
                 -------
                 IdqTable
                      Returns a the IdqTableGroup object
        """
    def get_table_group_names(self) -> list[str]:
        """
                 Returns a list of table group names
        
                 Returns
                 -------
                 List[str]
                      A list of table group names
        """
    def get_table_groups_as_list(self) -> list[IdqTableGroup]:
        """
                 Returns a list of table groups
        
                 Returns
                 -------
                 List[IdqTableGroup]
                      A list of table groups
        """
    def is_filter_active(self) -> bool:
        """
                 Returns true if a filter is applied to the table
        
                 Returns
                 -------
                 bool
        """
    def set_name(self, name: str) -> None:
        """
                 Sets the name of the table
        
                 Parameters
                 ----------
                 name : str
                      The new name of the table
        """
    @property
    def name(self) -> str:
        """
                Returns or sets the table name
        
                Returns
                -------
                str
                    Returns the table name
        """
    @name.setter
    def name(self, arg1: str) -> None:
        ...
    @property
    def table_groups(self) -> list[IdqTableGroup]:
        """
                 Returns a list of table groups
        
                 Returns
                 -------
                 List[IdqTableGroup]
                      A list of table groups
        """
class IdqTableCell:
    cell_value: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class IdqTableGroup:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    @typing.overload
    def get_cell_value(self, row_index: int, column_index: int) -> str | None:
        """
                Gets a string parameter in the table group
        
                Parameters
                ----------
                row_index : int
                    Index of the row in the table
                column_index : int
                    Index of the column in the table
        
                Returns
                -------
                str
        """
    @typing.overload
    def get_cell_value(self, row_index: int, column_name: str) -> str | None:
        """
                Gets a string parameter in the table group
        
                Parameters
                ----------
                row_index : int
                    Index of the row in the table
                column_name : str
                    Name of the column in the table
        
                Returns
                -------
                str
        """
    def get_column_names(self) -> list[str]:
        """
                Returns the headers as list of strings
        
                Returns
                -------
                StringList
                    Returns the headers as  list of strings
        """
    def get_name(self) -> str:
        """
                Returns the group name
        
                Returns
                -------
                str
                    Returns the group name
        """
    def get_range_descriptors(self) -> dict[str, list[str]]:
        """
                Returns the the description of the allowed parameter ranges for this group, if available
        
                Returns
                -------
                MapOfStringVectors
                    The the description of the allowed parameter ranges
        """
    def get_row(self, row_index: int) -> list[IdqTableCell]:
        """
                Returns the row at the given index.
        
                Returns
                -------
                IdqTableRow
                    Returns the row at the given index.
        """
    def get_row_index(self, column_name: str, column_value: str) -> int:
        """
                Returns the row index of a the first value in the given column that matches the given value
        
                Parameters
                ----------
                column_name : str
                    The name of the column
                column_value : str
                    The value in the column to search for
        
                Returns
                -------
                int
        """
    def get_rows(self) -> list[list[IdqTableCell]]:
        """
                Returns the rows as a list of list of strings (StringTable)
        
                Returns
                -------
                IdqTableRows
                    Returns the rows as a list of list of IdqTableCell
        """
    @typing.overload
    def set_cell_value(self, row_index: int, column_name: str, cell_value: str | None) -> None:
        """
                Sets a string parameter in the table group
        
                Parameters
                ----------
                row_index : int
                    Index of the row in the table
                column_name : str
                    Name of the column in the table
                cell_value : str
                    The value to set
        """
    @typing.overload
    def set_cell_value(self, row_index: int, column_index: int, cell_value: str | None) -> None:
        """
                Sets a string parameter in the table group
        
                Parameters
                ----------
                row_index : int
                    Index of the row in the table
                column_index : str
                    Index of the column in the table
                cell_value : str
                    The value to set
        """
    def set_name(self, name: str) -> None:
        """
                 Sets the name of the table group
        
                 Parameters
                 ----------
                 name : str
                      The new name of the table group
        """
    def set_parameter_value(self, row_index: int, parameter_name: str, parameter_value: str) -> None:
        """
                Sets a string parameter in the table group
        
                Parameters
                ----------
                row_index : int
                    Index of the row in the settings
                parameter_name : str
                    Name of the parameter
                parameter_value : str
                    String value of the parameter
        """
    @property
    def at(self) -> At:
        ...
    @property
    def columns(self) -> list[str]:
        ...
    @property
    def iloc(self) -> Iloc:
        ...
    @property
    def name(self) -> str:
        """
                Returns or sets the group name
        
                Returns
                -------
                str
                    Returns the group name
        """
    @name.setter
    def name(self, arg1: str) -> None:
        ...
    @property
    def shape(self) -> list[int]:
        ...
class IdqTableRow:
    """
    Row of IdqTableCells.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self: list[IdqTableCell]) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self: list[IdqTableCell], x: IdqTableCell) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self: list[IdqTableCell], arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self: list[IdqTableCell], arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self: list[IdqTableCell], arg0: list[IdqTableCell]) -> bool:
        ...
    @typing.overload
    def __getitem__(self: list[IdqTableCell], s: slice) -> list[IdqTableCell]:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self: list[IdqTableCell], arg0: int) -> IdqTableCell:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: list[IdqTableCell]) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self: list[IdqTableCell]) -> typing.Iterator[IdqTableCell]:
        ...
    def __len__(self: list[IdqTableCell]) -> int:
        ...
    def __ne__(self: list[IdqTableCell], arg0: list[IdqTableCell]) -> bool:
        ...
    def __repr__(self: list[IdqTableCell]) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self: list[IdqTableCell], arg0: int, arg1: IdqTableCell) -> None:
        ...
    @typing.overload
    def __setitem__(self: list[IdqTableCell], arg0: slice, arg1: list[IdqTableCell]) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self: list[IdqTableCell], x: IdqTableCell) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self: list[IdqTableCell]) -> None:
        """
        Clear the contents
        """
    def count(self: list[IdqTableCell], x: IdqTableCell) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self: list[IdqTableCell], L: list[IdqTableCell]) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self: list[IdqTableCell], L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self: list[IdqTableCell], i: int, x: IdqTableCell) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self: list[IdqTableCell]) -> IdqTableCell:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self: list[IdqTableCell], i: int) -> IdqTableCell:
        """
        Remove and return the item at index ``i``
        """
    def remove(self: list[IdqTableCell], x: IdqTableCell) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class IdqTableRows:
    """
    Table of IdqTableCells.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self: list[list[IdqTableCell]]) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self: list[list[IdqTableCell]], x: list[IdqTableCell]) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self: list[list[IdqTableCell]], arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self: list[list[IdqTableCell]], arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self: list[list[IdqTableCell]], arg0: list[list[IdqTableCell]]) -> bool:
        ...
    @typing.overload
    def __getitem__(self: list[list[IdqTableCell]], s: slice) -> list[list[IdqTableCell]]:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self: list[list[IdqTableCell]], arg0: int) -> list[IdqTableCell]:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: list[list[IdqTableCell]]) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self: list[list[IdqTableCell]]) -> typing.Iterator[list[IdqTableCell]]:
        ...
    def __len__(self: list[list[IdqTableCell]]) -> int:
        ...
    def __ne__(self: list[list[IdqTableCell]], arg0: list[list[IdqTableCell]]) -> bool:
        ...
    @typing.overload
    def __setitem__(self: list[list[IdqTableCell]], arg0: int, arg1: list[IdqTableCell]) -> None:
        ...
    @typing.overload
    def __setitem__(self: list[list[IdqTableCell]], arg0: slice, arg1: list[list[IdqTableCell]]) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self: list[list[IdqTableCell]], x: list[IdqTableCell]) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self: list[list[IdqTableCell]]) -> None:
        """
        Clear the contents
        """
    def count(self: list[list[IdqTableCell]], x: list[IdqTableCell]) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self: list[list[IdqTableCell]], L: list[list[IdqTableCell]]) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self: list[list[IdqTableCell]], L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self: list[list[IdqTableCell]], i: int, x: list[IdqTableCell]) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self: list[list[IdqTableCell]]) -> list[IdqTableCell]:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self: list[list[IdqTableCell]], i: int) -> list[IdqTableCell]:
        """
        Remove and return the item at index ``i``
        """
    def remove(self: list[list[IdqTableCell]], x: list[IdqTableCell]) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class Iloc:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __getitem__(self, arg0: tuple[int, int]) -> str | None:
        ...
    def __setitem__(self, arg0: tuple[int, int], arg1: str) -> None:
        ...
class ListSweep:
    """
    
             Class to perform a List Sweep on a idSmu module
        
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self, arg0: str, arg1: IdSmuBoardModel) -> None:
        ...
    def add_channel_configuration(self, channel_name: str, list_sweep_channel_configuration: ListSweepChannelConfiguration) -> None:
        """
                 Adds a list sweep configuration for the given channel
        
                 Parameters
                 ----------
                 channel_name : str
                      Name or Id of the channel
                 list_sweep_channel_configuration : ListSweepChannelConfiguration
                      The channel configuration
        """
    def can_run(self) -> bool:
        """
                 Returns true if the sweep can be executed (the memory used by the sweep does not exceed the memory limit of 4k)
        
                 Returns
                 -------
                 bool
        """
    def get_measurement_result(self, channel_name: str) -> numpy.ndarray[numpy.float64]:
        """
                 Returns the measurement results of the sweep
        
                 Returns
                 -------
                 ndarray
                      An array of measurement values
        """
    def get_timecode(self) -> numpy.ndarray[numpy.float64]:
        """
                 Returns the timecode of the sweep in microseconds
        
                 Returns
                 -------
                 ndarray
                      An array of timestamps, one entry for each measurement
        """
    def run(self) -> str | None:
        """
                 Runs the sweep
        
                 Returns
                 -------
                 str or None
                      In case of an error, the error is reported as string
        """
    def set_measurement_delay(self, measurement_delay: int) -> None:
        """
                 Sets the set to measurement delay in microseconds
        
                 Parameters
                 ----------
                 measurement_delay : int
                      Time in microseconds
        """
    def set_sample_count(self, sample_count: int) -> None:
        """
                 Sets the sample count for each measurement. The sampled values are averaged. Default is 1.
        
                 Parameters
                 ----------
                 sample_count : int
                      Number of samples
        """
    @property
    def size(self) -> int:
        """
                 Returns the number of words stored in memory when the sweep is executed (the memory used by the sweep shout not exceed the memory limit of 1k words)
        
                 Returns
                 -------
                 bool
        """
    @property
    def timecode(self) -> numpy.ndarray[numpy.float64]:
        """
                 Returns the timecode of the sweep in microseconds
        
                 Returns
                 -------
                 ndarray
                      An array of timestamps, one entry for each measurement
        """
class ListSweepChannelConfiguration:
    """
    
             Instances of this class are needed to configure a List Sweep
        
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self) -> None:
        ...
    def change_current_range_at(self, step_index: int, current_range: CurrentRange) -> None:
        """
                 Changes the current range at the given index within the sweep
        
                 Parameters
                 ----------
                 step_index : int
                      The step index in the sweep at which the current range changes
                 current_range : CurrentRange
                      The new current range 
        """
    def clear_current_ranges(self) -> None:
        """
                 Removes all current range changes from the configuration
        """
    def get_force_values(self) -> numpy.ndarray[numpy.float64]:
        ...
    def set_constant_force_mode(self, number_of_steps: int) -> None:
        """
                 Sets the configuration to measurement only mode - no sweep is performerd
        
                 Parameters
                 ----------
                 number_of_steps : int
                      Number of  measurement steps 
        """
    def set_disable_measurement(self) -> None:
        """
                 Disables the measurement for this configuration
        """
    def set_force_values(self, force_values: numpy.ndarray) -> None:
        """
                 Sets the custom sweep force values
        
                 Parameters
                 ----------
                 force_values : ndarray
                      The force values
        """
    def set_linear_sweep(self, start: float, end: float, number_of_steps: int) -> None:
        """
                 Configures a linear sweep
        
                 Parameters
                 ----------
                 start : float
                      Start value
                 stop : float
                      Stop value
                 number_of_steps : int
                      Number of steps 
        """
    def set_number_of_steps(self, number_of_steps: int) -> None:
        """
                 Sets the number of measurement steps
        
                 Parameters
                 ----------
                 number_of_steps : int
                      Number of measurement steps. Only valid for measurement only mode (constant force mode)
        """
    @property
    def force_values(self) -> numpy.ndarray[numpy.float64]:
        """
                 Sets the custom sweep force values
        
                 Parameters
                 ----------
                 force_values : ndarray
                      The force values
        """
    @force_values.setter
    def force_values(self, arg1: numpy.ndarray) -> None:
        ...
class LogLevel:
    """
    Members:
    
      None_
    
      Error
    
      Warning
    
      Info
    
      Debug
    
      Trace
    """
    Debug: typing.ClassVar[LogLevel]  # value = <LogLevel.Debug: 4>
    Error: typing.ClassVar[LogLevel]  # value = <LogLevel.Error: 1>
    Info: typing.ClassVar[LogLevel]  # value = <LogLevel.Info: 3>
    None_: typing.ClassVar[LogLevel]  # value = <LogLevel.None_: 0>
    Trace: typing.ClassVar[LogLevel]  # value = <LogLevel.Trace: 5>
    Warning: typing.ClassVar[LogLevel]  # value = <LogLevel.Warning: 2>
    __members__: typing.ClassVar[dict[str, LogLevel]]  # value = {'None_': <LogLevel.None_: 0>, 'Error': <LogLevel.Error: 1>, 'Warning': <LogLevel.Warning: 2>, 'Info': <LogLevel.Info: 3>, 'Debug': <LogLevel.Debug: 4>, 'Trace': <LogLevel.Trace: 5>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class LogService:
    """
    
             Log service of the Device Engine  
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def flush_file_log(self) -> None:
        """
                 This method forces a flush of the file log sink, ensuring that all buffered log messages are immediately written to the file.
                 This is essential for ensuring that logs are saved in real-time, particularly in scenarios where immediate persistence of log data
                 is critical, such as before application shutdown or during error handling processes.
        """
    def set_log_file(self, log_file: str) -> None:
        """
                 Sets the path to the log file
        
                 Parameters
                 ----------
                 log_file : str
                      Path to the log file
        """
    @property
    def console_log_level(self) -> LogLevel:
        """
                 Property that gets/sets console log level
        
                 Parameters
                 ----------
                 log_level : LogLevel
                      The log level
        
                 Returns
                 -------
                 LogLevel
                      The current log level for console output
        """
    @console_log_level.setter
    def console_log_level(self, arg1: LogLevel) -> None:
        ...
    @property
    def file_log_level(self) -> LogLevel:
        """
                 Property that gets/sets file log level
        
                 Parameters
                 ----------
                 log_level : LogLevel
                      The log level
        
                 Returns
                 -------
                 LogLevel
                      The current log level for file output
        """
    @file_log_level.setter
    def file_log_level(self, arg1: LogLevel) -> None:
        ...
class MapOfStringVectors:
    """
    Map of string vectors
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self) -> bool:
        """
        Check whether the map is nonempty
        """
    @typing.overload
    def __contains__(self, arg0: str) -> bool:
        ...
    @typing.overload
    def __contains__(self, arg0: typing.Any) -> bool:
        ...
    def __delitem__(self, arg0: str) -> None:
        ...
    def __getitem__(self, arg0: str) -> StringList:
        ...
    def __init__(self) -> None:
        ...
    def __iter__(self) -> typing.Iterator[str]:
        ...
    def __len__(self) -> int:
        ...
    def __setitem__(self, arg0: str, arg1: StringList) -> None:
        ...
    def items(self) -> typing.ItemsView:
        ...
    def keys(self) -> typing.KeysView:
        ...
    def values(self) -> typing.ValuesView:
        ...
class MeasurementMode:
    """
    Members:
    
      highZ
    
      isense
    
      vsense
    
      tsense
    """
    __members__: typing.ClassVar[dict[str, MeasurementMode]]  # value = {'highZ': <MeasurementMode.highZ: 3>, 'isense': <MeasurementMode.isense: 0>, 'vsense': <MeasurementMode.vsense: 1>, 'tsense': <MeasurementMode.tsense: 2>}
    highZ: typing.ClassVar[MeasurementMode]  # value = <MeasurementMode.highZ: 3>
    isense: typing.ClassVar[MeasurementMode]  # value = <MeasurementMode.isense: 0>
    tsense: typing.ClassVar[MeasurementMode]  # value = <MeasurementMode.tsense: 2>
    vsense: typing.ClassVar[MeasurementMode]  # value = <MeasurementMode.vsense: 1>
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class ParamterChangedObserverProxy:
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __init__(self) -> None:
        ...
    def register_observer(self, board_model: IdSmuBoardModel, resource_id: str, python_handler: typing.Callable[[], None]) -> None:
        """
                 Initialize all installed idSMU devices on the board
        
                 Parameters
                 ----------
                 board_model : IdSmuBoardModel
        
                 resource_id : str
        
                 python_handler : Functional
        """
    def unregister_observer(self) -> None:
        """
                Leave context manager.
        """
class ReadAdcCommandIdSmuResult(Result):
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __getitem__(self, arg0: str) -> numpy.ndarray[numpy.float64]:
        ...
    def get_execution_time(self) -> int:
        """
                 Gets the execution time in microseconds for the measurement command
        
                 Returns
                 -------
                 int
                      Execution time in microsecontd
        """
    def get_float_values(self, channel_name: str) -> numpy.ndarray[numpy.float64]:
        ...
    @typing.overload
    def get_values(self, channel_number: int) -> DoubleList:
        """
                 Gets the measured values for a channel number
        
                 Parameters
                 ----------
                 channel_number : int
                      The channel number for which the measured values should be retreived
        
                 Returns
                 -------
                 DoubleList
                      A DoubleList object
        """
    @typing.overload
    def get_values(self, channel_name: str) -> DoubleList:
        """
                 Gets the measured values for a channel name
        
                 Parameters
                 ----------
                 channel_name : str
                      The channel name for which the measured values should be retreived
        
                 Returns
                 -------
                 DoubleList
                      A DoubleList object
        """
    @property
    def channel_ids(self) -> StringList:
        """
                 Returns the channel ids associated with the results
        
                 Returns
                 -------
                 List[str]
                      Channel Ids
        """
    @property
    def channel_names(self) -> StringList:
        """
                 Returns the channel names associated with the results
        
                 Returns
                 -------
                 List[str]
                      Channel names
        """
    @property
    def device_id(self) -> str:
        """
                 Returns the device id associated with the results
        
                 Returns
                 -------
                 str
                      Device Id
        """
    @property
    def execution_time(self) -> int:
        """
                 Gets the execution time in microseconds for the measurement command
        
                 Returns
                 -------
                 int
                      Execution time in microseconts
        """
    @property
    def timecode(self) -> numpy.ndarray[numpy.uint32]:
        """
                 Gets the timecodes for the measurement command
        
                 Returns
                 -------
                 ndarray[int]
                      Array of time code values
        """
class ReadWriteFpgaIdSmuResult(Result):
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class Result(CommandReply):
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class RowFilter:
    column_name: str
    exact_match: bool
    filter_expression: str
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
class SequencingCommandResult(Result):
    """
    
             The result of a sequencing command.
        
    """
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def get_device_id(self) -> str:
        ...
    def get_results(self) -> list[CommandReply]:
        ...
class SmuCurrentRange:
    """
    Members:
    
      Range_5uA
    
      Range_20uA
    
      Range_200uA
    
      Range_2mA
    
      Range_70mA
    """
    Range_200uA: typing.ClassVar[SmuCurrentRange]  # value = <SmuCurrentRange.Range_200uA: 2>
    Range_20uA: typing.ClassVar[SmuCurrentRange]  # value = <SmuCurrentRange.Range_20uA: 1>
    Range_2mA: typing.ClassVar[SmuCurrentRange]  # value = <SmuCurrentRange.Range_2mA: 3>
    Range_5uA: typing.ClassVar[SmuCurrentRange]  # value = <SmuCurrentRange.Range_5uA: 0>
    Range_70mA: typing.ClassVar[SmuCurrentRange]  # value = <SmuCurrentRange.Range_70mA: 4>
    __members__: typing.ClassVar[dict[str, SmuCurrentRange]]  # value = {'Range_5uA': <SmuCurrentRange.Range_5uA: 0>, 'Range_20uA': <SmuCurrentRange.Range_20uA: 1>, 'Range_200uA': <SmuCurrentRange.Range_200uA: 2>, 'Range_2mA': <SmuCurrentRange.Range_2mA: 3>, 'Range_70mA': <SmuCurrentRange.Range_70mA: 4>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: int) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: int) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class StringList:
    """
    List of strings.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: str) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: StringList) -> bool:
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> StringList:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> str:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: StringList) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[str]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: StringList) -> bool:
        ...
    def __repr__(self) -> str:
        """
        Return the canonical string representation of this list.
        """
    @typing.overload
    def __setitem__(self, arg0: int, arg1: str) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: StringList) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: str) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: str) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: StringList) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: str) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> str:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> str:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: str) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
class StringTable:
    """
    Table of strings.
    """
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs):
        ...
    def __bool__(self) -> bool:
        """
        Check whether the list is nonempty
        """
    def __contains__(self, x: StringList) -> bool:
        """
        Return true the container contains ``x``
        """
    @typing.overload
    def __delitem__(self, arg0: int) -> None:
        """
        Delete the list elements at index ``i``
        """
    @typing.overload
    def __delitem__(self, arg0: slice) -> None:
        """
        Delete list elements using a slice object
        """
    def __eq__(self, arg0: StringTable) -> bool:
        ...
    @typing.overload
    def __getitem__(self, s: slice) -> StringTable:
        """
        Retrieve list elements using a slice object
        """
    @typing.overload
    def __getitem__(self, arg0: int) -> StringList:
        ...
    @typing.overload
    def __init__(self) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: StringTable) -> None:
        """
        Copy constructor
        """
    @typing.overload
    def __init__(self, arg0: typing.Iterable) -> None:
        ...
    def __iter__(self) -> typing.Iterator[StringList]:
        ...
    def __len__(self) -> int:
        ...
    def __ne__(self, arg0: StringTable) -> bool:
        ...
    @typing.overload
    def __setitem__(self, arg0: int, arg1: StringList) -> None:
        ...
    @typing.overload
    def __setitem__(self, arg0: slice, arg1: StringTable) -> None:
        """
        Assign list elements using a slice object
        """
    def append(self, x: StringList) -> None:
        """
        Add an item to the end of the list
        """
    def clear(self) -> None:
        """
        Clear the contents
        """
    def count(self, x: StringList) -> int:
        """
        Return the number of times ``x`` appears in the list
        """
    @typing.overload
    def extend(self, L: StringTable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    @typing.overload
    def extend(self, L: typing.Iterable) -> None:
        """
        Extend the list by appending all the items in the given list
        """
    def insert(self, i: int, x: StringList) -> None:
        """
        Insert an item at a given position.
        """
    @typing.overload
    def pop(self) -> StringList:
        """
        Remove and return the last item
        """
    @typing.overload
    def pop(self, i: int) -> StringList:
        """
        Remove and return the item at index ``i``
        """
    def remove(self, x: StringList) -> None:
        """
        Remove the first item from the list whose value is x. It is an error if there is no such item.
        """
def check_future_is_ready(arg0: CommandReplyFuture) -> bool:
    ...
def generate_function_generator_data(min_value: float, max_value: float, step_size: float, function_generator_type: FunctionGeneratorType) -> list[float]:
    """
             Returns the force values that are used by the function_generator method
    
             Parameters
             ----------
             min_value : float
                  Minimum in generated function
             max_value : float
                  Maximum in generated function
             step_size : float
                  Voltage step
             function_generator_type : FunctionGeneratorType
                  The type of the function generator
    """
def get_build_number() -> int:
    """
             Returns the build number
            
             Returns
             -------
             int
    """
def get_git_version() -> int:
    """
             Returns the git version
            
             Returns
             -------
             int
    """
__version__: str = '0.9.580'
