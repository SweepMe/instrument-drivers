""" base class labjack"""

import time
from collections import Counter
from typing import List

import ljm_constants_wrapped as ljm_constants
from labjack import ljm

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug

DEBUG = False


def gen_bit_mask(masked_channels: list, num_channels: int, invert_mask=False) -> int:
    """ generate a bit mask for a list of channels
        mask is right to left: 0b00001 1 for channel 0, 0 for channels 1-4
    Inputs:
        masked_channels : list of the channels numbers that will be masked
        num_channels : total number of channels
        invert_mask: if False (True) masked channels set to 1 (0) and all others to 0 (1)
    Returns:
        a binary mask as int (right most bit is address/channel 0)
    Example:
        (masked_channels = [4,5], num_channels = 12, invert_mask = True) --> 0b111111001111=4047
        (masked_channels = [0,5], num_channels = 7, invert_mask = True) --> 0b1011110"""

    # [::-1] invert list order for binary
    if not invert_mask:
        states = ["1" if i in masked_channels else "0" for i in range(num_channels)][::-1]
    else:
        states = ["0" if i in masked_channels else "1" for i in range(num_channels)][::-1]

    states_str = "".join(states)
    return int(states_str, 2)


class LabjackBaseClass(EmptyDevice):
    """ class to control the labjack T series"""

    def __init__(self):
        """Open device and get infos"""

        super().__init__()
        self.serial_number = None
        self.dev_type = None
        self.infos = None
        self.output_pin_names = []
        self.counter_pins = []
        self.parameters = {}
        self.handle = None

    def find_ports(self, dev_type="ANY"):
        types = ljm_constants.DEVICE_TYPES_TEXT
        if dev_type in types:
            dev_type = types[dev_type]
        elif dev_type not in list(types.values()):
            raise ValueError(f"Invalid labjack device type {dev_type}.")

        any_cnxn = "LJM_ctANY"
        num_found, dev_types, cnxn_types, serial_nums, ip_addresses = ljm.listAllS(
            dev_type, any_cnxn)
        dev_types = [ljm_constants.DEVICE_TYPES_CODES[dt] for dt in dev_types]

        cnxn_types = [ljm_constants.CONNECTION_TYPES_CODES[c_type] for c_type in cnxn_types]
        cnxn_types = ",".join(set(cnxn_types))
        # print(f"Found {num_found} labjack device(s) over {cnxn_types}")

        ports = [f"{dev_types[i]}:SN{ser_num}" for i, ser_num in enumerate(serial_nums)]

        if len(ports) > 0:
            return ports
        else:
            return ["No devices found!"]

    def connect(self) -> int:
        """ open device and return dll handle"""

        serial_number = self.parameters["serial number"]
        if not serial_number:
            raise ValueError("Labjack missing SN, please call find ports")

        if serial_number in self.device_communication:
            self.handle = self.device_communication[serial_number]
        else:
            self.handle = ljm.openS(deviceType="ANY",
                                    connectionType="ANY",
                                    identifier=serial_number)
            self.device_communication.update({serial_number: self.handle})

        self.infos = self.get_infos()
        self.dev_type = self.infos["dev_type"]
        self.serial_number = self.infos["SN"]

    def disconnect(self):
        """ release connection, flush connected dev list """

        if self.serial_number in self.device_communication:
            self.device_communication.pop(self.serial_number)
            try:
                ljm.close(self.handle)
            except ljm.ljm.LJMError:
                debug("Unable to close Labjack device because it is already closed")

        self.parameters = {}
        self.handle = None
        self.infos = None
        self.dev_type = None

    def get_infos(self):
        """ get infos"""

        dev_type, cnxn_type, serial_num, ip_address, port, _ = ljm.getHandleInfo(self.handle)
        names = ["HARDWARE_VERSION", "FIRMWARE_VERSION", "BOOTLOADER_VERSION"]
        results = ljm.eReadNames(self.handle, len(names), names)

        # parse returns
        dev_type = ljm_constants.DEVICE_TYPES_CODES[dev_type]
        cnxn_type = ljm_constants.CONNECTION_TYPES_CODES[cnxn_type]
        address = port if cnxn_type.find("USB") >= 0 else ip_address

        infos = {"dev_type": dev_type, "SN": serial_num, "CNXN": cnxn_type, "address": address}
        infos.update(dict(zip(names, results)))

        if serial_num not in self.device_communication:
            print(f"{dev_type} with SN{serial_num} connected over {cnxn_type} at {address}")

        return infos

    def write_pin(self, pin_name: str, value, debug=DEBUG):
        """ write a modbus register"""
        if pin_name not in ljm_constants.ALL_PIN_NAMES[self.dev_type]:
            raise ValueError(f"Invalid pin name {pin_name}")

        # address, allowed_type = ljm.nameToAddress(pin_name)
        ljm.eWriteName(handle=self.handle, name=pin_name, value=value)

        if debug:
            print(f"Set pin {pin_name} to {value}")

    def read_pin(self, pin_name: str, auto_switch_to_input=False, debug=DEBUG):
        """ read a modbus register
            WARNING: READING A DIGITAL INPUT WILL SET IT TO INPUT
        Inputs:
            pin_name: str eg 'DIO4'
            auto_switch_to_input: if pin is in OUTPUT switch to INPUT & read, otherwise skip
            "debug": print pin_name and return val """

        if pin_name in self.output_pin_names and not auto_switch_to_input:
            debug_msg = f"Skipped {pin_name} read as it was output"
            value = None
        else:
            value = ljm.eReadName(self.handle, pin_name)
            debug_msg = f"{pin_name} value out", value

        if debug:
            print(debug_msg)

        return float(value)

    def read_pins(self, pin_names: list, auto_switch_to_input=False):
        """ read several modbus registers to get the pin values
            WARNING: READING A DIGITAL INPUT WILL SET IT TO INPUT
        Inputs:
            pin_names: list of pin names eg ['AIN0', "AIN2"]
            auto_switch_to_input: if pin is in OUTPUT switch to INPUT & read, otherwise skip
            "debug": print pin_name and return val """

        if not pin_names:
            return []

        if not auto_switch_to_input:
            pins_filtered = [
                pin_name for pin_name in pin_names if pin_name not in self.output_pin_names
            ]
            skipped = [pin_name for pin_name in pin_names if pin_name not in pins_filtered]
            print(f"Skipped {skipped} read as it was output")
        else:
            pins_filtered = pin_names

        values = ljm.eReadNames(self.handle, len(pin_names), pin_names)
        return np.array([float(val) for val in values])

    def set_digital_IO(self, pins_names_inputs, pin_names_high, pin_names_low):
        """ A method to set the digital pin states to Input, High or Low.
            Input pin names are validated and cannot appear multiple times
        Inputs:
            pins_names_inputs: list of pin names to be set as DIG input eg ['FIO3', 'DIO8']
            pins_names_high: list of pin names to be set to OUTP HIGH eg ['FIO3', 'DIO8']
            pins_names_low: list of pin names to be set to OUTP LOW eg ['FIO3', 'DIO8']
        """
        # validate
        settable_pins = ljm_constants.DIO_PINS[self.dev_type]
        settable_pin_names = list(settable_pins.keys())
        pins_to_set = pins_names_inputs + pin_names_high + pin_names_low
        if not pins_to_set:
            return

        input_ok = all([(pin in settable_pin_names) for pin in pins_to_set])
        if not input_ok:
            err = f"Not all pins in {pins_to_set} are DIO pins. Valid: {list(settable_pins.keys())}"
            raise ValueError(err)

        # convert pin names to indices
        inputs = [settable_pins[name] for name in pins_names_inputs]
        highs = [settable_pins[name] for name in pin_names_high]
        lows = [settable_pins[name] for name in pin_names_low]
        outputs = highs + lows

        # check pins were not specified twice under different names (DIOX <--> FIOY)
        conflicts = False if len(inputs + outputs) == len(set(inputs + outputs)) else True
        if conflicts:
            non_unique_names = [k for k, count in Counter(pins_to_set).items() if count > 1]
            if non_unique_names:
                raise ValueError(f"Pins {pins_to_set} have several states requested")
            else:
                non_unique_pins = [k for k, count in Counter(inputs + outputs).items() if count > 1]
                raise ValueError(
                    f"Pin {non_unique_pins} have several states requested under different "
                    "aliases (eg DIOx<-->EIOy")

        # If there are flex pins need to set them to DIGITAL in case they were analogue
        if self.dev_type == "T4":
            all_pin_names = pin_names_high + pin_names_low + pin_names_low
            flex = [
                pin_name for pin_name in all_pin_names if pin_name in ljm_constants.FLEX_PINS_T4
            ]
            if flex:
                self.set_flex_pins_to_analog(flex, set_digital=True)

        # set DIO to IN/OUT
        # first block dio commands to all channels except inputs/outputs (in/out = 1, others =0)
        ignore_bit_mask = gen_bit_mask(inputs + outputs, len(settable_pins), invert_mask=True)
        ljm.eWriteName(self.handle, "DIO_INHIBIT", ignore_bit_mask)
        # now set DIO_direction (0 = in/1=out) for non-blocked channels (those we want to set)
        set_input_mask = gen_bit_mask(inputs, max(inputs + outputs) + 1, invert_mask=True)
        ljm.eWriteName(self.handle, "DIO_DIRECTION", set_input_mask)  # input =0, output = 1

        # set OUTPUT states
        for pin_name in pin_names_high:
            self.write_pin(pin_name=pin_name, value=1)
        for pin_name in pin_names_low:
            self.write_pin(pin_name=pin_name, value=0)

        self.output_pin_names = outputs

    def read_DIO_states(self):
        """ get all DIO states"""
        DIO_pin_dict = ljm_constants.DIO_PINS[self.dev_type]
        num_pins = len(DIO_pin_dict)
        IO_states = ljm.eReadName(self.handle, "DIO_DIRECTION")  # binary
        # format as binary then pad
        IO_states = format(int(IO_states), "b")[::-1]
        IO_states += "0" * (num_pins - len(IO_states))

        HILO = ljm.eReadName(self.handle, "DIO_STATE")
        HILO = format(int(HILO), "b")[::-1]
        HILO += "0" * (num_pins - len(HILO))

        IO_states = ["IN" if int(dir) == 0 else int(HILO[i]) for i, dir in enumerate(IO_states)]

        IO_states_dict = {pin_name: IO_states[num] for pin_name, num in DIO_pin_dict.items()}

        return IO_states_dict

    def set_pins_to_hs_counter(self, pin_names: List[str], reset=True, override_clock=True):
        """ method to set the counter pins to counter mode. See
        https://labjack.com/pages/support?doc=/datasheets/t-series-datasheet/132-dio-extended-features-t-series-datasheet/
        for valid pin names (model dependent)
        Inputs:
            pin_names: list of DIOx names to set to counter mode. CIO not accepted
            reset: reset counts (bool)
            override_clock: disable cloks 0 and 1 or 2 as needed to make sure no conflicts arise"""

        if not pin_names or pin_names == [""]:
            return

        allowed_pins = ljm_constants.COUNTER_PINS[self.dev_type]
        input_ok = all([(pin in allowed_pins) for pin in pin_names])
        if not input_ok:
            err = f"Not all pins in {pin_names} are DIO pins. Valid: {allowed_pins}"
            raise ValueError(err)

        # probably need to enable as input
        self.set_digital_IO(pins_names_inputs=pin_names, pin_names_high=[], pin_names_low=[])

        # now set counter: sequence: disable EF mode, set EF mode, enable EF mode
        hs_couter_index = 7
        clock_conflict_pins = ljm_constants.CLOCK_DISABLE_FOR_COUNTER[self.dev_type]
        set_commands, values = [], []
        for pin in pin_names:
            # some pins require c lock disable for HS mode
            if pin in clock_conflict_pins and override_clock:
                c0_enabled, cX_enabled = self.read_names(
                    ["DIO_EF_CLOCK0_ENABLE", clock_conflict_pins[pin]])
                if c0_enabled:
                    set_commands += ["DIO_EF_CLOCK0_ENABLE"]
                    values += [0]
                    print("Warning: clock 0 disabled to avoid conflict")
                if cX_enabled:
                    set_commands += [clock_conflict_pins[pin]]
                    values += [0]
                    print(f"Warning: clock disabled for {pin}")
            set_commands += [f"{pin}_EF_ENABLE", f"{pin}_EF_INDEX", f"{pin}_EF_ENABLE"]
            values += [0, hs_couter_index, 1]
        ljm.eWriteNames(self.handle, len(set_commands), set_commands, values)

        if reset:
            reset_command = []
            for pin in pin_names:
                reset_command += [f"{pin}_EF_READ_A_AND_RESET"]

            _ = ljm.eReadNames(self.handle, len(reset_command), reset_command)

        self.counter_pins = pin_names

    def set_adc_extended_function(self, adc_channel_names, index):
        """ set the ADC analog in extended functions roles"""
        commands = []
        for ch_name in adc_channel_names:
            commands += [f"{ch_name}_EF_INDEX"]
        values = [index] * len(commands)
        ljm.eWriteNames(self.handle, len(commands), commands, values)

    def read_counter_pins(self, count_time, bus_correction=0) -> list:
        """ method to get values from the high speed counter pins
        There are two options: read/reset before (can miss 30us) or read before after and
        then subtract. This is the one we take
        INPUTS:
            count_time in sec (sleep between read commands)
            bus_correction: any correction to the bus time """

        read_commands = []
        for pin in self.counter_pins:
            read_commands += [f"{pin}_EF_READ_A"]

        start_values = ljm.eReadNames(self.handle, len(read_commands), read_commands)
        time.sleep(count_time - bus_correction)
        end_values = ljm.eReadNames(self.handle, len(read_commands), read_commands)

        return np.array(
            [int(end_values[i]) - int(start_value) for i, start_value in enumerate(start_values)])

    def set_flex_pins_to_analog(self, pin_names: List[str], set_digital=False):
        """ A method for the T4 to switch the flexible pins (FIOx and EIO0-4) to ANALOG or DIGITAL
            Inputs:
                pin_names: list of pin names (either DIO or FIO/EIO)
                set_digital (bool): set pins to digital instead of analog """

        # validate
        if self.dev_type != "T4":
            print("set_flex_pin_mode only applicable to T4 devices")
            return

        settable_pins = ljm_constants.FLEX_PINS_T4
        input_ok = all([(pin in settable_pins) for pin in pin_names])

        if not input_ok:
            err = f"Not all pins in {pin_names} are flexible (valid: {list(settable_pins.keys())})"
            raise ValueError(err)

        # translate to pin DIO numbers
        pins = [settable_pins[name] for name in pin_names]

        # make a bit mask for channels that will not be addressed
        ignore_bit_mask = gen_bit_mask(pins, num_channels=20, invert_mask=True)
        invert = True if set_digital else False
        set_analog_mask = gen_bit_mask(pins, max(pins) + 1, invert_mask=invert)

        # command will only be sent to DIO# with 0 in bit mask
        ljm.eWriteName(self.handle, "DIO_INHIBIT", ignore_bit_mask)
        ljm.eWriteName(self.handle, "DIO_ANALOG_ENABLE", set_analog_mask)

    def write_names(self, commands: list, values: list):
        """wrap the ljm command for child classes + convenience"""
        assert len(commands) == len(values), "incompatible command and value lengths"
        ljm.eWriteNames(self.handle, len(commands), commands, values)

    def read_names(self, names_list: list):

        values = ljm.eReadNames(self.handle, len(names_list), names_list)
        return np.array(values).astype(float)

    def get_device_status(self):

        if not self.handle:
            return "Labjack device unconnected and no information available."
        else:
            return (f"Connected Labjack device {self.dev_type} with SN{self.infos['SN']} "
                    f"connected over {self.infos['CNXN']} at {self.infos['address']}")


if __name__ == "__main__":

    devices = LabjackBaseClass().find_ports()
    print(devices)
    sn = int(devices[0].split(":SN")[-1])

    labjack = LabjackBaseClass()
    labjack.parameters["serial number"] = sn
    labjack.connect()
    labjack.initialize()
    print(labjack)
    print(labjack.infos)

    labjack.write_pin("DAC0", 2.1)
    # labjack.write_pin("DIO4", 0)

    # labjack.set_flex_pins_to_analog(["FIO7", "FIO6"])

    # pins_high = ["EIO0"]
    # pins_low = ["EIO1", "CIO1", "FIO5"]
    # pins_in = ["EIO2", "FIO4"]
    # labjack.set_digital_IO(pins_in, pins_high, pins_low)

    # fio4_state = labjack.read_pin("FIO4")
    # print("PIN FIO04 state:", fio4_state)

    # # test reading an output
    # cio1_state = labjack.read_pin("CIO1")
    # print(cio1_state)

    labjack.set_pins_to_hs_counter(["DIO17", "DIO18"])
    counts = labjack.read_counter_pins(2)
    EF_states = ljm.eReadNames(labjack.handle, 2, ["DIO17_EF_ENABLE", "DIO18_EF_ENABLE"])
    print("counter states: ", EF_states)
    print("Counts: DIO17, DIO18 ", counts)

    labjack.disconnect()

    print("=) done =)")
