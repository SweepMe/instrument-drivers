import serial, serial.tools.list_ports
import struct
import time
import sys
import os
import re

# Telegram Header
SEND = 0xC0 + 0x20 + 0x10
RECEIVE = 0x40 + 0x20 + 0x10

# Constant telegram messages
GET_NAME = [RECEIVE, 0x0, 0x0]
GET_SN   = [RECEIVE, 0x0, 0x1]

STANDARD_HEADER = [SEND + 1, 0x0, 0x36]
#            Header  Output Obj  Mask   Command
REMOTE_ON = STANDARD_HEADER + [0x10, 0x10]
REMOTE_OFF = STANDARD_HEADER + [0x10, 0x00]
OUTPUT_ON =  STANDARD_HEADER + [0x01, 0x01]
OUTPUT_OFF = STANDARD_HEADER + [0x01, 0x00]

TRACKING_ON =  STANDARD_HEADER + [0xF0, 0xF0]
TRACKING_OFF = STANDARD_HEADER + [0xF0, 0xE0]


ERR_STRINGS = {
    0x0: 'NO ERROR',

    # Communication Error
    0x3: 'CHECKSUM WRONG',
    0x4: 'STARTDELIMITER WRONG',
    0x5: 'WRONG OUTPUT',
    0x7: 'OBJECT UNDEFINED',

    # User Error
    0x8: 'OBJECT LENGTH INCORRECT',
    0x9: 'NO RW ACCESS',
    0xf: 'DEVICE IN LOCK STATE',
    0x30: 'UPPER LIMIT OF OBJECT EXCEEDED',
    0x31: 'LOWER LIMIT OF OBJECT EXCEEDED'
}

OBJ_NOM_U = 0x2
OBJ_NOM_I = 0x3
OBJ_NOM_P = 0x4
OBJ_OVP_THRESHOLD = 0x26
OBJ_OCP_THRESHOLD = 0x27
OBJ_SET_U = 0x32
OBJ_SET_I = 0x33
OBJ_STATUS = 0x47

class ExceptionPSU(Exception):
    pass

class ExceptionTimeout(Exception):
    pass

class PsuEA(object):

    OUTPUT_1 = 0x0
    OUTPUT_2 = 0x1

    CV = 0x0
    CC = 0x2

    PSU_DEVICE_LIST_LINUX = ["ea-ps-20xx-xx", "ea-ps-23xx-xx"]
    PSU_DEVICE_LIST_WIN = ['PS 2000 B']


    def __init__(self, comport=None, sn=None, desi=None, baudrate=115200):
        """fac
        :brief: Class to control PSUs from Elektro Automatik
                Tested with: EA PS 2042 - 06B,
                             EA PS 2342 - 10B
        :param comport: Linux: ttyUSBx or ttyACMx
                        Windows: COMx
        :type comport: str
        :param sn:  Serial number of PSU.
        :type sn: str
        :param desi: Designator of PSU.
        :type desi: str
        :param baudrate: Should stay to this value. Not changeable on PSU
        :type baudrate: int

        """

        self._port = None
        self._baud = baudrate

        self.psu = None
        self.__nom_voltage = 0.0
        self.__nom_current = 0.0
        self.__nom_power = 0.0
        self.__act_voltage = 0.0
        self.__max_current = 0.0
        self.__output1_connected = False
        self.__output2_connected = False

        self.__find_devices(comport, sn, desi)

        if not self._port:
            raise ExceptionPSU('No PSU found')

        self.connect()
        self.get_config()

    def __del__(self):
        self.close(True,True)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(True,True)

    def __find_devices(self, comport, sn, desi):       
        found = []
        dev_list = None
        res = False
        _dev = ''
        if comport == None:
            if sys.platform == 'linux':
                dev_list = os.listdir('/dev')
            elif sys.platform == 'win32':
                dev_list = serial.tools.list_ports.comports()
            for dev in dev_list:
                if sys.platform == 'linux':
                    res = dev[:-2] in self.PSU_DEVICE_LIST_LINUX
                    _dev = dev
                elif sys.platform == 'win32':
                    res = dev.description[:9] in self.PSU_DEVICE_LIST_WIN
                    _dev = dev.device
                if res: # Compare without index at the end
                    self._port = _dev
                    self.connect()
                    desc = self.get_device_description()
                    self.close(remote=True)
                    if (not sn and not desi) or (sn == desc[1] or desi == desc[0]):
                        return
                    else:
                        found.append(desc[0] if desi else desc[1])
            help_str = ''
            if len(found) > 0:
                help_str = ' Found these devices: "%s"' % '", "'.join(found)
            if sn or desi:
                raise ExceptionPSU('ERROR: No PSU with %s "%s" found.%s' % ('S/N' if sn else 'designator', sn if sn else desi, help_str))
            raise ExceptionPSU('ERROR: No PSU found.')
        elif comport:
            if sys.platform == 'linux' and comport in os.listdir('/dev'):
                self._port = comport
                return
            elif sys.platform == 'win32':
                for p in serial.tools.list_ports.comports():                   
                    if comport in p.description:                        
                        self._port = p.device
                        return
        
        raise ExceptionPSU('ERROR: No PSU at port "%s" found.' % (comport))                       
                

    def __pack_list(self, list):
        return struct.pack('%sB' % len(list), *list)

    def __int_to_bytes(self, num, num_bytes):
        _list = [8*i for i in reversed(range(num_bytes))]
        return [(num >> i & 0xff) for i in _list]

    def __calc_checksum(self, cmd_list):
        checksum = 0
        for byte in cmd_list:
            checksum += byte
        return self.__int_to_bytes(checksum, 2)

    def __get_response(self, package):
        return package[3:-2]

    def __tx_rx(self, cmd, expect_length):
        crc = self.__calc_checksum(cmd)
        output = self.__pack_list(cmd + crc)
        self.psu.write(output)
        time.sleep(0.005)
        num = 0
        t0 = time.time()
        while num < (expect_length+5):
            num = self.psu.inWaiting()
            if time.time() - t0 > 1:
                raise ExceptionTimeout('Didn\'t receive %d bytes in time.' % (expect_length+5))
        res = self.__get_response(self.psu.read(num))
        time.sleep(0.04)
        return res

    def __set_value(self, value, max_value, obj_num, output):
        if (output == self.OUTPUT_1 and not self.__output1_connected)\
            or (output == self.OUTPUT_2 and not self.__output2_connected):
            self.remote_on(output)
        value_percent = int((value * 25600.0) / max_value)
        value_bytes = self.__int_to_bytes(value_percent, 2)
        packet = [SEND + len(value_bytes) - 1, output, obj_num] + value_bytes
        error = struct.unpack('B',self.__tx_rx(packet, 1))[0]
        if error != 0x0:
            raise ExceptionPSU(ERR_STRINGS[error])
        return error

    def __get_value(self, obj, exp_len, output):
        packet = [RECEIVE, output, obj]
        res = self.__tx_rx(packet, exp_len)
        return struct.unpack('>BBHH', res)

    def __get_float(self, obj, output):
        packet = [RECEIVE, output, obj]
        res = self.__tx_rx(packet, 4)
        return struct.unpack('>f', res)

    def connect(self, comport=None):
        """
        :brief Connect with PSU
        :param comport: COM port name
        :type comport: str
        """
        port = ''
        if sys.platform == 'win32':
            port = comport or self._port
        elif sys.platform == 'linux':
            port = "/dev/%s" % (comport if comport else self._port)
        self.psu = serial.Serial(port, self._baud, timeout=5)

    def close(self, remote=False, output=False, output_num=0):
        """
        :brier Closes the serial connection and can also
               turn off remote control mode and deactivate output.
        :param remote: True, if remote control mode should turned off.
        :type remote:  bool
        :param output: True, if output should be deactivated.
        :type output: bool
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        """
        if self.psu:            
            if output:
                self.output_off(output_num)
            if remote:
                self.remote_off(output_num)

            if not (self.__output1_connected or self.__output2_connected):
                #print('Close serial conn', file=sys.stderr)
                self.psu.close()
                self.psu = None

    def get_config(self, output_num=0):
        """
        :brief Get nominal voltage, current and power from device
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        """
        self.__nom_voltage = self.get_nominal_voltage(output_num)
        self.__nom_current = self.get_nominal_current(output_num)
        self.__nom_power = self.get_nominal_power(output_num)
        self.set_ovp(self.__nom_voltage)
        self.set_ocp(self.__nom_current)

    def get_device_description(self, output_num=0):
        """
        :brief Get device name
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Device name
        :rtype: str
        """
        GET_NAME[1] = output_num
        name = self.__tx_rx(GET_NAME, 11)[:-1].decode('ascii')
        GET_SN[1] = output_num
        sn = self.__tx_rx(GET_SN, 11)[:-1].decode('ascii')
        return (name, sn)

    def remote_on(self, output_num=0):
        """
        :brief Activates remote mode on device
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Device return message/ack
        :rtype: byte str
        """
        REMOTE_ON[1] = output_num
        self.__output1_connected = output_num == self.OUTPUT_1
        self.__output2_connected = output_num == self.OUTPUT_2
        res = self.__tx_rx(REMOTE_ON, 1)
        res = struct.unpack('B', res)[0]
        if res == 0:
            self.get_config(output_num)
        return res

    def remote_off(self, output_num=0):
        """
        :brief Deactivates remote mode on device
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Device return message/ack
        :rtype: byte str
        """
        self.__output1_connected = not (output_num == self.OUTPUT_1) and self.__output1_connected
        self.__output2_connected = not (output_num == self.OUTPUT_2) and self.__output2_connected    
        REMOTE_OFF[1] = output_num
        res = self.__tx_rx(REMOTE_OFF, 1)
        res = struct.unpack('B', res)[0]
        return res

    def get_nominal_voltage(self, output_num=0):
        """
        :brief: Get nominal voltage from device
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Nominal voltage
        :rtype: float
        """
        return self.__get_float(OBJ_NOM_U, output_num)[0]

    def get_nominal_current(self, output_num=0):
        """
        :brief: Get nominal current from device
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Nominal current
        :rtype: float
        """
        return self.__get_float(OBJ_NOM_I, output_num)[0]

    def get_nominal_power(self, output_num=0):
        """
        :brief: Get nominal power from device
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Nominal power
        :rtype: float
        """
        return self.__get_float(OBJ_NOM_P, output_num)[0]

    def set_voltage(self, voltage, output_num=0):
        """
        :brief: Set output voltage on device
        :param voltage: desired output voltage in V
        :type voltage: int/float
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Device return message
        :rtype: byte str
        """
        # Calculate actual possible maximum current depending on maximum output power
        set_voltage = voltage
        if set_voltage > self.__nom_voltage:
            set_voltage = self.__nom_voltage
        try:
            if set_voltage > self.__nom_power/self.__max_current:
                set_voltage = self.__nom_power/self.__max_current
        except ZeroDivisionError:
            pass              
            
        self.__act_voltage = float(set_voltage)
        self.__set_value(set_voltage, self.__nom_voltage, OBJ_SET_U, output_num)
        return self.__act_voltage

    def set_current(self, current, output_num=0):
        """
        :brief: Set maximum output current on device
        :param voltage: desired output current in A
        :type voltage: int/float
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Device return message
        :rtype: byte str
        """
        # Calculate actual possible maximum current depending on maximum output power
        set_current = current
        if set_current > self.__nom_current:
            set_current = self.__nom_current
        try:
            if set_current > self.__nom_power/self.__act_voltage:
                set_current = self.__nom_power/self.__act_voltage
        except ZeroDivisionError:
            pass
            
        self.__max_current = float(set_current)
        self.__set_value(set_current, self.__nom_current, OBJ_SET_I, output_num)
        return self.__max_current

    def get_voltage(self, output_num=0):
        """
        :brief: Get current output voltage from device
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Voltage in V
        :rtype: float
        """
        volt = self.__get_value(OBJ_STATUS, 6, output_num)
        return (volt[2] * self.__nom_voltage)/25600.0

    def get_current(self, output_num=0):
        """
        :brief: Get current output current from device
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Current in A
        :rtype: float
        """
        current = self.__get_value(OBJ_STATUS, 6, output_num)
        return (current[3] * self.__nom_current)/25600.0

    def get_status(self, output_num=0):
        """
        :brief: Get status from device. See programming Guide for further information page 11
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Dictionary with current states.
        :rtype: dict
        """
        status = self.__get_value(OBJ_STATUS, 6, output_num)
        remote_on = status[0]
        status_byte = status[1]
        d_status = {'remote on': remote_on == 1,
                    'output on' : (status_byte & 0x1) == 1,
                    'controller state': (status_byte >> 1) & 0x3,
                    'tracking active': ((status_byte >> 3) & 0x1) == 1,
                    'OVP activ': ((status_byte >> 4) & 0x1) == 1,
                    'OCP activ': ((status_byte >> 5) & 0x1) == 1,
                    'OPP activ': ((status_byte >> 6) & 0x1) == 1,
                    'OTP activ': ((status_byte >> 7) & 0x1) == 1}
        return d_status

    def output_on(self, output_num=0):
        """
        :brief Turn on power output on device
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Device return message/ack
        :rtype: byte str
        """
        OUTPUT_ON[1] = output_num
        return struct.unpack('B', self.__tx_rx(OUTPUT_ON, 1))[0]

    def output_off(self, output_num=0):
        """
        :brief Turn off power output on device
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Device return message/ack
        :rtype: byte str
        """
        OUTPUT_OFF[1] = output_num
        return struct.unpack('B', self.__tx_rx(OUTPUT_OFF, 1))[0]

    def set_ovp(self, voltage, output_num=0):
        """
        :brief: Set Over Voltage Protection
        :param voltage: desired OVP voltage
        :type voltage: float/int
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Device return message
        :rtype: byte str
        """
        return self.__set_value(voltage, self.__nom_voltage, OBJ_OVP_THRESHOLD, output_num)

    def set_ocp(self, current, output_num=0):
        """
        :brief: Set Over Current Protection
        :param voltage: desired OCP current
        :type voltage: float/int
        :param output_num: Output number for multi output devices (e.g. PS 2342-10B)
        :type outupu_num: int
        :return: Device return message
        :rtype: byte str
        """
        return self.__set_value(current, self.__nom_current, OBJ_OCP_THRESHOLD, output_num)


if __name__ == '__main__':
    psu = PsuEA()
    print(psu.get_device_description())
    psu.close(True,True)
    if sys.platform == 'linux':
        psu = PsuEA(comport='ea-ps-20xx-xx-0')
        print(psu.get_device_description())
        psu.close(True,True)
    elif sys.platform == 'win32':
        psu = PsuEA(comport='PS 2000 B')
        print(psu.get_device_description())
        psu.close(True,True)
        
        psu = PsuEA(comport='COM14')
        print(psu.get_device_description())
        psu.close(True,True)
    
    psu = PsuEA(desi='PS 2042-10B')
    print(psu.get_device_description())
    psu.close(True,True)
    psu = PsuEA(sn='2815450332')
    print(psu.get_device_description())
    psu.close(True,True)



    try:
        psu = PsuEA(comport='ea-ps-99xx-xx-1')
    except ExceptionPSU as e:
        print(str(e))
    try:
        psu = PsuEA(desi='PS 2142-10B')
    except ExceptionPSU as e:
        print(str(e))
    try:
        psu = PsuEA(sn='2815450333')
    except ExceptionPSU as e:
        print(str(e))

    psu = PsuEA(sn='2815450332')
    print(psu.get_device_description())
    output = psu.OUTPUT_1
    psu.remote_on(output)
    psu.output_on(output)
    psu.set_ovp(40, output)
    psu.set_ocp(10, output)
    print('Nom volt', psu.get_nominal_voltage(output))
    print('Nom curr', psu.get_nominal_current(output))
    print('Nom power', psu.get_nominal_power(output))
    psu.set_voltage(35, output)
    psu.set_current(1, output)
    time.sleep(2)
    print('Voltage', psu.get_voltage(output))
    print('Current', psu.get_current(output))
    psu.close(True, True, output)
    
    



    

