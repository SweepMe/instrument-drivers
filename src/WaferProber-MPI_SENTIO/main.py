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
# Type: WaferProber
# Device: MPI Corporation SENTIO

import socket

from pysweepme import EmptyDevice  # Class comes with SweepMe!
from pysweepme import debug
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()

import sentio
import importlib

importlib.reload(sentio)


class Device(EmptyDevice):
    description = """
    <p><strong>Usage:</strong></p>
    <ul>
    <li>This driver can communicate with MPI wafer probers through TCPIP and GPIB protocols. However,
    TCPIP is recommended, as the driver retrieves the probe plan at the beginning of the measurement, and due to slower
    data transfer rate of GPIB, this may take a long time.</li>
    </ul>
    """

    def __init__(self):

        EmptyDevice.__init__(self)

        self.shortname = "SENTIO"
        self.variables = ["Die index", "Die x", "Die y", "Subsite index"]
        self.units = ["", "", "", ""]
        self.plottype = [True, True, True, True]
        self.savetype = [True, True, True, True]

        self.port_manager = True
        self.port_types = ["TCPIP", "GPIB"]
        self.port_properties = {
            "timeout": 2,
            "TCPIP_EOLread": "\n",
        }
        self.port_properties = {
            "timeout": 20.0,
            "TCPIP_EOLread": "\n",
            "TCPIP_EOLwrite": "\n",
        }

    def set_GUIparameter(self):
        gui_parameter = {
            "Light at contact": ["As is", "On", "Off"],
            "Light at separation": ["As is", "On", "Off"],
            "": None,
            "End position": ['None', 'Home', 'Center']
        }
        return gui_parameter

    def get_GUIparameter(self, parameter):

        self.port_string = parameter["Port"]
        self.is_light_contact = parameter["Light at contact"]
        self.is_light_separation = parameter["Light at separation"]
        self.end_position = parameter["End position"]

        if not (self.port_string.startswith("TCPIP") or self.port_string.startswith("GPIB")):
            self.port_manager = False

    def get_probeplan(self):
        """
        Retrieves the wafers, dies, and subsites to be tested and returns a list of string for each

        Returns:
            wafers: list of strings
            dies: list of strings
            subsites: list of strings
        """

        wafers = []

        dies = []
        for i in range(0, self.prober.map_get_num_dies()):
            x, y = self.prober.map_path_get_die(i)
            dies.append("%s,%s#%s" % (x, y, i))
            # dies.append("%s" % i)

        subsites = []
        for i in range(0, self.prober.map_subsite_get_num()):
            subsites.append("%s" % i)

        return wafers, dies, subsites

    def get_current_wafer(self):
        """
        function is used by the WaferProber module to get the current wafer before the run starts in case
        the sweep values "Current Wafer" is used.
        """
        current_wafer = ""

        return current_wafer

    def get_current_die(self):
        """
        function is used by the WaferProber module to get the current die before the run starts in case
        the sweep value "Current Die" is used.
        """
        # Scan station is only supported only on fully automatic machines (TS2000-IFE, TS2500, TS3500).
        # if self.prober.loader_scan_station(station="chuck"):
        i, x, y = self.prober.map_die_get_current_index()
        current_die = "%s,%s#%s" % (x, y, i)
        # else:
        # current_die = ""

        return current_die

    def get_current_subsite(self):
        """
        function is used by the WaferProber module to get the current subsite before the run starts in case
        the sweep value "Current Subsite" is used.
        """
        # Scan station is only supported only on fully automatic machines (TS2000-IFE, TS2500, TS3500).
        # if self.prober.loader_scan_station(station="chuck"):
        current_subsite = str(self.prober.map_die_get_current_subsite())
        # else:
        # current_subsite = ""

        return current_subsite

    # here semantic functions start

    def connect(self):

        if self.port_manager:
            # needed because self.port_properties did not show any effect
            self.port.port.write_termination = '\n'
            self.port.port.read_termination = '\n'
            self.prober = sentio.MPISentioProber(self.port)
        else:
            if ":" in self.port_string:
                tcp_ip, tcp_port = self.port_string.split(":")
            else:
                tcp_ip, tcp_port = self.port_string, "35555"
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.settimeout(self.port_properties["timeout"])
            try:
                client.connect((tcp_ip, int(tcp_port)))
            except:
                debug("Unable to create a socket connection.")
                raise
            self.prober = sentio.MPISentioProber(client)

    def disconnect(self):
        del self.prober

    def initialize(self):
        pass

    def configure(self):

        self.prober.move_chuck_separation()

        if self.is_light_contact == "On":
            self.prober.light_off_at_contact(False)
        elif self.is_light_contact == "Off":
            self.prober.light_off_at_contact(True)

        if self.is_light_separation == "On":
            self.prober.light_on_at_separation(True)
        elif self.is_light_separation == "Off":
            self.prober.light_on_at_separation(False)

    def unconfigure(self):

        self.prober.move_chuck_separation()

        if self.end_position == 'Home':
            self.prober.move_chuck_home()
        elif self.end_position == 'Center':
            self.prober.move_chuck_center()

    def apply(self):
        # debug("New value to apply:", self.value)

        self.die_index = int(self.sweepvalues["Die"].split("#")[1])
        if self.sweepvalues["Subsite"] is None:
            self.subsite_index = None
        else:
            self.subsite_index = int(self.sweepvalues["Subsite"])
        
        self.prober.siph_move_separation("West")
        self.prober.siph_move_separation("East")
        self.prober.move_chuck_separation()

        # moving to new die and subsite
        self.die_x, self.die_y, _ = self.prober.map_step_die_seq(self.die_index, self.subsite_index)
        self.prober.move_chuck_contact()

    def call(self):

        if self.subsite_index is None:
            subsite_index = float('nan')
        else:
            subsite_index = self.subsite_index

        return [self.die_index, self.die_x, self.die_y, subsite_index]
