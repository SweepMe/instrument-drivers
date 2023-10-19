# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 SweepMe! (sweep-me.net)
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
# Type: Logger
# Device: WebSocket

import pysweepme.FolderManager as FoMa
FoMa.addFolderToPATH()

# import python module here as usual
import websocket  # websocket-client package
import threading
import time
import queue


from pysweepme.ErrorMessage import error, debug

from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!


class Device(EmptyDevice):

    description =   """
                    <p><strong>WebSocket-Logger</strong></p>
                    <ul>
                    <li>insert the socket string into the port field<br />e.g. "ws:\\localhost:8765"</li>
                    <li><strong>Send start message:</strong>&nbsp;Send a message to the WebSocket to start sending messages if needed. Leave free if the WebSocket automatically starts sending messages.</li>
                    <li><strong>Discard header lines:</strong>&nbsp;Read a number of lines at the beginning that are discarded and not returned by this Device Class</li>
                    <li><strong>Send query message:</strong> Send a message to the WebSocket to trigger it sending a further message. Leave free if the WebSocket automatically sends messages.</li>
                    <li><strong>Timeout in s:</strong> The time after which the measuremnt stops if no message is received.</li>
                    </ul>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "WebSocket"
        self.variables = ["Message"]
        self.units = [""]
        self.plottype = [False]
        self.savetype = [True]

    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        gui_parameter = {
                        "Port": "ws://localhost:8765",
                        "Discard header lines": 0,
                        "Send start message": "",
                        "Send query message": "",
                        "Timeout in s": 3.0,
                        }

        return gui_parameter
    
    def get_GUIparameter(self, parameter):

        self.port_string = parameter["Port"]
        try:
            self.header_lines = int(parameter["Discard header lines"])
        except:
            debug("Logger-PC_WebSocket: Cannot create integer from header lines, set to 0")
            self.header_lines = 0
        
        # global start_message
        self.start_message = parameter["Send start message"]
        self.query_message = parameter["Send query message"]
        self.message_timeout = float(parameter["Timeout in s"])

    # here functions start that are called by SweepMe! during a measurement

    def connect(self):
    
        # self.messages = queue.Queue()

        self.ws = websocket.WebSocketApp(
                                          self.port_string,
                                          on_open=self.on_open,
                                          on_message=self.on_message,
                                          on_error=self.on_error,
                                          on_close=self.on_close,
                                        )
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

        self.messages = queue.Queue()
            
    def disconnect(self):
        self.ws.close()    
     
    def initialize(self):
        for i in range(self.header_lines):
            msg = self.messages.get(block=True, timeout=self.message_timeout)
            print("Websocket header line:", i, msg)
        
    def deinitialize(self):
        pass

    def request_result(self):
        if self.query_message != "":
            self.ws.send(self.query_message)
    
    def read_result(self):
        self.msg = self.messages.get(block=True, timeout=self.message_timeout)
          
    def call(self):
        return self.msg

    # further functions defined by this Device Class

    def on_message(self, ws, message):
        # print(message)
        self.messages.put(message)

    def on_error(self, ws, error):
        debug("WebSocket error", error)

    def on_close(self, ws, close_status_code, close_msg):
        if close_status_code or close_msg:
            print("Close status code:", str(close_status_code))
            print("Close message:", str(close_msg))

    def on_open(self, ws):
        if self.start_message != "":
            ws.send(self.start_message)
