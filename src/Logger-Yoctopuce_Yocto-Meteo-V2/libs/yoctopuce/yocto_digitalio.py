# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_digitalio.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindDigitalIO(), the high-level API for DigitalIO functions
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


#--- (YDigitalIO class start)
#noinspection PyProtectedMember
class YDigitalIO(YFunction):
    """
    The YDigitalIO class allows you drive a Yoctopuce digital input/output port.
    It can be used to setup the direction of each channel, to read the state of each channel
    and to switch the state of each channel configures as an output.
    You can work on all channels at once, or one by one. Most functions
    use a binary representation for channels where bit 0 matches channel #0 , bit 1 matches channel
    #1 and so on. If you are not familiar with numbers binary representation, you will find more
    information here: https://en.wikipedia.org/wiki/Binary_number#Representation. It is also possible
    to automatically generate short pulses of a determined duration. Electrical behavior
    of each I/O can be modified (open drain and reverse polarity).

    """
    #--- (end of YDigitalIO class start)
    #--- (YDigitalIO return codes)
    #--- (end of YDigitalIO return codes)
    #--- (YDigitalIO dlldef)
    #--- (end of YDigitalIO dlldef)
    #--- (YDigitalIO yapiwrapper)
    #--- (end of YDigitalIO yapiwrapper)
    #--- (YDigitalIO definitions)
    PORTSTATE_INVALID = YAPI.INVALID_UINT
    PORTDIRECTION_INVALID = YAPI.INVALID_UINT
    PORTOPENDRAIN_INVALID = YAPI.INVALID_UINT
    PORTPOLARITY_INVALID = YAPI.INVALID_UINT
    PORTDIAGS_INVALID = YAPI.INVALID_UINT
    PORTSIZE_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    OUTPUTVOLTAGE_USB_5V = 0
    OUTPUTVOLTAGE_USB_3V = 1
    OUTPUTVOLTAGE_EXT_V = 2
    OUTPUTVOLTAGE_INVALID = -1
    #--- (end of YDigitalIO definitions)

    def __init__(self, func):
        super(YDigitalIO, self).__init__(func)
        self._className = 'DigitalIO'
        #--- (YDigitalIO attributes)
        self._callback = None
        self._portState = YDigitalIO.PORTSTATE_INVALID
        self._portDirection = YDigitalIO.PORTDIRECTION_INVALID
        self._portOpenDrain = YDigitalIO.PORTOPENDRAIN_INVALID
        self._portPolarity = YDigitalIO.PORTPOLARITY_INVALID
        self._portDiags = YDigitalIO.PORTDIAGS_INVALID
        self._portSize = YDigitalIO.PORTSIZE_INVALID
        self._outputVoltage = YDigitalIO.OUTPUTVOLTAGE_INVALID
        self._command = YDigitalIO.COMMAND_INVALID
        #--- (end of YDigitalIO attributes)

    #--- (YDigitalIO implementation)
    def _parseAttr(self, json_val):
        if json_val.has("portState"):
            self._portState = json_val.getInt("portState")
        if json_val.has("portDirection"):
            self._portDirection = json_val.getInt("portDirection")
        if json_val.has("portOpenDrain"):
            self._portOpenDrain = json_val.getInt("portOpenDrain")
        if json_val.has("portPolarity"):
            self._portPolarity = json_val.getInt("portPolarity")
        if json_val.has("portDiags"):
            self._portDiags = json_val.getInt("portDiags")
        if json_val.has("portSize"):
            self._portSize = json_val.getInt("portSize")
        if json_val.has("outputVoltage"):
            self._outputVoltage = json_val.getInt("outputVoltage")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YDigitalIO, self)._parseAttr(json_val)

    def get_portState(self):
        """
        Returns the digital IO port state as an integer with each bit
        representing a channel.
        value 0 = 0b00000000 -> all channels are OFF
        value 1 = 0b00000001 -> channel #0 is ON
        value 2 = 0b00000010 -> channel #1 is ON
        value 3 = 0b00000011 -> channels #0 and #1 are ON
        value 4 = 0b00000100 -> channel #2 is ON
        and so on...

        @return an integer corresponding to the digital IO port state as an integer with each bit
                representing a channel

        On failure, throws an exception or returns YDigitalIO.PORTSTATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDigitalIO.PORTSTATE_INVALID
        res = self._portState
        return res

    def set_portState(self, newval):
        """
        Changes the state of all digital IO port's channels at once: the parameter
        is an integer where each bit represents a channel, with bit 0 matching channel #0.
        To set all channels to  0 -> 0b00000000 -> parameter = 0
        To set channel #0 to 1 -> 0b00000001 -> parameter =  1
        To set channel #1 to  1 -> 0b00000010 -> parameter = 2
        To set channel #0 and #1 -> 0b00000011 -> parameter =  3
        To set channel #2 to 1 -> 0b00000100 -> parameter =  4
        an so on....
        Only channels configured as outputs will be affecter, according to the value
        configured using set_portDirection.

        @param newval : an integer corresponding to the state of all digital IO port's channels at once: the parameter
                is an integer where each bit represents a channel, with bit 0 matching channel #0

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("portState", rest_val)

    def get_portDirection(self):
        """
        Returns the I/O direction of all channels of the port (bitmap): 0 makes a bit an input, 1 makes it an output.

        @return an integer corresponding to the I/O direction of all channels of the port (bitmap): 0 makes
        a bit an input, 1 makes it an output

        On failure, throws an exception or returns YDigitalIO.PORTDIRECTION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDigitalIO.PORTDIRECTION_INVALID
        res = self._portDirection
        return res

    def set_portDirection(self, newval):
        """
        Changes the I/O direction of all channels of the port (bitmap): 0 makes a bit an input, 1 makes it an output.
        Remember to call the saveToFlash() method  to make sure the setting is kept after a reboot.

        @param newval : an integer corresponding to the I/O direction of all channels of the port (bitmap):
        0 makes a bit an input, 1 makes it an output

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("portDirection", rest_val)

    def get_portOpenDrain(self):
        """
        Returns the electrical interface for each bit of the port. For each bit set to 0  the matching I/O
        works in the regular,
        intuitive way, for each bit set to 1, the I/O works in reverse mode.

        @return an integer corresponding to the electrical interface for each bit of the port

        On failure, throws an exception or returns YDigitalIO.PORTOPENDRAIN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDigitalIO.PORTOPENDRAIN_INVALID
        res = self._portOpenDrain
        return res

    def set_portOpenDrain(self, newval):
        """
        Changes the electrical interface for each bit of the port. 0 makes a bit a regular input/output, 1 makes
        it an open-drain (open-collector) input/output. Remember to call the
        saveToFlash() method  to make sure the setting is kept after a reboot.

        @param newval : an integer corresponding to the electrical interface for each bit of the port

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("portOpenDrain", rest_val)

    def get_portPolarity(self):
        """
        Returns the polarity of all the bits of the port.  For each bit set to 0, the matching I/O works the regular,
        intuitive way; for each bit set to 1, the I/O works in reverse mode.

        @return an integer corresponding to the polarity of all the bits of the port

        On failure, throws an exception or returns YDigitalIO.PORTPOLARITY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDigitalIO.PORTPOLARITY_INVALID
        res = self._portPolarity
        return res

    def set_portPolarity(self, newval):
        """
        Changes the polarity of all the bits of the port: For each bit set to 0, the matching I/O works the regular,
        intuitive way; for each bit set to 1, the I/O works in reverse mode.
        Remember to call the saveToFlash() method  to make sure the setting will be kept after a reboot.

        @param newval : an integer corresponding to the polarity of all the bits of the port: For each bit
        set to 0, the matching I/O works the regular,
                intuitive way; for each bit set to 1, the I/O works in reverse mode

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("portPolarity", rest_val)

    def get_portDiags(self):
        """
        Returns the port state diagnostics (Yocto-IO and Yocto-MaxiIO-V2 only). Bit 0 indicates a shortcut on
        output 0, etc. Bit 8 indicates a power failure, and bit 9 signals overheating (overcurrent).
        During normal use, all diagnostic bits should stay clear.

        @return an integer corresponding to the port state diagnostics (Yocto-IO and Yocto-MaxiIO-V2 only)

        On failure, throws an exception or returns YDigitalIO.PORTDIAGS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDigitalIO.PORTDIAGS_INVALID
        res = self._portDiags
        return res

    def get_portSize(self):
        """
        Returns the number of bits (i.e. channels)implemented in the I/O port.

        @return an integer corresponding to the number of bits (i.e

        On failure, throws an exception or returns YDigitalIO.PORTSIZE_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDigitalIO.PORTSIZE_INVALID
        res = self._portSize
        return res

    def get_outputVoltage(self):
        """
        Returns the voltage source used to drive output bits.

        @return a value among YDigitalIO.OUTPUTVOLTAGE_USB_5V, YDigitalIO.OUTPUTVOLTAGE_USB_3V and
        YDigitalIO.OUTPUTVOLTAGE_EXT_V corresponding to the voltage source used to drive output bits

        On failure, throws an exception or returns YDigitalIO.OUTPUTVOLTAGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDigitalIO.OUTPUTVOLTAGE_INVALID
        res = self._outputVoltage
        return res

    def set_outputVoltage(self, newval):
        """
        Changes the voltage source used to drive output bits.
        Remember to call the saveToFlash() method  to make sure the setting is kept after a reboot.

        @param newval : a value among YDigitalIO.OUTPUTVOLTAGE_USB_5V, YDigitalIO.OUTPUTVOLTAGE_USB_3V and
        YDigitalIO.OUTPUTVOLTAGE_EXT_V corresponding to the voltage source used to drive output bits

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("outputVoltage", rest_val)

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDigitalIO.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindDigitalIO(func):
        """
        Retrieves a digital IO port for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the digital IO port is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YDigitalIO.isOnline() to test if the digital IO port is
        indeed online at a given time. In case of ambiguity when looking for
        a digital IO port by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the digital IO port, for instance
                YMINIIO0.digitalIO.

        @return a YDigitalIO object allowing you to drive the digital IO port.
        """
        # obj
        obj = YFunction._FindFromCache("DigitalIO", func)
        if obj is None:
            obj = YDigitalIO(func)
            YFunction._AddToCache("DigitalIO", func, obj)
        return obj

    def set_bitState(self, bitno, bitstate):
        """
        Sets a single bit (i.e. channel) of the I/O port.

        @param bitno : the bit number; lowest bit has index 0
        @param bitstate : the state of the bit (1 or 0)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        if not (bitstate >= 0):
            self._throw(YAPI.INVALID_ARGUMENT, "invalid bit state")
            return YAPI.INVALID_ARGUMENT
        if not (bitstate <= 1):
            self._throw(YAPI.INVALID_ARGUMENT, "invalid bit state")
            return YAPI.INVALID_ARGUMENT
        return self.set_command("" + str(chr(82+bitstate)) + "" + str(int(bitno)))

    def get_bitState(self, bitno):
        """
        Returns the state of a single bit (i.e. channel)  of the I/O port.

        @param bitno : the bit number; lowest bit has index 0

        @return the bit state (0 or 1)

        On failure, throws an exception or returns a negative error code.
        """
        # portVal
        portVal = self.get_portState()
        return ((((portVal) >> (bitno))) & (1))

    def toggle_bitState(self, bitno):
        """
        Reverts a single bit (i.e. channel) of the I/O port.

        @param bitno : the bit number; lowest bit has index 0

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("T" + str(int(bitno)))

    def set_bitDirection(self, bitno, bitdirection):
        """
        Changes  the direction of a single bit (i.e. channel) from the I/O port.

        @param bitno : the bit number; lowest bit has index 0
        @param bitdirection : direction to set, 0 makes the bit an input, 1 makes it an output.
                Remember to call the   saveToFlash() method to make sure the setting is kept after a reboot.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        if not (bitdirection >= 0):
            self._throw(YAPI.INVALID_ARGUMENT, "invalid direction")
            return YAPI.INVALID_ARGUMENT
        if not (bitdirection <= 1):
            self._throw(YAPI.INVALID_ARGUMENT, "invalid direction")
            return YAPI.INVALID_ARGUMENT
        return self.set_command("" + str(chr(73+6*bitdirection)) + "" + str(int(bitno)))

    def get_bitDirection(self, bitno):
        """
        Returns the direction of a single bit (i.e. channel) from the I/O port (0 means the bit is an
        input, 1  an output).

        @param bitno : the bit number; lowest bit has index 0

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # portDir
        portDir = self.get_portDirection()
        return ((((portDir) >> (bitno))) & (1))

    def set_bitPolarity(self, bitno, bitpolarity):
        """
        Changes the polarity of a single bit from the I/O port.

        @param bitno : the bit number; lowest bit has index 0.
        @param bitpolarity : polarity to set, 0 makes the I/O work in regular mode, 1 makes the I/O  works
        in reverse mode.
                Remember to call the   saveToFlash() method to make sure the setting is kept after a reboot.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        if not (bitpolarity >= 0):
            self._throw(YAPI.INVALID_ARGUMENT, "invalid bit polarity")
            return YAPI.INVALID_ARGUMENT
        if not (bitpolarity <= 1):
            self._throw(YAPI.INVALID_ARGUMENT, "invalid bit polarity")
            return YAPI.INVALID_ARGUMENT
        return self.set_command("" + str(chr(110+4*bitpolarity)) + "" + str(int(bitno)))

    def get_bitPolarity(self, bitno):
        """
        Returns the polarity of a single bit from the I/O port (0 means the I/O works in regular mode, 1
        means the I/O  works in reverse mode).

        @param bitno : the bit number; lowest bit has index 0

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # portPol
        portPol = self.get_portPolarity()
        return ((((portPol) >> (bitno))) & (1))

    def set_bitOpenDrain(self, bitno, opendrain):
        """
        Changes  the electrical interface of a single bit from the I/O port.

        @param bitno : the bit number; lowest bit has index 0
        @param opendrain : 0 makes a bit a regular input/output, 1 makes
                it an open-drain (open-collector) input/output. Remember to call the
                saveToFlash() method to make sure the setting is kept after a reboot.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        if not (opendrain >= 0):
            self._throw(YAPI.INVALID_ARGUMENT, "invalid state")
            return YAPI.INVALID_ARGUMENT
        if not (opendrain <= 1):
            self._throw(YAPI.INVALID_ARGUMENT, "invalid state")
            return YAPI.INVALID_ARGUMENT
        return self.set_command("" + str(chr(100-32*opendrain)) + "" + str(int(bitno)))

    def get_bitOpenDrain(self, bitno):
        """
        Returns the type of electrical interface of a single bit from the I/O port. (0 means the bit is an
        input, 1  an output).

        @param bitno : the bit number; lowest bit has index 0

        @return   0 means the a bit is a regular input/output, 1 means the bit is an open-drain
                (open-collector) input/output.

        On failure, throws an exception or returns a negative error code.
        """
        # portOpenDrain
        portOpenDrain = self.get_portOpenDrain()
        return ((((portOpenDrain) >> (bitno))) & (1))

    def pulse(self, bitno, ms_duration):
        """
        Triggers a pulse on a single bit for a specified duration. The specified bit
        will be turned to 1, and then back to 0 after the given duration.

        @param bitno : the bit number; lowest bit has index 0
        @param ms_duration : desired pulse duration in milliseconds. Be aware that the device time
                resolution is not guaranteed up to the millisecond.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("Z" + str(int(bitno)) + ",0," + str(int(ms_duration)))

    def delayedPulse(self, bitno, ms_delay, ms_duration):
        """
        Schedules a pulse on a single bit for a specified duration. The specified bit
        will be turned to 1, and then back to 0 after the given duration.

        @param bitno : the bit number; lowest bit has index 0
        @param ms_delay : waiting time before the pulse, in milliseconds
        @param ms_duration : desired pulse duration in milliseconds. Be aware that the device time
                resolution is not guaranteed up to the millisecond.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("Z" + str(int(bitno)) + "," + str(int(ms_delay)) + "," + str(int(ms_duration)))

    def nextDigitalIO(self):
        """
        Continues the enumeration of digital IO ports started using yFirstDigitalIO().
        Caution: You can't make any assumption about the returned digital IO ports order.
        If you want to find a specific a digital IO port, use DigitalIO.findDigitalIO()
        and a hardwareID or a logical name.

        @return a pointer to a YDigitalIO object, corresponding to
                a digital IO port currently online, or a None pointer
                if there are no more digital IO ports to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YDigitalIO.FindDigitalIO(hwidRef.value)

#--- (end of YDigitalIO implementation)

#--- (YDigitalIO functions)

    @staticmethod
    def FirstDigitalIO():
        """
        Starts the enumeration of digital IO ports currently accessible.
        Use the method YDigitalIO.nextDigitalIO() to iterate on
        next digital IO ports.

        @return a pointer to a YDigitalIO object, corresponding to
                the first digital IO port currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("DigitalIO", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YDigitalIO.FindDigitalIO(serialRef.value + "." + funcIdRef.value)

#--- (end of YDigitalIO functions)
