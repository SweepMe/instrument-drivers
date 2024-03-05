# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2021 - 2022 SweepMe! GmbH

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# Contribution: We like to thank Heliatek GmbH/Dr. Ivan Ramirez for providing the
# initial version of this driver.

# deal with dlls
import ctypes  # bentham dll reading
import os

# path management
import pathlib
import struct
import time
from os.path import dirname, join

import numpy as np
from pysweepme.EmptyDeviceClass import EmptyDevice

# from pysweepme.ErrorMessage import error
from pysweepme.FolderManager import addFolderToPATH

addFolderToPATH()

HTML_driver_descript = """
        <p>Driver for the Bentham TMc300 monochromator and tuneable light source</p>
        <p>&nbsp;</p>
        <p><strong>Keywords:</strong>&nbsp;
        TMc150, TMc300, Quantum Design, LOT,&nbsp;MSH-300, MSH150, MSHD-300, MSHD-150</p>
        <p>&nbsp;</p>
        <p><strong>Usage:</strong></p>
        <ul>
        <li>Use "Find Ports" and select a combination of .cfg and .atr file that you like to use.</li>
        <li>Filters can be changed with the following format "1 &lt;- 400 nm -&gt; 2 &lt;- 700 nm -&gt; 3 &lt;
        - 750 nm -&gt; 4 &lt;- 800 nm -&gt; 5". For example, filter 2 will be used between 400 nm and 700 nm.</li>
        <li>To add such filter changing strings permanently to the options of the Filter input field, you can copy
         the file "Monochromator-Bentham_TMc300.ini" that comes with the driver to the public folder 'CustomFiles'
        and modify it. Multiple filter changing strings can be added.</li>
        <li>To select white light, use wavelength = 0&nbsp;</li>
        <li>To select no light, use wavelength = -1</li>
        </ul>
        <p><br /> <br /> <strong>Features:</strong></p>
        <ul>
        <li>Change of filters at user-specific wavelengths</li>
        <li>Change of lamp at user-specific wavelengths</li>
        <li>Change of gratings at defined wavelengths according to the configuration and attribute files</li>
        <li>Change of mirrors&nbsp;at defined wavelengths according to the configuration and attribute files</li>
        <li>End position (optional): goes back to this wavelength after the run</li>
        <li>Bias light selection, use "None" if not available</li>
        <li>Besides wavelength in nm, users can also vary energy in eV.</li>
        </ul>
        <p>&nbsp;</p>
        <p><strong>Requirements:</strong></p>
        <ul>
        <li>requires a .cfg and .atr file from bentham for the monochromator which must be copied
         to the public SweepMe! folder "CustomFiles". You can optionally create a subfolder
          e.g. "Bentham TMc 300" to store the files.</li>
        </ul>
        <p>&nbsp;</p>
        <p><strong>Contribution:</strong></p>
        <p>We like to thank Heliatek GmbH/Dr. Ivan Ramirez
         for providing the initial version of this driver.</p>
        """


class Device(EmptyDevice):

    description = HTML_driver_descript

    def __init__(self):
        """the class file is reloaded everytime SweepMe! sequencer starts. -->
        __init__ is called at each runtime"""
        super().__init__()

        # shortname in sequencer
        self.shortname = "Bentham-TMc300"

        # sweepMe boiler plate
        self.variables = ["Wavelength", "Energy", "Filter", "Grating"]
        self.units = ["nm", "eV", "#", "#"]
        self.plottype = [True, True, True, True]  # True to plot data
        self.savetype = [True, True, True, True]  # True to save data

        """filters"""
        # for the UI:  We add filter strings from the config file in CustomFiles
        # this will only
        self.filters = ["Auto", 1, 2, 3, 4, 5]
        filters_to_add = self.get_configoptions("Filter")
        for key in filters_to_add:
            self.filters.append(filters_to_add[key])

        # If there are no filter options from config file, we add an example how to create a string
        # to change filters depending on wavelength
        if len(self.filters) <= 6:
            self.filters.append(
                "1 <- 400 nm -> 2 <- 700 nm -> 3 <- 750 nm -> 4 <- 800 nm -> 5"
            )

        """ Lamps """
        self.lamps = ["Xenon <- 600 nm -> Halogen", "Xenon", "Halogen"]
        lamps_to_add = self.get_configoptions("Lamp")
        for key in lamps_to_add:
            self.lamps.append(lamps_to_add[key])

        if len(self.lamps) == 2:
            self.lamps.append("Xenon <- 600 nm -> Halogen")

    def find_Ports(self):
        """All possible combinations of .cfg and .atr files are returned that can be found in the public
        folder 'CustomFiles'
        """

        # dir_ = pathlib.Path(__file__).resolve().parent #find current dir
        dir_ = pathlib.Path(self.get_folder("CUSTOMFILES"))
        length = len(str(dir_)) + 1

        gen_ = dir_.rglob("*.cfg")  # generator
        sys_config_files = [str(f)[length:] for f in gen_ if f.is_file()]

        if len(sys_config_files) == 0:
            self.message_Box(
                """
                No config files (*.cfg) found in public SweepMe! folder 'CustomFiles'.
                Please copy such files as shipped with your monochromator to this folder.
                """
            )

        gen_ = dir_.rglob("*.atr")  # generator
        sys_attr_files = [str(f)[length:] for f in gen_ if f.is_file()]

        if len(sys_attr_files) == 0:
            self.message_Box(
                """
                No attribute files (*.atr) found in public SweepMe! folder 'CustomFiles'.
                Please copy such files as shipped with your monochromator to this folder.
                """
            )

        ports = []
        for x in sys_config_files:
            for y in sys_attr_files:
                ports.append(x + " // " + y)

        return ports

    def set_GUIparameter(self):

        # dir_ = pathlib.Path(__file__).resolve().parent #find current dir
        GUIparameter = {
            "SweepMode": ["Wavelength in nm", "None"],
            "EndPosition": "",
            # ["1 <- 400 nm -> 2 <- 700 nm -> 3 <- 750 nm -> 4 <- 800 nm -> 5"]
            "Filter": self.filters,
            # "Grating":
            "Lamp": self.lamps,
            "Wavelength": 550,
            "BiasLight": ["None", "Off", "Source 1", "Source 2", "Source 1+2"],
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):

        # print(parameter)
        self.sweepmode = parameter["SweepMode"]

        try:
            cfg_file, attr_file = parameter["Port"].split(" // ")
            self.config_file = os.path.join(self.get_folder("CUSTOMFILES"), cfg_file)
            self.attr_file = os.path.join(self.get_folder("CUSTOMFILES"), attr_file)
        except Exception:
            self.attr_file = ""
            self.config_file = ""

        self.wavelength = float(parameter["Wavelength"])

        # hardcoded MC settle delay of 100 ms
        self.s_delay = ctypes.c_long(int(100))

        # older MC module versions dont support bias light
        if "BiasLight" not in parameter:
            raise Exception(
                """
            Monochromator module version is out of date, please
            update the MC module to run this driver"""
            )
        self.bias_light = parameter["BiasLight"]

        self.end_position = parameter["EndPosition"]

        # validate value
        if self.end_position != "":
            try:
                self.end_position = float(self.end_position)
            except ValueError:
                self.end_position = 0
                print(
                    """
                    Unable to convert end position of Monochromator module to float.
                    Please check the given value."""
                )
        else:
            self.end_position = 0

        lamp_string = parameter["Lamp"]
        if lamp_string == "Xenon":
            self.sam_switch = 2000
        elif lamp_string == "Halogen":
            self.sam_switch = 0
        elif lamp_string != "":
            lamp_readout = (
                lamp_string.replace("<", "")
                .replace(">", "")
                .replace("nm", "")
                .replace(" ", "")
                .split("-")
            )
            self.sam_switch = float(lamp_readout[1])
        else:
            self.sam_switch = 600

        self.filter_string = parameter["Filter"]

    def connect(self):

        # get names of system components from cfg file
        self.build_system_cfg()

        # might need to add some code here that transfers the dll object between multiple
        # instances of this device class

        # bentham backend
        py_arch = struct.calcsize("P") * 8
        # print("Bentham TLS: python architecture:", py_arch)
        driver_directory = os.path.abspath(os.path.dirname(__file__))

        if py_arch == 64:
            self.dll = ctypes.WinDLL(
                driver_directory + os.sep + "libs" + os.sep + "benhw64.dll"
            )  # ctypes.WinDLL?
        elif py_arch == 32:
            self.dll = ctypes.WinDLL(
                driver_directory + os.sep + "libs" + os.sep + "IEEE_32M.dll"
            )
            self.dll = ctypes.WinDLL(
                driver_directory + os.sep + "libs" + os.sep + "benhw32_stdcall.dll"
            )
        else:
            self.message_Box(
                "Error unexpected python architecture looking for TMC300 MC ports"
            )
            raise Exception("Unable to retrieve python bitness")

        if not os.path.exists(self.config_file):
            raise OSError(
                """
                Bentham TMC300 config file not found. Please put the .cfg file to
                the public SweepMe! folder 'CustomFiles'."""
            )

        buffer = ctypes.create_string_buffer(128)

        # here, we check whether the monochromator is already configured
        MC_configured = self.get_wavelength()

        if MC_configured < 0:  # not configured
            s1 = self.dll.BI_build_system_model(self.cpointer(self.config_file), buffer)
            if s1 != 0:
                raise Exception("Unable to connect to instrument build system model")

            s2 = self.dll.BI_load_setup(self.cpointer(self.attr_file))
            if s2 != 0:
                raise Exception("Unable to load setup with .atr file.")

            s3 = self.dll.BI_initialise()
            if s3 != 0:
                raise Exception("Unable to initialize.")

        # else:
        # print("Bentham MC/TLS: system Model already built.")

        setup_out = join(dirname(self.attr_file), "debug_setup_atstart.atr")
        self.dll.BI_save_setup(self.cpointer(setup_out))

    def initialize(self):

        # check whether the monochromator is already configured
        MC_configured = False if self.get_wavelength() < 0 else True
        if not MC_configured:
            # park monochromator (needs to be done before any set wavelength command)
            self.park()  #

    def deinitialize(self):

        if self.end_position != 0:
            self.goto_wavelength(self.end_position)

    def configure(self):
        # Auto uses the default config from the ben cfg file
        if not self.filter_string == "Auto":
            self.set_fwheel_switch_wlns()  # set fwheel options
        self.set_SAM_switch()  # set light source SAM options

        if self.bias_light != "None":
            self.change_bias_light()

        if not self.sweepmode == "Wavelength in nm":
            self.goto_wavelength(self.wavelength)

    def unconfigure(self):
        # close the shutter ?
        pass

    def apply(self):

        if self.sweepmode == "Wavelength in nm":
            self.goto_wavelength(float(self.value))

    def measure(self):
        pass

    def call(self):

        curr_wln = self.get_wavelength()
        curr_grating = self.get_grating_pos()
        curr_filter = self.get_fwheel_pos()

        if curr_wln > 0.0:
            energy = 1239.41974 / curr_wln
        else:
            energy = float("nan")

        return curr_wln, energy, curr_filter, curr_grating

    def cpointer(self, str_):
        """from bentham to encode messages to instrument"""
        byt = str_.encode("ascii")
        chars = ctypes.c_char_p(byt)
        return chars

    def build_system_cfg(self):
        """build & validate the system component names by checking
        they appear in the component file"""

        # read bentham file representing system as 2 col array
        # file declares handles of system components (eg TM300 --> mono)
        # bentham systems can have arbitrary number of MCs/FWs etc
        cfg_data = np.loadtxt(self.config_file, dtype=str, usecols=[0, 1])
        components = cfg_data[:, 0]
        fwheel_idx = np.where(np.char.startswith(components, "FW"))
        MC_idx = np.where(np.char.startswith(components, "TM300"))

        # CHECK system cfg has 1FW and 1
        assert (
            len(fwheel_idx) == 1
        ), "Bentham system.cfg/setup has more/fewer than 1 filter wheel (Not supported)."
        assert (
            len(MC_idx) == 1
        ), "Bentham system.cfg/setup has more/fewer than 1 filter wheel (Not supported)."

        # get component names from 2D array
        self.MC_name = cfg_data[MC_idx, 1][0, 0]
        self.FW_name = cfg_data[fwheel_idx, 1][0, 0]
        # TODO: read bias lights?\
        self.bias1 = "bias_src"
        self.bias2 = "bias_src2"

    def get_val(self, hardware_id="mono", command=None, ind=0):
        """implementation of dll "get" function"""

        val = ctypes.c_double(0)  # variable to which dll will write
        success = self.dll.BI_get(
            self.cpointer(hardware_id), int(command), ind, ctypes.byref(val)
        )  # actual command
        # user info
        if (success < 0) or (str(val).find("-1") >= 0):
            print("Bentham TMc300 ERROR for command id %s: " % command, val, success)
            return -1  # val may still exist and be nonesense

        return val.value

    def goto_wavelength(self, wl):

        if wl == -1:
            self.close_shutter()
            return

        prev_filter = self.get_fwheel_pos()
        prev_grating = self.get_grating_pos()

        self.set_wavelength(wl)

        if (
            wl == self.sam_switch
        ):  # TODO: check whether we have to toggle using the last
            time.sleep(5.5)  # let the mirror swing settle

        new_grating = self.get_grating_pos()

        if new_grating != prev_grating:
            # somehow the API fails to sleep after sam/MC grating changes
            time.sleep(0.8)

        new_filter = self.get_fwheel_pos()
        if new_filter != prev_filter:
            # somehow the API fails to sleep after sam/MC grating changes
            time.sleep(2.0)
            if (
                new_filter - prev_filter != 1
            ):  # more time if change several filter positions
                time.sleep(0.5 * abs(new_filter - prev_filter))
        time.sleep(0.1)

    def set_wavelength(self, wl):

        success = self.dll.BI_select_wavelength(
            ctypes.c_double(float(wl)), ctypes.byref(self.s_delay)
        )
        if success != 0:
            raise Exception(
                "Bentham TLS: go to wavelength %.2f failed: %s" % (wl, success)
            )

    def get_wavelength(self):
        return float(self.get_val(self.MC_name, MonochromatorCurrentWL, 0))

    def get_grating_pos(self):
        return int(self.get_val(self.MC_name, MonochromatorCurrentGrating, 0))

    def change_bias_light(self):
        """set state of both bias light sources based on user input"""

        state_source1 = 1 if self.bias_light.find("1") >= 0 else 0
        state_source2 = 1 if self.bias_light.find("2") >= 0 else 0

        self.set_bias_light(1, state_source1)
        self.set_bias_light(2, state_source2)

    def close_shutter(self):
        """close the shutter"""
        self.dll.BI_close_shutter()

    def park(self):
        """parks the monochromator"""
        self.dll.BI_park()

    def set_bias_light(self, src, state):
        """set the state of the given bias light source"""

        if "1" in str(src):
            bias_light_name = self.bias1
        elif "2" in str(src):
            bias_light_name = self.bias2

        sam = self.cpointer(bias_light_name)
        success = self.dll.BI_set(sam, SAMCurrentState, 0, ctypes.c_double(state))
        if success < 0:
            raise Exception(
                "Bentham TMc300 error - could not switch bias light for source '%s'"
                % str(src)
            )

    def set_fhweel_pos(self, ind):
        if not 0 < ind <= 6:
            print("invalid filter wheel index")
            return
        self.dll.BI_set(self.cpointer(self.FW_name), FWheelCurrentPosition, 1, ind)

    def get_fwheel_pos(self):

        return int(self.get_val(self.FW_name, FWheelCurrentPosition, 0))

    def set_fwheel_switch_wlns(self):
        """Parse user inputs and write wln at which each filter is switched
        to memory (.atr file loaded in mem)
        """
        # FW pos 6 normally corresponds to shutter.
        # All FW values need to be overwritten otherwise from loaded
        # .atr file will be used
        # 0 typically signifies do not use/or used by default
        # ! first 0 is used not last --> need a tiny value for last 0

        """ parse the GUI entry """
        # if was a single value
        try:
            fixed_filt_pos = int(self.filter_string)
            # self.set_fhweel_pos(fixed_filt_pos)
            filter_list = [1, 2, 3, 4, 5]
            fwheel_wlns = (
                [0] * (fixed_filt_pos - 1) + [0.1] + [1000000] * (5 - fixed_filt_pos)
            )
        # settings string or invalid input
        except ValueError:
            # parse settings string
            filter_readout = (
                self.filter_string.replace("<", "")
                .replace(">", "")
                .replace("nm", "")
                .replace(" ", "")
                .split("-")
            )
            filter_list = list(map(int, filter_readout[::2]))
            fwheel_wlns = [0] + list(map(float, filter_readout[1::2]))

            # reformat lists to attr file fmt
            # set missing filter positions to 0 wln
            for i in range(1, 7):
                if i not in filter_list:
                    filter_list.insert(i - 1, i)
                    fwheel_wlns.insert(i - 1, 0)

            # check whether there are consecutive 0s in the wlns
            consec_0s = [
                (fwheel_wlns[i] == fwheel_wlns[i + 1]) & (fwheel_wlns[i] == 0)
                for i in range(len(fwheel_wlns) - 1)
            ]
            # if there are consecutive 0s, make last 1 a small value
            if any(consec_0s):
                last_0_idx = len(consec_0s) - consec_0s[::-1].index(True)
                fwheel_wlns[last_0_idx] = 0.1

        # set the filter values
        for f_pos, wln in zip(filter_list, fwheel_wlns):
            wln_c = ctypes.c_double(wln)
            FW_pointer = self.cpointer(self.FW_name)
            self.dll.BI_set(FW_pointer, FWheelFilter, f_pos, wln_c)

        setup_out = join(dirname(self.attr_file), "debug_setup_SetFwheelPos.atr")
        self.dll.BI_save_setup(self.cpointer(setup_out))

    def set_SAM_switch(self):
        """set the wavelength at which the SAM is switched
        This may be attr file dependent - here looks like
        switch wavelength,1 =  0.00000000000000E+0000
        state,1 = 1
        switch wavelength,2 =  7.00000000000000E+0002
        state,2 = 0

        This does not permantly edit the attr file"""

        sam_name = "entrance"  # the MC sam
        wln_c = ctypes.c_double(self.sam_switch)
        sam = self.cpointer(sam_name)
        self.dll.BI_set(sam, SAMSwitchWL, 1, ctypes.c_double(0))  # Xe lamp
        self.dll.BI_set(sam, SAMSwitchWL, 2, wln_c)  # QTH lamp


# -----------------------------------------------------------------------------

# DLL Tokens below are taken from DLLTOKEN.txt that is shipped with this driver
# Please have at the top of this file regarding the license and copyright information.

# -----------------------------------------------------------------------------
# Monochromator attributes
# -----------------------------------------------------------------------------
MonochromatorScanDirection = 10
MonochromatorCurrentWL = 11
MonochromatorCurrentDialReading = 12
MonochromatorParkDialReading = 13
MonochromatorCurrentGrating = 14
MonochromatorPark = 15
MonochromatorSelfPark = 16
MonochromatorModeSwitchNum = 17
MonochromatorModeSwitchState = 18
MonochromatorCanModeSwitch = 19

Gratingd = 20
GratingZ = 21
GratingA = 22
GratingWLMin = 23
GratingWLMax = 24
GratingX2 = 25
GratingX1 = 26
GratingX = 27

ChangerZ = 50

# -----------------------------------------------------------------------------
# Filter wheel attributes
# -----------------------------------------------------------------------------
FWheelFilter = 100
FWheelPositions = 101
FWheelCurrentPosition = 102

# -----------------------------------------------------------------------------
# TLS attributes
# -----------------------------------------------------------------------------
TLSCurrentPosition = 150
TLSWL = 151
TLSPOS = 152
TLSSelectWavelength = 153
TLSPositionsCommand = 154

# -----------------------------------------------------------------------------
# Switch-over box attributes
# -----------------------------------------------------------------------------
SOBInitialState = 200
SOBState = 202

# -----------------------------------------------------------------------------
# SAM attributes
# -----------------------------------------------------------------------------
SAMInitialState = 300
SAMSwitchWL = 301
SAMState = 302
SAMCurrentState = 303
SAMDeflectName = 304
SAMNoDeflectName = 305

# -----------------------------------------------------------------------------
# Stepper SAM attributes
# -----------------------------------------------------------------------------
SSEnergisedSteps = 320
SSRelaxedSteps = 321
SSMaxSteps = 322
SSSpeed = 323
SSMoveCurrent = 324
SSIdleCurrent = 325

# -----------------------------------------------------------------------------
# 262
# -----------------------------------------------------------------------------
biRelay = 350
biCurrentRelay = 351

# -----------------------------------------------------------------------------
# MVSS attributes
# -----------------------------------------------------------------------------
MVSSSwitchWL = 401
MVSSWidth = 402
MVSSCurrentWidth = 403
MVSSSetWidth = 404
MVSSConstantBandwidth = 405
MVSSConstantwidth = 406
MVSSSlitMode = 407
MVSSPosition = 408

# -----------------------------------------------------------------------------
# ADC attributes
# -----------------------------------------------------------------------------
ADCSamplesPerReading = 500
ADCAdaptiveIntegration = 501
ADCSamplePeriod = 502
ADCVolts = 504
ADCAuxVolts = 507
ADCAuxOffset = 508
ADCAuxInput = 509

# -----------------------------------------------------------------------------
# SR810 ADC attributes
# -----------------------------------------------------------------------------
ADCTimeConstant = 505
ADCXYThetaReading = 506

# -----------------------------------------------------------------------------
# ADC CHOPPER attributes
# -----------------------------------------------------------------------------
ADCChoppedAverages = 503

# -----------------------------------------------------------------------------
# General amplifier attributes
# -----------------------------------------------------------------------------
AmpGain = 600
AmpChannel = 601
AmpMinRange = 602
AmpMaxRange = 603
AmpStartRange = 604
AmpUseSetup = 605
AmpCurrentRange = 606
AmpCurrentChannel = 607
AmpOverload = 608
AmpOverrideWl = 609
AmpCurrentSetup = 610

# -----------------------------------------------------------------------------
# 225 attributes
# -----------------------------------------------------------------------------
A225TargetRange = 700
A225PhaseVariable = 701
A225PhaseQuadrant = 702
A225TimeConstant = 703
A225fMode = 704

# -----------------------------------------------------------------------------
# Camera attributes
# -----------------------------------------------------------------------------
CameraIntegrationTime = 800
CameraWidthInPixels = 801
CameraWidthInMM = 802
CameraSAMState = 803
CameraAutoRange = 804
CameraMVSSWidth = 805
CameraAverages = 806
CameraMinITime = 807
CameraMaxITime = 808
CameraUnitMaxITime = 809
CameraDataLToR = 810
CameraBeta = 811
CameraPhi = 812

# -----------------------------------------------------------------------------
# Motorised Stage attributes
# -----------------------------------------------------------------------------
MotorPosition = 900
MotorStop = 901

# -----------------------------------------------------------------------------
# EBox Monitor attributes
# -----------------------------------------------------------------------------
EboxReadHv = 910
EboxReadTemp = 911
EboxReadHvRaw = 912
EboxReadTempRaw = 913
EboxWait = 914
EboxRepeats = 915
EboxCountsAtTargetTemp = 916
EboxGradientTemp = 917
EboxTargetTemp = 918
EboxCountsAtTargetHv = 919
EboxGradientHv = 920
EboxTargetHv = 921
# New attributes

# -----------------------------------------------------------------------------
# Keithley 2400 SourceMeter Attributes
# -----------------------------------------------------------------------------
ExternalADCAutoRange = 930
ExternalADCCurrentRange = 931
ExternalADCComms = 932
ExternalADCFourWireMode = 933
ExternalADCCurrentCompliance = 934
ExternalADCVoltageBias = 935
ExternalADCMode = 936

# -----------------------------------------------------------------------------
# Chopper418
# -----------------------------------------------------------------------------
ChopperFrequency = 940
ChopperDACValue = 941
ChopperState = 942
ChopperDACFromADC = 943

# -----------------------------------------------------------------------------
# Miscellaneous attributes
# -----------------------------------------------------------------------------
biSettleDelay = 1000
biMin = 1001
biMax = 1002
biParkPos = 1003
biInput = 1004
biCurrentInput = 1005
biMoveWithWavelength = 1006
biHasSetupWindow = 1007
biHasAdvancedWindow = 1008
biDescriptor = 1009
biParkOffset = 1010
biProductName = 1011

# -----------------------------------------------------------------------------
# System attributes
# -----------------------------------------------------------------------------
SysStopCount = 9000
SysDarkIIntegrationTime = 9001
Sys225_277Input = 9002

# -----------------------------------------------------------------------------
# Bentham Hardware Types
# -----------------------------------------------------------------------------
BenInterface = 10000
BenSAM = 10001
BenSlit = 10002
BenFilterWheel = 10003
BenADC = 10004
BenPREAMP = 10005
BenACAMP = 10006
BenDCAMP = 10007
BenPOSTAMP = 10012
BenRelayUnit = 10008
BenMono = 10009
BenAnonDevice = 10010
BenCamera = 10020
BenDiodeArray = 10021
BenORM = 10022
BenEBox_Monitor = 10023

BenUnknown = 10011

# tests
if __name__ == "__main__":
    TMC = Device()
