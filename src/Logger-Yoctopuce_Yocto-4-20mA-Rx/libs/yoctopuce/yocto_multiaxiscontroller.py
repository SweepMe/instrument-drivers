# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_multiaxiscontroller.py 37827 2019-10-25 13:07:48Z mvuilleu $
#
#  Implements yFindMultiAxisController(), the high-level API for MultiAxisController functions
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


#--- (YMultiAxisController class start)
#noinspection PyProtectedMember
class YMultiAxisController(YFunction):
    """
    The YMultiAxisController class allows you to drive multiple stepper motors
    synchronously.

    """
    #--- (end of YMultiAxisController class start)
    #--- (YMultiAxisController return codes)
    #--- (end of YMultiAxisController return codes)
    #--- (YMultiAxisController dlldef)
    #--- (end of YMultiAxisController dlldef)
    #--- (YMultiAxisController yapiwrapper)
    #--- (end of YMultiAxisController yapiwrapper)
    #--- (YMultiAxisController definitions)
    NAXIS_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    GLOBALSTATE_ABSENT = 0
    GLOBALSTATE_ALERT = 1
    GLOBALSTATE_HI_Z = 2
    GLOBALSTATE_STOP = 3
    GLOBALSTATE_RUN = 4
    GLOBALSTATE_BATCH = 5
    GLOBALSTATE_INVALID = -1
    #--- (end of YMultiAxisController definitions)

    def __init__(self, func):
        super(YMultiAxisController, self).__init__(func)
        self._className = 'MultiAxisController'
        #--- (YMultiAxisController attributes)
        self._callback = None
        self._nAxis = YMultiAxisController.NAXIS_INVALID
        self._globalState = YMultiAxisController.GLOBALSTATE_INVALID
        self._command = YMultiAxisController.COMMAND_INVALID
        #--- (end of YMultiAxisController attributes)

    #--- (YMultiAxisController implementation)
    def _parseAttr(self, json_val):
        if json_val.has("nAxis"):
            self._nAxis = json_val.getInt("nAxis")
        if json_val.has("globalState"):
            self._globalState = json_val.getInt("globalState")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YMultiAxisController, self)._parseAttr(json_val)

    def get_nAxis(self):
        """
        Returns the number of synchronized controllers.

        @return an integer corresponding to the number of synchronized controllers

        On failure, throws an exception or returns YMultiAxisController.NAXIS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiAxisController.NAXIS_INVALID
        res = self._nAxis
        return res

    def set_nAxis(self, newval):
        """
        Changes the number of synchronized controllers.

        @param newval : an integer corresponding to the number of synchronized controllers

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("nAxis", rest_val)

    def get_globalState(self):
        """
        Returns the stepper motor set overall state.

        @return a value among YMultiAxisController.GLOBALSTATE_ABSENT,
        YMultiAxisController.GLOBALSTATE_ALERT, YMultiAxisController.GLOBALSTATE_HI_Z,
        YMultiAxisController.GLOBALSTATE_STOP, YMultiAxisController.GLOBALSTATE_RUN and
        YMultiAxisController.GLOBALSTATE_BATCH corresponding to the stepper motor set overall state

        On failure, throws an exception or returns YMultiAxisController.GLOBALSTATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiAxisController.GLOBALSTATE_INVALID
        res = self._globalState
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiAxisController.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindMultiAxisController(func):
        """
        Retrieves a multi-axis controller for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the multi-axis controller is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YMultiAxisController.isOnline() to test if the multi-axis controller is
        indeed online at a given time. In case of ambiguity when looking for
        a multi-axis controller by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the multi-axis controller, for instance
                MyDevice.multiAxisController.

        @return a YMultiAxisController object allowing you to drive the multi-axis controller.
        """
        # obj
        obj = YFunction._FindFromCache("MultiAxisController", func)
        if obj is None:
            obj = YMultiAxisController(func)
            YFunction._AddToCache("MultiAxisController", func, obj)
        return obj

    def sendCommand(self, command):
        # url
        # retBin
        # res
        url = "cmd.txt?X=" + command
        # //may throw an exception
        retBin = self._download(url)
        res = YGetByte(retBin, 0)
        if res == 49:
            if not (res == 48):
                self._throw(YAPI.DEVICE_BUSY, "Motor command pipeline is full, try again later")
                return YAPI.DEVICE_BUSY
        else:
            if not (res == 48):
                self._throw(YAPI.IO_ERROR, "Motor command failed permanently")
                return YAPI.IO_ERROR
        return YAPI.SUCCESS

    def reset(self):
        """
        Reinitialize all controllers and clear all alert flags.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("Z")

    def findHomePosition(self, speed):
        """
        Starts all motors backward at the specified speeds, to search for the motor home position.

        @param speed : desired speed for all axis, in steps per second.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        # cmd
        # i
        # ndim
        ndim = len(speed)
        cmd = "H" + str(int(round(1000*speed[0])))
        i = 1
        while i < ndim:
            cmd = "" + cmd + "," + str(int(round(1000*speed[i])))
            i = i + 1
        return self.sendCommand(cmd)

    def moveTo(self, absPos):
        """
        Starts all motors synchronously to reach a given absolute position.
        The time needed to reach the requested position will depend on the lowest
        acceleration and max speed parameters configured for all motors.
        The final position will be reached on all axis at the same time.

        @param absPos : absolute position, measured in steps from each origin.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        # cmd
        # i
        # ndim
        ndim = len(absPos)
        cmd = "M" + str(int(round(16*absPos[0])))
        i = 1
        while i < ndim:
            cmd = "" + cmd + "," + str(int(round(16*absPos[i])))
            i = i + 1
        return self.sendCommand(cmd)

    def moveRel(self, relPos):
        """
        Starts all motors synchronously to reach a given relative position.
        The time needed to reach the requested position will depend on the lowest
        acceleration and max speed parameters configured for all motors.
        The final position will be reached on all axis at the same time.

        @param relPos : relative position, measured in steps from the current position.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        # cmd
        # i
        # ndim
        ndim = len(relPos)
        cmd = "m" + str(int(round(16*relPos[0])))
        i = 1
        while i < ndim:
            cmd = "" + cmd + "," + str(int(round(16*relPos[i])))
            i = i + 1
        return self.sendCommand(cmd)

    def pause(self, waitMs):
        """
        Keep the motor in the same state for the specified amount of time, before processing next command.

        @param waitMs : wait time, specified in milliseconds.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("_" + str(int(waitMs)))

    def emergencyStop(self):
        """
        Stops the motor with an emergency alert, without taking any additional precaution.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("!")

    def abortAndBrake(self):
        """
        Stops the motor smoothly as soon as possible, without waiting for ongoing move completion.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("B")

    def abortAndHiZ(self):
        """
        Turn the controller into Hi-Z mode immediately, without waiting for ongoing move completion.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("z")

    def nextMultiAxisController(self):
        """
        Continues the enumeration of multi-axis controllers started using yFirstMultiAxisController().
        Caution: You can't make any assumption about the returned multi-axis controllers order.
        If you want to find a specific a multi-axis controller, use MultiAxisController.findMultiAxisController()
        and a hardwareID or a logical name.

        @return a pointer to a YMultiAxisController object, corresponding to
                a multi-axis controller currently online, or a None pointer
                if there are no more multi-axis controllers to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YMultiAxisController.FindMultiAxisController(hwidRef.value)

#--- (end of YMultiAxisController implementation)

#--- (YMultiAxisController functions)

    @staticmethod
    def FirstMultiAxisController():
        """
        Starts the enumeration of multi-axis controllers currently accessible.
        Use the method YMultiAxisController.nextMultiAxisController() to iterate on
        next multi-axis controllers.

        @return a pointer to a YMultiAxisController object, corresponding to
                the first multi-axis controller currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("MultiAxisController", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YMultiAxisController.FindMultiAxisController(serialRef.value + "." + funcIdRef.value)

#--- (end of YMultiAxisController functions)
