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

    def test_send_data_frame(self) -> None:
        """Test the sending of a data frame."""
        # Test get_host
        command = 0x7FF0
        self.tmc.send_data_frame(command)

        answer = self.tmc.receive_data_frame()
        self.assertIsInstance(answer, bytes, "Answer has incorrect type.")  # noqa: PT009

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


class SetterTests(unittest.TestCase):
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

    def test_register_host(self) -> None:
        """Test the registration of the host."""
        self.tmc.register_host()

        self.assertEqual(self.tmc.host_address, chr(0x04), "Host is not assigned correctly.")  # noqa: PT009
        self.assertEqual(self.tmc.tmc.host_address, chr(0x04), "Host is not assigned correctly.")  # noqa: PT009

    def test_assign_release_master(self) -> None:
        """Test the enabling of the master mode."""
        self.tmc.register_host()
        self.tmc.enable_master()

        # TODO: Check Error Codes
        status = self.tmc.get_master_status()
        self.assertEqual(status, "11111", "Master status is incorrect.")  # noqa: PT009

        self.tmc.release_master()
        status = self.tmc.get_master_status()
        self.assertEqual(status, "11111", "Master status is incorrect.")  # noqa: PT009

    def test_reset_thickness(self) -> None:
        """Test the reset of the thickness."""
        self.tmc.reset_thickness()

        thickness = self.tmc.get_thickness()
        self.assertEqual(thickness, 0.0, "Thickness is not reset correctly.")  # noqa: PT009

    def test_set_tooling(self) -> None:
        """Test the setting of the tooling."""
        tooling = 50.0
        self.tmc.set_tooling(tooling)

        new_tooling = self.tmc.get_tooling_factor()
        self.assertEqual(new_tooling, tooling, "Tooling is not set correctly.")  # noqa: PT009

    def test_set_density(self) -> None:
        """Test the setting of the density."""
        density = 1.5
        self.tmc.set_material_density(density)

        new_density = self.tmc.get_material_density()
        self.assertEqual(new_density, density, "Density is not set correctly.")  # noqa: PT009

    def test_set_acoustic_impedance(self) -> None:
        """Test the setting of the acoustic impedance."""
        acoustic_impedance = 1.5
        self.tmc.set_acoustic_impedance(acoustic_impedance)

        new_acoustic_impedance = self.tmc.get_acoustic_impedance()
        self.assertEqual(new_acoustic_impedance, acoustic_impedance, "Acoustic impedance is not set correctly.")  # noqa: PT009

if __name__ == "__main__":
    unittest.main()
