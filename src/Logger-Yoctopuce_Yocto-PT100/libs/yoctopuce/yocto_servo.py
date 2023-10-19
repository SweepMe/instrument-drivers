# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_servo.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindServo(), the high-level API for Servo functions
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


#--- (YServo class start)
#noinspection PyProtectedMember
class YServo(YFunction):
    """
    The YServo class is designed to drive remote-control servo motors
    outputs. This class allows you not only to move
    a servo to a given position, but also to specify the time interval
    in which the move should be performed. This makes it possible to
    synchronize two servos involved in a same move.

    """
    #--- (end of YServo class start)
    #--- (YServo return codes)
    #--- (end of YServo return codes)
    #--- (YServo dlldef)
    #--- (end of YServo dlldef)
    #--- (YServo yapiwrapper)
    #--- (end of YServo yapiwrapper)
    #--- (YServo definitions)
    POSITION_INVALID = YAPI.INVALID_INT
    RANGE_INVALID = YAPI.INVALID_UINT
    NEUTRAL_INVALID = YAPI.INVALID_UINT
    MOVE_INVALID = None
    POSITIONATPOWERON_INVALID = YAPI.INVALID_INT
    ENABLED_FALSE = 0
    ENABLED_TRUE = 1
    ENABLED_INVALID = -1
    ENABLEDATPOWERON_FALSE = 0
    ENABLEDATPOWERON_TRUE = 1
    ENABLEDATPOWERON_INVALID = -1
    #--- (end of YServo definitions)

    def __init__(self, func):
        super(YServo, self).__init__(func)
        self._className = 'Servo'
        #--- (YServo attributes)
        self._callback = None
        self._position = YServo.POSITION_INVALID
        self._enabled = YServo.ENABLED_INVALID
        self._range = YServo.RANGE_INVALID
        self._neutral = YServo.NEUTRAL_INVALID
        self._move = YServo.MOVE_INVALID
        self._positionAtPowerOn = YServo.POSITIONATPOWERON_INVALID
        self._enabledAtPowerOn = YServo.ENABLEDATPOWERON_INVALID
        #--- (end of YServo attributes)

    #--- (YServo implementation)
    def _parseAttr(self, json_val):
        if json_val.has("position"):
            self._position = json_val.getInt("position")
        if json_val.has("enabled"):
            self._enabled = (json_val.getInt("enabled") > 0 if 1 else 0)
        if json_val.has("range"):
            self._range = json_val.getInt("range")
        if json_val.has("neutral"):
            self._neutral = json_val.getInt("neutral")
        if json_val.has("move"):
            subjson = json_val.getYJSONObject("move");
            self._move = {"moving": None, "target": None, "ms": None}
            if subjson.has("moving"):
                self._move["moving"] = subjson.getInt("moving")
            if subjson.has("target"):
                self._move["target"] = subjson.getInt("target")
            if subjson.has("ms"):
                self._move["ms"] = subjson.getInt("ms")
        if json_val.has("positionAtPowerOn"):
            self._positionAtPowerOn = json_val.getInt("positionAtPowerOn")
        if json_val.has("enabledAtPowerOn"):
            self._enabledAtPowerOn = (json_val.getInt("enabledAtPowerOn") > 0 if 1 else 0)
        super(YServo, self)._parseAttr(json_val)

    def get_position(self):
        """
        Returns the current servo position.

        @return an integer corresponding to the current servo position

        On failure, throws an exception or returns YServo.POSITION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YServo.POSITION_INVALID
        res = self._position
        return res

    def set_position(self, newval):
        """
        Changes immediately the servo driving position.

        @param newval : an integer corresponding to immediately the servo driving position

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("position", rest_val)

    def get_enabled(self):
        """
        Returns the state of the RC servo motors.

        @return either YServo.ENABLED_FALSE or YServo.ENABLED_TRUE, according to the state of the RC servo motors

        On failure, throws an exception or returns YServo.ENABLED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YServo.ENABLED_INVALID
        res = self._enabled
        return res

    def set_enabled(self, newval):
        """
        Stops or starts the RC servo motor.

        @param newval : either YServo.ENABLED_FALSE or YServo.ENABLED_TRUE

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("enabled", rest_val)

    def get_range(self):
        """
        Returns the current range of use of the servo.

        @return an integer corresponding to the current range of use of the servo

        On failure, throws an exception or returns YServo.RANGE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YServo.RANGE_INVALID
        res = self._range
        return res

    def set_range(self, newval):
        """
        Changes the range of use of the servo, specified in per cents.
        A range of 100% corresponds to a standard control signal, that varies
        from 1 [ms] to 2 [ms], When using a servo that supports a double range,
        from 0.5 [ms] to 2.5 [ms], you can select a range of 200%.
        Be aware that using a range higher than what is supported by the servo
        is likely to damage the servo. Remember to call the matching module
        saveToFlash() method, otherwise this call will have no effect.

        @param newval : an integer corresponding to the range of use of the servo, specified in per cents

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("range", rest_val)

    def get_neutral(self):
        """
        Returns the duration in microseconds of a neutral pulse for the servo.

        @return an integer corresponding to the duration in microseconds of a neutral pulse for the servo

        On failure, throws an exception or returns YServo.NEUTRAL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YServo.NEUTRAL_INVALID
        res = self._neutral
        return res

    def set_neutral(self, newval):
        """
        Changes the duration of the pulse corresponding to the neutral position of the servo.
        The duration is specified in microseconds, and the standard value is 1500 [us].
        This setting makes it possible to shift the range of use of the servo.
        Be aware that using a range higher than what is supported by the servo is
        likely to damage the servo. Remember to call the matching module
        saveToFlash() method, otherwise this call will have no effect.

        @param newval : an integer corresponding to the duration of the pulse corresponding to the neutral
        position of the servo

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("neutral", rest_val)

    def get_move(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YServo.MOVE_INVALID
        res = self._move
        return res

    def set_move(self, newval):
        rest_val = str(newval.target) + ":" + str(newval.ms)
        return self._setAttr("move", rest_val)

    def move(self, target, ms_duration):
        """
        Performs a smooth move at constant speed toward a given position.

        @param target      : new position at the end of the move
        @param ms_duration : total duration of the move, in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(target) + ":" + str(ms_duration)
        return self._setAttr("move", rest_val)

    def get_positionAtPowerOn(self):
        """
        Returns the servo position at device power up.

        @return an integer corresponding to the servo position at device power up

        On failure, throws an exception or returns YServo.POSITIONATPOWERON_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YServo.POSITIONATPOWERON_INVALID
        res = self._positionAtPowerOn
        return res

    def set_positionAtPowerOn(self, newval):
        """
        Configure the servo position at device power up. Remember to call the matching
        module saveToFlash() method, otherwise this call will have no effect.

        @param newval : an integer

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("positionAtPowerOn", rest_val)

    def get_enabledAtPowerOn(self):
        """
        Returns the servo signal generator state at power up.

        @return either YServo.ENABLEDATPOWERON_FALSE or YServo.ENABLEDATPOWERON_TRUE, according to the
        servo signal generator state at power up

        On failure, throws an exception or returns YServo.ENABLEDATPOWERON_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YServo.ENABLEDATPOWERON_INVALID
        res = self._enabledAtPowerOn
        return res

    def set_enabledAtPowerOn(self, newval):
        """
        Configure the servo signal generator state at power up. Remember to call the matching module saveToFlash()
        method, otherwise this call will have no effect.

        @param newval : either YServo.ENABLEDATPOWERON_FALSE or YServo.ENABLEDATPOWERON_TRUE

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("enabledAtPowerOn", rest_val)

    @staticmethod
    def FindServo(func):
        """
        Retrieves a RC servo motor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the RC servo motor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YServo.isOnline() to test if the RC servo motor is
        indeed online at a given time. In case of ambiguity when looking for
        a RC servo motor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the RC servo motor, for instance
                SERVORC1.servo1.

        @return a YServo object allowing you to drive the RC servo motor.
        """
        # obj
        obj = YFunction._FindFromCache("Servo", func)
        if obj is None:
            obj = YServo(func)
            YFunction._AddToCache("Servo", func, obj)
        return obj

    def nextServo(self):
        """
        Continues the enumeration of RC servo motors started using yFirstServo().
        Caution: You can't make any assumption about the returned RC servo motors order.
        If you want to find a specific a RC servo motor, use Servo.findServo()
        and a hardwareID or a logical name.

        @return a pointer to a YServo object, corresponding to
                a RC servo motor currently online, or a None pointer
                if there are no more RC servo motors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YServo.FindServo(hwidRef.value)

#--- (end of YServo implementation)

#--- (YServo functions)

    @staticmethod
    def FirstServo():
        """
        Starts the enumeration of RC servo motors currently accessible.
        Use the method YServo.nextServo() to iterate on
        next RC servo motors.

        @return a pointer to a YServo object, corresponding to
                the first RC servo motor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Servo", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YServo.FindServo(serialRef.value + "." + funcIdRef.value)

#--- (end of YServo functions)
