# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# SweepMe! device class
# Type: Switch
# Device: mb-Technologies HVM


import time
import string

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    description = """
                    <p><strong>Usage:</strong></p>
                    <ul>
                    <li>Enter colon-separated configurations, e.g "A1: A2: B3: D4".</li>
                    <li>Alternatively a relay can be specified by a 5 digit number 'biioo', where b=board (always 1), 
                    ii=input and oo=output, e.g. "10101, 10102: 10203: 10404".</li>
                    <li>A "Switch settling time in ms" will be waited for after a new configuration is applied.</li>
                    <li>Open means the relay is open/disconnected. No current will flow through. Closed means the relay 
                    is closed/connected, and current will flow through.</li>
                    <li>In the user manual page 8 you can find how channel list and channel configuration are defined 
                    for this instrument. The input channels are indicated with an alphabet (A-D) and the output channel 
                    is defined by a number 1-12. However, for compatibility reasons, the instrument also accepts numeric
                     channel string: 1iioo, where ii is the input channel number and oo is the output channel number.
                    This driver uses the second style.</li>
                    <li>When discharge mode is activate, the given discharge time will be waited for while discharge
                    is activate. Afterwards the instrument is switched back to normal mode. This happens during the 
                    'configure' phase of the driver, i.e. when a new branch is started to be processed.</li>
                    <li>Using a "0" all channels will remain open. This command is not part of the communication
                    protocol but was implemented in the SweepMe! driver for reasons of convenience.</li>
                    <li>TCPIP/LAN communication is possible by registering a raw socket with port 10001.</li>
                    </ul>
                """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "HVM"
        
        self.port_manager = True
        self.port_types = ['GPIB', 'TCPIP', 'COM']
        self.port_properties = {    
            "timeout": 3,
            "EOL": "\n",
            "TCPIP_EOLwrite": "\n",
            "TCPIP_EOLread": "\n",
        }

        self.variables = ["Channels"]
        self.units = ["#"]

    def set_GUIparameter(self):
        
        gui_parameter = {
            "SweepMode": ["Channels"],
            "Switch settling time in ms": 20,
            "Discharge": True,
            "Discharge time in s": "1.0",
        }
        
        return gui_parameter
        
    def get_GUIparameter(self, parameter={}):
        self.device = parameter['Device']
        self.switch_settling_time_ms = parameter["Switch settling time in ms"]
        self.sweepmode = parameter["SweepMode"]
        self.use_discharge = parameter["Discharge"]
        self.discharge_time = parameter["Discharge time in s"]

    def connect(self):

        # Identifier must be called in 'connect' because for unknown reason the identifier can not be called again once
        # other commands like *RST or OPEN ALL are used. Thus, other instances of the driver could not call the
        # identification anymore. However, it works if they do it one after another in the 'connect' phase.
        identifier = self.get_identification()
        # print("Identifier:", identifier)

        # Retrieving the number of inputs and outputs from the identification string by using the second entry
        # "HVMiioo" where i is the input number and oo is the output number
        n_inputs = int(identifier.split(",")[1][3:5])
        n_outputs = int(identifier.split(",")[1][5:7])

        # available channels as defined by mb-Technologies using a letter from A-L followed by a number from 1 to 12
        self.available_channels = [f"{letter}{i}" for letter in list(string.ascii_uppercase[:n_inputs])
                                   for i in range(1, n_outputs+1)]
        # available channels in the format as used by Keysight supported for compatibility reasons
        self.available_channels_5digit = [f"1{j:02d}{i:02d}" for j in range(1, n_inputs+1)
                                          for i in range(1, n_outputs+1)]

    def initialize(self):

        self.reset()
        self.open_all_channels()

    def configure(self):
        self.switch_settling_time_s = float(self.switch_settling_time_ms) / 1000

        self.set_connection_rule_free(rule=True)  # multiple connections are possible

        if self.use_discharge:
            self.set_discharge_mode(True)
            time.sleep(float(self.discharge_time))
            self.set_discharge_mode(False)

    def unconfigure(self):
        self.open_all_channels()

    def apply(self):
        self.value = str(self.value)

        self.open_all_channels()

        # "0" is not part of the communication protocol but can be used to keep all channels open
        if self.value.strip(" ") != "0":

            self.close_channel(self.value)

            # print(self.is_channel_closed(self.value))  # does not work with COM communication

            # for testing purposes
            # will be later removed/commented when driver is working
            # print("Closed channels: ", self.is_channel_closed(self.value))
            # print("Closed channels: ", self.get_closed_channels())
    
    def reach(self):
        time.sleep(self.switch_settling_time_s)
        
    def call(self):
        return self.value
        
    """ here, convenience functions start """

    @staticmethod
    def split_list(list_, chunk_size=50):
        """ this method returns chunks of a list to be processed
        """
        for i in range(0, len(list_), chunk_size):
            yield list_[i:i + chunk_size]

    def check_connections(self, connections):

        if isinstance(connections, str):
            connections = connections.replace(' ', '').replace(';', ',').replace(':', ',')
            connections = connections.split(',')

        if all([x in self.available_channels_5digit for x in connections]):  # 5 digits
            return connections
        elif all([x in self.available_channels for x in connections]):  # 2 digits - alphanumeric
            return connections
        else:
            raise ValueError("Channel configuration has wrong format")

    def get_identification(self):
        """
        Queries identification string 
        Returns:
            answer (manufacturer, model number, serial number, hardware version, software version)
        """
        self.port.write("*IDN?")
        answer = self.port.read()
        return answer
    
    def get_operation_complete(self):
        """
        Waits until all pending operations are complete then returns 1
        
        """
        self.port.write("*OPC?")
        if self.port.read() == "1":
            return True
        else:
            return False

    def reset(self) -> None:
        """
        Resets the instrument and opens all relays. 
        """
        self.port.write("*RST")

    def run_self_test(self) -> None:
        """
        Starts execution of the relay matrix self-test. Depending on the matrix size the test may take up to 1 minute to 
        finish. 
        Disconnect all measurement cables before starting the self-test! The test may fail if cables are connected. 
        """
        self.port.write("*TST")

    def enquiry_self_test(self) -> None:
        """
        Queries the result of the relay matrix self-test.
        Response: 
        0 Self-test passed 
        n (relay, …) Self-test failed , n=number of failing relays, list of failing relays follows 
        """
        self.port.write("*TST?")

    def set_remote(self) -> None:
        """
        Set device to remote mode which disables the keyboard.
        """
        self.port.write("*REM")

    def set_local(self) -> None:
        """
        Set device to remote mode which enabled the keyboard.
        """

        self.port.write("*LOC")

    def open_all_channels(self):
        """
        This function opens all relays.
        Returns:
            None
        """
        self.port.write("OPEN ALL")

    def close_channel(self, channels):
        """
        This function closes given channel string.
        Args:
            channels: string or list of strings

        Returns:
            None
        """

        channels = self.check_connections(channels)

        self.port.write('CLOS %s' % ",".join(channels))
    
    def open_channel(self, channels) -> None:
        """
        This function opens the given channels.
        Args:
            channels: string or list of strings

        Returns:
            None
        """

        channels = self.check_connections(channels)

        self.port.write('OPEN %s' % ",".join(channels))
    
    def is_channel_closed(self, channels):
        """
        Queries the close status of the relays specified in the list. Queries are sent in chunks as the e.g. the GPIB
        buffer is not large enough to process all possible channels for some switching matrices

        Returns:
            list of integer: 1 means closed, 0 means open
        """

        channels = self.check_connections(channels)

        closed_channels = []
        for chunk in split_list(channels):
            self.port.write(":CLOS? %s" % ",".join(chunk))
            answer = self.port.read()
            closed_channels += list(map(int, answer.split(' ')))
        return closed_channels

    def is_channel_open(self, channels):
        """
        Queries the close status of the relays specified in the list. Queries are sent in chunks as the e.g. the GPIB
        buffer is not large enough to process all possible channels for some switching matrices

        Returns:
            list of integer: 1 means open, 0 means closed
        """

        channels = self.check_connections(channels)

        open_channels = []
        for chunk in split_list(channels):
            self.port.write(":OPEN? %s" % ",".join(chunk))
            answer = self.port.read()
            open_channels += list(map(int, answer.split(' ')))
        return open_channels

    def get_closed_channels(self):

        all_channels = self.is_channel_closed(self.available_channels)
        closed_channels = []

        for i, channel in enumerate(self.available_channels):
            if all_channels[i]:
                closed_channels.append(channel)

        return closed_channels

    def get_open_channels(self):

        all_channels = self.is_channel_open(self.available_channels)

        open_channels = []
        for i, channel in enumerate(self.available_channels):
            if all_channels[i]:
                open_channels.append(channel)

        return open_channels

    def set_connection_rule_free(self, rule=True) -> None:
        """
        Sets the connection rule to
        free: an input port can connect to multiple output ports
        single: an input port can connect to one output port only
        """

        if rule:
            self.port.write("CONN:RULE ALL,FREE")
        else:
            self.port.write("CONN:RULE ALL,SROU")

    def get_relay_cycle_counts(self, channels):
        """
        Queries the number of relay switch cycles for the given channels

        """

        channels = self.check_connections(channels)

        self.port.write("SYST:STA:REL? %s" % channels)
        answer = self.port.read()
        return answer.split(" ")
    
    def set_discharge_mode(self, mode) -> None:
        """
        Set discharge mode

        Args:
            mode: int (bool) being 0 (False) or 1 (True)
        """
        self.port.write("ROUT:DIS %i" % int(mode))

    def get_discharge_mode(self):
        self.port.write("ROUT:DIS?")
        answer = int(self.port.read())
        return answer

    def get_serial_number(self, board):
        """
        board:
        1 to 12 Relay board
        101 Logic board
        102 Power board
        103 Display board
        104 Backplane board

        Args:
            board: number of the board

        Returns:
            string: serial number
            string: date

        """

        self.port.write("SYSTEM:BOARD:SERIAL? %s" % str(board))
        answer = self.port.read().split(',')
        return answer

    def get_error(self):
        """
        Errors are saved in a temporary storage. This command queries the first error in the list.
        The error is then removed from the list. The error list is cleared at power - on and when executing
        the *RST command.
        """

        self.port.write(":SYST:ERR?")
        return self.port.read()

    def get_all_errors(self):

        while True:
            error = self.get_error()
            if error == "0,No error":
                break
            else:
                print(error)


if __name__ == "__main__":
    device = Device()
    cmd = "A1, D4, A8"
    print(cmd, device.check_connections(cmd))
    cmd = "10101", "10201", "20101"  # triggers exception
    print(cmd, device.check_connections(cmd))
