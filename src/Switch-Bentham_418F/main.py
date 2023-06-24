# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2022 SweepMe! GmbH (sweep-me.net)

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

# deal with dlls
import ctypes  # bentham dll reading
import os
import sys
import time

from enum import Enum

from pysweepme.EmptyDeviceClass import EmptyDevice

# from pysweepme.ErrorMessage import error
from pysweepme.FolderManager import addFolderToPATH
addFolderToPATH()


class Device(EmptyDevice):

    description = """
    <p><strong>Model:</strong> optical chopper 418F</p>
    <p>&nbsp;</p>
    <p><strong>Usage:</strong></p>
    <ul>
    <li>There is only one sweep mode, so a frequency must be set always. Use the Sweep editor or the Sweep box to set 
    at least a single frequency.</li>
    <li>The driver automatically connects to a Bentham chopper, so using the button "Find_ports" is not needed. </li>
    </ul>
    <p>&nbsp;</p>
    <p><strong>Info:</strong></p>
    <ul>
    <li>The driver comes with a system.cfg and a system.atr file as needed by the Bentham SDK that define only a 
    Bentham chopper model 418F. This way, it should be possible to control the chopper independent from other 
    Bentham equipment.</li>
    </ul>
    <p>&nbsp;</p>
    <p><strong>Known issues:</strong></p>
    <ul>
    <li>At start of a measurement run, the optical chopper goes first to the default frequency before the desired 
    frequency is applied.</li>
    <li>Reading the frequency is unreliable. The values can match the current frequency but are also randomly 
    higher.</li>
    <li>It is not possible to control more than one chopper at the same time.</li>
    </ul>
     """

    def __init__(self):

        super().__init__()

        # shortname in sequencer
        self.shortname = "Chopper 418F"

        # sweepMe boiler plate
        self.variables = ["Frequency"]
        self.units = ["Hz"]
        self.plottype = [True]
        self.savetype = [True]

    def find_ports(self):

        # The option "Automatic detection" is more a message to the user that no port must be selected as people
        # might wonder why the port field is otherwise empty.
        return ["Automatic detection"]

    def set_GUIparameter(self):

        GUIparameter = {
            "SweepMode": ["Frequency in Hz"],
        }

        return GUIparameter

    def get_GUIparameter(self, parameter={}):

        self.sweepmode = parameter["SweepMode"]

    def connect(self):

        # might need to add some code here that transfers the dll object between multiple
        # instances of this driver, it means the self.dll object could be exchanged
        # can be done if it gets a problem

        driver_directory = os.path.abspath(os.path.dirname(__file__))

        # bentham backend
        bitness = 64 if sys.maxsize > 2**32 else 32

        if bitness == 64:
            self.dll = ctypes.WinDLL(
                driver_directory + os.sep + "libs" + os.sep + "benhw64.dll"
            )
        elif bitness == 32:
            self.dll = ctypes.WinDLL(
                driver_directory + os.sep + "libs" + os.sep + "IEEE_32M.dll"
            )
            self.dll = ctypes.WinDLL(
                driver_directory + os.sep + "libs" + os.sep + "benhw32_stdcall.dll"
            )
        else:
            raise Exception("Unable to retrieve python bitness. Must be 32 or 64, but not %s" % str(bitness))

        config_file = driver_directory + os.sep + "Configuration files" + os.sep + "system.cfg"
        attr_file = driver_directory + os.sep + "Configuration files" + os.sep + "system.atr"

        # check whether the instrument can already communicate i.e. it was already initialized
        is_configured = self.get_frequency()
        # print("config ready", is_configured)

        # if the instrument is not configured yet, we build the system model, load the setup, and initialize
        if is_configured < 0:

            buffer = ctypes.create_string_buffer(128)
            s1 = self.dll.BI_build_system_model(self.cpointer(config_file), buffer)
            if s1 != 0:
                raise Exception("Unable to connect to instrument build system model")

            s2 = self.dll.BI_load_setup(self.cpointer(attr_file))
            if s2 != 0:
                raise Exception("Unable to load setup with .atr file.")

            s3 = self.dll.BI_initialise()
            if s3 != 0:
                raise Exception("Unable to initialize.")

    def initialize(self):
        self.reach()

    def apply(self):

        if self.sweepmode == "Frequency in Hz":
            self.set_frequency(float(self.value))

    def reach(self):

        starttime = time.time()
        while True:
            if hasattr(self, "is_run_stopped") and self.is_run_stopped():
                break
            state = self.get_state()
            # print("State:", state)

            # frequency = self.get_frequency()
            # print("Frequency:", frequency)

            if time.time() - starttime > 300:
                raise Exception("Timeout reached when finding chopper frequency")

            if state == 2:
                break

            time.sleep(1)

    def call(self):

        frequency = self.get_frequency()
        return frequency

    @staticmethod
    def cpointer(str_):
        """from bentham to encode messages to instrument"""
        byt = str_.encode("ascii")
        chars = ctypes.c_char_p(byt)
        return chars

    def get_val(self, hardware_id="chopper", command=None, ind=0):
        """implementation of dll "BI_get" function"""

        val = ctypes.c_double(0)  # variable to which dll will write
        success = self.dll.BI_get(self.cpointer(hardware_id), command.value, ind, ctypes.byref(val))  # actual command
        # The attribute index (ind) is used where an attribute token may refer to one of several values.

        # user info
        if (success < 0) or (str(val).find("-1") >= 0):
            # print("Bentham SDK ERROR for command %s: " % command, val, success)
            return -1  # val may still exist and be nonesense

        return val.value

    def set_val(self, hardware_id="chopper", command=None, ind=0, value=None):
        """implementation of dll "BI_set" function

        Args:
            hardware_id: str
            command: Token
            ind: (int), index
            value: ctypes object, e.g. ctypes.c_double

        """

        success = self.dll.BI_set(self.cpointer(hardware_id), command.value, ind, value)

        # user info
        if success < 0:
            print("Bentham SDK ERROR for command %s: " % command, value, success)
            return -1  # val may still exist and be nonesense

        return True

    def set_frequency(self, frequency):
        self.set_val("chopper", Token.ChopperFrequency, 1, ctypes.c_double(frequency))

    def get_frequency(self):
        return float(self.get_val("chopper", Token.ChopperFrequency, 1))

    def get_state(self):
        return float(self.get_val("chopper", Token.ChopperState, 1))


class Token(Enum):
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
    # Instead of setting the chopper frequency, the user can set the DAC value (not sure why someone might do that).
    ChopperDACValue = 941
    # States{0:'off', 1:'on (local)', 2:'on (remote)', 3:'off (remote)'
    ChopperState = 942
    # ChopperDACFromADC When the chopper is in local mode, the frequency is driven by the
    # potentiometer. When in remote mode it is driven from a DAC. To find the DAC value that
    # corresponds most closely to the potentiometer, send the ChopperDACFromADC token. This
    # will take an ADC reading from the potentiometer and convert this to a DAC value
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
