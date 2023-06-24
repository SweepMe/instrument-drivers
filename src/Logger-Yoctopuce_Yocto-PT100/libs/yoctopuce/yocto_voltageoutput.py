# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_voltageoutput.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindVoltageOutput(), the high-level API for VoltageOutput functions
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


#--- (YVoltageOutput class start)
#noinspection PyProtectedMember
class YVoltageOutput(YFunction):
    """
    The YVoltageOutput class allows you to drive a voltage output.

    """
    #--- (end of YVoltageOutput class start)
    #--- (YVoltageOutput return codes)
    #--- (end of YVoltageOutput return codes)
    #--- (YVoltageOutput dlldef)
    #--- (end of YVoltageOutput dlldef)
    #--- (YVoltageOutput yapiwrapper)
    #--- (end of YVoltageOutput yapiwrapper)
    #--- (YVoltageOutput definitions)
    CURRENTVOLTAGE_INVALID = YAPI.INVALID_DOUBLE
    VOLTAGETRANSITION_INVALID = YAPI.INVALID_STRING
    VOLTAGEATSTARTUP_INVALID = YAPI.INVALID_DOUBLE
    #--- (end of YVoltageOutput definitions)

    def __init__(self, func):
        super(YVoltageOutput, self).__init__(func)
        self._className = 'VoltageOutput'
        #--- (YVoltageOutput attributes)
        self._callback = None
        self._currentVoltage = YVoltageOutput.CURRENTVOLTAGE_INVALID
        self._voltageTransition = YVoltageOutput.VOLTAGETRANSITION_INVALID
        self._voltageAtStartUp = YVoltageOutput.VOLTAGEATSTARTUP_INVALID
        #--- (end of YVoltageOutput attributes)

    #--- (YVoltageOutput implementation)
    def _parseAttr(self, json_val):
        if json_val.has("currentVoltage"):
            self._currentVoltage = round(json_val.getDouble("currentVoltage") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("voltageTransition"):
            self._voltageTransition = json_val.getString("voltageTransition")
        if json_val.has("voltageAtStartUp"):
            self._voltageAtStartUp = round(json_val.getDouble("voltageAtStartUp") * 1000.0 / 65536.0) / 1000.0
        super(YVoltageOutput, self)._parseAttr(json_val)

    def set_currentVoltage(self, newval):
        """
        Changes the output voltage, in V. Valid range is from 0 to 10V.

        @param newval : a floating point number corresponding to the output voltage, in V

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("currentVoltage", rest_val)

    def get_currentVoltage(self):
        """
        Returns the output voltage set point, in V.

        @return a floating point number corresponding to the output voltage set point, in V

        On failure, throws an exception or returns YVoltageOutput.CURRENTVOLTAGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YVoltageOutput.CURRENTVOLTAGE_INVALID
        res = self._currentVoltage
        return res

    def get_voltageTransition(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YVoltageOutput.VOLTAGETRANSITION_INVALID
        res = self._voltageTransition
        return res

    def set_voltageTransition(self, newval):
        rest_val = newval
        return self._setAttr("voltageTransition", rest_val)

    def set_voltageAtStartUp(self, newval):
        """
        Changes the output voltage at device start up. Remember to call the matching
        module saveToFlash() method, otherwise this call has no effect.

        @param newval : a floating point number corresponding to the output voltage at device start up

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("voltageAtStartUp", rest_val)

    def get_voltageAtStartUp(self):
        """
        Returns the selected voltage output at device startup, in V.

        @return a floating point number corresponding to the selected voltage output at device startup, in V

        On failure, throws an exception or returns YVoltageOutput.VOLTAGEATSTARTUP_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YVoltageOutput.VOLTAGEATSTARTUP_INVALID
        res = self._voltageAtStartUp
        return res

    @staticmethod
    def FindVoltageOutput(func):
        """
        Retrieves a voltage output for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the voltage output is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YVoltageOutput.isOnline() to test if the voltage output is
        indeed online at a given time. In case of ambiguity when looking for
        a voltage output by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the voltage output, for instance
                TX010V01.voltageOutput1.

        @return a YVoltageOutput object allowing you to drive the voltage output.
        """
        # obj
        obj = YFunction._FindFromCache("VoltageOutput", func)
        if obj is None:
            obj = YVoltageOutput(func)
            YFunction._AddToCache("VoltageOutput", func, obj)
        return obj

    def voltageMove(self, V_target, ms_duration):
        """
        Performs a smooth transition of output voltage. Any explicit voltage
        change cancels any ongoing transition process.

        @param V_target   : new output voltage value at the end of the transition
                (floating-point number, representing the end voltage in V)
        @param ms_duration : total duration of the transition, in milliseconds

        @return YAPI.SUCCESS when the call succeeds.
        """
        # newval
        if V_target < 0.0:
            V_target  = 0.0
        if V_target > 10.0:
            V_target = 10.0
        newval = "" + str(int(round(V_target*65536))) + ":" + str(int(ms_duration))

        return self.set_voltageTransition(newval)

    def nextVoltageOutput(self):
        """
        Continues the enumeration of voltage outputs started using yFirstVoltageOutput().
        Caution: You can't make any assumption about the returned voltage outputs order.
        If you want to find a specific a voltage output, use VoltageOutput.findVoltageOutput()
        and a hardwareID or a logical name.

        @return a pointer to a YVoltageOutput object, corresponding to
                a voltage output currently online, or a None pointer
                if there are no more voltage outputs to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YVoltageOutput.FindVoltageOutput(hwidRef.value)

#--- (end of YVoltageOutput implementation)

#--- (YVoltageOutput functions)

    @staticmethod
    def FirstVoltageOutput():
        """
        Starts the enumeration of voltage outputs currently accessible.
        Use the method YVoltageOutput.nextVoltageOutput() to iterate on
        next voltage outputs.

        @return a pointer to a YVoltageOutput object, corresponding to
                the first voltage output currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("VoltageOutput", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YVoltageOutput.FindVoltageOutput(serialRef.value + "." + funcIdRef.value)

#--- (end of YVoltageOutput functions)
