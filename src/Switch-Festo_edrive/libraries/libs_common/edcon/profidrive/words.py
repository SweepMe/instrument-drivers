"""Contains code that is related to PROFIDRIVE words"""

from dataclasses import dataclass, fields
from edcon.utils.boollist import bytes_to_boollist, boollist_to_bytes


class BitwiseWord:
    """This is the base class for any word that is considered a set of bitwise values"""

    byte_size: int = 2

    def __len__(self):
        """Returns the size of the word in bytes"""
        return self.byte_size

    def __int__(self):
        """Returns the integer representation"""
        return int.from_bytes(self.to_bytes(), 'little')

    def size(self):
        """Returns the size of the word in bytes"""
        return len(self.to_bytes())

    def to_bytes(self):
        """Returns the bytes representation"""
        blist = [getattr(self, v.name) for v in fields(self)]
        return boollist_to_bytes(blist)

    @classmethod
    def from_bytes(cls, data: bytes):
        """Initializes a BitwiseWord from a byte representation"""
        return cls(*bytes_to_boollist(data))

    @classmethod
    def from_int(cls, value: int):
        """Initializes a BitwiseWord from an integer"""
        return cls.from_bytes(value.to_bytes(cls.byte_size, 'little'))


@dataclass
class BitwiseWordGeneric(BitwiseWord):
    """This is a generic derivative of BitwiseWord e.g. to test it's methods"""
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    bit0: bool = False
    bit1: bool = False
    bit2: bool = False
    bit3: bool = False
    bit4: bool = False
    bit5: bool = False
    bit6: bool = False
    bit7: bool = False
    bit8: bool = False
    bit9: bool = False
    bit10: bool = False
    bit11: bool = False
    bit12: bool = False
    bit13: bool = False
    bit14: bool = False
    bit15: bool = False


@dataclass
class STW1_SM(BitwiseWord):
    """Implementation of STW1 in velocity mode"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    # pylint: disable=invalid-name
    on: bool = False
    no_coast_stop: bool = False
    no_quick_stop: bool = False
    enable_operation: bool = False
    enable_ramp_generator: bool = False
    unfreeze_ramp_generator: bool = False
    setpoint_enable: bool = False
    fault_ack: bool = False
    jog1_on: bool = False
    jog2_on: bool = False
    control_by_plc: bool = False
    invert_setpoint: bool = False
    open_holding_brake: bool = False
    motor_pot_increase: bool = False
    motor_pot_decrease: bool = False
    reserved1: bool = False


@dataclass
class STW1_PM(BitwiseWord):
    """Implementation of STW1 in position mode"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    # pylint: disable=invalid-name
    on: bool = False
    no_coast_stop: bool = False
    no_quick_stop: bool = False
    enable_operation: bool = False
    do_not_reject_traversing_task: bool = False
    no_intermediate_stop: bool = False
    activate_traversing_task: bool = False
    fault_ack: bool = False
    jog1_on: bool = False
    jog2_on: bool = False
    control_by_plc: bool = False
    start_homing_procedure: bool = False
    open_holding_brake: bool = False
    change_record_no: bool = False
    reserved1: bool = False
    reserved2: bool = False


@dataclass
class SATZANW(BitwiseWord):
    """Implementation of SATZANW"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    satzanw_bit0: bool = False
    satzanw_bit1: bool = False
    satzanw_bit2: bool = False
    satzanw_bit3: bool = False
    satzanw_bit4: bool = False
    satzanw_bit5: bool = False
    satzanw_bit6: bool = False
    reserved1: bool = False
    reserved2: bool = False
    reserved3: bool = False
    reserved4: bool = False
    reserved5: bool = False
    reserved6: bool = False
    reserved7: bool = False
    reserved8: bool = False
    mdi_active: bool = False


@dataclass
class STW2(BitwiseWord):
    """Implementation of STW2"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    reserved1: bool = False
    reserved2: bool = False
    reserved3: bool = False
    reserved4: bool = False
    reserved5: bool = False
    reserved6: bool = False
    reserved7: bool = False
    parking_axis: bool = False
    traversing_fixed_stop: bool = False
    reserved8: bool = False
    reserved9: bool = False
    motor_switch: bool = False
    sign_of_life0: bool = False
    sign_of_life1: bool = False
    sign_of_life2: bool = False
    sign_of_life3: bool = False


@dataclass
class POS_STW1(BitwiseWord):
    """Implementation of POS_STW1"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here
    record_table_selection0: bool = False
    record_table_selection1: bool = False
    record_table_selection2: bool = False
    record_table_selection3: bool = False
    record_table_selection4: bool = False
    record_table_selection5: bool = False
    record_table_selection6: bool = False
    reserved1: bool = False
    absolute_position: bool = False
    positioning_direction0: bool = False
    positioning_direction1: bool = False
    reserved2: bool = False
    continuous_update: bool = False
    reserved3: bool = False
    activate_setup: bool = False
    activate_mdi: bool = False


@dataclass
class POS_STW2(BitwiseWord):
    """Implementation of POS_STW1"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here
    activate_tracking_mode: bool = False
    set_reference_point: bool = False
    reserved1: bool = False
    reserved2: bool = False
    reserved3: bool = False
    incremental_jogging: bool = False
    reserved4: bool = False
    reserved5: bool = False
    reserved6: bool = False
    reserved7: bool = False
    measuring_probe2_is_activated: bool = False
    falling_edge_of_measuring_probe: bool = False
    reserved8: bool = False
    reserved9: bool = False
    activate_software_limit_switch: bool = False
    activate_hardware_limit_switch: bool = False


@dataclass
class ZSW1_SM(BitwiseWord):
    """Implementation of ZSW1 in velocity mode"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    ready_to_switch_on: bool = False
    ready_to_operate: bool = False
    operation_enabled: bool = False
    fault_present: bool = False
    coast_stop_not_activated: bool = False
    quick_stop_not_activated: bool = False
    switching_on_inhibited: bool = False
    warning_present: bool = False
    speed_error_within_tolerance_range: bool = False
    control_requested: bool = False
    f_or_n_reached_or_exceeded: bool = False
    im_or_p_not_reached: bool = False
    holding_break_released: bool = False
    motor_temp_warning_inactive: bool = False
    positive_direction_rotation: bool = False
    ps_temp_warning_inactive: bool = False


@dataclass
class ZSW1_PM(BitwiseWord):
    """Implementation of ZSW1 in position mode"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    ready_to_switch_on: bool = False
    ready_to_operate: bool = False
    operation_enabled: bool = False
    fault_present: bool = False
    coast_stop_not_activated: bool = False
    quick_stop_not_activated: bool = False
    switching_on_inhibited: bool = False
    warning_present: bool = False
    following_error_within_tolerance_range: bool = False
    control_requested: bool = False
    target_position_reached: bool = False
    home_position_set: bool = False
    traversing_task_ack: bool = False
    drive_stopped: bool = False
    axis_accelerates: bool = False
    axis_decelerates: bool = False


@dataclass
class AKTSATZ(BitwiseWord):
    """Implementation of AKTSATZ"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    aktsatz_bit0: bool = False
    aktsatz_bit1: bool = False
    aktsatz_bit2: bool = False
    aktsatz_bit3: bool = False
    aktsatz_bit4: bool = False
    aktsatz_bit5: bool = False
    aktsatz_bit6: bool = False
    reserved1: bool = False
    reserved2: bool = False
    reserved3: bool = False
    reserved4: bool = False
    reserved5: bool = False
    reserved6: bool = False
    reserved7: bool = False
    reserved8: bool = False
    mdi_active: bool = False


@dataclass
class ZSW2(BitwiseWord):
    """Implementation of ZSW2"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    reserved1: bool = False
    reserved2: bool = False
    reserved3: bool = False
    reserved4: bool = False
    reserved5: bool = False
    reserved6: bool = False
    reserved7: bool = False
    axis_parking: bool = False
    fixed_stop: bool = False
    reserved8: bool = False
    reserved9: bool = False
    pulses_enabled: bool = False
    sign_of_life0: bool = False
    sign_of_life1: bool = False
    sign_of_life2: bool = False
    sign_of_life3: bool = False


@dataclass
class POS_ZSW1(BitwiseWord):
    """Implementation of POS_ZSW1"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    record_table_selection0: bool = False
    record_table_selection1: bool = False
    record_table_selection2: bool = False
    record_table_selection3: bool = False
    record_table_selection4: bool = False
    record_table_selection5: bool = False
    record_table_selection6: bool = False
    reserved1: bool = False
    negative_hardware_limit_switch_active: bool = False
    positive_hardware_limit_switch_active: bool = False
    jogging_active: bool = False
    homing_active: bool = False
    reserved2: bool = False
    record_mode_active: bool = False
    setup_active: bool = False
    mdi_active: bool = False


@dataclass
class POS_ZSW2(BitwiseWord):
    """Implementation of POS_ZSW2"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    tracking_mode_active: bool = False
    velocity_limiting_active: bool = False
    setpoint_available: bool = False
    reserved1: bool = False
    axis_moves_forward: bool = False
    axis_moves_backward: bool = False
    negative_software_limit_switch_active: bool = False
    positive_software_limit_switch_active: bool = False
    position_actual_value_lower_equal_cam_switch1: bool = False
    position_actual_value_lower_equal_cam_switch2: bool = False
    direct_output1_via_traversing_block: bool = False
    direct_output2_via_traversing_block: bool = False
    fixed_stop_reached: bool = False
    fixed_stop_clamping_torque_reached: bool = False
    travel_to_fixed_stop_active: bool = False
    traversing_command_active: bool = False


@dataclass
class MELDW(BitwiseWord):
    """Implementation of MELDW"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    ramp_function_completed: bool = False
    torque_utilization_lower_threshold: bool = False
    rpm_lower_threshold: bool = False
    rpm_equal_threshold: bool = False
    reserved1: bool = False
    variable_signal_function: bool = False
    motor_temp_warning_inactive: bool = False
    ps_temp_warning_inactive: bool = False
    speed_setpoint_deviation_in_tolerance: bool = False
    reserved2: bool = False
    reserved3: bool = False
    controller_enabled: bool = False
    drive_ready: bool = False
    pulses_enabled: bool = False
    reserved4: bool = False
    reserved5: bool = False


@dataclass
class G1_STW(BitwiseWord):
    """Implementation of G1_STW"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    function0: bool = False
    function1: bool = False
    function2: bool = False
    function3: bool = False
    command0: bool = False
    command1: bool = False
    command2: bool = False
    mode: bool = False
    reserved1: bool = False
    reserved2: bool = False
    reserved3: bool = False
    home_pos_mode: bool = False
    request_set_shift_home_pos: bool = False
    request_abs_val_cyc: bool = False
    activate_park_sens: bool = False
    acknowledge_sens_err: bool = False


@dataclass
class G1_ZSW(BitwiseWord):
    """Implementation of G1_ZSW"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    function_status0: bool = False
    function_status1: bool = False
    function_status2: bool = False
    function_status3: bool = False
    value_status0: bool = False
    value_status1: bool = False
    value_status2: bool = False
    value_status3: bool = False
    probe1_deflected: bool = False
    probe2_deflected: bool = False
    reserved1: bool = False
    error_acknowledge: bool = False
    set_shift_home_pos_executed: bool = False
    transmit_abs_value_cyc: bool = False
    park_sens_active: bool = False
    sens_error: bool = False


@dataclass
class MDI_MOD(BitwiseWord):
    """Implementation of MDI_MOD"""
    # pylint: disable=invalid-name
    # pylint: disable=too-many-instance-attributes
    # Sixteen is needed here

    absolute_position: bool = False
    modulo_direction_positive: bool = False
    modulo_direction_negative: bool = False
    reserved1: bool = False
    reserved2: bool = False
    reserved3: bool = False
    reserved4: bool = False
    reserved5: bool = False
    reserved6: bool = False
    reserved7: bool = False
    reserved8: bool = False
    reserved9: bool = False
    reserved10: bool = False
    reserved11: bool = False
    reserved12: bool = False
    reserved13: bool = False


@dataclass
class IntWord:
    """This is the base class for any word that is considered a  (16 bit) integer value"""

    value: int = 0
    byte_size: int = 2

    def __len__(self):
        """Returns the size of the word in bytes"""
        return self.byte_size

    def __int__(self):
        """Returns the integer representation"""
        return getattr(self, fields(self)[0].name)

    def to_bytes(self) -> bytes:
        """Returns the bytes representation"""
        return int(self).to_bytes(2, 'little', signed=True)

    @classmethod
    def from_bytes(cls, data: bytes):
        """Initializes a int word value from a byte representation"""
        return cls(int.from_bytes(data, 'little', signed=True))

    @classmethod
    def from_int(cls, value: int):
        """Initializes a int word value from an integer"""
        return cls.from_bytes(value.to_bytes(cls.byte_size, 'little'))


class NSOLL_A(IntWord):  # pylint: disable=invalid-name
    """Implementation of NSOLL_A setpoint speed word"""


class NIST_A(IntWord):  # pylint: disable=invalid-name
    """Implementation of NIST_A current speed word"""


class MOMRED(IntWord):  # pylint: disable=invalid-name
    """Implementation of MOMRED current speed word"""


class OVERRIDE(IntWord):  # pylint: disable=invalid-name
    """Implementation of OVERRIDE word"""


class MDI_ACC(IntWord):  # pylint: disable=invalid-name
    """Implementation of MDI_ACC word"""


class MDI_DEC(IntWord):  # pylint: disable=invalid-name
    """Implementation of MDI_DEC word"""


class FAULT_CODE(IntWord):  # pylint: disable=invalid-name
    """Implementation of FAULT_CODE word"""


class WARN_CODE(IntWord):  # pylint: disable=invalid-name
    """Implementation of WARN_CODE word"""


@dataclass
class IntDoubleWord:
    """This is the base class for any word that is considered a (32 bit) integer value"""

    value: int = 0
    byte_size: int = 4

    def __len__(self):
        """Returns the size of the word in bytes"""
        return self.byte_size

    def __int__(self):
        """Returns the integer representation"""
        return getattr(self, fields(self)[0].name)

    def to_bytes(self) -> bytes:
        """Returns the bytes representation"""
        return int(self).to_bytes(4, 'little', signed=True)

    @classmethod
    def from_bytes(cls, data: bytes):
        """Initializes a int double word value from a byte representation"""
        return cls(int.from_bytes(data, 'little', signed=True))

    @classmethod
    def from_int(cls, value: int):
        """Initializes a int double word value from an integer"""
        return cls.from_bytes(value.to_bytes(cls.byte_size, 'little'))


class NSOLL_B(IntDoubleWord):  # pylint: disable=invalid-name
    """Implementation of NSOLL_B word"""


class NIST_B(IntDoubleWord):  # pylint: disable=invalid-name
    """Implementation of NIST_B word"""


class MDI_TARPOS(IntDoubleWord):  # pylint: disable=invalid-name
    """Implementation of MDI_TARPOS word"""


class MDI_VELOCITY(IntDoubleWord):  # pylint: disable=invalid-name
    """Implementation of MDI_VELOCITY word"""


class XIST_A(IntDoubleWord):  # pylint: disable=invalid-name
    """Implementation of XIST_A word"""


class G1_XIST1(IntDoubleWord):  # pylint: disable=invalid-name
    """Implementation of G1_XIST1 word"""


class G1_XIST2(IntDoubleWord):  # pylint: disable=invalid-name
    """Implementation of G1_XIST2 word"""
