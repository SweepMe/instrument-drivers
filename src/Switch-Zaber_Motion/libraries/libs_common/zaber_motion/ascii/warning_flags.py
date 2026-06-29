# ===== THIS FILE IS GENERATED FROM A TEMPLATE ===== #
# ============== DO NOT EDIT DIRECTLY ============== #


class WarningFlags:

    """
    Critical System Error.
    """
    CRITICAL_SYSTEM_ERROR = "FF"

    """
    Peripheral Not Supported.
    """
    PERIPHERAL_NOT_SUPPORTED = "FN"

    """
    Peripheral Inactive.
    """
    PERIPHERAL_INACTIVE = "FZ"

    """
    Hardware Emergency Stop Driver Disabled.
    """
    HARDWARE_EMERGENCY_STOP = "FH"

    """
    Overvoltage or Undervoltage Driver Disabled.
    """
    OVERVOLTAGE_OR_UNDERVOLTAGE = "FV"

    """
    Driver Disabled on Startup or by Command.
    Devices with Firmware 7.11 and above.
    """
    DRIVER_DISABLED_NO_FAULT = "FO"

    """
    Current Inrush Error.
    """
    CURRENT_INRUSH_ERROR = "FC"

    """
    Motor Temperature Error.
    """
    MOTOR_TEMPERATURE_ERROR = "FM"

    """
    Driver Disabled.
    Devices with Firmware 7.10 and lower.
    """
    DRIVER_DISABLED = "FD"

    """
    Encoder Error.
    """
    ENCODER_ERROR = "FQ"

    """
    Index Error.
    """
    INDEX_ERROR = "FI"

    """
    Analog Encoder Sync Error.
    """
    ANALOG_ENCODER_SYNC_ERROR = "FA"

    """
    Overdrive Limit Exceeded.
    """
    OVERDRIVE_LIMIT_EXCEEDED = "FR"

    """
    Stalled and Stopped.
    """
    STALLED_AND_STOPPED = "FS"

    """
    Stream Bounds Error.
    """
    STREAM_BOUNDS_ERROR = "FB"

    """
    Interpolated Path Deviation.
    """
    INTERPOLATED_PATH_DEVIATION = "FP"

    """
    Limit Error.
    """
    LIMIT_ERROR = "FE"

    """
    Excessive Twist.
    """
    EXCESSIVE_TWIST = "FT"

    """
    Unexpected Limit Trigger.
    """
    UNEXPECTED_LIMIT_TRIGGER = "WL"

    """
    Voltage Out of Range.
    """
    VOLTAGE_OUT_OF_RANGE = "WV"

    """
    Controller Temperature High.
    """
    CONTROLLER_TEMPERATURE_HIGH = "WT"

    """
    Stalled with Recovery.
    """
    STALLED_WITH_RECOVERY = "WS"

    """
    Displaced When Stationary.
    """
    DISPLACED_WHEN_STATIONARY = "WM"

    """
    Invalid Calibration Type.
    """
    INVALID_CALIBRATION_TYPE = "WP"

    """
    No Reference Position.
    """
    NO_REFERENCE_POSITION = "WR"

    """
    Device Not Homed.
    """
    DEVICE_NOT_HOMED = "WH"

    """
    Manual Control.
    """
    MANUAL_CONTROL = "NC"

    """
    Movement Interrupted.
    """
    MOVEMENT_INTERRUPTED = "NI"

    """
    Stream Discontinuity.
    """
    STREAM_DISCONTINUITY = "ND"

    """
    Value Rounded.
    """
    VALUE_ROUNDED = "NR"

    """
    Value Truncated.
    """
    VALUE_TRUNCATED = "NT"

    """
    Setting Update Pending.
    """
    SETTING_UPDATE_PENDING = "NU"

    """
    Joystick Calibrating.
    """
    JOYSTICK_CALIBRATING = "NJ"

    """
    Device in Firmware Update Mode.
    Firmware 6.xx only.
    """
    FIRMWARE_UPDATE_MODE = "NB"
