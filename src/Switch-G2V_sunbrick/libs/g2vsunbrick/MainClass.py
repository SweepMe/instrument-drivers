#!/usr/bin/env python

'''
Copyright 2021 G2V Optics

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation 
     and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. 
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, 
INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT 
NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR 
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) 
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE.
'''

import sys
import os
import time
import struct
import binascii
import subprocess
import json

try:
    import serial
except ImportError:
    print("Can not find serial module.  Downloading.")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "serial"])
    import serial

class G2VSunbrick(object):
    '''
    Python object representing a single Sunbrick

    Keyword Arguments:
    serial_obj -- serial object used to communicate with the Sunbrick
    slave_address -- address of the Sunbrick when part of an array / network (Default is 1)
    '''
    def __init__(self, serial_obj, slave_address=1):

        self.__CMD_ARB_BEGIN = 5
        self.__CMD_ARB_START_ROUND = 6
        self.__CMD_ARB_ASSIGN_SLAVE_ID = 7
        self.__CMD_ARB_END = 8
        self.__CMD_GET_FIRMWARE_VERSION = 9
        self.__CMD_GET_DEVICE_ID = 10
        self.__CMD_GET_TEMPERATURE = 14
        self.__CMD_GET_CHANNEL_VALUE = 17
        self.__CMD_SET_CHANNEL_VALUE = 18
        self.__CMD_GET_NODE_COUNT = 20
        self.__CMD_GET_CHANNEL_COUNT = 21
        self.__CMD_SOFTWARE_RESET = 24
        self.__CMD_GET_BRICK_FIRMWARE_VERSION = 28
        self.__CMD_GET_INTENSITY_FACTOR = 31
        self.__CMD_SET_INTENSITY_FACTOR = 32

        self.__serial = serial_obj
        self.__slave_address = slave_address
        self.__brick_id = None
        self.__node_count = 0
        self.__channel_count = 0
        self.__comm_version = None
        self.__brick_version = None

        self.__brick_id = self.__get_brick_id()
        self.__channel_count = self.__get_channel_count()
        self.__node_count = self.__get_node_count()
        self.__comm_version = self.__get_comm_version()
        self.__brick_version = self.__get_brick_version()


    def __repr__(self):
        return "Sunbrick ID: {id}".format(id=hex(int(self.__brick_id)).upper())

    def __dir__(self):
        restrict_list = []
        restrict_list.append("brick_id")
        restrict_list.append("channel_count")
        restrict_list.append("channel_list")
        restrict_list.append("node_count")
        restrict_list.append("node_list")

        restrict_list.append("get_channel_value")
        restrict_list.append("set_channel_value")
        restrict_list.append("get_intensity_factor")
        restrict_list.append("set_intensity_factor")
        restrict_list.append("turn_off")
        restrict_list.append("get_spectrum")
        restrict_list.append("set_spectrum")
        restrict_list.append("get_avg_temperature")
        restrict_list.append("get_brick_temperatures")
        restrict_list.append("get_all_temperatures")

        restrict_list.append("create_network")

        return restrict_list


    def __len__(self):
        return (self.__node_count * self.__channel_count)

    @property
    def brick_id(self):
        '''Returns the ID of the Sunbrick as a string'''
        return str(hex(self.__brick_id)).upper().replace('0X', '')
    
    @property
    def channel_count(self):
        '''Returns the number of channels in the Sunbrick'''
        return self.__channel_count

    @property
    def channel_list(self):
        '''Returns a list of channels in the Sunbrick'''
        return range(1, self.__channel_count+1)
    
    @property
    def node_count(self):
        '''Returns the number of nodes in the Sunbrick'''
        return self.__node_count

    @property
    def node_list(self):
        '''Returns a list of nodes in the Sunbrick'''
        return range(1, self.__node_count+1)    


    @property
    def firmware_version(self):
        '''Returns the firmware version of the Sunbrick'''
        return "{c}-{b}".format(c=self.__comm_version, b=self.__brick_version)


    @property
    def address(self):
        '''
        Returns the address used to communicate with the Sunbrick
        A value of 1 implies the Sunbrick is the master brick
        '''
        return self.__slave_address

    def __float_to_hex(self, value):
        '''Internal method to convert a float value to the 32-bit hex representation'''
        return hex(struct.unpack('<I',struct.pack('<f',value))[0])


    def __read_in_hex(self,count):
        '''Internal method to handle reading in hex values in python 2.7 or python 3.x'''
        if(sys.version_info[0] < 3):
            return int(self.__serial.read(count).encode('hex'),16)
        else:
            return int(self.__serial.read(count).hex(),16)

    def __open_serial_check(self):
        '''Internal method to check if the serial port is open and open it if not'''
        if self.__serial.isOpen() == False:
            self.__serial.open()


    def __get_brick_id(self):
        '''Internal method to retrieve the 32-bit ID of the Sunbrick'''
        cmd_msg = [3,2,self.__CMD_GET_DEVICE_ID,self.__slave_address]
        self.__open_serial_check()
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)

        length = self.__read_in_hex(1)

        if(length == 7):

            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)

            if (owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3]):
                device_id = self.__read_in_hex(4)
            else:
                device_id = None

        else:
            self.__serial.flush()
            device_id = None

        return device_id


    def __get_node_count(self):
        '''Internal method to get the number of nodes (usually 1 or 9) from the Sunbrick'''
        cmd_msg = [3,2,self.__CMD_GET_NODE_COUNT,self.__slave_address]
        self.__open_serial_check()
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)
        length = self.__read_in_hex(1)

        if(4 == length):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)

            if (owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3]):
                node_count = self.__read_in_hex(1)
            else:
                self.__serial.reset_input_buffer()
                node_count = None
    
        else:
            self.__serial.reset_input_buffer()
            node_count = None

        return node_count

    def __get_channel_count(self):
        '''Internal method to get the number of channels in each node (usually 24 or 36)'''
        cmd_msg = [3,2,self.__CMD_GET_CHANNEL_COUNT,self.__slave_address]
        self.__open_serial_check()
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)
        length = self.__read_in_hex(1)

        if(4 == length):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)

            if (owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3]):
                channel_count = self.__read_in_hex(1)
            else:
                self.__serial.reset_input_buffer()
                channel_count = None
    
        else:
            self.__serial.reset_input_buffer()
            channel_count = None

        return channel_count


    def __get_comm_version(self):
        '''Internal method to get the firmware version of the Comm processor'''
        cmd_msg = [3,2,self.__CMD_GET_FIRMWARE_VERSION,self.__slave_address]
        self.__open_serial_check()
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)
        length = self.__read_in_hex(1)

        if(length == 7):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)

            if (owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3]):
                major = self.__read_in_hex(1)
                minor = self.__read_in_hex(1)
                build = self.__read_in_hex(1)
                patch = self.__read_in_hex(1)

                firmware_version = "{mj}.{mn}.{bd}.{pt}".format(mj=major, mn=minor, bd=build, pt=patch)
            else:
                firmware_version = "0.0.0.0"

        else:
            self.__serial.flush()
            firmware_version = None

        return firmware_version

    def __get_brick_version(self):
        '''Internal Private method to get the firmware version of the Brick processor'''
        cmd_msg = [3,2,self.__CMD_GET_BRICK_FIRMWARE_VERSION,self.__slave_address]
        self.__open_serial_check()
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)
        length = self.__read_in_hex(1)

        if(length == 7):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)

            if (owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3]):
                major = self.__read_in_hex(1)
                minor = self.__read_in_hex(1)
                build = self.__read_in_hex(1)
                patch = self.__read_in_hex(1)

                firmware_version = "{mj}.{mn}.{bd}.{pt}".format(mj=major, mn=minor, bd=build, pt=patch)
            else:
                firmware_version = "0.0.0.0"

        else:
            self.__serial.flush()
            firmware_version = None

        return firmware_version


    def _arbitration_begin(self):
        '''Internal method to tell the Master Sunbrick to begin arbitration on the network'''
        if(self.__slave_address == 1):
            cmd_msg = [2,2,self.__CMD_ARB_BEGIN]
            self.__open_serial_check()
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            self.__serial.write(cmd_msg)
            
            length = self.__read_in_hex(1)

            if(length == 3):
                owner = self.__read_in_hex(1)
                cmd = self.__read_in_hex(1)
                if (owner == cmd_msg[1] and cmd == cmd_msg[2]):
                    result = self.__read_in_hex(1)
                else:
                    return None

                return (result == 1)
            else:
                self.__serial.flush()
                return False
        else:
            return None


    def _arbitration_start_round(self):
        '''Internal method to tell the Master Sunbrick to do a round of arbitration and return the brick ID'''
        if (self.__slave_address == 1):
            cmd_msg = [2,2,self.__CMD_ARB_START_ROUND]
            self.__open_serial_check()
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            self.__serial.write(cmd_msg)
            # time.sleep(1)
            length = self.__read_in_hex(1)

            if (length == 6):
                owner = self.__read_in_hex(1)
                cmd = self.__read_in_hex(1)

                if (owner == cmd_msg[1] and cmd == cmd_msg[2]):
                    slave_id = self.__read_in_hex(4)
                else:
                    slave_id = None

                return slave_id
        else:
            return None


    def _arbitration_assign_slave_address(self, brick_id, slave_address):
        '''Internal method to tell the Master Sunbrick to assign a slave address to the given Sunbrick with brick_id'''
        if(brick_id == self.__brick_id):
            return None
        elif(slave_address == self.__slave_address):
            return None
        elif(slave_address == 1):
            return None
        elif(1 != self.__slave_address):
            return None

        cmd_msg = [7,2,self.__CMD_ARB_ASSIGN_SLAVE_ID,0,0,0,0,0]
        cmd_msg[3] = (brick_id>>24) & 0xFF
        cmd_msg[4] = (brick_id>>16) & 0xFF
        cmd_msg[5] = (brick_id>>8) & 0xFF
        cmd_msg[6] = (brick_id>>0) & 0xFF
        cmd_msg[7] = (slave_address) & 0xFF

        self.__open_serial_check()
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)

        length = self.__read_in_hex(1)

        if(length == 3):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
    
            if (owner == cmd_msg[1] and cmd == cmd_msg[2]):
                result = self.__read_in_hex(1)
            else:
                return None

            return (result == 1)

        else:
            self.__serial.flush()
            return None

    def _arbitration_get_channel_count(self, slave_address):
        '''Internal method to request the number of channels from a slave Sunbrick'''
        cmd_msg = [3,2,self.__CMD_GET_CHANNEL_COUNT,slave_address]
        self.__open_serial_check()
        self.__serial.write(cmd_msg)
        length = self.__read_in_hex(1)

        if(4 == length):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)

            if (owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3]):
                channel_count = self.__read_in_hex(1)
            else:
                channel_count = None

        else:
            self.__serial.reset_input_buffer()
            channel_count = None

        return channel_count


    def _arbitration_end(self):
        '''Internal method to tell the Master Sunbrick to end arbitration'''
        if(self.__slave_address == 1):
            cmd_msg = [2,2,self.__CMD_ARB_END]
            self.__open_serial_check()
            self.__serial.reset_input_buffer()
            self.__serial.reset_output_buffer()
            self.__serial.write(cmd_msg)
            
            length = self.__read_in_hex(1)

            if(length == 3):
                owner = self.__read_in_hex(1)
                cmd = self.__read_in_hex(1)
                
                if(owner == cmd_msg[1] and cmd == cmd_msg[2]):
                    result = self.__read_in_hex(1)
                else:
                    return None

                return (result == 1)
            else:
                return False
        else:
            self.__serial.flush()
            return None

    def __get_temperature(self, node):
        '''Internal method to get the temperature of a single node'''
        cmd_msg = [4,2,self.__CMD_GET_TEMPERATURE,self.__slave_address,0]

        if(node < 0 or node > self.__node_count):
            raise ValueError("Node must be in range [{min} - {max}] - {v}".format(min=str(0), max=self.__node_count, v=str(node)))

        cmd_msg[4] = node

        self.__open_serial_check()
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)

        length = self.__read_in_hex(1)

        if(length == 6):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)
            node = self.__read_in_hex(1)

            if(owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3] and node == cmd_msg[4]):
                raw_temp = self.__read_in_hex(2)
                temperature = float(raw_temp)
                temperature = temperature/10
            else:
                temperature = None  

        else:
            self.__serial.flush()
            temperature = None

        return temperature


    def get_avg_temperature(self):
        '''Method to return the average temperature of all nodes'''
        cmd_msg = [4,2,self.__CMD_GET_TEMPERATURE,self.__slave_address,0]
        self.__open_serial_check()
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)

        length = self.__read_in_hex(1)

        if(length == 6):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)
            node = self.__read_in_hex(1)

            if(owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3]):
                raw_temp = self.__read_in_hex(2)
                temperature = float(raw_temp)
                temperature = temperature/10
            else:
                temperature = None  

        else:
            self.__serial.flush()
            temperature = None

        return temperature

    def get_all_temperatures(self):
        '''
        Method to return an array of temperatures matching to the nodes.
        '''
        temp_array = []
        for node in range(0,self.__node_count+1):

            temp_array.append(self.__get_temperature(node))

        return temp_array


    def get_channel_value(self, channel, node=1):
        '''
        Method to return the current channel value from a node (default node is 1)
        Keyword Arguments:
        channel -- integer representing the channel [1 - `channel_count`] to get the current value from. 
        node -- integer representing the node [1 - `node_count]. Default value of 1.
        '''
        node = int(node)
        channel = int(channel)

        if(node < 0 or node > self.__node_count):
            raise ValueError("Node must be in range [{min} - {max}]".format(min=str(1), max=self.__node_count))
        elif(channel < 0 or channel > self.__channel_count):
            raise ValueError("Channel must be in range [{min} - {max}]".format(min=str(1), max=self.__channel_count))

        cmd_msg = [5,2,self.__CMD_GET_CHANNEL_VALUE,self.__slave_address,node,channel]
        
        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)

        length = self.__read_in_hex(1)

        if(length == 7):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)
            node = self.__read_in_hex(1)
            channel = self.__read_in_hex(1)

            if(owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3] and node == cmd_msg[4] and channel == cmd_msg[5]):
                value = self.__read_in_hex(2)
                value = float(value/10)
            else:
                value = None

        else:
            self.__serial.flush()
            value = None

        return value


    def set_channel_value(self, channel, value, node=0):
        '''
        Sets the chosen LED channel to a certain value
        Keyword Arguments:
        channel -- integer representing the channel [1 - `channel_count`] to get the current value from.
        value -- float representing the value [0 - 100%] to set the channel to where 100% means fully on.
        node -- integer representing the node [Between 0 and `node_count] where 0 means all nodes. Default value of 0.
        '''
        node = int(node)
        channel = int(channel)
        value = float(round(value,1))

        if(node < 0 or node > self.__node_count):
            raise ValueError("Node must be in range [{min} - {max}]".format(min=str(0), max=self.__node_count))
        elif(channel < 0 or channel > self.__channel_count):
            raise ValueError("Channel must be in range [{min} - {max}]".format(min=str(1), max=self.__channel_count))
        elif(value < 0 or value > 100.0):
            raise ValueError("Value must be in range [{min} - {max}]".format(min=str(0), max=str(100.0)))

        value = int(value*10)

        cmd_msg = [7,2,self.__CMD_SET_CHANNEL_VALUE,self.__slave_address,node,channel,0,0]
        cmd_msg[6] = (value >> 8) & 0xFF
        cmd_msg[7] = (value >> 0) & 0xFF

        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)

        length = self.__read_in_hex(1)

        if(length == 4):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)

            if(owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3]):
                result = self.__read_in_hex(1)

            return (result == 1)

        else:
            self.__serial.flush()
            return None

    def get_intensity_factor(self, node=1):
        '''
        Returns the intensity factor (0-100.0%) of the Sunbrick.
        Different nodes can have different intensity factors but it is assumed they are all the same.
        Keyword Arguments:
        node -- integer representing the node [1 - `node_count].  Default is node 1. 
        '''
        node = int(node)
        if(node <= 0 or node > self.__node_count):
            raise ValueError("Node must be in range [{min} - {max}]".format(min=str(0), max=self.__node_count))
        
        cmd_msg = [4,2,self.__CMD_GET_INTENSITY_FACTOR,self.__slave_address,node]

        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)

        length = self.__read_in_hex(1)

        if(length == 8):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)
            node = self.__read_in_hex(1)

            if(owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3] and node == cmd_msg[4]):
                if(sys.version_info[0] < 3):
                    hex_value = binascii.hexlify(self.__serial.read(4))
                    value = struct.unpack('!f',hex_value.decode('hex'))[0]
                else:
                    hex_value = []
                    hex_value.append(self.__read_in_hex(1))
                    hex_value.append(self.__read_in_hex(1))
                    hex_value.append(self.__read_in_hex(1))
                    hex_value.append(self.__read_in_hex(1))

                    bytes_array = bytearray(hex_value)
                    value = struct.unpack('!f',bytes_array)[0]
                    value = round(value,1)

            else:
                self.__serial.flush()
                value = None

        else:
            self.__serial.flush()
            value = None

        return value


    def set_intensity_factor(self, value, node=0):
        ''' 
        Sets the intensity factor for a node (default is 0 which is all nodes).
        Keyword Arguments:
        node -- integer representing the node [0 - `node_count].  Default is node 0 which sets all nodes. 
        value -- float representing the intensity [0% to 100%]. 
        '''
        node = int(node)
        refresh = True
        refresh = bool(refresh)
        value = round(float(value),1)
        if(node < 0 or node > self.__node_count):
            raise ValueError("Node must be in range [{min} - {max}]".format(min=str(0), max=self.__node_count))

        if(value < 0 or value > 100.0):
            raise ValueError("Value must be in range [{min} - {max}]".format(min=str(0), max=str(100)))

        int_value = self.__float_to_hex(value)
        cmd_msg = [9,2,self.__CMD_SET_INTENSITY_FACTOR,self.__slave_address,node,0,0,0,0,0]
        cmd_msg[5] = (int(int_value,0) >> 24) & 0xFF
        cmd_msg[6] = (int(int_value,0) >> 16) & 0xFF
        cmd_msg[7] = (int(int_value,0) >> 8) & 0xFF
        cmd_msg[8] = (int(int_value,0) >> 0) & 0xFF
        cmd_msg[9] = int(refresh)

        self.__serial.reset_input_buffer()
        self.__serial.reset_output_buffer()
        self.__serial.write(cmd_msg)

        length = self.__read_in_hex(1)

        if(length == 5):
            owner = self.__read_in_hex(1)
            cmd = self.__read_in_hex(1)
            addr = self.__read_in_hex(1)
            node = self.__read_in_hex(1)

            if(owner == cmd_msg[1] and cmd == cmd_msg[2] and addr == cmd_msg[3] and node == cmd_msg[4]):
                result = self.__read_in_hex(1)
            else:
                return None

            return (result == 1)

        else:
            self.__serial.flush()
            return None


    def turn_off(self):
        '''Method used to set all channel values on all nodes to 0'''
        for channel in self.channel_list:
            self.set_channel_value(node=0, channel=channel, value=0)

        return True

    def get_spectrum(self, node=1):
        '''
        Method used to return an array of `dict` containing the different
         channel values where the `dict` is of the form:
          '{"Channel":<channel>, "Value":<value>}'
        Keyword Arguments
        node -- integer representing the node [1 - `node_count].  Default is node 1. 
        '''
        node = int(node)

        spectrum_array = [{'Channel':c, 'Value':round(self.get_channel_value(channel=c),1)} for c in self.channel_list]

        return spectrum_array


    def set_spectrum(self, spectrum_file):
        '''
        Method used to set a spectrum on a Sunbrick. 
        Keyword Arguments
        spectrum_file -- a JSON file that contains an array of `dict` types of
         the form:
         '{"Channel":<channel>, "Value":<value>}'
        '''
        if os.path.isfile(spectrum_file) == False:
            raise OSError("Spectrum file at {sf} can not be found.".format(sf=spectrum_file))

        with open(spectrum_file, 'r') as f:
            data = json.load(f)

        for item in data:
            if 'Channel' in item and 'Value' in item:
                self.set_channel_value(channel=int(item['Channel']), value=item['Value'])
            else:
                raise ValueError('Spectrum file {sf} contains invalid key-value pair {d}'.format(sf=spectrum_file, d=item))

        return True
                

    def setup_network_arbitration(self):
        '''
        Uses the Sunbrick arbitration protocol to automatically create a network of all Sunbricks.
        This method is used by `G2VSunbrickArray` and should not be called otherwise.
        '''
        id_dict = {}
        id_dict[self.brick_id] = 1

        slave_addr = 2

        new_slave_id = 1
        prev_slave_id = 1

        self._arbitration_begin()

        while (new_slave_id != None):
            new_slave_id = self._arbitration_start_round()
            
            if new_slave_id is not None:
                if new_slave_id == prev_slave_id:
                    raise Exception("Detected duplicate brick ids in network - {id}".format(id=new_slave_id))
                

                if self._arbitration_assign_slave_address(brick_id=new_slave_id, slave_address=slave_addr):
                    # Check that the channel count from the slave is valid
                    if (0xFF != self._arbitration_get_channel_count(slave_addr)):
                        id_dict[str(hex(new_slave_id)).upper().replace('0X', '')] = slave_addr
                        prev_slave_id = slave_addr
                        slave_addr = slave_addr + 1

            time.sleep(10)

        self._arbitration_end()

        return id_dict


class G2VSunbrickArray(object):
    '''
    Python object representing an array of Sunbricks.  An array must consist of a minimum of one Sunbrick.
    Keyword Arguments:
    serial_obj -- serial object used to communicate with the Sunbrick
    brick_ids -- list of brick_ids as strings to include in the network.  This list must be provided if there are more than 8 Sunbricks.
    '''
    def __init__(self, serial_obj, brick_ids=None):
        self.__brick_id_dict = None
        self.__brick_ids = brick_ids
        self.__serial = serial_obj
        self.__master_id = None
        self.__bricks = {}

        # Get the master brick first.  Master brick is always connected  via serial
        try:
            master_brick = G2VSunbrick(serial_obj)

            self.__master_id = master_brick.brick_id.upper().replace('0X','')
            self.__bricks[self.__master_id] = master_brick

        except Exception as e:
            raise OSError("No Sunbrick connected on port {p} - {e}".format(p=serial_obj.port, e=e))

        # If there is no assigned list, try using arbitration
        if self.__brick_ids is None:    
            self.__brick_id_dict = master_brick.setup_network_arbitration()

            for brick_id, addr in self.__brick_id_dict.items():
                if brick_id not in self.__bricks:
                    self.__bricks[brick_id] = G2VSunbrick(self.__serial, addr)

        # If there is an assigned list, go through each sunbrick in the list and assign slave address
        else:
            slave_addr = 2
            self.__bricks[self.__master_id]._arbitration_begin()

            for brick_id in self.__brick_ids:
                if brick_id != self.__master_id:
                    result = self.__bricks[self.__master_id]._arbitration_assign_slave_address(brick_id=int(brick_id.upper(),16), slave_address=slave_addr)
                    if result:
                        self.__bricks[brick_id] = G2VSunbrick(serial_obj=self.__serial, slave_address=slave_addr)
                        slave_addr += 1


    def __repr__(self):
        return "Sunbrick Array"

    def __dir__(self):
        restrict_list = []
        restrict_list.append("brick_count")
        restrict_list.append("brick_ids")
        restrict_list.append("master_id")

        restrict_list.append("turn_off")
        restrict_list.append("get_intensity_factor")
        restrict_list.append("set_intensity_factor")
        restrict_list.append("set_spectrum")
        restrict_list.append("get_spectrum")
        restrict_list.append("get_avg_temperature")
        restrict_list.append("get_brick_temperatures")

    @property
    def brick_count(self):
        '''Contains the number of Sunbricks in the network'''
        return len(self.__bricks)

    @property
    def brick_ids(self):
        '''Returns a list of brick IDs'''
        return [key for key in self.__bricks.keys()]

    @property
    def node_count(self):
        '''Returns the number of nodes in the Master Sunbrick '''

        return self.__bricks[self.__master_id].node_count

    @property
    def channel_count(self):
        '''Returns the number of channels in the Master Sunbrick'''
        return self.__bricks[self.__master_id].channel_count

    @property
    def channel_list(self):
        '''Returns a list of available channels using the Master Sunbrick'''
        return self.__bricks[self.__master_id].channel_list
    
    @property
    def node_list(self):
        '''Returns a list of available nodes using the Master Sunbrick'''
        return self.__bricks[self.__master_id].node_list

    @property
    def master_id(self):
        '''Returns the id of the master brick'''
        return self.__master_id

    @property
    def bricks(self):
        '''Allows for accessing individual G2VSunbricks'''
        return self.__bricks

    def turn_off(self):
        '''Turns off all the bricks in the network'''
        for brick in self.__bricks.values():
            brick.turn_off()


    def get_intensity_factor(self):
        '''Return the intensity factor from the master brick which represents the array'''
        return self.__bricks[self.__master_id].get_intensity_factor()

    def set_intensity_factor(self, value):
        '''Sets the intensity factor for the whole array to value'''
        value = round(float(value),1)
        fail_condition = 0
        for brick in self.__bricks.values():
            result = brick.set_intensity_factor(value=value)
            if result is None or result is False:
                fail_condition += 1

        return (fail_condition == 0)

    def get_spectrum(self):
        '''
        Method used to return a dictionary containing the different channel values of the form {<channel>:<value>}
        '''
        return self.__bricks[self.__master_id].get_spectrum()


    def set_spectrum(self, spectrum_file):
        '''
        Method used to set a spectrum on a Sunbrick array. 
        Keyword Arguments
        spectrum_file -- a JSON file that contains key-value pairs of the form '<channel>:<value>'
        '''
        if os.path.isfile(spectrum_file) == False:
            raise OSError("Spectrum file at {sf} can not be found.".format(sf=spectrum_file))

        fail_condition = 0
        for brick in self.__bricks.values():
            result = brick.set_spectrum(spectrum_file=spectrum_file)
            if result is None or result is False:
                fail_condition += 1

        return (fail_condition == 0)


    def get_avg_temperature(self):
        '''Return the average temperature of all the Sunbricks in an array'''

        avg_temperature = 0
        count = 0
        for brick in self.__bricks.values():
            temp = brick.get_avg_temperature()
            if temp is not None:
                avg_temperature += temp
                count += 1

        if count != 0:
            return (avg_temperature / count)
        else:
            return None

    def get_brick_temperatures(self):
        '''Return the temperature of each brick in a dictionary with the brick_id as the key'''
        temp_dict = {}
        for brick_id, brick in self.__bricks.items():
            temp_dict[brick_id] = brick.get_avg_temperature()

        return temp_dict




