# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from typing import Optional
from .dto import requests as dto
from .exceptions.motion_lib_exception import MotionLibException
from .exceptions.bad_command_exception import BadCommandException
from .exceptions.bad_data_exception import BadDataException
from .exceptions.binary_command_failed_exception import BinaryCommandFailedException
from .exceptions.command_failed_exception import CommandFailedException
from .exceptions.command_preempted_exception import CommandPreemptedException
from .exceptions.command_too_long_exception import CommandTooLongException
from .exceptions.connection_closed_exception import ConnectionClosedException
from .exceptions.connection_failed_exception import ConnectionFailedException
from .exceptions.conversion_failed_exception import ConversionFailedException
from .exceptions.device_address_conflict_exception import DeviceAddressConflictException
from .exceptions.device_busy_exception import DeviceBusyException
from .exceptions.device_db_failed_exception import DeviceDbFailedException
from .exceptions.device_detection_failed_exception import DeviceDetectionFailedException
from .exceptions.device_failed_exception import DeviceFailedException
from .exceptions.device_not_identified_exception import DeviceNotIdentifiedException
from .exceptions.driver_disabled_exception import DriverDisabledException
from .exceptions.g_code_execution_exception import GCodeExecutionException
from .exceptions.g_code_syntax_exception import GCodeSyntaxException
from .exceptions.ge_1_x_gripper_movement_failed_exception import Ge1xGripperMovementFailedException
from .exceptions.incompatible_shared_library_exception import IncompatibleSharedLibraryException
from .exceptions.internal_error_exception import InternalErrorException
from .exceptions.invalid_argument_exception import InvalidArgumentException
from .exceptions.invalid_csv_data_exception import InvalidCsvDataException
from .exceptions.invalid_data_exception import InvalidDataException
from .exceptions.invalid_operation_exception import InvalidOperationException
from .exceptions.invalid_packet_exception import InvalidPacketException
from .exceptions.invalid_park_state_exception import InvalidParkStateException
from .exceptions.invalid_request_data_exception import InvalidRequestDataException
from .exceptions.invalid_response_exception import InvalidResponseException
from .exceptions.io_channel_out_of_range_exception import IoChannelOutOfRangeException
from .exceptions.io_failed_exception import IoFailedException
from .exceptions.lockstep_enabled_exception import LockstepEnabledException
from .exceptions.lockstep_not_enabled_exception import LockstepNotEnabledException
from .exceptions.movement_failed_exception import MovementFailedException
from .exceptions.movement_interrupted_exception import MovementInterruptedException
from .exceptions.no_device_found_exception import NoDeviceFoundException
from .exceptions.no_value_for_key_exception import NoValueForKeyException
from .exceptions.not_supported_exception import NotSupportedException
from .exceptions.operation_failed_exception import OperationFailedException
from .exceptions.os_failed_exception import OsFailedException
from .exceptions.out_of_request_ids_exception import OutOfRequestIdsException
from .exceptions.pvt_discontinuity_exception import PvtDiscontinuityException
from .exceptions.pvt_execution_exception import PvtExecutionException
from .exceptions.pvt_mode_exception import PvtModeException
from .exceptions.pvt_movement_failed_exception import PvtMovementFailedException
from .exceptions.pvt_movement_interrupted_exception import PvtMovementInterruptedException
from .exceptions.pvt_sequence_generation_failed_exception import PvtSequenceGenerationFailedException
from .exceptions.pvt_setup_failed_exception import PvtSetupFailedException
from .exceptions.remote_mode_exception import RemoteModeException
from .exceptions.request_timeout_exception import RequestTimeoutException
from .exceptions.serial_port_busy_exception import SerialPortBusyException
from .exceptions.set_device_state_failed_exception import SetDeviceStateFailedException
from .exceptions.set_peripheral_state_failed_exception import SetPeripheralStateFailedException
from .exceptions.stream_discontinuity_exception import StreamDiscontinuityException
from .exceptions.stream_execution_exception import StreamExecutionException
from .exceptions.stream_mode_exception import StreamModeException
from .exceptions.stream_movement_failed_exception import StreamMovementFailedException
from .exceptions.stream_movement_interrupted_exception import StreamMovementInterruptedException
from .exceptions.stream_setup_failed_exception import StreamSetupFailedException
from .exceptions.timeout_exception import TimeoutException
from .exceptions.transport_already_used_exception import TransportAlreadyUsedException
from .exceptions.unknown_request_exception import UnknownRequestException

errorMap = {
    "BAD_COMMAND": BadCommandException,
    "BAD_DATA": BadDataException,
    "BINARY_COMMAND_FAILED": BinaryCommandFailedException,
    "COMMAND_FAILED": CommandFailedException,
    "COMMAND_PREEMPTED": CommandPreemptedException,
    "COMMAND_TOO_LONG": CommandTooLongException,
    "CONNECTION_CLOSED": ConnectionClosedException,
    "CONNECTION_FAILED": ConnectionFailedException,
    "CONVERSION_FAILED": ConversionFailedException,
    "DEVICE_ADDRESS_CONFLICT": DeviceAddressConflictException,
    "DEVICE_BUSY": DeviceBusyException,
    "DEVICE_DB_FAILED": DeviceDbFailedException,
    "DEVICE_DETECTION_FAILED": DeviceDetectionFailedException,
    "DEVICE_FAILED": DeviceFailedException,
    "DEVICE_NOT_IDENTIFIED": DeviceNotIdentifiedException,
    "DRIVER_DISABLED": DriverDisabledException,
    "G_CODE_EXECUTION": GCodeExecutionException,
    "G_CODE_SYNTAX": GCodeSyntaxException,
    "GE_1_X_GRIPPER_MOVEMENT_FAILED": Ge1xGripperMovementFailedException,
    "INCOMPATIBLE_SHARED_LIBRARY": IncompatibleSharedLibraryException,
    "INTERNAL_ERROR": InternalErrorException,
    "INVALID_ARGUMENT": InvalidArgumentException,
    "INVALID_CSV_DATA": InvalidCsvDataException,
    "INVALID_DATA": InvalidDataException,
    "INVALID_OPERATION": InvalidOperationException,
    "INVALID_PACKET": InvalidPacketException,
    "INVALID_PARK_STATE": InvalidParkStateException,
    "INVALID_REQUEST_DATA": InvalidRequestDataException,
    "INVALID_RESPONSE": InvalidResponseException,
    "IO_CHANNEL_OUT_OF_RANGE": IoChannelOutOfRangeException,
    "IO_FAILED": IoFailedException,
    "LOCKSTEP_ENABLED": LockstepEnabledException,
    "LOCKSTEP_NOT_ENABLED": LockstepNotEnabledException,
    "MOVEMENT_FAILED": MovementFailedException,
    "MOVEMENT_INTERRUPTED": MovementInterruptedException,
    "NO_DEVICE_FOUND": NoDeviceFoundException,
    "NO_VALUE_FOR_KEY": NoValueForKeyException,
    "NOT_SUPPORTED": NotSupportedException,
    "OPERATION_FAILED": OperationFailedException,
    "OS_FAILED": OsFailedException,
    "OUT_OF_REQUEST_IDS": OutOfRequestIdsException,
    "PVT_DISCONTINUITY": PvtDiscontinuityException,
    "PVT_EXECUTION": PvtExecutionException,
    "PVT_MODE": PvtModeException,
    "PVT_MOVEMENT_FAILED": PvtMovementFailedException,
    "PVT_MOVEMENT_INTERRUPTED": PvtMovementInterruptedException,
    "PVT_SEQUENCE_GENERATION_FAILED": PvtSequenceGenerationFailedException,
    "PVT_SETUP_FAILED": PvtSetupFailedException,
    "REMOTE_MODE": RemoteModeException,
    "REQUEST_TIMEOUT": RequestTimeoutException,
    "SERIAL_PORT_BUSY": SerialPortBusyException,
    "SET_DEVICE_STATE_FAILED": SetDeviceStateFailedException,
    "SET_PERIPHERAL_STATE_FAILED": SetPeripheralStateFailedException,
    "STREAM_DISCONTINUITY": StreamDiscontinuityException,
    "STREAM_EXECUTION": StreamExecutionException,
    "STREAM_MODE": StreamModeException,
    "STREAM_MOVEMENT_FAILED": StreamMovementFailedException,
    "STREAM_MOVEMENT_INTERRUPTED": StreamMovementInterruptedException,
    "STREAM_SETUP_FAILED": StreamSetupFailedException,
    "TIMEOUT": TimeoutException,
    "TRANSPORT_ALREADY_USED": TransportAlreadyUsedException,
    "UNKNOWN_REQUEST": UnknownRequestException,
}


def convert_exception(error_type: dto.Errors, message: str, custom_data: Optional[bytes] = None) -> MotionLibException:
    if custom_data:
        return errorMap[error_type.name](message, custom_data)  # type: ignore
    return errorMap[error_type.name](message)  # type: ignore
