# TODO: Add license
from __future__ import annotations

from abc import ABC, abstractmethod


class IsegDevice(ABC):

    def __init__(self):
        super().__init__()
        self.channel = "0"  # Default, can be overridden via GUI parameters or set_parameters()

    @abstractmethod
    def write(self, command: str) -> None:
        """Writes a command to the device."""

    @abstractmethod
    def query(self, command: str) -> str:
        """Queries the device and returns the response."""

    # Channel Voltage Commands - Page 33

    def set_voltage(self, voltage: float) -> None:
        """Set the voltage setpoint (Vset) in Volts."""
        self.write(f":VOLT {voltage},(@{self.channel})")

    def voltage_on(self) -> None:
        """Switch on high voltage with configured ramp speed."""
        self.write(f":VOLT ON,(@{self.channel})")

    def voltage_off(self) -> None:
        """Switch off high voltage with configured ramp speed."""
        self.write(f":VOLT OFF,(@{self.channel})")

    def voltage_emergency_off(self) -> None:
        """Immediately shut down high voltage output without ramp."""
        self.write(f":VOLT EMCY OFF,(@{self.channel})")

    def voltage_emergency_clear(self) -> None:
        """Clear emergency off state, return channel to off state."""
        self.write(f":VOLT EMCY CLR,(@{self.channel})")

    def set_voltage_bounds(self, bounds: float) -> None:
        """Set the voltage bounds (Vbounds) tolerance in Volts."""
        self.write(f":VOLT:BOUNDS {bounds},(@{self.channel})")


    # Channel current commands - page 33

    def set_current(self, current: float) -> None:
        """Set the current setpoint (Iset) in Amperes."""
        self.write(f":CURR {current},(@{self.channel})")

    def set_current_bounds(self, bounds: float) -> None:
        """Set the current bounds (Ibounds) tolerance in Amperes."""
        self.write(f":CURR:BOUNDS {bounds},(@{self.channel})")


    # Channel event commands - page 33

    def clear_event(self) -> None:
        """Clear the Channel Event Status register."""
        self.write(f":EVENT CLEAR,(@{self.channel})")

    def clear_event_mask(self, mask: int) -> None:
        """Clear specific bits in Channel Event Status register by mask."""
        self.write(f":EVENT {mask},(@{self.channel})")

    def set_event_mask(self, mask: int) -> None:
        """Set the Channel Event Mask register."""
        self.write(f":EVENT:MASK {mask},(@{self.channel})")





    # Channel configuration commands - Page 34

    def set_trip_timeout(self, time_ms: int) -> None:
        """Set the delayed trip timeout in milliseconds (1..4095ms)."""
        if time_ms < 1 or time_ms > 4095:
            msg = "Timeout must be between 1 and 4095 ms."
            raise ValueError(msg)
        self.write(f":CONF:TRIP:TIME {time_ms},(@{self.channel})")

    def get_trip_timeout(self) -> int:
        """Query the programmed trip timeout in milliseconds."""
        response = self.query(f":CONF:TRIP:TIME? (@{self.channel})")
        if response.endswith("ms"):
            response = response[:-3]
        return int(response)

    def set_trip_action(self, action: int) -> None:
        """Set the action that happens when a current trip occurs.

        Action values:
            0: No action, status flag Trip will be set after timeout
            1: Turn off channel with ramp
            2: Shut down channel without ramp
            3: Shut down the module without ramp
            4: Disable the delayed trip function
        """
        self.write(f":CONF:TRIP:ACTION {action},(@{self.channel})")

    def get_trip_action(self) -> int:
        """Query the configured trip action."""
        response = self.query(f":CONF:TRIP:ACTION? (@{self.channel})")
        return int(response)

    def set_inhibit_action(self, action: int) -> None:
        """Set the action that happens when external inhibit occurs.

        Action values:
            0: No action, status flag External Inhibit will be set
            1: Turn off channel with ramp
            2: Shut down channel without ramp
            3: Shut down the module without ramp
            4: Disable the External Inhibit function
        """
        self.write(f":CONF:INH:ACTION {action},(@{self.channel})")

    def get_inhibit_action(self) -> int:
        """Query the configured external inhibit action."""
        response = self.query(f":CONF:INH:ACTION? (@{self.channel})")
        return int(response)

    def set_output_mode(self, mode: int) -> None:
        """Set the channel output mode.

        Mode values:
            1: Normal mode
            2: Alternate mode 1
            3: Alternate mode 2
        """
        self.write(f":CONF:OUTP:MODE {mode},(@{self.channel})")

    def get_output_mode(self) -> int:
        """Query the channel output mode."""
        response = self.query(f":CONF:OUTP:MODE? (@{self.channel})")
        return int(response)

    def get_supported_output_modes(self) -> list[int]:
        """Query the available output modes."""
        response = self.query(f":CONF:OUTP:MODE:LIST? (@{self.channel})")
        return list(map(int, response.split(",")))

    def set_output_polarity(self, polarity: str) -> None:
        """Set the output polarity.

        Polarity values:
            'POS' - Positive polarity
            'NEG' - Negative polarity
        """
        self.write(f":CONF:OUTP:POL {polarity},(@{self.channel})")

    def get_output_polarity(self) -> str:
        """Query the channel output polarity."""
        response = self.query(f":CONF:OUTP:POL? (@{self.channel})")
        return response.strip()

    def get_supported_output_polarities(self) -> list[str]:
        """Query the available output polarities."""
        response = self.query(f":CONF:OUTP:POL:LIST? (@{self.channel})")
        return response.split(",")





    # Read channel commands - Page 35
    # Voltage read commands

    def get_voltage_set(self) -> float:
        """Get the voltage set V_set in Volt."""
        response = self.query(f":READ:VOLT? (@{self.channel})")
        return float(response[:-1])

    def get_voltage_limit(self) -> float:
        """Get the voltage limit V_lim in Volt."""
        response = self.query(f":READ:VOLT:LIM? (@{self.channel})")
        return float(response[:-1])

    def get_voltage_nominal(self) -> float:
        """Get the channel voltage nominal Vnom in Volt."""
        response = self.query(f":READ:VOLT:NOM? (@{self.channel})")
        return float(response[:-1])

    def get_voltage_mode(self) -> str:
        """Get the configured channel voltage mode with polarity sign in Volt."""
        response = self.query(f":READ:VOLT:MODE? (@{self.channel})")
        return response.strip()

    def get_supported_voltage_modes(self) -> list[float]:
        """Get the available voltage modes."""
        response = self.query(f":READ:VOLT:MODE:LIST? (@{self.channel})")
        supported_modes = response.split(",")
        return [float(mode[:-1]) for mode in supported_modes]

    def get_voltage_bounds(self) -> float:
        """Get the voltage bounds V_bounds in Volt."""
        response = self.query(f":READ:VOLT:BOUNDS? (@{self.channel})")
        return float(response[:-1])

    def get_voltage_on(self) -> bool:
        """Get the channel voltage on state."""
        response = self.query(f":READ:VOLT:ON? (@{self.channel})")
        return response.strip() == "1"

    def get_voltage_emergency(self) -> bool:
        """Get the channel emergency off state."""
        response = self.query(f":READ:VOLT:EMCY? (@{self.channel})")
        return response.strip() == "1"

    # Current read commands

    def get_current_set(self) -> float:
        """Get the current set I_set in Ampere."""
        response = self.query(f":READ:CURR? (@{self.channel})")
        return float(response[:-1])

    def get_current_limit(self) -> float:
        """Get the current limit I_lim in Ampere."""
        response = self.query(f":READ:CURR:LIM? (@{self.channel})")
        return float(response[:-1])

    def get_current_nominal(self) -> float:
        """Get the channel current nominal I_nom in Ampere."""
        response = self.query(f":READ:CURR:NOM? (@{self.channel})")
        return float(response[:-1])

    def get_current_mode(self) -> str:
        """Get the configured channel current mode with polarity sign in Ampere."""
        response = self.query(f":READ:CURR:MODE? (@{self.channel})")
        return response.strip()

    def get_supported_current_modes(self) -> list[float]:
        """Get the available current modes."""
        response = self.query(f":READ:CURR:MODE:LIST? (@{self.channel})")
        supported_modes = response.split(",")
        return [float(mode[:-1]) for mode in supported_modes]

    def get_current_bounds(self) -> float:
        """Get the current bounds I_bounds in Ampere."""
        response = self.query(f":READ:CURR:BOUNDS? (@{self.channel})")
        return float(response[:-1])

    # Ramp read commands

    def get_voltage_ramp_speed(self) -> float:
        """Get the ramp speed in V/s."""
        response = self.query(f":READ:RAMP:VOLT? (@{self.channel})")
        return float(response[:-3])

    def get_voltage_ramp_speed_minimum(self) -> float:
        """Get the minimum ramp speed in V/s."""
        response = self.query(f":READ:RAMP:VOLT:MIN? (@{self.channel})")
        return float(response[:-3])

    def get_voltage_ramp_speed_maximum(self) -> float:
        """Get the maximum ramp speed in V/s."""
        response = self.query(f":READ:RAMP:VOLT:MAX? (@{self.channel})")
        return float(response[:-3])

    def get_current_ramp_speed(self) -> float:
        """Get the ramp speed in A/s."""
        response = self.query(f":READ:RAMP:CURR? (@{self.channel})")
        return float(response[:-3])

    def get_current_ramp_speed_minimum(self) -> float:
        """Get the minimum ramp speed in A/s."""
        response = self.query(f":READ:RAMP:CURR:MIN? (@{self.channel})")
        return float(response[:-3])

    def get_current_ramp_speed_maximum(self) -> float:
        """Get the maximum ramp speed in A/s."""
        response = self.query(f":READ:RAMP:CURR:MAX? (@{self.channel})")
        return float(response[:-3])

    # Channel status

    def get_channel_control_register(self) -> str:
        """Get the channel control register."""
        return self.query(f":READ:CHAN:CONTROL? (@{self.channel})")

    def get_channel_status_register(self) -> str:
        """Get the channel status register."""
        return self.query(f":READ:CHAN:STATUS? (@{self.channel})")

    def get_channel_event_status_register(self) -> str:
        """Get the channel event status register."""
        return self.query(f":READ:CHAN:EVENT:STATUS? (@{self.channel})")

    def get_channel_event_mask_register(self) -> str:
        """Get the channel event mask register."""
        return self.query(f":READ:CHAN:EVENT:MASK? (@{self.channel})")



    # Measure commands - Page 35

    def get_voltage(self) -> float:
        """Get the measured voltage in Volts."""
        response = self.query(f":MEAS:VOLT? (@{self.channel})")
        return float(response[:-1])

    def get_current(self) -> float:
        """Get the measured current in Amperes."""
        response = self.query(f":MEAS:CURR? (@{self.channel})")
        return float(response[:-1])


    # Configure Module Ramps (for all channels) commands - Page 35

    def set_module_voltage_ramp_speed(self, speed: float) -> None:
        """Set the module voltage ramp speed in %/s."""
        self.write(f":CONF:RAMP:VOLT {speed}")

    def get_module_voltage_ramp_speed(self) -> float:
        """Get the module voltage ramp speed in %/s."""
        response = self.query(":CONF:RAMP:VOLT?")
        return float(response[:-3])

    def set_module_voltage_ramp_speed_emergency(self, speed: float) -> None:
        """Set the module voltage ramp speed emergency in %/s."""
        self.write(f":CONF:RAMP:VOLT:EMCY {speed}")

    # TODO: This function does not return the correct value/the device does not support it
    def get_module_voltage_ramp_speed_emergency(self) -> float:
        """Get the module voltage ramp speed emergency in %/s."""
        response = self.query(":CONF:RAMP:VOLT:EMCY?")
        return float(response[:-3])

    # TODO: This function does not return the correct value/the device does not support it
    def get_module_voltage_ramp_speed_emergency_minimum(self) -> float:
        """Get the module voltage ramp speed emergency minimum in %/s."""
        response = self.query(":CONF:RAMP:VOLT:EMCY:MIN?")
        return float(response[:-3])

    # TODO: This function does not return the correct value/the device does not support it
    def get_module_voltage_ramp_speed_emergency_maximum(self) -> float:
        """Get the module voltage ramp speed emergency maximum in %/s."""
        response = self.query(":CONF:RAMP:VOLT:EMCY:MAX?")
        return float(response[:-3])

    def set_module_current_ramp_speed(self, speed: float) -> None:
        """Set the module current ramp speed in %/s."""
        self.write(f":CONF:RAMP:CURR {speed}")

    def get_module_current_ramp_speed(self) -> float:
        """Get the module current ramp speed in %/s."""
        response = self.query(":CONF:RAMP:CURR?")
        return float(response[:-3])


    # Set ramp speed for up and down commands - Page 36

    def set_voltage_ramp_up_down_speed(self, speed: float) -> None:
        """Set the channel voltage ramp speed for up and down in Volt/second."""
        self.write(f":CONF:RAMP:VOLT {speed},(@{self.channel})")

    def set_voltage_ramp_up_speed(self, speed: float) -> None:
        """Set the channel voltage ramp up speed in Volt/second."""
        self.write(f":CONF:RAMP:VOLT:UP {speed},(@{self.channel})")

    def get_voltage_ramp_up_speed(self) -> float:
        """Get the channel voltage ramp up speed in Volt/second."""
        response = self.query(f":CONF:RAMP:VOLT:UP? (@{self.channel})")
        return float(response[:-3])

    def set_voltage_ramp_down_speed(self, speed: float) -> None:
        """Set the channel voltage ramp down speed in Volt/second."""
        self.write(f":CONF:RAMP:VOLT:DOWN {speed},(@{self.channel})")

    def get_voltage_ramp_down_speed(self) -> float:
        """Get the channel voltage ramp down speed in Volt/second."""
        response = self.query(f":CONF:RAMP:VOLT:DOWN? (@{self.channel})")
        return float(response[:-3])

    def set_current_ramp_up_down_speed(self, speed: float) -> None:
        """Set the channel current ramp speed for up and down in Ampere/second."""
        self.write(f":CONF:RAMP:CURR {speed},(@{self.channel})")

    def set_current_ramp_up_speed(self, speed: float) -> None:
        """Set the channel current ramp up speed in Ampere/second."""
        self.write(f":CONF:RAMP:CURR:UP {speed},(@{self.channel})")

    def get_current_ramp_up_speed(self) -> float:
        """Get the channel current ramp up speed in Ampere/second."""
        response = self.query(f":CONF:RAMP:CURR:UP? (@{self.channel})")
        return float(response[:-3])

    def set_current_ramp_down_speed(self, speed: float) -> None:
        """Set the channel current ramp down speed in Ampere/second."""
        self.write(f":CONF:RAMP:CURR:DOWN {speed},(@{self.channel})")

    def get_current_ramp_down_speed(self) -> float:
        """Get the channel current ramp down speed in Ampere/second."""
        response = self.query(f":CONF:RAMP:CURR:DOWN? (@{self.channel})")
        return float(response[:-3])

