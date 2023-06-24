# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #
from typing import Optional
from .protobufs import main_pb2
from .exceptions.motion_lib_exception import MotionLibException
from .exceptions.binary_command_failed_exception import BinaryCommandFailedException
from .exceptions.command_failed_exception import CommandFailedException
from .exceptions.command_preempted_exception import CommandPreemptedException
from .exceptions.connection_closed_exception import ConnectionClosedException
from .exceptions.connection_failed_exception import ConnectionFailedException
from .exceptions.conversion_failed_exception import ConversionFailedException
from .exceptions.device_address_conflict_exception import DeviceAddressConflictException
from .exceptions.device_busy_exception import DeviceBusyException
from .exceptions.device_db_failed_exception import DeviceDbFailedException
from .exceptions.device_failed_exception import DeviceFailedException
from .exceptions.device_not_identified_exception import DeviceNotIdentifiedException
from .exceptions.internal_error_exception import InternalErrorException
from .exceptions.invalid_argument_exception import InvalidArgumentException
from .exceptions.invalid_data_exception import InvalidDataException
from .exceptions.invalid_packet_exception import InvalidPacketException
from .exceptions.invalid_park_state_exception import InvalidParkStateException
from .exceptions.invalid_response_exception import InvalidResponseException
from .exceptions.io_channel_out_of_range_exception import IoChannelOutOfRangeException
from .exceptions.io_failed_exception import IoFailedException
from .exceptions.lockstep_enabled_exception import LockstepEnabledException
from .exceptions.lockstep_not_enabled_exception import LockstepNotEnabledException
from .exceptions.movement_failed_exception import MovementFailedException
from .exceptions.movement_interrupted_exception import MovementInterruptedException
from .exceptions.no_device_found_exception import NoDeviceFoundException
from .exceptions.not_supported_exception import NotSupportedException
from .exceptions.os_failed_exception import OsFailedException
from .exceptions.out_of_request_ids_exception import OutOfRequestIdsException
from .exceptions.request_timeout_exception import RequestTimeoutException
from .exceptions.serial_port_busy_exception import SerialPortBusyException
from .exceptions.setting_not_found_exception import SettingNotFoundException
from .exceptions.stream_execution_exception import StreamExecutionException
from .exceptions.stream_mode_exception import StreamModeException
from .exceptions.stream_movement_failed_exception import StreamMovementFailedException
from .exceptions.stream_movement_interrupted_exception import StreamMovementInterruptedException
from .exceptions.stream_setup_failed_exception import StreamSetupFailedException
from .exceptions.transport_already_used_exception import TransportAlreadyUsedException
from .exceptions.unknown_request_exception import UnknownRequestException

errorMap = {
    "BINARY_COMMAND_FAILED": BinaryCommandFailedException,
    "COMMAND_FAILED": CommandFailedException,
    "COMMAND_PREEMPTED": CommandPreemptedException,
    "CONNECTION_CLOSED": ConnectionClosedException,
    "CONNECTION_FAILED": ConnectionFailedException,
    "CONVERSION_FAILED": ConversionFailedException,
    "DEVICE_ADDRESS_CONFLICT": DeviceAddressConflictException,
    "DEVICE_BUSY": DeviceBusyException,
    "DEVICE_DB_FAILED": DeviceDbFailedException,
    "DEVICE_FAILED": DeviceFailedException,
    "DEVICE_NOT_IDENTIFIED": DeviceNotIdentifiedException,
    "INTERNAL_ERROR": InternalErrorException,
    "INVALID_ARGUMENT": InvalidArgumentException,
    "INVALID_DATA": InvalidDataException,
    "INVALID_PACKET": InvalidPacketException,
    "INVALID_PARK_STATE": InvalidParkStateException,
    "INVALID_RESPONSE": InvalidResponseException,
    "IO_CHANNEL_OUT_OF_RANGE": IoChannelOutOfRangeException,
    "IO_FAILED": IoFailedException,
    "LOCKSTEP_ENABLED": LockstepEnabledException,
    "LOCKSTEP_NOT_ENABLED": LockstepNotEnabledException,
    "MOVEMENT_FAILED": MovementFailedException,
    "MOVEMENT_INTERRUPTED": MovementInterruptedException,
    "NO_DEVICE_FOUND": NoDeviceFoundException,
    "NOT_SUPPORTED": NotSupportedException,
    "OS_FAILED": OsFailedException,
    "OUT_OF_REQUEST_IDS": OutOfRequestIdsException,
    "REQUEST_TIMEOUT": RequestTimeoutException,
    "SERIAL_PORT_BUSY": SerialPortBusyException,
    "SETTING_NOT_FOUND": SettingNotFoundException,
    "STREAM_EXECUTION": StreamExecutionException,
    "STREAM_MODE": StreamModeException,
    "STREAM_MOVEMENT_FAILED": StreamMovementFailedException,
    "STREAM_MOVEMENT_INTERRUPTED": StreamMovementInterruptedException,
    "STREAM_SETUP_FAILED": StreamSetupFailedException,
    "TRANSPORT_ALREADY_USED": TransportAlreadyUsedException,
    "UNKNOWN_REQUEST": UnknownRequestException,
}


def convert_exception(error_type: int, message: str, custom_data: Optional[bytes] = None) -> MotionLibException:
    if custom_data:
        return errorMap[main_pb2.Errors.Name(error_type)](message, custom_data)  # type: ignore
    return errorMap[main_pb2.Errors.Name(error_type)](message)  # type: ignore
