from pysweepme import get_port

MODBUS_ADDRESS = 1

port = get_port(
    ID="COM6",
    properties={
        "baudrate": 38400,
        "bytesize": 8,
        "parity": "N",
        "stopbits": 1,
        "timeout": 10,
    },
)


def crc16_modbus(data: bytes) -> bytes:
    """Compute Modbus RTU CRC16; return two bytes (low, high)."""
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if crc & 0x0001:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])


def bytes_to_hex_str(b: bytes) -> str:
    return ' '.join(f"{x:02X}" for x in b)


# Manual values from the device manual (hex groups without 0x prefix)
manual_payload_hex = "01 03 70 00 00 02"
# Build payload bytes from the hex string
payload = bytes.fromhex(manual_payload_hex.replace(' ', ''))
# Manual CRC provided by the manual (two bytes, low then high in the example)
manual_crc_hex = "DE CB"
manual_crc = bytes.fromhex(manual_crc_hex.replace(' ', ''))

# Compute CRC over payload
computed_crc = crc16_modbus(payload)

print("Payload               :", bytes_to_hex_str(payload))
print("Manual CRC            :", bytes_to_hex_str(manual_crc))
print("Computed CRC          :", bytes_to_hex_str(computed_crc))

# Prefer computed CRC if manual CRC doesn't match
if manual_crc != computed_crc:
    print("Warning: manual CRC != computed CRC; using computed CRC for sending")
    frame = payload + computed_crc
else:
    frame = payload + manual_crc

print("Frame to send         :", bytes_to_hex_str(frame))

port.write_raw(frame)

resp = port.read_raw()

# Normalize response to bytes for printing
if isinstance(resp, str):
    try:
        resp_bytes = bytes.fromhex(resp.replace(' ', ''))
    except ValueError:
        print('Received (string repr):', repr(resp))
        resp_bytes = b''
else:
    resp_bytes = resp or b''

print('Received (hex)        :', bytes_to_hex_str(resp_bytes))
print('Received (repr)       :', repr(resp))
