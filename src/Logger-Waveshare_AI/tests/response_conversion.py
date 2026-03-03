def convert_response_to_value(response: bytes) -> int:
    """Extract the 16-bit value from the Modbus response bytes."""
    word = response[3:5]
    return int.from_bytes(word, byteorder='big')


if __name__ == "__main__":
    manual_examples = {
        "05 04 02 00 60 48 D8": 96,
        "05 04 02 03 E4 48 48": 996,
        "05 04 02 09 C0 4E F0": 2496,
        "05 04 02 13 7A C4 23": 4986
    }

    for response_manual, expected_value in manual_examples.items():
        response = bytes.fromhex(response_manual.replace(" ", ""))
        value = convert_response_to_value(response)
        assert value == expected_value, f"Expected {expected_value}, got {value}"
