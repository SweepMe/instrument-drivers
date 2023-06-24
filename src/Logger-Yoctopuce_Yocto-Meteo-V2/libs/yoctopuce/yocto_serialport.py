# -*- coding: utf-8 -*-
#*********************************************************************
#*
#* $Id: yocto_serialport.py 40298 2020-05-05 08:37:49Z seb $
#*
#* Implements yFindSerialPort(), the high-level API for SerialPort functions
#*
#* - - - - - - - - - License information: - - - - - - - - -
#*
#*  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
#*
#*  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
#*  non-exclusive license to use, modify, copy and integrate this
#*  file into your software for the sole purpose of interfacing
#*  with Yoctopuce products.
#*
#*  You may reproduce and distribute copies of this file in
#*  source or object form, as long as the sole purpose of this
#*  code is to interface with Yoctopuce products. You must retain
#*  this notice in the distributed source file.
#*
#*  You should refer to Yoctopuce General Terms and Conditions
#*  for additional information regarding your rights and
#*  obligations.
#*
#*  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
#*  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
#*  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
#*  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
#*  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
#*  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
#*  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR
#*  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT
#*  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
#*  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
#*  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
#*  WARRANTY, OR OTHERWISE.
#*
#*********************************************************************/


__docformat__ = 'restructuredtext en'
from yoctopuce.yocto_api import *



# --- (generated code: YSnoopingRecord class start)
#noinspection PyProtectedMember
class YSnoopingRecord(object):
    #--- (end of generated code: YSnoopingRecord class start)
    # --- (generated code: YSnoopingRecord definitions)
    #--- (end of generated code: YSnoopingRecord definitions)

    def __init__(self, json_str):
        # --- (generated code: YSnoopingRecord attributes)
        self._tim = 0
        self._dir = 0
        self._msg = ''
        #--- (end of generated code: YSnoopingRecord attributes)
        json = YJSONObject(json_str, 0, len(json_str))
        json.parse()
        self._tim = json.getInt("t")
        m = json.getString("m")
        if m[0] == '<':
            self._dir = 1
        else:
            self._dir = 0
        self._msg = m[1:]

    # --- (generated code: YSnoopingRecord implementation)
    def get_time(self):
        """
        Returns the elapsed time, in ms, since the beginning of the preceding message.

        @return the elapsed time, in ms, since the beginning of the preceding message.
        """
        return self._tim

    def get_direction(self):
        """
        Returns the message direction (RX=0 , TX=1) .

        @return the message direction (RX=0 , TX=1) .
        """
        return self._dir

    def get_message(self):
        """
        Returns the message content.

        @return the message content.
        """
        return self._msg

#--- (end of generated code: YSnoopingRecord implementation)

# --- (generated code: YSnoopingRecord functions)
#--- (end of generated code: YSnoopingRecord functions)



#--- (generated code: YSerialPort class start)
#noinspection PyProtectedMember
class YSerialPort(YFunction):
    """
    The YSerialPort class allows you to fully drive a Yoctopuce serial port.
    It can be used to send and receive data, and to configure communication
    parameters (baud rate, bit count, parity, flow control and protocol).
    Note that Yoctopuce serial ports are not exposed as virtual COM ports.
    They are meant to be used in the same way as all Yoctopuce devices.

    """
    #--- (end of generated code: YSerialPort class start)
    #--- (generated code: YSerialPort return codes)
    #--- (end of generated code: YSerialPort return codes)
    #--- (generated code: YSerialPort dlldef)
    #--- (end of generated code: YSerialPort dlldef)
    #--- (generated code: YSerialPort definitions)
    RXCOUNT_INVALID = YAPI.INVALID_UINT
    TXCOUNT_INVALID = YAPI.INVALID_UINT
    ERRCOUNT_INVALID = YAPI.INVALID_UINT
    RXMSGCOUNT_INVALID = YAPI.INVALID_UINT
    TXMSGCOUNT_INVALID = YAPI.INVALID_UINT
    LASTMSG_INVALID = YAPI.INVALID_STRING
    CURRENTJOB_INVALID = YAPI.INVALID_STRING
    STARTUPJOB_INVALID = YAPI.INVALID_STRING
    JOBMAXTASK_INVALID = YAPI.INVALID_UINT
    JOBMAXSIZE_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    PROTOCOL_INVALID = YAPI.INVALID_STRING
    SERIALMODE_INVALID = YAPI.INVALID_STRING
    VOLTAGELEVEL_OFF = 0
    VOLTAGELEVEL_TTL3V = 1
    VOLTAGELEVEL_TTL3VR = 2
    VOLTAGELEVEL_TTL5V = 3
    VOLTAGELEVEL_TTL5VR = 4
    VOLTAGELEVEL_RS232 = 5
    VOLTAGELEVEL_RS485 = 6
    VOLTAGELEVEL_TTL1V8 = 7
    VOLTAGELEVEL_INVALID = -1
    #--- (end of generated code: YSerialPort definitions)

    def __init__(self, func):
        super(YSerialPort, self).__init__(func)
        self._className = 'SerialPort'
        #--- (generated code: YSerialPort attributes)
        self._callback = None
        self._rxCount = YSerialPort.RXCOUNT_INVALID
        self._txCount = YSerialPort.TXCOUNT_INVALID
        self._errCount = YSerialPort.ERRCOUNT_INVALID
        self._rxMsgCount = YSerialPort.RXMSGCOUNT_INVALID
        self._txMsgCount = YSerialPort.TXMSGCOUNT_INVALID
        self._lastMsg = YSerialPort.LASTMSG_INVALID
        self._currentJob = YSerialPort.CURRENTJOB_INVALID
        self._startupJob = YSerialPort.STARTUPJOB_INVALID
        self._jobMaxTask = YSerialPort.JOBMAXTASK_INVALID
        self._jobMaxSize = YSerialPort.JOBMAXSIZE_INVALID
        self._command = YSerialPort.COMMAND_INVALID
        self._protocol = YSerialPort.PROTOCOL_INVALID
        self._voltageLevel = YSerialPort.VOLTAGELEVEL_INVALID
        self._serialMode = YSerialPort.SERIALMODE_INVALID
        self._rxptr = 0
        self._rxbuff = ''
        self._rxbuffptr = 0
        #--- (end of generated code: YSerialPort attributes)

    #--- (generated code: YSerialPort implementation)
    def _parseAttr(self, json_val):
        if json_val.has("rxCount"):
            self._rxCount = json_val.getInt("rxCount")
        if json_val.has("txCount"):
            self._txCount = json_val.getInt("txCount")
        if json_val.has("errCount"):
            self._errCount = json_val.getInt("errCount")
        if json_val.has("rxMsgCount"):
            self._rxMsgCount = json_val.getInt("rxMsgCount")
        if json_val.has("txMsgCount"):
            self._txMsgCount = json_val.getInt("txMsgCount")
        if json_val.has("lastMsg"):
            self._lastMsg = json_val.getString("lastMsg")
        if json_val.has("currentJob"):
            self._currentJob = json_val.getString("currentJob")
        if json_val.has("startupJob"):
            self._startupJob = json_val.getString("startupJob")
        if json_val.has("jobMaxTask"):
            self._jobMaxTask = json_val.getInt("jobMaxTask")
        if json_val.has("jobMaxSize"):
            self._jobMaxSize = json_val.getInt("jobMaxSize")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        if json_val.has("protocol"):
            self._protocol = json_val.getString("protocol")
        if json_val.has("voltageLevel"):
            self._voltageLevel = json_val.getInt("voltageLevel")
        if json_val.has("serialMode"):
            self._serialMode = json_val.getString("serialMode")
        super(YSerialPort, self)._parseAttr(json_val)

    def get_rxCount(self):
        """
        Returns the total number of bytes received since last reset.

        @return an integer corresponding to the total number of bytes received since last reset

        On failure, throws an exception or returns YSerialPort.RXCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.RXCOUNT_INVALID
        res = self._rxCount
        return res

    def get_txCount(self):
        """
        Returns the total number of bytes transmitted since last reset.

        @return an integer corresponding to the total number of bytes transmitted since last reset

        On failure, throws an exception or returns YSerialPort.TXCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.TXCOUNT_INVALID
        res = self._txCount
        return res

    def get_errCount(self):
        """
        Returns the total number of communication errors detected since last reset.

        @return an integer corresponding to the total number of communication errors detected since last reset

        On failure, throws an exception or returns YSerialPort.ERRCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.ERRCOUNT_INVALID
        res = self._errCount
        return res

    def get_rxMsgCount(self):
        """
        Returns the total number of messages received since last reset.

        @return an integer corresponding to the total number of messages received since last reset

        On failure, throws an exception or returns YSerialPort.RXMSGCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.RXMSGCOUNT_INVALID
        res = self._rxMsgCount
        return res

    def get_txMsgCount(self):
        """
        Returns the total number of messages send since last reset.

        @return an integer corresponding to the total number of messages send since last reset

        On failure, throws an exception or returns YSerialPort.TXMSGCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.TXMSGCOUNT_INVALID
        res = self._txMsgCount
        return res

    def get_lastMsg(self):
        """
        Returns the latest message fully received (for Line, Frame and Modbus protocols).

        @return a string corresponding to the latest message fully received (for Line, Frame and Modbus protocols)

        On failure, throws an exception or returns YSerialPort.LASTMSG_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.LASTMSG_INVALID
        res = self._lastMsg
        return res

    def get_currentJob(self):
        """
        Returns the name of the job file currently in use.

        @return a string corresponding to the name of the job file currently in use

        On failure, throws an exception or returns YSerialPort.CURRENTJOB_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.CURRENTJOB_INVALID
        res = self._currentJob
        return res

    def set_currentJob(self, newval):
        """
        Selects a job file to run immediately. If an empty string is
        given as argument, stops running current job file.

        @param newval : a string

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("currentJob", rest_val)

    def get_startupJob(self):
        """
        Returns the job file to use when the device is powered on.

        @return a string corresponding to the job file to use when the device is powered on

        On failure, throws an exception or returns YSerialPort.STARTUPJOB_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.STARTUPJOB_INVALID
        res = self._startupJob
        return res

    def set_startupJob(self, newval):
        """
        Changes the job to use when the device is powered on.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the job to use when the device is powered on

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("startupJob", rest_val)

    def get_jobMaxTask(self):
        """
        Returns the maximum number of tasks in a job that the device can handle.

        @return an integer corresponding to the maximum number of tasks in a job that the device can handle

        On failure, throws an exception or returns YSerialPort.JOBMAXTASK_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.JOBMAXTASK_INVALID
        res = self._jobMaxTask
        return res

    def get_jobMaxSize(self):
        """
        Returns maximum size allowed for job files.

        @return an integer corresponding to maximum size allowed for job files

        On failure, throws an exception or returns YSerialPort.JOBMAXSIZE_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.JOBMAXSIZE_INVALID
        res = self._jobMaxSize
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    def get_protocol(self):
        """
        Returns the type of protocol used over the serial line, as a string.
        Possible values are "Line" for ASCII messages separated by CR and/or LF,
        "Frame:[timeout]ms" for binary messages separated by a delay time,
        "Modbus-ASCII" for MODBUS messages in ASCII mode,
        "Modbus-RTU" for MODBUS messages in RTU mode,
        "Wiegand-ASCII" for Wiegand messages in ASCII mode,
        "Wiegand-26","Wiegand-34", etc for Wiegand messages in byte mode,
        "Char" for a continuous ASCII stream or
        "Byte" for a continuous binary stream.

        @return a string corresponding to the type of protocol used over the serial line, as a string

        On failure, throws an exception or returns YSerialPort.PROTOCOL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.PROTOCOL_INVALID
        res = self._protocol
        return res

    def set_protocol(self, newval):
        """
        Changes the type of protocol used over the serial line.
        Possible values are "Line" for ASCII messages separated by CR and/or LF,
        "Frame:[timeout]ms" for binary messages separated by a delay time,
        "Modbus-ASCII" for MODBUS messages in ASCII mode,
        "Modbus-RTU" for MODBUS messages in RTU mode,
        "Wiegand-ASCII" for Wiegand messages in ASCII mode,
        "Wiegand-26","Wiegand-34", etc for Wiegand messages in byte mode,
        "Char" for a continuous ASCII stream or
        "Byte" for a continuous binary stream.
        The suffix "/[wait]ms" can be added to reduce the transmit rate so that there
        is always at lest the specified number of milliseconds between each bytes sent.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the type of protocol used over the serial line

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("protocol", rest_val)

    def get_voltageLevel(self):
        """
        Returns the voltage level used on the serial line.

        @return a value among YSerialPort.VOLTAGELEVEL_OFF, YSerialPort.VOLTAGELEVEL_TTL3V,
        YSerialPort.VOLTAGELEVEL_TTL3VR, YSerialPort.VOLTAGELEVEL_TTL5V, YSerialPort.VOLTAGELEVEL_TTL5VR,
        YSerialPort.VOLTAGELEVEL_RS232, YSerialPort.VOLTAGELEVEL_RS485 and YSerialPort.VOLTAGELEVEL_TTL1V8
        corresponding to the voltage level used on the serial line

        On failure, throws an exception or returns YSerialPort.VOLTAGELEVEL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.VOLTAGELEVEL_INVALID
        res = self._voltageLevel
        return res

    def set_voltageLevel(self, newval):
        """
        Changes the voltage type used on the serial line. Valid
        values  will depend on the Yoctopuce device model featuring
        the serial port feature.  Check your device documentation
        to find out which values are valid for that specific model.
        Trying to set an invalid value will have no effect.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a value among YSerialPort.VOLTAGELEVEL_OFF, YSerialPort.VOLTAGELEVEL_TTL3V,
        YSerialPort.VOLTAGELEVEL_TTL3VR, YSerialPort.VOLTAGELEVEL_TTL5V, YSerialPort.VOLTAGELEVEL_TTL5VR,
        YSerialPort.VOLTAGELEVEL_RS232, YSerialPort.VOLTAGELEVEL_RS485 and YSerialPort.VOLTAGELEVEL_TTL1V8
        corresponding to the voltage type used on the serial line

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("voltageLevel", rest_val)

    def get_serialMode(self):
        """
        Returns the serial port communication parameters, as a string such as
        "9600,8N1". The string includes the baud rate, the number of data bits,
        the parity, and the number of stop bits. An optional suffix is included
        if flow control is active: "CtsRts" for hardware handshake, "XOnXOff"
        for logical flow control and "Simplex" for acquiring a shared bus using
        the RTS line (as used by some RS485 adapters for instance).

        @return a string corresponding to the serial port communication parameters, as a string such as
                "9600,8N1"

        On failure, throws an exception or returns YSerialPort.SERIALMODE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSerialPort.SERIALMODE_INVALID
        res = self._serialMode
        return res

    def set_serialMode(self, newval):
        """
        Changes the serial port communication parameters, with a string such as
        "9600,8N1". The string includes the baud rate, the number of data bits,
        the parity, and the number of stop bits. An optional suffix can be added
        to enable flow control: "CtsRts" for hardware handshake, "XOnXOff"
        for logical flow control and "Simplex" for acquiring a shared bus using
        the RTS line (as used by some RS485 adapters for instance).
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the serial port communication parameters, with a string such as
                "9600,8N1"

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("serialMode", rest_val)

    @staticmethod
    def FindSerialPort(func):
        """
        Retrieves a serial port for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the serial port is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YSerialPort.isOnline() to test if the serial port is
        indeed online at a given time. In case of ambiguity when looking for
        a serial port by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the serial port, for instance
                RS232MK1.serialPort.

        @return a YSerialPort object allowing you to drive the serial port.
        """
        # obj
        obj = YFunction._FindFromCache("SerialPort", func)
        if obj is None:
            obj = YSerialPort(func)
            YFunction._AddToCache("SerialPort", func, obj)
        return obj

    def sendCommand(self, text):
        return self.set_command(text)

    def readLine(self):
        """
        Reads a single line (or message) from the receive buffer, starting at current stream position.
        This function is intended to be used when the serial port is configured for a message protocol,
        such as 'Line' mode or frame protocols.

        If data at current stream position is not available anymore in the receive buffer,
        the function returns the oldest available line and moves the stream position just after.
        If no new full line is received, the function returns an empty line.

        @return a string with a single line of text

        On failure, throws an exception or returns a negative error code.
        """
        # url
        # msgbin
        msgarr = []
        # msglen
        # res

        url = "rxmsg.json?pos=" + str(int(self._rxptr)) + "&len=1&maxw=1"
        msgbin = self._download(url)
        msgarr = self._json_get_array(msgbin)
        msglen = len(msgarr)
        if msglen == 0:
            return ""
        # // last element of array is the new position
        msglen = msglen - 1
        self._rxptr = YAPI._atoi(msgarr[msglen])
        if msglen == 0:
            return ""
        res = self._json_get_string(YString2Byte(msgarr[0]))
        return res

    def readMessages(self, pattern, maxWait):
        """
        Searches for incoming messages in the serial port receive buffer matching a given pattern,
        starting at current position. This function will only compare and return printable characters
        in the message strings. Binary protocols are handled as hexadecimal strings.

        The search returns all messages matching the expression provided as argument in the buffer.
        If no matching message is found, the search waits for one up to the specified maximum timeout
        (in milliseconds).

        @param pattern : a limited regular expression describing the expected message format,
                or an empty string if all messages should be returned (no filtering).
                When using binary protocols, the format applies to the hexadecimal
                representation of the message.
        @param maxWait : the maximum number of milliseconds to wait for a message if none is found
                in the receive buffer.

        @return an array of strings containing the messages found, if any.
                Binary messages are converted to hexadecimal representation.

        On failure, throws an exception or returns an empty array.
        """
        # url
        # msgbin
        msgarr = []
        # msglen
        res = []
        # idx

        url = "rxmsg.json?pos=" + str(int(self._rxptr)) + "&maxw=" + str(int(maxWait)) + "&pat=" + pattern
        msgbin = self._download(url)
        msgarr = self._json_get_array(msgbin)
        msglen = len(msgarr)
        if msglen == 0:
            return res
        # // last element of array is the new position
        msglen = msglen - 1
        self._rxptr = YAPI._atoi(msgarr[msglen])
        idx = 0

        while idx < msglen:
            res.append(self._json_get_string(YString2Byte(msgarr[idx])))
            idx = idx + 1

        return res

    def read_seek(self, absPos):
        """
        Changes the current internal stream position to the specified value. This function
        does not affect the device, it only changes the value stored in the API object
        for the next read operations.

        @param absPos : the absolute position index for next read operations.

        @return nothing.
        """
        self._rxptr = absPos
        return YAPI.SUCCESS

    def read_tell(self):
        """
        Returns the current absolute stream position pointer of the API object.

        @return the absolute position index for next read operations.
        """
        return self._rxptr

    def read_avail(self):
        """
        Returns the number of bytes available to read in the input buffer starting from the
        current absolute stream position pointer of the API object.

        @return the number of bytes available to read
        """
        # buff
        # bufflen
        # res

        buff = self._download("rxcnt.bin?pos=" + str(int(self._rxptr)))
        bufflen = len(buff) - 1
        while (bufflen > 0) and (YGetByte(buff, bufflen) != 64):
            bufflen = bufflen - 1
        res = YAPI._atoi((YByte2String(buff))[0: 0 + bufflen])
        return res

    def queryLine(self, query, maxWait):
        """
        Sends a text line query to the serial port, and reads the reply, if any.
        This function is intended to be used when the serial port is configured for 'Line' protocol.

        @param query : the line query to send (without CR/LF)
        @param maxWait : the maximum number of milliseconds to wait for a reply.

        @return the next text line received after sending the text query, as a string.
                Additional lines can be obtained by calling readLine or readMessages.

        On failure, throws an exception or returns an empty string.
        """
        # url
        # msgbin
        msgarr = []
        # msglen
        # res

        url = "rxmsg.json?len=1&maxw=" + str(int(maxWait)) + "&cmd=!" + self._escapeAttr(query)
        msgbin = self._download(url)
        msgarr = self._json_get_array(msgbin)
        msglen = len(msgarr)
        if msglen == 0:
            return ""
        # // last element of array is the new position
        msglen = msglen - 1
        self._rxptr = YAPI._atoi(msgarr[msglen])
        if msglen == 0:
            return ""
        res = self._json_get_string(YString2Byte(msgarr[0]))
        return res

    def queryHex(self, hexString, maxWait):
        """
        Sends a binary message to the serial port, and reads the reply, if any.
        This function is intended to be used when the serial port is configured for
        Frame-based protocol.

        @param hexString : the message to send, coded in hexadecimal
        @param maxWait : the maximum number of milliseconds to wait for a reply.

        @return the next frame received after sending the message, as a hex string.
                Additional frames can be obtained by calling readHex or readMessages.

        On failure, throws an exception or returns an empty string.
        """
        # url
        # msgbin
        msgarr = []
        # msglen
        # res

        url = "rxmsg.json?len=1&maxw=" + str(int(maxWait)) + "&cmd=$" + hexString
        msgbin = self._download(url)
        msgarr = self._json_get_array(msgbin)
        msglen = len(msgarr)
        if msglen == 0:
            return ""
        # // last element of array is the new position
        msglen = msglen - 1
        self._rxptr = YAPI._atoi(msgarr[msglen])
        if msglen == 0:
            return ""
        res = self._json_get_string(YString2Byte(msgarr[0]))
        return res

    def uploadJob(self, jobfile, jsonDef):
        """
        Saves the job definition string (JSON data) into a job file.
        The job file can be later enabled using selectJob().

        @param jobfile : name of the job file to save on the device filesystem
        @param jsonDef : a string containing a JSON definition of the job

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self._upload(jobfile, YString2Byte(jsonDef))
        return YAPI.SUCCESS

    def selectJob(self, jobfile):
        """
        Load and start processing the specified job file. The file must have
        been previously created using the user interface or uploaded on the
        device filesystem using the uploadJob() function.

        @param jobfile : name of the job file (on the device filesystem)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_currentJob(jobfile)

    def reset(self):
        """
        Clears the serial port buffer and resets counters to zero.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self._rxptr = 0
        self._rxbuffptr = 0
        self._rxbuff = bytearray(0)

        return self.sendCommand("Z")

    def writeByte(self, code):
        """
        Sends a single byte to the serial port.

        @param code : the byte to send

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("$" + ("%02X" % code))

    def writeStr(self, text):
        """
        Sends an ASCII string to the serial port, as is.

        @param text : the text string to send

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # buff
        # bufflen
        # idx
        # ch
        buff = YString2Byte(text)
        bufflen = len(buff)
        if bufflen < 100:
            # // if string is pure text, we can send it as a simple command (faster)
            ch = 0x20
            idx = 0
            while (idx < bufflen) and (ch != 0):
                ch = YGetByte(buff, idx)
                if (ch >= 0x20) and (ch < 0x7f):
                    idx = idx + 1
                else:
                    ch = 0
            if idx >= bufflen:
                return self.sendCommand("+" + text)
        # // send string using file upload
        return self._upload("txdata", buff)

    def writeBin(self, buff):
        """
        Sends a binary buffer to the serial port, as is.

        @param buff : the binary buffer to send

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self._upload("txdata", buff)

    def writeArray(self, byteList):
        """
        Sends a byte sequence (provided as a list of bytes) to the serial port.

        @param byteList : a list of byte codes

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # buff
        # bufflen
        # idx
        # hexb
        # res
        bufflen = len(byteList)
        buff = bytearray(bufflen)
        idx = 0
        while idx < bufflen:
            hexb = byteList[idx]
            buff[idx] = hexb
            idx = idx + 1

        res = self._upload("txdata", buff)
        return res

    def writeHex(self, hexString):
        """
        Sends a byte sequence (provided as a hexadecimal string) to the serial port.

        @param hexString : a string of hexadecimal byte codes

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # buff
        # bufflen
        # idx
        # hexb
        # res
        bufflen = len(hexString)
        if bufflen < 100:
            return self.sendCommand("$" + hexString)
        bufflen = ((bufflen) >> (1))
        buff = bytearray(bufflen)
        idx = 0
        while idx < bufflen:
            hexb = int((hexString)[2 * idx: 2 * idx + 2], 16)
            buff[idx] = hexb
            idx = idx + 1

        res = self._upload("txdata", buff)
        return res

    def writeLine(self, text):
        """
        Sends an ASCII string to the serial port, followed by a line break (CR LF).

        @param text : the text string to send

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # buff
        # bufflen
        # idx
        # ch
        buff = YString2Byte("" + text + "\r\n")
        bufflen = len(buff)-2
        if bufflen < 100:
            # // if string is pure text, we can send it as a simple command (faster)
            ch = 0x20
            idx = 0
            while (idx < bufflen) and (ch != 0):
                ch = YGetByte(buff, idx)
                if (ch >= 0x20) and (ch < 0x7f):
                    idx = idx + 1
                else:
                    ch = 0
            if idx >= bufflen:
                return self.sendCommand("!" + text)
        # // send string using file upload
        return self._upload("txdata", buff)

    def readByte(self):
        """
        Reads one byte from the receive buffer, starting at current stream position.
        If data at current stream position is not available anymore in the receive buffer,
        or if there is no data available yet, the function returns YAPI.NO_MORE_DATA.

        @return the next byte

        On failure, throws an exception or returns a negative error code.
        """
        # currpos
        # reqlen
        # buff
        # bufflen
        # mult
        # endpos
        # res
        # // first check if we have the requested character in the look-ahead buffer
        bufflen = len(self._rxbuff)
        if (self._rxptr >= self._rxbuffptr) and (self._rxptr < self._rxbuffptr+bufflen):
            res = YGetByte(self._rxbuff, self._rxptr-self._rxbuffptr)
            self._rxptr = self._rxptr + 1
            return res
        # // try to preload more than one byte to speed-up byte-per-byte access
        currpos = self._rxptr
        reqlen = 1024
        buff = self.readBin(reqlen)
        bufflen = len(buff)
        if self._rxptr == currpos+bufflen:
            res = YGetByte(buff, 0)
            self._rxptr = currpos+1
            self._rxbuffptr = currpos
            self._rxbuff = buff
            return res
        # // mixed bidirectional data, retry with a smaller block
        self._rxptr = currpos
        reqlen = 16
        buff = self.readBin(reqlen)
        bufflen = len(buff)
        if self._rxptr == currpos+bufflen:
            res = YGetByte(buff, 0)
            self._rxptr = currpos+1
            self._rxbuffptr = currpos
            self._rxbuff = buff
            return res
        # // still mixed, need to process character by character
        self._rxptr = currpos

        buff = self._download("rxdata.bin?pos=" + str(int(self._rxptr)) + "&len=1")
        bufflen = len(buff) - 1
        endpos = 0
        mult = 1
        while (bufflen > 0) and (YGetByte(buff, bufflen) != 64):
            endpos = endpos + mult * (YGetByte(buff, bufflen) - 48)
            mult = mult * 10
            bufflen = bufflen - 1
        self._rxptr = endpos
        if bufflen == 0:
            return YAPI.NO_MORE_DATA
        res = YGetByte(buff, 0)
        return res

    def readStr(self, nChars):
        """
        Reads data from the receive buffer as a string, starting at current stream position.
        If data at current stream position is not available anymore in the receive buffer, the
        function performs a short read.

        @param nChars : the maximum number of characters to read

        @return a string with receive buffer contents

        On failure, throws an exception or returns a negative error code.
        """
        # buff
        # bufflen
        # mult
        # endpos
        # res
        if nChars > 65535:
            nChars = 65535

        buff = self._download("rxdata.bin?pos=" + str(int(self._rxptr)) + "&len=" + str(int(nChars)))
        bufflen = len(buff) - 1
        endpos = 0
        mult = 1
        while (bufflen > 0) and (YGetByte(buff, bufflen) != 64):
            endpos = endpos + mult * (YGetByte(buff, bufflen) - 48)
            mult = mult * 10
            bufflen = bufflen - 1
        self._rxptr = endpos
        res = (YByte2String(buff))[0: 0 + bufflen]
        return res

    def readBin(self, nChars):
        """
        Reads data from the receive buffer as a binary buffer, starting at current stream position.
        If data at current stream position is not available anymore in the receive buffer, the
        function performs a short read.

        @param nChars : the maximum number of bytes to read

        @return a binary object with receive buffer contents

        On failure, throws an exception or returns a negative error code.
        """
        # buff
        # bufflen
        # mult
        # endpos
        # idx
        # res
        if nChars > 65535:
            nChars = 65535

        buff = self._download("rxdata.bin?pos=" + str(int(self._rxptr)) + "&len=" + str(int(nChars)))
        bufflen = len(buff) - 1
        endpos = 0
        mult = 1
        while (bufflen > 0) and (YGetByte(buff, bufflen) != 64):
            endpos = endpos + mult * (YGetByte(buff, bufflen) - 48)
            mult = mult * 10
            bufflen = bufflen - 1
        self._rxptr = endpos
        res = bytearray(bufflen)
        idx = 0
        while idx < bufflen:
            res[idx] = YGetByte(buff, idx)
            idx = idx + 1
        return res

    def readArray(self, nChars):
        """
        Reads data from the receive buffer as a list of bytes, starting at current stream position.
        If data at current stream position is not available anymore in the receive buffer, the
        function performs a short read.

        @param nChars : the maximum number of bytes to read

        @return a sequence of bytes with receive buffer contents

        On failure, throws an exception or returns an empty array.
        """
        # buff
        # bufflen
        # mult
        # endpos
        # idx
        # b
        res = []
        if nChars > 65535:
            nChars = 65535

        buff = self._download("rxdata.bin?pos=" + str(int(self._rxptr)) + "&len=" + str(int(nChars)))
        bufflen = len(buff) - 1
        endpos = 0
        mult = 1
        while (bufflen > 0) and (YGetByte(buff, bufflen) != 64):
            endpos = endpos + mult * (YGetByte(buff, bufflen) - 48)
            mult = mult * 10
            bufflen = bufflen - 1
        self._rxptr = endpos
        del res[:]
        idx = 0
        while idx < bufflen:
            b = YGetByte(buff, idx)
            res.append(b)
            idx = idx + 1

        return res

    def readHex(self, nBytes):
        """
        Reads data from the receive buffer as a hexadecimal string, starting at current stream position.
        If data at current stream position is not available anymore in the receive buffer, the
        function performs a short read.

        @param nBytes : the maximum number of bytes to read

        @return a string with receive buffer contents, encoded in hexadecimal

        On failure, throws an exception or returns a negative error code.
        """
        # buff
        # bufflen
        # mult
        # endpos
        # ofs
        # res
        if nBytes > 65535:
            nBytes = 65535

        buff = self._download("rxdata.bin?pos=" + str(int(self._rxptr)) + "&len=" + str(int(nBytes)))
        bufflen = len(buff) - 1
        endpos = 0
        mult = 1
        while (bufflen > 0) and (YGetByte(buff, bufflen) != 64):
            endpos = endpos + mult * (YGetByte(buff, bufflen) - 48)
            mult = mult * 10
            bufflen = bufflen - 1
        self._rxptr = endpos
        res = ""
        ofs = 0
        while ofs + 3 < bufflen:
            res = "" + res + "" + ("%02X" % YGetByte(buff, ofs)) + "" + ("%02X" % YGetByte(buff, ofs + 1)) + "" + ("%02X" % YGetByte(buff, ofs + 2)) + "" + ("%02X" % YGetByte(buff, ofs + 3))
            ofs = ofs + 4
        while ofs < bufflen:
            res = "" + res + "" + ("%02X" % YGetByte(buff, ofs))
            ofs = ofs + 1
        return res

    def set_RTS(self, val):
        """
        Manually sets the state of the RTS line. This function has no effect when
        hardware handshake is enabled, as the RTS line is driven automatically.

        @param val : 1 to turn RTS on, 0 to turn RTS off

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("R" + str(int(val)))

    def get_CTS(self):
        """
        Reads the level of the CTS line. The CTS line is usually driven by
        the RTS signal of the connected serial device.

        @return 1 if the CTS line is high, 0 if the CTS line is low.

        On failure, throws an exception or returns a negative error code.
        """
        # buff
        # res

        buff = self._download("cts.txt")
        if not (len(buff) == 1):
            self._throw(YAPI.IO_ERROR, "invalid CTS reply")
            return YAPI.IO_ERROR
        res = YGetByte(buff, 0) - 48
        return res

    def snoopMessages(self, maxWait):
        """
        Retrieves messages (both direction) in the serial port buffer, starting at current position.
        This function will only compare and return printable characters in the message strings.
        Binary protocols are handled as hexadecimal strings.

        If no message is found, the search waits for one up to the specified maximum timeout
        (in milliseconds).

        @param maxWait : the maximum number of milliseconds to wait for a message if none is found
                in the receive buffer.

        @return an array of YSnoopingRecord objects containing the messages found, if any.
                Binary messages are converted to hexadecimal representation.

        On failure, throws an exception or returns an empty array.
        """
        # url
        # msgbin
        msgarr = []
        # msglen
        res = []
        # idx

        url = "rxmsg.json?pos=" + str(int(self._rxptr)) + "&maxw=" + str(int(maxWait)) + "&t=0"
        msgbin = self._download(url)
        msgarr = self._json_get_array(msgbin)
        msglen = len(msgarr)
        if msglen == 0:
            return res
        # // last element of array is the new position
        msglen = msglen - 1
        self._rxptr = YAPI._atoi(msgarr[msglen])
        idx = 0

        while idx < msglen:
            res.append(YSnoopingRecord(msgarr[idx]))
            idx = idx + 1

        return res

    def writeMODBUS(self, hexString):
        """
        Sends a MODBUS message (provided as a hexadecimal string) to the serial port.
        The message must start with the slave address. The MODBUS CRC/LRC is
        automatically added by the function. This function does not wait for a reply.

        @param hexString : a hexadecimal message string, including device address but no CRC/LRC

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand(":" + hexString)

    def queryMODBUS(self, slaveNo, pduBytes):
        """
        Sends a message to a specified MODBUS slave connected to the serial port, and reads the
        reply, if any. The message is the PDU, provided as a vector of bytes.

        @param slaveNo : the address of the slave MODBUS device to query
        @param pduBytes : the message to send (PDU), as a vector of bytes. The first byte of the
                PDU is the MODBUS function code.

        @return the received reply, as a vector of bytes.

        On failure, throws an exception or returns an empty array (or a MODBUS error reply).
        """
        # funCode
        # nib
        # i
        # cmd
        # url
        # pat
        # msgs
        reps = []
        # rep
        res = []
        # replen
        # hexb
        funCode = pduBytes[0]
        nib = ((funCode) >> (4))
        pat = "" + ("%02X" % slaveNo) + "[" + ("%X" % nib) + "" + ("%X" % (nib+8)) + "]" + ("%X" % ((funCode) & (15))) + ".*"
        cmd = "" + ("%02X" % slaveNo) + "" + ("%02X" % funCode)
        i = 1
        while i < len(pduBytes):
            cmd = "" + cmd + "" + ("%02X" % ((pduBytes[i]) & (0xff)))
            i = i + 1

        url = "rxmsg.json?cmd=:" + cmd + "&pat=:" + pat
        msgs = self._download(url)
        reps = self._json_get_array(msgs)
        if not (len(reps) > 1):
            self._throw(YAPI.IO_ERROR, "no reply from MODBUS slave")
            return res
        if len(reps) > 1:
            rep = self._json_get_string(YString2Byte(reps[0]))
            replen = ((len(rep) - 3) >> (1))
            i = 0
            while i < replen:
                hexb = int((rep)[2 * i + 3: 2 * i + 3 + 2], 16)
                res.append(hexb)
                i = i + 1
            if res[0] != funCode:
                i = res[1]
                if not (i > 1):
                    self._throw(YAPI.NOT_SUPPORTED, "MODBUS error: unsupported function code")
                    return res
                if not (i > 2):
                    self._throw(YAPI.INVALID_ARGUMENT, "MODBUS error: illegal data address")
                    return res
                if not (i > 3):
                    self._throw(YAPI.INVALID_ARGUMENT, "MODBUS error: illegal data value")
                    return res
                if not (i > 4):
                    self._throw(YAPI.INVALID_ARGUMENT, "MODBUS error: failed to execute function")
                    return res
        return res

    def modbusReadBits(self, slaveNo, pduAddr, nBits):
        """
        Reads one or more contiguous internal bits (or coil status) from a MODBUS serial device.
        This method uses the MODBUS function code 0x01 (Read Coils).

        @param slaveNo : the address of the slave MODBUS device to query
        @param pduAddr : the relative address of the first bit/coil to read (zero-based)
        @param nBits : the number of bits/coils to read

        @return a vector of integers, each corresponding to one bit.

        On failure, throws an exception or returns an empty array.
        """
        pdu = []
        reply = []
        res = []
        # bitpos
        # idx
        # val
        # mask

        pdu.append(0x01)
        pdu.append(((pduAddr) >> (8)))
        pdu.append(((pduAddr) & (0xff)))
        pdu.append(((nBits) >> (8)))
        pdu.append(((nBits) & (0xff)))


        reply = self.queryMODBUS(slaveNo, pdu)
        if len(reply) == 0:
            return res
        if reply[0] != pdu[0]:
            return res

        bitpos = 0
        idx = 2
        val = reply[idx]
        mask = 1
        while bitpos < nBits:
            if ((val) & (mask)) == 0:
                res.append(0)
            else:
                res.append(1)
            bitpos = bitpos + 1
            if mask == 0x80:
                idx = idx + 1
                val = reply[idx]
                mask = 1
            else:
                mask = ((mask) << (1))

        return res

    def modbusReadInputBits(self, slaveNo, pduAddr, nBits):
        """
        Reads one or more contiguous input bits (or discrete inputs) from a MODBUS serial device.
        This method uses the MODBUS function code 0x02 (Read Discrete Inputs).

        @param slaveNo : the address of the slave MODBUS device to query
        @param pduAddr : the relative address of the first bit/input to read (zero-based)
        @param nBits : the number of bits/inputs to read

        @return a vector of integers, each corresponding to one bit.

        On failure, throws an exception or returns an empty array.
        """
        pdu = []
        reply = []
        res = []
        # bitpos
        # idx
        # val
        # mask

        pdu.append(0x02)
        pdu.append(((pduAddr) >> (8)))
        pdu.append(((pduAddr) & (0xff)))
        pdu.append(((nBits) >> (8)))
        pdu.append(((nBits) & (0xff)))


        reply = self.queryMODBUS(slaveNo, pdu)
        if len(reply) == 0:
            return res
        if reply[0] != pdu[0]:
            return res

        bitpos = 0
        idx = 2
        val = reply[idx]
        mask = 1
        while bitpos < nBits:
            if ((val) & (mask)) == 0:
                res.append(0)
            else:
                res.append(1)
            bitpos = bitpos + 1
            if mask == 0x80:
                idx = idx + 1
                val = reply[idx]
                mask = 1
            else:
                mask = ((mask) << (1))

        return res

    def modbusReadRegisters(self, slaveNo, pduAddr, nWords):
        """
        Reads one or more contiguous internal registers (holding registers) from a MODBUS serial device.
        This method uses the MODBUS function code 0x03 (Read Holding Registers).

        @param slaveNo : the address of the slave MODBUS device to query
        @param pduAddr : the relative address of the first holding register to read (zero-based)
        @param nWords : the number of holding registers to read

        @return a vector of integers, each corresponding to one 16-bit register value.

        On failure, throws an exception or returns an empty array.
        """
        pdu = []
        reply = []
        res = []
        # regpos
        # idx
        # val

        pdu.append(0x03)
        pdu.append(((pduAddr) >> (8)))
        pdu.append(((pduAddr) & (0xff)))
        pdu.append(((nWords) >> (8)))
        pdu.append(((nWords) & (0xff)))


        reply = self.queryMODBUS(slaveNo, pdu)
        if len(reply) == 0:
            return res
        if reply[0] != pdu[0]:
            return res

        regpos = 0
        idx = 2
        while regpos < nWords:
            val = ((reply[idx]) << (8))
            idx = idx + 1
            val = val + reply[idx]
            idx = idx + 1
            res.append(val)
            regpos = regpos + 1

        return res

    def modbusReadInputRegisters(self, slaveNo, pduAddr, nWords):
        """
        Reads one or more contiguous input registers (read-only registers) from a MODBUS serial device.
        This method uses the MODBUS function code 0x04 (Read Input Registers).

        @param slaveNo : the address of the slave MODBUS device to query
        @param pduAddr : the relative address of the first input register to read (zero-based)
        @param nWords : the number of input registers to read

        @return a vector of integers, each corresponding to one 16-bit input value.

        On failure, throws an exception or returns an empty array.
        """
        pdu = []
        reply = []
        res = []
        # regpos
        # idx
        # val

        pdu.append(0x04)
        pdu.append(((pduAddr) >> (8)))
        pdu.append(((pduAddr) & (0xff)))
        pdu.append(((nWords) >> (8)))
        pdu.append(((nWords) & (0xff)))


        reply = self.queryMODBUS(slaveNo, pdu)
        if len(reply) == 0:
            return res
        if reply[0] != pdu[0]:
            return res

        regpos = 0
        idx = 2
        while regpos < nWords:
            val = ((reply[idx]) << (8))
            idx = idx + 1
            val = val + reply[idx]
            idx = idx + 1
            res.append(val)
            regpos = regpos + 1

        return res

    def modbusWriteBit(self, slaveNo, pduAddr, value):
        """
        Sets a single internal bit (or coil) on a MODBUS serial device.
        This method uses the MODBUS function code 0x05 (Write Single Coil).

        @param slaveNo : the address of the slave MODBUS device to drive
        @param pduAddr : the relative address of the bit/coil to set (zero-based)
        @param value : the value to set (0 for OFF state, non-zero for ON state)

        @return the number of bits/coils affected on the device (1)

        On failure, throws an exception or returns zero.
        """
        pdu = []
        reply = []
        # res
        res = 0
        if value != 0:
            value = 0xff

        pdu.append(0x05)
        pdu.append(((pduAddr) >> (8)))
        pdu.append(((pduAddr) & (0xff)))
        pdu.append(value)
        pdu.append(0x00)


        reply = self.queryMODBUS(slaveNo, pdu)
        if len(reply) == 0:
            return res
        if reply[0] != pdu[0]:
            return res
        res = 1
        return res

    def modbusWriteBits(self, slaveNo, pduAddr, bits):
        """
        Sets several contiguous internal bits (or coils) on a MODBUS serial device.
        This method uses the MODBUS function code 0x0f (Write Multiple Coils).

        @param slaveNo : the address of the slave MODBUS device to drive
        @param pduAddr : the relative address of the first bit/coil to set (zero-based)
        @param bits : the vector of bits to be set (one integer per bit)

        @return the number of bits/coils affected on the device

        On failure, throws an exception or returns zero.
        """
        # nBits
        # nBytes
        # bitpos
        # val
        # mask
        pdu = []
        reply = []
        # res
        res = 0
        nBits = len(bits)
        nBytes = (((nBits + 7)) >> (3))

        pdu.append(0x0f)
        pdu.append(((pduAddr) >> (8)))
        pdu.append(((pduAddr) & (0xff)))
        pdu.append(((nBits) >> (8)))
        pdu.append(((nBits) & (0xff)))
        pdu.append(nBytes)
        bitpos = 0
        val = 0
        mask = 1
        while bitpos < nBits:
            if bits[bitpos] != 0:
                val = ((val) | (mask))
            bitpos = bitpos + 1
            if mask == 0x80:
                pdu.append(val)
                val = 0
                mask = 1
            else:
                mask = ((mask) << (1))
        if mask != 1:
            pdu.append(val)


        reply = self.queryMODBUS(slaveNo, pdu)
        if len(reply) == 0:
            return res
        if reply[0] != pdu[0]:
            return res
        res = ((reply[3]) << (8))
        res = res + reply[4]
        return res

    def modbusWriteRegister(self, slaveNo, pduAddr, value):
        """
        Sets a single internal register (or holding register) on a MODBUS serial device.
        This method uses the MODBUS function code 0x06 (Write Single Register).

        @param slaveNo : the address of the slave MODBUS device to drive
        @param pduAddr : the relative address of the register to set (zero-based)
        @param value : the 16 bit value to set

        @return the number of registers affected on the device (1)

        On failure, throws an exception or returns zero.
        """
        pdu = []
        reply = []
        # res
        res = 0

        pdu.append(0x06)
        pdu.append(((pduAddr) >> (8)))
        pdu.append(((pduAddr) & (0xff)))
        pdu.append(((value) >> (8)))
        pdu.append(((value) & (0xff)))


        reply = self.queryMODBUS(slaveNo, pdu)
        if len(reply) == 0:
            return res
        if reply[0] != pdu[0]:
            return res
        res = 1
        return res

    def modbusWriteRegisters(self, slaveNo, pduAddr, values):
        """
        Sets several contiguous internal registers (or holding registers) on a MODBUS serial device.
        This method uses the MODBUS function code 0x10 (Write Multiple Registers).

        @param slaveNo : the address of the slave MODBUS device to drive
        @param pduAddr : the relative address of the first internal register to set (zero-based)
        @param values : the vector of 16 bit values to set

        @return the number of registers affected on the device

        On failure, throws an exception or returns zero.
        """
        # nWords
        # nBytes
        # regpos
        # val
        pdu = []
        reply = []
        # res
        res = 0
        nWords = len(values)
        nBytes = 2 * nWords

        pdu.append(0x10)
        pdu.append(((pduAddr) >> (8)))
        pdu.append(((pduAddr) & (0xff)))
        pdu.append(((nWords) >> (8)))
        pdu.append(((nWords) & (0xff)))
        pdu.append(nBytes)
        regpos = 0
        while regpos < nWords:
            val = values[regpos]
            pdu.append(((val) >> (8)))
            pdu.append(((val) & (0xff)))
            regpos = regpos + 1


        reply = self.queryMODBUS(slaveNo, pdu)
        if len(reply) == 0:
            return res
        if reply[0] != pdu[0]:
            return res
        res = ((reply[3]) << (8))
        res = res + reply[4]
        return res

    def modbusWriteAndReadRegisters(self, slaveNo, pduWriteAddr, values, pduReadAddr, nReadWords):
        """
        Sets several contiguous internal registers (holding registers) on a MODBUS serial device,
        then performs a contiguous read of a set of (possibly different) internal registers.
        This method uses the MODBUS function code 0x17 (Read/Write Multiple Registers).

        @param slaveNo : the address of the slave MODBUS device to drive
        @param pduWriteAddr : the relative address of the first internal register to set (zero-based)
        @param values : the vector of 16 bit values to set
        @param pduReadAddr : the relative address of the first internal register to read (zero-based)
        @param nReadWords : the number of 16 bit values to read

        @return a vector of integers, each corresponding to one 16-bit register value read.

        On failure, throws an exception or returns an empty array.
        """
        # nWriteWords
        # nBytes
        # regpos
        # val
        # idx
        pdu = []
        reply = []
        res = []
        nWriteWords = len(values)
        nBytes = 2 * nWriteWords

        pdu.append(0x17)
        pdu.append(((pduReadAddr) >> (8)))
        pdu.append(((pduReadAddr) & (0xff)))
        pdu.append(((nReadWords) >> (8)))
        pdu.append(((nReadWords) & (0xff)))
        pdu.append(((pduWriteAddr) >> (8)))
        pdu.append(((pduWriteAddr) & (0xff)))
        pdu.append(((nWriteWords) >> (8)))
        pdu.append(((nWriteWords) & (0xff)))
        pdu.append(nBytes)
        regpos = 0
        while regpos < nWriteWords:
            val = values[regpos]
            pdu.append(((val) >> (8)))
            pdu.append(((val) & (0xff)))
            regpos = regpos + 1


        reply = self.queryMODBUS(slaveNo, pdu)
        if len(reply) == 0:
            return res
        if reply[0] != pdu[0]:
            return res

        regpos = 0
        idx = 2
        while regpos < nReadWords:
            val = ((reply[idx]) << (8))
            idx = idx + 1
            val = val + reply[idx]
            idx = idx + 1
            res.append(val)
            regpos = regpos + 1

        return res

    def nextSerialPort(self):
        """
        Continues the enumeration of serial ports started using yFirstSerialPort().
        Caution: You can't make any assumption about the returned serial ports order.
        If you want to find a specific a serial port, use SerialPort.findSerialPort()
        and a hardwareID or a logical name.

        @return a pointer to a YSerialPort object, corresponding to
                a serial port currently online, or a None pointer
                if there are no more serial ports to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YSerialPort.FindSerialPort(hwidRef.value)

#--- (end of generated code: YSerialPort implementation)

#--- (generated code: YSerialPort functions)

    @staticmethod
    def FirstSerialPort():
        """
        Starts the enumeration of serial ports currently accessible.
        Use the method YSerialPort.nextSerialPort() to iterate on
        next serial ports.

        @return a pointer to a YSerialPort object, corresponding to
                the first serial port currently online, or a None pointer
                if there are none.
        """
        devRef = YRefParam()
        neededsizeRef = YRefParam()
        serialRef = YRefParam()
        funcIdRef = YRefParam()
        funcNameRef = YRefParam()
        funcValRef = YRefParam()
        errmsgRef = YRefParam()
        size = YAPI.C_INTSIZE
        #noinspection PyTypeChecker,PyCallingNonCallable
        p = (ctypes.c_int * 1)()
        err = YAPI.apiGetFunctionsByClass("SerialPort", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YSerialPort.FindSerialPort(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YSerialPort functions)
