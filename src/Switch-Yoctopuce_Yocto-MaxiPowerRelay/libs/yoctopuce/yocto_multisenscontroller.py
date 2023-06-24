# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_multisenscontroller.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindMultiSensController(), the high-level API for MultiSensController functions
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


#--- (YMultiSensController class start)
#noinspection PyProtectedMember
class YMultiSensController(YFunction):
    """
    The YMultiSensController class allows you to setup a customized
    sensor chain on devices featuring that functionality.

    """
    #--- (end of YMultiSensController class start)
    #--- (YMultiSensController return codes)
    #--- (end of YMultiSensController return codes)
    #--- (YMultiSensController dlldef)
    #--- (end of YMultiSensController dlldef)
    #--- (YMultiSensController yapiwrapper)
    #--- (end of YMultiSensController yapiwrapper)
    #--- (YMultiSensController definitions)
    NSENSORS_INVALID = YAPI.INVALID_UINT
    MAXSENSORS_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    MAINTENANCEMODE_FALSE = 0
    MAINTENANCEMODE_TRUE = 1
    MAINTENANCEMODE_INVALID = -1
    #--- (end of YMultiSensController definitions)

    def __init__(self, func):
        super(YMultiSensController, self).__init__(func)
        self._className = 'MultiSensController'
        #--- (YMultiSensController attributes)
        self._callback = None
        self._nSensors = YMultiSensController.NSENSORS_INVALID
        self._maxSensors = YMultiSensController.MAXSENSORS_INVALID
        self._maintenanceMode = YMultiSensController.MAINTENANCEMODE_INVALID
        self._command = YMultiSensController.COMMAND_INVALID
        #--- (end of YMultiSensController attributes)

    #--- (YMultiSensController implementation)
    def _parseAttr(self, json_val):
        if json_val.has("nSensors"):
            self._nSensors = json_val.getInt("nSensors")
        if json_val.has("maxSensors"):
            self._maxSensors = json_val.getInt("maxSensors")
        if json_val.has("maintenanceMode"):
            self._maintenanceMode = (json_val.getInt("maintenanceMode") > 0 if 1 else 0)
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YMultiSensController, self)._parseAttr(json_val)

    def get_nSensors(self):
        """
        Returns the number of sensors to poll.

        @return an integer corresponding to the number of sensors to poll

        On failure, throws an exception or returns YMultiSensController.NSENSORS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiSensController.NSENSORS_INVALID
        res = self._nSensors
        return res

    def set_nSensors(self, newval):
        """
        Changes the number of sensors to poll. Remember to call the
        saveToFlash() method of the module if the
        modification must be kept. It is recommended to restart the
        device with  module->reboot() after modifying
        (and saving) this settings

        @param newval : an integer corresponding to the number of sensors to poll

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("nSensors", rest_val)

    def get_maxSensors(self):
        """
        Returns the maximum configurable sensor count allowed on this device.

        @return an integer corresponding to the maximum configurable sensor count allowed on this device

        On failure, throws an exception or returns YMultiSensController.MAXSENSORS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiSensController.MAXSENSORS_INVALID
        res = self._maxSensors
        return res

    def get_maintenanceMode(self):
        """
        Returns true when the device is in maintenance mode.

        @return either YMultiSensController.MAINTENANCEMODE_FALSE or
        YMultiSensController.MAINTENANCEMODE_TRUE, according to true when the device is in maintenance mode

        On failure, throws an exception or returns YMultiSensController.MAINTENANCEMODE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiSensController.MAINTENANCEMODE_INVALID
        res = self._maintenanceMode
        return res

    def set_maintenanceMode(self, newval):
        """
        Changes the device mode to enable maintenance and to stop sensor polling.
        This way, the device does not automatically restart when it cannot
        communicate with one of the sensors.

        @param newval : either YMultiSensController.MAINTENANCEMODE_FALSE or
        YMultiSensController.MAINTENANCEMODE_TRUE, according to the device mode to enable maintenance and
        to stop sensor polling

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("maintenanceMode", rest_val)

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YMultiSensController.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindMultiSensController(func):
        """
        Retrieves a multi-sensor controller for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the multi-sensor controller is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YMultiSensController.isOnline() to test if the multi-sensor controller is
        indeed online at a given time. In case of ambiguity when looking for
        a multi-sensor controller by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the multi-sensor controller, for instance
                YTEMPIR1.multiSensController.

        @return a YMultiSensController object allowing you to drive the multi-sensor controller.
        """
        # obj
        obj = YFunction._FindFromCache("MultiSensController", func)
        if obj is None:
            obj = YMultiSensController(func)
            YFunction._AddToCache("MultiSensController", func, obj)
        return obj

    def setupAddress(self, addr):
        """
        Configures the I2C address of the only sensor connected to the device.
        It is recommended to put the the device in maintenance mode before
        changing sensor addresses.  This method is only intended to work with a single
        sensor connected to the device, if several sensors are connected, the result
        is unpredictable.
        Note that the device is probably expecting to find a string of sensors with specific
        addresses. Check the device documentation to find out which addresses should be used.

        @param addr : new address of the connected sensor

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        # cmd
        cmd = "A" + str(int(addr))
        return self.set_command(cmd)

    def nextMultiSensController(self):
        """
        Continues the enumeration of multi-sensor controllers started using yFirstMultiSensController().
        Caution: You can't make any assumption about the returned multi-sensor controllers order.
        If you want to find a specific a multi-sensor controller, use MultiSensController.findMultiSensController()
        and a hardwareID or a logical name.

        @return a pointer to a YMultiSensController object, corresponding to
                a multi-sensor controller currently online, or a None pointer
                if there are no more multi-sensor controllers to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YMultiSensController.FindMultiSensController(hwidRef.value)

#--- (end of YMultiSensController implementation)

#--- (YMultiSensController functions)

    @staticmethod
    def FirstMultiSensController():
        """
        Starts the enumeration of multi-sensor controllers currently accessible.
        Use the method YMultiSensController.nextMultiSensController() to iterate on
        next multi-sensor controllers.

        @return a pointer to a YMultiSensController object, corresponding to
                the first multi-sensor controller currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("MultiSensController", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YMultiSensController.FindMultiSensController(serialRef.value + "." + funcIdRef.value)

#--- (end of YMultiSensController functions)
