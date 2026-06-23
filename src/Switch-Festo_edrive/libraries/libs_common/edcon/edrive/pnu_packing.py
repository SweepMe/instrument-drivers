"""Contains functions which provide mapping of PNU types."""
import struct
from edcon.utils.logging import Logging
from edcon.edrive.parameter_mapping import PnuMap

PNU_TYPE_TO_FORMAT_CHAR = {
    'BOOL': '?',
    'SINT': 'b',
    'INT': 'h',
    'DINT': 'i',
    'LINT': 'q',
    'USINT': 'B',
    'UINT': 'H',
    'UDINT': 'I',
    'ULINT': 'Q',
    'REAL': 'f'
}


def pnu_unpack(pnu: int, raw: bytes, forced_format: str = None):
    """Unpacks a raw byte value to specific type. 
       The type is determined by the pnu_map_file shipped with the package.

    Parameters:
        pnu (int): PNU number of value that should be unpacked.
        raw (bytes): Raw bytes value that should be unpacked.
        forced_format (str): Optional format char (see struct) to force the unpacking strategy.

    Returns:
        value: Unpacked value with determined type
    """
    if forced_format:
        Logging.logger.info(f"PNU {pnu} forced to type ({forced_format})")
        unpack_data_type = forced_format
    else:
        pnu_map = PnuMap()
        pnu_data_type = pnu_map[pnu].data_type
        pnu_name = pnu_map[pnu].name
        Logging.logger.info(f"PNU {pnu} ({pnu_name}) is of type {pnu_data_type}")
        if 'STRING' in pnu_data_type:
            unpack_data_type = f'{len(raw)}s'

        else:
            unpack_data_type = PNU_TYPE_TO_FORMAT_CHAR[pnu_data_type]

    if unpack_data_type == 's':
        value = struct.unpack(f"{len(raw)}s", raw)[0]
    if unpack_data_type == '?':
        value = struct.unpack('b', raw[0:1])[0]
    if unpack_data_type == 'B':
        value = struct.unpack('B', raw[0:1])[0]
    if unpack_data_type == 'b':
        value = struct.unpack('b', raw[0:1])[0]
    else:
        value = struct.unpack(unpack_data_type, raw)[0]

    return value


def pnu_pack(pnu: int, value, forced_format: str = None) -> bytes:
    """Packs a provided value to raw bytes object.
       The type is determined by the pnu_map_file shipped with the package.

    Parameters:
        pnu (int): PNU number of value that should be unpacked.
        value: Value that should be packed.
        forced_format (str): Optional format char (see struct) to force the packing strategy.

    Returns:
        bytes: Packed value
    """
    if not forced_format:
        pnu_map = PnuMap()
        pnu_data_type = pnu_map[pnu].data_type
        pnu_name = pnu_map[pnu].name
        Logging.logger.info(f"PNU {pnu} ({pnu_name}) is of type {pnu_data_type}")

        if 'INT' in pnu_data_type:
            value = int(value)
        if 'REAL' in pnu_data_type:
            value = float(value)
        if 'STRING' in pnu_data_type:
            return struct.pack('s', bytes(value, encoding='ascii'))
        return struct.pack(PNU_TYPE_TO_FORMAT_CHAR[pnu_data_type], value)

    Logging.logger.info(f"PNU {pnu} forced to type ({forced_format})")
    return struct.pack(forced_format, value)
