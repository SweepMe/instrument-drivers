from __future__ import annotations

import struct

from pysweepme import get_port

MODBUS_ADDRESS = 1

port = get_port(
    ID="COM12",
    properties={
        "baudrate": 38400,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1,
        "timeout": 10,
    },
)

def build_request_read(address: int, num_words: int) -> bytes:
    """Builds a Modbus RTU request to read 'num_words' words starting from 'address'."""
    data = [
        MODBUS_ADDRESS,
        0x03,
        (address >> 8) & 0xFF,
        address & 0xFF,
        (num_words >> 8) & 0xFF,
        num_words & 0xFF,
    ]
    crc = crc16(data)
    return bytes(data + crc)

def crc16(data: list[int]) -> list[int]:
    """CRC16 (Modbus RTU) calculation"""
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return [crc & 0xFF, (crc >> 8) & 0xFF]

def print_bytes(data: bytes) -> None:
    hexstr = ''.join(f"{b:02X}" for b in data)
    groups = ' '.join(hexstr[i:i+4] for i in range(0, len(hexstr), 4))
    print(groups)

def write_float(address: int, value: float) -> None:
    """Writes a FLOAT (2 words) to the given Modbus address"""
    packed = struct.pack(">f", value)
    reordered = packed[2:4] + packed[0:2]
    data = list(reordered)
    request = build_request_write_n_words(address, data)
    print_bytes(request)
    port.write_raw(request)

    port.read_raw(8)  # read ack

def write_int32(address: int, value: int) -> None:
    packed = struct.pack(">I", int(value))   # big-endian 4 bytes
    # if manual expects high-word then low-word as 00 00 00 67, packed is b'\x00\x00\x00\x67'
    data = list(packed)
    request = build_request_write_n_words(address, data)
    print_bytes(request)
    port.write_raw(request)
    port.read_raw(8)  # ack

def build_request_write_n_words(address: int, byte_data: list[int]) -> bytes:
    word_count = len(byte_data) // 2
    data = [
        MODBUS_ADDRESS,
        0x10,
        (address >> 8) & 0xFF,
        address & 0xFF,
        (word_count >> 8) & 0xFF,
        word_count & 0xFF,
        len(byte_data),
    ] + byte_data
    crc = crc16(data)
    return bytes(data + crc)













ret = port.query("0110 2114 0002 0400 0000 0067 01")
print(ret)

# Conversion works correctly, the number of from the debug matches the example query
write_float(8468, 0)
write_int32(8468, 100)

# read setpoint "0103 7010 0008 5F09"
port.write("0504 000 001 304E")  # readout current
ret = port.read_raw()
# show raw bytes for debugging
print_bytes(ret)  # e.g. '01 03 10 08 ...' grouped

# Also print ascii/hex read (if user-level read returns a string)
try:
    ascii_read = port.read()
    print('port.read():', ascii_read)
except Exception:
    pass

address = 8468
# request = build_request_read(address, 2)
# print_bytes(request)

# port.write_raw(request)
# response: bytes = port.read_raw(digits=9)
# print(list(response))
# raw = response[3:7]
# reordered = raw[2:4] + raw[0:2]
# result = struct.unpack(">f", reordered)[0]
# print(result)
# print(port.read())
