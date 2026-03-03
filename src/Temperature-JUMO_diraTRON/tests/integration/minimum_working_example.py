"""
Script for testing remote control of the 4 channel evaporation setup.

ModbusRTU command handling created by Claude.
"""
import struct

# use serial instead of pysweepme for most basic testing
import serial

serial_port = "COM6"
BAUD_RATE   = 38400
TIMEOUT     = 1  # seconds


def parse_modbus_response(response):
    """
    Parse Modbus RTU response containing 4 float32 values.

    Expected response format:
    - Byte 0: Slave address
    - Byte 1: Function code (0x03)
    - Byte 2: Byte count (0x10 = 16 bytes)
    - Bytes 3-18: 4 float32 values (IEEE 754, word-swapped)
    - Bytes 19-20: CRC

    Note: The byte order is swapped within each float32 value.
    Bytes are ordered as 2301 instead of 0123 (word-swapped).

    Args:
        response: bytes object containing the Modbus response

    Returns:
        tuple: (current_temp, diff_temp, set_temp, output_power_percent)
    """
    if len(response) < 21:
        raise ValueError(f"Response too short: {len(response)} bytes, expected at least 21")

    # Extract the data payload (skip address, function code, byte count)
    data_start = 3
    data_end = data_start + 16  # 16 bytes = 4 float32 values

    # Parse 4 float32 values with word-swapped byte order
    # Each float32 is 4 bytes, but words (2-byte pairs) are swapped
    values = []
    for i in range(4):
        offset = data_start + (i * 4)
        # Get 4 bytes: [0, 1, 2, 3] but they're stored as [2, 3, 0, 1]
        # So we need to swap the word order: read bytes 2,3,0,1
        word1 = response[offset + 2:offset + 4]  # bytes 2,3
        word0 = response[offset:offset + 2]      # bytes 0,1
        # Reconstruct in correct order: word0, word1 (which is bytes 2,3,0,1)
        float_bytes = word1 + word0
        # Unpack as big-endian float
        value = struct.unpack('>f', float_bytes)[0]
        values.append(value)

    current_temp = values[1]
    diff_temp = values[2]
    set_temp = values[0]
    output_power_percent = values[3]

    return current_temp, diff_temp, set_temp, output_power_percent


if __name__ == "__main__":
    port = serial.Serial(
        port=serial_port,
        baudrate=38400,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1,
        # xonxoff=False,
        # rtscts=False,
    )

    # Set set point
    setpoint_address = 2114
    value = 21
    set_raw_hex = "0110 2114 0002 0400 0042 4857 97"
    set_raw_hex_clean = set_raw_hex.replace(" ", "")
    set_cmd = bytes.fromhex(set_raw_hex_clean)
    print(f"Sending set point command: {set_raw_hex}, {set_cmd}")
    port.write(set_cmd)
    reponse = port.read(32)
    print(f"Received response: {reponse.hex().upper()}")

    # Commands from the manual already contain the CRC, they just need to be decoded from hex into raw bytes before sending
    raw_hex = "0303 7010 0008 5EEB"  # read 8 words CH3
    raw_hex = "0103 7010 0008 5F09"  # read 8 words
    raw_hex_clean = raw_hex.replace(" ", "")
    cmd = bytes.fromhex(raw_hex_clean)
    print(f"Sending command: {raw_hex}, {cmd}")

    port.reset_input_buffer()
    port.write(cmd)
    # time.sleep(0.1)  # wait for response

    response = port.read(32)  # read up to 32 bytes
    # response = b'\x01\x03\x10\x00\x00B\xc8\x1bLA\xbb9-B\x99\x00\x00B\xc8\xffu'
    print(f"Received response: {response.hex().upper()}")

    # Parse the response
    if len(response) >= 21:
        current_temp, diff_temp, set_temp, output_power = parse_modbus_response(response)
        print(f"\nParsed values:")
        print(f"  Current Temperature: {current_temp:.2f} °C")
        print(f"  Diff Temperature:    {diff_temp:.2f} °C")
        print(f"  Set Temperature:     {set_temp:.2f} °C")
        print(f"  Output Power:        {output_power:.2f} %")