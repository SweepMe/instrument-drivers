import minimalmodbus

if __name__ == "__main__":
    slave_address = 1
    register_address = 8468
    register_value = 100.0

    # Create a minimalmodbus instrument (port name is not relevant for this test)
    instrument = minimalmodbus.Instrument('COM1', slave_address)
    