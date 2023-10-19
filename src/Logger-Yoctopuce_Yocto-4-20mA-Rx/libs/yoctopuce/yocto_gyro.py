# -*- coding: utf-8 -*-
#*********************************************************************
#*
#* $Id: yocto_gyro.py 38899 2019-12-20 17:21:03Z mvuilleu $
#*
#* Implements yFindGyro(), the high-level API for Gyro functions
#*
#* - - - - - - - - - License information: - - - - - - - - -
#*
#*  Copyright (C) 2011 and beyond by Yoctopuce Sarl, Switzerland.
#*
#*  Yoctopuce Sarl (hereafter Licensor) grants to you a perpetual
#*  non-exclusive license to use, modify, copy and integrate this
#*  file into your software for the sole purpose of interfacing
#*  with Yoctopuce products.
#*
#*  You may reproduce and distribute copies of this file in
#*  source or object form, as long as the sole purpose of this
#*  code is to interface with Yoctopuce products. You must retain
#*  this notice in the distributed source file.
#*
#*  You should refer to Yoctopuce General Terms and Conditions
#*  for additional information regarding your rights and
#*  obligations.
#*
#*  THE SOFTWARE AND DOCUMENTATION ARE PROVIDED 'AS IS' WITHOUT
#*  WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING
#*  WITHOUT LIMITATION, ANY WARRANTY OF MERCHANTABILITY, FITNESS
#*  FOR A PARTICULAR PURPOSE, TITLE AND NON-INFRINGEMENT. IN NO
#*  EVENT SHALL LICENSOR BE LIABLE FOR ANY INCIDENTAL, SPECIAL,
#*  INDIRECT OR CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA,
#*  COST OF PROCUREMENT OF SUBSTITUTE GOODS, TECHNOLOGY OR
#*  SERVICES, ANY CLAIMS BY THIRD PARTIES (INCLUDING BUT NOT
#*  LIMITED TO ANY DEFENSE THEREOF), ANY CLAIMS FOR INDEMNITY OR
#*  CONTRIBUTION, OR OTHER SIMILAR COSTS, WHETHER ASSERTED ON THE
#*  BASIS OF CONTRACT, TORT (INCLUDING NEGLIGENCE), BREACH OF
#*  WARRANTY, OR OTHERWISE.
#*
#*********************************************************************/
import math


__docformat__ = 'restructuredtext en'
from yoctopuce.yocto_api import *

#--- (generated code: YQt class start)
#noinspection PyProtectedMember
class YQt(YSensor):
    """
    The YQt class provides direct access to the 3D attitude estimation
    provided by Yoctopuce inertial sensors. The four instances of YQt
    provide direct access to the individual quaternion components representing the
    orientation. It is usually not needed to use the YQt class
    directly, as the YGyro class provides a more convenient higher-level
    interface.

    """
    #--- (end of generated code: YQt class start)
    #--- (generated code: YQt return codes)
    #--- (end of generated code: YQt return codes)
    #--- (generated code: YQt definitions)
    #--- (end of generated code: YQt definitions)

    def __init__(self, func):
        super(YQt, self).__init__(func)
        self._className = 'Qt'
        #--- (generated code: YQt attributes)
        self._callback = None
        #--- (end of generated code: YQt attributes)

    #--- (generated code: YQt implementation)
    def _parseAttr(self, json_val):
        super(YQt, self)._parseAttr(json_val)

    @staticmethod
    def FindQt(func):
        """
        Retrieves a quaternion component for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the quaternion component is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YQt.isOnline() to test if the quaternion component is
        indeed online at a given time. In case of ambiguity when looking for
        a quaternion component by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the quaternion component, for instance
                Y3DMK002.qt1.

        @return a YQt object allowing you to drive the quaternion component.
        """
        # obj
        obj = YFunction._FindFromCache("Qt", func)
        if obj is None:
            obj = YQt(func)
            YFunction._AddToCache("Qt", func, obj)
        return obj

    def nextQt(self):
        """
        Continues the enumeration of quaternion components started using yFirstQt().
        Caution: You can't make any assumption about the returned quaternion components order.
        If you want to find a specific a quaternion component, use Qt.findQt()
        and a hardwareID or a logical name.

        @return a pointer to a YQt object, corresponding to
                a quaternion component currently online, or a None pointer
                if there are no more quaternion components to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YQt.FindQt(hwidRef.value)

#--- (end of generated code: YQt implementation)

#--- (generated code: YQt functions)

    @staticmethod
    def FirstQt():
        """
        Starts the enumeration of quaternion components currently accessible.
        Use the method YQt.nextQt() to iterate on
        next quaternion components.

        @return a pointer to a YQt object, corresponding to
                the first quaternion component currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Qt", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YQt.FindQt(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YQt functions)

def yInternalGyroCallback(YQt_obj, str_value):
    gyro = YQt_obj.get_userData()
    if gyro is None:
        return
    tmp = YQt_obj.get_functionId()[2]
    idx = int(tmp)
    dbl_value = float(str_value)
    # noinspection PyProtectedMember
    gyro._invokeGyroCallbacks(idx, dbl_value)

#--- (generated code: YGyro class start)
#noinspection PyProtectedMember
class YGyro(YSensor):
    """
    The YGyro class allows you to read and configure Yoctopuce gyroscopes.
    It inherits from YSensor class the core functions to read measurements,
    to register callback functions, and to access the autonomous datalogger.
    This class adds the possibility to access x, y and z components of the rotation
    vector separately, as well as the possibility to deal with quaternion-based
    orientation estimates.

    """
    #--- (end of generated code: YGyro class start)
    #--- (generated code: YGyro return codes)
    #--- (end of generated code: YGyro return codes)
    #--- (generated code: YGyro definitions)
    BANDWIDTH_INVALID = YAPI.INVALID_UINT
    XVALUE_INVALID = YAPI.INVALID_DOUBLE
    YVALUE_INVALID = YAPI.INVALID_DOUBLE
    ZVALUE_INVALID = YAPI.INVALID_DOUBLE
    #--- (end of generated code: YGyro definitions)

    def __init__(self, func):
        super(YGyro, self).__init__(func)
        self._className = 'Gyro'
        #--- (generated code: YGyro attributes)
        self._callback = None
        self._bandwidth = YGyro.BANDWIDTH_INVALID
        self._xValue = YGyro.XVALUE_INVALID
        self._yValue = YGyro.YVALUE_INVALID
        self._zValue = YGyro.ZVALUE_INVALID
        self._qt_stamp = 0
        self._qt_w = None
        self._qt_x = None
        self._qt_y = None
        self._qt_z = None
        self._w = 0
        self._x = 0
        self._y = 0
        self._z = 0
        self._angles_stamp = 0
        self._head = 0
        self._pitch = 0
        self._roll = 0
        self._quatCallback = None
        self._anglesCallback = None
        #--- (end of generated code: YGyro attributes)

    #--- (generated code: YGyro implementation)
    def _parseAttr(self, json_val):
        if json_val.has("bandwidth"):
            self._bandwidth = json_val.getInt("bandwidth")
        if json_val.has("xValue"):
            self._xValue = round(json_val.getDouble("xValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("yValue"):
            self._yValue = round(json_val.getDouble("yValue") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("zValue"):
            self._zValue = round(json_val.getDouble("zValue") * 1000.0 / 65536.0) / 1000.0
        super(YGyro, self)._parseAttr(json_val)

    def get_bandwidth(self):
        """
        Returns the measure update frequency, measured in Hz (Yocto-3D-V2 only).

        @return an integer corresponding to the measure update frequency, measured in Hz (Yocto-3D-V2 only)

        On failure, throws an exception or returns YGyro.BANDWIDTH_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGyro.BANDWIDTH_INVALID
        res = self._bandwidth
        return res

    def set_bandwidth(self, newval):
        """
        Changes the measure update frequency, measured in Hz (Yocto-3D-V2 only). When the
        frequency is lower, the device performs averaging.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the measure update frequency, measured in Hz (Yocto-3D-V2 only)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("bandwidth", rest_val)

    def get_xValue(self):
        """
        Returns the angular velocity around the X axis of the device, as a floating point number.

        @return a floating point number corresponding to the angular velocity around the X axis of the
        device, as a floating point number

        On failure, throws an exception or returns YGyro.XVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGyro.XVALUE_INVALID
        res = self._xValue
        return res

    def get_yValue(self):
        """
        Returns the angular velocity around the Y axis of the device, as a floating point number.

        @return a floating point number corresponding to the angular velocity around the Y axis of the
        device, as a floating point number

        On failure, throws an exception or returns YGyro.YVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGyro.YVALUE_INVALID
        res = self._yValue
        return res

    def get_zValue(self):
        """
        Returns the angular velocity around the Z axis of the device, as a floating point number.

        @return a floating point number corresponding to the angular velocity around the Z axis of the
        device, as a floating point number

        On failure, throws an exception or returns YGyro.ZVALUE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YGyro.ZVALUE_INVALID
        res = self._zValue
        return res

    @staticmethod
    def FindGyro(func):
        """
        Retrieves a gyroscope for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the gyroscope is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YGyro.isOnline() to test if the gyroscope is
        indeed online at a given time. In case of ambiguity when looking for
        a gyroscope by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the gyroscope, for instance
                Y3DMK002.gyro.

        @return a YGyro object allowing you to drive the gyroscope.
        """
        # obj
        obj = YFunction._FindFromCache("Gyro", func)
        if obj is None:
            obj = YGyro(func)
            YFunction._AddToCache("Gyro", func, obj)
        return obj

    def _loadQuaternion(self):
        # now_stamp
        # age_ms
        now_stamp = int((YRelTickCount(YAPI.GetTickCount()) & (0x7FFFFFFF)))
        age_ms = (((now_stamp - self._qt_stamp)) & (0x7FFFFFFF))
        if (age_ms >= 10) or (self._qt_stamp == 0):
            if self.load(10) != YAPI.SUCCESS:
                return YAPI.DEVICE_NOT_FOUND
            if self._qt_stamp == 0:
                self._qt_w = YQt.FindQt("" + self._serial + ".qt1")
                self._qt_x = YQt.FindQt("" + self._serial + ".qt2")
                self._qt_y = YQt.FindQt("" + self._serial + ".qt3")
                self._qt_z = YQt.FindQt("" + self._serial + ".qt4")
            if self._qt_w.load(9) != YAPI.SUCCESS:
                return YAPI.DEVICE_NOT_FOUND
            if self._qt_x.load(9) != YAPI.SUCCESS:
                return YAPI.DEVICE_NOT_FOUND
            if self._qt_y.load(9) != YAPI.SUCCESS:
                return YAPI.DEVICE_NOT_FOUND
            if self._qt_z.load(9) != YAPI.SUCCESS:
                return YAPI.DEVICE_NOT_FOUND
            self._w = self._qt_w.get_currentValue()
            self._x = self._qt_x.get_currentValue()
            self._y = self._qt_y.get_currentValue()
            self._z = self._qt_z.get_currentValue()
            self._qt_stamp = now_stamp
        return YAPI.SUCCESS

    def _loadAngles(self):
        # sqw
        # sqx
        # sqy
        # sqz
        # norm
        # delta

        if self._loadQuaternion() != YAPI.SUCCESS:
            return YAPI.DEVICE_NOT_FOUND
        if self._angles_stamp != self._qt_stamp:
            sqw = self._w * self._w
            sqx = self._x * self._x
            sqy = self._y * self._y
            sqz = self._z * self._z
            norm = sqx + sqy + sqz + sqw
            delta = self._y * self._w - self._x * self._z
            if delta > 0.499 * norm:
                # // singularity at north pole
                self._pitch = 90.0
                self._head  = round(2.0 * 1800.0/math.pi * math.atan2(self._x,-self._w)) / 10.0
            else:
                if delta < -0.499 * norm:
                    # // singularity at south pole
                    self._pitch = -90.0
                    self._head  = round(-2.0 * 1800.0/math.pi * math.atan2(self._x,-self._w)) / 10.0
                else:
                    self._roll  = round(1800.0/math.pi * math.atan2(2.0 * (self._w * self._x + self._y * self._z),sqw - sqx - sqy + sqz)) / 10.0
                    self._pitch = round(1800.0/math.pi * math.asin(2.0 * delta / norm)) / 10.0
                    self._head  = round(1800.0/math.pi * math.atan2(2.0 * (self._x * self._y + self._z * self._w),sqw + sqx - sqy - sqz)) / 10.0
            self._angles_stamp = self._qt_stamp
        return YAPI.SUCCESS

    def get_roll(self):
        """
        Returns the estimated roll angle, based on the integration of
        gyroscopic measures combined with acceleration and
        magnetic field measurements.
        The axis corresponding to the roll angle can be mapped to any
        of the device X, Y or Z physical directions using methods of
        the class YRefFrame.

        @return a floating-point number corresponding to roll angle
                in degrees, between -180 and +180.
        """
        self._loadAngles()
        return self._roll

    def get_pitch(self):
        """
        Returns the estimated pitch angle, based on the integration of
        gyroscopic measures combined with acceleration and
        magnetic field measurements.
        The axis corresponding to the pitch angle can be mapped to any
        of the device X, Y or Z physical directions using methods of
        the class YRefFrame.

        @return a floating-point number corresponding to pitch angle
                in degrees, between -90 and +90.
        """
        self._loadAngles()
        return self._pitch

    def get_heading(self):
        """
        Returns the estimated heading angle, based on the integration of
        gyroscopic measures combined with acceleration and
        magnetic field measurements.
        The axis corresponding to the heading can be mapped to any
        of the device X, Y or Z physical directions using methods of
        the class YRefFrame.

        @return a floating-point number corresponding to heading
                in degrees, between 0 and 360.
        """
        self._loadAngles()
        return self._head

    def get_quaternionW(self):
        """
        Returns the w component (real part) of the quaternion
        describing the device estimated orientation, based on the
        integration of gyroscopic measures combined with acceleration and
        magnetic field measurements.

        @return a floating-point number corresponding to the w
                component of the quaternion.
        """
        self._loadQuaternion()
        return self._w

    def get_quaternionX(self):
        """
        Returns the x component of the quaternion
        describing the device estimated orientation, based on the
        integration of gyroscopic measures combined with acceleration and
        magnetic field measurements. The x component is
        mostly correlated with rotations on the roll axis.

        @return a floating-point number corresponding to the x
                component of the quaternion.
        """
        self._loadQuaternion()
        return self._x

    def get_quaternionY(self):
        """
        Returns the y component of the quaternion
        describing the device estimated orientation, based on the
        integration of gyroscopic measures combined with acceleration and
        magnetic field measurements. The y component is
        mostly correlated with rotations on the pitch axis.

        @return a floating-point number corresponding to the y
                component of the quaternion.
        """
        self._loadQuaternion()
        return self._y

    def get_quaternionZ(self):
        """
        Returns the x component of the quaternion
        describing the device estimated orientation, based on the
        integration of gyroscopic measures combined with acceleration and
        magnetic field measurements. The x component is
        mostly correlated with changes of heading.

        @return a floating-point number corresponding to the z
                component of the quaternion.
        """
        self._loadQuaternion()
        return self._z

    def registerQuaternionCallback(self, callback):
        """
        Registers a callback function that will be invoked each time that the estimated
        device orientation has changed. The call frequency is typically around 95Hz during a move.
        The callback is invoked only during the execution of ySleep or yHandleEvents.
        This provides control over the time when the callback is triggered.
        For good responsiveness, remember to call one of these two functions periodically.
        To unregister a callback, pass a None pointer as argument.

        @param callback : the callback function to invoke, or a None pointer.
                The callback function should take five arguments:
                the YGyro object of the turning device, and the floating
                point values of the four components w, x, y and z
                (as floating-point numbers).
        @noreturn
        """
        self._quatCallback = callback
        if callback is not None:
            if self._loadQuaternion() != YAPI.SUCCESS:
                return YAPI.DEVICE_NOT_FOUND
            self._qt_w.set_userData(self)
            self._qt_x.set_userData(self)
            self._qt_y.set_userData(self)
            self._qt_z.set_userData(self)
            self._qt_w.registerValueCallback(yInternalGyroCallback)
            self._qt_x.registerValueCallback(yInternalGyroCallback)
            self._qt_y.registerValueCallback(yInternalGyroCallback)
            self._qt_z.registerValueCallback(yInternalGyroCallback)
        else:
            if not (self._anglesCallback is not None):
                self._qt_w.registerValueCallback(None)
                self._qt_x.registerValueCallback(None)
                self._qt_y.registerValueCallback(None)
                self._qt_z.registerValueCallback(None)
        return 0

    def registerAnglesCallback(self, callback):
        """
        Registers a callback function that will be invoked each time that the estimated
        device orientation has changed. The call frequency is typically around 95Hz during a move.
        The callback is invoked only during the execution of ySleep or yHandleEvents.
        This provides control over the time when the callback is triggered.
        For good responsiveness, remember to call one of these two functions periodically.
        To unregister a callback, pass a None pointer as argument.

        @param callback : the callback function to invoke, or a None pointer.
                The callback function should take four arguments:
                the YGyro object of the turning device, and the floating
                point values of the three angles roll, pitch and heading
                in degrees (as floating-point numbers).
        @noreturn
        """
        self._anglesCallback = callback
        if callback is not None:
            if self._loadQuaternion() != YAPI.SUCCESS:
                return YAPI.DEVICE_NOT_FOUND
            self._qt_w.set_userData(self)
            self._qt_x.set_userData(self)
            self._qt_y.set_userData(self)
            self._qt_z.set_userData(self)
            self._qt_w.registerValueCallback(yInternalGyroCallback)
            self._qt_x.registerValueCallback(yInternalGyroCallback)
            self._qt_y.registerValueCallback(yInternalGyroCallback)
            self._qt_z.registerValueCallback(yInternalGyroCallback)
        else:
            if not (self._quatCallback is not None):
                self._qt_w.registerValueCallback(None)
                self._qt_x.registerValueCallback(None)
                self._qt_y.registerValueCallback(None)
                self._qt_z.registerValueCallback(None)
        return 0

    def _invokeGyroCallbacks(self, qtIndex, qtValue):
        if qtIndex - 1 == 0:
            self._w = qtValue
        elif qtIndex - 1 == 1:
            self._x = qtValue
        elif qtIndex - 1 == 2:
            self._y = qtValue
        elif qtIndex - 1 == 3:
            self._z = qtValue
        if qtIndex < 4:
            return 0
        self._qt_stamp = int((YRelTickCount(YAPI.GetTickCount()) & (0x7FFFFFFF)))
        if self._quatCallback is not None:
            self._quatCallback(self, self._w, self._x, self._y, self._z)
        if self._anglesCallback is not None:
            self._loadAngles()
            self._anglesCallback(self, self._roll, self._pitch, self._head)
        return 0

    def nextGyro(self):
        """
        Continues the enumeration of gyroscopes started using yFirstGyro().
        Caution: You can't make any assumption about the returned gyroscopes order.
        If you want to find a specific a gyroscope, use Gyro.findGyro()
        and a hardwareID or a logical name.

        @return a pointer to a YGyro object, corresponding to
                a gyroscope currently online, or a None pointer
                if there are no more gyroscopes to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YGyro.FindGyro(hwidRef.value)

#--- (end of generated code: YGyro implementation)

#--- (generated code: YGyro functions)

    @staticmethod
    def FirstGyro():
        """
        Starts the enumeration of gyroscopes currently accessible.
        Use the method YGyro.nextGyro() to iterate on
        next gyroscopes.

        @return a pointer to a YGyro object, corresponding to
                the first gyro currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Gyro", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YGyro.FindGyro(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YGyro functions)
