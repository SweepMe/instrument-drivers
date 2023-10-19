# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_steppermotor.py 37827 2019-10-25 13:07:48Z mvuilleu $
#
#  Implements yFindStepperMotor(), the high-level API for StepperMotor functions
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


#--- (YStepperMotor class start)
#noinspection PyProtectedMember
class YStepperMotor(YFunction):
    """
    The YStepperMotor class allows you to drive a stepper motor.

    """
    #--- (end of YStepperMotor class start)
    #--- (YStepperMotor return codes)
    #--- (end of YStepperMotor return codes)
    #--- (YStepperMotor dlldef)
    #--- (end of YStepperMotor dlldef)
    #--- (YStepperMotor yapiwrapper)
    #--- (end of YStepperMotor yapiwrapper)
    #--- (YStepperMotor definitions)
    DIAGS_INVALID = YAPI.INVALID_UINT
    STEPPOS_INVALID = YAPI.INVALID_DOUBLE
    SPEED_INVALID = YAPI.INVALID_DOUBLE
    PULLINSPEED_INVALID = YAPI.INVALID_DOUBLE
    MAXACCEL_INVALID = YAPI.INVALID_DOUBLE
    MAXSPEED_INVALID = YAPI.INVALID_DOUBLE
    OVERCURRENT_INVALID = YAPI.INVALID_UINT
    TCURRSTOP_INVALID = YAPI.INVALID_UINT
    TCURRRUN_INVALID = YAPI.INVALID_UINT
    ALERTMODE_INVALID = YAPI.INVALID_STRING
    AUXMODE_INVALID = YAPI.INVALID_STRING
    AUXSIGNAL_INVALID = YAPI.INVALID_INT
    COMMAND_INVALID = YAPI.INVALID_STRING
    MOTORSTATE_ABSENT = 0
    MOTORSTATE_ALERT = 1
    MOTORSTATE_HI_Z = 2
    MOTORSTATE_STOP = 3
    MOTORSTATE_RUN = 4
    MOTORSTATE_BATCH = 5
    MOTORSTATE_INVALID = -1
    STEPPING_MICROSTEP16 = 0
    STEPPING_MICROSTEP8 = 1
    STEPPING_MICROSTEP4 = 2
    STEPPING_HALFSTEP = 3
    STEPPING_FULLSTEP = 4
    STEPPING_INVALID = -1
    #--- (end of YStepperMotor definitions)

    def __init__(self, func):
        super(YStepperMotor, self).__init__(func)
        self._className = 'StepperMotor'
        #--- (YStepperMotor attributes)
        self._callback = None
        self._motorState = YStepperMotor.MOTORSTATE_INVALID
        self._diags = YStepperMotor.DIAGS_INVALID
        self._stepPos = YStepperMotor.STEPPOS_INVALID
        self._speed = YStepperMotor.SPEED_INVALID
        self._pullinSpeed = YStepperMotor.PULLINSPEED_INVALID
        self._maxAccel = YStepperMotor.MAXACCEL_INVALID
        self._maxSpeed = YStepperMotor.MAXSPEED_INVALID
        self._stepping = YStepperMotor.STEPPING_INVALID
        self._overcurrent = YStepperMotor.OVERCURRENT_INVALID
        self._tCurrStop = YStepperMotor.TCURRSTOP_INVALID
        self._tCurrRun = YStepperMotor.TCURRRUN_INVALID
        self._alertMode = YStepperMotor.ALERTMODE_INVALID
        self._auxMode = YStepperMotor.AUXMODE_INVALID
        self._auxSignal = YStepperMotor.AUXSIGNAL_INVALID
        self._command = YStepperMotor.COMMAND_INVALID
        #--- (end of YStepperMotor attributes)

    #--- (YStepperMotor implementation)
    def _parseAttr(self, json_val):
        if json_val.has("motorState"):
            self._motorState = json_val.getInt("motorState")
        if json_val.has("diags"):
            self._diags = json_val.getInt("diags")
        if json_val.has("stepPos"):
            self._stepPos = json_val.getDouble("stepPos") / 16.0
        if json_val.has("speed"):
            self._speed = round(json_val.getDouble("speed") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("pullinSpeed"):
            self._pullinSpeed = round(json_val.getDouble("pullinSpeed") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("maxAccel"):
            self._maxAccel = round(json_val.getDouble("maxAccel") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("maxSpeed"):
            self._maxSpeed = round(json_val.getDouble("maxSpeed") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("stepping"):
            self._stepping = json_val.getInt("stepping")
        if json_val.has("overcurrent"):
            self._overcurrent = json_val.getInt("overcurrent")
        if json_val.has("tCurrStop"):
            self._tCurrStop = json_val.getInt("tCurrStop")
        if json_val.has("tCurrRun"):
            self._tCurrRun = json_val.getInt("tCurrRun")
        if json_val.has("alertMode"):
            self._alertMode = json_val.getString("alertMode")
        if json_val.has("auxMode"):
            self._auxMode = json_val.getString("auxMode")
        if json_val.has("auxSignal"):
            self._auxSignal = json_val.getInt("auxSignal")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YStepperMotor, self)._parseAttr(json_val)

    def get_motorState(self):
        """
        Returns the motor working state.

        @return a value among YStepperMotor.MOTORSTATE_ABSENT, YStepperMotor.MOTORSTATE_ALERT,
        YStepperMotor.MOTORSTATE_HI_Z, YStepperMotor.MOTORSTATE_STOP, YStepperMotor.MOTORSTATE_RUN and
        YStepperMotor.MOTORSTATE_BATCH corresponding to the motor working state

        On failure, throws an exception or returns YStepperMotor.MOTORSTATE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.MOTORSTATE_INVALID
        res = self._motorState
        return res

    def get_diags(self):
        """
        Returns the stepper motor controller diagnostics, as a bitmap.

        @return an integer corresponding to the stepper motor controller diagnostics, as a bitmap

        On failure, throws an exception or returns YStepperMotor.DIAGS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.DIAGS_INVALID
        res = self._diags
        return res

    def set_stepPos(self, newval):
        """
        Changes the current logical motor position, measured in steps.
        This command does not cause any motor move, as its purpose is only to setup
        the origin of the position counter. The fractional part of the position,
        that corresponds to the physical position of the rotor, is not changed.
        To trigger a motor move, use methods moveTo() or moveRel()
        instead.

        @param newval : a floating point number corresponding to the current logical motor position, measured in steps

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "%.2f" % (round(newval * 100.0, 1)/100.0)
        return self._setAttr("stepPos", rest_val)

    def get_stepPos(self):
        """
        Returns the current logical motor position, measured in steps.
        The value may include a fractional part when micro-stepping is in use.

        @return a floating point number corresponding to the current logical motor position, measured in steps

        On failure, throws an exception or returns YStepperMotor.STEPPOS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.STEPPOS_INVALID
        res = self._stepPos
        return res

    def get_speed(self):
        """
        Returns current motor speed, measured in steps per second.
        To change speed, use method changeSpeed().

        @return a floating point number corresponding to current motor speed, measured in steps per second

        On failure, throws an exception or returns YStepperMotor.SPEED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.SPEED_INVALID
        res = self._speed
        return res

    def set_pullinSpeed(self, newval):
        """
        Changes the motor speed immediately reachable from stop state, measured in steps per second.

        @param newval : a floating point number corresponding to the motor speed immediately reachable from
        stop state, measured in steps per second

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("pullinSpeed", rest_val)

    def get_pullinSpeed(self):
        """
        Returns the motor speed immediately reachable from stop state, measured in steps per second.

        @return a floating point number corresponding to the motor speed immediately reachable from stop
        state, measured in steps per second

        On failure, throws an exception or returns YStepperMotor.PULLINSPEED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.PULLINSPEED_INVALID
        res = self._pullinSpeed
        return res

    def set_maxAccel(self, newval):
        """
        Changes the maximal motor acceleration, measured in steps per second^2.

        @param newval : a floating point number corresponding to the maximal motor acceleration, measured
        in steps per second^2

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("maxAccel", rest_val)

    def get_maxAccel(self):
        """
        Returns the maximal motor acceleration, measured in steps per second^2.

        @return a floating point number corresponding to the maximal motor acceleration, measured in steps per second^2

        On failure, throws an exception or returns YStepperMotor.MAXACCEL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.MAXACCEL_INVALID
        res = self._maxAccel
        return res

    def set_maxSpeed(self, newval):
        """
        Changes the maximal motor speed, measured in steps per second.

        @param newval : a floating point number corresponding to the maximal motor speed, measured in steps per second

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("maxSpeed", rest_val)

    def get_maxSpeed(self):
        """
        Returns the maximal motor speed, measured in steps per second.

        @return a floating point number corresponding to the maximal motor speed, measured in steps per second

        On failure, throws an exception or returns YStepperMotor.MAXSPEED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.MAXSPEED_INVALID
        res = self._maxSpeed
        return res

    def get_stepping(self):
        """
        Returns the stepping mode used to drive the motor.

        @return a value among YStepperMotor.STEPPING_MICROSTEP16, YStepperMotor.STEPPING_MICROSTEP8,
        YStepperMotor.STEPPING_MICROSTEP4, YStepperMotor.STEPPING_HALFSTEP and
        YStepperMotor.STEPPING_FULLSTEP corresponding to the stepping mode used to drive the motor

        On failure, throws an exception or returns YStepperMotor.STEPPING_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.STEPPING_INVALID
        res = self._stepping
        return res

    def set_stepping(self, newval):
        """
        Changes the stepping mode used to drive the motor.

        @param newval : a value among YStepperMotor.STEPPING_MICROSTEP16,
        YStepperMotor.STEPPING_MICROSTEP8, YStepperMotor.STEPPING_MICROSTEP4,
        YStepperMotor.STEPPING_HALFSTEP and YStepperMotor.STEPPING_FULLSTEP corresponding to the stepping
        mode used to drive the motor

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("stepping", rest_val)

    def get_overcurrent(self):
        """
        Returns the overcurrent alert and emergency stop threshold, measured in mA.

        @return an integer corresponding to the overcurrent alert and emergency stop threshold, measured in mA

        On failure, throws an exception or returns YStepperMotor.OVERCURRENT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.OVERCURRENT_INVALID
        res = self._overcurrent
        return res

    def set_overcurrent(self, newval):
        """
        Changes the overcurrent alert and emergency stop threshold, measured in mA.

        @param newval : an integer corresponding to the overcurrent alert and emergency stop threshold, measured in mA

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("overcurrent", rest_val)

    def get_tCurrStop(self):
        """
        Returns the torque regulation current when the motor is stopped, measured in mA.

        @return an integer corresponding to the torque regulation current when the motor is stopped, measured in mA

        On failure, throws an exception or returns YStepperMotor.TCURRSTOP_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.TCURRSTOP_INVALID
        res = self._tCurrStop
        return res

    def set_tCurrStop(self, newval):
        """
        Changes the torque regulation current when the motor is stopped, measured in mA.

        @param newval : an integer corresponding to the torque regulation current when the motor is
        stopped, measured in mA

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("tCurrStop", rest_val)

    def get_tCurrRun(self):
        """
        Returns the torque regulation current when the motor is running, measured in mA.

        @return an integer corresponding to the torque regulation current when the motor is running, measured in mA

        On failure, throws an exception or returns YStepperMotor.TCURRRUN_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.TCURRRUN_INVALID
        res = self._tCurrRun
        return res

    def set_tCurrRun(self, newval):
        """
        Changes the torque regulation current when the motor is running, measured in mA.

        @param newval : an integer corresponding to the torque regulation current when the motor is
        running, measured in mA

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("tCurrRun", rest_val)

    def get_alertMode(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.ALERTMODE_INVALID
        res = self._alertMode
        return res

    def set_alertMode(self, newval):
        rest_val = newval
        return self._setAttr("alertMode", rest_val)

    def get_auxMode(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.AUXMODE_INVALID
        res = self._auxMode
        return res

    def set_auxMode(self, newval):
        rest_val = newval
        return self._setAttr("auxMode", rest_val)

    def get_auxSignal(self):
        """
        Returns the current value of the signal generated on the auxiliary output.

        @return an integer corresponding to the current value of the signal generated on the auxiliary output

        On failure, throws an exception or returns YStepperMotor.AUXSIGNAL_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.AUXSIGNAL_INVALID
        res = self._auxSignal
        return res

    def set_auxSignal(self, newval):
        """
        Changes the value of the signal generated on the auxiliary output.
        Acceptable values depend on the auxiliary output signal type configured.

        @param newval : an integer corresponding to the value of the signal generated on the auxiliary output

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("auxSignal", rest_val)

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YStepperMotor.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindStepperMotor(func):
        """
        Retrieves a stepper motor for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the stepper motor is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YStepperMotor.isOnline() to test if the stepper motor is
        indeed online at a given time. In case of ambiguity when looking for
        a stepper motor by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the stepper motor, for instance
                MyDevice.stepperMotor1.

        @return a YStepperMotor object allowing you to drive the stepper motor.
        """
        # obj
        obj = YFunction._FindFromCache("StepperMotor", func)
        if obj is None:
            obj = YStepperMotor(func)
            YFunction._AddToCache("StepperMotor", func, obj)
        return obj

    def sendCommand(self, command):
        # id
        # url
        # retBin
        # res
        id = self.get_functionId()
        id = (id)[12: 12 + 1]
        url = "cmd.txt?" + id + "=" + command
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
        Reinitialize the controller and clear all alert flags.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("Z")

    def findHomePosition(self, speed):
        """
        Starts the motor backward at the specified speed, to search for the motor home position.

        @param speed : desired speed, in steps per second.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("H" + str(int(round(1000*speed))))

    def changeSpeed(self, speed):
        """
        Starts the motor at a given speed. The time needed to reach the requested speed
        will depend on the acceleration parameters configured for the motor.

        @param speed : desired speed, in steps per second. The minimal non-zero speed
                is 0.001 pulse per second.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("R" + str(int(round(1000*speed))))

    def moveTo(self, absPos):
        """
        Starts the motor to reach a given absolute position. The time needed to reach the requested
        position will depend on the acceleration and max speed parameters configured for
        the motor.

        @param absPos : absolute position, measured in steps from the origin.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("M" + str(int(round(16*absPos))))

    def moveRel(self, relPos):
        """
        Starts the motor to reach a given relative position. The time needed to reach the requested
        position will depend on the acceleration and max speed parameters configured for
        the motor.

        @param relPos : relative position, measured in steps from the current position.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("m" + str(int(round(16*relPos))))

    def moveRelSlow(self, relPos, maxSpeed):
        """
        Starts the motor to reach a given relative position, keeping the speed under the
        specified limit. The time needed to reach the requested position will depend on
        the acceleration parameters configured for the motor.

        @param relPos : relative position, measured in steps from the current position.
        @param maxSpeed : limit speed, in steps per second.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("m" + str(int(round(16*relPos))) + "@" + str(int(round(1000*maxSpeed))))

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

    def alertStepOut(self):
        """
        Move one step in the direction opposite the direction set when the most recent alert was raised.
        The move occurs even if the system is still in alert mode (end switch depressed). Caution.
        use this function with great care as it may cause mechanical damages !

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.set_command(".")

    def alertStepDir(self, dir):
        """
        Move one single step in the selected direction without regards to end switches.
        The move occurs even if the system is still in alert mode (end switch depressed). Caution.
        use this function with great care as it may cause mechanical damages !

        @param dir : Value +1 or -1, according to the desired direction of the move

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        if not (dir != 0):
            self._throw(YAPI.INVALID_ARGUMENT, "direction must be +1 or -1")
            return YAPI.INVALID_ARGUMENT
        if dir > 0:
            return self.set_command(".+")
        return self.set_command(".-")

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

    def nextStepperMotor(self):
        """
        Continues the enumeration of stepper motors started using yFirstStepperMotor().
        Caution: You can't make any assumption about the returned stepper motors order.
        If you want to find a specific a stepper motor, use StepperMotor.findStepperMotor()
        and a hardwareID or a logical name.

        @return a pointer to a YStepperMotor object, corresponding to
                a stepper motor currently online, or a None pointer
                if there are no more stepper motors to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YStepperMotor.FindStepperMotor(hwidRef.value)

#--- (end of YStepperMotor implementation)

#--- (YStepperMotor functions)

    @staticmethod
    def FirstStepperMotor():
        """
        Starts the enumeration of stepper motors currently accessible.
        Use the method YStepperMotor.nextStepperMotor() to iterate on
        next stepper motors.

        @return a pointer to a YStepperMotor object, corresponding to
                the first stepper motor currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("StepperMotor", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YStepperMotor.FindStepperMotor(serialRef.value + "." + funcIdRef.value)

#--- (end of YStepperMotor functions)
