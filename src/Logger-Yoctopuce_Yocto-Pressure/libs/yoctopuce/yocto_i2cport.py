# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_i2cport.py 39333 2020-01-30 10:05:40Z mvuilleu $
#
#  Implements yFindI2cPort(), the high-level API for I2cPort functions
#
#  - - - - - - - - - License information: - - - - - - - - -
#
#  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
#
#  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
#  non-exclusive license to use, modify, copy and integrate this
#  file into your software for the sole purpose of interfacing
#  with Yoctopuce products.
#
#  You may reproduce and distribute copies of this file in
#  source or object form, as long as the sole purpose of this
#  code is to interface with Yoctopuce products. You must retain
#  this notice in the distributed source file.
#
#  You should refer to Yoctopuce General Terms and Conditions
#  for additional information regarding your rights and
#  obligations.
#
#  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
#  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
#  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
#  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
#  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
#  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
#  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR
#  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT
#  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
#  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
#  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
#  WARRANTY, OR OTHERWISE.
#
# *********************************************************************


__docformat__ = 'restructuredtext en'
from yoctopuce.yocto_api import *


#--- (YI2cPort class start)
#noinspection PyProtectedMember
class YI2cPort(YFunction):
    """
    The YI2cPort classe allows you to fully drive a Yoctopuce I2C port.
    It can be used to send and receive data, and to configure communication
    parameters (baud rate, etc).
    Note that Yoctopuce I2C ports are not exposed as virtual COM ports.
    They are meant to be used in the same way as all Yoctopuce devices.

    """
    #--- (end of YI2cPort class start)
    #--- (YI2cPort return codes)
    #--- (end of YI2cPort return codes)
    #--- (YI2cPort dlldef)
    #--- (end of YI2cPort dlldef)
    #--- (YI2cPort yapiwrapper)
    #--- (end of YI2cPort yapiwrapper)
    #--- (YI2cPort definitions)
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
    I2CMODE_INVALID = YAPI.INVALID_STRING
    I2CVOLTAGELEVEL_OFF = 0
    I2CVOLTAGELEVEL_3V3 = 1
    I2CVOLTAGELEVEL_1V8 = 2
    I2CVOLTAGELEVEL_INVALID = -1
    #--- (end of YI2cPort definitions)

    def __init__(self, func):
        super(YI2cPort, self).__init__(func)
        self._className = 'I2cPort'
        #--- (YI2cPort attributes)
        self._callback = None
        self._rxCount = YI2cPort.RXCOUNT_INVALID
        self._txCount = YI2cPort.TXCOUNT_INVALID
        self._errCount = YI2cPort.ERRCOUNT_INVALID
        self._rxMsgCount = YI2cPort.RXMSGCOUNT_INVALID
        self._txMsgCount = YI2cPort.TXMSGCOUNT_INVALID
        self._lastMsg = YI2cPort.LASTMSG_INVALID
        self._currentJob = YI2cPort.CURRENTJOB_INVALID
        self._startupJob = YI2cPort.STARTUPJOB_INVALID
        self._jobMaxTask = YI2cPort.JOBMAXTASK_INVALID
        self._jobMaxSize = YI2cPort.JOBMAXSIZE_INVALID
        self._command = YI2cPort.COMMAND_INVALID
        self._protocol = YI2cPort.PROTOCOL_INVALID
        self._i2cVoltageLevel = YI2cPort.I2CVOLTAGELEVEL_INVALID
        self._i2cMode = YI2cPort.I2CMODE_INVALID
        self._rxptr = 0
        self._rxbuff = ''
        self._rxbuffptr = 0
        #--- (end of YI2cPort attributes)

    #--- (YI2cPort implementation)
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
        if json_val.has("i2cVoltageLevel"):
            self._i2cVoltageLevel = json_val.getInt("i2cVoltageLevel")
        if json_val.has("i2cMode"):
            self._i2cMode = json_val.getString("i2cMode")
        super(YI2cPort, self)._parseAttr(json_val)

    def get_rxCount(self):
        """
        Returns the total number of bytes received since last reset.

        @return an integer corresponding to the total number of bytes received since last reset

        On failure, throws an exception or returns YI2cPort.RXCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.RXCOUNT_INVALID
        res = self._rxCount
        return res

    def get_txCount(self):
        """
        Returns the total number of bytes transmitted since last reset.

        @return an integer corresponding to the total number of bytes transmitted since last reset

        On failure, throws an exception or returns YI2cPort.TXCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.TXCOUNT_INVALID
        res = self._txCount
        return res

    def get_errCount(self):
        """
        Returns the total number of communication errors detected since last reset.

        @return an integer corresponding to the total number of communication errors detected since last reset

        On failure, throws an exception or returns YI2cPort.ERRCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.ERRCOUNT_INVALID
        res = self._errCount
        return res

    def get_rxMsgCount(self):
        """
        Returns the total number of messages received since last reset.

        @return an integer corresponding to the total number of messages received since last reset

        On failure, throws an exception or returns YI2cPort.RXMSGCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.RXMSGCOUNT_INVALID
        res = self._rxMsgCount
        return res

    def get_txMsgCount(self):
        """
        Returns the total number of messages send since last reset.

        @return an integer corresponding to the total number of messages send since last reset

        On failure, throws an exception or returns YI2cPort.TXMSGCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.TXMSGCOUNT_INVALID
        res = self._txMsgCount
        return res

    def get_lastMsg(self):
        """
        Returns the latest message fully received (for Line and Frame protocols).

        @return a string corresponding to the latest message fully received (for Line and Frame protocols)

        On failure, throws an exception or returns YI2cPort.LASTMSG_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.LASTMSG_INVALID
        res = self._lastMsg
        return res

    def get_currentJob(self):
        """
        Returns the name of the job file currently in use.

        @return a string corresponding to the name of the job file currently in use

        On failure, throws an exception or returns YI2cPort.CURRENTJOB_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.CURRENTJOB_INVALID
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

        On failure, throws an exception or returns YI2cPort.STARTUPJOB_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.STARTUPJOB_INVALID
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

        On failure, throws an exception or returns YI2cPort.JOBMAXTASK_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.JOBMAXTASK_INVALID
        res = self._jobMaxTask
        return res

    def get_jobMaxSize(self):
        """
        Returns maximum size allowed for job files.

        @return an integer corresponding to maximum size allowed for job files

        On failure, throws an exception or returns YI2cPort.JOBMAXSIZE_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.JOBMAXSIZE_INVALID
        res = self._jobMaxSize
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    def get_protocol(self):
        """
        Returns the type of protocol used to send I2C messages, as a string.
        Possible values are
        "Line" for messages separated by LF or
        "Char" for continuous stream of codes.

        @return a string corresponding to the type of protocol used to send I2C messages, as a string

        On failure, throws an exception or returns YI2cPort.PROTOCOL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.PROTOCOL_INVALID
        res = self._protocol
        return res

    def set_protocol(self, newval):
        """
        Changes the type of protocol used to send I2C messages.
        Possible values are
        "Line" for messages separated by LF or
        "Char" for continuous stream of codes.
        The suffix "/[wait]ms" can be added to reduce the transmit rate so that there
        is always at lest the specified number of milliseconds between each message sent.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the type of protocol used to send I2C messages

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("protocol", rest_val)

    def get_i2cVoltageLevel(self):
        """
        Returns the voltage level used on the I2C bus.

        @return a value among YI2cPort.I2CVOLTAGELEVEL_OFF, YI2cPort.I2CVOLTAGELEVEL_3V3 and
        YI2cPort.I2CVOLTAGELEVEL_1V8 corresponding to the voltage level used on the I2C bus

        On failure, throws an exception or returns YI2cPort.I2CVOLTAGELEVEL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.I2CVOLTAGELEVEL_INVALID
        res = self._i2cVoltageLevel
        return res

    def set_i2cVoltageLevel(self, newval):
        """
        Changes the voltage level used on the I2C bus.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a value among YI2cPort.I2CVOLTAGELEVEL_OFF, YI2cPort.I2CVOLTAGELEVEL_3V3 and
        YI2cPort.I2CVOLTAGELEVEL_1V8 corresponding to the voltage level used on the I2C bus

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("i2cVoltageLevel", rest_val)

    def get_i2cMode(self):
        """
        Returns the I2C port communication parameters, as a string such as
        "400kbps,2000ms,NoRestart". The string includes the baud rate, the
        recovery delay after communications errors, and if needed the option
        NoRestart to use a Stop/Start sequence instead of the
        Restart state when performing read on the I2C bus.

        @return a string corresponding to the I2C port communication parameters, as a string such as
                "400kbps,2000ms,NoRestart"

        On failure, throws an exception or returns YI2cPort.I2CMODE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YI2cPort.I2CMODE_INVALID
        res = self._i2cMode
        return res

    def set_i2cMode(self, newval):
        """
        Changes the I2C port communication parameters, with a string such as
        "400kbps,2000ms". The string includes the baud rate, the
        recovery delay after communications errors, and if needed the option
        NoRestart to use a Stop/Start sequence instead of the
        Restart state when performing read on the I2C bus.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the I2C port communication parameters, with a string such as
                "400kbps,2000ms"

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("i2cMode", rest_val)

    @staticmethod
    def FindI2cPort(func):
        """
        Retrieves an I2C port for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the I2C port is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YI2cPort.isOnline() to test if the I2C port is
        indeed online at a given time. In case of ambiguity when looking for
        an I2C port by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the I2C port, for instance
                YI2CMK01.i2cPort.

        @return a YI2cPort object allowing you to drive the I2C port.
        """
        # obj
        obj = YFunction._FindFromCache("I2cPort", func)
        if obj is None:
            obj = YI2cPort(func)
            YFunction._AddToCache("I2cPort", func, obj)
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

    def i2cSendBin(self, slaveAddr, buff):
        """
        Sends a one-way message (provided as a a binary buffer) to a device on the I2C bus.
        This function checks and reports communication errors on the I2C bus.

        @param slaveAddr : the 7-bit address of the slave device (without the direction bit)
        @param buff : the binary buffer to be sent

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # nBytes
        # idx
        # val
        # msg
        # reply
        msg = "@" + ("%02x" % slaveAddr) + ":"
        nBytes = len(buff)
        idx = 0
        while idx < nBytes:
            val = YGetByte(buff, idx)
            msg = "" + msg + "" + ("%02x" % val)
            idx = idx + 1

        reply = self.queryLine(msg,1000)
        if not (len(reply) > 0):
            self._throw(YAPI.IO_ERROR, "No response from I2C device")
            return YAPI.IO_ERROR
        idx = reply.find("[N]!")
        if not (idx < 0):
            self._throw(YAPI.IO_ERROR, "No I2C ACK received")
            return YAPI.IO_ERROR
        idx = reply.find("!")
        if not (idx < 0):
            self._throw(YAPI.IO_ERROR, "I2C protocol error")
            return YAPI.IO_ERROR
        return YAPI.SUCCESS

    def i2cSendArray(self, slaveAddr, values):
        """
        Sends a one-way message (provided as a list of integer) to a device on the I2C bus.
        This function checks and reports communication errors on the I2C bus.

        @param slaveAddr : the 7-bit address of the slave device (without the direction bit)
        @param values : a list of data bytes to be sent

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # nBytes
        # idx
        # val
        # msg
        # reply
        msg = "@" + ("%02x" % slaveAddr) + ":"
        nBytes = len(values)
        idx = 0
        while idx < nBytes:
            val = values[idx]
            msg = "" + msg + "" + ("%02x" % val)
            idx = idx + 1

        reply = self.queryLine(msg,1000)
        if not (len(reply) > 0):
            self._throw(YAPI.IO_ERROR, "No response from I2C device")
            return YAPI.IO_ERROR
        idx = reply.find("[N]!")
        if not (idx < 0):
            self._throw(YAPI.IO_ERROR, "No I2C ACK received")
            return YAPI.IO_ERROR
        idx = reply.find("!")
        if not (idx < 0):
            self._throw(YAPI.IO_ERROR, "I2C protocol error")
            return YAPI.IO_ERROR
        return YAPI.SUCCESS

    def i2cSendAndReceiveBin(self, slaveAddr, buff, rcvCount):
        """
        Sends a one-way message (provided as a a binary buffer) to a device on the I2C bus,
        then read back the specified number of bytes from device.
        This function checks and reports communication errors on the I2C bus.

        @param slaveAddr : the 7-bit address of the slave device (without the direction bit)
        @param buff : the binary buffer to be sent
        @param rcvCount : the number of bytes to receive once the data bytes are sent

        @return a list of bytes with the data received from slave device.

        On failure, throws an exception or returns an empty binary buffer.
        """
        # nBytes
        # idx
        # val
        # msg
        # reply
        # rcvbytes
        msg = "@" + ("%02x" % slaveAddr) + ":"
        nBytes = len(buff)
        idx = 0
        while idx < nBytes:
            val = YGetByte(buff, idx)
            msg = "" + msg + "" + ("%02x" % val)
            idx = idx + 1
        idx = 0
        while idx < rcvCount:
            msg = "" + msg + "xx"
            idx = idx + 1

        reply = self.queryLine(msg,1000)
        rcvbytes = bytearray(0)
        if not (len(reply) > 0):
            self._throw(YAPI.IO_ERROR, "No response from I2C device")
            return rcvbytes
        idx = reply.find("[N]!")
        if not (idx < 0):
            self._throw(YAPI.IO_ERROR, "No I2C ACK received")
            return rcvbytes
        idx = reply.find("!")
        if not (idx < 0):
            self._throw(YAPI.IO_ERROR, "I2C protocol error")
            return rcvbytes
        reply = (reply)[len(reply)-2*rcvCount: len(reply)-2*rcvCount + 2*rcvCount]
        rcvbytes = YAPI._hexStrToBin(reply)
        return rcvbytes

    def i2cSendAndReceiveArray(self, slaveAddr, values, rcvCount):
        """
        Sends a one-way message (provided as a list of integer) to a device on the I2C bus,
        then read back the specified number of bytes from device.
        This function checks and reports communication errors on the I2C bus.

        @param slaveAddr : the 7-bit address of the slave device (without the direction bit)
        @param values : a list of data bytes to be sent
        @param rcvCount : the number of bytes to receive once the data bytes are sent

        @return a list of bytes with the data received from slave device.

        On failure, throws an exception or returns an empty array.
        """
        # nBytes
        # idx
        # val
        # msg
        # reply
        # rcvbytes
        res = []
        msg = "@" + ("%02x" % slaveAddr) + ":"
        nBytes = len(values)
        idx = 0
        while idx < nBytes:
            val = values[idx]
            msg = "" + msg + "" + ("%02x" % val)
            idx = idx + 1
        idx = 0
        while idx < rcvCount:
            msg = "" + msg + "xx"
            idx = idx + 1

        reply = self.queryLine(msg,1000)
        if not (len(reply) > 0):
            self._throw(YAPI.IO_ERROR, "No response from I2C device")
            return res
        idx = reply.find("[N]!")
        if not (idx < 0):
            self._throw(YAPI.IO_ERROR, "No I2C ACK received")
            return res
        idx = reply.find("!")
        if not (idx < 0):
            self._throw(YAPI.IO_ERROR, "I2C protocol error")
            return res
        reply = (reply)[len(reply)-2*rcvCount: len(reply)-2*rcvCount + 2*rcvCount]
        rcvbytes = YAPI._hexStrToBin(reply)
        del res[:]
        idx = 0
        while idx < rcvCount:
            val = YGetByte(rcvbytes, idx)
            res.append(val)
            idx = idx + 1

        return res

    def writeStr(self, codes):
        """
        Sends a text-encoded I2C code stream to the I2C bus, as is.
        An I2C code stream is a string made of hexadecimal data bytes,
        but that may also include the I2C state transitions code:
        "{S}" to emit a start condition,
        "{R}" for a repeated start condition,
        "{P}" for a stop condition,
        "xx" for receiving a data byte,
        "{A}" to ack a data byte received and
        "{N}" to nack a data byte received.
        If a newline ("\n") is included in the stream, the message
        will be terminated and a newline will also be added to the
        receive stream.

        @param codes : the code stream to send

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # bufflen
        # buff
        # idx
        # ch
        buff = YString2Byte(codes)
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
                return self.sendCommand("+" + codes)
        # // send string using file upload
        return self._upload("txdata", buff)

    def writeLine(self, codes):
        """
        Sends a text-encoded I2C code stream to the I2C bus, and terminate
        the message en relâchant le bus.
        An I2C code stream is a string made of hexadecimal data bytes,
        but that may also include the I2C state transitions code:
        "{S}" to emit a start condition,
        "{R}" for a repeated start condition,
        "{P}" for a stop condition,
        "xx" for receiving a data byte,
        "{A}" to ack a data byte received and
        "{N}" to nack a data byte received.
        At the end of the stream, a stop condition is added if missing
        and a newline is added to the receive buffer as well.

        @param codes : the code stream to send

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # bufflen
        # buff
        bufflen = len(codes)
        if bufflen < 100:
            return self.sendCommand("!" + codes)
        # // send string using file upload
        buff = YString2Byte("" + codes + "\n")
        return self._upload("txdata", buff)

    def writeByte(self, code):
        """
        Sends a single byte to the I2C bus. Depending on the I2C bus state, the byte
        will be interpreted as an address byte or a data byte.

        @param code : the byte to send

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("+" + ("%02X" % code))

    def writeHex(self, hexString):
        """
        Sends a byte sequence (provided as a hexadecimal string) to the I2C bus.
        Depending on the I2C bus state, the first byte will be interpreted as an
        address byte or a data byte.

        @param hexString : a string of hexadecimal byte codes

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # bufflen
        # buff
        bufflen = len(hexString)
        if bufflen < 100:
            return self.sendCommand("+" + hexString)
        buff = YString2Byte(hexString)

        return self._upload("txdata", buff)

    def writeBin(self, buff):
        """
        Sends a binary buffer to the I2C bus, as is.
        Depending on the I2C bus state, the first byte will be interpreted
        as an address byte or a data byte.

        @param buff : the binary buffer to send

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # nBytes
        # idx
        # val
        # msg
        msg = ""
        nBytes = len(buff)
        idx = 0
        while idx < nBytes:
            val = YGetByte(buff, idx)
            msg = "" + msg + "" + ("%02x" % val)
            idx = idx + 1

        return self.writeHex(msg)

    def writeArray(self, byteList):
        """
        Sends a byte sequence (provided as a list of bytes) to the I2C bus.
        Depending on the I2C bus state, the first byte will be interpreted as an
        address byte or a data byte.

        @param byteList : a list of byte codes

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # nBytes
        # idx
        # val
        # msg
        msg = ""
        nBytes = len(byteList)
        idx = 0
        while idx < nBytes:
            val = byteList[idx]
            msg = "" + msg + "" + ("%02x" % val)
            idx = idx + 1

        return self.writeHex(msg)

    def nextI2cPort(self):
        """
        Continues the enumeration of I2C ports started using yFirstI2cPort().
        Caution: You can't make any assumption about the returned I2C ports order.
        If you want to find a specific an I2C port, use I2cPort.findI2cPort()
        and a hardwareID or a logical name.

        @return a pointer to a YI2cPort object, corresponding to
                an I2C port currently online, or a None pointer
                if there are no more I2C ports to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YI2cPort.FindI2cPort(hwidRef.value)

#--- (end of YI2cPort implementation)

#--- (YI2cPort functions)

    @staticmethod
    def FirstI2cPort():
        """
        Starts the enumeration of I2C ports currently accessible.
        Use the method YI2cPort.nextI2cPort() to iterate on
        next I2C ports.

        @return a pointer to a YI2cPort object, corresponding to
                the first I2C port currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("I2cPort", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YI2cPort.FindI2cPort(serialRef.value + "." + funcIdRef.value)

#--- (end of YI2cPort functions)
