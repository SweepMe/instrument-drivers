from __future__ import annotations

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
print(port.query("*IDN?"))
print(port.read())

cmd = "05 04 00 00 00 01 30 4E"
port.write(bytes.fromhex(cmd))
ret = port.read()
# print original raw return (for debugging) and the converted hex string
print('raw repr:', repr(ret))
