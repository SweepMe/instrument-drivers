"""
Evaporation Setup Control - ModbusRTU over RS485/USB
=====================================================
Based on: Remote Sequence ModbusRTU, Project 24-018 (IFW Dresden)

Hardware:
  - 4x Jumo diraTRON (Modbus address 1-4)
  - Waveshare Analog Input 8CH (Modbus address 5)
  - Waveshare IO 8CH (Modbus address 6)

Connection: USB -> RS485 adapter, 38400 baud, 8N1

Dependencies:
    pip install pyserial

Usage example at the bottom of this file.
"""
from __future__ import annotations

import serial
import struct
import time


# ---------------------------------------------------------------------------
# Serial port configuration (adjust COM port as needed)
# ---------------------------------------------------------------------------
SERIAL_PORT = "COM3"       # Windows: "COM3", "COM4", etc.
                            # Linux:   "/dev/ttyUSB0", "/dev/ttyACM0", etc.
BAUD_RATE   = 38400
TIMEOUT     = 10            # seconds


# ---------------------------------------------------------------------------
# Modbus device addresses (as defined in the manual)
# ---------------------------------------------------------------------------
ADDR_JUMO_CH1       = 0x01
ADDR_JUMO_CH2       = 0x02
ADDR_JUMO_CH3       = 0x03
ADDR_JUMO_CH4       = 0x04
ADDR_WAVESHARE_AI   = 0x05  # Analog Input 8CH
ADDR_WAVESHARE_IO   = 0x06  # Digital IO 8CH

# Jumo diraTRON register addresses
REG_SETPOINT        = 0x2114  # float r/w  - Setpoint value 1 (Sollwert 1)
REG_ANALOG_IN       = 0x7000  # float r/o  - Analog input (raw measurement)
REG_CTRL_SETPOINT   = 0x7010  # float r/o  - Controller setpoint value
REG_CTRL_ACTUAL     = 0x7012  # float r/o  - Controller actual value (temperature)
REG_CTRL_DEVIATION  = 0x7014  # float r/o  - Control deviation
REG_CTRL_LEVEL      = 0x7016  # float r/o  - Output level display

# Waveshare IO 8CH digital output channel addresses
DO_CHANNEL_ADDR = {
    1: 0x0000,  # Output 1 (channel 1 on/off)
    2: 0x0001,  # Output 3 (channel 3 on/off, note: not a typo, see manual)
    3: 0x0002,  # Mode 1   (Temperature vs Angstrom/s for channel 1)
    4: 0x0003,  # Mode 3
    5: 0x0004,  # Output 2 (channel 2 on/off)
    6: 0x0005,  # Output 4 (channel 4 on/off)
    7: 0x0006,  # Mode 2
    8: 0x0007,  # Mode 4
}

# Map evaporation channel number -> DO channels for output and mode
CHANNEL_DO_MAP = {
    #  channel: (output_DO, mode_DO)
    1: (1, 3),
    2: (5, 7),
    3: (2, 4),
    4: (6, 8),
}


# ---------------------------------------------------------------------------
# CRC-16 (Modbus)
# ---------------------------------------------------------------------------
def crc16_modbus(data: bytes) -> int:
    """Calculate the Modbus CRC-16 checksum for the given bytes."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


def append_crc(data: bytes) -> bytes:
    """Append the 2-byte CRC (little-endian) to a Modbus message."""
    crc = crc16_modbus(data)
    return data + struct.pack("<H", crc)


# ---------------------------------------------------------------------------
# Low-level send / receive
# ---------------------------------------------------------------------------
def open_port(port: str = SERIAL_PORT) -> serial.Serial:
    """Open and return the serial port configured for this setup."""
    ser = serial.Serial(
        port=port,
        baudrate=BAUD_RATE,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=TIMEOUT,
        xonxoff=False,
        rtscts=False,
    )
    print(f"[Serial] Opened {port} at {BAUD_RATE} baud")
    return ser


def send_raw(ser: serial.Serial, raw_hex: str, label: str = "") -> bytes:
    """
    Send a raw hex string (spaces allowed) and return the response bytes.

    These are the pre-built commands from the manual, e.g.:
        "0605 0002 FF00 2C4D"
    The function strips spaces, decodes to bytes, and sends as-is.
    Note: these strings already include the CRC.
    """
    raw_hex_clean = raw_hex.replace(" ", "")
    cmd = bytes.fromhex(raw_hex_clean)
    ser.reset_input_buffer()
    ser.write(cmd)
    if label:
        print(f"[TX] {label}: {raw_hex_clean.upper()}")
    time.sleep(0.05)                # short inter-frame gap
    response = ser.read(32)         # read up to 32 bytes
    print(f"[RX] {response.hex().upper()}")
    return response


def send_command(ser: serial.Serial, payload: bytes, label: str = "") -> bytes:
    """
    Build a complete Modbus frame: payload + CRC, send it, return raw response.
    Use this when you construct the payload yourself (without a pre-built CRC).
    """
    frame = append_crc(payload)
    ser.reset_input_buffer()
    ser.write(frame)
    if label:
        print(f"[TX] {label}: {frame.hex().upper()}")
    time.sleep(0.05)
    response = ser.read(32)
    print(f"[RX] {response.hex().upper()}")
    return response


# ---------------------------------------------------------------------------
# Modbus function code helpers
# ---------------------------------------------------------------------------
def fc05_write_single_coil(device_addr: int, coil_addr: int, value: bool) -> bytes:
    """
    FC05 - Write Single Coil.
    value=True  -> FF 00 (logic "1" / ON)
    value=False -> 00 00 (logic "0" / OFF)
    """
    coil_value = 0xFF00 if value else 0x0000
    payload = struct.pack(">B B H H", device_addr, 0x05, coil_addr, coil_value)
    return payload


def fc03_read_holding_registers(device_addr: int, start_addr: int, num_regs: int) -> bytes:
    """FC03 - Read Holding Registers (Jumo uses this for most r/o values)."""
    payload = struct.pack(">B B H H", device_addr, 0x03, start_addr, num_regs)
    return payload


def fc16_write_multiple_registers(device_addr: int, start_addr: int, data_bytes: bytes) -> bytes:
    """
    FC16 (0x10) - Write Multiple Registers.
    Used to write float setpoint values (2 registers = 4 bytes per float).
    """
    num_regs  = len(data_bytes) // 2
    byte_count = len(data_bytes)
    payload = struct.pack(
        ">B B H H B",
        device_addr, 0x10, start_addr, num_regs, byte_count
    ) + data_bytes
    return payload


# ---------------------------------------------------------------------------
# Float encoding / decoding (Jumo uses big-endian IEEE 754)
# ---------------------------------------------------------------------------
def float_to_jumo_bytes(value: float) -> bytes:
    """Encode a Python float to 4 bytes (big-endian IEEE 754) for Jumo registers."""
    return struct.pack(">f", value)


def jumo_bytes_to_float(data: bytes, offset: int = 0) -> float:
    """Decode 4 bytes (big-endian IEEE 754) from a Modbus response into a float."""
    return struct.unpack(">f", data[offset:offset + 4])[0]


def parse_fc03_response(response: bytes, num_floats: int = 1):
    """
    Parse a FC03 response for float values.
    Response structure: [addr][0x03][byte_count][data...][CRC low][CRC high]
    Each float occupies 2 registers = 4 bytes.
    Returns a list of floats.
    """
    if len(response) < 3:
        print("[ERROR] Response too short")
        return None
    byte_count = response[2]
    data = response[3: 3 + byte_count]
    results = []
    for i in range(num_floats):
        offset = i * 4
        if offset + 4 <= len(data):
            results.append(jumo_bytes_to_float(data, offset))
    return results


# ---------------------------------------------------------------------------
# High-level API
# ---------------------------------------------------------------------------

# --- Digital output control (Waveshare IO 8CH, address 0x06) ---

def set_digital_output(ser: serial.Serial, do_channel: int, on: bool):
    """
    Set a single digital output on the Waveshare IO 8CH module.
    do_channel: 1-8
    on: True = logic "1" (ON), False = logic "0" (OFF)
    """
    coil_addr = DO_CHANNEL_ADDR[do_channel]
    payload = fc05_write_single_coil(ADDR_WAVESHARE_IO, coil_addr, on)
    state = "ON" if on else "OFF"
    send_command(ser, payload, label=f"Set DO{do_channel} {state}")


def set_output_power(ser: serial.Serial, channel: int, on: bool):
    """Switch the power output of an evaporation channel ON or OFF."""
    output_do, _ = CHANNEL_DO_MAP[channel]
    state = "ON" if on else "OFF"
    print(f"[INFO] Channel {channel}: Output power -> {state}")
    set_digital_output(ser, output_do, on)


def set_control_mode_temperature(ser: serial.Serial, channel: int, temperature_mode: bool):
    """
    Switch between control modes:
      temperature_mode=True  -> Jumo diraTRON temperature PID control
      temperature_mode=False -> Angstrom/s (thickness rate) control via Inficon QCM
    """
    _, mode_do = CHANNEL_DO_MAP[channel]
    mode_name = "Temperature" if temperature_mode else "Angstrom/s"
    print(f"[INFO] Channel {channel}: Control mode -> {mode_name}")
    set_digital_output(ser, mode_do, temperature_mode)


# --- Jumo diraTRON setpoint ---

def set_temperature_setpoint(ser: serial.Serial, channel: int, temperature_celsius: float):
    """
    Write a new temperature setpoint to the Jumo diraTRON on the given channel.
    channel: 1-4
    temperature_celsius: target temperature in °C
    """
    device_addr = channel  # Jumo channel 1-4 == Modbus address 1-4
    float_bytes = float_to_jumo_bytes(temperature_celsius)
    payload = fc16_write_multiple_registers(device_addr, REG_SETPOINT, float_bytes)
    send_command(ser, payload, label=f"Jumo CH{channel}: Set setpoint -> {temperature_celsius}°C")


# --- Jumo diraTRON read values ---

def read_actual_temperature(ser: serial.Serial, channel: int) -> float | None:
    """Read the controller actual value (current temperature) from a Jumo channel."""
    device_addr = channel
    payload = fc03_read_holding_registers(device_addr, REG_CTRL_ACTUAL, 2)
    response = send_command(ser, payload, label=f"Jumo CH{channel}: Read actual temperature")
    values = parse_fc03_response(response, num_floats=1)
    if values:
        temp = values[0]
        print(f"[INFO] Channel {channel}: Actual temperature = {temp:.2f} °C")
        return temp
    return None


def read_all_controller_values(ser: serial.Serial, channel: int) -> dict | None:
    """
    Read all 4 controller values in one request (more efficient):
    - Setpoint, Actual value, Deviation, Output level
    Starting address 0x7010, 8 registers = 4 floats.
    """
    device_addr = channel
    payload = fc03_read_holding_registers(device_addr, REG_CTRL_SETPOINT, 8)
    response = send_command(ser, payload, label=f"Jumo CH{channel}: Read all controller values")
    values = parse_fc03_response(response, num_floats=4)
    if values and len(values) == 4:
        result = {
            "setpoint":   values[0],
            "actual":     values[1],
            "deviation":  values[2],
            "level":      values[3],
        }
        print(f"[INFO] Channel {channel}: {result}")
        return result
    return None


# --- Waveshare Analog Input: output current measurement ---

def read_output_current(ser: serial.Serial, channel: int) -> float | None:
    """
    Read the output current for an evaporation channel via the
    Waveshare Analog Input 8CH (address 0x05).

    The analog input measures 0-5 V. The power supply's current monitor
    outputs 2.5 V at 10 A, so the conversion factor is 20 A / 5 V = 4 A/V.

    channel: 1-4 (maps directly to AI1-AI4)
    Returns: current in Amperes
    """
    ai_register = channel - 1   # AI1 = register 0, AI2 = register 1, ...
    # FC04 - Read Input Registers (Waveshare analog uses function code 04)
    payload = struct.pack(
        ">B B H H",
        ADDR_WAVESHARE_AI, 0x04, ai_register, 1
    )
    response = send_command(ser, payload, label=f"Waveshare AI: Read channel {channel} current")

    # Response: [0x05][0x04][0x02][high byte][low byte][CRC][CRC]
    if len(response) >= 5:
        raw_counts = struct.unpack(">H", response[3:5])[0]
        voltage = raw_counts / 1000.0       # counts are in mV (0-5000)
        current = voltage * (20.0 / 5.0)   # 20A full scale at 5V
        print(f"[INFO] Channel {channel}: ADC={raw_counts} counts, "
              f"V={voltage:.3f} V, I={current:.3f} A")
        return current
    return None


# ---------------------------------------------------------------------------
# Complete sequences (mirroring Section 2 of the manual)
# ---------------------------------------------------------------------------

def run_temperature_sequence(
    ser: serial.Serial,
    channel: int,
    target_temp: float,
    duration_seconds: float = 60.0,
    poll_interval: float = 5.0,
):
    """
    Full temperature control sequence for one channel:
      1. Switch control mode to Temperature
      2. Set the target setpoint
      3. Enable output power
      4. Poll temperature + current until duration is reached
      5. Disable output power
    """
    print(f"\n{'='*60}")
    print(f" Temperature Sequence: Channel {channel}, Target {target_temp}°C")
    print(f"{'='*60}\n")

    # Step 1: Set control mode to temperature
    set_control_mode_temperature(ser, channel, temperature_mode=True)
    time.sleep(0.1)

    # Step 2: Set the setpoint
    set_temperature_setpoint(ser, channel, target_temp)
    time.sleep(0.1)

    # Step 3: Enable output
    set_output_power(ser, channel, on=True)
    time.sleep(0.1)

    # Step 4: Monitor loop
    start_time = time.time()
    try:
        while (time.time() - start_time) < duration_seconds:
            elapsed = time.time() - start_time
            print(f"\n--- t = {elapsed:.1f}s ---")
            read_all_controller_values(ser, channel)
            read_output_current(ser, channel)
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")

    # Step 5: Disable output
    print(f"\n[INFO] Sequence complete. Turning off channel {channel}.")
    set_output_power(ser, channel, on=False)


def run_thickness_rate_sequence(
    ser: serial.Serial,
    channel: int,
    duration_seconds: float = 60.0,
    poll_interval: float = 5.0,
):
    """
    Thickness rate (Angstrom/s) control sequence for one channel.
    The Inficon QCM provides the rate feedback (see Inficon manual for QCM commands).
    This script handles the evaporation controller side only.
    """
    print(f"\n{'='*60}")
    print(f" Thickness Rate Sequence: Channel {channel}")
    print(f"{'='*60}\n")

    # Step 1: Set control mode to Angstrom/s
    set_control_mode_temperature(ser, channel, temperature_mode=False)
    time.sleep(0.1)

    # Step 2: Enable output
    set_output_power(ser, channel, on=True)
    time.sleep(0.1)

    # Step 3: Monitor loop (QCM communication handled separately)
    start_time = time.time()
    try:
        while (time.time() - start_time) < duration_seconds:
            elapsed = time.time() - start_time
            print(f"\n--- t = {elapsed:.1f}s ---")
            read_actual_temperature(ser, channel)   # for safety monitoring
            read_output_current(ser, channel)
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user.")

    # Step 4: Disable output
    print(f"\n[INFO] Sequence complete. Turning off channel {channel}.")
    set_output_power(ser, channel, on=False)


# ---------------------------------------------------------------------------
# Verification helper: send the raw pre-built commands from the manual
# ---------------------------------------------------------------------------
def demo_raw_commands(ser: serial.Serial):
    """
    Send the exact raw hex commands from the manual (Section 2) for channel 1.
    Useful to verify your connection before using the high-level API.
    """
    print("\n--- Demo: Raw commands from manual (channel 1 temperature sequence) ---")

    # 1. Set mode to temperature (DO3 = 1)
    send_raw(ser, "0605 0002 FF00 2C4D", "Set DO3 ON (temperature mode)")
    time.sleep(0.1)

    # 2. Turn output ON (DO1 = 1)
    send_raw(ser, "0605 0000 FF00 8D8D", "Set DO1 ON (output ON)")
    time.sleep(0.1)

    # 3. Set setpoint to 0°C
    send_raw(ser, "0110 2114 0002 0400 0000 0067 01", "Set setpoint 0°C")
    time.sleep(0.1)

    # 4. Read actual temperature
    send_raw(ser, "0103 7012 0002 7ECE", "Read actual temperature")
    time.sleep(0.1)

    # 5. Read all 4 controller values at once
    send_raw(ser, "0103 7010 0008 5F09", "Read all controller values")
    time.sleep(0.1)

    # 6. Turn output OFF (DO1 = 0)
    send_raw(ser, "0605 0000 0000 CC7D", "Set DO1 OFF (output OFF)")


# ---------------------------------------------------------------------------
# Entry point / usage example
# ---------------------------------------------------------------------------
if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # STEP 0: Open the serial port
    #   Adjust SERIAL_PORT at the top of this file to match your system.
    #   Windows: "COM3", "COM4", ...
    #   Linux:   "/dev/ttyUSB0", "/dev/ttyACM0", ...
    # -----------------------------------------------------------------------
    ser = open_port(SERIAL_PORT)

    try:
        # -------------------------------------------------------------------
        # Option A: Send raw commands from the manual to test connectivity
        # -------------------------------------------------------------------
        demo_raw_commands(ser)

        # -------------------------------------------------------------------
        # Option B: Use the high-level API
        # -------------------------------------------------------------------

        # Example 1: Read current temperature from all 4 channels
        for ch in range(1, 5):
            read_actual_temperature(ser, ch)
            time.sleep(0.05)

        # Example 2: Run a temperature-controlled evaporation on channel 1
        #   - Target: 150°C
        #   - Duration: 5 minutes
        #   - Poll every 10 seconds
        # run_temperature_sequence(
        #     ser,
        #     channel=1,
        #     target_temp=150.0,
        #     duration_seconds=300,
        #     poll_interval=10,
        # )

        # Example 3: Read output current of all 4 channels
        for ch in range(1, 5):
            read_output_current(ser, ch)
            time.sleep(0.05)

        # Example 4: Manually set setpoint on channel 2 to 200°C
        # set_control_mode_temperature(ser, channel=2, temperature_mode=True)
        # set_temperature_setpoint(ser, channel=2, temperature_celsius=200.0)
        # set_output_power(ser, channel=2, on=True)

    finally:
        ser.close()
        print("\n[Serial] Port closed.")