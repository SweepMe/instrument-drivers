import unittest

import pysweepme


class SequencerTest(unittest.TestCase):
    """Test semantic functions of the Sequencer."""

    def setUp(self) -> None:
        """Set up the test environment with local driver_path and COM port address."""
        driver_name = "Logger-PREVAC_TMC13"
        driver_path = r"C:\Code\instrument-drivers\src"  # Needs to be adjusted
        port_string = "COM13"  # Needs to be adjusted
        self.tmc = pysweepme.get_driver(driver_name, driver_path, port_string)
        self.tmc.set_parameters(
            {
                "Channel": "1",  # Currently not used
                "Reset thickness": False,
                "Set tooling": False,
                "Tooling in %": "100.0",
                "Set density": False,
                "Density in g/cm^3": "1.3",
                "Set acoustic impedance": False,
                "Acoustic impedance in 1e5 g/cm²/s": 1.0,
            },
        )

    def test_gui_parameter(self) -> None:
        """Test the conversion of input GUI parameter."""
        self.assertEqual(self.tmc.channel, "\x01", "Channel is not converted correctly.")  # noqa: PT009

        bool_parameters = [
            "should_reset_thickness",
            "should_set_tooling",
            "should_set_density",
            "should_set_acoustic_impedance",
        ]
        for parameter in bool_parameters:
            self.assertIsInstance(getattr(self.tmc, parameter), bool, f"{parameter} has incorrect type.")  # noqa: PT009

        float_parameters = ["tooling_factor", "density", "acoustic_impedance"]
        for parameter in float_parameters:
            self.assertIsInstance(
                getattr(self.tmc, parameter), float, f"{parameter} has incorrect type.",
            )

    def test_connect(self) -> None:
        """Test the connection to the device and hardware numbers."""
        self.tmc.connect()
        # TODO: Set host_address
        print(self.tmc.host_address)
        assert self.host_address is not None

    def test_initialize(self) -> None:
        """Test the initialization of the device."""
        self.tmc.connect()
        self.tmc.initialize()
        assert self.tmc.frequency_min >= 0.0
        assert self.tmc.frequency_max >= 0.0

    def test_configure(self) -> None:
        """Test the configuration of the device."""
        self.tmc.connect()
        self.tmc.initialize()
        self.tmc.configure()

    def test_call(self) -> None:
        """Test the call of the device."""
        self.tmc.connect()
        self.tmc.initialize()
        self.tmc.configure()
        values = self.tmc.call()
        print(values)


class GetterTests(unittest.TestCase):
    """Test data frame communication using PREVAC protocol."""

    def setUp(self) -> None:
        """Set up the test environment with local driver_path and COM port address."""
        driver_name = "Logger-PREVAC_TMC13"
        driver_path = r"C:\Code\instrument-drivers\src"  # Needs to be adjusted
        port_string = "COM13"  # Needs to be adjusted
        self.tmc = pysweepme.get_driver(driver_name, driver_path, port_string)
        self.tmc.set_parameters(
            {
                "Channel": "1",
                "Reset thickness": False,
                "Set tooling": False,
                "Tooling in %": "100.0",
                "Set density": False,
                "Density in g/cm^3": "1.3",
                "Set acoustic impedance": False,
                "Acoustic impedance in 1e5 g/cm²/s": 1.0,
            },
        )

    def test_checksum(self) -> None:
        """Test the calculation of the checksum."""
        message = "\x01\xC8\x01\x01\x01\x01"
        checksum = self.tmc.generate_checksum(message)
        checksum_bytes = checksum.encode("latin1")

        assert checksum_bytes == b"\xcd", "Checksum is not calculated correctly."

    def test_send_data_frame(self) -> None:
        """Test the sending of a data frame."""
        # Test get_host
        command = 0x7FF0
        self.tmc.send_data_frame(command)

        answer = self.tmc.receive_data_frame()
        self.assertIsInstance(answer, bytes, "Answer has incorrect type.")  # noqa: PT009

    def test_device_numbers(self) -> None:
        """Test the reading of the product number."""
        product_number = self.tmc.get_product_number()
        self.assertEqual(len(product_number), 15, "Product number has incorrect length.")  # noqa: PT009
        # print(product_number, len(product_number), type(product_number))

        serial_number = self.tmc.get_serial_number()
        self.assertEqual(len(serial_number), 13, "Serial number has incorrect length.")  # noqa: PT009
        # print(serial_number, len(serial_number), type(serial_number))

        device_version = self.tmc.get_device_version()
        self.assertEqual(len(device_version), 15, "Device version has incorrect length.")  # noqa: PT009
        # print(device_version, len(device_version), type(device_version))

    # TODO: Remove the other tests and only test the measurements
    def test_measurements(self) -> None:
        """Test the reading of the measurements."""
        parameters = [
            "thickness",
            "rate",
            "tooling_factor",
            # "material_density",
            "crystal_frequency",
            "maximum_frequency",
            "minimum_frequency",
            "pressure",
        ]
        for parameter in parameters:
            value = getattr(self.tmc, f"get_{parameter}")()

            self.assertIsInstance(value, float, f"{parameter} has incorrect type.")  # noqa: PT009
            self.assertGreaterEqual(value, 0, f"{parameter} is negative.")  # noqa: PT009

    def test_get_thickness(self) -> None:
        """Test the reading of the thickness."""
        thickness = self.tmc.get_thickness()
        print(thickness)

        self.assertIsInstance(thickness, float, "thickness has incorrect type.")  # noqa: PT009
        self.assertGreaterEqual(thickness, 0, "thickness is negative.")  # noqa: PT009

    def test_get_rate(self) -> None:
        """Test the reading of the rate."""
        rate = self.tmc.get_rate()

        self.assertIsInstance(rate, float, "Rate has incorrect type.")  # noqa: PT009
        self.assertGreaterEqual(rate, 0, "Rate is negative.")  # noqa: PT009

    def test_get_tooling_factor(self) -> None:
        """Test the reading of the tooling factor."""
        tooling_factor = self.tmc.get_tooling_factor()
        print(tooling_factor)

        assert isinstance(tooling_factor, float), "Tooling factor has incorrect type."
        assert tooling_factor >= 0.0, "Tooling factor is negative."

    def test_get_density(self) -> None:
        """Test the reading of the density."""
        density = self.tmc.get_material_density()
        print(density)

        assert isinstance(density, float), "Density has incorrect type."
        assert density >= 0.0, "Density is negative."

    def test_get_pressure(self) -> None:
        """Test the reading of the pressure."""
        pressure = self.tmc.get_pressure()
        print(pressure)

    def test_get_pressure_unit(self) -> None:
        """Test the reading of the pressure unit."""
        pressure_unit = self.tmc.get_pressure_unit()
        print(pressure_unit)

    def test_get_unit(self) -> None:
        """Test the reading of the unit."""
        parameter_dict = {
            "thickness" : "A",
            "rate": "A/s",
            "pressure": "mbar",
        }

        for parameter in parameter_dict:
            unit = getattr(self.tmc, f"get_{parameter}_unit")()
            self.assertEqual(unit, parameter_dict[parameter], f"{parameter} unit is incorrect.")  # noqa: PT009


if __name__ == "__main__":
    unittest.main()
