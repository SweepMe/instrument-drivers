"""
LJM library constants.
"""

from typing import NamedTuple

# DATA types
DATA_TYPES = {"UINT16": 0, "UINT32": 1, "INT32": 2, "FLOAT32": 3}

# Device types:
DEVICE_TYPES_CODES = {0: "ANY", 4: "T4", 7: "T7", 200: "DIGIT", 84: "TSERIES"}
DEVICE_TYPES_TEXT = {"dtANY": "ANY", "dtT4": "T4", "dtT7": "T7"}
# Connection types:
CONNECTION_TYPES_CODES = {
    0: 'ANY',
    1: 'USB',
    2: 'TCP',
    3: 'ETHERNET',
    4: 'WIFI',
    5: 'NETWORK_UDP',
    6: 'ETHERNET_UDP',
    7: 'WIFI_UDP',
    8: 'NETWORK_ANY',
    9: 'ETHERNET_ANY',
    10: 'WIFI_ANY',
    11: 'ANY_UDP'
}
CONNECTION_TYPES = {
    "ctANY": 0,
    "ctANY_TCP": "ctANY",
    "ctUSB": 1,
    "ctTCP": 2,
    "ctNETWORK_TCP": "ctTCP",
    "ctETHERNET": 3,
    "ctETHERNET_TCP": "ctETHERNET",
    "ctWIFI": 4,
    "ctWIFI_TCP": "ctWIFI",
    "ctANY_UDP": 11,
    "ctNETWORK_UDP": 5,
    "ctETHERNET_UDP": 6,
    "ctWIFI_UDP": 7,
    "ctNETWORK_ANY": 8,
    "ctETHERNET_ANY": 9,
    "ctWIFI_ANY": 10,
}

# PIN NAMES
ALL_PIN_NAMES = {
    "T4": [
        "AIN0", "AIN1", 'CIO0', 'CIO1', 'CIO2', 'CIO3', 'EIO0', 'EIO1', 'EIO2', 'EIO3', 'EIO4',
        'EIO5', 'EIO6', 'EIO7', 'FIO4', 'FIO5', 'FIO6', "FIO7", "DAC0", "DAC1"
    ] + [f"DIO{i}" for i in range(4, 20)],
    "T7": [
        'AIN0', 'AIN1', 'AIN2', 'AIN3', 'AIN4', 'AIN5', 'AIN6', 'AIN7', 'AIN8', 'AIN9', 'AIN10',
        'AIN11', 'AIN12', 'AIN13'
        'CIO0', 'CIO1', 'CIO2', 'CIO3', 'EIO0', 'EIO1', 'EIO2', 'EIO3', 'EIO4', 'EIO5', 'EIO6',
        'EIO7', 'FIO0', 'FIO1', 'FIO2', 'FIO3', 'FIO4', 'FIO5', 'FIO6', "FIO7", "DAC0", "DAC1",
        "MIO0", "MIO1", "MIO2", "10uA", "200uA"
    ] + [f"DIO{i}" for i in range(0, 23)],
}

COUNTER_PINS = {
    "T4": ['CIO0', 'CIO1', 'CIO2', 'CIO3', 'DIO16', 'DIO17', 'DIO18', 'DIO19'],
    "T7": ['CIO0', 'CIO1', 'CIO2', 'CIO3', 'DIO16', 'DIO17', 'DIO18', 'DIO19']
}
CLOCK_DISABLE_FOR_COUNTER = {
    "T4": {
        'CIO0': "DIO_EF_CLOCK1_ENABLE",
        'CIO1': "DIO_EF_CLOCK2_ENABLE",
        'DIO16': "DIO_EF_CLOCK1_ENABLE",
        'DIO17': "DIO_EF_CLOCK2_ENABLE"
    },
    "T7": {
        'CIO0': "DIO_EF_CLOCK1_ENABLE",
        'CIO1': "DIO_EF_CLOCK2_ENABLE",
        'DIO16': "DIO_EF_CLOCK1_ENABLE",
        'DIO17': "DIO_EF_CLOCK2_ENABLE",
    },
}
# CIO not accepted by EF PIN set commands
EF_DIO_NAMES = {
    "T4": {
        'CIO0': 'DIO16',
        'CIO1': 'DIO17',
        'CIO2': 'DIO18',
        'CIO3': 'DIO19'
    },
    "T7": {
        'CIO0': 'DIO16',
        'CIO1': 'DIO17',
        'CIO2': 'DIO18',
        'CIO3': 'DIO19'
    }
}
DIO_PINS = {
    "T4": {
        'FIO4': 4,
        'FIO5': 5,
        'FIO6': 6,
        'FIO7': 7,
        'EIO0': 8,
        'EIO1': 9,
        'EIO2': 10,
        'EIO3': 11,
        'EIO4': 12,
        'EIO5': 13,
        'EIO6': 14,
        'EIO7': 15,
        'CIO0': 16,
        'CIO1': 17,
        'CIO2': 18,
        'CIO3': 19,
        'DIO4': 4,
        'DIO5': 5,
        'DIO6': 6,
        'DIO7': 7,
        'DIO8': 8,
        'DIO9': 9,
        'DIO10': 10,
        'DIO11': 11,
        'DIO12': 12,
        'DIO13': 13,
        'DIO14': 14,
        'DIO15': 15,
        'DIO16': 16,
        'DIO17': 17,
        'DIO18': 18,
        'DIO19': 19,
    },
    "T7": {
        'DIO0': 0,
        'DIO1': 1,
        'DIO2': 2,
        'DIO3': 3,
        'DIO4': 4,
        'DIO5': 5,
        'DIO6': 6,
        'DIO7': 7,
        'DIO8': 8,
        'DIO9': 9,
        'DIO10': 10,
        'DIO11': 11,
        'DIO12': 12,
        'DIO13': 13,
        'DIO14': 14,
        'DIO15': 15,
        'DIO16': 16,
        'DIO17': 17,
        'DIO18': 18,
        'DIO19': 19,
        'DIO20': 20,
        'DIO21': 21,
        'DIO22': 22,
        'FIO0': 0,
        'FIO1': 1,
        'FIO2': 2,
        'FIO3': 3,
        'FIO4': 4,
        'FIO5': 5,
        'FIO6': 6,
        'FIO7': 7,
        'EIO0': 8,
        'EIO1': 9,
        'EIO2': 10,
        'EIO3': 11,
        'EIO4': 12,
        'EIO5': 13,
        'EIO6': 14,
        'EIO7': 15,
        'CIO0': 16,
        'CIO1': 17,
        'CIO2': 18,
        'CIO3': 19,
        'MIO0': 20,
        'MIO1': 21,
        'MIO2': 22,
    }
}
# pins that can act as both analog inputs and digital IOs
FLEX_PINS_T4 = {
    "FIO4": 4,
    "FIO5": 5,
    "FIO6": 6,
    "FIO7": 7,
    "EIO0": 8,
    "EIO1": 9,
    "EIO2": 10,
    "EIO3": 11,
    'DIO4': 4,
    'DIO5': 5,
    'DIO6': 6,
    'DIO7': 7,
    'DIO8': 8,
    'DIO9': 9,
    'DIO10': 10,
    'DIO11': 11,
}
# {f"DIO{i}":i for i in range(4, 12)} # alternate


class ADC_EF(NamedTuple):
    index: int
    return_names: list
    units: list
    read_channels: list


ADC_EF_FUNCTIONS = {
    "None (disabled)":
    ADC_EF(index=0, return_names=[""], units=["V"], read_channels=None),
    "Offset and Slope":
    ADC_EF(index=1, return_names=["translated"], units=["V"], read_channels=["A"]),
    "Avg, Max, Min":
    ADC_EF(index=3,
           return_names=["Avg", "Max", "Min"],
           units=["V"] * 3,
           read_channels=["A", "B", "C"]),
    "Resistance":
    ADC_EF(index=4, return_names=["R", "V"], units=["Ohm", "V"], read_channels=["A", "B"]),
    "Average and Threshold":
    ADC_EF(index=5, return_names=["Avg"], units=["V"], read_channels=["B"]),
    "RMS Flex":
    ADC_EF(index=10, return_names=["RMS", "Pk2Pk"], units=["V", "V"], read_channels=["A", "B"]),
    "RMS Auto":
    ADC_EF(index=11, return_names=["RMS", "Pk2Pk"], units=["V", "V"], read_channels=["A", "B"]),
    "Thermocouple type E":
    ADC_EF(index=20,
           return_names=["TC T", "TC V", "CJC T"],
           units=["K", "V", "K"],
           read_channels=["A", "B", "C"]),
    "Thermocouple type J":
    ADC_EF(index=21,
           return_names=["TC T", "TC V", "CJC T"],
           units=["K", "V", "K"],
           read_channels=["A", "B", "C"]),
    "Thermocouple type K":
    ADC_EF(index=22,
           return_names=["TC T", "TC V", "CJC T"],
           units=["K", "V", "K"],
           read_channels=["A", "B", "C"]),
    "Thermocouple type R":
    ADC_EF(index=23,
           return_names=["TC T", "TC V", "CJC T"],
           units=["K", "V", "K"],
           read_channels=["A", "B", "C"]),
    "Thermocouple type T":
    ADC_EF(index=24,
           return_names=["TC T", "TC V", "CJC T"],
           units=["K", "V", "K"],
           read_channels=["A", "B", "C"]),
    "Thermocouple type S":
    ADC_EF(index=25,
           return_names=["TC T", "TC V", "CJC T"],
           units=["K", "V", "K"],
           read_channels=["A", "B", "C"]),
    "Thermocouple type C":
    ADC_EF(index=30,
           return_names=["TC T", "TC V", "CJC T"],
           units=["K", "V", "K"],
           read_channels=["A", "B", "C"]),
    "RTD PT100":
    ADC_EF(index=40,
           return_names=["T", "R", "V"],
           units=["K", "Ohm", "V"],
           read_channels=["A", "B", "C"]),
    "RTD PT500":
    ADC_EF(index=41,
           return_names=["T", "R", "V"],
           units=["K", "Ohm", "V"],
           read_channels=["A", "B", "C"]),
    "RTD PT1000":
    ADC_EF(index=42,
           return_names=["T", "R", "V"],
           units=["K", "Ohm", "V"],
           read_channels=["A", "B", "C"]),
    "Thermistor (Steinhart-Hart equation)":
    ADC_EF(index=50,
           return_names=["T", "R", "V"],
           units=["K", "Ohm", "V"],
           read_channels=["A", "B", "C"]),
    "Thermistor (Beta equation)":
    ADC_EF(index=51,
           return_names=["T", "R", "V"],
           units=["K", "Ohm", "V"],
           read_channels=["A", "B", "C"]),
}
