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


def send_data():
    global delimiter, data
    delimiter = ","

    serial.write_string(str(input.light_level()))
    serial.write_string(delimiter)
    serial.write_string(str(input.sound_level()))
    serial.write_string(delimiter)
    serial.write_string(str(input.temperature()))
    serial.write_string(delimiter)
    serial.write_string(str(input.acceleration(Dimension.X)))
    serial.write_string(delimiter)
    serial.write_string(str(input.acceleration(Dimension.Y)))
    serial.write_string(delimiter)
    serial.write_string(str(input.acceleration(Dimension.Z)))
    serial.write_string(delimiter)
    serial.write_string(str(input.rotation(Rotation.PITCH)))
    serial.write_string(delimiter)
    serial.write_string(str(input.rotation(Rotation.Roll)))
    serial.write_string(delimiter)
    serial.write_string(str(input.magnetic_force(Dimension.X)))
    serial.write_string(delimiter)
    serial.write_string(str(input.magnetic_force(Dimension.Y)))
    serial.write_string(delimiter)
    serial.write_string(str(input.magnetic_force(Dimension.Z)))

    serial.write_string("\n")

def on_data_received():
    send_data()

serial.on_data_received(serial.delimiters(Delimiters.NEW_LINE), on_data_received)

data = ""
delimiter = ""
basic.clear_screen()