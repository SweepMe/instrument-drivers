# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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


# SweepMe! driver
# * Module: Calliope
# * Instrument: mini 3


from pysweepme.EmptyDeviceClass import EmptyDevice
from pysweepme.ErrorMessage import debug, error


class Device(EmptyDevice):
    description = """<h3>Calliope mini 3</h3>
<p><br />This SweepMe! driver can be used to readout the basic sensors of the Calliope mini 3. The Calliope mini is a mini computer/ micro controller that is used at schools for educational purposes. The board comes with several included sensors that can be read out without any further wiring.</p>
<p><br /><br /><strong>Sensors:</strong></p>
<ul>
<li>Light level</li>
<li>Sound level</li>
<li>Acceleration (x,y,z)</li>
<li>Magnetic field (x, y, z)</li>
<li>Rotation (pitch, roll)</li>
</ul>
<p>&nbsp;</p>
<p><strong>Usage:</strong></p>
<ul>
<li>Before the first use, please download the Calliope script onto the device. Please use the following link&nbsp;<a href="https://makecode.calliope.cc/_E77YhDWRVcCk">https://makecode.calliope.cc/_E77YhDWRVcCk</a>&nbsp;to open the script in the online editor. There you can directly download the script to the Calliope mini. Alternatively, you can find&nbsp;.hex file shipped with this SweepMe! driver. This file can be also used to load it with the Calliope online editor and program the mini computer.</li>
<li>In SweepMe!: Add the module "Logger" to your sequencer and select the Device "Logger-Calliope_mini3". To read out the Calliope device multiple times, put the Logger module into a Loop module. Use a Delay module to slow down the measurement. Typically, it is enough to read the sensor data every second or every 0.1 s (= 10 times per second).</li>
</ul>
<p>&nbsp;</p>
<p><strong>Known issues:<br /></strong></p>
<ul>
<li>Please make sure that the Calliope online editor is closed or the Calliope mini is disconnected in the online editor. Otherwise, the serial communication is disturbed.</li>
</ul>
    """

    def __init__(self):
        super().__init__()

        self.shortname = "Calliope mini 3"
        self.variables = ["Light level",
                          "Sound level",
                          "Temperature",
                          "Acceleration x",
                          "Acceleration y",
                          "Acceleration z",
                          "Rotation pitch",
                          "Rotation roll",
                          "Magnetic force x",
                          "Magnetic force y",
                          "Magnetic force z",
                          ]

        self.units = ["", "", "°C", "mg", "mg", "mg", "°", "°", "µT", "µT", "µT"]
        
        self.port_manager = True
        self.port_types = ["COM"]
        self.port_properties = {
            "timeout": 1,
            "baudrate": 115200,
            "EOL": "\n",
        }

    def measure(self):
        self.port.write("R")

    def call(self):
        answer = self.port.read()

        try:
            light, sound, t, acc_x, acc_y, acc_z, rot_p, rot_r, mag_x, mag_y, mag_z = map(float, answer.split(","))
        except ValueError:
            msg = ("Unable to interprete values. Please make sure Calliope Mini is disconnected in online editor.")
            raise ValueError(msg)
        
        return light, sound, t, acc_x, acc_y, acc_z, rot_p, rot_r, mag_x, mag_y, mag_z 
