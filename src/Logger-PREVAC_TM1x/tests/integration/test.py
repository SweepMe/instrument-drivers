import pysweepme

COM_PORT = "COM3"  # Needs to be adjusted
DRIVER_PATH = r"C:\Code\instrument-drivers\src"  # Needs to be adjusted
DRIVER_NAME = "Logger-PREVAC_TM1x"


def test_get_product_number() -> None:
    """Test readout of product number."""
    device = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, COM_PORT)
    product_number = device.get_product_number()
    your_product_number = "021321000003302"  # Needs to be adjusted
    assert product_number == your_product_number


def test_get_serial_number() -> None:
    """Test readout of serial number."""
    device = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, COM_PORT)
    serial_number = device.get_serial_number()
    your_serial_number = "0000000010275"  # Needs to be adjusted
    assert serial_number == your_serial_number


def test_get_frequency() -> None:
    """Test readout of frequency."""
    device = pysweepme.get_driver(DRIVER_NAME, DRIVER_PATH, COM_PORT)
    frequency = device.get_frequency()
    print(frequency)
    assert frequency > 0
