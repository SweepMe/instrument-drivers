import pysweepme

COM_PORT = "COM19"  # Needs to be adjusted
DRIVER_PATH = r"C:\Code\instrument-drivers\src"  # Needs to be adjusted
DRIVER_NAME = "Logger-PREVAC_TM1x"


class DeviceTest:
    """Test semantic functions of the Sequencer."""

    def set_up(self) -> None:
        """Set up the test environment with local driver_path and COM port address."""
        self.device = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, COM_PORT)
        self.device.set_parameters(
            {
                "Model": "TM13",
                "Sample rate in Hz": 1,
            },
        )

    def test_get_product_number(self) -> None:
        """Test readout of product number."""
        product_number = self.device.get_product_number()
        print(product_number)

    def test_get_serial_number(self) -> None:
        """Test readout of serial number."""
        serial_number = self.device.get_serial_number()
        print(serial_number)

    def test_get_frequency(self) -> None:
        """Test readout of frequency."""
        frequency = self.device.get_frequency()
        print(frequency)

    def test_set_device_address(self) -> None:
        """Test setting the device address."""
        self.device.set_device_address(1)

    def test_set_logic_group(self) -> None:
        """Test setting the logic group."""
        self.device.set_logic_group(1)
