# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_currentloopoutput.py 38913 2019-12-20 18:59:49Z mvuilleu $
#
#  Implements yFindCurrentLoopOutput(), the high-level API for CurrentLoopOutput functions
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


#--- (YCurrentLoopOutput class start)
#noinspection PyProtectedMember
class YCurrentLoopOutput(YFunction):
    """
    The YCurrentLoopOutput class allows you to drive a 4-20mA output
    by regulating the current flowing through the current loop.
    It can also provide information about the power state of the current loop.

    """
    #--- (end of YCurrentLoopOutput class start)
    #--- (YCurrentLoopOutput return codes)
    #--- (end of YCurrentLoopOutput return codes)
    #--- (YCurrentLoopOutput dlldef)
    #--- (end of YCurrentLoopOutput dlldef)
    #--- (YCurrentLoopOutput yapiwrapper)
    #--- (end of YCurrentLoopOutput yapiwrapper)
    #--- (YCurrentLoopOutput definitions)
    CURRENT_INVALID = YAPI.INVALID_DOUBLE
    CURRENTTRANSITION_INVALID = YAPI.INVALID_STRING
    CURRENTATSTARTUP_INVALID = YAPI.INVALID_DOUBLE
    LOOPPOWER_NOPWR = 0
    LOOPPOWER_LOWPWR = 1
    LOOPPOWER_POWEROK = 2
    LOOPPOWER_INVALID = -1
    #--- (end of YCurrentLoopOutput definitions)

    def __init__(self, func):
        super(YCurrentLoopOutput, self).__init__(func)
        self._className = 'CurrentLoopOutput'
        #--- (YCurrentLoopOutput attributes)
        self._callback = None
        self._current = YCurrentLoopOutput.CURRENT_INVALID
        self._currentTransition = YCurrentLoopOutput.CURRENTTRANSITION_INVALID
        self._currentAtStartUp = YCurrentLoopOutput.CURRENTATSTARTUP_INVALID
        self._loopPower = YCurrentLoopOutput.LOOPPOWER_INVALID
        #--- (end of YCurrentLoopOutput attributes)

    #--- (YCurrentLoopOutput implementation)
    def _parseAttr(self, json_val):
        if json_val.has("current"):
            self._current = round(json_val.getDouble("current") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("currentTransition"):
            self._currentTransition = json_val.getString("currentTransition")
        if json_val.has("currentAtStartUp"):
            self._currentAtStartUp = round(json_val.getDouble("currentAtStartUp") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("loopPower"):
            self._loopPower = json_val.getInt("loopPower")
        super(YCurrentLoopOutput, self)._parseAttr(json_val)

    def set_current(self, newval):
        """
        Changes the current loop, the valid range is from 3 to 21mA. If the loop is
        not properly powered, the  target current is not reached and
        loopPower is set to LOWPWR.

        @param newval : a floating point number corresponding to the current loop, the valid range is from 3 to 21mA

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("current", rest_val)

    def get_current(self):
        """
        Returns the loop current set point in mA.

        @return a floating point number corresponding to the loop current set point in mA

        On failure, throws an exception or returns YCurrentLoopOutput.CURRENT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCurrentLoopOutput.CURRENT_INVALID
        res = self._current
        return res

    def get_currentTransition(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCurrentLoopOutput.CURRENTTRANSITION_INVALID
        res = self._currentTransition
        return res

    def set_currentTransition(self, newval):
        rest_val = newval
        return self._setAttr("currentTransition", rest_val)

    def set_currentAtStartUp(self, newval):
        """
        Changes the loop current at device start up. Remember to call the matching
        module saveToFlash() method, otherwise this call has no effect.

        @param newval : a floating point number corresponding to the loop current at device start up

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("currentAtStartUp", rest_val)

    def get_currentAtStartUp(self):
        """
        Returns the current in the loop at device startup, in mA.

        @return a floating point number corresponding to the current in the loop at device startup, in mA

        On failure, throws an exception or returns YCurrentLoopOutput.CURRENTATSTARTUP_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCurrentLoopOutput.CURRENTATSTARTUP_INVALID
        res = self._currentAtStartUp
        return res

    def get_loopPower(self):
        """
        Returns the loop powerstate.  POWEROK: the loop
        is powered. NOPWR: the loop in not powered. LOWPWR: the loop is not
        powered enough to maintain the current required (insufficient voltage).

        @return a value among YCurrentLoopOutput.LOOPPOWER_NOPWR, YCurrentLoopOutput.LOOPPOWER_LOWPWR and
        YCurrentLoopOutput.LOOPPOWER_POWEROK corresponding to the loop powerstate

        On failure, throws an exception or returns YCurrentLoopOutput.LOOPPOWER_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YCurrentLoopOutput.LOOPPOWER_INVALID
        res = self._loopPower
        return res

    @staticmethod
    def FindCurrentLoopOutput(func):
        """
        Retrieves a 4-20mA output for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the 4-20mA output is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YCurrentLoopOutput.isOnline() to test if the 4-20mA output is
        indeed online at a given time. In case of ambiguity when looking for
        a 4-20mA output by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the 4-20mA output, for instance
                TX420MA1.currentLoopOutput.

        @return a YCurrentLoopOutput object allowing you to drive the 4-20mA output.
        """
        # obj
        obj = YFunction._FindFromCache("CurrentLoopOutput", func)
        if obj is None:
            obj = YCurrentLoopOutput(func)
            YFunction._AddToCache("CurrentLoopOutput", func, obj)
        return obj

    def currentMove(self, mA_target, ms_duration):
        """
        Performs a smooth transition of current flowing in the loop. Any current explicit
        change cancels any ongoing transition process.

        @param mA_target   : new current value at the end of the transition
                (floating-point number, representing the end current in mA)
        @param ms_duration : total duration of the transition, in milliseconds

        @return YAPI.SUCCESS when the call succeeds.
        """
        # newval
        if mA_target < 3.0:
            mA_target  = 3.0
        if mA_target > 21.0:
            mA_target = 21.0
        newval = "" + str(int(round(mA_target*65536))) + ":" + str(int(ms_duration))

        return self.set_currentTransition(newval)

    def nextCurrentLoopOutput(self):
        """
        Continues the enumeration of 4-20mA outputs started using yFirstCurrentLoopOutput().
        Caution: You can't make any assumption about the returned 4-20mA outputs order.
        If you want to find a specific a 4-20mA output, use CurrentLoopOutput.findCurrentLoopOutput()
        and a hardwareID or a logical name.

        @return a pointer to a YCurrentLoopOutput object, corresponding to
                a 4-20mA output currently online, or a None pointer
                if there are no more 4-20mA outputs to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YCurrentLoopOutput.FindCurrentLoopOutput(hwidRef.value)

#--- (end of YCurrentLoopOutput implementation)

#--- (YCurrentLoopOutput functions)

    @staticmethod
    def FirstCurrentLoopOutput():
        """
        Starts the enumeration of 4-20mA outputs currently accessible.
        Use the method YCurrentLoopOutput.nextCurrentLoopOutput() to iterate on
        next 4-20mA outputs.

        @return a pointer to a YCurrentLoopOutput object, corresponding to
                the first 4-20mA output currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("CurrentLoopOutput", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YCurrentLoopOutput.FindCurrentLoopOutput(serialRef.value + "." + funcIdRef.value)

#--- (end of YCurrentLoopOutput functions)
