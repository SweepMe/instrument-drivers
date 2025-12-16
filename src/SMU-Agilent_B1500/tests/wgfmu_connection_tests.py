import time
import unittest

# add parent path to sys.path to enable import of pysweepme
import sys
from pathlib import Path
here = Path(__file__).resolve().parent
if str(here) not in sys.path:
    sys.path.insert(0, str(here))

import wgfmu_sandbox as wgfmu

# COM_PORT = "COM16"  # Needs to be adjusted
DRIVER_PATH = r"C:\~\instrument-drivers\src"  # Needs to be adjusted
DRIVER_NAME = "Logger-PREVAC_TMC13"

ADDRESS = "GPIB0::16::INSTR"
CHANNEL = 101  # wgfmu.create_channel_id(1, 1)


class ConnectionTest(unittest.TestCase):
    """Test semantic functions of the Sequencer."""

    def setUp(self) -> None:
        """Load the WGFMU DLL and establish a connection before each test.

        This uses addCleanup to guarantee that the instrument is disconnected
        even if a test fails or raises an exception. If the DLL can't be loaded
        or the connection fails we skip the test (useful for CI / developer
        machines without the hardware).
        """
        # Try to load the DLL; skip the test if it fails
        try:
            wgfmu.load_dll()
        except Exception as exc:  # pragma: no cover - hardware-specific
            self.skipTest(f"Could not load WGFMU DLL: {exc}")

        # Try to connect; skip the test if it fails
        try:
            wgfmu.open_session(ADDRESS)
        except Exception as exc:  # pragma: no cover - hardware-specific
            self.skipTest(f"Could not connect to WGFMU at {ADDRESS}: {exc}")

    def tearDown(self) -> None:
        """Clear the WGFMU state and disconnect after each test."""
        try:
            wgfmu.initialize()
        except Exception:
            pass  # Ignore errors during cleanup

        try:
            wgfmu.close_session()
        except Exception:
            pass  # Ignore errors during cleanup

    def test_connect(self) -> None:
        """Test the connection to the device and hardware numbers."""
        # If we reach this point, setUp succeeded and the instrument is connected.
        # Replace the following with real assertions (e.g. query device IDs)
        self.assertTrue(True)

    def test_error_handling(self) -> None:
        # Test error handling by forcing an error
        invalid_channel = 7
        wgfmu.connect(invalid_channel)
        error_summary = wgfmu.get_error_summary()
        assert error_summary == f"-9: Error in WGFMU_connect({invalid_channel});\n\tChannel {invalid_channel} does not exist or is not a WGFMU channel.\n"

    def test_channel_ids(self) -> None:
        """Test the readout of the channel IDs."""
        number_of_channels = wgfmu.get_channel_id_size()
        assert number_of_channels >= 1, "Number of channels should be at least 1."

        channel_ids = wgfmu.get_channel_ids()
        assert len(channel_ids) == number_of_channels, "Channel ID size mismatch."
        assert channel_ids[0] == CHANNEL, "First channel ID does not match expected value."
        assert channel_ids[1] == CHANNEL + 1, "Second channel ID does not match expected value."

    def test_waveform_generation(self) -> None:
        """Test basic waveform generation functionality."""
        pattern_name = "pulse"

        # Offline
        wgfmu.clear()
        wgfmu.create_pattern(pattern_name, 0.0)

        # Rectangular Pulse
        wgfmu.add_vector(pattern_name, 0.0001, 1.0)
        wgfmu.add_vector(pattern_name, 0.0004, 1.0)
        wgfmu.add_vector(pattern_name, 0.0001, 0)
        wgfmu.add_vector(pattern_name, 0.0004, 0)

        wgfmu.set_measure_event(
            pattern_name,
            "evt",
            0,
            1000,
            0.000001,
            0,
            "average"
        )
        wgfmu.set_measure_event(
            pattern_name,
            "evt",
            0,
            100,
            0.00001,
            0,
            "average"
        )

        # Repeat 10 times
        wgfmu.add_sequence(CHANNEL, pattern_name, 10)

        # Online - open session is done in setUp
        wgfmu.initialize()
        wgfmu.set_operation_mode(CHANNEL, wgfmu.OperationMode.FASTIV)
        wgfmu.connect(CHANNEL)
        status = wgfmu.get_channel_status(CHANNEL)
        print(status)

        assert wgfmu.is_measure_enabled(CHANNEL), "Measurement should be enabled."

        wgfmu.execute()

        # for _ in range(10):
        #     status = wgfmu.get_channel_status(CHANNEL)
        #     print(status)
        #     time.sleep(0.01)
        time.sleep(5)
        wgfmu.wait_until_completed()

        completed_points, total_points = wgfmu.get_measure_value_size(CHANNEL)
        print(f"Completed points: {completed_points}, Total points: {total_points}")
        assert completed_points > 0, "No measurement points were completed."

        wgfmu.initialize()
        # wgfmu.disconnect(CHANNEL)
