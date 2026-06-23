import struct
from ctypes import string_at, c_void_p
from functools import reduce
from typing import List

SIZE_TYPE_SIZE = 4
SIZE_TYPE_PACKING = "I"


def serialize(buffers: List[bytes]) -> bytes:
    size = SIZE_TYPE_SIZE + reduce((lambda sum, buffer: sum + len(buffer) + SIZE_TYPE_SIZE), buffers, 0)

    buffer = struct.pack(SIZE_TYPE_PACKING, size)

    for messageBuffer in buffers:
        buffer = buffer + struct.pack(SIZE_TYPE_PACKING, len(messageBuffer)) + bytes(messageBuffer)

    return buffer


def deserialize(data: c_void_p) -> List[bytes]:
    total_size = struct.unpack_from(SIZE_TYPE_PACKING, string_at(data, SIZE_TYPE_SIZE))[0]
    offset = SIZE_TYPE_SIZE

    buffers = []
    while offset < total_size:
        size = struct.unpack_from(SIZE_TYPE_PACKING, string_at(data + offset, SIZE_TYPE_SIZE))[0]  # type: ignore
        offset += SIZE_TYPE_SIZE
        buffers.append(string_at(data + offset, size))  # type: ignore
        offset += size

    return buffers
