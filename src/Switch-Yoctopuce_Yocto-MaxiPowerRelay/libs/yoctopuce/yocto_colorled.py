# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_colorled.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindColorLed(), the high-level API for ColorLed functions
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


#--- (YColorLed class start)
#noinspection PyProtectedMember
class YColorLed(YFunction):
    """
    The ColorLed class allows you to drive a color LED.
    The color can be specified using RGB coordinates as well as HSL coordinates.
    The module performs all conversions form RGB to HSL automatically. It is then
    self-evident to turn on a LED with a given hue and to progressively vary its
    saturation or lightness. If needed, you can find more information on the
    difference between RGB and HSL in the section following this one.

    """
    #--- (end of YColorLed class start)
    #--- (YColorLed return codes)
    #--- (end of YColorLed return codes)
    #--- (YColorLed dlldef)
    #--- (end of YColorLed dlldef)
    #--- (YColorLed yapiwrapper)
    #--- (end of YColorLed yapiwrapper)
    #--- (YColorLed definitions)
    RGBCOLOR_INVALID = YAPI.INVALID_UINT
    HSLCOLOR_INVALID = YAPI.INVALID_UINT
    RGBMOVE_INVALID = None
    HSLMOVE_INVALID = None
    RGBCOLORATPOWERON_INVALID = YAPI.INVALID_UINT
    BLINKSEQSIZE_INVALID = YAPI.INVALID_UINT
    BLINKSEQMAXSIZE_INVALID = YAPI.INVALID_UINT
    BLINKSEQSIGNATURE_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    #--- (end of YColorLed definitions)

    def __init__(self, func):
        super(YColorLed, self).__init__(func)
        self._className = 'ColorLed'
        #--- (YColorLed attributes)
        self._callback = None
        self._rgbColor = YColorLed.RGBCOLOR_INVALID
        self._hslColor = YColorLed.HSLCOLOR_INVALID
        self._rgbMove = YColorLed.RGBMOVE_INVALID
        self._hslMove = YColorLed.HSLMOVE_INVALID
        self._rgbColorAtPowerOn = YColorLed.RGBCOLORATPOWERON_INVALID
        self._blinkSeqSize = YColorLed.BLINKSEQSIZE_INVALID
        self._blinkSeqMaxSize = YColorLed.BLINKSEQMAXSIZE_INVALID
        self._blinkSeqSignature = YColorLed.BLINKSEQSIGNATURE_INVALID
        self._command = YColorLed.COMMAND_INVALID
        #--- (end of YColorLed attributes)

    #--- (YColorLed implementation)
    def _parseAttr(self, json_val):
        if json_val.has("rgbColor"):
            self._rgbColor = json_val.getInt("rgbColor")
        if json_val.has("hslColor"):
            self._hslColor = json_val.getInt("hslColor")
        if json_val.has("rgbMove"):
            subjson = json_val.getYJSONObject("rgbMove");
            self._rgbMove = {"moving": None, "target": None, "ms": None}
            if subjson.has("moving"):
                self._rgbMove["moving"] = subjson.getInt("moving")
            if subjson.has("target"):
                self._rgbMove["target"] = subjson.getInt("target")
            if subjson.has("ms"):
                self._rgbMove["ms"] = subjson.getInt("ms")
        if json_val.has("hslMove"):
            subjson = json_val.getYJSONObject("hslMove");
            self._hslMove = {"moving": None, "target": None, "ms": None}
            if subjson.has("moving"):
                self._hslMove["moving"] = subjson.getInt("moving")
            if subjson.has("target"):
                self._hslMove["target"] = subjson.getInt("target")
            if subjson.has("ms"):
                self._hslMove["ms"] = subjson.getInt("ms")
        if json_val.has("rgbColorAtPowerOn"):
            self._rgbColorAtPowerOn = json_val.getInt("rgbColorAtPowerOn")
        if json_val.has("blinkSeqSize"):
            self._blinkSeqSize = json_val.getInt("blinkSeqSize")
        if json_val.has("blinkSeqMaxSize"):
            self._blinkSeqMaxSize = json_val.getInt("blinkSeqMaxSize")
        if json_val.has("blinkSeqSignature"):
            self._blinkSeqSignature = json_val.getInt("blinkSeqSignature")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YColorLed, self)._parseAttr(json_val)

    def get_rgbColor(self):
        """
        Returns the current RGB color of the LED.

        @return an integer corresponding to the current RGB color of the LED

        On failure, throws an exception or returns YColorLed.RGBCOLOR_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLed.RGBCOLOR_INVALID
        res = self._rgbColor
        return res

    def set_rgbColor(self, newval):
        """
        Changes the current color of the LED, using an RGB color. Encoding is done as follows: 0xRRGGBB.

        @param newval : an integer corresponding to the current color of the LED, using an RGB color

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "0x" + '%X' % newval
        return self._setAttr("rgbColor", rest_val)

    def get_hslColor(self):
        """
        Returns the current HSL color of the LED.

        @return an integer corresponding to the current HSL color of the LED

        On failure, throws an exception or returns YColorLed.HSLCOLOR_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLed.HSLCOLOR_INVALID
        res = self._hslColor
        return res

    def set_hslColor(self, newval):
        """
        Changes the current color of the LED, using a color HSL. Encoding is done as follows: 0xHHSSLL.

        @param newval : an integer corresponding to the current color of the LED, using a color HSL

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "0x" + '%X' % newval
        return self._setAttr("hslColor", rest_val)

    def get_rgbMove(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLed.RGBMOVE_INVALID
        res = self._rgbMove
        return res

    def set_rgbMove(self, newval):
        rest_val = str(newval.target) + ":" + str(newval.ms)
        return self._setAttr("rgbMove", rest_val)

    def rgbMove(self, rgb_target, ms_duration):
        """
        Performs a smooth transition in the RGB color space between the current color and a target color.

        @param rgb_target  : desired RGB color at the end of the transition
        @param ms_duration : duration of the transition, in millisecond

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(rgb_target) + ":" + str(ms_duration)
        return self._setAttr("rgbMove", rest_val)

    def get_hslMove(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLed.HSLMOVE_INVALID
        res = self._hslMove
        return res

    def set_hslMove(self, newval):
        rest_val = str(newval.target) + ":" + str(newval.ms)
        return self._setAttr("hslMove", rest_val)

    def hslMove(self, hsl_target, ms_duration):
        """
        Performs a smooth transition in the HSL color space between the current color and a target color.

        @param hsl_target  : desired HSL color at the end of the transition
        @param ms_duration : duration of the transition, in millisecond

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(hsl_target) + ":" + str(ms_duration)
        return self._setAttr("hslMove", rest_val)

    def get_rgbColorAtPowerOn(self):
        """
        Returns the configured color to be displayed when the module is turned on.

        @return an integer corresponding to the configured color to be displayed when the module is turned on

        On failure, throws an exception or returns YColorLed.RGBCOLORATPOWERON_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLed.RGBCOLORATPOWERON_INVALID
        res = self._rgbColorAtPowerOn
        return res

    def set_rgbColorAtPowerOn(self, newval):
        """
        Changes the color that the LED displays by default when the module is turned on.
        Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : an integer corresponding to the color that the LED displays by default when the
        module is turned on

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "0x" + '%X' % newval
        return self._setAttr("rgbColorAtPowerOn", rest_val)

    def get_blinkSeqSize(self):
        """
        Returns the current length of the blinking sequence.

        @return an integer corresponding to the current length of the blinking sequence

        On failure, throws an exception or returns YColorLed.BLINKSEQSIZE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLed.BLINKSEQSIZE_INVALID
        res = self._blinkSeqSize
        return res

    def get_blinkSeqMaxSize(self):
        """
        Returns the maximum length of the blinking sequence.

        @return an integer corresponding to the maximum length of the blinking sequence

        On failure, throws an exception or returns YColorLed.BLINKSEQMAXSIZE_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLed.BLINKSEQMAXSIZE_INVALID
        res = self._blinkSeqMaxSize
        return res

    def get_blinkSeqSignature(self):
        """
        Return the blinking sequence signature. Since blinking
        sequences cannot be read from the device, this can be used
        to detect if a specific blinking sequence is already
        programmed.

        @return an integer

        On failure, throws an exception or returns YColorLed.BLINKSEQSIGNATURE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLed.BLINKSEQSIGNATURE_INVALID
        res = self._blinkSeqSignature
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLed.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindColorLed(func):
        """
        Retrieves an RGB LED for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the RGB LED is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YColorLed.isOnline() to test if the RGB LED is
        indeed online at a given time. In case of ambiguity when looking for
        an RGB LED by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the RGB LED, for instance
                YRGBLED2.colorLed1.

        @return a YColorLed object allowing you to drive the RGB LED.
        """
        # obj
        obj = YFunction._FindFromCache("ColorLed", func)
        if obj is None:
            obj = YColorLed(func)
            YFunction._AddToCache("ColorLed", func, obj)
        return obj

    def sendCommand(self, command):
        return self.set_command(command)

    def addHslMoveToBlinkSeq(self, HSLcolor, msDelay):
        """
        Add a new transition to the blinking sequence, the move will
        be performed in the HSL space.

        @param HSLcolor : desired HSL color when the transition is completed
        @param msDelay : duration of the color transition, in milliseconds.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("H" + str(int(HSLcolor)) + "," + str(int(msDelay)))

    def addRgbMoveToBlinkSeq(self, RGBcolor, msDelay):
        """
        Adds a new transition to the blinking sequence, the move is
        performed in the RGB space.

        @param RGBcolor : desired RGB color when the transition is completed
        @param msDelay : duration of the color transition, in milliseconds.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("R" + str(int(RGBcolor)) + "," + str(int(msDelay)))

    def startBlinkSeq(self):
        """
        Starts the preprogrammed blinking sequence. The sequence is
        run in a loop until it is stopped by stopBlinkSeq or an explicit
        change.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("S")

    def stopBlinkSeq(self):
        """
        Stops the preprogrammed blinking sequence.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("X")

    def resetBlinkSeq(self):
        """
        Resets the preprogrammed blinking sequence.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("Z")

    def nextColorLed(self):
        """
        Continues the enumeration of RGB LEDs started using yFirstColorLed().
        Caution: You can't make any assumption about the returned RGB LEDs order.
        If you want to find a specific an RGB LED, use ColorLed.findColorLed()
        and a hardwareID or a logical name.

        @return a pointer to a YColorLed object, corresponding to
                an RGB LED currently online, or a None pointer
                if there are no more RGB LEDs to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YColorLed.FindColorLed(hwidRef.value)

#--- (end of YColorLed implementation)

#--- (YColorLed functions)

    @staticmethod
    def FirstColorLed():
        """
        Starts the enumeration of RGB LEDs currently accessible.
        Use the method YColorLed.nextColorLed() to iterate on
        next RGB LEDs.

        @return a pointer to a YColorLed object, corresponding to
                the first RGB LED currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("ColorLed", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YColorLed.FindColorLed(serialRef.value + "." + funcIdRef.value)

#--- (end of YColorLed functions)
