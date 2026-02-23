import logging

from pymodbus.client import ModbusSerialClient

# Enable detailed logging for pymodbus to debug sent/received frames
logging.basicConfig(format='%(asctime)s %(name)s %(levelname)s: %(message)s', level=logging.DEBUG)
logging.getLogger('pymodbus').setLevel(logging.DEBUG)
logging.getLogger('pymodbus.transaction').setLevel(logging.DEBUG)
logging.getLogger('pymodbus.client').setLevel(logging.DEBUG)

client = ModbusSerialClient(
    port="COM6",
    baudrate=38400,
    bytesize=8,
    parity="N",
    stopbits=1,
    timeout=10,
)

client.connect()

SLAVE_ID = 1  # typical JUMO default

# actual_value_address = 28690 - 1
setpoint_value_address = 8468 - 1

readout_methods = [
    "read_holding_registers",
    "read_input_registers",
    "read_discrete_inputs",
]

addresses = [
    # 28468,
    # 28468 - 1,
    8468,
    # 8468 - 1,
    28688,
]

# small helper: compute Modbus RTU CRC16 (low, high)
def crc16(data: list[int]) -> list[int]:
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


def bytes_to_hex_str(b: bytes) -> str:
    return ' '.join(f"{x:02X}" for x in b)


# convenience mapping from function name to Modbus function code
FUNC_CODE = {
    'read_holding_registers': 0x03,
    'read_input_registers': 0x04,
    'read_discrete_inputs': 0x02,
}

# helper to build an RTU request (slave, func, addr_hi, addr_lo, count_hi, count_lo, crc_lo, crc_hi)
def build_rtu_request(slave: int, func: int, address: int, count: int) -> bytes:
    payload = [slave, func, (address >> 8) & 0xFF, address & 0xFF, (count >> 8) & 0xFF, count & 0xFF]
    crc = crc16(payload)
    return bytes(payload + crc)


# # Example: explicitly build a request and print it
# req = build_rtu_request(SLAVE_ID, 0x03, 8468, 2)
# logging.debug("Example RTU request for address=8468 count=2: %s", bytes_to_hex_str(req))


# “0110 2114 0002 0400 0000 0067 01”

# call once to warm-up
response = client.read(
    address=8468,
    count=2,
    slave=SLAVE_ID
)

print("test")
#
#
# for address in addresses:
#     for func_name in readout_methods:
#         try:
#             func = client.__getattribute__(func_name)
#
#             # build and log the raw RTU frame we will send
#             func_code = FUNC_CODE.get(func_name, 0x03)
#             # usually reading registers uses 'count' in words; use 2 words for a float32
#             request_frame = build_rtu_request(SLAVE_ID, func_code, address, 2)
#             logging.debug("About to send (RTU): %s for %s at address %s", bytes_to_hex_str(request_frame), func_name, address)
#
#             result = func(
#                 address=setpoint_value_address,
#                 count=2,
#                 slave=SLAVE_ID
#             )
#             print(address, func_name, result)
#         except Exception as e:
#             print(address, func_name, e)

