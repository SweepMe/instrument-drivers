# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_poweroutput.py 38913 2019-12-20 18:59:49Z mvuilleu $
#
#  Implements yFindPowerOutput(), the high-level API for PowerOutput functions
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


#--- (YPowerOutput class start)
#noinspection PyProtectedMember
class YPowerOutput(YFunction):
    """
    The YPowerOutput class allows you to control
    the power output featured on some Yoctopuce devices.

    """
    #--- (end of YPowerOutput class start)
    #--- (YPowerOutput return codes)
    #--- (end of YPowerOutput return codes)
    #--- (YPowerOutput dlldef)
    #--- (end of YPowerOutput dlldef)
    #--- (YPowerOutput yapiwrapper)
    #--- (end of YPowerOutput yapiwrapper)
    #--- (YPowerOutput definitions)
    VOLTAGE_OFF = 0
    VOLTAGE_OUT3V3 = 1
    VOLTAGE_OUT5V = 2
    VOLTAGE_OUT4V7 = 3
    VOLTAGE_OUT1V8 = 4
    VOLTAGE_INVALID = -1
    #--- (end of YPowerOutput definitions)

    def __init__(self, func):
        super(YPowerOutput, self).__init__(func)
        self._className = 'PowerOutput'
        #--- (YPowerOutput attributes)
        self._callback = None
        self._voltage = YPowerOutput.VOLTAGE_INVALID
        #--- (end of YPowerOutput attributes)

    #--- (YPowerOutput implementation)
    def _parseAttr(self, json_val):
        if json_val.has("voltage"):
            self._voltage = json_val.getInt("voltage")
        super(YPowerOutput, self)._parseAttr(json_val)

    def get_voltage(self):
        """
        Returns the voltage on the power output featured by the module.

        @return a value among YPowerOutput.VOLTAGE_OFF, YPowerOutput.VOLTAGE_OUT3V3,
        YPowerOutput.VOLTAGE_OUT5V, YPowerOutput.VOLTAGE_OUT4V7 and YPowerOutput.VOLTAGE_OUT1V8
        corresponding to the voltage on the power output featured by the module

        On failure, throws an exception or returns YPowerOutput.VOLTAGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YPowerOutput.VOLTAGE_INVALID
        res = self._voltage
        return res

    def set_voltage(self, newval):
        """
        Changes the voltage on the power output provided by the
        module. Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a value among YPowerOutput.VOLTAGE_OFF, YPowerOutput.VOLTAGE_OUT3V3,
        YPowerOutput.VOLTAGE_OUT5V, YPowerOutput.VOLTAGE_OUT4V7 and YPowerOutput.VOLTAGE_OUT1V8
        corresponding to the voltage on the power output provided by the
                module

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("voltage", rest_val)

    @staticmethod
    def FindPowerOutput(func):
        """
        Retrieves a power output for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the power output is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YPowerOutput.isOnline() to test if the power output is
        indeed online at a given time. In case of ambiguity when looking for
        a power output by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the power output, for instance
                YI2CMK01.powerOutput.

        @return a YPowerOutput object allowing you to drive the power output.
        """
        # obj
        obj = YFunction._FindFromCache("PowerOutput", func)
        if obj is None:
            obj = YPowerOutput(func)
            YFunction._AddToCache("PowerOutput", func, obj)
        return obj

    def nextPowerOutput(self):
        """
        Continues the enumeration of power output started using yFirstPowerOutput().
        Caution: You can't make any assumption about the returned power output order.
        If you want to find a specific a power output, use PowerOutput.findPowerOutput()
        and a hardwareID or a logical name.

        @return a pointer to a YPowerOutput object, corresponding to
                a power output currently online, or a None pointer
                if there are no more power output to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YPowerOutput.FindPowerOutput(hwidRef.value)

#--- (end of YPowerOutput implementation)

#--- (YPowerOutput functions)

    @staticmethod
    def FirstPowerOutput():
        """
        Starts the enumeration of power output currently accessible.
        Use the method YPowerOutput.nextPowerOutput() to iterate on
        next power output.

        @return a pointer to a YPowerOutput object, corresponding to
                the first power output currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("PowerOutput", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YPowerOutput.FindPowerOutput(serialRef.value + "." + funcIdRef.value)

#--- (end of YPowerOutput functions)
