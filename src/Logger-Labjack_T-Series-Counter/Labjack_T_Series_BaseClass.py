""" base class labjack"""

import time
from collections import Counter
from typing import Annotated, List, Literal

import ljm_constants_wrapped as ljm_constants
from labjack import ljm

import numpy as np
from pysweepme import Label, Range, Selector, Unit, command
from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug

DEBUG = False

# What the communication commands take and answer (checked by @command on every call). Pin names are model dependent
# (T4, T7, T8), so they stay text and the commands check them against the connected model. A pin addresses a line of
# the device (a selector); several names reach one line (DIO4 is FIO4, and on the T4 also AIN4), which pin_overlaps
# answers for the model connected.
Pin = Annotated[str, Selector(overlaps="pin_overlaps")]
Volts = Annotated[float, Unit("V")]
Celsius = Annotated[float, Unit("°C")]
Hertz = Annotated[float, Unit("Hz")]
DacChannel = Annotated[int, Selector(), Range(0, 1)]
DacVoltage = Annotated[Volts, Range(0.0, 5.0), Label("DAC voltage")]
DigitalDirection = Literal["IN", "OUT"]

# LJM fills scans that were lost after a device buffer overflow (stream auto-recovery) with this value.
# The stream commands replace it by NaN, so that it cannot be mistaken for a measured value.
LJM_DUMMY_VALUE = -9999.0


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

    # state of the stream commands, set on the instance when a stream is started
    _stream_running = False
    _stream_pins = ()
    _scan_rate = None

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

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
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

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
    def write_pin(self, pin_name: str, value, debug=DEBUG):
        """ write a modbus register"""
        if pin_name not in ljm_constants.ALL_PIN_NAMES[self.dev_type]:
            raise ValueError(f"Invalid pin name {pin_name}")

        # address, allowed_type = ljm.nameToAddress(pin_name)
        ljm.eWriteName(handle=self.handle, name=pin_name, value=value)

        if debug:
            print(f"Set pin {pin_name} to {value}")

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
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

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
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

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
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
            all_pin_names = pins_names_inputs + pin_names_high + pin_names_low
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

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
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

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
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

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
    def set_adc_extended_function(self, adc_channel_names, index):
        """ set the ADC analog in extended functions roles"""
        commands = []
        for ch_name in adc_channel_names:
            commands += [f"{ch_name}_EF_INDEX"]
        values = [index] * len(commands)
        ljm.eWriteNames(self.handle, len(commands), commands, values)

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
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

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
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

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
    def write_names(self, commands: list, values: list):
        """wrap the ljm command for child classes + convenience"""
        assert len(commands) == len(values), "incompatible command and value lengths"
        ljm.eWriteNames(self.handle, len(commands), commands, values)

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
    def read_names(self, names_list: list):

        values = ljm.eReadNames(self.handle, len(names_list), names_list)
        return np.array(values).astype(float)

    # check_driver: ignore DC004 - a helper of the semantic functions, not a communication command
    def get_device_status(self):

        if not self.handle:
            return "Labjack device unconnected and no information available."
        else:
            return (f"Connected Labjack device {self.dev_type} with SN{self.infos['SN']} "
                    f"connected over {self.infos['CNXN']} at {self.infos['address']}")


    def pin_overlaps(self) -> dict[str, tuple[str, ...]] | None:
        """The pin names reaching one line on the connected model, {name: (other names, ...)}; None unconnected.

        DIOn is FIOn, EIOn, CIOn or MIOn on every model; on the T4 the flexible FIO4-FIO7 and EIO0-EIO3 are also the
        analog inputs AIN4-AIN11.
        """
        if self.dev_type not in ljm_constants.DIO_PINS:
            return None
        lines: dict[int, list[str]] = {}
        for name, line in ljm_constants.DIO_PINS[self.dev_type].items():
            lines.setdefault(line, []).append(name)
        if self.dev_type == "T4":
            for line in sorted(set(ljm_constants.FLEX_PINS_T4.values())):
                lines[line].append(f"AIN{line}")
        return {name: tuple(other for other in names if other != name)
                for names in lines.values() if len(names) > 1 for name in names}

    # -- Communication commands -------------------------------------------------
    # Declared with pysweepme's @command: only these are the driver's commands, and every call is checked against
    # the annotations. Pins carry the names printed on the device (AIN0, DAC0, FIO4, EIO0, CIO1, DIO8). The semantic
    # functions of the drivers (initialize, configure, measure, apply, ...) do not call them, and the methods above are
    # unchanged. Reference: https://support.labjack.com/docs/t-series-datasheet

    @command(returns=("identification",), reads="state")
    def get_identification(self) -> str:
        """Return device type, serial number, connection type and versions as text."""
        infos = self.get_infos()
        return (f"LabJack {infos['dev_type']}, SN{infos['SN']}, {infos['CNXN']}, "
                f"hardware {infos['HARDWARE_VERSION']:.4f}, "
                f"firmware {infos['FIRMWARE_VERSION']:.4f}")

    @command(returns=("device_temperature",))
    def get_device_temperature(self) -> Celsius:
        """Return the temperature of the device in degree C ('TEMPERATURE_DEVICE_K')."""
        return float(ljm.eReadName(self.handle, "TEMPERATURE_DEVICE_K")) - 273.15

    @command(returns=("voltage",))
    def get_voltage(self, pin: Pin) -> Volts:
        """Return the voltage of an analog input in V, e.g. pin 'AIN0'.

        On the T4, AIN4 to AIN11 are the flexible pins FIO4-FIO7 and EIO0-EIO3: they have to be
        switched to analog with set_pin_analog first.
        """
        if not str(pin).upper().startswith("AIN"):
            raise ValueError(f"{pin} is not an analog input, use a name like 'AIN0'")
        return float(ljm.eReadName(self.handle, str(pin).upper()))

    @command(returns=("voltages",))
    def get_voltages(self, pins: list) -> list:
        """Return the voltages in V of several analog inputs, e.g. ['AIN0', 'AIN1']."""
        names = [str(pin).upper() for pin in pins]
        if not names:
            return []
        if not all(name.startswith("AIN") for name in names):
            raise ValueError(f"Not all pins in {pins} are analog inputs")
        return [float(value) for value in ljm.eReadNames(self.handle, len(names), names)]

    @command
    def set_pin_analog(self, pin: Pin, pin_analog: bool) -> None:
        """Switch a flexible pin of the T4 (FIO4-FIO7, EIO0-EIO7) to an analog input (True) or a digital pin (False).

        As an analog input, FIO4 is read as AIN4, ..., EIO3 as AIN11. Other models have no flexible pins.
        """
        if self.dev_type != "T4":
            raise ValueError(f"Only the T4 has flexible pins, this is a {self.dev_type}")
        self.set_flex_pins_to_analog([str(pin)], set_digital=not pin_analog)

    @command
    def set_resolution_index(self, resolution_index: int) -> None:
        """Set the resolution index of all analog inputs ('AIN_ALL_RESOLUTION_INDEX').

        0 is the default. Higher indices give a lower noise at a lower speed, the maximum depends
        on the model (T4: 5).
        """
        ljm.eWriteName(self.handle, "AIN_ALL_RESOLUTION_INDEX", int(resolution_index))

    @command(returns=("resolution_index",), reads="setpoint")
    def get_resolution_index(self) -> int:
        """Return the resolution index of all analog inputs."""
        return int(ljm.eReadName(self.handle, "AIN_ALL_RESOLUTION_INDEX"))

    @command
    def set_dac_voltage(self, channel: DacChannel, dac_voltage: DacVoltage) -> None:
        """Set the voltage of an analog output in V (channel 0 or 1 for 'DAC0' or 'DAC1', 0 to 5 V)."""
        ljm.eWriteName(self.handle, f"DAC{channel}", dac_voltage)

    @command(returns=("dac_voltage",), reads="setpoint")
    def get_dac_voltage(self, channel: DacChannel) -> DacVoltage:
        """Return the voltage in V that an analog output is set to (channel 0 or 1)."""
        return float(ljm.eReadName(self.handle, f"DAC{channel}"))

    @command(hazards="The pin becomes an output: a signal that drives the same line from outside is shorted "
                     "against it.")
    def set_digital_output(self, pin: Pin, digital_output: bool) -> None:
        """Set a digital pin to an output that is high (True) or low (False).

        Other pins are not changed. Flexible pins of the T4 are switched to digital.
        """
        pins = [str(pin)]
        self.set_digital_IO(pins_names_inputs=[],
                            pin_names_high=pins if digital_output else [],
                            pin_names_low=[] if digital_output else pins)

    @command(returns=("digital_output",), reads="setpoint", composite=True)
    def get_digital_output(self, pin: Pin) -> bool:
        """Return whether a digital output pin is high ('DIO_STATE') - the read-back of set_digital_output."""
        return bool(self.get_digital_state(pin))

    @command(kind="run")
    def set_digital_input(self, pin: Pin) -> None:
        """Set a digital pin to an input. Other pins are not changed."""
        self.set_digital_IO(pins_names_inputs=[str(pin)], pin_names_high=[], pin_names_low=[])

    @command(returns=("digital_state",))
    def get_digital_state(self, pin: Pin) -> int:
        """Return the level of a digital pin, 1 for high and 0 for low ('DIO_STATE').

        Unlike read_pin this does not change the direction of the pin.
        """
        pins = ljm_constants.DIO_PINS[self.dev_type]
        if str(pin) not in pins:
            raise ValueError(f"{pin} is not a digital pin. Valid: {list(pins.keys())}")
        return (int(ljm.eReadName(self.handle, "DIO_STATE")) >> pins[str(pin)]) & 1

    @command(composite=True,
             hazards="OUT makes the pin an output: a signal that drives the same line from outside is shorted "
                     "against it.")
    def set_digital_direction(self, pin: Pin, digital_direction: DigitalDirection) -> None:
        """Make a digital pin an input ('IN') or an output ('OUT'); an output keeps the level the pin has now.

        Other pins are not changed. Flexible pins of the T4 are switched to digital.
        """
        if str(digital_direction).upper() == "IN":
            self.set_digital_input(pin)
        else:
            self.set_digital_output(pin, bool(self.get_digital_state(pin)))

    @command(returns=("digital_direction",), reads="setpoint")
    def get_digital_direction(self, pin: Pin) -> DigitalDirection:
        """Return the direction of a digital pin, 'IN' or 'OUT' ('DIO_DIRECTION')."""
        pins = ljm_constants.DIO_PINS[self.dev_type]
        if str(pin) not in pins:
            raise ValueError(f"{pin} is not a digital pin. Valid: {list(pins.keys())}")
        return "OUT" if (int(ljm.eReadName(self.handle, "DIO_DIRECTION")) >> pins[str(pin)]) & 1 else "IN"

    def _counter_dio_name(self, pin: str) -> str:
        """Return the DIO name of a high speed counter pin, CIOx are translated to DIOx."""
        pin = str(pin)
        pin = ljm_constants.EF_DIO_NAMES[self.dev_type].get(pin, pin)
        if pin not in ljm_constants.COUNTER_PINS[self.dev_type]:
            raise ValueError(f"{pin} is not a counter pin. "
                             f"Valid: {ljm_constants.COUNTER_PINS[self.dev_type]}")
        return pin

    # One batch of LJM writes rather than one command per register: the counter is disabled, its mode set and
    # enabled again in one call, so it is never left half configured.
    @command(kind="run", composite=True,
             hazards="Clock 0 and the clock sharing the pin are switched off if they run, so a PWM or other "
                     "clocked output that uses them stops.")
    def enable_counter(self, pin: Pin) -> None:
        """Make a pin a high speed counter and reset its count to zero (e.g. 'CIO1' or 'DIO17').

        The pin becomes a digital input. Read the count with get_counter or reset_counter.
        """
        self.set_pins_to_hs_counter([self._counter_dio_name(pin)], reset=True)

    @command(returns=("count",))
    def get_counter(self, pin: Pin) -> int:
        """Return the count of a high speed counter without resetting it ('DIOx_EF_READ_A').

        The counter has to be enabled with enable_counter first.
        """
        return int(ljm.eReadName(self.handle, f"{self._counter_dio_name(pin)}_EF_READ_A"))

    @command(returns=("count",))
    def reset_counter(self, pin: Pin) -> int:
        """Return the count of a high speed counter and reset it to zero ('DIOx_EF_READ_A_AND_RESET')."""
        return int(ljm.eReadName(self.handle,
                                 f"{self._counter_dio_name(pin)}_EF_READ_A_AND_RESET"))

    @command(kind="run")
    def disable_counter(self, pin: Pin) -> None:
        """Disable the high speed counter of a pin ('DIOx_EF_ENABLE')."""
        ljm.eWriteName(self.handle, f"{self._counter_dio_name(pin)}_EF_ENABLE", 0)

    @command(kind="run", composite=True)  # stops a running stream first
    def start_stream(self, pins: list, scan_rate: Hertz, scans_per_read: int = 0,
                     resolution_index: int = 0) -> None:
        """Start streaming analog inputs at a fixed rate.

        pins: analog inputs to scan in this order, e.g. ['AIN0', 'AIN1'].
        scan_rate: scans per second. One scan is one value of every pin.
        scans_per_read: scans that read_stream returns at once, 0 for half a second of data.
        resolution_index: resolution index of the stream, 0 is the default.
        The data is collected with read_stream and the stream ended with stop_stream. A stream
        that is still running is stopped first. The device may run at a rate close to the one asked
        for: get_stream_scan_rate answers the rate it actually runs at.
        """
        names = [str(pin).upper() for pin in pins]
        if not names or not all(name.startswith("AIN") for name in names):
            raise ValueError(f"Streaming needs analog inputs like ['AIN0'], not {pins}")
        if scan_rate <= 0:
            raise ValueError("The scan rate must be positive")

        self.stop_stream()

        # settings that must not be left from earlier use: no triggered stream, internal clock
        for name, value in (("STREAM_TRIGGER_INDEX", 0), ("STREAM_CLOCK_SOURCE", 0)):
            try:
                ljm.eWriteName(self.handle, name, value)
            except ljm.ljm.LJMError:
                debug(f"{name} could not be set, the device may not have it")
        ljm.eWriteName(self.handle, "STREAM_RESOLUTION_INDEX", resolution_index)

        scans_per_read = scans_per_read or max(1, int(scan_rate / 2))
        addresses = ljm.namesToAddresses(len(names), names)[0]
        # LJM answers the scan rate the device actually runs at; the data is timed by it, so it is kept for
        # get_stream_scan_rate and read_stream.
        actual_rate = ljm.eStreamStart(self.handle, scans_per_read, len(names), addresses, scan_rate)
        self._scan_rate = float(actual_rate)
        self._stream_pins = tuple(names)
        self._stream_running = True

    @command(returns=("scan_rate",), reads="setpoint")
    def get_stream_scan_rate(self) -> Hertz:
        """Return the scan rate in Hz the last stream started with start_stream actually runs (or ran) at."""
        if self._scan_rate is None:
            raise RuntimeError("No stream was started, call start_stream first")
        return self._scan_rate

    @command(returns=("stream_block",))
    def read_stream(self) -> dict:
        """Return the next block of a running stream as a dictionary.

        'data' is a list of scans, each scan a list of values in V in the order of the pins given
        to start_stream, taken at 'scan_rate' scans per second. 'device_backlog' and 'ljm_backlog'
        are the scans waiting in the device and in LJM; if they keep growing the stream is read too
        slowly and data will be lost.
        After a device buffer overflow LJM fills in the lost scans with the dummy value -9999.0
        (stream auto-recovery). They keep the timing of the stream intact but carry no
        measurement, so they are returned as NaN, and 'skipped_scans' is the number of such scans
        in 'data'.
        The call waits until a block of scans_per_read scans is available.
        """
        if not self._stream_running:
            raise RuntimeError("No stream is running, call start_stream first")
        data, device_backlog, ljm_backlog = ljm.eStreamRead(self.handle)
        scans = np.array(data, dtype=float).reshape(-1, len(self._stream_pins))
        dummy = scans == LJM_DUMMY_VALUE
        skipped_scans = int(np.any(dummy, axis=1).sum())
        scans[dummy] = np.nan
        return {"pins": list(self._stream_pins), "scan_rate": self._scan_rate, "data": scans.tolist(),
                "device_backlog": int(device_backlog), "ljm_backlog": int(ljm_backlog),
                "skipped_scans": skipped_scans}

    @command
    def stop_stream(self) -> None:
        """Stop a running stream. Nothing happens if no stream is running."""
        try:
            ljm.eStreamStop(self.handle)
        except ljm.ljm.LJMError:
            pass  # LJME_STREAM_NOT_RUNNING
        self._stream_running = False

    @command(returns=("stream",), composite=True)
    def acquire_stream(self, pins: list, scan_rate: Hertz, number_of_scans: int,
                       resolution_index: int = 0) -> dict:
        """Stream analog inputs, collect a number of scans and stop; return the result.

        The call blocks for number_of_scans / scan_rate seconds, which is limited to 60 s. The
        result has the 'pins', the actual 'scan_rate' in Hz, the 'time' of every scan in s and the
        'data' as a list of scans in V, like read_stream, and 'skipped_scans', the number of scans
        in 'data' that are missing and returned as NaN (see read_stream). Use start_stream and
        read_stream for longer streams.
        """
        if number_of_scans < 1:
            raise ValueError("number_of_scans must be at least 1")
        if scan_rate <= 0:
            raise ValueError("The scan rate must be positive")
        if number_of_scans / scan_rate > 60:
            raise ValueError("The acquisition would take more than 60 s, "
                             "use start_stream and read_stream instead")

        self.start_stream(pins, scan_rate, scans_per_read=min(number_of_scans, max(1, int(scan_rate / 2))),
                          resolution_index=resolution_index)
        actual_rate = self.get_stream_scan_rate()
        scans = []
        try:
            while len(scans) < number_of_scans:
                scans += self.read_stream()["data"]
        finally:
            self.stop_stream()
        scans = scans[:number_of_scans]
        skipped_scans = int(np.any(np.isnan(np.asarray(scans, dtype=float)), axis=1).sum())
        return {"pins": [str(pin).upper() for pin in pins], "scan_rate": actual_rate,
                "time": [i / actual_rate for i in range(len(scans))], "data": scans,
                "skipped_scans": skipped_scans}


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
