import struct


def calculate_crc16(data: bytes) -> bytes:
    """
    Calculate CRC16 for Modbus RTU.

    Uses CRC-16-CCITT with polynomial 0xA001.

    Args:
        data: bytes to calculate CRC for

    Returns:
        bytes: CRC16 as 2 bytes (low byte, high byte)
    """
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


def swap_bytes(data: bytes) -> bytes:
    """
    Swap bytes in pairs for word-swapped order.

    The input [0, 1, 2, 3] becomes [2, 3, 0, 1].
    """
    if len(data) != 4:
        raise ValueError("Data must be exactly 4 bytes for float32 swapping")

    swapped = bytearray(4)
    swapped[0] = data[2]  # byte 2 goes to position
    swapped[1] = data[3]  # byte 3 goes to position
    swapped[2] = data[0]  # byte 0 goes to position
    swapped[3] = data[1]  # byte 1 goes to position

    return bytes(swapped)


def generate_set_register_command(
    slave_address: int,
    register_address: int,
    register_value: float,
) -> str:
    """
    Generate a Modbus RTU command for setting a single register to a float value.

    This generates a write single register (function code 0x10) command that sets
    a register to a 32-bit IEEE 754 float value (2 registers).

    Args:
        slave_address: Modbus slave address (1-247), typically matches the channel
        register_address: Register address (e.g., 2114 for setpoint)
        register_value: Value to write as float32

    Returns:
        str: Hex string representation of the command (with spaces between bytes)
    """
    # Function code 0x10 = Write Multiple Registers
    function_code = 0x10

    # Number of registers to write (2 for float32)
    num_registers = 0x0002

    # Byte count (4 bytes for 2 registers)
    # calculate from num_registers * 2 (bytes per register)
    byte_count = num_registers * 2

    # Convert float to bytes (big-endian IEEE 754)
    float_bytes = struct.pack('>f', register_value)

    # The JUMO device uses word-swapped byte order for float values
    # Bytes come in as [0, 1, 2, 3] but need to be sent as [2, 3, 0, 1]
    swapped_float_bytes = swap_bytes(float_bytes)  # bytes([float_bytes[2], float_bytes[3], float_bytes[0], float_bytes[1]])

    # Build the command payload
    command = bytes([slave_address, function_code])
    command += register_address.to_bytes(2, byteorder='big')  # Register address 0x2114 -> 21 14
    command += num_registers.to_bytes(2, byteorder='big')
    command += byte_count.to_bytes(1, byteorder='big')
    command += swapped_float_bytes

    # Calculate CRC16
    crc = calculate_crc16(command)

    # Append CRC
    command += crc

    # Convert to hex string with spaces
    hex_string = ' '.join(f'{byte:02X}' for byte in command)
    return hex_string


if __name__ == "__main__":
    # Example usage: Set channel 1 setpoint to 100.0°C
    slave_address = 1
    register_address = 8468  # Setpoint decimal register for channel 1, hex = 21224
    register_value = 100.0

    command_hex = generate_set_register_command(slave_address, register_address, register_value)
    print(f"Generated cmd for {register_value}: {command_hex}")
    print("Expected cmd for 100.0:  01 10 21 14 00 02 04 90 00 40 05 BB C2")

    # Create reading commands
    modbus_address = 1
    read_command = 3  # function code for reading holding registers
    starting_register = 28688  # controller setpoint, other values are at 28690, 28692, 28694
    number_of_registers = 8  # read 8 registers to get all 4 float values (2 registers per float)

    command = bytes([modbus_address, read_command])
    command += starting_register.to_bytes(2, byteorder='big')
    command += number_of_registers.to_bytes(2, byteorder='big')
    command += calculate_crc16(command)
    print(command, len(command))
    print(f"Gen. Read command: {' '.join(f'{byte:02X}' for byte in command)}")
    print(f"Expected read cmd: 01 03 70 10 00 08 5F 09")

