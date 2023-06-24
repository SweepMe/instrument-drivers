# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_pressure.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindPressure(), the high-level API for Pressure functions
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


#--- (YPressure class start)
#noinspection PyProtectedMember
class YPressure(YSensor):
    """
    The YPressure class allows you to read and configure Yoctopuce pressure sensors.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.

    """
    #--- (end of YPressure class start)
    #--- (YPressure return codes)
    #--- (end of YPressure return codes)
    #--- (YPressure dlldef)
    #--- (end of YPressure dlldef)
    #--- (YPressure yapiwrapper)
    #--- (end of YPressure yapiwrapper)
    #--- (YPressure definitions)
    #--- (end of YPressure definitions)

    def __init__(self, func):
        super(YPressure, self).__init__(func)
        self._className = 'Pressure'
        #--- (YPressure attributes)
        self._callback = None
        #--- (end of YPressure attributes)

    #--- (YPressure implementation)
    def _parseAttr(self, json_val):
        super(YPressure, self)._parseAttr(json_val)

    @staticmethod
    def FindPressure(func):
        """
        Retrieves a pressure sensor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the pressure sensor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YPressure.isOnline() to test if the pressure sensor is
        indeed online at a given time. In case of ambiguity when looking for
        a pressure sensor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the pressure sensor, for instance
                YALTIMK2.pressure.

        @return a YPressure object allowing you to drive the pressure sensor.
        """
        # obj
        obj = YFunction._FindFromCache("Pressure", func)
        if obj is None:
            obj = YPressure(func)
            YFunction._AddToCache("Pressure", func, obj)
        return obj

    def nextPressure(self):
        """
        Continues the enumeration of pressure sensors started using yFirstPressure().
        Caution: You can't make any assumption about the returned pressure sensors order.
        If you want to find a specific a pressure sensor, use Pressure.findPressure()
        and a hardwareID or a logical name.

        @return a pointer to a YPressure object, corresponding to
                a pressure sensor currently online, or a None pointer
                if there are no more pressure sensors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YPressure.FindPressure(hwidRef.value)

#--- (end of YPressure implementation)

#--- (YPressure functions)

    @staticmethod
    def FirstPressure():
        """
        Starts the enumeration of pressure sensors currently accessible.
        Use the method YPressure.nextPressure() to iterate on
        next pressure sensors.

        @return a pointer to a YPressure object, corresponding to
                the first pressure sensor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Pressure", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YPressure.FindPressure(serialRef.value + "." + funcIdRef.value)

#--- (end of YPressure functions)
