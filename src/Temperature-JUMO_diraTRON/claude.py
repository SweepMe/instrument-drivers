"""
Script for testing remote control of the 4 channel evaporation setup.

ModbusRTU command handling created by Claude.
"""
import time

# use serial instead of pysweepme for most basic testing
import serial

serial_port = "COM12"
BAUD_RATE   = 38400
TIMEOUT     = 10  # seconds

if __name__ == "__main__":
    port = serial.Serial(
        port=serial_port,
        baudrate=BAUD_RATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=TIMEOUT,
        xonxoff=False,
        rtscts=False,
    )

    # Commands from the manual already contain the CRC, they just need to be decoded from hex into raw bytes before sending
    raw_hex = "0103 7012 0002 7ECE"  # read actual temperature
    raw_hex_clean = raw_hex.replace(" ", "")
    cmd = bytes.fromhex(raw_hex_clean)
    print(f"Sending command: {raw_hex}, {cmd}")

    port.reset_input_buffer()
    port.write(cmd)
    time.sleep(0.1)  # wait for response

    response = port.read(32)  # read up to 32 bytes
    print(f"Received response: {response.hex().upper()}")