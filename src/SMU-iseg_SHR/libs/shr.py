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


    # Configure Ramp commands - Page 35



    def set_ramp_speed_voltage(self, speed: float) -> None:
        """Set the ramp speed for voltage in V/s or %/s depending on the device."""
        self.write(f":CONF:RAMP:VOLT {speed},(@{self.channel})")

    def set_ramp_speed_current(self, speed: float) -> None:
        """Set the ramp speed for current in A/s or %/s depending on the device."""
        self.write(f":CONF:RAMP:CURR {speed},(@{self.channel})")

    def set_ramp_speed_max(self, speed: float) -> None:
        """Set the maximum ramp speed limit."""
        self.write(f":CONF:RAMP:MAX {speed},(@{self.channel})")

    # TODO Page 36

    # Page 37

    def configure_ramp_current_up(self, current: float) -> None:
        """Configures the channel current ramp-up speed."""
        self.write(f":CONF:RAMP:CURR:UP {current},(@{self.channel})")

    def query_ramp_current_up(self) -> str:
        """Queries the channel current ramp-up speed."""
        return self.query(f":CONF:RAMP:CURR:UP? (@{self.channel})")

    def configure_ramp_current_down(self, current: float) -> None:
        """Configures the channel current ramp-down speed."""
        self.write(f":CONF:RAMP:CURR:DOWN {current},(@{self.channel})")

    def query_ramp_current_down(self) -> str:
        """Queries the channel current ramp-down speed."""
        return self.query(f":CONF:RAMP:CURR:DOWN? (@{self.channel})")

    def configure_adc_sample_rate(self, value: int) -> None:
        """Sets the ADC sample rate."""
        self.write(f":CONF:ADC:SAMP:RATE {value},(@{self.channel})")

    def query_adc_sample_rate(self) -> str:
        """Queries the ADC sample rate."""
        return self.query(f":CONF:ADC:SAMP:RATE? (@{self.channel})")

    def configure_digital_filter(self, value: int) -> None:
        """Sets the digital filter value."""
        self.write(f":CONF:DIG:FILT {value},(@{self.channel})")

    def query_digital_filter(self) -> str:
        """Queries the digital filter value."""
        return self.query(f":CONF:DIG:FILT? (@{self.channel})")

    def configure_fine_adjustment(self, state: str) -> None:
        """Enables or disables the fine adjustment."""
        self.write(f":CONF:FINE:ADJ {state},(@{self.channel})")

    def query_fine_adjustment(self) -> str:
        """Queries the state of fine adjustment."""
        return self.query(f":CONF:FINE:ADJ? (@{self.channel})")

    def configure_fine_adjustment_clear(self) -> None:
        """Clears the fine adjustment value."""
        self.write(f":CONF:FINE:ADJ:CLEAR,(@{self.channel})")

    def configure_kill_enable(self, state: str) -> None:
        """Enables or disables kill function."""
        self.write(f":CONF:KILL:ENABLE {state}")

    def query_kill_enable(self) -> str:
        """Queries the kill enable state."""
        return self.query(f":CONF:KILL:ENABLE?")

    # Page 38

    def configure_kill_bounds_voltage(self, voltage: float) -> None:
        """Sets the voltage bounds for the kill function."""
        self.write(f":CONF:KILL:BOUNDS:VOLT {voltage},(@{self.channel})")

    def query_kill_bounds_voltage(self) -> str:
        """Queries the voltage bounds for the kill function."""
        return self.query(f":CONF:KILL:BOUNDS:VOLT? (@{self.channel})")

    def configure_kill_bounds_current(self, current: float) -> None:
        """Sets the current bounds for the kill function."""
        self.write(f":CONF:KILL:BOUNDS:CURR {current},(@{self.channel})")

    def query_kill_bounds_current(self) -> str:
        """Queries the current bounds for the kill function."""
        return self.query(f":CONF:KILL:BOUNDS:CURR? (@{self.channel})")

    def configure_kill_timeout(self, timeout: int) -> None:
        """Sets the kill timeout in milliseconds."""
        self.write(f":CONF:KILL:TIME {timeout},(@{self.channel})")

    def query_kill_timeout(self) -> str:
        """Queries the kill timeout in milliseconds."""
        return self.query(f":CONF:KILL:TIME? (@{self.channel})")

    def configure_kill_action(self, action: int) -> None:
        """Sets the action on kill condition."""
        self.write(f":CONF:KILL:ACTION {action},(@{self.channel})")

    def query_kill_action(self) -> str:
        """Queries the action on kill condition."""
        return self.query(f":CONF:KILL:ACTION? (@{self.channel})")

    # Page 39

    def configure_voltage_nominal(self, voltage: float) -> None:
        """Sets the channel nominal voltage."""
        self.write(f":CONF:VOLT:NOM {voltage},(@{self.channel})")

    def query_voltage_nominal(self) -> str:
        """Queries the channel nominal voltage."""
        return self.query(f":CONF:VOLT:NOM? (@{self.channel})")

    def configure_current_nominal(self, current: float) -> None:
        """Sets the channel nominal current."""
        self.write(f":CONF:CURR:NOM {current},(@{self.channel})")

    def query_current_nominal(self) -> str:
        """Queries the channel nominal current."""
        return self.query(f":CONF:CURR:NOM? (@{self.channel})")

    def configure_voltage_limit(self, voltage: float) -> None:
        """Sets the channel voltage limit."""
        self.write(f":CONF:VOLT:LIM {voltage},(@{self.channel})")

    def query_voltage_limit(self) -> str:
        """Queries the channel voltage limit."""
        return self.query(f":CONF:VOLT:LIM? (@{self.channel})")

    def configure_current_limit(self, current: float) -> None:
        """Sets the channel current limit."""
        self.write(f":CONF:CURR:LIM {current},(@{self.channel})")

    def query_current_limit(self) -> str:
        """Queries the channel current limit."""
        return self.query(f":CONF:CURR:LIM? (@{self.channel})")

    # Page 40

