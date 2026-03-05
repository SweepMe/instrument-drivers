def calculate_crc16(data: bytes) -> bytes:
    """Calculate CRC16 for Modbus RTU."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    # Return as bytes (low byte first, high byte second - little endian)
    return bytes([crc & 0xFF, (crc >> 8) & 0xFF])


def create_command(
        slave_address: int,
        channel: int,
        value: bool,
) -> bytes:
    """Generate a Modbus RTU command for setting a single register to a bool value."""
    function_code = 5  # Write command
    channel_address = channel - 1  # Map channel 1-8 to register addresses 0-7

    # Build the command payload
    command = bytes([slave_address, function_code])
    command += channel_address.to_bytes(2, byteorder='big')
    # For Modbus FC05, True = 0xFF00, False = 0x0000
    command += (0xFF00 if value else 0x0000).to_bytes(2, byteorder='big')

    # Calculate CRC16
    crc = calculate_crc16(command)

    # Append CRC
    command += crc

    return command


if __name__ == "__main__":
    cmd = create_command(
        slave_address=6,
        channel=3,
        value=True,
    )

    # add whitespace every 2 characters for readability
    cmd_hex_with_spaces = ' '.join([cmd.hex()[i:i + 2].upper() for i in range(0, len(cmd.hex()), 2)])
    print(f"Generated command: {cmd_hex_with_spaces}")
    print(f"Expected command:  06 05 00 02 FF 00 2C 4D")