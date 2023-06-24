# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_spiport.py 40298 2020-05-05 08:37:49Z seb $
#
#  Implements yFindSpiPort(), the high-level API for SpiPort functions
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


#--- (YSpiPort class start)
#noinspection PyProtectedMember
class YSpiPort(YFunction):
    """
    The YSpiPort class allows you to fully drive a Yoctopuce SPI port.
    It can be used to send and receive data, and to configure communication
    parameters (baud rate, bit count, parity, flow control and protocol).
    Note that Yoctopuce SPI ports are not exposed as virtual COM ports.
    They are meant to be used in the same way as all Yoctopuce devices.

    """
    #--- (end of YSpiPort class start)
    #--- (YSpiPort return codes)
    #--- (end of YSpiPort return codes)
    #--- (YSpiPort dlldef)
    #--- (end of YSpiPort dlldef)
    #--- (YSpiPort yapiwrapper)
    #--- (end of YSpiPort yapiwrapper)
    #--- (YSpiPort definitions)
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
    SPIMODE_INVALID = YAPI.INVALID_STRING
    VOLTAGELEVEL_OFF = 0
    VOLTAGELEVEL_TTL3V = 1
    VOLTAGELEVEL_TTL3VR = 2
    VOLTAGELEVEL_TTL5V = 3
    VOLTAGELEVEL_TTL5VR = 4
    VOLTAGELEVEL_RS232 = 5
    VOLTAGELEVEL_RS485 = 6
    VOLTAGELEVEL_TTL1V8 = 7
    VOLTAGELEVEL_INVALID = -1
    SSPOLARITY_ACTIVE_LOW = 0
    SSPOLARITY_ACTIVE_HIGH = 1
    SSPOLARITY_INVALID = -1
    SHIFTSAMPLING_OFF = 0
    SHIFTSAMPLING_ON = 1
    SHIFTSAMPLING_INVALID = -1
    #--- (end of YSpiPort definitions)

    def __init__(self, func):
        super(YSpiPort, self).__init__(func)
        self._className = 'SpiPort'
        #--- (YSpiPort attributes)
        self._callback = None
        self._rxCount = YSpiPort.RXCOUNT_INVALID
        self._txCount = YSpiPort.TXCOUNT_INVALID
        self._errCount = YSpiPort.ERRCOUNT_INVALID
        self._rxMsgCount = YSpiPort.RXMSGCOUNT_INVALID
        self._txMsgCount = YSpiPort.TXMSGCOUNT_INVALID
        self._lastMsg = YSpiPort.LASTMSG_INVALID
        self._currentJob = YSpiPort.CURRENTJOB_INVALID
        self._startupJob = YSpiPort.STARTUPJOB_INVALID
        self._jobMaxTask = YSpiPort.JOBMAXTASK_INVALID
        self._jobMaxSize = YSpiPort.JOBMAXSIZE_INVALID
        self._command = YSpiPort.COMMAND_INVALID
        self._protocol = YSpiPort.PROTOCOL_INVALID
        self._voltageLevel = YSpiPort.VOLTAGELEVEL_INVALID
        self._spiMode = YSpiPort.SPIMODE_INVALID
        self._ssPolarity = YSpiPort.SSPOLARITY_INVALID
        self._shiftSampling = YSpiPort.SHIFTSAMPLING_INVALID
        self._rxptr = 0
        self._rxbuff = ''
        self._rxbuffptr = 0
        #--- (end of YSpiPort attributes)

    #--- (YSpiPort implementation)
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
        if json_val.has("spiMode"):
            self._spiMode = json_val.getString("spiMode")
        if json_val.has("ssPolarity"):
            self._ssPolarity = (json_val.getInt("ssPolarity") > 0 if 1 else 0)
        if json_val.has("shiftSampling"):
            self._shiftSampling = (json_val.getInt("shiftSampling") > 0 if 1 else 0)
        super(YSpiPort, self)._parseAttr(json_val)

    def get_rxCount(self):
        """
        Returns the total number of bytes received since last reset.

        @return an integer corresponding to the total number of bytes received since last reset

        On failure, throws an exception or returns YSpiPort.RXCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.RXCOUNT_INVALID
        res = self._rxCount
        return res

    def get_txCount(self):
        """
        Returns the total number of bytes transmitted since last reset.

        @return an integer corresponding to the total number of bytes transmitted since last reset

        On failure, throws an exception or returns YSpiPort.TXCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.TXCOUNT_INVALID
        res = self._txCount
        return res

    def get_errCount(self):
        """
        Returns the total number of communication errors detected since last reset.

        @return an integer corresponding to the total number of communication errors detected since last reset

        On failure, throws an exception or returns YSpiPort.ERRCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.ERRCOUNT_INVALID
        res = self._errCount
        return res

    def get_rxMsgCount(self):
        """
        Returns the total number of messages received since last reset.

        @return an integer corresponding to the total number of messages received since last reset

        On failure, throws an exception or returns YSpiPort.RXMSGCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.RXMSGCOUNT_INVALID
        res = self._rxMsgCount
        return res

    def get_txMsgCount(self):
        """
        Returns the total number of messages send since last reset.

        @return an integer corresponding to the total number of messages send since last reset

        On failure, throws an exception or returns YSpiPort.TXMSGCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.TXMSGCOUNT_INVALID
        res = self._txMsgCount
        return res

    def get_lastMsg(self):
        """
        Returns the latest message fully received (for Line and Frame protocols).

        @return a string corresponding to the latest message fully received (for Line and Frame protocols)

        On failure, throws an exception or returns YSpiPort.LASTMSG_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.LASTMSG_INVALID
        res = self._lastMsg
        return res

    def get_currentJob(self):
        """
        Returns the name of the job file currently in use.

        @return a string corresponding to the name of the job file currently in use

        On failure, throws an exception or returns YSpiPort.CURRENTJOB_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.CURRENTJOB_INVALID
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

        On failure, throws an exception or returns YSpiPort.STARTUPJOB_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.STARTUPJOB_INVALID
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

        On failure, throws an exception or returns YSpiPort.JOBMAXTASK_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.JOBMAXTASK_INVALID
        res = self._jobMaxTask
        return res

    def get_jobMaxSize(self):
        """
        Returns maximum size allowed for job files.

        @return an integer corresponding to maximum size allowed for job files

        On failure, throws an exception or returns YSpiPort.JOBMAXSIZE_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.JOBMAXSIZE_INVALID
        res = self._jobMaxSize
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.COMMAND_INVALID
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
        "Char" for a continuous ASCII stream or
        "Byte" for a continuous binary stream.

        @return a string corresponding to the type of protocol used over the serial line, as a string

        On failure, throws an exception or returns YSpiPort.PROTOCOL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.PROTOCOL_INVALID
        res = self._protocol
        return res

    def set_protocol(self, newval):
        """
        Changes the type of protocol used over the serial line.
        Possible values are "Line" for ASCII messages separated by CR and/or LF,
        "Frame:[timeout]ms" for binary messages separated by a delay time,
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

        @return a value among YSpiPort.VOLTAGELEVEL_OFF, YSpiPort.VOLTAGELEVEL_TTL3V,
        YSpiPort.VOLTAGELEVEL_TTL3VR, YSpiPort.VOLTAGELEVEL_TTL5V, YSpiPort.VOLTAGELEVEL_TTL5VR,
        YSpiPort.VOLTAGELEVEL_RS232, YSpiPort.VOLTAGELEVEL_RS485 and YSpiPort.VOLTAGELEVEL_TTL1V8
        corresponding to the voltage level used on the serial line

        On failure, throws an exception or returns YSpiPort.VOLTAGELEVEL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.VOLTAGELEVEL_INVALID
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

        @param newval : a value among YSpiPort.VOLTAGELEVEL_OFF, YSpiPort.VOLTAGELEVEL_TTL3V,
        YSpiPort.VOLTAGELEVEL_TTL3VR, YSpiPort.VOLTAGELEVEL_TTL5V, YSpiPort.VOLTAGELEVEL_TTL5VR,
        YSpiPort.VOLTAGELEVEL_RS232, YSpiPort.VOLTAGELEVEL_RS485 and YSpiPort.VOLTAGELEVEL_TTL1V8
        corresponding to the voltage type used on the serial line

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("voltageLevel", rest_val)

    def get_spiMode(self):
        """
        Returns the SPI port communication parameters, as a string such as
        "125000,0,msb". The string includes the baud rate, the SPI mode (between
        0 and 3) and the bit order.

        @return a string corresponding to the SPI port communication parameters, as a string such as
                "125000,0,msb"

        On failure, throws an exception or returns YSpiPort.SPIMODE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.SPIMODE_INVALID
        res = self._spiMode
        return res

    def set_spiMode(self, newval):
        """
        Changes the SPI port communication parameters, with a string such as
        "125000,0,msb". The string includes the baud rate, the SPI mode (between
        0 and 3) and the bit order.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the SPI port communication parameters, with a string such as
                "125000,0,msb"

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("spiMode", rest_val)

    def get_ssPolarity(self):
        """
        Returns the SS line polarity.

        @return either YSpiPort.SSPOLARITY_ACTIVE_LOW or YSpiPort.SSPOLARITY_ACTIVE_HIGH, according to the
        SS line polarity

        On failure, throws an exception or returns YSpiPort.SSPOLARITY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.SSPOLARITY_INVALID
        res = self._ssPolarity
        return res

    def set_ssPolarity(self, newval):
        """
        Changes the SS line polarity.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : either YSpiPort.SSPOLARITY_ACTIVE_LOW or YSpiPort.SSPOLARITY_ACTIVE_HIGH, according
        to the SS line polarity

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("ssPolarity", rest_val)

    def get_shiftSampling(self):
        """
        Returns true when the SDI line phase is shifted with regards to the SDO line.

        @return either YSpiPort.SHIFTSAMPLING_OFF or YSpiPort.SHIFTSAMPLING_ON, according to true when the
        SDI line phase is shifted with regards to the SDO line

        On failure, throws an exception or returns YSpiPort.SHIFTSAMPLING_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YSpiPort.SHIFTSAMPLING_INVALID
        res = self._shiftSampling
        return res

    def set_shiftSampling(self, newval):
        """
        Changes the SDI line sampling shift. When disabled, SDI line is
        sampled in the middle of data output time. When enabled, SDI line is
        samples at the end of data output time.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : either YSpiPort.SHIFTSAMPLING_OFF or YSpiPort.SHIFTSAMPLING_ON, according to the
        SDI line sampling shift

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("shiftSampling", rest_val)

    @staticmethod
    def FindSpiPort(func):
        """
        Retrieves a SPI port for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the SPI port is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YSpiPort.isOnline() to test if the SPI port is
        indeed online at a given time. In case of ambiguity when looking for
        a SPI port by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the SPI port, for instance
                YSPIMK01.spiPort.

        @return a YSpiPort object allowing you to drive the SPI port.
        """
        # obj
        obj = YFunction._FindFromCache("SpiPort", func)
        if obj is None:
            obj = YSpiPort(func)
            YFunction._AddToCache("SpiPort", func, obj)
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

    def set_SS(self, val):
        """
        Manually sets the state of the SS line. This function has no effect when
        the SS line is handled automatically.

        @param val : 1 to turn SS active, 0 to release SS.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("S" + str(int(val)))

    def nextSpiPort(self):
        """
        Continues the enumeration of SPI ports started using yFirstSpiPort().
        Caution: You can't make any assumption about the returned SPI ports order.
        If you want to find a specific a SPI port, use SpiPort.findSpiPort()
        and a hardwareID or a logical name.

        @return a pointer to a YSpiPort object, corresponding to
                a SPI port currently online, or a None pointer
                if there are no more SPI ports to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YSpiPort.FindSpiPort(hwidRef.value)

#--- (end of YSpiPort implementation)

#--- (YSpiPort functions)

    @staticmethod
    def FirstSpiPort():
        """
        Starts the enumeration of SPI ports currently accessible.
        Use the method YSpiPort.nextSpiPort() to iterate on
        next SPI ports.

        @return a pointer to a YSpiPort object, corresponding to
                the first SPI port currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("SpiPort", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YSpiPort.FindSpiPort(serialRef.value + "." + funcIdRef.value)

#--- (end of YSpiPort functions)
