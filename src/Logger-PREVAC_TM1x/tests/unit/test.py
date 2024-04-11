import pysweepme

COM_PORT = "COM3"  # Needs to be adjusted
DRIVER_PATH = r"C:\Code\instrument-drivers\src"  # Needs to be adjusted
DRIVER_NAME = "Logger-PREVAC_TM1x"

def test_checksum():
    device = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, COM_PORT)
    example_message = [0x04, 0xFF, 0x47, 0xFF, 0x01, 0x58, *[0, 0, 0], 0xC8]
    checksum = device.calculate_checksum(example_message)
    example_checksum = 0x6A
    assert checksum == example_checksum


def test_sauerbreys_equation():
    device = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, COM_PORT)

    initial_frequency = 5E6
    frequency = initial_frequency - 5.7
    density_material = 1  # Al
    impedance_ratio = 1.0

    thickness = device.calculate_thickness(frequency, initial_frequency, density_material, impedance_ratio)
    expected_thickness = 1.0
    assert thickness - expected_thickness < 1E-2