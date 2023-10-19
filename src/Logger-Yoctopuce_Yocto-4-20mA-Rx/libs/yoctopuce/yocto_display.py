# -*- coding: utf-8 -*-
#*********************************************************************
#*
#* $Id: yocto_display.py 38899 2019-12-20 17:21:03Z mvuilleu $
#*
#* Implements yFindDisplay(), the high-level API for Display functions
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

__docformat__ = 'restructuredtext en'
from yoctopuce.yocto_api import *


#--- (generated code: YDisplayLayer class start)
#noinspection PyProtectedMember
class YDisplayLayer(object):
    """
    Each DisplayLayer represents an image layer containing objects
    to display (bitmaps, text, etc.). The content is displayed only when
    the layer is active on the screen (and not masked by other
    overlapping layers).

    """
    #--- (end of generated code: YDisplayLayer class start)

    def __init__(self, parent, layerId):
        self._display = parent
        self._id = int(layerId)
        self._cmdbuff = ""
        self._hidden = False
        #--- (generated code: YDisplayLayer attributes)
        #--- (end of generated code: YDisplayLayer attributes)

    #--- (generated code: YDisplayLayer definitions)
    class ALIGN:
        def __init__(self):
            pass
        TOP_LEFT, CENTER_LEFT, BASELINE_LEFT, BOTTOM_LEFT, TOP_CENTER, CENTER, BASELINE_CENTER, BOTTOM_CENTER, \
            TOP_DECIMAL, CENTER_DECIMAL, BASELINE_DECIMAL, BOTTOM_DECIMAL, TOP_RIGHT, CENTER_RIGHT, BASELINE_RIGHT, \
            BOTTOM_RIGHT = range(16)
    #--- (end of generated code: YDisplayLayer definitions)

    def flush_now(self):
        res = YAPI.SUCCESS
        if self._cmdbuff != "":
            res = self._display.sendCommand(self._cmdbuff)
            self._cmdbuff = ""
        return res

    def command_push(self, cmd):
        res = YAPI.SUCCESS
        if len(self._cmdbuff) + len(cmd) >= 100:
            res = self.flush_now()
        if self._cmdbuff == "":
            self._cmdbuff = str(self._id)
        self._cmdbuff = self._cmdbuff + cmd
        return res

    def command_flush(self, cmd):
        res = self.command_push(cmd)
        if not self._hidden:
            res = self.flush_now()
        return res

    #--- (generated code: YDisplayLayer implementation)
    def reset(self):
        """
        Reverts the layer to its initial state (fully transparent, default settings).
        Reinitializes the drawing pointer to the upper left position,
        and selects the most visible pen color. If you only want to erase the layer
        content, use the method clear() instead.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self._hidden = False
        return self.command_flush("X")

    def clear(self):
        """
        Erases the whole content of the layer (makes it fully transparent).
        This method does not change any other attribute of the layer.
        To reinitialize the layer attributes to defaults settings, use the method
        reset() instead.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("x")

    def selectColorPen(self, color):
        """
        Selects the pen color for all subsequent drawing functions,
        including text drawing. The pen color is provided as an RGB value.
        For grayscale or monochrome displays, the value is
        automatically converted to the proper range.

        @param color : the desired pen color, as a 24-bit RGB value

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_push("c" + ("%06x" % color))

    def selectGrayPen(self, graylevel):
        """
        Selects the pen gray level for all subsequent drawing functions,
        including text drawing. The gray level is provided as a number between
        0 (black) and 255 (white, or whichever the lightest color is).
        For monochrome displays (without gray levels), any value
        lower than 128 is rendered as black, and any value equal
        or above to 128 is non-black.

        @param graylevel : the desired gray level, from 0 to 255

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_push("g" + str(int(graylevel)))

    def selectEraser(self):
        """
        Selects an eraser instead of a pen for all subsequent drawing functions,
        except for bitmap copy functions. Any point drawn using the eraser
        becomes transparent (as when the layer is empty), showing the other
        layers beneath it.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_push("e")

    def setAntialiasingMode(self, mode):
        """
        Enables or disables anti-aliasing for drawing oblique lines and circles.
        Anti-aliasing provides a smoother aspect when looked from far enough,
        but it can add fuzziness when the display is looked from very close.
        At the end of the day, it is your personal choice.
        Anti-aliasing is enabled by default on grayscale and color displays,
        but you can disable it if you prefer. This setting has no effect
        on monochrome displays.

        @param mode : true to enable anti-aliasing, false to
                disable it.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_push("a" + ("1" if mode else "0"))

    def drawPixel(self, x, y):
        """
        Draws a single pixel at the specified position.

        @param x : the distance from left of layer, in pixels
        @param y : the distance from top of layer, in pixels

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("P" + str(int(x)) + "," + str(int(y)))

    def drawRect(self, x1, y1, x2, y2):
        """
        Draws an empty rectangle at a specified position.

        @param x1 : the distance from left of layer to the left border of the rectangle, in pixels
        @param y1 : the distance from top of layer to the top border of the rectangle, in pixels
        @param x2 : the distance from left of layer to the right border of the rectangle, in pixels
        @param y2 : the distance from top of layer to the bottom border of the rectangle, in pixels

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("R" + str(int(x1)) + "," + str(int(y1)) + "," + str(int(x2)) + "," + str(int(y2)))

    def drawBar(self, x1, y1, x2, y2):
        """
        Draws a filled rectangular bar at a specified position.

        @param x1 : the distance from left of layer to the left border of the rectangle, in pixels
        @param y1 : the distance from top of layer to the top border of the rectangle, in pixels
        @param x2 : the distance from left of layer to the right border of the rectangle, in pixels
        @param y2 : the distance from top of layer to the bottom border of the rectangle, in pixels

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("B" + str(int(x1)) + "," + str(int(y1)) + "," + str(int(x2)) + "," + str(int(y2)))

    def drawCircle(self, x, y, r):
        """
        Draws an empty circle at a specified position.

        @param x : the distance from left of layer to the center of the circle, in pixels
        @param y : the distance from top of layer to the center of the circle, in pixels
        @param r : the radius of the circle, in pixels

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("C" + str(int(x)) + "," + str(int(y)) + "," + str(int(r)))

    def drawDisc(self, x, y, r):
        """
        Draws a filled disc at a given position.

        @param x : the distance from left of layer to the center of the disc, in pixels
        @param y : the distance from top of layer to the center of the disc, in pixels
        @param r : the radius of the disc, in pixels

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("D" + str(int(x)) + "," + str(int(y)) + "," + str(int(r)))

    def selectFont(self, fontname):
        """
        Selects a font to use for the next text drawing functions, by providing the name of the
        font file. You can use a built-in font as well as a font file that you have previously
        uploaded to the device built-in memory. If you experience problems selecting a font
        file, check the device logs for any error message such as missing font file or bad font
        file format.

        @param fontname : the font file name, embedded fonts are 8x8.yfm, Small.yfm, Medium.yfm, Large.yfm
        (not available on Yocto-MiniDisplay).

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_push("&" + fontname + "" + str(chr(27)))

    def drawText(self, x, y, anchor, text):
        """
        Draws a text string at the specified position. The point of the text that is aligned
        to the specified pixel position is called the anchor point, and can be chosen among
        several options. Text is rendered from left to right, without implicit wrapping.

        @param x : the distance from left of layer to the text anchor point, in pixels
        @param y : the distance from top of layer to the text anchor point, in pixels
        @param anchor : the text anchor point, chosen among the YDisplayLayer.ALIGN enumeration:
                YDisplayLayer.ALIGN.TOP_LEFT,    YDisplayLayer.ALIGN.CENTER_LEFT,   
                YDisplayLayer.ALIGN.BASELINE_LEFT,    YDisplayLayer.ALIGN.BOTTOM_LEFT,
                YDisplayLayer.ALIGN.TOP_CENTER,  YDisplayLayer.ALIGN.CENTER,        
                YDisplayLayer.ALIGN.BASELINE_CENTER,  YDisplayLayer.ALIGN.BOTTOM_CENTER,
                YDisplayLayer.ALIGN.TOP_DECIMAL, YDisplayLayer.ALIGN.CENTER_DECIMAL,
                YDisplayLayer.ALIGN.BASELINE_DECIMAL, YDisplayLayer.ALIGN.BOTTOM_DECIMAL,
                YDisplayLayer.ALIGN.TOP_RIGHT,   YDisplayLayer.ALIGN.CENTER_RIGHT,  
                YDisplayLayer.ALIGN.BASELINE_RIGHT,   YDisplayLayer.ALIGN.BOTTOM_RIGHT.
        @param text : the text string to draw

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("T" + str(int(x)) + "," + str(int(y)) + "," + str(anchor) + "," + text + "" + str(chr(27)))

    def drawImage(self, x, y, imagename):
        """
        Draws a GIF image at the specified position. The GIF image must have been previously
        uploaded to the device built-in memory. If you experience problems using an image
        file, check the device logs for any error message such as missing image file or bad
        image file format.

        @param x : the distance from left of layer to the left of the image, in pixels
        @param y : the distance from top of layer to the top of the image, in pixels
        @param imagename : the GIF file name

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("*" + str(int(x)) + "," + str(int(y)) + "," + imagename + "" + str(chr(27)))

    def drawBitmap(self, x, y, w, bitmap, bgcol):
        """
        Draws a bitmap at the specified position. The bitmap is provided as a binary object,
        where each pixel maps to a bit, from left to right and from top to bottom.
        The most significant bit of each byte maps to the leftmost pixel, and the least
        significant bit maps to the rightmost pixel. Bits set to 1 are drawn using the
        layer selected pen color. Bits set to 0 are drawn using the specified background
        gray level, unless -1 is specified, in which case they are not drawn at all
        (as if transparent).

        @param x : the distance from left of layer to the left of the bitmap, in pixels
        @param y : the distance from top of layer to the top of the bitmap, in pixels
        @param w : the width of the bitmap, in pixels
        @param bitmap : a binary object
        @param bgcol : the background gray level to use for zero bits (0 = black,
                255 = white), or -1 to leave the pixels unchanged

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        # destname
        destname = "layer" + str(int(self._id)) + ":" + str(int(w)) + "," + str(int(bgcol)) + "@" + str(int(x)) + "," + str(int(y))
        return self._display.upload(destname,bitmap)

    def moveTo(self, x, y):
        """
        Moves the drawing pointer of this layer to the specified position.

        @param x : the distance from left of layer, in pixels
        @param y : the distance from top of layer, in pixels

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_push("@" + str(int(x)) + "," + str(int(y)))

    def lineTo(self, x, y):
        """
        Draws a line from current drawing pointer position to the specified position.
        The specified destination pixel is included in the line. The pointer position
        is then moved to the end point of the line.

        @param x : the distance from left of layer to the end point of the line, in pixels
        @param y : the distance from top of layer to the end point of the line, in pixels

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("-" + str(int(x)) + "," + str(int(y)))

    def consoleOut(self, text):
        """
        Outputs a message in the console area, and advances the console pointer accordingly.
        The console pointer position is automatically moved to the beginning
        of the next line when a newline character is met, or when the right margin
        is hit. When the new text to display extends below the lower margin, the
        console area is automatically scrolled up.

        @param text : the message to display

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("!" + text + "" + str(chr(27)))

    def setConsoleMargins(self, x1, y1, x2, y2):
        """
        Sets up display margins for the consoleOut function.

        @param x1 : the distance from left of layer to the left margin, in pixels
        @param y1 : the distance from top of layer to the top margin, in pixels
        @param x2 : the distance from left of layer to the right margin, in pixels
        @param y2 : the distance from top of layer to the bottom margin, in pixels

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_push("m" + str(int(x1)) + "," + str(int(y1)) + "," + str(int(x2)) + "," + str(int(y2)))

    def setConsoleBackground(self, bgcol):
        """
        Sets up the background color used by the clearConsole function and by
        the console scrolling feature.

        @param bgcol : the background gray level to use when scrolling (0 = black,
                255 = white), or -1 for transparent

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_push("b" + str(int(bgcol)))

    def setConsoleWordWrap(self, wordwrap):
        """
        Sets up the wrapping behavior used by the consoleOut function.

        @param wordwrap : true to wrap only between words,
                false to wrap on the last column anyway.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_push("w" + ("1" if wordwrap else "0"))

    def clearConsole(self):
        """
        Blanks the console area within console margins, and resets the console pointer
        to the upper left corner of the console.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("^")

    def setLayerPosition(self, x, y, scrollTime):
        """
        Sets the position of the layer relative to the display upper left corner.
        When smooth scrolling is used, the display offset of the layer is
        automatically updated during the next milliseconds to animate the move of the layer.

        @param x : the distance from left of display to the upper left corner of the layer
        @param y : the distance from top of display to the upper left corner of the layer
        @param scrollTime : number of milliseconds to use for smooth scrolling, or
                0 if the scrolling should be immediate.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self.command_flush("#" + str(int(x)) + "," + str(int(y)) + "," + str(int(scrollTime)))

    def hide(self):
        """
        Hides the layer. The state of the layer is preserved but the layer is not displayed
        on the screen until the next call to unhide(). Hiding the layer can positively
        affect the drawing speed, since it postpones the rendering until all operations are
        completed (double-buffering).

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.command_push("h")
        self._hidden = True
        return self.flush_now()

    def unhide(self):
        """
        Shows the layer. Shows the layer again after a hide command.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self._hidden = False
        return self.command_flush("s")

    def get_display(self):
        """
        Gets parent YDisplay. Returns the parent YDisplay object of the current YDisplayLayer.

        @return an YDisplay object
        """
        return self._display

    def get_displayWidth(self):
        """
        Returns the display width, in pixels.

        @return an integer corresponding to the display width, in pixels

        On failure, throws an exception or returns YDisplayLayer.DISPLAYWIDTH_INVALID.
        """
        return self._display.get_displayWidth()

    def get_displayHeight(self):
        """
        Returns the display height, in pixels.

        @return an integer corresponding to the display height, in pixels

        On failure, throws an exception or returns YDisplayLayer.DISPLAYHEIGHT_INVALID.
        """
        return self._display.get_displayHeight()

    def get_layerWidth(self):
        """
        Returns the width of the layers to draw on, in pixels.

        @return an integer corresponding to the width of the layers to draw on, in pixels

        On failure, throws an exception or returns YDisplayLayer.LAYERWIDTH_INVALID.
        """
        return self._display.get_layerWidth()

    def get_layerHeight(self):
        """
        Returns the height of the layers to draw on, in pixels.

        @return an integer corresponding to the height of the layers to draw on, in pixels

        On failure, throws an exception or returns YDisplayLayer.LAYERHEIGHT_INVALID.
        """
        return self._display.get_layerHeight()

    def resetHiddenFlag(self):
        self._hidden = False
        return YAPI.SUCCESS

#--- (end of generated code: YDisplayLayer implementation)

#--- (generated code: YDisplayLayer functions)
#--- (end of generated code: YDisplayLayer functions)


#--- (generated code: YDisplay class start)
#noinspection PyProtectedMember
class YDisplay(YFunction):
    """
    The YDisplay class allows to drive Yoctopuce displays.
    Yoctopuce display interface has been designed to easily
    show information and images. The device provides built-in
    multi-layer rendering. Layers can be drawn offline, individually,
    and freely moved on the display. It can also replay recorded
    sequences (animations).

    In order to draw on the screen, you should use the
    display.get_displayLayer method to retrieve the layer(s) on
    which you want to draw, and then use methods defined in
    YDisplayLayer to draw on the layers.

    """
    #--- (end of generated code: YDisplay class start)
    #--- (generated code: YDisplay definitions)
    STARTUPSEQ_INVALID = YAPI.INVALID_STRING
    BRIGHTNESS_INVALID = YAPI.INVALID_UINT
    DISPLAYWIDTH_INVALID = YAPI.INVALID_UINT
    DISPLAYHEIGHT_INVALID = YAPI.INVALID_UINT
    LAYERWIDTH_INVALID = YAPI.INVALID_UINT
    LAYERHEIGHT_INVALID = YAPI.INVALID_UINT
    LAYERCOUNT_INVALID = YAPI.INVALID_UINT
    COMMAND_INVALID = YAPI.INVALID_STRING
    ENABLED_FALSE = 0
    ENABLED_TRUE = 1
    ENABLED_INVALID = -1
    ORIENTATION_LEFT = 0
    ORIENTATION_UP = 1
    ORIENTATION_RIGHT = 2
    ORIENTATION_DOWN = 3
    ORIENTATION_INVALID = -1
    DISPLAYTYPE_MONO = 0
    DISPLAYTYPE_GRAY = 1
    DISPLAYTYPE_RGB = 2
    DISPLAYTYPE_INVALID = -1
    #--- (end of generated code: YDisplay definitions)

    def __init__(self, func):
        super(YDisplay, self).__init__(func)
        self._className = "Display"
        #--- (generated code: YDisplay attributes)
        self._callback = None
        self._enabled = YDisplay.ENABLED_INVALID
        self._startupSeq = YDisplay.STARTUPSEQ_INVALID
        self._brightness = YDisplay.BRIGHTNESS_INVALID
        self._orientation = YDisplay.ORIENTATION_INVALID
        self._displayWidth = YDisplay.DISPLAYWIDTH_INVALID
        self._displayHeight = YDisplay.DISPLAYHEIGHT_INVALID
        self._displayType = YDisplay.DISPLAYTYPE_INVALID
        self._layerWidth = YDisplay.LAYERWIDTH_INVALID
        self._layerHeight = YDisplay.LAYERHEIGHT_INVALID
        self._layerCount = YDisplay.LAYERCOUNT_INVALID
        self._command = YDisplay.COMMAND_INVALID
        #--- (end of generated code: YDisplay attributes)
        self._sequence = ""
        self._allDisplayLayers = []
        self._recording = False

    #--- (generated code: YDisplay implementation)
    def _parseAttr(self, json_val):
        if json_val.has("enabled"):
            self._enabled = (json_val.getInt("enabled") > 0 if 1 else 0)
        if json_val.has("startupSeq"):
            self._startupSeq = json_val.getString("startupSeq")
        if json_val.has("brightness"):
            self._brightness = json_val.getInt("brightness")
        if json_val.has("orientation"):
            self._orientation = json_val.getInt("orientation")
        if json_val.has("displayWidth"):
            self._displayWidth = json_val.getInt("displayWidth")
        if json_val.has("displayHeight"):
            self._displayHeight = json_val.getInt("displayHeight")
        if json_val.has("displayType"):
            self._displayType = json_val.getInt("displayType")
        if json_val.has("layerWidth"):
            self._layerWidth = json_val.getInt("layerWidth")
        if json_val.has("layerHeight"):
            self._layerHeight = json_val.getInt("layerHeight")
        if json_val.has("layerCount"):
            self._layerCount = json_val.getInt("layerCount")
        if json_val.has("command"):
            self._command = json_val.getString("command")
        super(YDisplay, self)._parseAttr(json_val)

    def get_enabled(self):
        """
        Returns true if the screen is powered, false otherwise.

        @return either YDisplay.ENABLED_FALSE or YDisplay.ENABLED_TRUE, according to true if the screen is
        powered, false otherwise

        On failure, throws an exception or returns YDisplay.ENABLED_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.ENABLED_INVALID
        res = self._enabled
        return res

    def set_enabled(self, newval):
        """
        Changes the power state of the display.

        @param newval : either YDisplay.ENABLED_FALSE or YDisplay.ENABLED_TRUE, according to the power
        state of the display

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = "1" if newval > 0 else "0"
        return self._setAttr("enabled", rest_val)

    def get_startupSeq(self):
        """
        Returns the name of the sequence to play when the displayed is powered on.

        @return a string corresponding to the name of the sequence to play when the displayed is powered on

        On failure, throws an exception or returns YDisplay.STARTUPSEQ_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.STARTUPSEQ_INVALID
        res = self._startupSeq
        return res

    def set_startupSeq(self, newval):
        """
        Changes the name of the sequence to play when the displayed is powered on.
        Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : a string corresponding to the name of the sequence to play when the displayed is powered on

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = newval
        return self._setAttr("startupSeq", rest_val)

    def get_brightness(self):
        """
        Returns the luminosity of the  module informative LEDs (from 0 to 100).

        @return an integer corresponding to the luminosity of the  module informative LEDs (from 0 to 100)

        On failure, throws an exception or returns YDisplay.BRIGHTNESS_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.BRIGHTNESS_INVALID
        res = self._brightness
        return res

    def set_brightness(self, newval):
        """
        Changes the brightness of the display. The parameter is a value between 0 and
        100. Remember to call the saveToFlash() method of the module if the
        modification must be kept.

        @param newval : an integer corresponding to the brightness of the display

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("brightness", rest_val)

    def get_orientation(self):
        """
        Returns the currently selected display orientation.

        @return a value among YDisplay.ORIENTATION_LEFT, YDisplay.ORIENTATION_UP,
        YDisplay.ORIENTATION_RIGHT and YDisplay.ORIENTATION_DOWN corresponding to the currently selected
        display orientation

        On failure, throws an exception or returns YDisplay.ORIENTATION_INVALID.
        """
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.ORIENTATION_INVALID
        res = self._orientation
        return res

    def set_orientation(self, newval):
        """
        Changes the display orientation. Remember to call the saveToFlash()
        method of the module if the modification must be kept.

        @param newval : a value among YDisplay.ORIENTATION_LEFT, YDisplay.ORIENTATION_UP,
        YDisplay.ORIENTATION_RIGHT and YDisplay.ORIENTATION_DOWN corresponding to the display orientation

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        rest_val = str(newval)
        return self._setAttr("orientation", rest_val)

    def get_displayWidth(self):
        """
        Returns the display width, in pixels.

        @return an integer corresponding to the display width, in pixels

        On failure, throws an exception or returns YDisplay.DISPLAYWIDTH_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.DISPLAYWIDTH_INVALID
        res = self._displayWidth
        return res

    def get_displayHeight(self):
        """
        Returns the display height, in pixels.

        @return an integer corresponding to the display height, in pixels

        On failure, throws an exception or returns YDisplay.DISPLAYHEIGHT_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.DISPLAYHEIGHT_INVALID
        res = self._displayHeight
        return res

    def get_displayType(self):
        """
        Returns the display type: monochrome, gray levels or full color.

        @return a value among YDisplay.DISPLAYTYPE_MONO, YDisplay.DISPLAYTYPE_GRAY and
        YDisplay.DISPLAYTYPE_RGB corresponding to the display type: monochrome, gray levels or full color

        On failure, throws an exception or returns YDisplay.DISPLAYTYPE_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.DISPLAYTYPE_INVALID
        res = self._displayType
        return res

    def get_layerWidth(self):
        """
        Returns the width of the layers to draw on, in pixels.

        @return an integer corresponding to the width of the layers to draw on, in pixels

        On failure, throws an exception or returns YDisplay.LAYERWIDTH_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.LAYERWIDTH_INVALID
        res = self._layerWidth
        return res

    def get_layerHeight(self):
        """
        Returns the height of the layers to draw on, in pixels.

        @return an integer corresponding to the height of the layers to draw on, in pixels

        On failure, throws an exception or returns YDisplay.LAYERHEIGHT_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.LAYERHEIGHT_INVALID
        res = self._layerHeight
        return res

    def get_layerCount(self):
        """
        Returns the number of available layers to draw on.

        @return an integer corresponding to the number of available layers to draw on

        On failure, throws an exception or returns YDisplay.LAYERCOUNT_INVALID.
        """
        # res
        if self._cacheExpiration == datetime.datetime.fromtimestamp(86400):
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.LAYERCOUNT_INVALID
        res = self._layerCount
        return res

    def get_command(self):
        # res
        if self._cacheExpiration <= YAPI.GetTickCount():
            if self.load(YAPI._yapiContext.GetCacheValidity()) != YAPI.SUCCESS:
                return YDisplay.COMMAND_INVALID
        res = self._command
        return res

    def set_command(self, newval):
        rest_val = newval
        return self._setAttr("command", rest_val)

    @staticmethod
    def FindDisplay(func):
        """
        Retrieves a display for a given identifier.
        The identifier can be specified using several formats:
        <ul>
        <li>FunctionLogicalName</li>
        <li>ModuleSerialNumber.FunctionIdentifier</li>
        <li>ModuleSerialNumber.FunctionLogicalName</li>
        <li>ModuleLogicalName.FunctionIdentifier</li>
        <li>ModuleLogicalName.FunctionLogicalName</li>
        </ul>

        This function does not require that the display is online at the time
        it is invoked. The returned object is nevertheless valid.
        Use the method YDisplay.isOnline() to test if the display is
        indeed online at a given time. In case of ambiguity when looking for
        a display by logical name, no error is notified: the first instance
        found is returned. The search is performed first by hardware name,
        then by logical name.

        If a call to this object's is_online() method returns FALSE although
        you are certain that the matching device is plugged, make sure that you did
        call registerHub() at application initialization time.

        @param func : a string that uniquely characterizes the display, for instance
                YD128X32.display.

        @return a YDisplay object allowing you to drive the display.
        """
        # obj
        obj = YFunction._FindFromCache("Display", func)
        if obj is None:
            obj = YDisplay(func)
            YFunction._AddToCache("Display", func, obj)
        return obj

    def resetAll(self):
        """
        Clears the display screen and resets all display layers to their default state.
        Using this function in a sequence will kill the sequence play-back. Don't use that
        function to reset the display at sequence start-up.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.flushLayers()
        self.resetHiddenLayerFlags()
        return self.sendCommand("Z")

    def fade(self, brightness, duration):
        """
        Smoothly changes the brightness of the screen to produce a fade-in or fade-out
        effect.

        @param brightness : the new screen brightness
        @param duration : duration of the brightness transition, in milliseconds.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.flushLayers()
        return self.sendCommand("+" + str(int(brightness)) + "," + str(int(duration)))

    def newSequence(self):
        """
        Starts to record all display commands into a sequence, for later replay.
        The name used to store the sequence is specified when calling
        saveSequence(), once the recording is complete.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.flushLayers()
        self._sequence = ""
        self._recording = True
        return YAPI.SUCCESS

    def saveSequence(self, sequenceName):
        """
        Stops recording display commands and saves the sequence into the specified
        file on the display internal memory. The sequence can be later replayed
        using playSequence().

        @param sequenceName : the name of the newly created sequence

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.flushLayers()
        self._recording = False
        self._upload(sequenceName, YString2Byte(self._sequence))
        # //We need to use YPRINTF("") for Objective-C
        self._sequence = ""
        return YAPI.SUCCESS

    def playSequence(self, sequenceName):
        """
        Replays a display sequence previously recorded using
        newSequence() and saveSequence().

        @param sequenceName : the name of the newly created sequence

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.flushLayers()
        return self.sendCommand("S" + sequenceName)

    def pauseSequence(self, delay_ms):
        """
        Waits for a specified delay (in milliseconds) before playing next
        commands in current sequence. This method can be used while
        recording a display sequence, to insert a timed wait in the sequence
        (without any immediate effect). It can also be used dynamically while
        playing a pre-recorded sequence, to suspend or resume the execution of
        the sequence. To cancel a delay, call the same method with a zero delay.

        @param delay_ms : the duration to wait, in milliseconds

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.flushLayers()
        return self.sendCommand("W" + str(int(delay_ms)))

    def stopSequence(self):
        """
        Stops immediately any ongoing sequence replay.
        The display is left as is.

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.flushLayers()
        return self.sendCommand("S")

    def upload(self, pathname, content):
        """
        Uploads an arbitrary file (for instance a GIF file) to the display, to the
        specified full path name. If a file already exists with the same path name,
        its content is overwritten.

        @param pathname : path and name of the new file to create
        @param content : binary buffer with the content to set

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        return self._upload(pathname, content)

    def copyLayerContent(self, srcLayerId, dstLayerId):
        """
        Copies the whole content of a layer to another layer. The color and transparency
        of all the pixels from the destination layer are set to match the source pixels.
        This method only affects the displayed content, but does not change any
        property of the layer object.
        Note that layer 0 has no transparency support (it is always completely opaque).

        @param srcLayerId : the identifier of the source layer (a number in range 0..layerCount-1)
        @param dstLayerId : the identifier of the destination layer (a number in range 0..layerCount-1)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.flushLayers()
        return self.sendCommand("o" + str(int(srcLayerId)) + "," + str(int(dstLayerId)))

    def swapLayerContent(self, layerIdA, layerIdB):
        """
        Swaps the whole content of two layers. The color and transparency of all the pixels from
        the two layers are swapped. This method only affects the displayed content, but does
        not change any property of the layer objects. In particular, the visibility of each
        layer stays unchanged. When used between one hidden layer and a visible layer,
        this method makes it possible to easily implement double-buffering.
        Note that layer 0 has no transparency support (it is always completely opaque).

        @param layerIdA : the first layer (a number in range 0..layerCount-1)
        @param layerIdB : the second layer (a number in range 0..layerCount-1)

        @return YAPI.SUCCESS if the call succeeds.

        On failure, throws an exception or returns a negative error code.
        """
        self.flushLayers()
        return self.sendCommand("E" + str(int(layerIdA)) + "," + str(int(layerIdB)))

    def nextDisplay(self):
        """
        Continues the enumeration of displays started using yFirstDisplay().
        Caution: You can't make any assumption about the returned displays order.
        If you want to find a specific a display, use Display.findDisplay()
        and a hardwareID or a logical name.

        @return a pointer to a YDisplay object, corresponding to
                a display currently online, or a None pointer
                if there are no more displays to enumerate.
        """
        hwidRef = YRefParam()
        if YAPI.YISERR(self._nextFunction(hwidRef)):
            return None
        if hwidRef.value == "":
            return None
        return YDisplay.FindDisplay(hwidRef.value)

#--- (end of generated code: YDisplay implementation)

    def get_displayLayer(self, layerId):
        """
        Returns a YDisplayLayer object that can be used to draw on the specified
        layer. The content is displayed only when the layer is active on the
        screen (and not masked by other overlapping layers).

        @param layerId : the identifier of the layer (a number in range 0..layerCount-1)

        @return an YDisplayLayer object

        On failure, throws an exception or returns None.
        """
        layercount = self.get_layerCount()
        if (layerId < 0) or (layerId >= layercount):
            self._throw(-1, "invalid DisplayLayer index, valid values are [0.." + str(layercount - 1) + "]")
            return None

        if len(self._allDisplayLayers) == 0:
            for i in range(0, layercount):
                self._allDisplayLayers.append(YDisplayLayer(self, str(i)))

        return self._allDisplayLayers[layerId]

    def flushLayers(self):
        if self._allDisplayLayers is not None:
            for it in self._allDisplayLayers:
                it.flush_now()
        return YAPI.SUCCESS

    def resetHiddenLayerFlags(self):
        if self._allDisplayLayers is not None:
            for it in self._allDisplayLayers:
                it.resetHiddenFlag()

    def sendCommand(self, cmd):
        if not self._recording:
            return self.set_command(cmd)
        self._sequence = self._sequence + cmd + '\n'
        return YAPI.SUCCESS

    #--- (generated code: YDisplay functions)

    @staticmethod
    def FirstDisplay():
        """
        Starts the enumeration of displays currently accessible.
        Use the method YDisplay.nextDisplay() to iterate on
        next displays.

        @return a pointer to a YDisplay object, corresponding to
                the first display currently online, or a None pointer
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
        err = YAPI.apiGetFunctionsByClass("Display", 0, p, size, neededsizeRef, errmsgRef)

        if YAPI.YISERR(err) or not neededsizeRef.value:
            return None

        if YAPI.YISERR(
                YAPI.yapiGetFunctionInfo(p[0], devRef, serialRef, funcIdRef, funcNameRef, funcValRef, errmsgRef)):
            return None

        return YDisplay.FindDisplay(serialRef.value + "." + funcIdRef.value)

#--- (end of generated code: YDisplay functions)
