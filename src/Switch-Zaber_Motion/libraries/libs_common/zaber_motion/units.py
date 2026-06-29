# This file is generated from the Zaber device database. Do not manually edit this file.
# pylint: disable=line-too-long, too-many-branches, too-many-return-statements

from enum import Enum
from typing import Union, Literal


class Units(Enum):
    NATIVE = ''

    LENGTH_METRES = 'Length:metres'
    LENGTH_CENTIMETRES = 'Length:centimetres'
    LENGTH_MILLIMETRES = 'Length:millimetres'
    LENGTH_MICROMETRES = 'Length:micrometres'
    LENGTH_NANOMETRES = 'Length:nanometres'
    LENGTH_INCHES = 'Length:inches'

    VELOCITY_METRES_PER_SECOND = 'Velocity:metres per second'
    VELOCITY_CENTIMETRES_PER_SECOND = 'Velocity:centimetres per second'
    VELOCITY_MILLIMETRES_PER_SECOND = 'Velocity:millimetres per second'
    VELOCITY_MICROMETRES_PER_SECOND = 'Velocity:micrometres per second'
    VELOCITY_NANOMETRES_PER_SECOND = 'Velocity:nanometres per second'
    VELOCITY_INCHES_PER_SECOND = 'Velocity:inches per second'

    ACCELERATION_METRES_PER_SECOND_SQUARED = 'Acceleration:metres per second squared'
    ACCELERATION_CENTIMETRES_PER_SECOND_SQUARED = 'Acceleration:centimetres per second squared'
    ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED = 'Acceleration:millimetres per second squared'
    ACCELERATION_MICROMETRES_PER_SECOND_SQUARED = 'Acceleration:micrometres per second squared'
    ACCELERATION_NANOMETRES_PER_SECOND_SQUARED = 'Acceleration:nanometres per second squared'
    ACCELERATION_INCHES_PER_SECOND_SQUARED = 'Acceleration:inches per second squared'

    ANGLE_DEGREES = 'Angle:degrees'
    ANGLE_RADIANS = 'Angle:radians'

    ANGULAR_VELOCITY_DEGREES_PER_SECOND = 'Angular Velocity:degrees per second'
    ANGULAR_VELOCITY_RADIANS_PER_SECOND = 'Angular Velocity:radians per second'

    ANGULAR_ACCELERATION_DEGREES_PER_SECOND_SQUARED = 'Angular Acceleration:degrees per second squared'
    ANGULAR_ACCELERATION_RADIANS_PER_SECOND_SQUARED = 'Angular Acceleration:radians per second squared'

    AC_ELECTRIC_CURRENT_AMPERES_PEAK = 'AC Electric Current:amperes peak'
    AC_ELECTRIC_CURRENT_AMPERES_RMS = 'AC Electric Current:amperes RMS'

    PERCENT_PERCENT = 'Percent:percent'

    DC_ELECTRIC_CURRENT_AMPERES = 'DC Electric Current:amperes'

    FORCE_NEWTONS = 'Force:newtons'
    FORCE_MILLINEWTONS = 'Force:millinewtons'
    FORCE_POUNDS_FORCE = 'Force:pounds-force'
    FORCE_KILONEWTONS = 'Force:kilonewtons'

    TIME_SECONDS = 'Time:seconds'
    TIME_MILLISECONDS = 'Time:milliseconds'
    TIME_MICROSECONDS = 'Time:microseconds'

    TORQUE_NEWTON_METRES = 'Torque:newton metres'
    TORQUE_NEWTON_CENTIMETRES = 'Torque:newton centimetres'
    TORQUE_POUND_FORCE_FEET = 'Torque:pound-force-feet'
    TORQUE_OUNCE_FORCE_INCHES = 'Torque:ounce-force-inches'

    INERTIA_GRAMS = 'Inertia:grams'
    INERTIA_KILOGRAMS = 'Inertia:kilograms'
    INERTIA_MILLIGRAMS = 'Inertia:milligrams'
    INERTIA_POUNDS = 'Inertia:pounds'
    INERTIA_OUNCES = 'Inertia:ounces'

    ROTATIONAL_INERTIA_GRAM_SQUARE_METRE = 'Rotational Inertia:gram-square metre'
    ROTATIONAL_INERTIA_KILOGRAM_SQUARE_METRE = 'Rotational Inertia:kilogram-square metre'
    ROTATIONAL_INERTIA_POUND_SQUARE_FEET = 'Rotational Inertia:pound-square-feet'
    ROTATIONAL_INERTIA_GRAM_SQUARE_MILLIMETRE = 'Rotational Inertia:gram-square millimetre'

    FORCE_CONSTANT_NEWTONS_PER_AMP = 'Force Constant:newtons per amp'
    FORCE_CONSTANT_MILLINEWTONS_PER_AMP = 'Force Constant:millinewtons per amp'
    FORCE_CONSTANT_KILONEWTONS_PER_AMP = 'Force Constant:kilonewtons per amp'
    FORCE_CONSTANT_POUNDS_FORCE_PER_AMP = 'Force Constant:pounds-force per amp'

    TORQUE_CONSTANT_NEWTON_METRES_PER_AMP = 'Torque Constant:newton metres per amp'
    TORQUE_CONSTANT_MILLINEWTON_METRES_PER_AMP = 'Torque Constant:millinewton metres per amp'
    TORQUE_CONSTANT_KILONEWTON_METRES_PER_AMP = 'Torque Constant:kilonewton metres per amp'
    TORQUE_CONSTANT_POUND_FORCE_FEET_PER_AMP = 'Torque Constant:pound-force-feet per amp'

    VOLTAGE_VOLTS = 'Voltage:volts'
    VOLTAGE_MILLIVOLTS = 'Voltage:millivolts'
    VOLTAGE_MICROVOLTS = 'Voltage:microvolts'

    CURRENT_CONTROLLER_PROPORTIONAL_GAIN_VOLTS_PER_AMP = 'Current Controller Proportional Gain:volts per amp'
    CURRENT_CONTROLLER_PROPORTIONAL_GAIN_MILLIVOLTS_PER_AMP = 'Current Controller Proportional Gain:millivolts per amp'
    CURRENT_CONTROLLER_PROPORTIONAL_GAIN_MICROVOLTS_PER_AMP = 'Current Controller Proportional Gain:microvolts per amp'

    CURRENT_CONTROLLER_INTEGRAL_GAIN_VOLTS_PER_AMP_PER_SECOND = 'Current Controller Integral Gain:volts per amp per second'
    CURRENT_CONTROLLER_INTEGRAL_GAIN_MILLIVOLTS_PER_AMP_PER_SECOND = 'Current Controller Integral Gain:millivolts per amp per second'
    CURRENT_CONTROLLER_INTEGRAL_GAIN_MICROVOLTS_PER_AMP_PER_SECOND = 'Current Controller Integral Gain:microvolts per amp per second'

    CURRENT_CONTROLLER_DERIVATIVE_GAIN_VOLTS_SECOND_PER_AMP = 'Current Controller Derivative Gain:volts second per amp'
    CURRENT_CONTROLLER_DERIVATIVE_GAIN_MILLIVOLTS_SECOND_PER_AMP = 'Current Controller Derivative Gain:millivolts second per amp'
    CURRENT_CONTROLLER_DERIVATIVE_GAIN_MICROVOLTS_SECOND_PER_AMP = 'Current Controller Derivative Gain:microvolts second per amp'

    RESISTANCE_KILOOHMS = 'Resistance:kiloohms'
    RESISTANCE_OHMS = 'Resistance:ohms'
    RESISTANCE_MILLIOHMS = 'Resistance:milliohms'
    RESISTANCE_MICROOHMS = 'Resistance:microohms'
    RESISTANCE_NANOOHMS = 'Resistance:nanoohms'

    INDUCTANCE_HENRIES = 'Inductance:henries'
    INDUCTANCE_MILLIHENRIES = 'Inductance:millihenries'
    INDUCTANCE_MICROHENRIES = 'Inductance:microhenries'
    INDUCTANCE_NANOHENRIES = 'Inductance:nanohenries'

    VOLTAGE_CONSTANT_VOLT_SECONDS_PER_RADIAN = 'Voltage Constant:volt seconds per radian'
    VOLTAGE_CONSTANT_MILLIVOLT_SECONDS_PER_RADIAN = 'Voltage Constant:millivolt seconds per radian'
    VOLTAGE_CONSTANT_MICROVOLT_SECONDS_PER_RADIAN = 'Voltage Constant:microvolt seconds per radian'

    ABSOLUTE_TEMPERATURE_DEGREES_CELSIUS = 'Absolute Temperature:degrees Celsius'
    ABSOLUTE_TEMPERATURE_KELVINS = 'Absolute Temperature:kelvins'
    ABSOLUTE_TEMPERATURE_DEGREES_FAHRENHEIT = 'Absolute Temperature:degrees Fahrenheit'
    ABSOLUTE_TEMPERATURE_DEGREES_RANKINE = 'Absolute Temperature:degrees Rankine'

    RELATIVE_TEMPERATURE_DEGREES_CELSIUS = 'Relative Temperature:degrees Celsius'
    RELATIVE_TEMPERATURE_KELVINS = 'Relative Temperature:kelvins'
    RELATIVE_TEMPERATURE_DEGREES_FAHRENHEIT = 'Relative Temperature:degrees Fahrenheit'
    RELATIVE_TEMPERATURE_DEGREES_RANKINE = 'Relative Temperature:degrees Rankine'

    FREQUENCY_GIGAHERTZ = 'Frequency:gigahertz'
    FREQUENCY_MEGAHERTZ = 'Frequency:megahertz'
    FREQUENCY_KILOHERTZ = 'Frequency:kilohertz'
    FREQUENCY_HERTZ = 'Frequency:hertz'
    FREQUENCY_MILLIHERTZ = 'Frequency:millihertz'
    FREQUENCY_MICROHERTZ = 'Frequency:microhertz'
    FREQUENCY_NANOHERTZ = 'Frequency:nanohertz'


UnitsAndLiterals = Union[Units, Literal["m", "cm", "mm", "µm", "um", "μm", "nm", "in", "m/s", "cm/s", "mm/s", "µm/s", "um/s", "μm/s", "nm/s", "in/s", "m/s²", "m/s^2", "cm/s²", "cm/s^2", "mm/s²", "mm/s^2", "µm/s²", "um/s^2", "μm/s²", "nm/s²", "nm/s^2", "in/s²", "in/s^2", "°", "deg", "rad", "°/s", "deg/s", "rad/s", "°/s²", "deg/s^2", "r/s²", "r/s^2", "rad/s²", "rad/s^2", "%", "s", "ms", "µs", "us", "μs", "GHz", "MHz", "kHz", "Hz", "mHz", "µHz", "uHz", "μHz", "nHz"]]
LengthUnits = Union[Units, Literal["m", "cm", "mm", "µm", "um", "μm", "nm", "in", "°", "deg", "rad"]]
VelocityUnits = Union[Units, Literal["m/s", "cm/s", "mm/s", "µm/s", "um/s", "μm/s", "nm/s", "in/s", "°/s", "deg/s", "rad/s"]]
AccelerationUnits = Union[Units, Literal["m/s²", "m/s^2", "cm/s²", "cm/s^2", "mm/s²", "mm/s^2", "µm/s²", "um/s^2", "μm/s²", "nm/s²", "nm/s^2", "in/s²", "in/s^2", "°/s²", "deg/s^2", "r/s²", "r/s^2", "rad/s²", "rad/s^2"]]
TimeUnits = Union[Units, Literal["s", "ms", "µs", "us", "μs"]]
FrequencyUnits = Union[Units, Literal["GHz", "MHz", "kHz", "Hz", "mHz", "µHz", "uHz", "μHz", "nHz"]]

LITERALS_TO_UNITS = {
    "m": Units.LENGTH_METRES,
    "cm": Units.LENGTH_CENTIMETRES,
    "mm": Units.LENGTH_MILLIMETRES,
    "µm": Units.LENGTH_MICROMETRES,
    "um": Units.LENGTH_MICROMETRES,
    "μm": Units.LENGTH_MICROMETRES,
    "nm": Units.LENGTH_NANOMETRES,
    "in": Units.LENGTH_INCHES,
    "m/s": Units.VELOCITY_METRES_PER_SECOND,
    "cm/s": Units.VELOCITY_CENTIMETRES_PER_SECOND,
    "mm/s": Units.VELOCITY_MILLIMETRES_PER_SECOND,
    "µm/s": Units.VELOCITY_MICROMETRES_PER_SECOND,
    "um/s": Units.VELOCITY_MICROMETRES_PER_SECOND,
    "μm/s": Units.VELOCITY_MICROMETRES_PER_SECOND,
    "nm/s": Units.VELOCITY_NANOMETRES_PER_SECOND,
    "in/s": Units.VELOCITY_INCHES_PER_SECOND,
    "m/s²": Units.ACCELERATION_METRES_PER_SECOND_SQUARED,
    "m/s^2": Units.ACCELERATION_METRES_PER_SECOND_SQUARED,
    "cm/s²": Units.ACCELERATION_CENTIMETRES_PER_SECOND_SQUARED,
    "cm/s^2": Units.ACCELERATION_CENTIMETRES_PER_SECOND_SQUARED,
    "mm/s²": Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED,
    "mm/s^2": Units.ACCELERATION_MILLIMETRES_PER_SECOND_SQUARED,
    "µm/s²": Units.ACCELERATION_MICROMETRES_PER_SECOND_SQUARED,
    "um/s^2": Units.ACCELERATION_MICROMETRES_PER_SECOND_SQUARED,
    "μm/s²": Units.ACCELERATION_MICROMETRES_PER_SECOND_SQUARED,
    "nm/s²": Units.ACCELERATION_NANOMETRES_PER_SECOND_SQUARED,
    "nm/s^2": Units.ACCELERATION_NANOMETRES_PER_SECOND_SQUARED,
    "in/s²": Units.ACCELERATION_INCHES_PER_SECOND_SQUARED,
    "in/s^2": Units.ACCELERATION_INCHES_PER_SECOND_SQUARED,
    "°": Units.ANGLE_DEGREES,
    "deg": Units.ANGLE_DEGREES,
    "rad": Units.ANGLE_RADIANS,
    "°/s": Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
    "deg/s": Units.ANGULAR_VELOCITY_DEGREES_PER_SECOND,
    "rad/s": Units.ANGULAR_VELOCITY_RADIANS_PER_SECOND,
    "°/s²": Units.ANGULAR_ACCELERATION_DEGREES_PER_SECOND_SQUARED,
    "deg/s^2": Units.ANGULAR_ACCELERATION_DEGREES_PER_SECOND_SQUARED,
    "r/s²": Units.ANGULAR_ACCELERATION_RADIANS_PER_SECOND_SQUARED,
    "r/s^2": Units.ANGULAR_ACCELERATION_RADIANS_PER_SECOND_SQUARED,
    "rad/s²": Units.ANGULAR_ACCELERATION_RADIANS_PER_SECOND_SQUARED,
    "rad/s^2": Units.ANGULAR_ACCELERATION_RADIANS_PER_SECOND_SQUARED,
    "%": Units.PERCENT_PERCENT,
    "s": Units.TIME_SECONDS,
    "ms": Units.TIME_MILLISECONDS,
    "µs": Units.TIME_MICROSECONDS,
    "us": Units.TIME_MICROSECONDS,
    "μs": Units.TIME_MICROSECONDS,
    "GHz": Units.FREQUENCY_GIGAHERTZ,
    "MHz": Units.FREQUENCY_MEGAHERTZ,
    "kHz": Units.FREQUENCY_KILOHERTZ,
    "Hz": Units.FREQUENCY_HERTZ,
    "mHz": Units.FREQUENCY_MILLIHERTZ,
    "µHz": Units.FREQUENCY_MICROHERTZ,
    "uHz": Units.FREQUENCY_MICROHERTZ,
    "μHz": Units.FREQUENCY_MICROHERTZ,
    "nHz": Units.FREQUENCY_NANOHERTZ,
}


def units_from_literals(units: UnitsAndLiterals) -> Units:
    if isinstance(units, Units):
        return units

    converted = LITERALS_TO_UNITS.get(units)
    if converted is None:
        raise ValueError(f"Invalid units: {units}")

    return converted
