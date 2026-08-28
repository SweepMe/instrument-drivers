# ruff: noqa: T201, INP001
"""Print a raw PAX1000 scan record and the interpretation the driver uses for it.

Run this once against a real PAX1000 to confirm the layout of the "SENS:DATA:LAT?" response. The
number of fields and the position of azimuth, ellipticity and DOP are known; the positions of optical
power, revolution time and misalignment are derived from the Thorlabs instrument driver and are the
part worth checking.

How to read the output:

* Azimuth and ellipticity are angles in radian, so both stay within +/- 1.6.
* DOP is a fraction between 0 and 1. Block the beam and it drops; use a clean linear polarizer and it
  approaches 1.
* Optical power is in watt and is the only value that scales with the input light level. Block the
  beam and it must fall by orders of magnitude.
* Revolution time is the duration of one waveplate turn in seconds. It follows the basic scan rate and
  does not react to the light level.
* Misalignment stays small and near zero for a well aligned beam.

If a column does not behave as its label claims, swap the corresponding IDX_ constant at the top of
main.py.

Usage:
    python probe_scan_record.py [resource]

    The resource defaults to the first USB instrument with the Thorlabs vendor id 0x1313.
"""

from __future__ import annotations

import sys
import time

import pysweepme
from pysweepme.Ports import get_resources

MEASUREMENT_MODE = 5  # full turn, 1024 points

FIELD_LABELS = [
    "int 0  scan counter",
    "int 1  timestamp",
    "int 2  ?",
    "int 3  ?",
    "int 4  ?",
    "int 5  waveplate count",
    "int 6  ?",
    "flt 7  azimuth in rad",
    "flt 8  DOP",
    "flt 9  ellipticity in rad",
    "flt 10 power in W",
    "flt 11 revolution time in s",
    "flt 12 misalignment",
]


def find_resource() -> str:
    """Return the VISA resource of the first Thorlabs USB instrument."""
    for resource in get_resources(["USBTMC"]):
        if "0x1313" in resource.lower():
            return resource

    msg = "No Thorlabs USB instrument found. Pass the VISA resource as argument instead."
    raise RuntimeError(msg)


def main() -> None:
    """Start a measurement, print a few scan records and stop the motor again."""
    resource = sys.argv[1] if len(sys.argv) > 1 else find_resource()
    print(f"Opening {resource}")

    port = pysweepme.get_port(resource, {"timeout": 5})

    try:
        port.write("*IDN?")
        print("Identification:", port.read())

        port.write(f"SENS:CALC {MEASUREMENT_MODE};:INP:ROT:STAT 1")

        print("Waiting for the waveplate motor to settle ...")
        for _ in range(100):
            port.write("INP:ROT:SETT?")
            if bool(int(port.read())):
                break
            time.sleep(0.2)

        for reading in range(3):
            port.write("SENS:DATA:LAT?")
            answer = port.read()

            print(f"\n--- reading {reading + 1} ---")
            print("raw:", answer)

            fields = answer.split(",")
            print(f"field count: {len(fields)} (the driver expects 13)")
            for index in range(max(len(FIELD_LABELS), len(fields))):
                label = FIELD_LABELS[index] if index < len(FIELD_LABELS) else f"--- {index} unexpected"
                value = fields[index] if index < len(fields) else "--- missing"
                print(f"  {label:<28} {value}")

            time.sleep(0.5)

    finally:
        port.write("SENS:CALC 0;:INP:ROT:STAT 0")
        pysweepme.close_port(port)
        print("\nMotor stopped, port closed.")


if __name__ == "__main__":
    main()
