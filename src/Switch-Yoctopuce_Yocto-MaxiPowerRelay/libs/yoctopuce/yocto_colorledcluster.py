# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_colorledcluster.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindColorLedCluster(), the high-level API for ColorLedCluster functions
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


#--- (YColorLedCluster class start)
#noinspection PyProtectedMember
class YColorLedCluster(YFunction):
    """
    The YColorLedCluster class allows you to drive a
    color LED cluster. Unlike the ColorLed class, the YColorLedCluster
    class allows to handle several LEDs at once. Color changes can be done using RGB
    coordinates as well as HSL coordinates.
    The module performs all conversions form RGB to HSL automatically. It is then
    self-evident to turn on a LED with a given hue and to progressively vary its
    saturation or lightness. If needed, you can find more information on the
    difference between RGB and HSL in the section following this one.

    """
    #--- (end of YColorLedCluster class start)
    #--- (YColorLedCluster return codes)
    #--- (end of YColorLedCluster return codes)
    #--- (YColorLedCluster dlldef)
    #--- (end of YColorLedCluster dlldef)
    #--- (YColorLedCluster yapiwrapper)
    #--- (end of YColorLedCluster yapiwrapper)
    #--- (YColorLedCluster definitions)
    ACTIVELEDCOUNT_INVALID = YAPI.INVALID_UINT
    MAXLEDCOUNT_INVALID = YAPI.INVALID_UINT
    BLINKSEQMAXCOUNT_INVALID = YAPI.INVALID_UINT
    BLINKSEQMAXSIZE_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    LEDTYPE_RGB = 0
    LEDTYPE_RGBW = 1
    LEDTYPE_INVALID = -1
    #--- (end of YColorLedCluster definitions)

    def __init__(self, func):
        super(YColorLedCluster, self).__init__(func)
        self._className = 'ColorLedCluster'
        #--- (YColorLedCluster attributes)
        self._callback = None
        self._activeLedCount = YColorLedCluster.ACTIVELEDCOUNT_INVALID
        self._ledType = YColorLedCluster.LEDTYPE_INVALID
        self._maxLedCount = YColorLedCluster.MAXLEDCOUNT_INVALID
        self._blinkSeqMaxCount = YColorLedCluster.BLINKSEQMAXCOUNT_INVALID
        self._blinkSeqMaxSize = YColorLedCluster.BLINKSEQMAXSIZE_INVALID
        self._command = YColorLedCluster.COMMAND_INVALID
        #--- (end of YColorLedCluster attributes)

    #--- (YColorLedCluster implementation)
    def _parseAttr(self, json_val):
        if json_val.has("activeLedCount"):
            self._activeLedCount = json_val.getInt("activeLedCount")
        if json_val.has("ledType"):
            self._ledType = json_val.getInt("ledType")
        if json_val.has("maxLedCount"):
            self._maxLedCount = json_val.getInt("maxLedCount")
        if json_val.has("blinkSeqMaxCount"):
            self._blinkSeqMaxCount = json_val.getInt("blinkSeqMaxCount")
        if json_val.has("blinkSeqMaxSize"):
            self._blinkSeqMaxSize = json_val.getInt("blinkSeqMaxSize")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YColorLedCluster, self)._parseAttr(json_val)

    def get_activeLedCount(self):
        """
        Returns the number of LEDs currently handled by the device.

        @return an integer corresponding to the number of LEDs currently handled by the device

        On failure, throws an exception or returns YColorLedCluster.ACTIVELEDCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLedCluster.ACTIVELEDCOUNT_INVALID
        res = self._activeLedCount
        return res

    def set_activeLedCount(self, newval):
        """
        Changes the number of LEDs currently handled by the device.
        Remember to call the matching module
        saveToFlash() method to save the setting permanently.

        @param newval : an integer corresponding to the number of LEDs currently handled by the device

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("activeLedCount", rest_val)

    def get_ledType(self):
        """
        Returns the RGB LED type currently handled by the device.

        @return either YColorLedCluster.LEDTYPE_RGB or YColorLedCluster.LEDTYPE_RGBW, according to the RGB
        LED type currently handled by the device

        On failure, throws an exception or returns YColorLedCluster.LEDTYPE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLedCluster.LEDTYPE_INVALID
        res = self._ledType
        return res

    def set_ledType(self, newval):
        """
        Changes the RGB LED type currently handled by the device.
        Remember to call the matching module
        saveToFlash() method to save the setting permanently.

        @param newval : either YColorLedCluster.LEDTYPE_RGB or YColorLedCluster.LEDTYPE_RGBW, according to
        the RGB LED type currently handled by the device

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("ledType", rest_val)

    def get_maxLedCount(self):
        """
        Returns the maximum number of LEDs that the device can handle.

        @return an integer corresponding to the maximum number of LEDs that the device can handle

        On failure, throws an exception or returns YColorLedCluster.MAXLEDCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLedCluster.MAXLEDCOUNT_INVALID
        res = self._maxLedCount
        return res

    def get_blinkSeqMaxCount(self):
        """
        Returns the maximum number of sequences that the device can handle.

        @return an integer corresponding to the maximum number of sequences that the device can handle

        On failure, throws an exception or returns YColorLedCluster.BLINKSEQMAXCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLedCluster.BLINKSEQMAXCOUNT_INVALID
        res = self._blinkSeqMaxCount
        return res

    def get_blinkSeqMaxSize(self):
        """
        Returns the maximum length of sequences.

        @return an integer corresponding to the maximum length of sequences

        On failure, throws an exception or returns YColorLedCluster.BLINKSEQMAXSIZE_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLedCluster.BLINKSEQMAXSIZE_INVALID
        res = self._blinkSeqMaxSize
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YColorLedCluster.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindColorLedCluster(func):
        """
        Retrieves a RGB LED cluster for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the RGB LED cluster is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YColorLedCluster.isOnline() to test if the RGB LED cluster is
        indeed online at a given time. In case of ambiguity when looking for
        a RGB LED cluster by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the RGB LED cluster, for instance
                YRGBLED2.colorLedCluster.

        @return a YColorLedCluster object allowing you to drive the RGB LED cluster.
        """
        # obj
        obj = YFunction._FindFromCache("ColorLedCluster", func)
        if obj is None:
            obj = YColorLedCluster(func)
            YFunction._AddToCache("ColorLedCluster", func, obj)
        return obj

    def sendCommand(self, command):
        return self.set_command(command)

    def set_rgbColor(self, ledIndex, count, rgbValue):
        """
        Changes the current color of consecutive LEDs in the cluster, using a RGB color. Encoding is done
        as follows: 0xRRGGBB.

        @param ledIndex :  index of the first affected LED.
        @param count    :  affected LED count.
        @param rgbValue :  new color.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("SR" + str(int(ledIndex)) + "," + str(int(count)) + "," + ("%x" % rgbValue))

    def set_rgbColorAtPowerOn(self, ledIndex, count, rgbValue):
        """
        Changes the  color at device startup of consecutive LEDs in the cluster, using a RGB color.
        Encoding is done as follows: 0xRRGGBB. Don't forget to call saveLedsConfigAtPowerOn()
        to make sure the modification is saved in the device flash memory.

        @param ledIndex :  index of the first affected LED.
        @param count    :  affected LED count.
        @param rgbValue :  new color.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("SC" + str(int(ledIndex)) + "," + str(int(count)) + "," + ("%x" % rgbValue))

    def set_hslColorAtPowerOn(self, ledIndex, count, hslValue):
        """
        Changes the  color at device startup of consecutive LEDs in the cluster, using a HSL color.
        Encoding is done as follows: 0xHHSSLL. Don't forget to call saveLedsConfigAtPowerOn()
        to make sure the modification is saved in the device flash memory.

        @param ledIndex :  index of the first affected LED.
        @param count    :  affected LED count.
        @param hslValue :  new color.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # rgbValue
        rgbValue = self.hsl2rgb(hslValue)
        return self.sendCommand("SC" + str(int(ledIndex)) + "," + str(int(count)) + "," + ("%x" % rgbValue))

    def set_hslColor(self, ledIndex, count, hslValue):
        """
        Changes the current color of consecutive LEDs in the cluster, using a HSL color. Encoding is done
        as follows: 0xHHSSLL.

        @param ledIndex :  index of the first affected LED.
        @param count    :  affected LED count.
        @param hslValue :  new color.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("SH" + str(int(ledIndex)) + "," + str(int(count)) + "," + ("%x" % hslValue))

    def rgb_move(self, ledIndex, count, rgbValue, delay):
        """
        Allows you to modify the current color of a group of adjacent LEDs to another color, in a seamless and
        autonomous manner. The transition is performed in the RGB space.

        @param ledIndex :  index of the first affected LED.
        @param count    :  affected LED count.
        @param rgbValue :  new color (0xRRGGBB).
        @param delay    :  transition duration in ms

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("MR" + str(int(ledIndex)) + "," + str(int(count)) + "," + ("%x" % rgbValue) + "," + str(int(delay)))

    def hsl_move(self, ledIndex, count, hslValue, delay):
        """
        Allows you to modify the current color of a group of adjacent LEDs  to another color, in a seamless and
        autonomous manner. The transition is performed in the HSL space. In HSL, hue is a circular
        value (0..360°). There are always two paths to perform the transition: by increasing
        or by decreasing the hue. The module selects the shortest transition.
        If the difference is exactly 180°, the module selects the transition which increases
        the hue.

        @param ledIndex :  index of the first affected LED.
        @param count    :  affected LED count.
        @param hslValue :  new color (0xHHSSLL).
        @param delay    :  transition duration in ms

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("MH" + str(int(ledIndex)) + "," + str(int(count)) + "," + ("%x" % hslValue) + "," + str(int(delay)))

    def addRgbMoveToBlinkSeq(self, seqIndex, rgbValue, delay):
        """
        Adds an RGB transition to a sequence. A sequence is a transition list, which can
        be executed in loop by a group of LEDs.  Sequences are persistent and are saved
        in the device flash memory as soon as the saveBlinkSeq() method is called.

        @param seqIndex :  sequence index.
        @param rgbValue :  target color (0xRRGGBB)
        @param delay    :  transition duration in ms

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("AR" + str(int(seqIndex)) + "," + ("%x" % rgbValue) + "," + str(int(delay)))

    def addHslMoveToBlinkSeq(self, seqIndex, hslValue, delay):
        """
        Adds an HSL transition to a sequence. A sequence is a transition list, which can
        be executed in loop by an group of LEDs.  Sequences are persistent and are saved
        in the device flash memory as soon as the saveBlinkSeq() method is called.

        @param seqIndex : sequence index.
        @param hslValue : target color (0xHHSSLL)
        @param delay    : transition duration in ms

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("AH" + str(int(seqIndex)) + "," + ("%x" % hslValue) + "," + str(int(delay)))

    def addMirrorToBlinkSeq(self, seqIndex):
        """
        Adds a mirror ending to a sequence. When the sequence will reach the end of the last
        transition, its running speed will automatically be reversed so that the sequence plays
        in the reverse direction, like in a mirror. After the first transition of the sequence
        is played at the end of the reverse execution, the sequence starts again in
        the initial direction.

        @param seqIndex : sequence index.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("AC" + str(int(seqIndex)) + ",0,0")

    def addJumpToBlinkSeq(self, seqIndex, linkSeqIndex):
        """
        Adds to a sequence a jump to another sequence. When a pixel will reach this jump,
        it will be automatically relinked to the new sequence, and will run it starting
        from the beginning.

        @param seqIndex : sequence index.
        @param linkSeqIndex : index of the sequence to chain.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("AC" + str(int(seqIndex)) + ",100," + str(int(linkSeqIndex)) + ",1000")

    def addUnlinkToBlinkSeq(self, seqIndex):
        """
        Adds a to a sequence a hard stop code. When a pixel will reach this stop code,
        instead of restarting the sequence in a loop it will automatically be unlinked
        from the sequence.

        @param seqIndex : sequence index.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("AC" + str(int(seqIndex)) + ",100,-1,1000")

    def linkLedToBlinkSeq(self, ledIndex, count, seqIndex, offset):
        """
        Links adjacent LEDs to a specific sequence. These LEDs start to execute
        the sequence as soon as  startBlinkSeq is called. It is possible to add an offset
        in the execution: that way we  can have several groups of LED executing the same
        sequence, with a  temporal offset. A LED cannot be linked to more than one sequence.

        @param ledIndex :  index of the first affected LED.
        @param count    :  affected LED count.
        @param seqIndex :  sequence index.
        @param offset   :  execution offset in ms.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("LS" + str(int(ledIndex)) + "," + str(int(count)) + "," + str(int(seqIndex)) + "," + str(int(offset)))

    def linkLedToBlinkSeqAtPowerOn(self, ledIndex, count, seqIndex, offset):
        """
        Links adjacent LEDs to a specific sequence at device power-on. Don't forget to configure
        the sequence auto start flag as well and call saveLedsConfigAtPowerOn(). It is possible to add an offset
        in the execution: that way we  can have several groups of LEDs executing the same
        sequence, with a  temporal offset. A LED cannot be linked to more than one sequence.

        @param ledIndex :  index of the first affected LED.
        @param count    :  affected LED count.
        @param seqIndex :  sequence index.
        @param offset   :  execution offset in ms.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("LO" + str(int(ledIndex)) + "," + str(int(count)) + "," + str(int(seqIndex)) + "," + str(int(offset)))

    def linkLedToPeriodicBlinkSeq(self, ledIndex, count, seqIndex, periods):
        """
        Links adjacent LEDs to a specific sequence. These LED start to execute
        the sequence as soon as  startBlinkSeq is called. This function automatically
        introduces a shift between LEDs so that the specified number of sequence periods
        appears on the group of LEDs (wave effect).

        @param ledIndex :  index of the first affected LED.
        @param count    :  affected LED count.
        @param seqIndex :  sequence index.
        @param periods  :  number of periods to show on LEDs.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("LP" + str(int(ledIndex)) + "," + str(int(count)) + "," + str(int(seqIndex)) + "," + str(int(periods)))

    def unlinkLedFromBlinkSeq(self, ledIndex, count):
        """
        Unlinks adjacent LEDs from a  sequence.

        @param ledIndex  :  index of the first affected LED.
        @param count     :  affected LED count.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("US" + str(int(ledIndex)) + "," + str(int(count)))

    def startBlinkSeq(self, seqIndex):
        """
        Starts a sequence execution: every LED linked to that sequence starts to
        run it in a loop. Note that a sequence with a zero duration can't be started.

        @param seqIndex :  index of the sequence to start.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("SS" + str(int(seqIndex)))

    def stopBlinkSeq(self, seqIndex):
        """
        Stops a sequence execution. If started again, the execution
        restarts from the beginning.

        @param seqIndex :  index of the sequence to stop.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("XS" + str(int(seqIndex)))

    def resetBlinkSeq(self, seqIndex):
        """
        Stops a sequence execution and resets its contents. LEDs linked to this
        sequence are not automatically updated anymore.

        @param seqIndex :  index of the sequence to reset

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("ZS" + str(int(seqIndex)))

    def set_blinkSeqStateAtPowerOn(self, seqIndex, autostart):
        """
        Configures a sequence to make it start automatically at device
        startup. Note that a sequence with a zero duration can't be started.
        Don't forget to call saveBlinkSeq() to make sure the
        modification is saved in the device flash memory.

        @param seqIndex :  index of the sequence to reset.
        @param autostart : 0 to keep the sequence turned off and 1 to start it automatically.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("AS" + str(int(seqIndex)) + "," + str(int(autostart)))

    def set_blinkSeqSpeed(self, seqIndex, speed):
        """
        Changes the execution speed of a sequence. The natural execution speed is 1000 per
        thousand. If you configure a slower speed, you can play the sequence in slow-motion.
        If you set a negative speed, you can play the sequence in reverse direction.

        @param seqIndex :  index of the sequence to start.
        @param speed :     sequence running speed (-1000...1000).

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("CS" + str(int(seqIndex)) + "," + str(int(speed)))

    def saveLedsConfigAtPowerOn(self):
        """
        Saves the LEDs power-on configuration. This includes the start-up color or
        sequence binding for all LEDs. Warning: if some LEDs are linked to a sequence, the
        method saveBlinkSeq() must also be called to save the sequence definition.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("WL")

    def saveLedsState(self):
        return self.sendCommand("WL")

    def saveBlinkSeq(self, seqIndex):
        """
        Saves the definition of a sequence. Warning: only sequence steps and flags are saved.
        to save the LEDs startup bindings, the method saveLedsConfigAtPowerOn()
        must be called.

        @param seqIndex :  index of the sequence to start.

        @return YAPI.SUCCESS when the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("WS" + str(int(seqIndex)))

    def set_rgbColorBuffer(self, ledIndex, buff):
        """
        Sends a binary buffer to the LED RGB buffer, as is.
        First three bytes are RGB components for LED specified as parameter, the
        next three bytes for the next LED, etc.

        @param ledIndex : index of the first LED which should be updated
        @param buff : the binary buffer to send

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self._upload("rgb:0:" + str(int(ledIndex)), buff)

    def set_rgbColorArray(self, ledIndex, rgbList):
        """
        Sends 24bit RGB colors (provided as a list of integers) to the LED RGB buffer, as is.
        The first number represents the RGB value of the LED specified as parameter, the second
        number represents the RGB value of the next LED, etc.

        @param ledIndex : index of the first LED which should be updated
        @param rgbList : a list of 24bit RGB codes, in the form 0xRRGGBB

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # listlen
        # buff
        # idx
        # rgb
        # res
        listlen = len(rgbList)
        buff = bytearray(3*listlen)
        idx = 0
        while idx < listlen:
            rgb = rgbList[idx]
            buff[3*idx] = ((((rgb) >> (16))) & (255))
            buff[3*idx+1] = ((((rgb) >> (8))) & (255))
            buff[3*idx+2] = ((rgb) & (255))
            idx = idx + 1

        res = self._upload("rgb:0:" + str(int(ledIndex)), buff)
        return res

    def rgbArrayOfs_move(self, ledIndex, rgbList, delay):
        """
        Sets up a smooth RGB color transition to the specified pixel-by-pixel list of RGB
        color codes. The first color code represents the target RGB value of the first LED,
        the next color code represents the target value of the next LED, etc.

        @param ledIndex : index of the first LED which should be updated
        @param rgbList : a list of target 24bit RGB codes, in the form 0xRRGGBB
        @param delay   : transition duration in ms

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # listlen
        # buff
        # idx
        # rgb
        # res
        listlen = len(rgbList)
        buff = bytearray(3*listlen)
        idx = 0
        while idx < listlen:
            rgb = rgbList[idx]
            buff[3*idx] = ((((rgb) >> (16))) & (255))
            buff[3*idx+1] = ((((rgb) >> (8))) & (255))
            buff[3*idx+2] = ((rgb) & (255))
            idx = idx + 1

        res = self._upload("rgb:" + str(int(delay)) + ":" + str(int(ledIndex)), buff)
        return res

    def rgbArray_move(self, rgbList, delay):
        """
        Sets up a smooth RGB color transition to the specified pixel-by-pixel list of RGB
        color codes. The first color code represents the target RGB value of the first LED,
        the next color code represents the target value of the next LED, etc.

        @param rgbList : a list of target 24bit RGB codes, in the form 0xRRGGBB
        @param delay   : transition duration in ms

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # res

        res = self.rgbArrayOfs_move(0,rgbList,delay)
        return res

    def set_hslColorBuffer(self, ledIndex, buff):
        """
        Sends a binary buffer to the LED HSL buffer, as is.
        First three bytes are HSL components for the LED specified as parameter, the
        next three bytes for the second LED, etc.

        @param ledIndex : index of the first LED which should be updated
        @param buff : the binary buffer to send

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self._upload("hsl:0:" + str(int(ledIndex)), buff)

    def set_hslColorArray(self, ledIndex, hslList):
        """
        Sends 24bit HSL colors (provided as a list of integers) to the LED HSL buffer, as is.
        The first number represents the HSL value of the LED specified as parameter, the second number represents
        the HSL value of the second LED, etc.

        @param ledIndex : index of the first LED which should be updated
        @param hslList : a list of 24bit HSL codes, in the form 0xHHSSLL

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # listlen
        # buff
        # idx
        # hsl
        # res
        listlen = len(hslList)
        buff = bytearray(3*listlen)
        idx = 0
        while idx < listlen:
            hsl = hslList[idx]
            buff[3*idx] = ((((hsl) >> (16))) & (255))
            buff[3*idx+1] = ((((hsl) >> (8))) & (255))
            buff[3*idx+2] = ((hsl) & (255))
            idx = idx + 1

        res = self._upload("hsl:0:" + str(int(ledIndex)), buff)
        return res

    def hslArray_move(self, hslList, delay):
        """
        Sets up a smooth HSL color transition to the specified pixel-by-pixel list of HSL
        color codes. The first color code represents the target HSL value of the first LED,
        the second color code represents the target value of the second LED, etc.

        @param hslList : a list of target 24bit HSL codes, in the form 0xHHSSLL
        @param delay   : transition duration in ms

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # res

        res = self.hslArrayOfs_move(0,hslList, delay)
        return res

    def hslArrayOfs_move(self, ledIndex, hslList, delay):
        """
        Sets up a smooth HSL color transition to the specified pixel-by-pixel list of HSL
        color codes. The first color code represents the target HSL value of the first LED,
        the second color code represents the target value of the second LED, etc.

        @param ledIndex : index of the first LED which should be updated
        @param hslList : a list of target 24bit HSL codes, in the form 0xHHSSLL
        @param delay   : transition duration in ms

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # listlen
        # buff
        # idx
        # hsl
        # res
        listlen = len(hslList)
        buff = bytearray(3*listlen)
        idx = 0
        while idx < listlen:
            hsl = hslList[idx]
            buff[3*idx] = ((((hsl) >> (16))) & (255))
            buff[3*idx+1] = ((((hsl) >> (8))) & (255))
            buff[3*idx+2] = ((hsl) & (255))
            idx = idx + 1

        res = self._upload("hsl:" + str(int(delay)) + ":" + str(int(ledIndex)), buff)
        return res

    def get_rgbColorBuffer(self, ledIndex, count):
        """
        Returns a binary buffer with content from the LED RGB buffer, as is.
        First three bytes are RGB components for the first LED in the interval,
        the next three bytes for the second LED in the interval, etc.

        @param ledIndex : index of the first LED which should be returned
        @param count    : number of LEDs which should be returned

        @return a binary buffer with RGB components of selected LEDs.

        On failure, throws an exception or returns an empty binary buffer.
        """
        return self._download("rgb.bin?typ=0&pos=" + str(int(3*ledIndex)) + "&len=" + str(int(3*count)))

    def get_rgbColorArray(self, ledIndex, count):
        """
        Returns a list on 24bit RGB color values with the current colors displayed on
        the RGB LEDs. The first number represents the RGB value of the first LED,
        the second number represents the RGB value of the second LED, etc.

        @param ledIndex : index of the first LED which should be returned
        @param count    : number of LEDs which should be returned

        @return a list of 24bit color codes with RGB components of selected LEDs, as 0xRRGGBB.

        On failure, throws an exception or returns an empty array.
        """
        # buff
        res = []
        # idx
        # r
        # g
        # b

        buff = self._download("rgb.bin?typ=0&pos=" + str(int(3*ledIndex)) + "&len=" + str(int(3*count)))
        del res[:]

        idx = 0
        while idx < count:
            r = YGetByte(buff, 3*idx)
            g = YGetByte(buff, 3*idx+1)
            b = YGetByte(buff, 3*idx+2)
            res.append(r*65536+g*256+b)
            idx = idx + 1

        return res

    def get_rgbColorArrayAtPowerOn(self, ledIndex, count):
        """
        Returns a list on 24bit RGB color values with the RGB LEDs startup colors.
        The first number represents the startup RGB value of the first LED,
        the second number represents the RGB value of the second LED, etc.

        @param ledIndex : index of the first LED  which should be returned
        @param count    : number of LEDs which should be returned

        @return a list of 24bit color codes with RGB components of selected LEDs, as 0xRRGGBB.

        On failure, throws an exception or returns an empty array.
        """
        # buff
        res = []
        # idx
        # r
        # g
        # b

        buff = self._download("rgb.bin?typ=4&pos=" + str(int(3*ledIndex)) + "&len=" + str(int(3*count)))
        del res[:]

        idx = 0
        while idx < count:
            r = YGetByte(buff, 3*idx)
            g = YGetByte(buff, 3*idx+1)
            b = YGetByte(buff, 3*idx+2)
            res.append(r*65536+g*256+b)
            idx = idx + 1

        return res

    def get_linkedSeqArray(self, ledIndex, count):
        """
        Returns a list on sequence index for each RGB LED. The first number represents the
        sequence index for the the first LED, the second number represents the sequence
        index for the second LED, etc.

        @param ledIndex : index of the first LED which should be returned
        @param count    : number of LEDs which should be returned

        @return a list of integers with sequence index

        On failure, throws an exception or returns an empty array.
        """
        # buff
        res = []
        # idx
        # seq

        buff = self._download("rgb.bin?typ=1&pos=" + str(int(ledIndex)) + "&len=" + str(int(count)))
        del res[:]

        idx = 0
        while idx < count:
            seq = YGetByte(buff, idx)
            res.append(seq)
            idx = idx + 1

        return res

    def get_blinkSeqSignatures(self, seqIndex, count):
        """
        Returns a list on 32 bit signatures for specified blinking sequences.
        Since blinking sequences cannot be read from the device, this can be used
        to detect if a specific blinking sequence is already programmed.

        @param seqIndex : index of the first blinking sequence which should be returned
        @param count    : number of blinking sequences which should be returned

        @return a list of 32 bit integer signatures

        On failure, throws an exception or returns an empty array.
        """
        # buff
        res = []
        # idx
        # hh
        # hl
        # lh
        # ll

        buff = self._download("rgb.bin?typ=2&pos=" + str(int(4*seqIndex)) + "&len=" + str(int(4*count)))
        del res[:]

        idx = 0
        while idx < count:
            hh = YGetByte(buff, 4*idx)
            hl = YGetByte(buff, 4*idx+1)
            lh = YGetByte(buff, 4*idx+2)
            ll = YGetByte(buff, 4*idx+3)
            res.append(((hh) << (24))+((hl) << (16))+((lh) << (8))+ll)
            idx = idx + 1

        return res

    def get_blinkSeqStateSpeed(self, seqIndex, count):
        """
        Returns a list of integers with the current speed for specified blinking sequences.

        @param seqIndex : index of the first sequence speed which should be returned
        @param count    : number of sequence speeds which should be returned

        @return a list of integers, 0 for sequences turned off and 1 for sequences running

        On failure, throws an exception or returns an empty array.
        """
        # buff
        res = []
        # idx
        # lh
        # ll

        buff = self._download("rgb.bin?typ=6&pos=" + str(int(seqIndex)) + "&len=" + str(int(count)))
        del res[:]

        idx = 0
        while idx < count:
            lh = YGetByte(buff, 2*idx)
            ll = YGetByte(buff, 2*idx+1)
            res.append(((lh) << (8))+ll)
            idx = idx + 1

        return res

    def get_blinkSeqStateAtPowerOn(self, seqIndex, count):
        """
        Returns a list of integers with the "auto-start at power on" flag state for specified blinking sequences.

        @param seqIndex : index of the first blinking sequence which should be returned
        @param count    : number of blinking sequences which should be returned

        @return a list of integers, 0 for sequences turned off and 1 for sequences running

        On failure, throws an exception or returns an empty array.
        """
        # buff
        res = []
        # idx
        # started

        buff = self._download("rgb.bin?typ=5&pos=" + str(int(seqIndex)) + "&len=" + str(int(count)))
        del res[:]

        idx = 0
        while idx < count:
            started = YGetByte(buff, idx)
            res.append(started)
            idx = idx + 1

        return res

    def get_blinkSeqState(self, seqIndex, count):
        """
        Returns a list of integers with the started state for specified blinking sequences.

        @param seqIndex : index of the first blinking sequence which should be returned
        @param count    : number of blinking sequences which should be returned

        @return a list of integers, 0 for sequences turned off and 1 for sequences running

        On failure, throws an exception or returns an empty array.
        """
        # buff
        res = []
        # idx
        # started

        buff = self._download("rgb.bin?typ=3&pos=" + str(int(seqIndex)) + "&len=" + str(int(count)))
        del res[:]

        idx = 0
        while idx < count:
            started = YGetByte(buff, idx)
            res.append(started)
            idx = idx + 1

        return res

    def hsl2rgbInt(self, temp1, temp2, temp3):
        if temp3 >= 170:
            return int(((temp1 + 127)) / (255))
        if temp3 > 42:
            if temp3 <= 127:
                return int(((temp2 + 127)) / (255))
            temp3 = 170 - temp3
        return int(((temp1*255 + (temp2-temp1) * (6 * temp3) + 32512)) / (65025))

    def hsl2rgb(self, hslValue):
        # R
        # G
        # B
        # H
        # S
        # L
        # temp1
        # temp2
        # temp3
        # res
        L = ((hslValue) & (0xff))
        S = ((((hslValue) >> (8))) & (0xff))
        H = ((((hslValue) >> (16))) & (0xff))
        if S==0:
            res = ((L) << (16))+((L) << (8))+L
            return res
        if L<=127:
            temp2 = L * (255 + S)
        else:
            temp2 = (L+S) * 255 - L*S
        temp1 = 510 * L - temp2
        # // R
        temp3 = (H + 85)
        if temp3 > 255:
            temp3 = temp3-255
        R = self.hsl2rgbInt(temp1, temp2, temp3)
        # // G
        temp3 = H
        if temp3 > 255:
            temp3 = temp3-255
        G = self.hsl2rgbInt(temp1, temp2, temp3)
        # // B
        if H >= 85:
            temp3 = H - 85
        else:
            temp3 = H + 170
        B = self.hsl2rgbInt(temp1, temp2, temp3)
        # // just in case
        if R>255:
            R=255
        if G>255:
            G=255
        if B>255:
            B=255
        res = ((R) << (16))+((G) << (8))+B
        return res

    def nextColorLedCluster(self):
        """
        Continues the enumeration of RGB LED clusters started using yFirstColorLedCluster().
        Caution: You can't make any assumption about the returned RGB LED clusters order.
        If you want to find a specific a RGB LED cluster, use ColorLedCluster.findColorLedCluster()
        and a hardwareID or a logical name.

        @return a pointer to a YColorLedCluster object, corresponding to
                a RGB LED cluster currently online, or a None pointer
                if there are no more RGB LED clusters to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YColorLedCluster.FindColorLedCluster(hwidRef.value)

#--- (end of YColorLedCluster implementation)

#--- (YColorLedCluster functions)

    @staticmethod
    def FirstColorLedCluster():
        """
        Starts the enumeration of RGB LED clusters currently accessible.
        Use the method YColorLedCluster.nextColorLedCluster() to iterate on
        next RGB LED clusters.

        @return a pointer to a YColorLedCluster object, corresponding to
                the first RGB LED cluster currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("ColorLedCluster", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YColorLedCluster.FindColorLedCluster(serialRef.value + "." + funcIdRef.value)

#--- (end of YColorLedCluster functions)
