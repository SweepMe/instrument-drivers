"""Move a Thorlabs LTS stage with the SweepMe! driver outside of SweepMe! to check the driver with the hardware.

Close Kinesis before running this script. Run it with a Python environment that contains pysweepme and pythonnet and
has the same bitness as the installed Kinesis.
"""

# ruff: noqa: T201

from __future__ import annotations

from pathlib import Path
from typing import Any

import pysweepme

SERIAL_NUMBER = ""  # serial number of the stage as listed by Kinesis, empty to use the first listed device
PARAMETERS = {
    "SweepMode": "Absolute position in mm",
    "Velocity in mm/s": 10.0,
    "Home at start": True,
    "Home velocity in mm/s": 5.0,
}
POSITIONS = [10.0, 20.0, 10.0]  # in mm, absolute or relative positions depending on the SweepMode

DRIVERS_FOLDER = Path(__file__).resolve().parents[3]  # folder that contains the driver folder Switch-Thorlabs_LTS


def run_check(serial_number: str, parameters: dict[str, Any], positions: list[float]) -> None:
    """Configure the stage like in a SweepMe! run, move it to each position and print the position read back."""
    driver = pysweepme.get_driver("Switch-Thorlabs_LTS", folder=str(DRIVERS_FOLDER))

    devices = driver.list_devices()
    print(f"Devices found by Kinesis: {devices}")
    if not serial_number:
        if not devices:
            msg = "Kinesis does not list any device."
            raise RuntimeError(msg)
        serial_number = devices[0]

    driver.set_parameters({"Port": serial_number, **parameters})

    driver.connect()
    try:
        driver.initialize()
        print(f"Travel range: {driver.position_min} mm to {driver.position_max} mm")
        print(f"Maximum velocity: {driver.velocity_limit} mm/s")

        driver.configure()
        print(f"Position after configure: {driver.get_position_mm()} mm")

        # Same order as the SweepMe! sequencer, which calls apply() and reach() only if the sweep value changed
        previous_position = None
        for position in positions:
            driver.value = position
            driver.start()
            if position != previous_position:
                driver.apply()
                driver.reach()
            driver.adapt()
            print(f"Sweep value {position} mm -> position {driver.call()[0]} mm")
            previous_position = position

    finally:
        driver.poweroff()
        driver.disconnect()


if __name__ == "__main__":
    run_check(
        serial_number=SERIAL_NUMBER,
        parameters=PARAMETERS,
        positions=POSITIONS,
    )
