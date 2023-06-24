__author__ = 'Christoph Staudinger'
# Python module for communication with PyroScience devices with firmware < 4.0 (FireStingO2 and Piccolo)

# This module is not officially supported by PyroScience
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY.

# Please send bug reports to cs@pyroscience.com


########################################################################################################################
# Use case 1:
# - Sensors were calibrated with the "Oxygen Logger" software
# - This module is used for readout and adjustment of environment conditions
# This is the recommended mode for most applications. The sensor constants and calibration routines are provided by
# the "Oxygen Logger". Calibration values are stored on the device and not lost upon disconnect.
#
# import os
# import time
# from FireControl import FireSting
#
# firesting = FireSting('/dev/ttyUSB0')
# firesting.channels[3].active = False
# firesting.channels[4].active = False
# firesting.channels[1].salinity = 35  # unit: g/L, e.g. seawater salinity
# firesting.channels[2].salinity = 0.1
# firesting.channels[1].temperature = 'external'  # use pt100 temperature sensor
# firesting.channels[2].temperature = 37  # set 37°C as fixed temperature
#
# interval = 5
#
# while True:
#     start = time.time()
#     result = firesting.measure()
#     for channel, data in result.items():
#         timestamp = data.pop('time')
#         fname = 'logfile{}.txt'.format(channel)
#         if not os.path.exists(fname):  # write header if file does not exist
#             with open(fname, 'w') as f:
#                 f.write('data_time,')
#                 f.write(','.join(sorted(data)))
#                 f.write('\n')
#         with open(fname, 'a') as f:
#             f.write(time.strftime('%Y-%m-%d %H:%M:%S,', time.gmtime(timestamp)))
#             f.write(','.join([str(data[k]) for k in sorted(data)]))
#             f.write('\n')
#     wait_time = start + interval - time.time()
#     if wait_time > 0:
#         time.sleep(wait_time)
########################################################################################################################


########################################################################################################################
# Use case 2:
# - Sensors are (re)calibrated with the module
#
# import os
# import time
# from FireControl import FireSting
#
# # Setup
# firesting = FireSting('/dev/ttyUSB0')
# firesting.channels[1].led_intensity = 20
# firesting.channels[2].led_intensity = 15
# firesting.channels[1].amplification = 400
# firesting.channels[2].amplification = 400
# firesting.channels[1].set_calibration_constants(.....)  # details on request
# firesting.channels[2].set_calibration_constants(.....)  # details on request
#
# # Calibration
# # Put sensors in air or air saturated water and wait for full response
# # channel 1 uses the external pt100 sensor and the internal pressure and humidity sensor for compensation
# firesting.channels[1].calibrate_air(temperature='external', pressure='internal', humidity='internal')
# # channel 2 is in a water sample at 37.02°C
# firesting.channels[2].calibrate_air(temperature=37.02, pressure=960, humidity=100)
#
# # Next Step: place sensors in nitrogen atmosphere or a sodium sulfite solution. Wait for full response.
# firesting.channels[1].calibrate_zero(temperature='external')
# firesting.channels[2].calibrate_zero(temperature='external')
#
# measurement conditions
# firesting.channels[1].salinity = 35  # e.g. seawater salinity
# firesting.channels[2].salinity = 0.1
# firesting.channels[1].temperature = 'external'
# firesting.channels[2].temperature = 37
# firesting.channels[2].humidity = 100
#
# firesting.channels[3].active = False
# firesting.channels[4].active = False
#
# interval = 5
#
# while True:
#     start = time.time()
#     result = firesting.measure()
#     for channel, data in result.items():
#         timestamp = data.pop('time')
#         fname = 'logfile{}.txt'.format(channel)
#         if not os.path.exists(fname):  # write header if file does not exist
#             with open(fname, 'w') as f:
#                 f.write('data_time,')
#                 f.write(','.join(sorted(data)))
#                 f.write('\n')
#         with open(fname, 'a') as f:
#             f.write(time.strftime('%Y-%m-%d %H:%M:%S,', time.gmtime(timestamp)))
#             f.write(','.join([str(data[k]) for k in sorted(data)]))
#             f.write('\n')
#     wait_time = start + interval - time.time()
#     if wait_time > 0:
#         time.sleep(wait_time)
########################################################################################################################

import serial
import time

DEFAULT_BAUD = 19200

led_intensity_dict = {0: 10, 1: 15, 2: 20, 3: 30, 4: 40, 5: 60, 6: 80, 7: 100}
amp_dict = {0: 1, 1: 4, 2: 20, 3: 40, 4: 80, 5: 200, 6: 400, 7: 800}
measure_time_dict = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16, 6: 32, 7: 64, 8: 128}

########################################################################################################################
# Register specification
########################################################################################################################
# Settings
SETTINGS_REGISTERS_310 = ['temperature', 'pressure', 'salinity', 'measure_time', 'intensity', 'amplification', '',
                          'fiberType', 'bkgdComp']
SETTINGS_REGISTERS_FACTORS_310 = {k: 1 for k in SETTINGS_REGISTERS_310}
SETTINGS_REGISTERS_FACTORS_310['temperature'] = 1000  # convert to °C
SETTINGS_REGISTERS_FACTORS_310['salinity'] = 1000  # convert to g/L
# pressure is already in mbar and needs no conversion

SETTINGS_REGISTERS = ['temperature', 'pressure', 'salinity', 'measure_time', 'intensity', 'amplification', 'frequency',
                      'crcEnable', 'writeLock']
SETTINGS_REGISTERS_FACTORS = {k: 1 for k in SETTINGS_REGISTERS}
SETTINGS_REGISTERS_FACTORS['temperature'] = 1000  # convert to °C
SETTINGS_REGISTERS_FACTORS['pressure'] = 1  # convert to mbar
SETTINGS_REGISTERS_FACTORS['salinity'] = 1000  # convert to g/L

########################################################################################################################
# Calibration
########################################################################################################################
CALIBRATION_REGISTERS_OXYGEN = ['dphi0', 'dphi100', 'temp0', 'temp100', 'pressure', 'humidity', 'f', 'm', 'calFreq',
                                'tt', 'kt', 'bkgdAmpl', 'bkgdDphi', 'useKsv', 'ksv', 'ft', 'mt', 'tempOffset',
                                'percentO2']
# convert to °, °C, mbar, %RH, mV, %O2
CALIBRATION_REGISTERS_OXYGEN_FACTORS_310 = {k: 1000 for k in CALIBRATION_REGISTERS_OXYGEN}
CALIBRATION_REGISTERS_OXYGEN_FACTORS_310['pressure'] = 1
CALIBRATION_REGISTERS_OXYGEN_FACTORS_310['humidity'] = 1
CALIBRATION_REGISTERS_OXYGEN_FACTORS_310['calFreq'] = 1
CALIBRATION_REGISTERS_OXYGEN_FACTORS_310['tt'] = 1e5
CALIBRATION_REGISTERS_OXYGEN_FACTORS_310['kt'] = 1e5
CALIBRATION_REGISTERS_OXYGEN_FACTORS_310['useKsv'] = 1
CALIBRATION_REGISTERS_OXYGEN_FACTORS_310['ksv'] = 1e6
CALIBRATION_REGISTERS_OXYGEN_FACTORS_310['ft'] = 1e6
CALIBRATION_REGISTERS_OXYGEN_FACTORS_310['mt'] = 1e6
CALIBRATION_REGISTERS_OXYGEN_FACTORS = CALIBRATION_REGISTERS_OXYGEN_FACTORS_310.copy()
CALIBRATION_REGISTERS_OXYGEN_FACTORS['pressure'] = 1000
CALIBRATION_REGISTERS_OXYGEN_FACTORS['humidity'] = 1000

########################################################################################################################
# Results
########################################################################################################################
RESULT_REGISTERS = ['status', 'dphi', 'umolar', 'mbar', 'airSat', 'tempSample', 'tempCase', 'signalIntensity',
                    'ambientLight', 'pressure', 'humidity', 'resistorTemp', 'percentO2']
RESULT_REGISTERS_FACTORS = {k: 1000 for k in RESULT_REGISTERS}  # convert to °, °C, mbar, %RH, mV, %O2
RESULT_REGISTERS_FACTORS['status'] = 1


class PyroIO:
    def __init__(self, port, baud=None):
        """ Basic input/output class of all Fire* devices

        This class handles all device and firmware specific functions.
        Queried values are returned as useful types and can be passed to this class in
        meaningful values. If a function is not available for some reason, either a workaround is used
        (e.g. background measurement) or NotImplementedError is raised
        """
        self.port = port
        self.connection = None
        self.available = {  # available functionality of the device, can be checked before a command is sent
            'optical': False,  # measure function setting of frequency, led, etc
            'pressure': False,  # measurement of pressure
            'humidity': False,  # measurement of humidity
            'analog in': False,
            'case temperature': False,  # measurement of case temperature
            'oxygen': False,
            'change_baud': False}
        self.dev_id = None  # device type
        self.nof_channels = 0  # number of channels
        self.firmware = 0  # firmware version 300 = 3.00
        self.connect(baud=baud)

    def __del__(self):
        self.disconnect()

    ####################################################################################################################
    # Connect / Disconnect Functions
    ####################################################################################################################
    def connect(self, baud=None):
        baudlist = [19200, 38400, 115200, 230400, 460800, 921600]
        # if a baudrate is passed try it first
        if baud:
            baudlist.insert(0, baud)

        # try all baudrates till a connection is established
        for b in baudlist:
            try:
                self.connection = serial.Serial(port=self.port, baudrate=b, timeout=1)
                self.dev_id, self.nof_channels, self.firmware, self.available = self.get_device_information()
                break
            except:
                self.connection.close()
                continue

        if not self.connection:
            raise ConnectionError()
        # increase connection timeout
        self.connection.timeout = 5

    def disconnect(self):
        if self.connected:
            self.connection.close()

    @property
    def connected(self):
        try:
            return self.connection.isOpen()
        except AttributeError:
            return False

    ####################################################################################################################
    # Primitive IO Functions
    ####################################################################################################################
    def send(self, msg, repeat_on_fail=True):
        """ Send a command to the device and receive (and check the result).

        The echo and if available the crc checksum are controlled. If the transmission fails the command is
        repeated by default (up to 5 times)

        :param msg: the command
        :param repeat_on_fail: repeat the command if transmission is not successful (default: True)
        """
        if not self.connected:
            raise ConnectionError('PyroScience device on port {} lost connection.'.format(self.port))
        for i in range(1, 5):
            success = False
            self.connection.read(self.connection.inWaiting())  # clear buffer
            self.write(msg)
            try:
                answ = self.read()[:-1]  # cut away \r
                success = True
            except ConnectionError:
                print("Communication failure with PyroScience Dev on port {}. Sent: {}. "
                      "Got no return.".format(self.port, msg))
                answ = ''

            # check the echo
            if success:
                echo, answ = answ[:len(msg)], answ[len(msg) + 1:]
                if not echo == msg[:len(msg)]:
                    print('Communication Failure with PyroScience Dev on port {}.'
                          'Sent: {} got: {}. Repeating command!'.format(self.port, msg, echo))
                    success = False

            if success:
                return answ
            elif repeat_on_fail:
                time.sleep(0.1)
                self.connection.read(self.connection.inWaiting())  # clear buffer
                self.write('#VERS')
                time.sleep(0.2)
                print('Checking Connection on port: ', self.port, 'Sent: #VERS. Return:', self.read())
            else:
                break
        raise ConnectionError('Could not send command "{}" successfully'.format(msg))

    def write(self, msg):
        """ write a command to the device

        Users should usually use the more high-level "send" function

        :param msg: command to send
        """
        self.connection.write(bytes('{}\r'.format(msg), 'utf8'))

    def read(self):
        """ receive the response of the device

        Users should usually use the more high-level "send" function

        :return: response of the device without any processing and checking
        """
        answ = ''
        while True:
            ret = self.connection.read(1).decode('latin1')
            answ += ret
            if ret == '\r':
                break
            elif ret == '':
                raise ConnectionError()
        return answ

    ####################################################################################################################
    # Device-wide functions (not channel specific)
    ####################################################################################################################
    def get_device_information(self):
        """ Collect information of the device (nof channels, firmware, etc) and return it

        This function is called during the connecting of the device and finds out what type of device it is
        and what it can do.
        """
        ret = [int(i) for i in self.get_version_info().split(':')[0].split()]  # cut off potential crc check
        available = {
            'optical': False,  # measure function setting of frequency, led, etc
            'temperature': False,  # measurement of sample temperature, offset cal of T sensor
            'pressure': False,  # measurement of pressure
            'humidity': False,  # measurement of humidity
            'analog in': False,
            'case temperature': False,  # measurement of case temperature
            'oxygen': False}
        if len(ret) == 3:  # FireSting  = workaround for old firmware
            dev_id, chans, firm = ret
            types = 0x01 | 0x02 | 0x04 | 0x08  # FireSting can measure oxygen, temperature, pressure and humidity
        else:
            dev_id, chans, firm, types = ret[:4]  # some special devices (xprize?) send more than 4 values -> ignore

        # parse sensor types
        available['optical'] = True
        if types & 0x01:
            available['oxygen'] = True
        if types & 0x02:
            available['temperature'] = True
        if types & 0x04:
            available['pressure'] = True
        if types & 0x08:
            available['humidity'] = True
        if types & 0x0F:
            available['analog in'] = True

        # parse id
        if dev_id not in (0, 1, 3, 4, 8):
            raise NotImplementedError('Unknown device: ' + self.get_version_info())

        return dev_id, chans, firm, available

    def read_unique_id(self):
        """ Read the unique id number of the device
        """
        if self.firmware < 322:
            raise NotImplementedError('Not available < Firmware 3.20')
        return self.send('#IDNR')

    def blink(self):
        """ Flash the logo of the device
        """
        self.send('#LOGO')

    ####################################################################################################################
    # Calibration Functions
    ####################################################################################################################
    def calibrate_zero(self, channel: int, temperature: float, save=True):
        """ Calibrate zero command.

        Calibration can be performed in nitrogen or in deoxigenated water (e.g. sulfite). Sensor must be equilibrated
        with the calibration standard before this command is called. Measures the phase angle 16 times, takes the
        average and stores the result in the dphi0 register.

        :param channel: channel to calibrate
        :param temperature: temperature of sample during calibration (°C)
        :param save: store to flash memory
        """
        if self.dev_id == 0 and self.firmware <= 318:
            return self._calibrate_zero_firesting(channel, temperature, save=save)
        # measure 16 times and take average and store
        self.send('CLO {} {}'.format(channel, int(temperature * CALIBRATION_REGISTERS_OXYGEN_FACTORS['temp0'])))
        if save:
            self.save_to_flash()

    def calibrate_air(self, channel: int, temperature: float, pressure: float, humidity: float, save=True):
        """ Calibrate air command

        Calibration can be performed in air or in air saturated water (100%RH). Sensor must be equilibrated with the
        calibration standard before this command is called. Measures the phase angle 16 times, takes the average and
        stores the result in the dphi100 register.

        :param channel: channel to calibrate
        :param temperature: temperature of sample during calibration (°C)
        :param pressure: ambient air pressure during calibration (mbar)
        :param humidity: relative humidity during calibration (100% if in water) (%RH)
        :param save: store to flash memory
        """
        if self.dev_id == 0 and self.firmware <= 318:
            return self._calibrate_air_firesting(channel, temperature, pressure, humidity, save=save)
        self.send('CHI {} {} {}'.format(channel, int(temperature * CALIBRATION_REGISTERS_OXYGEN_FACTORS['temp100']),
                                        int(pressure * CALIBRATION_REGISTERS_OXYGEN_FACTORS['pressure']),
                                        int(humidity * CALIBRATION_REGISTERS_OXYGEN_FACTORS['humidity'])))
        if save:
            self.save_to_flash()

    def _calibrate_zero_firesting(self, channel: int, temperature: float, save=True):
        """ Calibrate zero command for FireSting

        Calibration can be performed in Nitrogen or in deoxigenated water (e.g. sulfite). Sensor must be equilibrated
        with the calibration standard before this command is called. Measures the phase angle 16 times, takes the
        average and stores the result in the dphi0 register.

        :param channel: channel to calibrate
        :param temperature: temperature of sample during calibration
        :param save: store to flash memory
        """
        self.write_calibration_register_by_name(1, 'temp0', temperature)
        self.send('CLO {} 16 0'.format(channel))  # measure 16 times and take average and store
        if save:
            self.save_to_flash()

    def _calibrate_air_firesting(self, channel: int, temperature: float, pressure: float, humidity: float, save=True):
        """ Calibrate air command for FireSting

        Calibration can be performed in Air or in air saturated water (100%RH). Sensor must be equilibrated with the
        calibration standard before this command is called. Measures the phase angle 16 times, takes the average and
        stores the result in the dphi100 register.

        :param channel: channel to calibrate
        :param temperature: temperature of sample during calibration
        :param pressure: ambient air pressure during calibration
        :param humidity: relative humidity during calibration (100% if in water)
        :param save: store to flash memory
        """
        self.write_calibration_register_by_name(1, 'temp100', temperature)
        self.write_calibration_register_by_name(1, 'pressure', pressure)
        self.write_calibration_register_by_name(1, 'humidity', humidity)
        self.send('CHI {} 16 0'.format(channel))  # measure 16 times and take average
        if save:
            self.save_to_flash()

    ####################################################################################################################
    # Measure Functions
    ####################################################################################################################
    def trigger_oxygen_measurement(self, channel: int):
        """ Triggers an optical measurement. Results are stored in device registers
        """
        if channel > self.nof_channels:
            raise ValueError('Invalid Channel')
        self.send('MSR {}'.format(channel))

    def trigger_temperature_measurement(self, channel: int):
        """ Triggers a temperature measurement. Results are stored in device registers
        """
        if channel > self.nof_channels:
            raise ValueError('Invalid Channel')
        if not self.available['temperature']:
            print('Warning: temperature measurement not available. Skipping.')
            return
        self.send('TMP {}'.format(channel))

    def trigger_pressure_measurement(self, channel: int):
        """ Triggers a environment pressure measurement. Results are stored in device registers
        """
        if channel > self.nof_channels:
            raise ValueError('Invalid Channel')
        if not self.available['pressure']:
            print('Warning: pressure measurement not available. Skipping.')
            return
        self.send('PRS {}'.format(channel))

    def trigger_humidity_measurement(self, channel: int):
        """ Triggers a humidity measurement. Results are stored in device registers
        """
        if channel > self.nof_channels:
            raise ValueError('Invalid Channel')
        if not self.available['humidity']:
            print('Warning: humidity measurement not available. Skipping.')
            return
        self.send('HUM {}'.format(channel))

    def get_version_info(self):
        """ get information about the device
        """
        return self.send('#VERS')

    def clear_background(self, channel: int, save: bool = True):
        """ Clear the background registers

        :param channel: Channel to clear
        :param save: save to permanent flash storage
        """
        if self.firmware > 320:
            self.send('BCL {}'.format(channel))
        else:
            self.write_bkgd_amp(channel=channel, value=0, save=False)
            self.write_bkgd_dphi(channel=channel, value=0, save=False)
        if save:
            self.save_to_flash()

    def measure_background(self, channel: int, save: bool = True):
        """ Measure the current phase shift and amplitude and store it in the background registers.

        All following measurements are corrected by these background values.
        Note: the registers expect the background values with 10% LED intensity and 400x amplification!
        These values are scaled when the measurement settings are different or changed. After a change of led intensity
        no new measurement of background is necessary.
        """
        if self.firmware > 320:
            self.send('BGC {}'.format(channel))
        else:
            # measure current amplitude and phase
            current_settings = self.read_all_settings_registers(channel)
            self.write_intensity_setting(channel, 10)
            self.write_amplification_setting(channel, 400)
            amp = 0
            phase = 0
            for i in range(16):
                self.trigger_oxygen_measurement(channel)
                amp += self.read_signal_intensity(channel)
                phase += self.read_dphi(channel)
            # calculate mean
            amp /= 16
            phase /= 16
            self.write_bkgd_amp(channel, amp, save=False)
            self.write_bkgd_dphi(channel, phase)
            self.write_intensity_setting(channel, current_settings['intensity'])
            self.write_amplification_setting(channel, current_settings['amplification'])
        if save:
            self.save_to_flash()

    ####################################################################################################################
    # basic read/write register
    ####################################################################################################################
    def read_register(self, channel, reg_type, addr) -> str:
        """ read a single register

        :param channel: channel to read from
        :param reg_type: register type (0: settings, 1: calibration, 3: results)
        :param addr: address in the register
        """
        return self.send('RMR {} {} {} 1'.format(channel, reg_type, addr))

    def read_multiple_registers(self, channel, reg_type, addr, number):
        """ read multiple registers. Results are separated with whitespace.

        :param channel: channel to read from
        :param reg_type: register type (0: settings, 1: calibration, 3: results)
        :param addr: start address in the registers
        :param number: number of registers to read
        """
        return self.send('RMR {} {} {} {}'.format(channel, reg_type, addr, number))

    def write_register(self, channel, reg_type, addr, value: int):
        """ write a single register

        :param channel: channel to write to
        :param reg_type: register type (0: settings, 1: calibration, 3: results)
        :param addr: address in the register
        :param value: value to write into the register
        """
        if not isinstance(value, int):
            raise TypeError('Invalid type: {} for register. Must be int.'.format(reg_type(value)))
        return self.send('WTM {} {} {} 1 {}'.format(channel, reg_type, addr, value))

    def save_to_flash(self, channel: int = 1):
        """ saves the current settings etc. to the permanent flash storage

        """
        self.send('SVS {}'.format(channel))

    def load_from_flash(self, channel: int = 1):
        """ loads the settings, etc. from the flash storage

        all non-saved changes are lost
        """
        self.send('LDS {}'.format(channel))

    ####################################################################################################################
    # read settings registers
    ####################################################################################################################
    def read_all_settings_registers(self, channel) -> dict:
        """ Read all settings registers of the channel and returns the parsed results as a dict

        The contents of the returned dict depend on the firmware version of the device, but the following entries can
        always be expected:
            name        unit
            temp        [°C]
            pressure    [mbar]
            salinity    [g/L]
            intensity   [%]
            amp         []
            frequency   [Hz]
            measure_time    [ms]

        :param channel: channel to read the settings from
        :return:
        """
        if self.firmware >= 320:
            settings = self.read_multiple_registers(channel, 0, 0, 9).strip()
        else:  # 310 and below
            settings = self.read_multiple_registers(channel, 0, 0, 6).strip()

        # parsing
        settings = settings.strip().split()
        if self.firmware >= 320:
            registers, factors = SETTINGS_REGISTERS, SETTINGS_REGISTERS_FACTORS
        else:
            registers, factors = SETTINGS_REGISTERS_310, SETTINGS_REGISTERS_FACTORS_310
        res = dict()
        for value, name in zip(settings, registers):
            if not name:
                continue
            factor = factors[name]
            if factor == 1:
                res[name] = int(value)
            else:
                res[name] = int(value) / factor

        # parse coded values
        res['intensity'] = led_intensity_dict[res['intensity']]
        res['amplification'] = amp_dict[res['amplification']]
        if self.firmware >= 320:
            res['measure_time'] = 2**(res['measure_time']-1)
        if self.firmware <= 310:
            # frequency was stored in calibration prior to 3.20. Collect data for compatibility
            res['frequency'] = int(self.read_calibration_register(channel, 8))
        return res

    ####################################################################################################################
    # read calibration data
    ####################################################################################################################
    def read_calibration_register(self, channel, addr):
        """ read a single calibration register
        """
        return self.read_register(channel, 1, addr)

    def read_cal_register_by_name(self, channel, name) -> float:
        i = CALIBRATION_REGISTERS_OXYGEN.index(name)
        if self.firmware <= 310:
            factor = CALIBRATION_REGISTERS_OXYGEN_FACTORS_310[name]
        else:
            factor = CALIBRATION_REGISTERS_OXYGEN_FACTORS[name]
        return int(self.read_calibration_register(channel=channel, addr=i)) / factor

    def read_bkgd_amp(self, channel: int):
        return self.read_cal_register_by_name(channel, 'bkgdAmpl')

    def read_bkgd_dphi(self, channel: int):
        return self.read_cal_register_by_name(channel, 'bkgdDphi')

    def read_all_cal_registers(self, channel) -> dict:
        """ Read all calibration registers and return the parsed result as a dict

            entries of the dict:
                name        unit        description
                dphi0       [°]         phase shift at 0%O2
                dphi100     [°]         phase shift at upper calibration point
                temp0       [°C]        temperature at 0% calibration
                temp100     [°C]        temperature at upper calibration point
                pressure    [mbar]      ambient air pressure at upper calibration point
                humidity    [%RH]       relative humidity at upper calibration point (100% in water)
                f           []          sensor specific
                m           []          sensor specific
                calFreq     [Hz]        sensor specific calibration frequency
                tt          []          sensor specific
                kt          []          sensor specific
                bkgdAmpl    [mV]        Amplitude of background compensation
                bkgdDphi    [°]         Phase shift of background compensation
                percentO2   [%]         Oxygen content of upper calibration point (In air: 20.95)

        :param channel:
        :return: dictionary
        """
        # get the analyte
        registers, factors = CALIBRATION_REGISTERS_OXYGEN, CALIBRATION_REGISTERS_OXYGEN_FACTORS_310

        cal = self.read_multiple_registers(channel, 1, 0, len(registers))
        cal = cal.strip().split()
        res = dict()
        for value, name in zip(cal, registers):
            if not name:
                continue
            factor = factors[name]
            if factor == 1:
                res[name] = int(value)
            else:
                res[name] = int(value) / factor
        return res

    ####################################################################################################################
    # read results
    ####################################################################################################################
    def read_result_register(self, channel, addr) -> str:
        """ read a single result register

        :param channel: channel to read from
        :param addr: address of the register
        """
        return self.read_register(channel, 3, addr)

    def read_result_register_by_name(self, channel, name):
        """ read a single results register identified by name
        
        :param channel: channel to read from 
        :param name: name of the register. Available registers: see RESULT_REGISTERS
        """
        try:
            i = RESULT_REGISTERS.index(name)
        except ValueError:
            raise ValueError('Invalid register: "{}"! Use one of the following: {}'.format(name, RESULT_REGISTERS))
        factor = RESULT_REGISTERS_FACTORS[name]
        print('factor', factor)
        res = int(self.read_result_register(channel=channel, addr=i))
        print('res', res)
        if factor > 1:
            res /= factor
        return res

    def read_status(self, channel) -> int:
        """ read the status of the last measurement.

        :param channel: channel to read from
        status messages are encoded. Use function PyroIO.decode_status() to get human readable messages
        """
        return self.read_result_register_by_name(channel, 'status')

    def read_dphi(self, channel) -> float:
        """ read dphi of the last measurement. Unit: °

        :param channel: channel to read from
        """
        return self.read_result_register_by_name(channel, 'dphi')

    def read_sample_temperature(self, channel) -> float:
        """ read sample temperature of the last measurement. Unit °C

        :param channel: channel to read from
        """
        return self.read_result_register_by_name(channel, 'temperature')

    def read_pressure(self, channel) -> float:
        """ read ambient pressure during the last measurement. Unit: mbar

        :param channel: channel to read from
        """
        return self.read_result_register_by_name(channel, 'pressure')

    def read_signal_intensity(self, channel) -> float:
        """ read signal intensity during the last measurement. Unit: mV

        :param channel: channel to read from
        """
        return self.read_result_register_by_name(channel, 'signalIntensity')

    def read_ambient_light(self, channel) -> float:
        """ read ambient light during the last measurement. Unit: mV

        :param channel: channel to read from
        """
        return self.read_result_register_by_name(channel, 'ambientLight')

    def read_all_result_registers(self, channel: int) -> dict:
        """ Get all values in the result registers

        No measurement is triggered. The results from the last measurement are returned.
        the values are returned in a dict and parsed into useful types. Units: °, µmol/L, mbar, %air sat, °C, mV,
        %RH, Ohm, %O2

        :param channel: channel

        :return dict of results:
        """
        return self.parse_result_registers(self.read_multiple_registers(channel, 3, 0, 13))

    @staticmethod
    def parse_result_registers(result: str):
        """ Parse the result string (the full results register of a channel

        returned units: °, µmol/L, mbar, %air sat, °C, mV, %RH, Ohm, %O2

        :param result: result register 0-13 separated by spaces
        :return dict with named results
        """
        results = result.strip().split()
        res = dict()

        for value, name in zip(results, RESULT_REGISTERS):
            if not name:
                continue
            factor = RESULT_REGISTERS_FACTORS[name]
            if factor == 1:
                res[name] = int(value)
            else:
                res[name] = int(value) / factor
        return res

    ####################################################################################################################
    # write settings register
    ####################################################################################################################
    def _write_setting_register(self, channel: int, addr: int, value: int, save=True):
        """ write a single settings register

        In most cases it is better to use the specific function to change measure time, frequency, etc.
        This function does not do the encoding of the human readable values!

        :param channel: channel to write to
        :param addr: address in the register
        :param value: value to write into the register
        :param save: store the change in the permanent flash memory of the device
        """
        if not isinstance(value, int):
            raise ValueError('Invalid data for settings register: {}'.format(value))
        ret = self.write_register(channel, 0, addr, value)
        if save:
            self.save_to_flash()
        return ret

    def write_temperature_setting(self, channel: int, value: float):
        """ change the temperature setting of the channel.

        The set temperature is used for temperature compensation of the sensor and to calculate temperature dependent
        derived units (umolar, %airSat)

        If the temperature is set to -300 the external temperature sensor is used for compensation

        :param channel: channel to change the temperature setting
        :param value: new temperature in °C
        """
        value1000 = int(value * 1000)
        if not -300000 <= value1000 <= 300000:
            raise ValueError('Invalid Temperature: {}. Range -300 to +300'.format(value))
        return self._write_setting_register(channel, 0, value1000)

    def write_pressure_setting(self, channel: int, value: float):
        """ change the ambient pressure setting of the channel.

        The set ambient pressure is used to calculate pressure dependent derived units (umolar, percentO2)

        If the pressure is set to -1 the internal pressure sensor is used for compensation

        :param channel: channel to change the pressure setting
        :param value: new pressure in mbar
        """
        if value == -1:
            return self._write_setting_register(channel, 1, -1)
        if not 0 <= value <= 10000:
            raise ValueError('Invalid Pressure: {}. Range 0 to 10000 (or -1)'.format(value))
        return self._write_setting_register(channel, 1, int(value * 1000))

    def write_salinity_setting(self, channel: int, value: float):
        """ change the salinity setting of the channel in g/L.

        The set salinity is used to calculate salinity dependent derived units (umolar)

        :param channel: channel to change the pressure setting
        :param value: new pressure in mbar
        """
        value1000 = int(value * 1000)
        if not 0 <= value1000 <= 10000000:
            raise ValueError('Invalid salinity: {}. Range 0 to 10000 (or -1)'.format(value))
        return self._write_setting_register(channel, 2, int(value * 1000))

    def write_measure_time_setting(self, channel, value):
        """ change the measure time of the channel.

        Valid values:
            FireSting: 1-200; unit ms
            all other devices: 1, 2, 4, 8, 16, 32, 64, 128; unit: ms

        A longer measure time reduces the noise of the measurement but leads to a higher photodamage at the sensor
        and to larger drift. Recommendations for different sensor types and applications on request.

        :param channel: channel to change the measure time
        :param value: new measure time in ms (valid: 1, 2, 4, 8, 16, 32, 64, 128)
        """
        if not isinstance(value, int):
            raise TypeError('Invalid type: {} for measure_time. Must be int (unit = ms).'.format(type(value)))
        if self.dev_id == 0:  # = FireSting does not encode measure time
            if not 1 <= value <= 200:
                raise ValueError('Invalid Value: {}. Must be 1-200!'.format(value))
            encoded = value
        else:
            if value not in (1, 2, 4, 8, 16, 32, 64, 128):
                raise ValueError('Invalid Value: {}. Must be in (1, 2, 4, 8, 16, 32, 64, 128)!'.format(value))
            encoded = {v: k for k, v in measure_time_dict.items()}[value]
        return self._write_setting_register(channel, 3, encoded)

    def write_intensity_setting(self, channel, value):
        """ change the led intensity setting of the channel.

        Valid values:
            10, 15, 20, 30, 40, 60, 80, 100

        A larger LED intensity increases the signal intensity. A signal intensity > 100mV is recommended. (signal
        changes with oxygen concentration (low oxygen -> high signal, high oxygen -> low signal)
        A too high LED intensity leads to higher photodamage at the sensor and to larger drift or can result in
        oversaturation of the detector (> 2000mV).

        :param channel: channel to change the measure time
        :param value: new led intensity time in % (valid: 10, 15, 20, 30, 40, 60, 80, 100)
        """
        try:
            value = {v: k for k, v in led_intensity_dict.items()}[value]
        except KeyError:
            raise ValueError('Invalid Intensity: {}. Valid are: {}'.format(value, led_intensity_dict.values()))
        return self._write_setting_register(channel, 4, value)

    def write_amplification_setting(self, channel, value):
        """ change the amplification setting of the channel.

        Valid values:
            1, 4, 20, 40, 80, 200, 400, 800
        It is strongly recommended to use only: 80, 200 or 400

        A larger amplification increases the signal. If the detector is oversaturated the amplification can be reduced.

        :param channel: channel to change the amplification
        :param value: new amplification (recommended:: 80, 200, 400) (valid: 1, 4, 20, 40, 80, 200, 400, 800)
        """
        try:
            value = {v: k for k, v in amp_dict.items()}[value]
        except KeyError:
            raise ValueError('Invalid Amplification: {}. Valid are: {}'.format(value, amp_dict.values()))
        if value not in range(3, 7):
            print('Amplification "{}" not in recommended region 40-400')
        return self._write_setting_register(channel, 5, value)

    def write_frequency_setting(self, channel, value, save=False):
        """ change the frequency setting of the channel.

        Valid values:
            100-20000 (default: 4000)

        :param channel: channel to change the measure time
        :param value: new modulation frequency
        :param save: store the change in the permanent flash memory of the device
        """
        if value not in range(1, 32001):
            raise ValueError('Invalid value {} for frequency setting. Must be 1-32000.'.format(value))
        if self.dev_id == 0:
            return self._write_firesting_frequency_setting(channel, value, save=save)
        else:
            return self._write_setting_register(channel, 6, value, save=save)

    def _write_firesting_frequency_setting(self, channel, value, save=False):
        """ FireStings use a different register for frequency.
        """
        if value not in range(1, 32001):
            raise ValueError('Invalid value {} for frequency setting. Must be 1-32000.'.format(value))
        return self._write_calibration_register(channel, 8, value, save)

    def write_fiber_type_setting(self, channel: int, fiber_type: int):
        """ Changes the type of connected sensor fiber

        0: 200µm fiber (orange)
        1: 400µm fiber (brown)
        2: 1mm fiber (black)

        :param channel: channel
        :param fiber_type: One of 0 (200µm), 1 (400µm), 2 (1mm)
        """
        if not self.dev_id == 0:
            raise NotImplementedError('Only available for FireStings')
        if fiber_type not in (0, 1, 2):
            raise ValueError('Invalid fiber type. Use only: 0 (orange), 1 (brown), 2 (black)')
        self._write_setting_register(channel, 7, fiber_type)

    ####################################################################################################################
    # write calibration register
    ####################################################################################################################
    def _write_calibration_register(self, channel: int, addr: int, value: int, save=False):
        """ write a single calibration register

        In most cases it is better to use the specific function to change background amplitude, etc

        :param channel: channel to write to
        :param addr: address in the register
        :param value: value to write into the register
        :param save: store the change in the permanent flash memory of the device
        """
        if not isinstance(value, int):
            raise ValueError('Invalid data for calibration register: {}'.format(value))
        self.write_register(channel, 1, addr, value)
        if save:
            self.save_to_flash()

    def write_calibration_register_by_name(self, channel, name, value: float, save=True):
        """ write to a calibration register by its name

        available are:
            dphi0, dphi100, temp0, temp100, pressure, humidity, f, m, calFreq, tt, kt, bkgdAmpl, bkgdDphi, useKsv, ksv,
            ft, mt, tempOffset, percentO2
        """
        i = CALIBRATION_REGISTERS_OXYGEN.index(name)
        if self.firmware <= 310:
            factor = CALIBRATION_REGISTERS_OXYGEN_FACTORS_310[name]
        else:
            factor = CALIBRATION_REGISTERS_OXYGEN_FACTORS[name]
        self._write_calibration_register(channel=channel, addr=i, value=int(value * factor), save=save)

    def write_bkgd_amp(self, channel: int, value: float, save=True):
        """ manually write the background amplitude

        It is usually better to use the "measure_background" or "clear_background" functions.

        :param channel: channel to write to
        :param value: new background amplitude
        :param save: save to permanent flash memory of the device
        """
        return self.write_calibration_register_by_name(channel, 'bkgdAmpl', value, save)

    def write_bkgd_dphi(self, channel: int, value: float, save=True):
        """ manually write the background phase angle

        It is usually better to use the "measure_background" or "clear_background" functions.

        :param channel: channel to write to
        :param value: new background amplitude
        :param save: save to permanent flash memory of the device
        """
        return self.write_calibration_register_by_name(channel, 'bkgdDphi', value, save)


class FireChannel:
    def __init__(self, device: PyroIO, channel: int, name: str, active=True):
        """ Represents a single optical measurement channel of a PyroScience device.

        This class is not intended for direct creation but is created by the FireSting class during construction

        It is used to manage the settings and get measurement results from a single optical measurement channel.
        important attributes are:
            name (str): name of the channel or sensor.
            active (bool): if False the channel is deactivated
            led_intensity: read or write the led intensity settings (possible: 10, 15, 20, 30, 40, 60, 80, 100)
            measure_time: read or write the measure time settings (FireSting 1-200ms,
                                                                   all others: 1, 2, 4, 8, 16, 32, 64, 128 ms)
            amplification: read or write the amplification settings (recommended: 80x, 200x, 400x)
            frequency: read or write the frequency settings (1-32000, normal range O2 sensor: 4000)

        :param device: PyroIO instance used for communication with the hardware
        :param channel: channel number
        :param name: name of this channel. Is used to identify the measurement results
        :param active: if False the device is deactivated and does not trigger measurements
        """
        self.device = device
        self.channel = channel
        self.name = name
        self.active = active
        self.settings_cache = {'intensity': None, 'measure_time': None, 'frequency': None, 'amplification': None,
                               'temperature': None, 'pressure': None, 'salinity': None}

        # default values for measurements
        self.measure_temperature_default = True
        self.measure_humidity_default = True
        self.measure_pressure_default = False
        if self.device.available['humidity']:
            self.measure_humidity_default = True
        if self.device.available['pressure']:
            self.measure_pressure_default = True

        self.refresh_settings_cache()

    def refresh_settings_cache(self):
        """ Reads all settings (led_intensity, measure_time, frequency, amplification) from the device

        The data is stored in a cache to avoid rereading this data every time
        """
        settings = self.device.read_all_settings_registers(self.channel)
        self.settings_cache = {k: v for k, v in settings.items() if k in self.settings_cache}

    @property
    def settings(self):
        """ View the settings of the channel"""
        if None in self.settings_cache.values():
            self.refresh_settings_cache()
        return {'intensity': self.led_intensity, 'measure_time': self.measure_time, 'frequency': self.frequency,
                'amplification': self.amplification, 'temperature': self.temperature, 'pressure': self.pressure,
                'salinity': self.salinity}

    @property
    def led_intensity(self):
        """ Get or set the led intensity of the channel

        Available values: 10, 15, 20, 30, 40, 60, 80, (100)
        """
        if self.settings_cache['intensity']:
            return self.settings_cache['intensity']
        else:
            self.refresh_settings_cache()
        return self.settings_cache['intensity']

    @led_intensity.setter
    def led_intensity(self, intensity):
        # invalidate settings cache. Change might fail
        self.settings_cache['intensity'] = None
        self.device.write_intensity_setting(self.channel, intensity)

    @property
    def measure_time(self):
        """ Get or set the measurement time of the channel

        FireSting: 1-200 ms
        Other devices: 1, 2, 4, 8, 16, 32, 64, 128 ms
        """
        if self.settings_cache['measure_time']:
            return self.settings_cache['measure_time']
        else:
            self.refresh_settings_cache()
        return self.settings_cache['measure_time']

    @measure_time.setter
    def measure_time(self, meas_time):  # 1-8!
        # invalidate settings cache. Change might fail
        self.settings_cache['measure_time'] = None
        self.device.write_measure_time_setting(self.channel, meas_time)

    @property
    def frequency(self):
        """ Get or set the modulation frequency of the channel

        Range: 1-32000 Hz
        Sensor specific (details on request)
        Normal range oxygen sensor: 4000Hz
        """
        if self.settings_cache['frequency']:
            return self.settings_cache['frequency']
        else:
            self.refresh_settings_cache()
        return self.settings_cache['frequency']

    @frequency.setter
    def frequency(self, frequency):  # 1- 32000
        # invalidate settings cache. Change might fail
        self.settings_cache['frequency'] = None
        self.device.write_frequency_setting(self.channel, frequency)

    @property
    def amplification(self):
        """ Get or set the amplification of the channel

        Recommended values: 80, 200, 400
        """
        if self.settings_cache['amplification']:
            return self.settings_cache['amplification']
        else:
            self.refresh_settings_cache()
        return self.settings_cache['amplification']

    @amplification.setter
    def amplification(self, amp):
        # invalidate settings cache. Change might fail
        self.settings_cache['amplification'] = None
        self.device.write_amplification_setting(self.channel, amp)

    @property
    def temperature(self):
        """ Set the sample temperature to a fixed value (unit °C)

        Used to compensate oxygen measurements and calculated temperature dependent derived units (umolar, airSat)

        If set to -300 or "external" the measurement of the external temperature sensor is used for compensation
        (if available)
        """
        if self.settings_cache['temperature'] is None:
            self.refresh_settings_cache()
        if self.settings_cache['temperature'] <= -299.999:
            return 'external'
        return self.settings_cache['temperature']

    @temperature.setter
    def temperature(self, temperature):
        if temperature == 'external':
            temperature = -300
        # invalidate settings cache. Change might fail
        self.settings_cache['temperature'] = None
        self.device.write_temperature_setting(self.channel, temperature)

    @property
    def pressure(self):
        """ Get or set the environment pressure to a fixed value (unit: mbar)

        Used to calculated pressure dependent derived units (umolar, percentO2)

        If set to -1 or "internal" the measurement of the internal pressure sensor is used for compensation
        (if available)
        """
        if self.settings_cache['pressure'] is None:
            self.refresh_settings_cache()
        if self.settings_cache['pressure'] == -1:
            return 'internal'
        return self.settings_cache['pressure']

    @pressure.setter
    def pressure(self, pressure):
        if pressure == 'internal':
            pressure = -1
        # invalidate settings cache. Change might fail
        self.settings_cache['pressure'] = None
        self.device.write_pressure_setting(self.channel, pressure)

    @property
    def salinity(self):
        """ Set the sample salinity to a fixed value (unit: g/L)

        Used to calculated salinity dependent derived units (umolar)
        """
        if self.settings_cache['salinity'] is None:
            self.refresh_settings_cache()
        return self.settings_cache['salinity']

    @salinity.setter
    def salinity(self, salinity):
        # invalidate settings cache. Change might fail
        self.settings_cache['salinity'] = None
        self.device.write_salinity_setting(self.channel, salinity)

    def calibrate_zero(self, temperature='external'):
        """ Calibrate zero value of oxygen sensor

        Calibration can be performed in nitrogen or in deoxigenated water (e.g. sulfite). Sensor must be equilibrated
        with the calibration standard before this command is called. Measures the phase angle 16 times, takes the
        average and stores the result in the dphi0 register.

        :param temperature: supply temperature in °C or use the external (PT100) temperature sensor
        """
        if temperature == 'external':
            temperature = self.measure_sample_temperature()
            if temperature is None:
                raise ValueError("External temperature measurement failed. Please connect a temperature "
                                 "sensor or supply the calibration temperature")
        try:
            temperature = float(temperature)
        except ValueError:
            raise ValueError('Invalid temperature: "{}"'.format(temperature))
        self.device.calibrate_zero(self.channel, temperature)

    def calibrate_air(self, temperature='external', pressure='internal', humidity='internal'):
        """ Calibrate air command for FireSting

        Calibration can be performed in air or in air saturated water (100%RH). Sensor must be equilibrated with the
        calibration standard before this command is called. Measures the phase angle 16 times, takes the average and
        stores the result in the dphi100 register.

        :param temperature: supply temperature in °C or use the external (PT100) temperature sensor
        :param pressure: supply pressure in mbar or use the internal pressure sensor (default)
        :param humidity: supply the relative humidity in % or use the internal humidity sensor (default)
        """
        if temperature == 'external':
            temperature = self.measure_sample_temperature()
            if temperature is None:
                raise ValueError("External temperature measurement failed. Please connect a temperature "
                                 "sensor or supply the calibration temperature")
        if pressure == 'internal':
            pressure = self.measure_pressure()
            if pressure is None:
                raise ValueError("Ambient pressure measurement failed. Please supply the ambient pressure")
        if humidity == 'water':
            humidity = 100
        elif humidity == 'internal':
            humidity = self.measure_humidity()
            if humidity is None:
                raise ValueError("Humidity measurement failed. Please supply the ambient humidity")
        try:
            temperature = float(temperature)
        except ValueError:
            raise ValueError('Invalid temperature: "{}"'.format(temperature))
        try:
            pressure = float(pressure)
        except ValueError:
            raise ValueError('Invalid pressure: "{}"'.format(pressure))
        try:
            humidity = float(humidity)
        except ValueError:
            raise ValueError('Invalid humidity: "{}"'.format(humidity))

        self.device.calibrate_air(self.channel, temperature, pressure, humidity)

    def measure(self, measure_temperature=None, measure_pressure=None, measure_humidity=None,
                decode_status: bool = False) -> dict:
        """ Trigger a measurement and return the results

        The settings during the measurement are included in this result. This is a bit verbose but makes the results
        more traceable.

        returns a dictionary with the following entries:
            name                unit    description
            time                s       seconds till the Epoch
            dPhi                °       measured phase angle
            status              -       encoded status message

            umolar              µM      concentration of oxygen in water, pressure and temperature required for
                                        calculation
            mbar                mbar    partial pressure of oxygen in air or water
            airSat              %       air saturation in water, temperature required for calculation
            percentO2           %       %O2 in the gas phase, ambient pressure required for calculation
            pressure            mbar    ambient pressure (only if device can measure air pressure)
            sample_temperature  °C      temperature of the sample (only if the device can measure temperature,
                                        "None" if no temperature sensor is connected
            humidity            %RH     percent relative humidity. (only if the device can measure humidity)

            signal_intensity    mV      signal intensity during the measurement (recommended > 100mV)
            ambient_light       mV      amount of ambient light reaching the photodetector
                                        (signal_intensity + ambient_light must be < 2000mV or the photodetector is
                                        oversaturated)
            device_temperature  °C      internal temperature of the device

            led_intensity       %       reports current led_intensity
            measure_time        ms      reports current measure_time
            amplification       x       reports current amplification
            frequency           Hz      reports current modulation frequency
            temperature_setting °C      temperature setting during measurement. If "external" the external temperature
                                        sensor is used for compensation.
            salinity_setting    g/L     salinity setting during the measurement. Used for calculation of umolar
            pressure_setting    mbar    pressure setting. If "internal" the internal pressure sensor is used for
                                        calculation of umolar and percentO2.

        :param measure_temperature: Measure temperature (both sample and device temperature!), necessary for temperature
                                    compensation, but slow. If a very fast measurement interval is required it should be
                                    deactivated.
        :param measure_pressure: Measure ambient pressure (not available on all devices)
        :param measure_humidity: Measure ambient humidity (not available on all devices)
        :param decode_status: translate the status bits to human readable massages (status becomes a list of strings)

        :return dictionary with results
        """
        if not self.active:
            return {}
        if measure_temperature is None:
            measure_temperature = self.measure_temperature_default
        if measure_pressure is None:
            measure_pressure = self.measure_pressure_default
        if measure_humidity is None:
            measure_humidity = self.measure_humidity_default

        if measure_temperature:
            self.device.trigger_temperature_measurement(self.channel)
        if measure_pressure:
            self.device.trigger_pressure_measurement(self.channel)
        if measure_humidity:
            self.device.trigger_humidity_measurement(self.channel)

        self.device.trigger_oxygen_measurement(self.channel)
        res = self.device.read_all_result_registers(self.channel)

        res_d = {
            'time': time.time(),
            'dPhi': res['dphi'],
            'umolar': res['umolar'],
            'mbar': res['mbar'],
            'airSat': res['airSat'],
            'percentO2': res['percentO2'],
            'status': res['status'],
            'signal_intensity': res['signalIntensity'],
            'ambient_light': res['ambientLight'],
            'led_intensity': self.led_intensity,
            'measure_time': self.measure_time,
            'amplification': self.amplification,
            'frequency': self.frequency,
            'device_temperature': res['tempCase'],
            'temperature_setting': self.temperature,
            'salinity_setting': self.salinity,
            'pressure_setting': self.pressure
        }

        if self.device.available['temperature']:
            res_d['sample_temperature'] = res['tempSample']
            if res_d['sample_temperature'] == -300:
                res_d['sample_temperature'] = None
        if self.device.available['pressure']:
            res_d['pressure'] = res['pressure']
        if self.device.available['humidity']:
            res_d['humidity'] = res['humidity']

        # if no sample temperature is available delete oxygen results
        if self.temperature == 'external' and res_d['sample_temperature'] is None:
            res_d['umolar'] = None
            res_d['mbar'] = None
            res_d['airSat'] = None
            res_d['percentO2'] = None
        # if no pressure is available delete pressure dependent oxygen results
        if self.pressure == 'internal' and not self.device.available['pressure']:
            res_d['umolar'] = None
            res_d['percentO2'] = None

        if decode_status:
            res_d['status'] = self.decode_status(res_d['status'])

        return res_d

    def measure_sample_temperature(self):
        """ triggers a sample temperature measurement and returns the result in °C

        """
        self.device.trigger_temperature_measurement(self.channel)
        res = self.device.read_all_result_registers(self.channel)
        t = res['tempSample']
        if t == -300:
            t = None
        return t

    def measure_pressure(self):
        """ triggers a ambient pressure measurement and returns the result in mbar

        """
        self.device.trigger_pressure_measurement(self.channel)
        res = self.device.read_all_result_registers(self.channel)
        return res['pressure']

    def measure_humidity(self):
        """ triggers a humidity measurement and returns the result in %RH

        """
        self.device.trigger_humidity_measurement(self.channel)
        res = self.device.read_all_result_registers(self.channel)
        return res['humidity']

    def get_background_data(self):
        res = dict()
        res['background_amp'] = self.device.read_bkgd_amp(self.channel)
        res['background_dphi'] = self.device.read_bkgd_dphi(self.channel)
        return res

    def get_calibration_data(self):
        """ Returns the current calibration data"""
        return self.device.read_all_cal_registers(self.channel)

    def clear_background(self):
        """ Clears the Background-Data from the device

        """
        self.device.clear_background(self.channel)

    def measure_background(self) -> (float, float):
        """ Measures the current amplitude and phase (16 times) and stores the result on the device

        Important: Only for measurements with bare-fibers. The fiber must not point on the sensor material during
        this measurement!

        This measured values are then always substracted from the measurement values
        """
        self.clear_background()
        self.device.measure_background(self.channel)
        return self.get_background_data()

    def set_background(self, amp: float, dphi: float):
        """ set background amplitude and phase
        """
        self.device.write_bkgd_amp(self.channel, amp, save=False)
        self.device.write_bkgd_dphi(self.channel, dphi)

    def blink(self):
        """ Triggers a optical measurement to identify the channel
        """
        self.device.trigger_oxygen_measurement(self.channel)

    def set_background_compensation_by_fiber_length(self, length: float):
        """ Sets the background compensation based on the fiber length. Only 1mm fibers (black)!

        optical fibers cause some background during the measurement.

        :param length: length of the fiber in meter
        """
        amp = length * 0.234 + 0.343
        self.set_background(amp, 0)

    def set_calibration_constants(self, f, m, tt, kt, ksv, ft, mt):
        """ Set the sensor specific calibration constants

        Details for the different sensor types on request.
        Or use Oxygen Logger software for setup of the measurement (=enter sensor code).
        """
        self.device.write_calibration_register_by_name(self.channel, 'f', f, save=False)
        self.device.write_calibration_register_by_name(self.channel, 'm', m, save=False)
        self.device.write_calibration_register_by_name(self.channel, 'tt', tt, save=False)
        self.device.write_calibration_register_by_name(self.channel, 'kt', kt, save=False)
        self.device.write_calibration_register_by_name(self.channel, 'ksv', ksv, save=False)
        self.device.write_calibration_register_by_name(self.channel, 'ft', ft, save=False)
        self.device.write_calibration_register_by_name(self.channel, 'mt', mt, save=True)

    @staticmethod
    def decode_status(status: int):
        """decode the status in the result register and return a list of error messages

        """
        msgs = []
        if status & 0x02:
            msgs.append('signal too low')
        if status & 0x04:
            msgs.append('Sensor or Background too high')
        if status & 0x08:
            msgs.append('Reference Signal too low')
        if status & 0x10:
            msgs.append('Reference Signal too high')
        if status & 0x20:
            msgs.append('No ext. T sensor detected')
        if len(msgs) == 0:
            msgs.append('Ok')
        if status % 0x40:
            msgs.append('init_flag')
        return msgs


class FireSting:
    def __init__(self, port, baud=None):
        """ This class provides a simple interface to control PyroScience oxygen meters

        For every (optical) channel of the device a FireChannel instance is created and stored
        in the "channels" dict.

        Settings can be changed individually for every channel (e.g. FireSting.channels[1].salinity = 3.4) or
        for all channels at the same time (e.g. FireSting.temperature = 37).
        Channels can also be deactivated to skip them during a measurement (e.g. FireSting.channels[2].active = False)

        The most important settings are:
            led_intensity: intensity of the LED in % (possible values: 10, 15, 20, 30, 40, 60, 80, 100)
            measure_time: duration of the measurement (possible values FireSting: 1-200 ms,
                                                                       other devices: 1, 2, 4, 8, 16, 32, 64, 128ms)
            amplification: (recommended values: 80x, 200x or 400x)
            frequency: modulation frequency (sensor type specific. Normal range oxygen sensor: 4000Hz)
            temperature: compensation temperature for the sensor and used to calculate temperature dependent derived
                         values (umolar, airSat). If set to -300 or "external" the external temperature sensor is used
                         for compensation.
            pressure: used for calculation of pressure dependent values (umolar, airSat, percentO2), if set to -1 or
                     "internal" the internal pressure sensor is used (if available)
            salinity: used for calculation of salinity dependent values (umolar)

        If led_intensity or amplification is changed a new calibration of the sensor is recommended. Frequency should
        only be changed if a different sensor type is connected (new calibration necessary).
        temperature, pressure or salinity can be changed without any influence on the calibration.

        It is recommended to do the setup and calibration with the "Oxygen Logger" Software
        from PyroScience. The settings and calibration are stored on the device itself and are not lost upon
        power cycling.

        After this setup measurements can be triggered with the "measure" function.

        :param port: Port of the device (e.g. "/dev/ttyUSB0" on linux, or "COM1" on windows)
        :param baud: first baudrate to try for the connection. Usually not necessary
        """
        self.pyroio = PyroIO(port, baud=baud)
        self.channels = {}
        for i in range(self.pyroio.nof_channels):
            i += 1
            self.channels[i] = FireChannel(self.pyroio, i, '{}'.format(i))

    def measure(self, measure_temperature: bool = True, measure_pressure: bool = True, measure_humidity: bool = True,
                decode_status: bool = False) -> dict:
        """ Measure all channels of the device. Results are returned as dict of channel results
            e.g {1: {'dPhi': 30.123
                      'umolar': 140.456
                       ...
                      }
                 2: {'dPhi': ...
                     ...
                    }
                 ...
                }

        The settings during the measurement are included in this result. This is a bit verbose but makes the results
        more traceable.

        Every channel returns a dictionary with the following entries:
            name                unit    description
            time                s       seconds till the Epoch
            dPhi                °       measured phase angle
            status              -       encoded status message

            umolar              µM      concentration of oxygen in water, pressure and temperature required for
                                        calculation
            mbar                mbar    partial pressure of oxygen in air or water
            airSat              %       air saturation in water, temperature required for calculation
            percentO2           %       %O2 in the gas phase, ambient pressure required for calculation
            pressure            mbar    ambient pressure (only if device can measure air pressure)
            sample_temperature  °C      temperature of the sample (only if the device can measure temperature,
                                        "None" if no temperature sensor is connected
            humidity            %RH     percent relative humidity. (only if the device can measure humidity)

            signal_intensity    mV      signal intensity during the measurement (recommended > 100mV)
            ambient_light       mV      amount of ambient light reaching the photodetector
                                        (signal_intensity + ambient_light must be < 2000mV or the photodetector is
                                        oversaturated)
            device_temperature  °C      internal temperature of the device

            led_intensity       %       reports current led_intensity
            measure_time        ms      reports current measure_time
            amplification       x       reports current amplification
            frequency           Hz      reports current modulation frequency
            temperature_setting °C      temperature setting during measurement. If "external" the external temperature
                                        sensor is used for compensation.
            salinity_setting    g/L     salinity setting during the measurement. Used for calculation of umolar
            pressure_setting    mbar    pressure setting. If "internal" the internal pressure sensor is used for
                                        calculation of umolar and percentO2.


        :param measure_temperature: bool, trigger a temperature measurement (sample and case), if False the last
            measured temperature or the set temperature is used for compensation
        :param measure_pressure: bool, trigger a pressure measurement, if False the last measured pressure or the set
            pressure is used for compensation
        :param measure_humidity: bool, trigger a humidity measurement, if False the last measured humidity or the set
            humidity are used for compensation
        :param decode_status: translate the status bits to human readable massages (status becomes a list of strings)
        :return:
        """
        # To improve measurement time measure temperature only once
        if measure_temperature:
            self.channels[1].measure_sample_temperature()
        if measure_pressure:
            self.channels[1].measure_pressure()
        if measure_humidity:
            self.channels[1].measure_humidity()
        res = {}
        for k, v in self.channels.items():
            if v.active:
                res[k] = v.measure(measure_temperature=False, measure_pressure=False, measure_humidity=False,
                                   decode_status=decode_status)

        return res

    @property
    def settings(self):
        """ Fet the settings of all channels"""
        return {k: c.settings for k, c in self.channels.items()}

    @property
    def led_intensity(self):
        """ Get or set the led intensity of all channels.

        Available values: 10, 15, 20, 30, 40, 60, 80, (100)
        """
        return {k: c.led_intensity for k, c in self.channels.items()}

    @led_intensity.setter
    def led_intensity(self, intensity):
        for c in self.channels.values():
            c.led_intensity = intensity

    @property
    def measure_time(self):
        """ Get or set the measurement time of all channels

        FireSting: 1-200 ms
        Other devices: 1, 2, 4, 8, 16, 32, 64, 128 ms
        """
        return {k: c.measure_time for k, c in self.channels.items()}

    @measure_time.setter
    def measure_time(self, meas_time):
        for c in self.channels.values():
            c.measure_time = meas_time

    @property
    def amplification(self):
        """ Get or set the amplification of all channels

        Recommended values: 80, 200, 400
        """
        return {k: c.amplification for k, c in self.channels.items()}

    @amplification.setter
    def amplification(self, amp):
        for c in self.channels.values():
            c.amplification = amp

    @property
    def frequency(self):
        """ Get or set the modulation frequency of all channels

        Range: 1-32000 Hz
        Sensor specific (details on request)
        Normal range oxygen sensor: 4000Hz
        """
        return {k: c.frequency for k, c in self.channels.items()}

    @frequency.setter
    def frequency(self, freq):
        for c in self.channels.values():
            c.frequency = freq

    @property
    def temperature(self):
        """ Get or set the sample temperature to a fixed value (unit °C) for all channels

        Used to compensate oxygen measurements and calculated temperature dependent derived units (umolar, airSat)

        If set to -300 or "external" the measurement of the external temperature sensor is used for compensation
        (if available)
        """
        return {k: c.temperature for k, c in self.channels.items()}

    @property
    def salinity(self):
        """ Set the sample salinity to a fixed value (unit: g/L) for all channels

        Used to calculated salinity dependent derived units (umolar)
        """
        return {k: c.salinity for k, c in self.channels.items()}

    @property
    def pressure(self):
        """ Get or set the environment pressure to a fixed value (unit: mbar) for all channels

        Used to calculated pressure dependent derived units (umolar, percentO2)

        If set to -1 or "internal" the measurement of the internal pressure sensor is used for compensation
        (if available)
        """
        return {k: c.pressure for k, c in self.channels.items()}

    def blink(self):
        """ Flash the logo and trigger an optical measurement in all channels

        useful to identify the device
        """
        self.pyroio.blink()
        for c in sorted(self.channels):
            self.channels[c].blink()

    def disconnect(self):
        self.pyroio.disconnect()


if __name__ == '__main__':
    pass
