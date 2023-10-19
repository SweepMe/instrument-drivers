# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2023 SweepMe! GmbH (sweep-me.net)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# SweepMe! device class
# Type: Switch
# Device: EXFO MXS-9100


from pysweepme import debug, EmptyDevice
import re


class Device(EmptyDevice):

    description = """
                    The MXS-9100 can be controlled remotely over the network via the Ethernet interface. For this,
                    the MXS-9100 has an integrated Perle IOLAN DSI Device Server to enable network access to
                    the native RS232 interface of the switch module inside the chassis. Please refer to the user
                    manual to configure the IP address of Perle Device Server.
                    <br>
                    <p><strong>Usage:</strong></p>
                    <ul>
    
                    <li>Enter semicolon separated configurations, to connect multiple channels at once,
                     e.g. "1 11;5 8". The respective input and output channels are separated with a space.</li>
                    <li>Closed means the switch is parked (no optical path). Open means a parked switch will be set to
                    pre-parked configuration. Connect means setting an input channel to a specified output channel.</li>
                    <li>In case SweepBox is used as Sweep value, each channel configuration can be separated with a 
                    comma, e.g. "1 11;5 8,2 3;4 7"
                    </ul>
                """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "MXS-9100"
        
        self.port_manager = True
        self.port_types = ["TCPIP"]
        self.port_properties = {
            "TCPIP_EOLwrite": "\n",
            "TCPIP_EOLread": "\n",
        }

        self.variables = ["Channels"]
        self.units = [""]
        self.plottype = [True]
        self.savetype = [False]

        self.channel_delimiters = [";", ":", ","]

    def set_GUIparameter(self):
        
        gui_parameter = {
                        "SweepMode": ["Channels"],
                        }
        
        return gui_parameter
        
    def get_GUIparameter(self, parameter={}):

        self.sweepmode = parameter["SweepMode"]
        self.sweepvalue = parameter["SweepValue"]
        self.port_string = parameter["Port"]

    def connect(self):

        # should be not needed in case latest SweepMe! 1.5.5 version is used
        if self.port_manager:
            # needed because self.port_properties did not show any effect
            self.port.write_termination = '\n'
            self.port.read_termination = '\n'

    def initialize(self):

        # identification = self.get_identification()
        # print("Identification:", identification)

        self.reset()

    def apply(self):

        channels_string = str(self.value)

        # split channels for all defined delimiters
        channels_list = re.split('|'.join(self.channel_delimiters), channels_string)

        channels_list_trimmed = []
        for channel_combination in channels_list:

            # split first and second number
            input_output_list = channel_combination.strip().split(" ")

            # filter out empty strings
            input_output_list = [item for item in input_output_list if item]

            if not input_output_list[0].isnumeric() or not input_output_list[1].isnumeric():
                raise ValueError("Channel list '%s' contains non-numeric characters." % str(input_output_list))

            channels_list_trimmed.append(input_output_list)

        for channel_combination in channels_list_trimmed:
            self.connect_channels(int(channel_combination[0]), int(channel_combination[1]))

        # Because the MXS-9100 has no display, we at least print a status message
        print("EXFO MXS-9100 connected channels: ", self.get_state_channels())

    def call(self):
        return self.value
        
    """ here, convenience functions start """

    def get_identification(self):
        self.port.write("*IDN?")
        identification_string = self.port.read()
        return identification_string

    def get_operation_complete(self):
        self.port.write("*OPC?")
        answer = self.port.read()
        return answer

    def reset(self):
        """
        This function sets all the input channels to output channel 0 (parked, no optical continuity).
        """
        self.port.write("*RST?")

    def close_channel(self, channel):
        """
        This function positions input channel i to the park position. In the park position
        there is no optical continuity.
        Args:
            channel: int

        Returns:
            None
        """
        self.port.write("ROUT%d:CLOS" % channel)

    def open_channel(self, channel):
        """
        This function restores input channel i from the park position (no optical continuity) to the channel position
        in effect when the switch was closed.
        Args:
            channel: int

        Returns:
            None
        """
        self.port.write("ROUT%d:OPEN" % channel)

    def connect_channels(self, input_channel, output_channel):
        """
        This command sets input channel to the specified output channel.
        Args:
            input_channel: int
            output_channel: int

        Returns:
            None
        """
        self.port.write("ROUT%d:SCAN %d" % (input_channel, output_channel))

    def get_state_channels(self):
        """
        This function returns a tuple of all connected input channels to the respective output.
        If the input channel is not connected (no optical continuity), a 0 is returned, which means
        it's connected to output channel 0 (parked).

        Returns:
            tuple: channels
        """
        self.port.write("ROUT:SCAN:ALL?")
        channels = self.port.read().split(" ")
        return channels

    def check_input_channel(self, input_channel):
        """
        This function returns the output channel of a given input.
        Args:
            input_channel: int

        Returns:
            int: output_channel
        """
        self.port.write('ROUT%d:SCAN?' % input_channel)
        output_channel = int(self.port.read())
        return output_channel

    def check_output_channel(self, output_channel):
        """
        This function returns the input channel of a given output.
        Args:
            output_channel: int

        Returns:
            int: input_channel
        """
        self.port.write('ROUT:SCAN:OUT? %d' % output_channel)
        input_channel = int(self.port.read())
        return input_channel

    def get_switch_size(self):
        """
        This command returns the dimensions of the whole rackmount in the format ix1xN, where i is
        the number of 1xN switch matrices.
        If the switch is a 3D Matrix Switch it will return with the format MxN, where M is
        the number of input channels and N is the number of output channels.

        Returns:
            tuple: switch_size
        """
        self.port.write('ROUT:PATH:CAT?')
        switch_size = tuple(map(int, self.port.read().split("x")))
        return switch_size
