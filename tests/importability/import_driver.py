"""Test if an instrument driver can be imported.

Usage:
    From the root of the repository, call

    `python ./tests/importability/import_driver.py <driver-name>`
"""

import json
import logging
import sys
import traceback
from configparser import ConfigParser
from pathlib import Path

import pysweepme

logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")


def is_compatible(driver_name: str) -> bool:
    """Check if the driver compatibility information matches the currently running python version.

    Args:
        driver_name: Name (folder) of the driver to import.
    """
    limit_for_32_bit = 0x100000000
    version = sys.version_info
    python_version = f"{version.major}.{version.minor}"
    bitness = "64" if sys.maxsize > limit_for_32_bit else "32"
    compatibility_flags = {
        "any",
        f"any-{bitness}",
        f"{python_version}-any",
        f"{python_version}-{bitness}",
    }
    config = ConfigParser()
    config.read(Path("src") / driver_name / "info.ini")
    # get the architecture from the run section, and if it does not exist from the info section. This is
    # the same order the server checks in uploaded drivers.
    # If no architecture is found at all, use the default "any" (as a quoted string)
    architecture_str = json.loads(
        config.get("run", "architecture", fallback=config.get("info", "architecture", fallback='"any"')),
    )
    architecture = {a.strip() for a in architecture_str.split(",")}
    # compatibility is given if the two sets have non-empty intersection
    if architecture & compatibility_flags:
        return True
    return False


# Driver name and reason for skipping
SKIPPED_DRIVERS = {
    "Logger-MCC_DAQ": "Driver requires installed manufacturer software",
    "Switch-FTDI_FTD2xx": "Driver requires installed manufacturer software",
    "Logger-ArtifexEngineering_OPM150": "Driver requires installed manufacturer software",
    "Logger-ArtifexEngineering_TZA500": "Driver requires installed manufacturer software",
    "Switch-AdvancedMicrofluidics_LSPone-Series": "Driver requires installed manufacturer software",
}


def should_skip_driver(driver_name: str) -> bool:
    """Check if the driver can be tested on a virtual machine.

    Args:
        driver_name: Name (folder) of the driver to import.
    """
    if SKIPPED_DRIVERS.get(driver_name) is not None:
        logging.debug(
            f"Skipped importing {driver_name}. Reason: {SKIPPED_DRIVERS[driver_name]}",
        )
        return True

    return False


def import_driver(driver_name: str) -> None:
    """Let pysweepme import a driver from the src directory.

    Args:
        driver_name: Name (folder) of the driver to import.
    """
    # some devices already get an initialized (not opened) port from the PortManager and require a port string.
    # There is no universal port string that works for all devices, so we try a couple until we got something
    # that works.
    # We are using "" (no port), "USB" (gets initialized without any side-effects), and "0" (for Indexes, e.g. Webcam)
    port_strings = ["", "USB", "0"]
    exceptions = []
    for port_string in port_strings:
        try:
            driver_instance = pysweepme.get_driver(
                driver_name,
                folder="src",
                port_string=port_string,
            )
            break
        except Exception:
            exceptions.append((port_string, sys.exc_info()))
    else:
        for port_string, exc in exceptions:
            msg = f'Failed to import {driver_name} with port string "{port_string}".'
            logging.error(msg)
            traceback.print_exception(*exc)
        msg = f"Driver {driver_name} could not be imported with any of the tested port_strings."
        raise Exception(msg)

    assert driver_name == driver_instance._latest_parameters["Device"]

    logging.debug(f"Imported {driver_name}.")


try:
    driver_name = sys.argv[1]
except IndexError as e:
    msg = "This script must be called with the driver name as first argument."
    raise IndexError(msg) from e

if not is_compatible(driver_name):
    logging.debug(
        f"Skipped importing {driver_name} because it is not meant to be compatible with this python version.",
    )
elif should_skip_driver(driver_name):
    pass
else:
    import_driver(driver_name)
