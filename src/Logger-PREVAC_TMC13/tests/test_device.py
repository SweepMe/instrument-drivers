import unittest

import pysweepme

COM_PORT = "COM16"  # Needs to be adjusted
DRIVER_PATH = r"C:\~\instrument-drivers\src"  # Needs to be adjusted
DRIVER_NAME = "Logger-PREVAC_TMC13"

class SequencerTest(unittest.TestCase):
    """Test semantic functions of the Sequencer."""

    def setUp(self) -> None:
        """Set up the test environment with local driver_path and COM port address."""
        self.tmc = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, COM_PORT)
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
                getattr(self.tmc, parameter),
                float,
                f"{parameter} has incorrect type.",
            )

    def test_connect(self) -> None:
        """Test the connection to the device and hardware numbers."""
        self.tmc.connect()
        assert self.tmc.host_address is not None

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
        self.tmc = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, COM_PORT)
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

        self.tmc.connect()

    def test_send_data_frame(self) -> None:
        """Test the sending of a data frame."""
        # Test get_host
        command = 0x7FF0
        self.tmc.prevac_interface.send_data_frame(command)

        answer = self.tmc.prevac_interface.receive_data_frame()
        self.assertIsInstance(answer, bytes, "Answer has incorrect type.")  # noqa: PT009

    def test_measurements(self) -> None:
        """Test the reading of the measurements."""
        parameters = [
            "thickness",
            "rate",
            "tooling_factor",
            "material_density",
            "material_acoustic_impedance",
            "crystal_frequency",
            "maximum_frequency",
            "minimum_frequency",
            "pressure",
        ]
        for parameter in parameters:
            value = getattr(self.tmc, f"get_{parameter}")()

            self.assertIsInstance(value, float, f"{parameter} has incorrect type.")  # noqa: PT009

    def test_get_unit(self) -> None:
        """Test the reading of the unit."""
        parameter_dict = {
            "thickness": "A",
            "rate": "A/s",
            "pressure": "mbar",
        }

        for parameter in parameter_dict:
            unit = getattr(self.tmc, f"get_{parameter}_unit")()
            self.assertEqual(unit, parameter_dict[parameter], f"{parameter} unit is incorrect.")  # noqa: PT009

    def test_get_material_name(self) -> None:
        """Test the reading of the material name."""
        name = self.tmc.get_material_name()
        self.assertEqual(name, "SweepMeTest", "Material name is incorrect.")  # noqa: PT009


    def test_get_pressure_by_channel(self) -> None:
        """Test the reading of the pressure by channel."""
        for channel in range(1, 3):
            pressure = self.tmc.get_pressure(channel)
            self.assertIsInstance(pressure, float, "Pressure has incorrect type.")  # noqa: PT009


class SetterTests(unittest.TestCase):
    """Test data frame communication using PREVAC protocol."""

    def setUp(self) -> None:
        """Set up the test environment with local driver_path and COM port address."""
        self.tmc = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, COM_PORT)
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

        self.tmc.connect()

    def test_register_host(self) -> None:
        """Test the registration of the host."""
        self.tmc.register_host()
        self.assertEqual(self.tmc.host_address, chr(0x01), "Host is not assigned correctly.")  # noqa: PT009

    def test_assign_release_master(self) -> None:
        """Test the enabling of the master mode."""
        self.tmc.register_host()
        self.tmc.assign_master()

        # TODO: Check Error Codes
        status = self.tmc.get_master_status()
        self.assertEqual(status, "1101", "Master status is incorrect.")  # noqa: PT009

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
        old_tooling = self.tmc.get_tooling_factor()

        tooling = 72  # The same value as in the setup
        self.tmc.set_tooling_factor(tooling)

        new_tooling = self.tmc.get_tooling_factor()
        self.assertEqual(new_tooling, tooling, "Tooling is not set correctly.")  # noqa: PT009

    def test_set_density(self) -> None:
        """Test the setting of the density."""
        old_density = self.tmc.get_material_density()

        density = old_density + 0.1
        self.tmc.set_material_density(density)

        new_density = self.tmc.get_material_density()
        self.assertEqual(density, new_density, "Density is not set correctly.")  # noqa: PT009

    def test_set_acoustic_impedance(self) -> None:
        """Test the setting of the acoustic impedance."""
        old_impedance = self.tmc.get_material_acoustic_impedance()

        acoustic_impedance = old_impedance + 0.1
        self.tmc.set_material_acoustic_impedance(acoustic_impedance)

        new_acoustic_impedance = self.tmc.get_material_acoustic_impedance()
        self.assertEqual(
            new_acoustic_impedance,
            acoustic_impedance,
            "Acoustic impedance is not set correctly.",
        )

    def test_check_device_status(self) -> None:
        """Test the reading of the error status."""
        self.tmc.check_device_status()

    def test_check_error_status(self) -> None:
        """Test the reading of the error status."""
        self.tmc.prevac_interface.check_error_status()

if __name__ == "__main__":
    unittest.main()
