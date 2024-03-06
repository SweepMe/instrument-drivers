import importlib.util
from pathlib import Path
import unittest

# Import the communication interface
file_path = Path(__file__).resolve().parent.parent / "prevac_protocol.py"
spec = importlib.util.spec_from_file_location("prevac_protocol", file_path)
prevac_protocol = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prevac_protocol)

SendingDataFrame = prevac_protocol.SendingDataFrame
ReceiverDataFrame = prevac_protocol.ReceivingDataFrame

class DataFrameTest(unittest.TestCase):
    """Test the data frame class."""

    def test_message_generation(self) -> None:
        """Test the generation of the message."""
        device_address = 0xC8
        host_address = 0x01
        command = 0x0101  # example for read vacuum level
        data = [0x01] # example for read vacuum level

        dataframe = SendingDataFrame(device=device_address, host=host_address, command=command, data=data)

        self.assertEqual(dataframe.msb, 0x01, "MSB is not generated correctly.")  # noqa: PT009
        self.assertEqual(dataframe.lsb, 0x01, "LSB is not generated correctly.")  # noqa: PT009

        length = 0x01  # example for read vacuum level
        self.assertEqual(dataframe.length, length, "Length is not generated correctly.")  # noqa: PT009

        checksum = 0xCD  # example for read vacuum level
        self.assertEqual(dataframe.checksum, checksum, "Checksum is not generated correctly.")  # noqa: PT009

        expected_message = b"\xBB\x01\xC8\x01\x01\x01\x01\xCD"
        self.assertEqual(dataframe.command_to_write, expected_message, "Message is not generated correctly.")  # noqa: PT009

    def test_complicated_command(self) -> None:
        """Test the generation of the shutter control message."""
        device_address = 0xC8
        host_address = 0x01
        command = 0x8207  # example for shutter control
        data = [0x01, 0x01]  # example for shutter control

        dataframe = SendingDataFrame(device=device_address, host=host_address, command=command, data=data)

        expected_message = b"\xBB\x02\xC8\x01\x82\x07\x01\x01\x56"
        self.assertEqual(dataframe.command_to_write, expected_message, "Message is not generated correctly.") # noqa: PT009
