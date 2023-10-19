# -*- coding: utf-8 -*-
# ********************************************************************
#
#  $Id: yocto_buzzer.py 38899 2019-12-20 17:21:03Z mvuilleu $
#
#  Implements yFindBuzzer(), the high-level API for Buzzer functions
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
import math
from yoctopuce.yocto_api import *


#--- (YBuzzer class start)
#noinspection PyProtectedMember
class YBuzzer(YFunction):
    """
    The YBuzzer class allows you to drive a buzzer. You can
    choose the frequency and the volume at which the buzzer must sound.
    You can also pre-program a play sequence.

    """
    #--- (end of YBuzzer class start)
    #--- (YBuzzer return codes)
    #--- (end of YBuzzer return codes)
    #--- (YBuzzer dlldef)
    #--- (end of YBuzzer dlldef)
    #--- (YBuzzer yapiwrapper)
    #--- (end of YBuzzer yapiwrapper)
    #--- (YBuzzer definitions)
    FREQUENCY_INVALID = YAPI.INVALID_DOUBLE
    VOLUME_INVALID = YAPI.INVALID_UINT
    PLAYSEQSIZE_INVALID = YAPI.INVALID_UINT
    PLAYSEQMAXSIZE_INVALID = YAPI.INVALID_UINT
    PLAYSEQSIGNATURE_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    #--- (end of YBuzzer definitions)

    def __init__(self, func):
        super(YBuzzer, self).__init__(func)
        self._className = 'Buzzer'
        #--- (YBuzzer attributes)
        self._callback = None
        self._frequency = YBuzzer.FREQUENCY_INVALID
        self._volume = YBuzzer.VOLUME_INVALID
        self._playSeqSize = YBuzzer.PLAYSEQSIZE_INVALID
        self._playSeqMaxSize = YBuzzer.PLAYSEQMAXSIZE_INVALID
        self._playSeqSignature = YBuzzer.PLAYSEQSIGNATURE_INVALID
        self._command = YBuzzer.COMMAND_INVALID
        #--- (end of YBuzzer attributes)

    #--- (YBuzzer implementation)
    def _parseAttr(self, json_val):
        if json_val.has("frequency"):
            self._frequency = round(json_val.getDouble("frequency") * 1000.0 / 65536.0) / 1000.0
        if json_val.has("volume"):
            self._volume = json_val.getInt("volume")
        if json_val.has("playSeqSize"):
            self._playSeqSize = json_val.getInt("playSeqSize")
        if json_val.has("playSeqMaxSize"):
            self._playSeqMaxSize = json_val.getInt("playSeqMaxSize")
        if json_val.has("playSeqSignature"):
            self._playSeqSignature = json_val.getInt("playSeqSignature")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YBuzzer, self)._parseAttr(json_val)

    def set_frequency(self, newval):
        """
        Changes the frequency of the signal sent to the buzzer. A zero value stops the buzzer.

        @param newval : a floating point number corresponding to the frequency of the signal sent to the buzzer

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(int(round(newval * 65536.0, 1)))
        return self._setAttr("frequency", rest_val)

    def get_frequency(self):
        """
        Returns the  frequency of the signal sent to the buzzer/speaker.

        @return a floating point number corresponding to the  frequency of the signal sent to the buzzer/speaker

        On failure, throws an exception or returns YBuzzer.FREQUENCY_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBuzzer.FREQUENCY_INVALID
        res = self._frequency
        return res

    def get_volume(self):
        """
        Returns the volume of the signal sent to the buzzer/speaker.

        @return an integer corresponding to the volume of the signal sent to the buzzer/speaker

        On failure, throws an exception or returns YBuzzer.VOLUME_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBuzzer.VOLUME_INVALID
        res = self._volume
        return res

    def set_volume(self, newval):
        """
        Changes the volume of the signal sent to the buzzer/speaker. Remember to call the
        saveToFlash() method of the module if the modification must be kept.

        @param newval : an integer corresponding to the volume of the signal sent to the buzzer/speaker

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("volume", rest_val)

    def get_playSeqSize(self):
        """
        Returns the current length of the playing sequence.

        @return an integer corresponding to the current length of the playing sequence

        On failure, throws an exception or returns YBuzzer.PLAYSEQSIZE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBuzzer.PLAYSEQSIZE_INVALID
        res = self._playSeqSize
        return res

    def get_playSeqMaxSize(self):
        """
        Returns the maximum length of the playing sequence.

        @return an integer corresponding to the maximum length of the playing sequence

        On failure, throws an exception or returns YBuzzer.PLAYSEQMAXSIZE_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBuzzer.PLAYSEQMAXSIZE_INVALID
        res = self._playSeqMaxSize
        return res

    def get_playSeqSignature(self):
        """
        Returns the playing sequence signature. As playing
        sequences cannot be read from the device, this can be used
        to detect if a specific playing sequence is already
        programmed.

        @return an integer corresponding to the playing sequence signature

        On failure, throws an exception or returns YBuzzer.PLAYSEQSIGNATURE_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBuzzer.PLAYSEQSIGNATURE_INVALID
        res = self._playSeqSignature
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YBuzzer.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindBuzzer(func):
        """
        Retrieves a buzzer for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the buzzer is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YBuzzer.isOnline() to test if the buzzer is
        indeed online at a given time. In case of ambiguity when looking for
        a buzzer by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the buzzer, for instance
                YBUZZER2.buzzer.

        @return a YBuzzer object allowing you to drive the buzzer.
        """
        # obj
        obj = YFunction._FindFromCache("Buzzer", func)
        if obj is None:
            obj = YBuzzer(func)
            YFunction._AddToCache("Buzzer", func, obj)
        return obj

    def sendCommand(self, command):
        return self.set_command(command)

    def addFreqMoveToPlaySeq(self, freq, msDelay):
        """
        Adds a new frequency transition to the playing sequence.

        @param freq    : desired frequency when the transition is completed, in Hz
        @param msDelay : duration of the frequency transition, in milliseconds.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("A" + str(int(freq)) + "," + str(int(msDelay)))

    def addPulseToPlaySeq(self, freq, msDuration):
        """
        Adds a pulse to the playing sequence.

        @param freq : pulse frequency, in Hz
        @param msDuration : pulse duration, in milliseconds.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("B" + str(int(freq)) + "," + str(int(msDuration)))

    def addVolMoveToPlaySeq(self, volume, msDuration):
        """
        Adds a new volume transition to the playing sequence. Frequency stays untouched:
        if frequency is at zero, the transition has no effect.

        @param volume    : desired volume when the transition is completed, as a percentage.
        @param msDuration : duration of the volume transition, in milliseconds.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("C" + str(int(volume)) + "," + str(int(msDuration)))

    def addNotesToPlaySeq(self, notes):
        """
        Adds notes to the playing sequence. Notes are provided as text words, separated by
        spaces. The pitch is specified using the usual letter from A to G. The duration is
        specified as the divisor of a whole note: 4 for a fourth, 8 for an eight note, etc.
        Some modifiers are supported: # and b to alter a note pitch,
        ' and , to move to the upper/lower octave, . to enlarge
        the note duration.

        @param notes : notes to be played, as a text string.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        # tempo
        # prevPitch
        # prevDuration
        # prevFreq
        # note
        # num
        # typ
        # ascNotes
        # notesLen
        # i
        # ch
        # dNote
        # pitch
        # freq
        # ms
        # ms16
        # rest
        tempo = 100
        prevPitch = 3
        prevDuration = 4
        prevFreq = 110
        note = -99
        num = 0
        typ = 3
        ascNotes = YString2Byte(notes)
        notesLen = len(ascNotes)
        i = 0
        while i < notesLen:
            ch = YGetByte(ascNotes, i)
            # // A (note))
            if ch == 65:
                note = 0
            # // B (note)
            if ch == 66:
                note = 2
            # // C (note)
            if ch == 67:
                note = 3
            # // D (note)
            if ch == 68:
                note = 5
            # // E (note)
            if ch == 69:
                note = 7
            # // F (note)
            if ch == 70:
                note = 8
            # // G (note)
            if ch == 71:
                note = 10
            # // '#' (sharp modifier)
            if ch == 35:
                note = note + 1
            # // 'b' (flat modifier)
            if ch == 98:
                note = note - 1
            # // ' (octave up)
            if ch == 39:
                prevPitch = prevPitch + 12
            # // , (octave down)
            if ch == 44:
                prevPitch = prevPitch - 12
            # // R (rest)
            if ch == 82:
                typ = 0
            # // ! (staccato modifier)
            if ch == 33:
                typ = 1
            # // ^ (short modifier)
            if ch == 94:
                typ = 2
            # // _ (legato modifier)
            if ch == 95:
                typ = 4
            # // - (glissando modifier)
            if ch == 45:
                typ = 5
            # // % (tempo change)
            if (ch == 37) and (num > 0):
                tempo = num
                num = 0
            if (ch >= 48) and (ch <= 57):
                # // 0-9 (number)
                num = (num * 10) + (ch - 48)
            if ch == 46:
                # // . (duration modifier)
                num = int((num * 2) / (3))
            if ((ch == 32) or (i+1 == notesLen)) and ((note > -99) or (typ != 3)):
                if num == 0:
                    num = prevDuration
                else:
                    prevDuration = num
                ms = int(round(320000.0 / (tempo * num)))
                if typ == 0:
                    self.addPulseToPlaySeq(0, ms)
                else:
                    dNote = note - (((prevPitch) % (12)))
                    if dNote > 6:
                        dNote = dNote - 12
                    if dNote <= -6:
                        dNote = dNote + 12
                    pitch = prevPitch + dNote
                    freq = int(round(440 * math.exp(pitch * 0.05776226504666)))
                    ms16 = ((ms) >> (4))
                    rest = 0
                    if typ == 3:
                        rest = 2 * ms16
                    if typ == 2:
                        rest = 8 * ms16
                    if typ == 1:
                        rest = 12 * ms16
                    if typ == 5:
                        self.addPulseToPlaySeq(prevFreq, ms16)
                        self.addFreqMoveToPlaySeq(freq, 8 * ms16)
                        self.addPulseToPlaySeq(freq, ms - 9 * ms16)
                    else:
                        self.addPulseToPlaySeq(freq, ms - rest)
                        if rest > 0:
                            self.addPulseToPlaySeq(0, rest)
                    prevFreq = freq
                    prevPitch = pitch
                note = -99
                num = 0
                typ = 3
            i = i + 1
        return YAPI.SUCCESS

    def startPlaySeq(self):
        """
        Starts the preprogrammed playing sequence. The sequence
        runs in loop until it is stopped by stopPlaySeq or an explicit
        change. To play the sequence only once, use oncePlaySeq().

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("S")

    def stopPlaySeq(self):
        """
        Stops the preprogrammed playing sequence and sets the frequency to zero.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("X")

    def resetPlaySeq(self):
        """
        Resets the preprogrammed playing sequence and sets the frequency to zero.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("Z")

    def oncePlaySeq(self):
        """
        Starts the preprogrammed playing sequence and run it once only.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("s")

    def savePlaySeq(self):
        """
        Saves the preprogrammed playing sequence to flash memory.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("W")

    def reloadPlaySeq(self):
        """
        Reloads the preprogrammed playing sequence from the flash memory.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        return self.sendCommand("R")

    def pulse(self, frequency, duration):
        """
        Activates the buzzer for a short duration.

        @param frequency : pulse frequency, in hertz
        @param duration : pulse duration in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("P" + str(int(frequency)) + "," + str(int(duration)))

    def freqMove(self, frequency, duration):
        """
        Makes the buzzer frequency change over a period of time.

        @param frequency : frequency to reach, in hertz. A frequency under 25Hz stops the buzzer.
        @param duration :  pulse duration in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("F" + str(int(frequency)) + "," + str(int(duration)))

    def volumeMove(self, volume, duration):
        """
        Makes the buzzer volume change over a period of time, frequency  stays untouched.

        @param volume : volume to reach in %
        @param duration : change duration in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.set_command("V" + str(int(volume)) + "," + str(int(duration)))

    def playNotes(self, notes):
        """
        Immediately play a note sequence. Notes are provided as text words, separated by
        spaces. The pitch is specified using the usual letter from A to G. The duration is
        specified as the divisor of a whole note: 4 for a fourth, 8 for an eight note, etc.
        Some modifiers are supported: # and b to alter a note pitch,
        ' and , to move to the upper/lower octave, . to enlarge
        the note duration.

        @param notes : notes to be played, as a text string.

        @return YAPI.SUCCESS if the call succeeds.
                On failure, throws an exception or returns a negative error code.
        """
        self.resetPlaySeq()
        self.addNotesToPlaySeq(notes)
        return self.oncePlaySeq()

    def nextBuzzer(self):
        """
        Continues the enumeration of buzzers started using yFirstBuzzer().
        Caution: You can't make any assumption about the returned buzzers order.
        If you want to find a specific a buzzer, use Buzzer.findBuzzer()
        and a hardwareID or a logical name.

        @return a pointer to a YBuzzer object, corresponding to
                a buzzer currently online, or a None pointer
                if there are no more buzzers to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YBuzzer.FindBuzzer(hwidRef.value)

#--- (end of YBuzzer implementation)

#--- (YBuzzer functions)

    @staticmethod
    def FirstBuzzer():
        """
        Starts the enumeration of buzzers currently accessible.
        Use the method YBuzzer.nextBuzzer() to iterate on
        next buzzers.

        @return a pointer to a YBuzzer object, corresponding to
                the first buzzer currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Buzzer", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YBuzzer.FindBuzzer(serialRef.value + "." + funcIdRef.value)

#--- (end of YBuzzer functions)
