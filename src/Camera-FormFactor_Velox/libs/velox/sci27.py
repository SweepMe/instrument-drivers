
# MIT License
#
# Copyright 2025 FormFactor GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software 
# and associated documentation files (the “Software”), to deal in the Software without 
# restriction, including without limitation the rights to use, copy, modify, merge, publish, 
# distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or 
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR 
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR 
# OTHER DEALINGS IN THE SOFTWARE.

from  velox.vxmessageserver import *
from decimal import Decimal
from collections import namedtuple

"""
Velox SCI Commands
This module provides a function interface to the FormFactor Velox software suite. 
The module was auto-generated on 2025-02-12.  
677 SCI commands were found and included.

To use this module, your code must import the Velox Python module.
Create a connection to the Velox Message Server using the 'with MessageServerInterface():' 
command as shown in the sample below.

The Velox Message Server must be running prior to establishing a connection. 
To start the Message Server, run Velox.

The sample code to use this module is:

import velox
with velox.MessageServerInterface() as msgServer:

    # Your Code: try some SCI Commands - such as:
    response = velox.ReportKernelVersion()
    print ('The Kernel version is', response.Version, 'and', response.Description)
    
"""
def EchoData(TestCmd=""):
    """
    Test Command for the Kernel Communication. Like a ping command, the given text
    string is returned unchanged.
    Status: published
    ----------
    Parameters:
        TestCmd:str = "Test"
    ----------
    Response:
        TestRsp:str
    ----------
    Command Timeout: 5000
    Example:EchoData Test
    """
    rsp = MessageServerInterface.sendSciCommand("EchoData",TestCmd)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ReportKernelVersion(Module=""):
    """
    Returns the version information of the Kernel. The "Version" value contains
    version number and revision level of the actual Kernel implementation. The text
    string contains a code description, version number and the revision date.
    Status: published
    ----------
    Parameters:
        Module:str = "K"
    ----------
    Response:
        Version:Decimal
        Description:str
    ----------
    Command Timeout: 5000
    Example:ReportKernelVersion K
    """
    rsp = MessageServerInterface.sendSciCommand("ReportKernelVersion",Module)
    global ReportKernelVersion_Response
    if not "ReportKernelVersion_Response" in globals(): ReportKernelVersion_Response = namedtuple("ReportKernelVersion_Response", "Version,Description")
    return ReportKernelVersion_Response(Decimal(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def ReadProberStatus():
    """
    Returns an actual status information of the Probe Station.
    Status: published
    ----------
    Response:
        FlagsBusy:int
        FlagsContact:int
        Mode:str
        IsQuiet:int
    ----------
    Command Timeout: 5000
    Example:ReadProberStatus
    """
    rsp = MessageServerInterface.sendSciCommand("ReadProberStatus")
    global ReadProberStatus_Response
    if not "ReadProberStatus_Response" in globals(): ReadProberStatus_Response = namedtuple("ReadProberStatus_Response", "FlagsBusy,FlagsContact,Mode,IsQuiet")
    return ReadProberStatus_Response(int(rsp[0]),int(rsp[1]),str(rsp[2]),int(rsp[3]))

def EnableMotorQuiet(WantQuietModeOn="", Stage=""):
    """
    Toggles the motor power for quiet probing. In most applications this feature is
    not required. However, for special measurements it may be necessary to reduce
    the noise of the system. Quiet on turns off the motor power for all stages (or
    the one specified with the optional parameter). Quiet off will turn on the motor
    power of all stages (or the one specified with the optional parameter) for
    subsequent movements. A move command will also turn on the motor power of the
    moved stage automatically. For automatically switching of the quiet mode refer
    to Auto Quiet functionality.  Sending 'EnableMotorQuiet 1' will enable the quiet
    mode for all stages. Sending 'EnableMotorQuiet 1 C' will only enable the quiet
    mode for the Chuck stage. Sending 'EnableMotorQuiet 1 1' will only enable the
    quiet mode for the Positioner1 stage. Sending 'EnableMotorQuiet 0 S' will only
    disable the quiet mode for the Scope stage.
    Status: published
    ----------
    Parameters:
        WantQuietModeOn:int = 0
        Stage:str = "None"
    ----------
    Command Timeout: 10000
    Example:EnableMotorQuiet 1
    """
    MessageServerInterface.sendSciCommand("EnableMotorQuiet",WantQuietModeOn,Stage)


def SetChuckVacuum(WantChuckVacuumOn=""):
    """
    Toggles the Chuck vacuum on (1) or off (0). Can return vacuum timeout error for
    stations with wafer vacuum sensors in case no wafer was detected.
    Status: published
    ----------
    Parameters:
        WantChuckVacuumOn:int = 0
    ----------
    Command Timeout: 10000
    Example:SetChuckVacuum 1
    """
    MessageServerInterface.sendSciCommand("SetChuckVacuum",WantChuckVacuumOn)


def SetMicroLight(WantIlluminatorOn=""):
    """
    Toggles the microscope light channel of the peripheral output board and all
    cameras. Notifications: 7
    Status: published
    ----------
    Parameters:
        WantIlluminatorOn:int = 2
    ----------
    Command Timeout: 5000
    Example:SetMicroLight 1
    """
    MessageServerInterface.sendSciCommand("SetMicroLight",WantIlluminatorOn)


def SetBeaconStatus(FlagsMode="", PulseWidthRed="", PulseWidthGreen="", PulseWidthYellow="", PulseWidthBlue="", PulseWidthWhite=""):
    """
    This command controls the beacon channel of the peripheral output board. All
    lights can be switched on, off, or blinking. Setting an interval to zero means,
    that the corresponding light will be statically on or off. The minimum blinking
    interval is 50ms.
    Status: published
    ----------
    Parameters:
        FlagsMode:int = 0
        PulseWidthRed:int = 1000
        PulseWidthGreen:int = 0
        PulseWidthYellow:int = 0
        PulseWidthBlue:int = 0
        PulseWidthWhite:int = 0
    ----------
    Command Timeout: 5000
    Example:SetBeaconStatus 1 1000
    """
    MessageServerInterface.sendSciCommand("SetBeaconStatus",FlagsMode,PulseWidthRed,PulseWidthGreen,PulseWidthYellow,PulseWidthBlue,PulseWidthWhite)


def SetOutput(Channel="", WantOutputOn="", PulseTime=""):
    """
    Controls the Velox output channel signals. It can be used to activate/deactivate
    outputs.
    Status: published
    ----------
    Parameters:
        Channel:int = 1
        WantOutputOn:int = 0
        PulseTime:int = -1
    ----------
    Command Timeout: 5000
    Example:SetOutput 4 0
    """
    MessageServerInterface.sendSciCommand("SetOutput",Channel,WantOutputOn,PulseTime)


def StopAllMovements():
    """
    Stops all Probe Station movements immediately. The response status value of any
    pending movement will signify that the stop command was executed.
    Status: published
    ----------
    Command Timeout: 5000
    Example:StopAllMovements
    """
    MessageServerInterface.sendSciCommand("StopAllMovements")


def InkDevice(FlagsInker="", PulseWidth=""):
    """
    Inks the current device under test. The range of PulseWidth is 20ms to 2000ms.
    For correct function, the inkers have to be linked to default outputs.
    Status: published
    ----------
    Parameters:
        FlagsInker:int = 0
        PulseWidth:int = 50
    ----------
    Command Timeout: 10000
    Example:InkDevice 1 40
    """
    MessageServerInterface.sendSciCommand("InkDevice",FlagsInker,PulseWidth)


def ReadProbeSetup():
    """
    Returns the current Positioner configuration.  The output pattern is:  1. Type
    Positioner 1 2. Type Positioner 2 3. Type Positioner 3 4. Type Positioner 4 5.
    Type Positioner 5 6. Axis Positioner 1 (Bit 0: XY, Bit 1: Z) 7. Axis Positioner
    2 (Bit 0: XY, Bit 1: Z) 8. Axis Positioner 3 (Bit 0: XY, Bit 1: Z) 9. Axis
    Positioner 4 (Bit 0: XY, Bit 1: Z) 10. Axis Positioner 5 (Bit 0: XY, Bit 1: Z)
    11. Type Positioner 6 12. Axis Positioner 6 (Bit 0: XY, Bit 1: Z)
    Status: published
    ----------
    Response:
        TypePositioner1:int
        TypePositioner2:int
        TypePositioner3:int
        TypePositioner4:int
        TypePositioner5:int
        AxisPositioner1:int
        AxisPositioner2:int
        AxisPositioner3:int
        AxisPositioner4:int
        AxisPositioner5:int
        TypePositioner6:int
        AxisPositioner6:int
    ----------
    Command Timeout: 5000
    Example:ReadProbeSetup
    """
    rsp = MessageServerInterface.sendSciCommand("ReadProbeSetup")
    global ReadProbeSetup_Response
    if not "ReadProbeSetup_Response" in globals(): ReadProbeSetup_Response = namedtuple("ReadProbeSetup_Response", "TypePositioner1,TypePositioner2,TypePositioner3,TypePositioner4,TypePositioner5,AxisPositioner1,AxisPositioner2,AxisPositioner3,AxisPositioner4,AxisPositioner5,TypePositioner6,AxisPositioner6")
    return ReadProbeSetup_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]),int(rsp[7]),int(rsp[8]),int(rsp[9]),int(rsp[10]),int(rsp[11]))

def ReadSystemStatus():
    """
    Returns the system options which are currently enabled at the Probe Station.
    Status: published
    ----------
    Response:
        Name:str
        System:str
        ChuckXY:int
        ChuckZ:int
        ChuckTheta:int
        ScopeXY:int
        ScopeZ:int
        EdgeSensor:int
        OperationalMode:str
        Turret:int
        TemperatureChuck:int
        AuxSiteCount:int
        PlatenXY:int
        PlatenZ:int
        LoaderGateState:str
        NucleusType:str
    ----------
    Command Timeout: 10000
    Example:ReadSystemStatus
    """
    rsp = MessageServerInterface.sendSciCommand("ReadSystemStatus")
    global ReadSystemStatus_Response
    if not "ReadSystemStatus_Response" in globals(): ReadSystemStatus_Response = namedtuple("ReadSystemStatus_Response", "Name,System,ChuckXY,ChuckZ,ChuckTheta,ScopeXY,ScopeZ,EdgeSensor,OperationalMode,Turret,TemperatureChuck,AuxSiteCount,PlatenXY,PlatenZ,LoaderGateState,NucleusType")
    return ReadSystemStatus_Response(str(rsp[0]),str(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]),int(rsp[7]),str(rsp[8]),int(rsp[9]),int(rsp[10]),int(rsp[11]),int(rsp[12]),int(rsp[13]),str(rsp[14]),str("" if len(rsp) < 16 else ' '.join(rsp[15:])))

def SetExternalMode(Mode=""):
    """
    If 'R' is sent, it sets the external mode of the Kernel. This disables most of
    the UI functions. Otherwise, this command re-enables all functions of the UI.
    Status: published
    ----------
    Parameters:
        Mode:str = "L"
    ----------
    Command Timeout: 5000
    Example:SetExternalMode L
    """
    MessageServerInterface.sendSciCommand("SetExternalMode",Mode)


def SetStageLock(Stage="", WantStageLock="", Application=""):
    """
    Enables or disables the stage lock functionality. Stages which are locked can't
    be moved in any way. If the joystick controller is locked, the display and the
    keys are deactivated. The name of the application can be stored by using the
    Application Name parameter and is shown in lock-caused error messages.
    Status: published
    ----------
    Parameters:
        Stage:str = "0"
        WantStageLock:int = 1
        Application:str = ""
    ----------
    Command Timeout: 10000
    Example:SetStageLock C 0 WaferMap
    """
    MessageServerInterface.sendSciCommand("SetStageLock",Stage,WantStageLock,Application)


def ReadSensor(Channel="", Type=""):
    """
    Returns the actual status of the specified input channel, output channel or edge
    sensor. The signal table is described in the Hardware Manual. Each used IO-board
    has 16 channels (max. 4 IO-boards are supported), what results in a domain of 64
    channel numbers. Beyond this range there are pseudo channels, which are used for
    special purposes. Pseudo channels: 65 - Edge sensor one; 66 - Edge sensor two
    Status: published
    ----------
    Parameters:
        Channel:int = 1
        Type:str = "Input"
    ----------
    Response:
        IsSensorOn:int
    ----------
    Command Timeout: 10000
    Example:ReadSensor 11 I
    """
    rsp = MessageServerInterface.sendSciCommand("ReadSensor",Channel,Type)
    return int(rsp[0])

def GetStageLock(Stage=""):
    """
    Reads whether stages or joystick controller are locked.
    Status: published
    ----------
    Parameters:
        Stage:str = "0"
    ----------
    Response:
        Locks:int
        Application:str
    ----------
    Command Timeout: 10000
    Example:GetStageLock C
    """
    rsp = MessageServerInterface.sendSciCommand("GetStageLock",Stage)
    global GetStageLock_Response
    if not "GetStageLock_Response" in globals(): GetStageLock_Response = namedtuple("GetStageLock_Response", "Locks,Application")
    return GetStageLock_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def SetBackSideMode(WantBackSideMode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command sets bottomside mode. In this mode the Z axis is reverse and the
    command MoveChuckLoad is not allowed.
    Status: internal
    ----------
    Parameters:
        WantBackSideMode:int = 0
    ----------
    Command Timeout: 5000
    Example:SetBackSideMode 1
    """
    MessageServerInterface.sendSciCommand("SetBackSideMode",WantBackSideMode)


def GetBackSideMode():
    """
    Returns the current side mode.
    Status: published
    ----------
    Response:
        IsBackSideModeOn:int
    ----------
    Command Timeout: 5000
    Example:GetBackSideMode
    """
    rsp = MessageServerInterface.sendSciCommand("GetBackSideMode")
    return int(rsp[0])

def SetDarkMode(WantSetDarkMode=""):
    """
    Switches off all LEDs on the station, on the Positioner and also the light of
    the cameras.
    Status: published
    ----------
    Parameters:
        WantSetDarkMode:int = 0
    ----------
    Command Timeout: 5000
    Example:SetDarkMode 1
    """
    MessageServerInterface.sendSciCommand("SetDarkMode",WantSetDarkMode)


def GetDarkMode():
    """
    Returns the current mode of the light sources.
    Status: published
    ----------
    Response:
        IsDarkMode:int
    ----------
    Command Timeout: 5000
    Example:GetDarkMode
    """
    rsp = MessageServerInterface.sendSciCommand("GetDarkMode")
    return int(rsp[0])

def DockChuckCamera(ConnectCamera="", Velocity=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Connect or disconnect the Chuck camera to the Chuck stage. The command is only
    available for the Prober type PA300BEP.
    Status: internal
    ----------
    Parameters:
        ConnectCamera:str = "ParkPos"
        Velocity:Decimal = 100
    ----------
    Command Timeout: 300000
    Example:DockChuckCamera P 75
    """
    MessageServerInterface.sendSciCommand("DockChuckCamera",ConnectCamera,Velocity)


def ReadCBoxStage():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the current selected stage of the joystick controller.
    Status: internal
    ----------
    Response:
        Stage:str
    ----------
    Command Timeout: 5000
    Example:ReadCBoxStage
    """
    rsp = MessageServerInterface.sendSciCommand("ReadCBoxStage")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetCBoxStage(Stage=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the current stage of the joystick controller.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
    ----------
    Command Timeout: 5000
    Example:SetCBoxStage C
    """
    MessageServerInterface.sendSciCommand("SetCBoxStage",Stage)


def ReadCBoxPosMonConf(Stage=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the current setting of the joystick controllers position monitor for the
    specified stage.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
    ----------
    Response:
        PosRef:str
        Unit:str
    ----------
    Command Timeout: 5000
    Example:ReadCBoxPosMonConf C
    """
    rsp = MessageServerInterface.sendSciCommand("ReadCBoxPosMonConf",Stage)
    global ReadCBoxPosMonConf_Response
    if not "ReadCBoxPosMonConf_Response" in globals(): ReadCBoxPosMonConf_Response = namedtuple("ReadCBoxPosMonConf_Response", "PosRef,Unit")
    return ReadCBoxPosMonConf_Response(str(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def SetCBoxPosMonConf(Stage="", PosRef="", Unit=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Configures the joystick controller position monitor for the specified stage.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        PosRef:str = "Zero"
        Unit:str = "Microns"
    ----------
    Command Timeout: 5000
    Example:SetCBoxPosMonConf C Z Y
    """
    MessageServerInterface.sendSciCommand("SetCBoxPosMonConf",Stage,PosRef,Unit)


def ReadCBoxCurrSpeed(Stage=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the current speed of the joystick controller for the specified stage.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
    ----------
    Response:
        CBoxSpeed:str
    ----------
    Command Timeout: 5000
    Example:ReadCBoxCurrSpeed C
    """
    rsp = MessageServerInterface.sendSciCommand("ReadCBoxCurrSpeed",Stage)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetCBoxCurrSpeed(Stage="", CBoxSpeed=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the current speed of the joystick controller for the specified stage.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        CBoxSpeed:str = "Speed4"
    ----------
    Command Timeout: 5000
    Example:SetCBoxCurrSpeed C 3
    """
    MessageServerInterface.sendSciCommand("SetCBoxCurrSpeed",Stage,CBoxSpeed)


def MoveChuckAsync(XValue="", YValue="", PosRef="", Unit="", Velocity="", Comp=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the Chuck stage to the specified X,Y position without waiting for the move
    to be finished If Chuck Z is in Contact Height or higher, the Chuck will drop to
    separation.
    Status: internal
    ----------
    Parameters:
        XValue:Decimal = 0
        YValue:Decimal = 0
        PosRef:str = "Home"
        Unit:str = "Microns"
        Velocity:Decimal = 100
        Comp:str = "Technology"
    ----------
    Command Timeout: 5000
    Example:MoveChuckAsync 5000. 5000. R Y 100
    """
    MessageServerInterface.sendSciCommand("MoveChuckAsync",XValue,YValue,PosRef,Unit,Velocity,Comp)


def MoveScopeAsync(XValue="", YValue="", PosRef="", Unit="", Velocity="", Comp=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the Scope stage to the specified X,Y position without waiting for the move
    to be finished.
    Status: internal
    ----------
    Parameters:
        XValue:Decimal = 0
        YValue:Decimal = 0
        PosRef:str = "Home"
        Unit:str = "Microns"
        Velocity:Decimal = 100
        Comp:str = "Technology"
    ----------
    Command Timeout: 5000
    Example:MoveScopeAsync 5000 5000 R Y 100
    """
    MessageServerInterface.sendSciCommand("MoveScopeAsync",XValue,YValue,PosRef,Unit,Velocity,Comp)


def MoveProbeAsync(Probe="", XValue="", YValue="", PosRef="", Unit="", Velocity="", Comp=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the probe stage to the specified X,Y position without waiting for the move
    to be finished.
    Status: internal
    ----------
    Parameters:
        Probe:int = 1
        XValue:Decimal = 0
        YValue:Decimal = 0
        PosRef:str = "Home"
        Unit:str = "Microns"
        Velocity:Decimal = 100
        Comp:str = "Technology"
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("MoveProbeAsync",Probe,XValue,YValue,PosRef,Unit,Velocity,Comp)
    return int(rsp[0])

def ReadChuckStatus():
    """
    Returns the current Chuck status. Every bit in the bit fields works like a
    boolean value: One &lt;1&gt; means true/on and zero &lt;0&gt; means false/off.
    Its counted from LSB to MSB.   - FlagsInit: X, Y, Z, Theta - FlagsMode:
    HasOvertravel, HasAutoZ, HasInterlock, ContactSearch, IsContactSet,
    EdgeInterlock, QuietContact, IsLocked - FlagsLimit: XHigh, XLow, YHigh, YLow,
    ZHigh, ZLow, ThetaHigh, ThetaLow - FlagsMoving: X, Y, Z, Theta  All parameters
    are provided as indirect access (e.g. first bit of M_pvecFlagsInit can be
    accessed by M_pbIsInitX).
    Status: published
    ----------
    Response:
        FlagsInit:int
        FlagsMode:int
        FlagsLimit:int
        FlagsMoving:int
        Comp:str
        IsVacuumOn:int
        PresetHeight:str
        LoadPos:str
        IsLiftDown:int
        CameraConnection:str
        IsQuiet:int
    ----------
    Command Timeout: 5000
    Example:ReadChuckStatus
    """
    rsp = MessageServerInterface.sendSciCommand("ReadChuckStatus")
    global ReadChuckStatus_Response
    if not "ReadChuckStatus_Response" in globals(): ReadChuckStatus_Response = namedtuple("ReadChuckStatus_Response", "FlagsInit,FlagsMode,FlagsLimit,FlagsMoving,Comp,IsVacuumOn,PresetHeight,LoadPos,IsLiftDown,CameraConnection,IsQuiet")
    return ReadChuckStatus_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),str(rsp[4]),int(rsp[5]),str(rsp[6]),str(rsp[7]),int(rsp[8]),str(rsp[9]),int(rsp[10]))

def ReadChuckPosition(Unit="", PosRef="", Comp=""):
    """
    Returns the current Chuck stage position in X, Y and Z.
    Status: published
    ----------
    Parameters:
        Unit:str = "Microns"
        PosRef:str = "Home"
        Comp:str = "Technology"
    ----------
    Response:
        X:Decimal
        Y:Decimal
        Z:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadChuckPosition Y Z
    """
    rsp = MessageServerInterface.sendSciCommand("ReadChuckPosition",Unit,PosRef,Comp)
    global ReadChuckPosition_Response
    if not "ReadChuckPosition_Response" in globals(): ReadChuckPosition_Response = namedtuple("ReadChuckPosition_Response", "X,Y,Z")
    return ReadChuckPosition_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def ReadChuckHeights(Unit=""):
    """
    Returns the current settings used for the Chuck Z movement. `Contact` is the
    contact-height from zero in Technology compensation. The other heights are
    relative to this. If no contact is set, the value will be -1.
    Status: published
    ----------
    Parameters:
        Unit:str = "Microns"
    ----------
    Response:
        Contact:Decimal
        Overtravel:Decimal
        AlignDist:Decimal
        SepDist:Decimal
        SearchGap:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadChuckHeights Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadChuckHeights",Unit)
    global ReadChuckHeights_Response
    if not "ReadChuckHeights_Response" in globals(): ReadChuckHeights_Response = namedtuple("ReadChuckHeights_Response", "Contact,Overtravel,AlignDist,SepDist,SearchGap")
    return ReadChuckHeights_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]))

def InitChuck(FlagsInit="", FlagsDirection="", FlagsMoveRange=""):
    """
    Machine Coordinate System: Chuck X Y Z Theta  - _FlagsInit_: X, Y, Z, Theta -
    _FlagsDirection_: X, Y, Z, Theta (true means plus direction) - _FlagsMoveRange_:
    X, Y, Z, Theta   All flags can be accessed by indirect members.  Initializes the
    Chuck stage and resets current coordinate system. Should be used only in cases
    when the reported coordinates do not correspond to real position of mechanics.
    Find Move Range starts the initialization in the defined direction and then
    moves to the other limit and finds the whole range of the axes.
    Status: published
    ----------
    Parameters:
        FlagsInit:int = 0
        FlagsDirection:int = 0
        FlagsMoveRange:int = 0
    ----------
    Command Timeout: 180000
    Example:InitChuck 7 0 0
    """
    MessageServerInterface.sendSciCommand("InitChuck",FlagsInit,FlagsDirection,FlagsMoveRange)


def MoveChuck(XValue="", YValue="", PosRef="", Unit="", Velocity="", Comp=""):
    """
    Moves the Chuck stage to the specified X,Y position. If Chuck Z is in Contact
    Height or higher, Interlock and Auto Z flags will be analyzed and stage will
    behave correspondingly - can move to separation first or return an error:
    Status: published
    ----------
    Parameters:
        XValue:Decimal = 0
        YValue:Decimal = 0
        PosRef:str = "Home"
        Unit:str = "Microns"
        Velocity:Decimal = 100
        Comp:str = "Technology"
    ----------
    Command Timeout: 30000
    Example:MoveChuck 5000. 5000. R Y 100
    """
    MessageServerInterface.sendSciCommand("MoveChuck",XValue,YValue,PosRef,Unit,Velocity,Comp)


def MoveChuckIndex(XSteps="", YSteps="", PosRef="", Velocity=""):
    """
    Moves the Chuck stage in index steps. This command modifies Die Home Position.
    Status: published
    ----------
    Parameters:
        XSteps:int = 0
        YSteps:int = 0
        PosRef:str = "Home"
        Velocity:Decimal = 100
    ----------
    Command Timeout: 30000
    Example:MoveChuckIndex 1 1 R 100
    """
    MessageServerInterface.sendSciCommand("MoveChuckIndex",XSteps,YSteps,PosRef,Velocity)


def MoveChuckSubsite(XValue="", YValue="", Unit="", Velocity=""):
    """
    Moves the Chuck stage to the specified X, Y sub-site position. Die home position
    is defined by destination position of last successful MoveChuck or
    MoveChuckIndex commands. MoveChuckVelocity does not touch die home position. If
    you have moved Chuck with MoveChuckVelocity, "MoveChuckSubsite 0 0" will move it
    back to die home position.
    Status: published
    ----------
    Parameters:
        XValue:Decimal = 0
        YValue:Decimal = 0
        Unit:str = "Microns"
        Velocity:Decimal = 100
    ----------
    Command Timeout: 30000
    Example:MoveChuckSubsite 200 200 Y 100
    """
    MessageServerInterface.sendSciCommand("MoveChuckSubsite",XValue,YValue,Unit,Velocity)


def MoveChuckContact(Velocity=""):
    """
    Performs a movement of Chuck Z axis to preset Contact Height or will return
    error if no Contact Height is set.
    Status: published
    ----------
    Parameters:
        Velocity:Decimal = 100
    ----------
    Command Timeout: 60000
    Example:MoveChuckContact 100
    """
    MessageServerInterface.sendSciCommand("MoveChuckContact",Velocity)


def MoveChuckAlign(Velocity=""):
    """
    Moves the Chuck Z axis to the align height. If no Contact height is set will
    return an error.
    Status: published
    ----------
    Parameters:
        Velocity:Decimal = 100
    ----------
    Command Timeout: 60000
    Example:MoveChuckAlign 100
    """
    MessageServerInterface.sendSciCommand("MoveChuckAlign",Velocity)


def MoveChuckSeparation(Velocity=""):
    """
    Moves the Chuck Z axis to the separation height. Returns error if no Contact
    height is set.
    Status: published
    ----------
    Parameters:
        Velocity:Decimal = 100
    ----------
    Command Timeout: 60000
    Example:MoveChuckSeparation 100
    """
    MessageServerInterface.sendSciCommand("MoveChuckSeparation",Velocity)


def MoveChuckLoad(LoadPosition=""):
    """
    Moves the Chuck stage in X, Y, Z and Theta to the load position.
    Status: published
    ----------
    Parameters:
        LoadPosition:str = "First"
    ----------
    Command Timeout: 90000
    Example:MoveChuckLoad 1
    """
    MessageServerInterface.sendSciCommand("MoveChuckLoad",LoadPosition)


def MoveChuckZ(Height="", PosRef="", Unit="", Velocity="", Comp=""):
    """
    Moves the Chuck Z axis to the specified height. If contact is set, only moves up
    to Contact Height will be allowed. If Overtravel is enabled - up to Overtravel
    height.
    Status: published
    ----------
    Parameters:
        Height:Decimal = 0
        PosRef:str = "Zero"
        Unit:str = "Microns"
        Velocity:Decimal = 100
        Comp:str = "Technology"
    ----------
    Command Timeout: 60000
    Example:MoveChuckZ 1000. R Y 67
    """
    MessageServerInterface.sendSciCommand("MoveChuckZ",Height,PosRef,Unit,Velocity,Comp)


def SearchChuckContact(Height="", PosRef="", Unit="", Velocity="", Comp="", NoFinalMoveToOvertravel=""):
    """
    Moves the Chuck Z axis to the specified height and sets contact. The move stops
    immediately if the Edge Sensor is triggered.   If no contact has been found and
    Contact Height was previously set, the previous Contact Height is kept but the
    Chuck will not move to it.   Typical Velocity values are < 5% and thus a
    velocity should always be set to avoid risk of probe damage.
    Status: published
    ----------
    Parameters:
        Height:Decimal = 100
        PosRef:str = "Relative"
        Unit:str = "Microns"
        Velocity:Decimal = 100
        Comp:str = "Technology"
        NoFinalMoveToOvertravel:int = 0
    ----------
    Response:
        ContactHeight:Decimal
    ----------
    Command Timeout: 60000
    Example:SearchChuckContact 1000 R Y 10 T 0
    """
    rsp = MessageServerInterface.sendSciCommand("SearchChuckContact",Height,PosRef,Unit,Velocity,Comp,NoFinalMoveToOvertravel)
    return Decimal(rsp[0])

def MoveChuckVelocity(PolarityX="", PolarityY="", PolarityZ="", VelocityX="", VelocityY="", VelocityZ=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the Chuck stage in velocity mode. The motion continues until the
    StopChuckMovement command is received, or the end limit is reached.
    Status: internal
    ----------
    Parameters:
        PolarityX:str = "Fixed"
        PolarityY:str = "Fixed"
        PolarityZ:str = "Fixed"
        VelocityX:Decimal = 100
        VelocityY:Decimal = 0
        VelocityZ:Decimal = 0
    ----------
    Command Timeout: 30000
    Example:MoveChuckVelocity + + 0 100 30 0
    """
    MessageServerInterface.sendSciCommand("MoveChuckVelocity",PolarityX,PolarityY,PolarityZ,VelocityX,VelocityY,VelocityZ)


def StopChuckMovement(FlagsStop=""):
    """
    Stops Chuck movement for the given axis. Notifications: 31 / 32 / 5
    Status: published
    ----------
    Parameters:
        FlagsStop:int = 15
    ----------
    Command Timeout: 5000
    Example:StopChuckMovement 7
    """
    MessageServerInterface.sendSciCommand("StopChuckMovement",FlagsStop)


def SetChuckMode(Overtravel="", AutoZ="", Interlock="", ContactSearch="", EdgeInterlock="", QuietContact=""):
    """
    Mode manages the way the Chuck behaves when it is in Contact Height. Chuck mode
    is made from 6 flags and you can control all of them using this command. Every
    flag can be turned on by using value 1 or turned off by using value 0. If you do
    not want to change a flag - use value of 2.
    Status: published
    ----------
    Parameters:
        Overtravel:int = 2
        AutoZ:int = 2
        Interlock:int = 2
        ContactSearch:int = 2
        EdgeInterlock:int = 2
        QuietContact:int = 2
    ----------
    Command Timeout: 5000
    Example:SetChuckMode 2 2 2 2 2 2
    """
    MessageServerInterface.sendSciCommand("SetChuckMode",Overtravel,AutoZ,Interlock,ContactSearch,EdgeInterlock,QuietContact)


def SetChuckHome(Mode="", Unit="", XValue="", YValue=""):
    """
    Sets wafer and die home position, which can be used later as coordinate system
    for movements.
    Status: published
    ----------
    Parameters:
        Mode:str = "0"
        Unit:str = "Microns"
        XValue:Decimal = 0
        YValue:Decimal = 0
    ----------
    Command Timeout: 5000
    Example:SetChuckHome 0 Y
    """
    MessageServerInterface.sendSciCommand("SetChuckHome",Mode,Unit,XValue,YValue)


def SetChuckIndex(XValue="", YValue="", Unit=""):
    """
    Sets the wafer index size. Normally the size of one die.
    Status: published
    ----------
    Parameters:
        XValue:Decimal = 0
        YValue:Decimal = 0
        Unit:str = "Microns"
    ----------
    Command Timeout: 5000
    Example:SetChuckIndex 5000. 5000. Y
    """
    MessageServerInterface.sendSciCommand("SetChuckIndex",XValue,YValue,Unit)


def SetChuckHeight(PresetHeight="", Mode="", Unit="", Value=""):
    """
    Defines the predefined Contact Height and corresponding gaps for Overtravel,
    align and separation. A predefined contact search gap is able to write. No data
    in the optional parameters sets contact height at current position. If Mode is
    '0', Contact Height can be set at current position. The levels O, A, S and T
    support no Mode '0'. If Mode is 'V' and no value for height is specified -
    default 0 will be used, what potentially can be not what you expect. If Mode is
    'R', Contact Height can be invalidated. The levels O, A, S and T support no Mode
    'R'.
    Status: published
    ----------
    Parameters:
        PresetHeight:str = "Contact"
        Mode:str = "0"
        Unit:str = "Microns"
        Value:Decimal = 0
    ----------
    Command Timeout: 5000
    Example:SetChuckHeight C V Y 5000.
    """
    MessageServerInterface.sendSciCommand("SetChuckHeight",PresetHeight,Mode,Unit,Value)


def ReadChuckIndex(Unit=""):
    """
    The command gets the current die size which is stored in the Kernel.
    Status: published
    ----------
    Parameters:
        Unit:str = "Microns"
    ----------
    Response:
        IndexX:Decimal
        IndexY:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadChuckIndex Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadChuckIndex",Unit)
    global ReadChuckIndex_Response
    if not "ReadChuckIndex_Response" in globals(): ReadChuckIndex_Response = namedtuple("ReadChuckIndex_Response", "IndexX,IndexY")
    return ReadChuckIndex_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def MoveChuckTransfer():
    """
    Moves the Chuck to the Transfer Position. If the movement starts in Load
    Position (where it's possible to pull out the Chuck) the handling of the Add On
    Platen or the Pin Chuck is integrated.
    Status: published
    ----------
    Command Timeout: 90000
    Example:MoveChuckTransfer
    """
    MessageServerInterface.sendSciCommand("MoveChuckTransfer")


def MoveChuckLift(SetLift=""):
    """
    Moves the Chuck to the upper (0) or lower = lifted (1) position. This initiates
    motion only, the actual movement may take some seconds.
    Status: published
    ----------
    Parameters:
        SetLift:int = 1
    ----------
    Command Timeout: 10000
    Example:MoveChuckLift 1
    """
    MessageServerInterface.sendSciCommand("MoveChuckLift",SetLift)


def SetChuckThermoScale(ScaleX="", ScaleY=""):
    """
    Thermal drifts of the wafer will be compensated. The compensation is not
    persistent, (power off - this compensation is deleted). The algorithm works as
    an additional one.  This is for an iterative usage, so:  1. `ResetProber H` 2.
    `SetChuckThermoScale 1.5 1.5` 3. `SetChuckThermoScale 1.5 1.5`  will result in a
    scale of 2.25 in both directions. The thermal scale can also be reset using the
    command 'SetChuckThermoValue 20 C'
    Status: published
    ----------
    Parameters:
        ScaleX:Decimal = 1
        ScaleY:Decimal = 1
    ----------
    Command Timeout: 5000
    Example:SetChuckThermoScale 1.000005 1.0000045
    """
    MessageServerInterface.sendSciCommand("SetChuckThermoScale",ScaleX,ScaleY)


def ReadChuckThermoScale():
    """
    Read the linear scaling value of the Chuck.
    Status: published
    ----------
    Response:
        ScaleX:Decimal
        ScaleY:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadChuckThermoScale
    """
    rsp = MessageServerInterface.sendSciCommand("ReadChuckThermoScale")
    global ReadChuckThermoScale_Response
    if not "ReadChuckThermoScale_Response" in globals(): ReadChuckThermoScale_Response = namedtuple("ReadChuckThermoScale_Response", "ScaleX,ScaleY")
    return ReadChuckThermoScale_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def SetChuckThermoValue(Temperature="", Unit="", ExpCoeffX="", ExpCoeffY=""):
    """
    Set a temperature and optional the expansion coefficient. The temperature for
    normal level is 20 degree. The scaling factor at this temperature is 1.0. If you
    set the temperature directly the controller calculates the stage difference in
    the coordinate system. For the calculation use the set coefficient of expansion
    from the controller. The default coefficient of expansion is based on silicon:
    2.33E-06 1/K.
    Status: published
    ----------
    Parameters:
        Temperature:Decimal = 0
        Unit:str = "Celsius"
        ExpCoeffX:Decimal = 0
        ExpCoeffY:Decimal = 0
    ----------
    Command Timeout: 5000
    Example:SetChuckThermoValue 250 C 2.43 2.32
    """
    MessageServerInterface.sendSciCommand("SetChuckThermoValue",Temperature,Unit,ExpCoeffX,ExpCoeffY)


def ReadChuckThermoValue(Unit=""):
    """
    Read the current temperature (either set or calculated) for the thermal scaling.
    With SetChuckThermoScale in use, the value will be calculated by the current
    scale and the expansion factor of silicon. The temperature that is read with
    this command is not identical to the current Chuck temperature.
    Status: published
    ----------
    Parameters:
        Unit:str = "Celsius"
    ----------
    Response:
        Temperature:Decimal
        ExpCoeffX:Decimal
        ExpCoeffY:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadChuckThermoValue C
    """
    rsp = MessageServerInterface.sendSciCommand("ReadChuckThermoValue",Unit)
    global ReadChuckThermoValue_Response
    if not "ReadChuckThermoValue_Response" in globals(): ReadChuckThermoValue_Response = namedtuple("ReadChuckThermoValue_Response", "Temperature,ExpCoeffX,ExpCoeffY")
    return ReadChuckThermoValue_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def GetChuckTableID(TableName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Return the TableID Number of the stored Chuck table or create a new table. The
    ID Number is unique for the name and the Chuck. The table itself has a string
    name, this name is not case sensitive. This command has to be used before all
    other table commands can be used. Accesses to the table is possible only with an
    ID Number (name dependent).
    Status: internal
    ----------
    Parameters:
        TableName:str = "ChuckTable"
    ----------
    Response:
        TableID:int
    ----------
    Command Timeout: 5000
    Example:GetChuckTableID ChuckTable
    """
    rsp = MessageServerInterface.sendSciCommand("GetChuckTableID",TableName)
    return int(rsp[0])

def MoveChuckTablePoint(TableID="", PointID="", Velocity=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Move the Chuck to the next stored table site.
    Status: internal
    ----------
    Parameters:
        TableID:int = 0
        PointID:int = 0
        Velocity:Decimal = 100
    ----------
    Command Timeout: 30000
    Example:MoveChuckTablePoint 3 10 67
    """
    MessageServerInterface.sendSciCommand("MoveChuckTablePoint",TableID,PointID,Velocity)


def ReadChuckTablePoint(TableID="", PointID="", Unit=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Read back the table site information for this point from the Kernel.
    Status: internal
    ----------
    Parameters:
        TableID:int = 0
        PointID:int = 0
        Unit:str = "Microns"
    ----------
    Response:
        CoordX:Decimal
        CoordY:Decimal
        CoordSystem:str
    ----------
    Command Timeout: 5000
    Example:ReadChuckTablePoint 10 250 Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadChuckTablePoint",TableID,PointID,Unit)
    global ReadChuckTablePoint_Response
    if not "ReadChuckTablePoint_Response" in globals(): ReadChuckTablePoint_Response = namedtuple("ReadChuckTablePoint_Response", "CoordX,CoordY,CoordSystem")
    return ReadChuckTablePoint_Response(Decimal(rsp[0]),Decimal(rsp[1]),str("" if len(rsp) < 3 else ' '.join(rsp[2:])))

def SetChuckTablePoint(TableID="", PointID="", CoordX="", CoordY="", Unit="", CoordSystem=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Set one point of the Chuck table inside of the Kernel. If there is still a point
    with this index loaded, the Kernel returns an error. Number of positions and
    number of tables are dependent on the internal memory. All positions are stored
    persistent, that means after switching power on or off the positions are still
    available. The table starts with point number 1 and ends with the ID 16. The
    table can contain 65535 points with the ID 0 up to 65534. Overwriting of
    position points is not possible. The point has to be deleted before other values
    are set.
    Status: internal
    ----------
    Parameters:
        TableID:int = 0
        PointID:int = 0
        CoordX:Decimal = 0
        CoordY:Decimal = 0
        Unit:str = "Microns"
        CoordSystem:str = "HomeSystem"
    ----------
    Response:
        ValidPoint:int
    ----------
    Command Timeout: 5000
    Example:SetChuckTablePoint 10 12000.0 2344.0 Y F
    """
    rsp = MessageServerInterface.sendSciCommand("SetChuckTablePoint",TableID,PointID,CoordX,CoordY,Unit,CoordSystem)
    return int(rsp[0])

def ClearChuckTablePoint(TableID="", StartPoint="", EndPoint=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Clear one or a range of Chuck table site points in the in the Kernel. If Start
    Point is -1 or negative the whole table will be deleted.
    Status: internal
    ----------
    Parameters:
        TableID:int = 0
        StartPoint:int = -1
        EndPoint:int = 0
    ----------
    Response:
        ClearNumber:int
        ValidNumber:int
    ----------
    Command Timeout: 5000
    Example:ClearChuckTablePoint 5 10 15
    """
    rsp = MessageServerInterface.sendSciCommand("ClearChuckTablePoint",TableID,StartPoint,EndPoint)
    global ClearChuckTablePoint_Response
    if not "ClearChuckTablePoint_Response" in globals(): ClearChuckTablePoint_Response = namedtuple("ClearChuckTablePoint_Response", "ClearNumber,ValidNumber")
    return ClearChuckTablePoint_Response(int(rsp[0]),int(rsp[1]))

def AttachAmbientWafer(MoveTimeMs=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command is moved to slowly attach a wafer that is at ambient temperature while
    the Chuck is hot.   The command acts similar to MoveChuckTransfer when moving
    out of Load 2 but will use a much slower Z velocity.   This is only supported
    for BnR/ACS stations (CM300 and SUMMIT200) at the moment.
    Status: internal
    ----------
    Parameters:
        MoveTimeMs:Decimal = 30000
    ----------
    Command Timeout: 300000
    Example:AttachAmbientWafer
    """
    MessageServerInterface.sendSciCommand("AttachAmbientWafer",MoveTimeMs)


def ReadThetaStatus():
    """
    Returns the actual status of the Chuck Theta axis.
    Status: published
    ----------
    Response:
        IsInit:int
        FlagsLimit:int
        IsMoving:int
    ----------
    Command Timeout: 5000
    Example:ReadThetaStatus
    """
    rsp = MessageServerInterface.sendSciCommand("ReadThetaStatus")
    global ReadThetaStatus_Response
    if not "ReadThetaStatus_Response" in globals(): ReadThetaStatus_Response = namedtuple("ReadThetaStatus_Response", "IsInit,FlagsLimit,IsMoving")
    return ReadThetaStatus_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]))

def ReadThetaPosition(Unit="", PosRef=""):
    """
    Returns the actual Theta position.
    Status: published
    ----------
    Parameters:
        Unit:str = "Degrees"
        PosRef:str = "Home"
    ----------
    Response:
        Position:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadThetaPosition D Z
    """
    rsp = MessageServerInterface.sendSciCommand("ReadThetaPosition",Unit,PosRef)
    return Decimal(rsp[0])

def InitTheta(FlagsDoPlus="", FlagsMoveRange=""):
    """
    Performs an initialization move and resets the coordinate system of the Theta
    axis.
    Status: published
    ----------
    Parameters:
        FlagsDoPlus:int = 0
        FlagsMoveRange:int = 0
    ----------
    Command Timeout: 120000
    Example:InitTheta 0 0
    """
    MessageServerInterface.sendSciCommand("InitTheta",FlagsDoPlus,FlagsMoveRange)


def MoveTheta(Position="", PosRef="", Unit="", Velocity=""):
    """
    Moves the Chuck Theta axis to the specified position. The positive direction is
    counter-clockwise.
    Status: published
    ----------
    Parameters:
        Position:Decimal = 0
        PosRef:str = "Home"
        Unit:str = "Degrees"
        Velocity:Decimal = 100
    ----------
    Command Timeout: 30000
    Example:MoveTheta 1000. R E
    """
    MessageServerInterface.sendSciCommand("MoveTheta",Position,PosRef,Unit,Velocity)


def MoveThetaVelocity(Polarity="", Velocity=""):
    """
    Moves the Chuck Theta axis in velocity mode. The positive direction is counter-
    clockwise. The motion continues until the StopThetaMovement command is received,
    or the end limit (error condition) is reached. This command is mostly used for
    joystick movements that do not have a target destination.
    Status: published
    ----------
    Parameters:
        Polarity:str = "Fixed"
        Velocity:Decimal = 0
    ----------
    Command Timeout: 240000
    Example:MoveThetaVelocity + 67
    """
    MessageServerInterface.sendSciCommand("MoveThetaVelocity",Polarity,Velocity)


def StopThetaMovement():
    """
    Stops any type (velocity, position etc.) of Chuck Theta axis movement. This is
    treated as a smooth stop rather than an emergency stop.
    Status: published
    ----------
    Command Timeout: 5000
    Example:StopThetaMovement
    """
    MessageServerInterface.sendSciCommand("StopThetaMovement")


def SetThetaHome(Mode="", Unit="", Position=""):
    """
    Sets the Chuck Theta position to home. This position is usable as reference
    position for other commands.
    Status: published
    ----------
    Parameters:
        Mode:str = "0"
        Unit:str = "Degrees"
        Position:Decimal = 0
    ----------
    Command Timeout: 5000
    Example:SetThetaHome 0
    """
    MessageServerInterface.sendSciCommand("SetThetaHome",Mode,Unit,Position)


def ScanChuckZ(ZDistance="", TriggerEveryNthCycle="", Velocity=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Starts moving the Chuck from the current position with Velocity [%] over
    ZDistance (sign is important, as a negative sign will move Chuck down during
    scan) - Predefined camera trigger pulses (TTL active high for at least 5us) will
    be sent during the scan every passed number of BnR cycles (800us per cycle)
    until the ZDistance has been reached.  Command returns number of positions and
    all compensated Z Positions from Zero, where the trigger was sent.
    Status: internal
    ----------
    Parameters:
        ZDistance:Decimal = 1000
        TriggerEveryNthCycle:int = 3
        Velocity:Decimal = 10
    ----------
    Response:
        NumberOfPositions:int
        TriggerPositions:str
    ----------
    Command Timeout: 60000
    Example:ScanChuckZ 300 3 1.5
    """
    rsp = MessageServerInterface.sendSciCommand("ScanChuckZ",ZDistance,TriggerEveryNthCycle,Velocity)
    global ScanChuckZ_Response
    if not "ScanChuckZ_Response" in globals(): ScanChuckZ_Response = namedtuple("ScanChuckZ_Response", "NumberOfPositions,TriggerPositions")
    return ScanChuckZ_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def MoveChuckZSafe():
    """
    Moves the Chuck Z axis to a z height considered safe. This is either the lower
    Z-Fence or the Kernel item Chuck:SafeTransferHeight (whichever is larger)
    Status: published
    ----------
    Command Timeout: 60000
    Example:MoveChuckZSafe
    """
    MessageServerInterface.sendSciCommand("MoveChuckZSafe")


def ReadManualPlatenState():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Reads the current status of the manual platen.
    Status: internal
    ----------
    Response:
        IsUp:int
        IsDown:int
        IsSafe:int
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("ReadManualPlatenState")
    global ReadManualPlatenState_Response
    if not "ReadManualPlatenState_Response" in globals(): ReadManualPlatenState_Response = namedtuple("ReadManualPlatenState_Response", "IsUp,IsDown,IsSafe")
    return ReadManualPlatenState_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]))

def ReadScopeStatus():
    """
    Returns the current Scope status.
    Status: published
    ----------
    Response:
        FlagsInit:int
        FlagsLimit:int
        FlagsMoving:int
        Comp:str
        IsScopeLiftUp:int
        PresetHeight:str
        IsScopeLight:int
        FlagsMode:int
        IsQuiet:int
    ----------
    Command Timeout: 5000
    Example:ReadScopeStatus
    """
    rsp = MessageServerInterface.sendSciCommand("ReadScopeStatus")
    global ReadScopeStatus_Response
    if not "ReadScopeStatus_Response" in globals(): ReadScopeStatus_Response = namedtuple("ReadScopeStatus_Response", "FlagsInit,FlagsLimit,FlagsMoving,Comp,IsScopeLiftUp,PresetHeight,IsScopeLight,FlagsMode,IsQuiet")
    return ReadScopeStatus_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),str(rsp[3]),int(rsp[4]),str(rsp[5]),int(rsp[6]),int(rsp[7]),int(rsp[8]))

def ReadScopePosition(Unit="", PosRef="", Comp=""):
    """
    Returns the actual Scope stage position in X, Y and Z. The Technology
    Compensation Mode is the currently activated compensation mode of the Kernel.
    Status: published
    ----------
    Parameters:
        Unit:str = "Microns"
        PosRef:str = "Home"
        Comp:str = "Technology"
    ----------
    Response:
        X:Decimal
        Y:Decimal
        Z:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadScopePosition Y Z
    """
    rsp = MessageServerInterface.sendSciCommand("ReadScopePosition",Unit,PosRef,Comp)
    global ReadScopePosition_Response
    if not "ReadScopePosition_Response" in globals(): ReadScopePosition_Response = namedtuple("ReadScopePosition_Response", "X,Y,Z")
    return ReadScopePosition_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def ReadScopeHeights(Unit=""):
    """
    Returns the actual settings of the focus height, align gap and separation gap
    for the Scope Z axis.
    Status: published
    ----------
    Parameters:
        Unit:str = "Microns"
    ----------
    Response:
        FocusHeight:Decimal
        AlignDist:Decimal
        SepDist:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadScopeHeights Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadScopeHeights",Unit)
    global ReadScopeHeights_Response
    if not "ReadScopeHeights_Response" in globals(): ReadScopeHeights_Response = namedtuple("ReadScopeHeights_Response", "FocusHeight,AlignDist,SepDist")
    return ReadScopeHeights_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def InitScope(FlagsInit="", FlagsDirection="", FlagsMoveRange=""):
    """
    Initializes the microscope stage in X, Y and Z. The Axis default is all axes and
    the Direction default is XY in minus and Z in plus. Should be used only in cases
    when the reported coordinates do not correspond to real position of mechanics.
    Find Move Range starts the initialization in the defined direction and then
    moves to the other limit and finds the whole range of the axes.
    Status: published
    ----------
    Parameters:
        FlagsInit:int = 0
        FlagsDirection:int = 0
        FlagsMoveRange:int = 0
    ----------
    Command Timeout: 240000
    Example:InitScope 3 0 0
    """
    MessageServerInterface.sendSciCommand("InitScope",FlagsInit,FlagsDirection,FlagsMoveRange)


def MoveScope(XValue="", YValue="", PosRef="", Unit="", Velocity="", Comp=""):
    """
    Moves the microscope stage to the specified X,Y position relative to the per
    PosRef specified reference position.
    Status: published
    ----------
    Parameters:
        XValue:Decimal = 0
        YValue:Decimal = 0
        PosRef:str = "Home"
        Unit:str = "Microns"
        Velocity:Decimal = 100
        Comp:str = "Technology"
    ----------
    Command Timeout: 70000
    Example:MoveScope 5000 5000 R Y 100
    """
    MessageServerInterface.sendSciCommand("MoveScope",XValue,YValue,PosRef,Unit,Velocity,Comp)


def MoveScopeIndex(XSteps="", YSteps="", PosRef="", Velocity=""):
    """
    Moves the microscope stage in index steps. If no PositionReference byte is
    passed the Scope will step relative to the wafer home position. ('R' means the
    step relative to current position).
    Status: published
    ----------
    Parameters:
        XSteps:int = 0
        YSteps:int = 0
        PosRef:str = "Home"
        Velocity:Decimal = 100
    ----------
    Command Timeout: 30000
    Example:MoveScopeIndex 1 1 R 100
    """
    MessageServerInterface.sendSciCommand("MoveScopeIndex",XSteps,YSteps,PosRef,Velocity)


def MoveScopeZ(Height="", PosRef="", Unit="", Velocity="", Comp=""):
    """
    Moves the microscope Z axis to the specified height. Default velocity is 100%.
    Status: published
    ----------
    Parameters:
        Height:Decimal = 0
        PosRef:str = "Zero"
        Unit:str = "Microns"
        Velocity:Decimal = 100
        Comp:str = "Technology"
    ----------
    Command Timeout: 120000
    Example:MoveScopeZ 1000. R Y 67
    """
    MessageServerInterface.sendSciCommand("MoveScopeZ",Height,PosRef,Unit,Velocity,Comp)


def SetScopeMode(QuietMode="", FollowMode=""):
    """
    Scope mode is made up of two flags which can be controlled using this command.
    Each flag can be turned on by using value 1 or turned off by using value 0. If
    you do not want to change a flag, use value of 2.
    Status: published
    ----------
    Parameters:
        QuietMode:int = 2
        FollowMode:int = 2
    ----------
    Command Timeout: 5000
    Example:SetScopeMode 2 2
    """
    MessageServerInterface.sendSciCommand("SetScopeMode",QuietMode,FollowMode)


def MoveScopeVelocity(PolarityX="", PolarityY="", PolarityZ="", VelocityX="", VelocityY="", VelocityZ=""):
    """
    Moves the microscope stage in velocity mode. The motion continues until the
    StopScopeMovement command is received, or the end limit (error condition) is
    reached. Axes parameter: '+' move this axis in plus direction '-' move this axis
    in minus direction '0' Do not change this axis
    Status: published
    ----------
    Parameters:
        PolarityX:str = "Fixed"
        PolarityY:str = "Fixed"
        PolarityZ:str = "Fixed"
        VelocityX:Decimal = 100
        VelocityY:Decimal = 0
        VelocityZ:Decimal = 0
    ----------
    Command Timeout: 30000
    Example:MoveScopeVelocity + + 0 67 100 0
    """
    MessageServerInterface.sendSciCommand("MoveScopeVelocity",PolarityX,PolarityY,PolarityZ,VelocityX,VelocityY,VelocityZ)


def StopScopeMovement(FlagsStop=""):
    """
    Stops Scope movement for the given axis. A smooth stop is executed, no emergency
    stop.
    Status: published
    ----------
    Parameters:
        FlagsStop:int = 7
    ----------
    Command Timeout: 5000
    Example:StopScopeMovement 7
    """
    MessageServerInterface.sendSciCommand("StopScopeMovement",FlagsStop)


def SetScopeHome(Mode="", Unit="", XValue="", YValue=""):
    """
    Sets the Scope Home position in X and Y. It identifies the Scope coordinate
    system for later movements. Usually this position is identical to the die home
    location.
    Status: published
    ----------
    Parameters:
        Mode:str = "0"
        Unit:str = "Microns"
        XValue:Decimal = 0
        YValue:Decimal = 0
    ----------
    Command Timeout: 5000
    Example:SetScopeHome 0 Y
    """
    MessageServerInterface.sendSciCommand("SetScopeHome",Mode,Unit,XValue,YValue)


def SetScopeIndex(XValue="", YValue="", Unit=""):
    """
    Sets the microscope index size. Normally set in relation to the wafer index
    size.
    Status: published
    ----------
    Parameters:
        XValue:Decimal = 0
        YValue:Decimal = 0
        Unit:str = "Microns"
    ----------
    Command Timeout: 5000
    Example:SetScopeIndex 5000. 5000. Y
    """
    MessageServerInterface.sendSciCommand("SetScopeIndex",XValue,YValue,Unit)


def SetScopeHeight(PresetHeight="", Mode="", Unit="", Value=""):
    """
    This command defines Scope focus height and the corresponding gaps for alignment
    or separation. No data sets focus height at current position.
    Status: published
    ----------
    Parameters:
        PresetHeight:str = "Focus"
        Mode:str = "0"
        Unit:str = "Microns"
        Value:Decimal = 0
    ----------
    Command Timeout: 5000
    Example:SetScopeHeight F 0 Y
    """
    MessageServerInterface.sendSciCommand("SetScopeHeight",PresetHeight,Mode,Unit,Value)


def ReadScopeIndex(Unit=""):
    """
    Returns the actual Scope stage index values in X and Y.
    Status: published
    ----------
    Parameters:
        Unit:str = "Microns"
    ----------
    Response:
        IndexX:Decimal
        IndexY:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadScopeIndex Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadScopeIndex",Unit)
    global ReadScopeIndex_Response
    if not "ReadScopeIndex_Response" in globals(): ReadScopeIndex_Response = namedtuple("ReadScopeIndex_Response", "IndexX,IndexY")
    return ReadScopeIndex_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def MoveScopeFocus(Velocity=""):
    """
    Moves the microscope stage to the specified X,Y position relative to the per
    PosRef specified reference position.
    Status: published
    ----------
    Parameters:
        Velocity:Decimal = 100
    ----------
    Command Timeout: 25000
    Example:MoveScopeFocus 100
    """
    MessageServerInterface.sendSciCommand("MoveScopeFocus",Velocity)


def MoveScopeAlign(Velocity=""):
    """
    Moves the Scope Z axis to the alignment height. If no focus height is set an
    error will be returned.
    Status: published
    ----------
    Parameters:
        Velocity:Decimal = 100
    ----------
    Command Timeout: 25000
    Example:MoveScopeAlign 100
    """
    MessageServerInterface.sendSciCommand("MoveScopeAlign",Velocity)


def MoveScopeSeparation(Velocity=""):
    """
    Moves the Scope Z axis to the separation height. Returns an error if no focus
    height is set.
    Status: published
    ----------
    Parameters:
        Velocity:Decimal = 100
    ----------
    Command Timeout: 60000
    Example:MoveScopeSeparation 100
    """
    MessageServerInterface.sendSciCommand("MoveScopeSeparation",Velocity)


def MoveScopeLift(SetLift=""):
    """
    Moves the microscope lift to the lower (0) or upper = lifted (1) position. This
    initiates the motion only, the actual movement may take some seconds.
    Status: published
    ----------
    Parameters:
        SetLift:int = 1
    ----------
    Command Timeout: 10000
    Example:MoveScopeLift 1
    """
    MessageServerInterface.sendSciCommand("MoveScopeLift",SetLift)


def ReadTurretStatus():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the current status of the motorized turret.
    Status: internal
    ----------
    Response:
        IsMoving:int
    ----------
    Command Timeout: 5000
    Example:ReadTurretStatus
    """
    rsp = MessageServerInterface.sendSciCommand("ReadTurretStatus")
    return int(rsp[0])

def SelectLens(Lens=""):
    """
    Parfocality and parcentricity are adjusted according to the stored values. This
    can be used with manual turrets to compensate for XYZ differences between
    lenses.
    Status: published
    ----------
    Parameters:
        Lens:int = 1
    ----------
    Command Timeout: 30000
    Example:SelectLens 1
    """
    MessageServerInterface.sendSciCommand("SelectLens",Lens)


def GetScopeTable(TableName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Return the TableID Number of the stored Chuck table or create a new table. The
    ID Number is unique for the name and the Chuck. The table itself has a string
    name, this name is not case sensitive. This command has to be used before all
    other table commands can be used. Accesses to the table is possible only with an
    ID Number (name dependet).
    Status: internal
    ----------
    Parameters:
        TableName:str = "ScopeTable"
    ----------
    Response:
        TableID:int
    ----------
    Command Timeout: 5000
    Example:GetScopeTable ScopeTable
    """
    rsp = MessageServerInterface.sendSciCommand("GetScopeTable",TableName)
    return int(rsp[0])

def MoveScopeTablePoint(TableID="", PointID="", Velocity=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the microscope stage to the specified X,Y position relative to the per
    PosRef specified reference position.
    Status: internal
    ----------
    Parameters:
        TableID:int = 0
        PointID:int = 0
        Velocity:Decimal = 100
    ----------
    Command Timeout: 30000
    Example:MoveScopeTablePoint 10 5 67
    """
    MessageServerInterface.sendSciCommand("MoveScopeTablePoint",TableID,PointID,Velocity)


def ReadScopeTablePoint(TableID="", PointID="", Unit=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Read back the Scope table site Information for this point from the Kernel.
    Status: internal
    ----------
    Parameters:
        TableID:int = 0
        PointID:int = 0
        Unit:str = "Microns"
    ----------
    Response:
        CoordX:Decimal
        CoordY:Decimal
        CoordSystem:str
    ----------
    Command Timeout: 5000
    Example:ReadScopeTablePoint 2 10 Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadScopeTablePoint",TableID,PointID,Unit)
    global ReadScopeTablePoint_Response
    if not "ReadScopeTablePoint_Response" in globals(): ReadScopeTablePoint_Response = namedtuple("ReadScopeTablePoint_Response", "CoordX,CoordY,CoordSystem")
    return ReadScopeTablePoint_Response(Decimal(rsp[0]),Decimal(rsp[1]),str("" if len(rsp) < 3 else ' '.join(rsp[2:])))

def ReadCurrentLens():
    """
    Returns the number of the current microscope lens.
    Status: published
    ----------
    Response:
        Lens:int
    ----------
    Command Timeout: 5000
    Example:ReadCurrentLens
    """
    rsp = MessageServerInterface.sendSciCommand("ReadCurrentLens")
    return int(rsp[0])

def SetScopeTablePoint(TableID="", PointID="", CoordX="", CoordY="", Unit="", CoordSystem=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Set one point of the Scope table inside of the Kernel. If there is still a point
    with this index loaded, the Kernel returns an error. Number of positions and
    number of tables are dependent on the internal memory. All positions are stored
    persistent, that means after switching power on or off the positions are still
    available. The table starts with point number 1 and ends with the ID 16. The
    table can contain 65535 points with the ID 0 up to 65534. Overwriting of
    position points is not possible. The point has to be deleted before other values
    are set.
    Status: internal
    ----------
    Parameters:
        TableID:int = 0
        PointID:int = 0
        CoordX:Decimal = 0
        CoordY:Decimal = 0
        Unit:str = "Microns"
        CoordSystem:str = "HomeSystem"
    ----------
    Response:
        ValidPoint:int
    ----------
    Command Timeout: 5000
    Example:SetScopeTablePoint 10 10 8992.5 7883.0 Y H
    """
    rsp = MessageServerInterface.sendSciCommand("SetScopeTablePoint",TableID,PointID,CoordX,CoordY,Unit,CoordSystem)
    return int(rsp[0])

def ClearScopeTablePoint(TableID="", StartPoint="", EndPoint=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Clear one or a range of Scope table site points in the Kernel. If Start Point is
    -1 or negative the whole table will be deleted.
    Status: internal
    ----------
    Parameters:
        TableID:int = 0
        StartPoint:int = -1
        EndPoint:int = 0
    ----------
    Response:
        ClearNumber:int
        ValidNumber:int
    ----------
    Command Timeout: 5000
    Example:ClearScopeTablePoint 2 10 15
    """
    rsp = MessageServerInterface.sendSciCommand("ClearScopeTablePoint",TableID,StartPoint,EndPoint)
    global ClearScopeTablePoint_Response
    if not "ClearScopeTablePoint_Response" in globals(): ClearScopeTablePoint_Response = namedtuple("ClearScopeTablePoint_Response", "ClearNumber,ValidNumber")
    return ClearScopeTablePoint_Response(int(rsp[0]),int(rsp[1]))

def ReadScopeSiloCount():
    """
    Returns the number of silos in the Scope fence. Will be zero if no silos are
    configured.
    Status: published
    ----------
    Response:
        Count:int
    ----------
    Command Timeout: 5000
    Example:ReadScopeSiloCount
    """
    rsp = MessageServerInterface.sendSciCommand("ReadScopeSiloCount")
    return int(rsp[0])

def ReadProbeStatus(Probe=""):
    """
    Returns the current Positioner's status.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
    ----------
    Response:
        ProbeEcho:int
        FlagsInit:int
        FlagsMode:int
        FlagsLimit:int
        FlagsMoving:int
        Comp:str
        Side:str
        PresetHeight:str
        IsLiftUp:int
        IsQuiet:int
    ----------
    Command Timeout: 5000
    Example:ReadProbeStatus 1
    """
    rsp = MessageServerInterface.sendSciCommand("ReadProbeStatus",Probe)
    global ReadProbeStatus_Response
    if not "ReadProbeStatus_Response" in globals(): ReadProbeStatus_Response = namedtuple("ReadProbeStatus_Response", "ProbeEcho,FlagsInit,FlagsMode,FlagsLimit,FlagsMoving,Comp,Side,PresetHeight,IsLiftUp,IsQuiet")
    return ReadProbeStatus_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),str(rsp[5]),str(rsp[6]),str(rsp[7]),int(rsp[8]),int(rsp[9]))

def ReadProbePosition(Probe="", Unit="", PosRef="", Comp=""):
    """
    Returns the actual Positioner's position in X, Y and Z. The Technology
    Compensation Mode is the currently activated compensation mode of the Kernel.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Unit:str = "Microns"
        PosRef:str = "Home"
        Comp:str = "Technology"
    ----------
    Response:
        ProbeEcho:int
        X:Decimal
        Y:Decimal
        Z:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadProbePosition 1 Y Z
    """
    rsp = MessageServerInterface.sendSciCommand("ReadProbePosition",Probe,Unit,PosRef,Comp)
    global ReadProbePosition_Response
    if not "ReadProbePosition_Response" in globals(): ReadProbePosition_Response = namedtuple("ReadProbePosition_Response", "ProbeEcho,X,Y,Z")
    return ReadProbePosition_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]))

def ReadProbeHeights(Probe="", Unit=""):
    """
    Returns the actual settings for the probe Z movement.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Unit:str = "Microns"
    ----------
    Response:
        ProbeEcho:int
        Contact:Decimal
        Overtravel:Decimal
        AlignDist:Decimal
        SepDist:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadProbeHeights 1 Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadProbeHeights",Probe,Unit)
    global ReadProbeHeights_Response
    if not "ReadProbeHeights_Response" in globals(): ReadProbeHeights_Response = namedtuple("ReadProbeHeights_Response", "ProbeEcho,Contact,Overtravel,AlignDist,SepDist")
    return ReadProbeHeights_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]))

def OrientProbe(Probe="", Side=""):
    """
    Defines the orientation of the Positioner's coordinate system and turns the
    Y-axis of the probe coordinate system.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Side:str = "Left"
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 5000
    Example:OrientProbe 1 R
    """
    rsp = MessageServerInterface.sendSciCommand("OrientProbe",Probe,Side)
    return int(rsp[0])

def InitProbe(Probe="", FlagsInit="", FlagsDirection="", FlagsMoveRange="", FlagsInitInPlace=""):
    """
    Performs an initialization move and resets the coordinate system of the given
    Positioner.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        FlagsInit:int = 0
        FlagsDirection:int = 0
        FlagsMoveRange:int = 0
        FlagsInitInPlace:int = 0
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 240000
    Example:InitProbe 1 7 0 0
    """
    rsp = MessageServerInterface.sendSciCommand("InitProbe",Probe,FlagsInit,FlagsDirection,FlagsMoveRange,FlagsInitInPlace)
    return int(rsp[0])

def MoveProbe(Probe="", XValue="", YValue="", PosRef="", Unit="", Velocity="", Comp=""):
    """
    Moves a defined Positioner to a X, Y position relative to a per PosRef specified
    reference position. Notifications: 51 / 52 / 5
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        XValue:Decimal = 0
        YValue:Decimal = 0
        PosRef:str = "Home"
        Unit:str = "Microns"
        Velocity:Decimal = 100
        Comp:str = "Technology"
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 30000
    Example:MoveProbe 1 1000. 1000. R Y 100
    """
    rsp = MessageServerInterface.sendSciCommand("MoveProbe",Probe,XValue,YValue,PosRef,Unit,Velocity,Comp)
    return int(rsp[0])

def MoveProbeIndex(Probe="", XSteps="", YSteps="", PosRef="", Velocity=""):
    """
    Moves a defined Positioner to a X, Y position relative to a per PosRef specified
    reference position. Notifications: 51 / 52 / 5
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        XSteps:int = 0
        YSteps:int = 0
        PosRef:str = "Home"
        Velocity:Decimal = 100
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 30000
    Example:MoveProbeIndex 1 1 1 R 100
    """
    rsp = MessageServerInterface.sendSciCommand("MoveProbeIndex",Probe,XSteps,YSteps,PosRef,Velocity)
    return int(rsp[0])

def MoveProbeContact(Probe="", Velocity=""):
    """
    Moves the given Positioner Z axis to the preset Contact Height. If no Contact
    Height is set, the Kernel will return a 'Contact Height not set' error.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Velocity:Decimal = 100
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 30000
    Example:MoveProbeContact 1 100
    """
    rsp = MessageServerInterface.sendSciCommand("MoveProbeContact",Probe,Velocity)
    return int(rsp[0])

def MoveProbeAlign(Probe="", Velocity=""):
    """
    Moves the given Positioner Z axis to the align height.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Velocity:Decimal = 100
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 30000
    Example:MoveProbeAlign 1 100
    """
    rsp = MessageServerInterface.sendSciCommand("MoveProbeAlign",Probe,Velocity)
    return int(rsp[0])

def MoveProbeSeparation(Probe="", Velocity=""):
    """
    Moves a defined Positioner to a X, Y position relative to a per PosRef specified
    reference position. Notifications: 51 / 52 / 5
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Velocity:Decimal = 100
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 30000
    Example:MoveProbeSeparation 1 100
    """
    rsp = MessageServerInterface.sendSciCommand("MoveProbeSeparation",Probe,Velocity)
    return int(rsp[0])

def MoveProbeZ(Probe="", Height="", PosRef="", Unit="", Velocity="", Comp=""):
    """
    Moves a given Positioner Z axis to a defined Z height.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Height:Decimal = 0
        PosRef:str = "Zero"
        Unit:str = "Microns"
        Velocity:Decimal = 100
        Comp:str = "Technology"
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 30000
    Example:MoveProbeZ 1 1000. R Y 67
    """
    rsp = MessageServerInterface.sendSciCommand("MoveProbeZ",Probe,Height,PosRef,Unit,Velocity,Comp)
    return int(rsp[0])

def MoveProbeLift(Probe="", SetLift=""):
    """
    Moves the Positioner to the lower (0) or upper = lifted (1) position. The
    command initiates the motion only, the whole movement may take some seconds.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        SetLift:int = 1
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 10000
    Example:MoveProbeLift 1
    """
    rsp = MessageServerInterface.sendSciCommand("MoveProbeLift",Probe,SetLift)
    return int(rsp[0])

def MoveProbeVelocity(Probe="", PolarityX="", PolarityY="", PolarityZ="", VelocityX="", VelocityY="", VelocityZ=""):
    """
    '+' Move this axis into plus direction '-' Move this axis into minus direction
    '0' Do not change this axis
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        PolarityX:str = "Fixed"
        PolarityY:str = "Fixed"
        PolarityZ:str = "Fixed"
        VelocityX:Decimal = 100
        VelocityY:Decimal = 0
        VelocityZ:Decimal = 0
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 30000
    Example:MoveProbeVelocity 1 + + 0 67 100 0
    """
    rsp = MessageServerInterface.sendSciCommand("MoveProbeVelocity",Probe,PolarityX,PolarityY,PolarityZ,VelocityX,VelocityY,VelocityZ)
    return int(rsp[0])

def StopProbeMovement(Probe="", FlagsStop=""):
    """
    Stops Positioner movement for the given axes immediately. A smooth stop is
    performed.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        FlagsStop:int = 7
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 5000
    Example:StopProbeMovement 1 7
    """
    rsp = MessageServerInterface.sendSciCommand("StopProbeMovement",Probe,FlagsStop)
    return int(rsp[0])

def SetProbeMode(Probe="", Overtravel="", AutoZ="", Interlock="", AutoZFollow="", AutoQuiet=""):
    """
    The mode manages the way the Chuck behaves when it is in Contact Height.
    Positioner mode is made up from 5 flags and the user can control all of them by
    using this command. Every flag can be turned on by setting value 1, or turned
    off by setting value 0. Use the value 2 if no change for a flag is needed.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Overtravel:int = 2
        AutoZ:int = 2
        Interlock:int = 2
        AutoZFollow:int = 2
        AutoQuiet:int = 2
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 5000
    Example:SetProbeMode 1 2 2 2 2
    """
    rsp = MessageServerInterface.sendSciCommand("SetProbeMode",Probe,Overtravel,AutoZ,Interlock,AutoZFollow,AutoQuiet)
    return int(rsp[0])

def SetProbeHome(Probe="", Mode="", Unit="", XValue="", YValue=""):
    """
    Sets the Positioner's Home position in X and Y. This position identifies the
    probe coordinate system for later movements. Usually this position is identical
    to the die home position.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Mode:str = "0"
        Unit:str = "Microns"
        XValue:Decimal = 0
        YValue:Decimal = 0
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 5000
    Example:SetProbeHome 1 0 Y
    """
    rsp = MessageServerInterface.sendSciCommand("SetProbeHome",Probe,Mode,Unit,XValue,YValue)
    return int(rsp[0])

def SetProbeIndex(Probe="", XValue="", YValue="", Unit=""):
    """
    Sets the Positioner's index size or the location of the reference die relative
    to the home die.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        XValue:Decimal = 0
        YValue:Decimal = 0
        Unit:str = "Microns"
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 5000
    Example:SetProbeIndex 1 1000. 1000. Y
    """
    rsp = MessageServerInterface.sendSciCommand("SetProbeIndex",Probe,XValue,YValue,Unit)
    return int(rsp[0])

def SetProbeHeight(Probe="", PresetHeight="", Mode="", Unit="", Value=""):
    """
    Defines the predefined Contact Height and corresponding gaps for Overtravel,
    Align and Separation height. No data sets Contact Height at current position.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        PresetHeight:str = "Contact"
        Mode:str = "0"
        Unit:str = "Microns"
        Value:Decimal = 0
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 5000
    Example:SetProbeHeight 1 C 0 Y
    """
    rsp = MessageServerInterface.sendSciCommand("SetProbeHeight",Probe,PresetHeight,Mode,Unit,Value)
    return int(rsp[0])

def ReadProbeIndex(Probe="", Unit=""):
    """
    Returns the current Positioner's wafer index values or the current Positioner's
    index positions for X and Y.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Unit:str = "Microns"
    ----------
    Response:
        ProbeEcho:int
        IndexX:Decimal
        IndexY:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadProbeIndex 1 Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadProbeIndex",Probe,Unit)
    global ReadProbeIndex_Response
    if not "ReadProbeIndex_Response" in globals(): ReadProbeIndex_Response = namedtuple("ReadProbeIndex_Response", "ProbeEcho,IndexX,IndexY")
    return ReadProbeIndex_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def SetProbeBacklash(Probe="", MoveDistX="", MoveDistY="", MoveDistZ=""):
    """
    Sets the backlash compensation move distance for X, Y and Z
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        MoveDistX:Decimal = 0
        MoveDistY:Decimal = 0
        MoveDistZ:Decimal = 0
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 5000
    Example:SetProbeBacklash 1 100 100 100
    """
    rsp = MessageServerInterface.sendSciCommand("SetProbeBacklash",Probe,MoveDistX,MoveDistY,MoveDistZ)
    return int(rsp[0])

def SetProbeLED(Probe="", NewLEDState=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Set the Positioner LED On or Off.
    Status: internal
    ----------
    Parameters:
        Probe:int = 1
        NewLEDState:int = 0
    ----------
    Response:
        ProbeEcho:int
        LEDState:int
    ----------
    Command Timeout: 5000
    Example:SetProbeLED 1 1
    """
    rsp = MessageServerInterface.sendSciCommand("SetProbeLED",Probe,NewLEDState)
    global SetProbeLED_Response
    if not "SetProbeLED_Response" in globals(): SetProbeLED_Response = namedtuple("SetProbeLED_Response", "ProbeEcho,LEDState")
    return SetProbeLED_Response(int(rsp[0]),int(rsp[1]))

def GetProbeTableID(Probe="", TableName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the ID of a stored probe table or creates a new table. The ID is unique
    for the name and the probe. The table itself has a string name. This name is not
    case sensitive. The command has to be used before all other table commands can
    be used. Access to tables is possible only with an ID Number (name dependent).
    Status: internal
    ----------
    Parameters:
        Probe:int = 1
        TableName:str = "ProbeTable"
    ----------
    Response:
        ProbeEcho:int
        TableID:int
    ----------
    Command Timeout: 5000
    Example:GetProbeTableID 1 ProbeTable
    """
    rsp = MessageServerInterface.sendSciCommand("GetProbeTableID",Probe,TableName)
    global GetProbeTableID_Response
    if not "GetProbeTableID_Response" in globals(): GetProbeTableID_Response = namedtuple("GetProbeTableID_Response", "ProbeEcho,TableID")
    return GetProbeTableID_Response(int(rsp[0]),int(rsp[1]))

def MoveProbeTablePoint(Probe="", TableID="", PointID="", Velocity=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves a defined Positioner to a X, Y position relative to a per PosRef specified
    reference position. Notifications: 51 / 52 / 5
    Status: internal
    ----------
    Parameters:
        Probe:int = 1
        TableID:int = 1
        PointID:int = 1
        Velocity:Decimal = 100
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 30000
    Example:MoveProbeTablePoint 3 14 10 67
    """
    rsp = MessageServerInterface.sendSciCommand("MoveProbeTablePoint",Probe,TableID,PointID,Velocity)
    return int(rsp[0])

def ReadProbeTablePoint(Probe="", TableID="", PointID="", Unit=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Reads the data from a point of a stored table in the Kernel.
    Status: internal
    ----------
    Parameters:
        Probe:int = 1
        TableID:int = 0
        PointID:int = 0
        Unit:str = "Microns"
    ----------
    Response:
        ProbeEcho:int
        CoordX:Decimal
        CoordY:Decimal
        CoordSystem:str
    ----------
    Command Timeout: 5000
    Example:ReadProbeTablePoint 2 4 10 Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadProbeTablePoint",Probe,TableID,PointID,Unit)
    global ReadProbeTablePoint_Response
    if not "ReadProbeTablePoint_Response" in globals(): ReadProbeTablePoint_Response = namedtuple("ReadProbeTablePoint_Response", "ProbeEcho,CoordX,CoordY,CoordSystem")
    return ReadProbeTablePoint_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),str("" if len(rsp) < 4 else ' '.join(rsp[3:])))

def SetProbeTablePoint(Probe="", TableID="", PointID="", CoordX="", CoordY="", Unit="", CoordSystem=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets one point of a Positioner table inside the Kernel. If there is still a
    point with this index loaded, the Kernel returns an error. Number of positions
    and number of tables are dependent on the internal memory. All positions are
    stored persistent, that means after switching power on or off the positions are
    still available. The table starts with point number 1 and ends with the ID 16.
    The table can contain 65535 points with the ID 0 up to 65534. Overwriting of
    position points is not possible. The point has to be deleted before other values
    are set.
    Status: internal
    ----------
    Parameters:
        Probe:int = 1
        TableID:int = 0
        PointID:int = 0
        CoordX:Decimal = 0
        CoordY:Decimal = 0
        Unit:str = "Microns"
        CoordSystem:str = "HomeSystem"
    ----------
    Response:
        ProbeEcho:int
        ValidPoint:int
    ----------
    Command Timeout: 5000
    Example:SetProbeTablePoint 3 12 10 8992.5 7883.0 Y Z M
    """
    rsp = MessageServerInterface.sendSciCommand("SetProbeTablePoint",Probe,TableID,PointID,CoordX,CoordY,Unit,CoordSystem)
    global SetProbeTablePoint_Response
    if not "SetProbeTablePoint_Response" in globals(): SetProbeTablePoint_Response = namedtuple("SetProbeTablePoint_Response", "ProbeEcho,ValidPoint")
    return SetProbeTablePoint_Response(int(rsp[0]),int(rsp[1]))

def ClearProbeTablePoint(Probe="", TableID="", StartPoint="", EndPoint=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Clear one or a range of Positioner table site points in the Kernel. If
    StartPoint is a negative value, the whole table will be deleted.
    Status: internal
    ----------
    Parameters:
        Probe:int = 1
        TableID:int = 0
        StartPoint:int = -1
        EndPoint:int = 0
    ----------
    Response:
        ProbeEcho:int
        ClearNumber:int
        ValidNumber:int
    ----------
    Command Timeout: 5000
    Example:ClearProbeTablePoint 3 4 10 15
    """
    rsp = MessageServerInterface.sendSciCommand("ClearProbeTablePoint",Probe,TableID,StartPoint,EndPoint)
    global ClearProbeTablePoint_Response
    if not "ClearProbeTablePoint_Response" in globals(): ClearProbeTablePoint_Response = namedtuple("ClearProbeTablePoint_Response", "ProbeEcho,ClearNumber,ValidNumber")
    return ClearProbeTablePoint_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]))

def MoveScopeSilo(Index=""):
    """
    Move the Scope to the reference position of the given silo. The reference
    position should be - if not defined otherwise - 200 um above the safe z-height
    in the center of the Scope.
    Status: published
    ----------
    Parameters:
        Index:int = 1
    ----------
    Command Timeout: 70000
    Example:MoveScopeSilo 1
    """
    MessageServerInterface.sendSciCommand("MoveScopeSilo",Index)


def SetScopeSiloReference(Index="", X="", Y="", Z=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Set the reference position of a silo. The next time the Scope moves to this
    silo, it will go to this position. The Reference position must be inside the
    silo in xy and above the lower Z-Fence of the silo.  Setting the reference
    position directly on the fence in x, y or z typically leads to errors. Try to
    keep a safety margin.
    Status: internal
    ----------
    Parameters:
        Index:int = 1
        X:Decimal = 0
        Y:Decimal = 0
        Z:Decimal = 0
    ----------
    Command Timeout: 5000
    Example:SetScopeSiloReference 1 1000 2000 3000
    """
    MessageServerInterface.sendSciCommand("SetScopeSiloReference",Index,X,Y,Z)


def AlignChuckTheta(XDistance="", YDistance="", PosRef=""):
    """
    This command causes a Chuck Theta axis rotation to align the wafer to the Chuck
    X,Y movements.   It can be used to perform a two point alignment with P1(X1,Y1)
    and P2(X2,Y2) as two points on a wafer street line.   The units of the distances
    are not important - but both distances should use the same unit.    If one or
    both distances are zero, the command does not return an error and instead ignore
    this alignment
    Status: published
    ----------
    Parameters:
        XDistance:Decimal = 0
        YDistance:Decimal = 0
        PosRef:str = "Relative"
    ----------
    Command Timeout: 10000
    Example:AlignChuckTheta 10000 10 R
    """
    MessageServerInterface.sendSciCommand("AlignChuckTheta",XDistance,YDistance,PosRef)


def AlignScopeTheta(XDistance="", YDistance="", PosRef=""):
    """
    This command causes a virtual rotation of the Scope coordinate system to align
    the Scope to the Chuck X,Y axis or/and to the wafer alignment. It can be used to
    perform a two point alignment with the points P1(X1,Y1) and P2(X2,Y2).
    Calculation of X and Y distances:
    Status: published
    ----------
    Parameters:
        XDistance:Decimal = 0
        YDistance:Decimal = 0
        PosRef:str = "Relative"
    ----------
    Command Timeout: 10000
    Example:AlignScopeTheta 10000 10 R
    """
    MessageServerInterface.sendSciCommand("AlignScopeTheta",XDistance,YDistance,PosRef)


def AlignProbeTheta(Probe="", XDistance="", YDistance="", PosRef=""):
    """
    This command causes a rotation of the coordinate system of given probe to align
    the probe to the Chuck X,Y axis or/and to the wafer alignment. It can be used to
    perform a two point alignment with the points P1(X1,Y1) and P2(X2,Y2).
    Calculation of Y and Y distances:
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        XDistance:Decimal = 0
        YDistance:Decimal = 0
        PosRef:str = "Relative"
    ----------
    Response:
        ProbeEcho:int
    ----------
    Command Timeout: 10000
    Example:AlignProbeTheta 1 10000 10 R
    """
    rsp = MessageServerInterface.sendSciCommand("AlignProbeTheta",Probe,XDistance,YDistance,PosRef)
    return int(rsp[0])

def AlignCardTheta(Angle="", Unit="", PosRef=""):
    """
    This command causes a rotation of the Chuck coordinate system to align the Chuck
    X, Y axis to the probecard.   The polarity of the data determines a left or a
    right rotation of the Chuck coordinate system.
    Status: published
    ----------
    Parameters:
        Angle:Decimal = 0
        Unit:str = "Degrees"
        PosRef:str = "Relative"
    ----------
    Command Timeout: 10000
    Example:AlignCardTheta 2.5 D R
    """
    MessageServerInterface.sendSciCommand("AlignCardTheta",Angle,Unit,PosRef)


def ReadCardTheta(Unit=""):
    """
    Returns the angle between the Chuck coordinate-system and the probecard
    coordinate-system.
    Status: published
    ----------
    Parameters:
        Unit:str = "Degrees"
    ----------
    Response:
        Angle:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadCardTheta D
    """
    rsp = MessageServerInterface.sendSciCommand("ReadCardTheta",Unit)
    return Decimal(rsp[0])

def ReadChuckTheta(Unit=""):
    """
    Returns the current Chuck alignment angle which is identical to the current
    value of theta rotation.
    Status: published
    ----------
    Parameters:
        Unit:str = "Degrees"
    ----------
    Response:
        Angle:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadChuckTheta D
    """
    rsp = MessageServerInterface.sendSciCommand("ReadChuckTheta",Unit)
    return Decimal(rsp[0])

def ReadScopeTheta(Unit=""):
    """
    Returns the Scope's alignment angle, which is the angle between the Chuck
    coordinate system and the Scope coordinate system.
    Status: published
    ----------
    Parameters:
        Unit:str = "Degrees"
    ----------
    Response:
        Angle:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadScopeTheta D
    """
    rsp = MessageServerInterface.sendSciCommand("ReadScopeTheta",Unit)
    return Decimal(rsp[0])

def ReadProbeTheta(Probe="", Unit=""):
    """
    Returns the actual Positioner's alignment angle, which is the angle between the
    Chuck coordinate system and the Positioner coordinate system.
    Status: published
    ----------
    Parameters:
        Probe:int = 1
        Unit:str = "Degrees"
    ----------
    Response:
        ProbeEcho:int
        Angle:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadProbeTheta 1 D
    """
    rsp = MessageServerInterface.sendSciCommand("ReadProbeTheta",Probe,Unit)
    global ReadProbeTheta_Response
    if not "ReadProbeTheta_Response" in globals(): ReadProbeTheta_Response = namedtuple("ReadProbeTheta_Response", "ProbeEcho,Angle")
    return ReadProbeTheta_Response(int(rsp[0]),Decimal(rsp[1]))

def ReadJoystickSpeeds(Stage="", Axis=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Gets the preset speeds, which are used by the joystick controller for moving a
    single stage. The speeds can be read for XY, for Z and for Theta axis
    separately. Jog timing and index timing are the times, the joystick controller
    waits between two single jog or index moves.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        Axis:str = "X"
    ----------
    Response:
        JogTime:Decimal
        Speed2:Decimal
        Speed3:Decimal
        Speed4:Decimal
        IndexTime:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadJoystickSpeeds S Z
    """
    rsp = MessageServerInterface.sendSciCommand("ReadJoystickSpeeds",Stage,Axis)
    global ReadJoystickSpeeds_Response
    if not "ReadJoystickSpeeds_Response" in globals(): ReadJoystickSpeeds_Response = namedtuple("ReadJoystickSpeeds_Response", "JogTime,Speed2,Speed3,Speed4,IndexTime")
    return ReadJoystickSpeeds_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]))

def SetJoystickSpeeds(Stage="", JogTime="", Speed2="", Speed3="", Speed4="", IndexTime="", Axis=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the preset speeds, which are used by the joystick controller for moving a
    single stage. After setting, the speeds can be selected by pressing the Speed n
    buttons at the controller. The speeds must be set separately for XY, for Z and
    for Theta axis. Jog timing and index timing are the times, the joystick
    controller waits between two single jog or index moves.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        JogTime:Decimal = 0
        Speed2:Decimal = 0
        Speed3:Decimal = 0
        Speed4:Decimal = 0
        IndexTime:Decimal = 0
        Axis:str = "X"
    ----------
    Command Timeout: 5000
    Example:SetJoystickSpeeds S 10 20 30 40 50 Z
    """
    MessageServerInterface.sendSciCommand("SetJoystickSpeeds",Stage,JogTime,Speed2,Speed3,Speed4,IndexTime,Axis)


def SetLoaderGate(Open=""):
    """
    Opens or closes the loader gate. Automatic handling systems can load wafers to
    the Chuck through the gate.
    Status: published
    ----------
    Parameters:
        Open:int = 0
    ----------
    Command Timeout: 5000
    Example:SetLoaderGate 0
    """
    MessageServerInterface.sendSciCommand("SetLoaderGate",Open)


def ReadWaferStatus():
    """
    Returns whether the system detected a wafer. This feature can be used if the
    Probe Station is equipped with a vacuum sensor and while vacuum is activated.
    Status: published
    ----------
    Response:
        SensedByVac:str
    ----------
    Command Timeout: 5000
    Example:ReadWaferStatus
    """
    rsp = MessageServerInterface.sendSciCommand("ReadWaferStatus")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ReadContactCount(Stage=""):
    """
    Returns the number of times this stage moved to contact since the last time the
    counter was reset.
    Status: published
    ----------
    Parameters:
        Stage:str = "Chuck"
    ----------
    Response:
        Count:int
    ----------
    Command Timeout: 5000
    Example:ReadContactCount C
    """
    rsp = MessageServerInterface.sendSciCommand("ReadContactCount",Stage)
    return int(rsp[0])

def ResetContactCount(Stage=""):
    """
    Resets the contact counter for the specified stage to zero. Notifications: 23
    Status: published
    ----------
    Parameters:
        Stage:str = "Chuck"
    ----------
    Command Timeout: 5000
    Example:ResetContactCount C
    """
    MessageServerInterface.sendSciCommand("ResetContactCount",Stage)


def SetManualMode(Enable=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command enables the manual mode on stations with XY knobs. This mode will
    allow to move the Chuck using the knobs.
    Status: internal
    ----------
    Parameters:
        Enable:int = 1
    ----------
    Command Timeout: 10000
    Example:SetManualMode 1
    """
    MessageServerInterface.sendSciCommand("SetManualMode",Enable)


def GetManualMode():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command returns the state of the manual mode for stations with XY knobs.
    Status: internal
    ----------
    Response:
        Enable:int
    ----------
    Command Timeout: 10000
    Example:GetManualMode 1
    """
    rsp = MessageServerInterface.sendSciCommand("GetManualMode")
    return int(rsp[0])

def GetAxisReverse(Stage="", Axis=""):
    """
    Allows reading if an axis is reverse.
    Status: published
    ----------
    Parameters:
        Stage:str = "Chuck"
        Axis:str = "XAxis"
    ----------
    Response:
        IsReverse:int
    ----------
    Command Timeout: 5000
    Example:GetAxisReverse C X
    """
    rsp = MessageServerInterface.sendSciCommand("GetAxisReverse",Stage,Axis)
    return int(rsp[0])

def EnableEdgeSensor(EdgeSensor="", Enable=""):
    """
    Enables/disables the use of an edge sensor.
    Status: published
    ----------
    Parameters:
        EdgeSensor:int = 1
        Enable:int = 1
    ----------
    Command Timeout: 5000
    Example:EnableEdgeSensor 1 1
    """
    MessageServerInterface.sendSciCommand("EnableEdgeSensor",EdgeSensor,Enable)


def SetTypedOutput(Channel="", WantOutputOn="", PulseTime=""):
    """
    Controls the Velox output channel signals. It can be used to activate/deactivate
    outputs.
    Status: published
    ----------
    Parameters:
        Channel:str = "NoSensor"
        WantOutputOn:int = 0
        PulseTime:int = -1
    ----------
    Command Timeout: 5000
    Example:SetTypedOutput DO_WaferVacuum 1
    """
    MessageServerInterface.sendSciCommand("SetTypedOutput",Channel,WantOutputOn,PulseTime)


def ReadTypedSensor(Channel=""):
    """
    Returns the status of the specified input channel, output channel, or edge
    sensor.
    Status: published
    ----------
    Parameters:
        Channel:str = "NoSensor"
    ----------
    Response:
        IsSensorOn:int
    ----------
    Command Timeout: 10000
    Example:ReadTypedSensor DI_EMO
    """
    rsp = MessageServerInterface.sendSciCommand("ReadTypedSensor",Channel)
    return int(rsp[0])

def MoveCoolDownPosition():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the Chuck to the cool down position that is defined in KernelSetup. The
    cooldown position is used to move the Chuck away in XY while the robot is in the
    chamber and tries to get a hot wafer.
    Status: internal
    ----------
    Command Timeout: 30000
    Example:MoveCoolDownPosition
    """
    MessageServerInterface.sendSciCommand("MoveCoolDownPosition")


def ReadJoystickSpeedsCycle(Stage=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command reads the cycling speeds - these are the speeds that are used by
    the USB joystick when cycling through the speeds. Can be setup in Control
    Center.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
    ----------
    Response:
        CycleJog:int
        CycleSpeed2:int
        CycleSpeed3:int
        CycleSpeed4:int
        CycleIndex:int
    ----------
    Command Timeout: 5000
    Example:ReadJoystickSpeedsCycle S
    """
    rsp = MessageServerInterface.sendSciCommand("ReadJoystickSpeedsCycle",Stage)
    global ReadJoystickSpeedsCycle_Response
    if not "ReadJoystickSpeedsCycle_Response" in globals(): ReadJoystickSpeedsCycle_Response = namedtuple("ReadJoystickSpeedsCycle_Response", "CycleJog,CycleSpeed2,CycleSpeed3,CycleSpeed4,CycleIndex")
    return ReadJoystickSpeedsCycle_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]))

def SetJoystickSpeedsCycle(Stage="", CycleJog="", CycleSpeed2="", CycleSpeed3="", CycleSpeed4="", CycleIndex=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command sets the cycling speeds - these are the speeds that are used by the
    USB joystick when cycling through the speeds. Can be setup in Control Center.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        CycleJog:int = 0
        CycleSpeed2:int = 0
        CycleSpeed3:int = 0
        CycleSpeed4:int = 0
        CycleIndex:int = 0
    ----------
    Command Timeout: 5000
    Example:SetJoystickSpeedsCycle C 1 1 1 1 1
    """
    MessageServerInterface.sendSciCommand("SetJoystickSpeedsCycle",Stage,CycleJog,CycleSpeed2,CycleSpeed3,CycleSpeed4,CycleIndex)


def SendAUCSCommand(Command=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command allows sending low level AUCS commands to the ECX box stage. Only
    applies to Elite/12k/S300 stations.
    Status: internal
    ----------
    Parameters:
        Command:str = ""
    ----------
    Response:
        Response:str
    ----------
    Command Timeout: 60000
    Example:SendAUCSCommand "MM 1 0 INIT 0"
    """
    rsp = MessageServerInterface.sendSciCommand("SendAUCSCommand",Command)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ReadCompensationStatus(Stage="", Compensation=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command allows reading if a specific type of compensation is enabled or
    disabled. Returns an error if this type of compensation is not available for
    this stage.
    Status: internal
    ----------
    Parameters:
        Stage:str = "None"
        Compensation:str = "None"
    ----------
    Response:
        Enabled:int
        Active:int
    ----------
    Command Timeout: 5000
    Example:ReadCompensationStatus C A
    """
    rsp = MessageServerInterface.sendSciCommand("ReadCompensationStatus",Stage,Compensation)
    global ReadCompensationStatus_Response
    if not "ReadCompensationStatus_Response" in globals(): ReadCompensationStatus_Response = namedtuple("ReadCompensationStatus_Response", "Enabled,Active")
    return ReadCompensationStatus_Response(int(rsp[0]),int(rsp[1]))

def RegisterNotification(NotificationCode="", WantNotification=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Deprecated. All Kernel notifications are enabled by default.
    Status: internal
    ----------
    Parameters:
        NotificationCode:int = 0
        WantNotification:int = 1
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("RegisterNotification",NotificationCode,WantNotification)


def SetCompensationStatus(Stage="", Compensation="", Status=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Enables or disables a compensation mode for the specified stage
    Status: internal
    ----------
    Parameters:
        Stage:str = "None"
        Compensation:str = "None"
        Status:int = -1
    ----------
    Command Timeout: 5000
    Example:SetCompensationStatus C A 1
    """
    MessageServerInterface.sendSciCommand("SetCompensationStatus",Stage,Compensation,Status)


def GetControllerInfo(ControllerInfo=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command gets the value "Value" for the parameter "Parameter". The unit is
    parameter specific.
    Status: internal
    ----------
    Parameters:
        ControllerInfo:str = "Unknown"
    ----------
    Response:
        Value:Decimal
    ----------
    Command Timeout: 1000
    Example:GetControllerInfo HasScanChuckZ
    """
    rsp = MessageServerInterface.sendSciCommand("GetControllerInfo",ControllerInfo)
    return Decimal(rsp[0])

def SetOperationalMode(OperationalMode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    In unprotected mode a number of security features like software fence and
    initialization necessity are deactivated.          Unprotected mode is
    deactivated automatically after 5 minutes. Sending 'SetOperationalMode U'
    anytime before resets the timer back to 5 minutes. It is not necessary to
    deactivate it before.  **WARNING**: If unprotected mode is enabled, even the
    most basic safety- and sanity-checks are skipped. Any movement may cause
    irreparable damage to the prober or attached hardware.
    Status: internal
    ----------
    Parameters:
        OperationalMode:str = "ProtectedMode"
    ----------
    Command Timeout: 5000
    Example:SetOperationalMode P
    """
    MessageServerInterface.sendSciCommand("SetOperationalMode",OperationalMode)


def GetNanoChamberState():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Get the currently configured Nano-chamber-state.
    Status: internal
    ----------
    Response:
        NanoChamberState:str
    ----------
    Command Timeout: 1000
    """
    rsp = MessageServerInterface.sendSciCommand("GetNanoChamberState")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetNanoChamberState(NanoChamberState=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Set the NanoChamber-state.
    Status: internal
    ----------
    Parameters:
        NanoChamberState:str = "Free"
    ----------
    Command Timeout: 1000
    """
    MessageServerInterface.sendSciCommand("SetNanoChamberState",NanoChamberState)


def SetCameraCool(State=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Allows to force activate/deactivate the camera cool output or to let it be set
    automatically by purge control.
    Status: internal
    ----------
    Parameters:
        State:int = 2
    ----------
    Command Timeout: 10000
    Example:SetCameraCool 0
    """
    MessageServerInterface.sendSciCommand("SetCameraCool",State)


def ActivateChuckVacuum():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Activates the Chuck vacuum and forces it to be on. This command ignores the
    vacuum sensor and timeout.
    Status: internal
    ----------
    Command Timeout: 10000
    Example:ActivateChuckVacuum
    """
    MessageServerInterface.sendSciCommand("ActivateChuckVacuum")


def ReadMatrixValues(Stage="", MatrixIndexX="", MatrixIndexY=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command returns a point from the matrix compensation table for the
    specified axis from the Kernel. All command parameters are mandatory.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        MatrixIndexX:int = 0
        MatrixIndexY:int = 0
    ----------
    Response:
        XVal:Decimal
        YVal:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadMatrixValues C 0 0
    """
    rsp = MessageServerInterface.sendSciCommand("ReadMatrixValues",Stage,MatrixIndexX,MatrixIndexY)
    global ReadMatrixValues_Response
    if not "ReadMatrixValues_Response" in globals(): ReadMatrixValues_Response = namedtuple("ReadMatrixValues_Response", "XVal,YVal")
    return ReadMatrixValues_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def SetMatrixValues(Stage="", MatrixIndexX="", MatrixIndexY="", XVal="", YVal=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Downloads a point of the matrix compensation table for a specified stage to the
    Kernel. All command parameters are mandatory.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        MatrixIndexX:int = 0
        MatrixIndexY:int = 0
        XVal:Decimal = 0
        YVal:Decimal = 0
    ----------
    Command Timeout: 5000
    Example:SetMatrixValues C 0 0 5000.0 5000.0 2500.0
    """
    MessageServerInterface.sendSciCommand("SetMatrixValues",Stage,MatrixIndexX,MatrixIndexY,XVal,YVal)


def ReadMEAStatus(Stage="", Type=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Reads if the MEA file for a stage is loaded/enabled (Nucleus legacy stations
    only)
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        Type:int = 0
    ----------
    Response:
        Enable:int
    ----------
    Command Timeout: 5000
    Example:ReadMEAStatus C 0
    """
    rsp = MessageServerInterface.sendSciCommand("ReadMEAStatus",Stage,Type)
    return int(rsp[0])

def LoadMEAFile(Stage="", Type="", Load=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Load the MEA file for a stage (Nucleus legacy stations only)
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        Type:int = 0
        Load:int = 0
    ----------
    Command Timeout: 5000
    Example:LoadMEAFile C 0 1
    """
    MessageServerInterface.sendSciCommand("LoadMEAFile",Stage,Type,Load)


def ReadSoftwareLimits(Stage=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    The command returns the positions of the actual software limits (end of move
    range) for each axis of the specified stage in microns. If the Theta stage is
    selected Z1 and Z2 include the values for the Theta limits.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
    ----------
    Response:
        ZLowValue:Decimal
        ZHighValue:Decimal
        X1Value:Decimal
        Y1Value:Decimal
        X2Value:Decimal
        Y2Value:Decimal
        X3Value:Decimal
        Y3Value:Decimal
        X4Value:Decimal
        Y4Value:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadSoftwareLimits C
    """
    rsp = MessageServerInterface.sendSciCommand("ReadSoftwareLimits",Stage)
    global ReadSoftwareLimits_Response
    if not "ReadSoftwareLimits_Response" in globals(): ReadSoftwareLimits_Response = namedtuple("ReadSoftwareLimits_Response", "ZLowValue,ZHighValue,X1Value,Y1Value,X2Value,Y2Value,X3Value,Y3Value,X4Value,Y4Value")
    return ReadSoftwareLimits_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),Decimal(rsp[5]),Decimal(rsp[6]),Decimal(rsp[7]),Decimal(rsp[8]),Decimal(rsp[9]))

def SetSoftwareFence(Stage="", AuxID="", FenceForm="", XBase="", YBase="", XDist="", YDist=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command sets types and dimensions of technological software fences. It can
    also be used for enabling and disabling the software fence.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        AuxID:int = 0
        FenceForm:str = "None"
        XBase:Decimal = 0
        YBase:Decimal = 0
        XDist:Decimal = 0
        YDist:Decimal = 0
    ----------
    Command Timeout: 10000
    Example:SetSoftwareFence C 0 R 5000 5000 25000 25000
    """
    MessageServerInterface.sendSciCommand("SetSoftwareFence",Stage,AuxID,FenceForm,XBase,YBase,XDist,YDist)


def GetSoftwareFence(Stage="", AuxID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command reads the type and the dimensions of an actual set technological
    software fence. In case of a rectangular software fence, X and Y coordinates of
    the four edge points of the fence are given back. In case of a circular software
    fence, X and Y coordinates of the center point and the radius are given back.
    All other return values are filled with zeros. All position values are in
    microns from zero.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        AuxID:int = 0
    ----------
    Response:
        FenceForm:str
        XValue1:Decimal
        YValue1:Decimal
        XValue2:Decimal
        YValue2:Decimal
        XValue3:Decimal
        YValue3:Decimal
        XValue4:Decimal
        YValue4:Decimal
    ----------
    Command Timeout: 10000
    Example:GetSoftwareFence C
    """
    rsp = MessageServerInterface.sendSciCommand("GetSoftwareFence",Stage,AuxID)
    global GetSoftwareFence_Response
    if not "GetSoftwareFence_Response" in globals(): GetSoftwareFence_Response = namedtuple("GetSoftwareFence_Response", "FenceForm,XValue1,YValue1,XValue2,YValue2,XValue3,YValue3,XValue4,YValue4")
    return GetSoftwareFence_Response(str(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),Decimal(rsp[5]),Decimal(rsp[6]),Decimal(rsp[7]),Decimal(rsp[8]))

def GetZFence(Stage="", CompLayer=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This commands reads if the Z-Fence is activated and the currently set Z-fence
    values for the specified stage.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        CompLayer:str = "Technology"
    ----------
    Response:
        Enabled:int
        ZLow:Decimal
        ZHigh:Decimal
    ----------
    Command Timeout: 10000
    Example:GetZFence S
    """
    rsp = MessageServerInterface.sendSciCommand("GetZFence",Stage,CompLayer)
    global GetZFence_Response
    if not "GetZFence_Response" in globals(): GetZFence_Response = namedtuple("GetZFence_Response", "Enabled,ZLow,ZHigh")
    return GetZFence_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def SetZFence(Stage="", Enabled="", ZLow="", ZHigh="", CompLayer=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This commands sets Z-Fence and the Z-fence values for the specified stage.
    Values are stored uncompensated internally and set Technology compensated as
    default.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        Enabled:int = 0
        ZLow:Decimal = 0
        ZHigh:Decimal = 0
        CompLayer:str = "Technology"
    ----------
    Command Timeout: 10000
    Example:SetZFence S 1 5000 10000
    """
    MessageServerInterface.sendSciCommand("SetZFence",Stage,Enabled,ZLow,ZHigh,CompLayer)


def ResetProber(Mode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Restarts the Prober and replaces the current configuration with a formerly
    written recovery file. If no recovery file was written, the configuration is
    reset to the version of the last Prober restart. For ProberBench electronics,
    'H' will restart the Operating system, 'S' will only restart the Kernel
    application. For Windows Kernel, 'H' and 'S' are identical and will only restart
    the Kernel software.
    Status: internal
    ----------
    Parameters:
        Mode:str = "S"
    ----------
    Command Timeout: 20000
    Example:ResetProber S
    """
    MessageServerInterface.sendSciCommand("ResetProber",Mode)


def ResetCBox(ResetMode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Reboots the operation system inside the Joystick Controller and restarts the
    functionality. The restart will need a time of around 20 seconds. Only applies
    to PA stations.
    Status: internal
    ----------
    Parameters:
        ResetMode:str = "S"
    ----------
    Command Timeout: 20000
    Example:ResetCBox S
    """
    MessageServerInterface.sendSciCommand("ResetCBox",ResetMode)


def ReadStageLocations(Stage="", LocationType="", AuxID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command allows reading the Home, Load, Transfer, Transfer for Load, Die
    Home and Station Rest locations for each stage (if applicable) and for any AUX
    site.   The Home Position on the Chuck or Positioner Z axis is also called
    Contact Height. The Home Position on the Scope Z axis is also called Focus
    Height.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        LocationType:str = "Center"
        AuxID:int = 0
    ----------
    Response:
        X:Decimal
        Y:Decimal
        Z:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadStageLocations C C 0
    """
    rsp = MessageServerInterface.sendSciCommand("ReadStageLocations",Stage,LocationType,AuxID)
    global ReadStageLocations_Response
    if not "ReadStageLocations_Response" in globals(): ReadStageLocations_Response = namedtuple("ReadStageLocations_Response", "X,Y,Z")
    return ReadStageLocations_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def GetDataIterator(ShowAll=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns a data stream handle which represents a data stream of setup parameters.
    and requires the GetNextDatum command.
    Status: internal
    ----------
    Parameters:
        ShowAll:int = 0
    ----------
    Response:
        IdentityToken:int
        SizeNoAll:int
    ----------
    Command Timeout: 10000
    Example:GetDataIterator 1
    """
    rsp = MessageServerInterface.sendSciCommand("GetDataIterator",ShowAll)
    global GetDataIterator_Response
    if not "GetDataIterator_Response" in globals(): GetDataIterator_Response = namedtuple("GetDataIterator_Response", "IdentityToken,SizeNoAll")
    return GetDataIterator_Response(int(rsp[0]),int(rsp[1]))

def GetNextDatum(IdentityToken=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the next parameter from the data stream. Fields are separated by a
    colon. Structure of the response parameter Value:
    Path_Path:Name:Description:Value
    Status: internal
    ----------
    Parameters:
        IdentityToken:int = 0
    ----------
    Response:
        IsLastDatum:int
        DatumCode:int
        Attributes:int
        PathNameDescrValue:str
    ----------
    Command Timeout: 10000
    Example:GetNextDatum 0
    """
    rsp = MessageServerInterface.sendSciCommand("GetNextDatum",IdentityToken)
    global GetNextDatum_Response
    if not "GetNextDatum_Response" in globals(): GetNextDatum_Response = namedtuple("GetNextDatum_Response", "IsLastDatum,DatumCode,Attributes,PathNameDescrValue")
    return GetNextDatum_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),str("" if len(rsp) < 4 else ' '.join(rsp[3:])))

def SetDatum(PathNameAndValue=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the value of a parameter. An empty parameter string saves the whole
    configuration to non-volatile memory. Fields are separated by a colon.
    Status: internal
    ----------
    Parameters:
        PathNameAndValue:str = ""
    ----------
    Command Timeout: 20000
    Example:SetDatum Chuck:AlignGap:25
    """
    MessageServerInterface.sendSciCommand("SetDatum",PathNameAndValue)


def GetDatum(PathName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns a value string. The Value string consists of the value and the
    description. The Locator only consists of the path and the name. All fields are
    separated by a colon.  Structure of the command parameter Locator:
    Path_Path:Name Structure of the response parameter Value: Value:Description
    Status: internal
    ----------
    Parameters:
        PathName:str = ""
    ----------
    Response:
        Attributes:int
        DatumCode:int
        ValueDesc:str
    ----------
    Command Timeout: 5000
    Example:GetDatum Chuck:AlignGap
    """
    rsp = MessageServerInterface.sendSciCommand("GetDatum",PathName)
    global GetDatum_Response
    if not "GetDatum_Response" in globals(): GetDatum_Response = namedtuple("GetDatum_Response", "Attributes,DatumCode,ValueDesc")
    return GetDatum_Response(int(rsp[0]),int(rsp[1]),str("" if len(rsp) < 3 else ' '.join(rsp[2:])))

def SetRecoveryDatum(PathNameAndValue=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the value of a parameter. An empty parameter string saves the whole
    configuration to non-volatile memory. Fields are separated by a colon.
    Status: internal
    ----------
    Parameters:
        PathNameAndValue:str = ""
    ----------
    Command Timeout: 5000
    Example:SetRecoveryDatum Chuck:AlignGap:25
    """
    MessageServerInterface.sendSciCommand("SetRecoveryDatum",PathNameAndValue)


def SetZProfilePoint(Stage="", XValue="", YValue="", ZGap="", PosRef="", Unit="", ZProfileType=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Set a point for the Z height profile. If this profile is enabled, the Z height
    depends on a X and Y coordinate. The Z value is a gap to the current Z height.
    Positive values are elevated spots, negative values are hollows. The height
    profile is used to adjust the Z height. The adjusted Z height at a X and Y
    position is derived from the nearest profile point. The Z contact level will be
    calculated from the Contact Height and the stored Z gap at this point.  See
    GetZProfilePoint for details.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        XValue:Decimal = 0
        YValue:Decimal = 0
        ZGap:Decimal = 0
        PosRef:str = "Home"
        Unit:str = "Microns"
        ZProfileType:int = 0
    ----------
    Response:
        ValueCount:int
    ----------
    Command Timeout: 5000
    Example:SetZProfilePoint C 5000 5000 -3 H Y
    """
    rsp = MessageServerInterface.sendSciCommand("SetZProfilePoint",Stage,XValue,YValue,ZGap,PosRef,Unit,ZProfileType)
    return int(rsp[0])

def ReadZProfilePoint(Stage="", Index="", PosRef="", Unit="", ZProfileType=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Get a single point and the corresponding Z gap of the Z height profile.  The
    different z profiles are:  - transient: meant to be used on a per-wafer-basis,
    default - persistent: configured once, stays in memory - persistent-offset: same
    as persistent, active when offset is enabled - scratch: not used internally. Can
    be used to translate KernelDatums <-> ZProfile-Points
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        Index:int = 0
        PosRef:str = "Home"
        Unit:str = "Microns"
        ZProfileType:int = 0
    ----------
    Response:
        XValue:Decimal
        YValue:Decimal
        ZGap:Decimal
        ValueCount:int
    ----------
    Command Timeout: 5000
    Example:ReadZProfilePoint C 1 H
    """
    rsp = MessageServerInterface.sendSciCommand("ReadZProfilePoint",Stage,Index,PosRef,Unit,ZProfileType)
    global ReadZProfilePoint_Response
    if not "ReadZProfilePoint_Response" in globals(): ReadZProfilePoint_Response = namedtuple("ReadZProfilePoint_Response", "XValue,YValue,ZGap,ValueCount")
    return ReadZProfilePoint_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),int(rsp[3]))

def ClearZProfile(Stage="", ZProfileType=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Clears all profile points. See GetZProfile for type description.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        ZProfileType:int = 0
    ----------
    Command Timeout: 5000
    Example:ClearZProfile C
    """
    MessageServerInterface.sendSciCommand("ClearZProfile",Stage,ZProfileType)


def ReadScopeSilo(Index=""):
    """
    Returns the definition of a silo. If the type is rectangle, center means
    _Point1_. If the type is circle, the meaning of Pos2X and Pos2Y is undefined.
    Status: published
    ----------
    Parameters:
        Index:int = 1
    ----------
    Response:
        Type:str
        CenterX:Decimal
        CenterY:Decimal
        Radius:Decimal
        Pos2X:Decimal
        Pos2Y:Decimal
        ZHigh:Decimal
        RefX:Decimal
        RefY:Decimal
        RefZ:Decimal
    ----------
    Command Timeout: 5000
    Example:ReadScopeSilo 1
    """
    rsp = MessageServerInterface.sendSciCommand("ReadScopeSilo",Index)
    global ReadScopeSilo_Response
    if not "ReadScopeSilo_Response" in globals(): ReadScopeSilo_Response = namedtuple("ReadScopeSilo_Response", "Type,CenterX,CenterY,Radius,Pos2X,Pos2Y,ZHigh,RefX,RefY,RefZ")
    return ReadScopeSilo_Response(str(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),Decimal(rsp[5]),Decimal(rsp[6]),Decimal(rsp[7]),Decimal(rsp[8]),Decimal(rsp[9]))

def OpenProjectDialog(ProjectFilename="", Option=""):
    """
    Asks if the current project should be saved and then brings up the Open Project
    window which opens the selected project file if the user clicks ok.
    Status: published
    ----------
    Parameters:
        ProjectFilename:str = ""
        Option:int = 0
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("OpenProjectDialog",ProjectFilename,Option)


def SaveProjectAsDialog():
    """
    Brings up the Save Project window which saves the project if the user clicks ok.
    Status: published
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("SaveProjectAsDialog")


def LoginDialog(LevelToOffer=""):
    """
    Brings up the Login window and sends a New Access Level alert if the user enters
    a valid password.
    Status: published
    ----------
    Parameters:
        LevelToOffer:str = "1"
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("LoginDialog",LevelToOffer)


def GetStatus():
    """
    Returns the current software status. The server holds and maintains the software
    status. Status can be changed by using any of the following commands:
    LoginDialog and SetExternalMode.
    Status: published
    ----------
    Response:
        DummyCommonMode:int
        RunningMode:str
        AccessLevel:str
        ExternalMode:int
        LicenseDaysLeft:int
        MKH:int
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("GetStatus")
    global GetStatus_Response
    if not "GetStatus_Response" in globals(): GetStatus_Response = namedtuple("GetStatus_Response", "DummyCommonMode,RunningMode,AccessLevel,ExternalMode,LicenseDaysLeft,MKH")
    return GetStatus_Response(int(rsp[0]),str(rsp[1]),str(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]))

def LicensingDialog():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Brings up the Licensing window.
    Status: internal
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("LicensingDialog")


def GetLicenseInfo():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the current license information.
    Status: internal
    ----------
    Response:
        AnnualEnabled:int
        AnnualDaysLeft:int
        VeloxProEnabled:int
        VueTrackEnabled:int
        VueTrack4PEnabled:int
        ReAlignEnabled:int
        AutomationEnabled:int
        IdToolsEnabled:int
        IVistaEnabled:int
        IVistaProEnabled:int
        LaserCutterEnabled:int
        SiPToolsEnabled:int
        AutoRfEnabled:int
        SecsGemEnabled:int
        Evue5ProEnabled:int
        Evue5_40XEnabled:int
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("GetLicenseInfo")
    global GetLicenseInfo_Response
    if not "GetLicenseInfo_Response" in globals(): GetLicenseInfo_Response = namedtuple("GetLicenseInfo_Response", "AnnualEnabled,AnnualDaysLeft,VeloxProEnabled,VueTrackEnabled,VueTrack4PEnabled,ReAlignEnabled,AutomationEnabled,IdToolsEnabled,IVistaEnabled,IVistaProEnabled,LaserCutterEnabled,SiPToolsEnabled,AutoRfEnabled,SecsGemEnabled,Evue5ProEnabled,Evue5_40XEnabled")
    return GetLicenseInfo_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]),int(rsp[7]),int(rsp[8]),int(rsp[9]),int(rsp[10]),int(rsp[11]),int(rsp[12]),int(rsp[13]),int(rsp[14]),int(rsp[15]))

def GetProjectFile():
    """
    Returns the current project file.
    Status: published
    ----------
    Response:
        ProjectFilename:str
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("GetProjectFile")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ReportSoftwareVersion():
    """
    Returns the Velox software version as string.
    Status: published
    ----------
    Response:
        SoftwareVersion:str
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("ReportSoftwareVersion")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def OpenProject(ProjectFilename=""):
    """
    The OpenProject command opens the specified project.
    Status: published
    ----------
    Parameters:
        ProjectFilename:str = ""
    ----------
    Command Timeout: 15000
    """
    MessageServerInterface.sendSciCommand("OpenProject",ProjectFilename)


def IsAppRegistered(Application=""):
    """
    Checks the server to see if the application "AppName" is registered with the
    server.
    Status: published
    ----------
    Parameters:
        Application:str = ""
    ----------
    Response:
        IsAppRegistered:int
    ----------
    Command Timeout: 5000
    Example:IsAppRegistered WaferMap
    """
    rsp = MessageServerInterface.sendSciCommand("IsAppRegistered",Application)
    return int(rsp[0])

def SaveProject(ProjectFilename=""):
    """
    Saves the current data to the project file.
    Status: published
    ----------
    Parameters:
        ProjectFilename:str = ""
    ----------
    Command Timeout: 15000
    """
    MessageServerInterface.sendSciCommand("SaveProject",ProjectFilename)


def GetSoftwarePath(PathType=""):
    """
    Returns the path for either the applications/data or project files.
    Status: published
    ----------
    Parameters:
        PathType:str = "User"
    ----------
    Response:
        SoftwarePath:str
    ----------
    Command Timeout: 5000
    Example:GetSoftwarePath User
    """
    rsp = MessageServerInterface.sendSciCommand("GetSoftwarePath",PathType)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def CCSelectLens(Lens=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Internal AZoom Helper Command.
    Status: internal
    ----------
    Parameters:
        Lens:int = 1
    ----------
    Command Timeout: 10000
    Example:CCSelectLens 1
    """
    MessageServerInterface.sendSciCommand("CCSelectLens",Lens)


def CCReadCurrentLens():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Internal AZoom Helper Command. Probably no longer used.
    Status: internal
    ----------
    Response:
        Lens:int
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("CCReadCurrentLens")
    return int(rsp[0])

def CCMoveAuxSite(AuxID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command calls the Kernel command MoveAuxSite to move the Chuck to the
    position of a given AUX Site. For the transfer move a safe height is used. If
    AUX ID is set to 0, the target of the move is the Wafer Site. If the flag 'Auto
    Align by Spectrum' in Velox Settings is True, the Spectrum command AlignAux is
    executed after MoveAuxSite to align the Site automatically. The flag is only
    visible, if the AUX Site type is CalSubstrate and Spectrum is installed. AUX ID
    in the response is the ID of the new active Site.
    Status: internal
    ----------
    Parameters:
        AuxID:int = 1
    ----------
    Command Timeout: 200000
    """
    MessageServerInterface.sendSciCommand("CCMoveAuxSite",AuxID)


def ExecuteCleaningSequence(SequenceName="", AllowMediaReuse="", SkipAlignAux="", SkipReturnMove=""):
    """
    This command moves to the single cleaning Site, executes CleanProbeTip, moves to
    the contact verify Site, and then moves to contact. Returns an error if the
    clean or verify Sites aren't defined.
    Status: published
    ----------
    Parameters:
        SequenceName:str = ""
        AllowMediaReuse:int = 0
        SkipAlignAux:int = 0
        SkipReturnMove:int = 0
    ----------
    Command Timeout: 1800000
    Example:ExecuteCleaningSequence "DeepClean"
    """
    MessageServerInterface.sendSciCommand("ExecuteCleaningSequence",SequenceName,AllowMediaReuse,SkipAlignAux,SkipReturnMove)


def GetAlignmentMode():
    """
    Get the active alignment mode (either on axis or off axis).
    Status: published
    ----------
    Response:
        AlignmentMode:str
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("GetAlignmentMode")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetAlignmentMode(AlignmentMode=""):
    """
    Sets the active alignment mode (either on axis or off axis).
    Status: published
    ----------
    Parameters:
        AlignmentMode:str = "OnAxis"
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("SetAlignmentMode",AlignmentMode)


def GetLoginData(CmdUserName=""):
    """
    Gets the Velox user data: name, full name, group, access level.     If the
    commanded user name is empty, the data of the current user will be returned
    Status: published
    ----------
    Parameters:
        CmdUserName:str = ""
    ----------
    Response:
        UserName:str
        LongUserName:str
        UserGroup:str
        AccessLevel:str
        VeloxLocked:int
    ----------
    Command Timeout: 5000
    Example:GetLoginData
    """
    rsp = MessageServerInterface.sendSciCommand("GetLoginData",CmdUserName)
    global GetLoginData_Response
    if not "GetLoginData_Response" in globals(): GetLoginData_Response = namedtuple("GetLoginData_Response", "UserName,LongUserName,UserGroup,AccessLevel,VeloxLocked")
    return GetLoginData_Response(str(rsp[0]),str(rsp[1]),str(rsp[2]),str(rsp[3]),int(rsp[4]))

def NucleusInitChuck():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Brings up message box to warn user of Chuck initialization for Nucleus stations.
    Allows user to OK/Cancel.
    Status: internal
    ----------
    Command Timeout: 1000
    """
    MessageServerInterface.sendSciCommand("NucleusInitChuck")


def ShutdownVeloxWithSave():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Brings up message box to allow saving project before shutting down Velox. Allows
    user to OK/Cancel. This command returns an error if the shutdown is canceled.
    Status: internal
    ----------
    Command Timeout: 600000
    """
    MessageServerInterface.sendSciCommand("ShutdownVeloxWithSave")


def WinCalAutoCal():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the WinCalAutoCal command to WinCal.
    Status: internal
    ----------
    Command Timeout: 300000
    """
    MessageServerInterface.sendSciCommand("WinCalAutoCal")


def WinCalCheckAutoRFStability(AllowMove=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the WinCalCheckAutoRFStability command to WinCal.
    Status: internal
    ----------
    Parameters:
        AllowMove:int = 0
    ----------
    Response:
        StabilityPassed:int
    ----------
    Command Timeout: 300000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalCheckAutoRFStability",AllowMove)
    return int(rsp[0])

def WinCalCloseRFStabilityReport():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the WinCalCloseRFStabilityReport command to WinCal.
    Status: internal
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("WinCalCloseRFStabilityReport")


def WinCalMoveToIssRef(IssIdx=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the WinCalMoveToIssRef command to WinCal to move to the specified ISS
    reference.     The ISS index is the IssIdxMap index as returned from
    WinCalGetIssListForAuxSite.
    Status: internal
    ----------
    Parameters:
        IssIdx:int = 0
    ----------
    Command Timeout: 60000
    """
    MessageServerInterface.sendSciCommand("WinCalMoveToIssRef",IssIdx)


def WinCalVerifyIssRefLocAtHome(IssIdx=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the WinCalVerifyIssRefLocAtHome command to WinCal and returns AllRefAtHome
    as 1 if stage and Positioners at home.
    Status: internal
    ----------
    Parameters:
        IssIdx:int = 0
    ----------
    Response:
        AllRefAtHome:int
    ----------
    Command Timeout: 60000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalVerifyIssRefLocAtHome",IssIdx)
    return int(rsp[0])

def WinCalGetIssForAuxSite(AuxID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the WinCalGetIssForAuxSite command to WinCal and returns the ISS
    information for the given AUX Site ID.
    Status: internal
    ----------
    Parameters:
        AuxID:int = 0
    ----------
    Response:
        IssIdx:int
        IssPN:str
        IssDescription:str
        IssEnabled:int
        AuxSiteName:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalGetIssForAuxSite",AuxID)
    global WinCalGetIssForAuxSite_Response
    if not "WinCalGetIssForAuxSite_Response" in globals(): WinCalGetIssForAuxSite_Response = namedtuple("WinCalGetIssForAuxSite_Response", "IssIdx,IssPN,IssDescription,IssEnabled,AuxSiteName")
    return WinCalGetIssForAuxSite_Response(int(rsp[0]),str(rsp[1]),str(rsp[2]),int(rsp[3]),str("" if len(rsp) < 5 else ' '.join(rsp[4:])))

def WinCalGetNameAndVersion():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the WinCalGetNameAndVersion command to WinCal.
    Status: internal
    ----------
    Response:
        ServerName:str
        Version:str
        MajorVersion:int
        MinorVersion:int
        Revision:int
        Build:int
    ----------
    Command Timeout: 30000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalGetNameAndVersion")
    global WinCalGetNameAndVersion_Response
    if not "WinCalGetNameAndVersion_Response" in globals(): WinCalGetNameAndVersion_Response = namedtuple("WinCalGetNameAndVersion_Response", "ServerName,Version,MajorVersion,MinorVersion,Revision,Build")
    return WinCalGetNameAndVersion_Response(str(rsp[0]),str(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]))

def WinCalMonitorNoMove():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalMonitorNoMove command to WinCal. Triggers WinCal to measure the
    monitor portion of the current calibration setup.
    Status: internal
    ----------
    Response:
        MonitorPassed:int
    ----------
    Command Timeout: 300000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalMonitorNoMove")
    return int(rsp[0])

def WinCalValidateAdvanced(ProbeSpacing="", ResetTrace="", AllowMove=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalValidateAdvanced command to WinCal. Performs the validation step of
    the currently selected calibration setup.     Resets the model used in WinCal
    for validation.
    Status: internal
    ----------
    Parameters:
        ProbeSpacing:Decimal = 130
        ResetTrace:int = 1
        AllowMove:int = 1
    ----------
    Response:
        ValidationPassed:int
    ----------
    Command Timeout: 300000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalValidateAdvanced",ProbeSpacing,ResetTrace,AllowMove)
    return int(rsp[0])

def WinCalMeasureMonitorReference(AllowMove=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalMeasureMonitorReference command to WinCal.
    Status: internal
    ----------
    Parameters:
        AllowMove:int = 0
    ----------
    Command Timeout: 300000
    """
    MessageServerInterface.sendSciCommand("WinCalMeasureMonitorReference",AllowMove)


def WinCalGetNumValidationPorts():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalGetNumValidationPorts command to WinCal.
    Status: internal
    ----------
    Response:
        NumValidationPorts:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalGetNumValidationPorts")
    return int(rsp[0])

def WinCalSetNumValidationPorts(NumValidationPorts=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalSetNumValidationPorts command to WinCal.
    Status: internal
    ----------
    Parameters:
        NumValidationPorts:int = 2
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("WinCalSetNumValidationPorts",NumValidationPorts)


def WinCalGetNumMonitoringPorts():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalGetNumMonitoringPorts command to WinCal.
    Status: internal
    ----------
    Response:
        NumMonitoringPorts:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalGetNumMonitoringPorts")
    return int(rsp[0])

def WinCalSetNumMonitoringPorts(NumMonitoringPorts=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalSetNumMonitoringPorts command to WinCal.
    Status: internal
    ----------
    Parameters:
        NumMonitoringPorts:int = 2
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("WinCalSetNumMonitoringPorts",NumMonitoringPorts)


def WinCalGetNumRepeatabilityPorts():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalGetNumRepeatabilityPorts command to WinCal.
    Status: internal
    ----------
    Response:
        NumRepeatabilityPorts:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalGetNumRepeatabilityPorts")
    return int(rsp[0])

def WinCalSetNumRepeatabilityPorts(NumRepeatabilityPorts=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalSetNumRepeatabilityPorts command to WinCal.
    Status: internal
    ----------
    Parameters:
        NumRepeatabilityPorts:int = 2
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("WinCalSetNumRepeatabilityPorts",NumRepeatabilityPorts)


def WinCalValidate():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalValidate command to WinCal. Performs the validation step of the
    currently selected calibration setup in WinCal.
    Status: internal
    ----------
    Response:
        ValidationPassed:int
    ----------
    Command Timeout: 300000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalValidate")
    return int(rsp[0])

def WinCalGetValidationSetup(Port=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends CalGetValidationSetup command to WinCal. Returns calibration setup
    parameters.
    Status: internal
    ----------
    Parameters:
        Port:int = 1
    ----------
    Response:
        StandardType:str
        StandardPorts:int
        StandardCompareType:int
        StructureType:str
        PostCorrect:int
        PostCorrectMatching:int
        AutoConfigure:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalGetValidationSetup",Port)
    global WinCalGetValidationSetup_Response
    if not "WinCalGetValidationSetup_Response" in globals(): WinCalGetValidationSetup_Response = namedtuple("WinCalGetValidationSetup_Response", "StandardType,StandardPorts,StandardCompareType,StructureType,PostCorrect,PostCorrectMatching,AutoConfigure")
    return WinCalGetValidationSetup_Response(str(rsp[0]),int(rsp[1]),int(rsp[2]),str(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]))

def WinCalAutoCalNoValidation(ProbeSpacing=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the WinCalAutoCalNoValidation command to WinCal. Performs an AutoCal
    without the validation step
    Status: internal
    ----------
    Parameters:
        ProbeSpacing:Decimal = 130
    ----------
    Command Timeout: 300000
    """
    MessageServerInterface.sendSciCommand("WinCalAutoCalNoValidation",ProbeSpacing)


def WinCalHideAllWindows():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the WinCalHideAllWindows command to WinCal. This minimizes all the WinCal
    windows
    Status: internal
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("WinCalHideAllWindows")


def WinCalGetReferenceStructureInfo(IssIdx=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalGetReferenceStructureInfo command to WinCal. Given the WinCal ISS
    index it will return a string with the reference information
    Status: internal
    ----------
    Parameters:
        IssIdx:int = 0
    ----------
    Response:
        ReferenceInfo:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalGetReferenceStructureInfo",IssIdx)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def WinCalSystemSetupHasUnappliedChanges(ShowErrors=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the WinCalSystemSetupHasUnappliedChanges command to WinCal. Returns true
    if WinCal has unapplied changes
    Status: internal
    ----------
    Parameters:
        ShowErrors:int = 0
    ----------
    Response:
        HasUnappliedChanges:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalSystemSetupHasUnappliedChanges",ShowErrors)
    return int(rsp[0])

def WinCalRecordIssRefAtCurrentLoc(IssIdx=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalRecordIssRefAtCurrentLoc command to WinCal. Record the ISS,
    indicated by the index, reference as being the current location
    Status: internal
    ----------
    Parameters:
        IssIdx:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("WinCalRecordIssRefAtCurrentLoc",IssIdx)


def WinCalGetNumPortsAndProbes():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns Max Ports and Number of probes connected to a port
    Status: internal
    ----------
    Response:
        MaxPorts:int
        NumPortsConnectedtoProbes:int
    ----------
    Command Timeout: 1000
    Example:WinCalGetNumPortsAndProbes
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalGetNumPortsAndProbes")
    global WinCalGetNumPortsAndProbes_Response
    if not "WinCalGetNumPortsAndProbes_Response" in globals(): WinCalGetNumPortsAndProbes_Response = namedtuple("WinCalGetNumPortsAndProbes_Response", "MaxPorts,NumPortsConnectedtoProbes")
    return WinCalGetNumPortsAndProbes_Response(int(rsp[0]),int(rsp[1]))

def WinCalGetProbeInfoForPort(VnaPortNum=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the properties from one probe, based on the passed in index. Pass in a
    physical VNA port number that is less than or equal to Max Probes from the call
    to CalGetNumPortsAndProbes
    Status: internal
    ----------
    Parameters:
        VnaPortNum:int = 1
    ----------
    Response:
        IsSelected:int
        BaseProbe:str
        Options:str
        PhysicalOrient:str
        IsDual:int
        IsSymmetric:int
        SignalConfig:str
        SelectedPitch:int
    ----------
    Command Timeout: 10000
    Example:WinCalGetProbeInfoForPort 1
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalGetProbeInfoForPort",VnaPortNum)
    global WinCalGetProbeInfoForPort_Response
    if not "WinCalGetProbeInfoForPort_Response" in globals(): WinCalGetProbeInfoForPort_Response = namedtuple("WinCalGetProbeInfoForPort_Response", "IsSelected,BaseProbe,Options,PhysicalOrient,IsDual,IsSymmetric,SignalConfig,SelectedPitch")
    return WinCalGetProbeInfoForPort_Response(int(rsp[0]),str(rsp[1]),str(rsp[2]),str(rsp[3]),int(rsp[4]),int(rsp[5]),str(rsp[6]),int(rsp[7]))

def GetMachineState():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Gets the current state of the machine.
    Status: internal
    ----------
    Response:
        MachineState:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetMachineState")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ShowAboutDialog(Pid=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Shows the help about dialog for the given application
    Status: internal
    ----------
    Parameters:
        Pid:int = -1
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("ShowAboutDialog",Pid)


def ShowSplashScreen(Pid="", TimeoutMs=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Shows the splash screen for the given application
    Status: internal
    ----------
    Parameters:
        Pid:int = -1
        TimeoutMs:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("ShowSplashScreen",Pid,TimeoutMs)


def CloseSplashScreen(Pid=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Closes the splash screen for the given application
    Status: internal
    ----------
    Parameters:
        Pid:int = -1
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("CloseSplashScreen",Pid)


def GetLastFourProjects():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the last four project files that were opened.
    Status: internal
    ----------
    Response:
        ProjectFile1:str
        ProjectFile2:str
        ProjectFile3:str
        ProjectFile4:str
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("GetLastFourProjects")
    global GetLastFourProjects_Response
    if not "GetLastFourProjects_Response" in globals(): GetLastFourProjects_Response = namedtuple("GetLastFourProjects_Response", "ProjectFile1,ProjectFile2,ProjectFile3,ProjectFile4")
    return GetLastFourProjects_Response(str(rsp[0]),str(rsp[1]),str(rsp[2]),str("" if len(rsp) < 4 else ' '.join(rsp[3:])))

def WinCalExecuteCommand(Command=""):
    """
    Sends the WinCalExecuteCommand command to WinCal and returns the response
    string.
    Status: published
    ----------
    Parameters:
        Command:str = ""
    ----------
    Response:
        Response:str
    ----------
    Command Timeout: 300000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalExecuteCommand",Command)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def WinCalUseNextGoodGroupOnIss():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Marks the current ISS group as bad and selects the next good one, using WinCal's
    normal criteria.
    Status: internal
    ----------
    Command Timeout: 10000
    Example:WinCalUseNextGoodGroupOnIss
    """
    MessageServerInterface.sendSciCommand("WinCalUseNextGoodGroupOnIss")


def WinCalGetCompleteEnabledIssList():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends the CalGetCompleteIssList command to WinCal. Returns a string with all the
    enabled ISS in WinCal regardless of training or Aux site
    Status: internal
    ----------
    Response:
        IssEnabled:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("WinCalGetCompleteEnabledIssList")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetDemoMode(TurnOnDemoMode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    The DemoMode is not supported anymore. Use ChangeDemoRsp to install a demo mode.
    This command will return an error if its called with any other parameter as 0.
    Status: internal
    ----------
    Parameters:
        TurnOnDemoMode:int = 1
    ----------
    Command Timeout: 5000
    Example:SetDemoMode 0
    """
    MessageServerInterface.sendSciCommand("SetDemoMode",TurnOnDemoMode)


def ChangeDemoRsp(Param=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Override a command with a demo response. The command will not reach its
    destination but the supplied demo response will be returned. An active override
    for a command will be removed if the provided timeout is negative. Format:  [ID]
    [Time] [ErrorCode]:[Response]  - Id: command id in hex without leading 0x -
    Time: time in ms between command and response, negative to reset demo mode for
    this command - Errorcode: 0 for success, everything else indicates an error -
    Response: response string
    Status: internal
    ----------
    Parameters:
        Param:str = ""
    ----------
    Command Timeout: 5000
    Example:ChangeDemoRsp 31 200 0:5000.0 5000.0 8500
    """
    MessageServerInterface.sendSciCommand("ChangeDemoRsp",Param)


def GetDemoMode():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    The DemoMode is not supported anymore. Use ChangeDemoRsp to install a demo mode.
    This command will always return 0.
    Status: internal
    ----------
    Response:
        DemoModeOn:int
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDemoMode")
    return int(rsp[0])

def ResetNetworkPort(Param=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    (Re)sets the IP address and listen port of the socket to which the NetworkDriver
    tries to connect to (IP address and listen port of Kernel socket). Dummy
    implementation for Kernel to support backwards.
    Status: internal
    ----------
    Parameters:
        Param:str = ""
    ----------
    Command Timeout: 10000
    Example:ResetNetworkPort 192.168.3.1 10000
    """
    MessageServerInterface.sendSciCommand("ResetNetworkPort",Param)


def GetNDriverClientStatus(ClientNum="", Param=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Gets status information about the connection NetworkDriver to Kernel. Socket
    Error is the Windows socket error, Description the Windows socket error
    description. If Socket Error is 0, the description 'Registered' informs that the
    Kernel is ready to receive Remote Commands.
    Status: internal
    ----------
    Parameters:
        ClientNum:int = 1
        Param:str = ""
    ----------
    Response:
        Response:str
    ----------
    Command Timeout: 5000
    Example:GetNDriverClientStatus
    """
    rsp = MessageServerInterface.sendSciCommand("GetNDriverClientStatus",ClientNum,Param)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def OverrideCommandTimeout(CmdID="", TimeoutMilliSec=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command allows specifying a separate command timeout for a single instance
    of a command. This is especially useful if the application that receives a
    command knows how long a command will take.  This command had been added for
    SoakTime-handling of StepNextDie. A safe guess for the timeout of StepNextDie is
    5s.
    Status: internal
    ----------
    Parameters:
        CmdID:int = 0
        TimeoutMilliSec:int = 1000
    ----------
    Command Timeout: 5000
    Example:OverrideCommandTimeout 3234 20000
    """
    MessageServerInterface.sendSciCommand("OverrideCommandTimeout",CmdID,TimeoutMilliSec)


def ShutdownVelox(IgnorePID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Shut down all Velox applications in an ordered fashion. When this command
    returns success, all non-mandatory apps are closed and the mandatory ones will
    follow shortly
    Status: internal
    ----------
    Parameters:
        IgnorePID:int = 0
    ----------
    Command Timeout: 120000
    Example:ShutdownVelox
    """
    MessageServerInterface.sendSciCommand("ShutdownVelox",IgnorePID)


def InitializationDone(CommandGroup=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Registration of an application can be delayed. To trigger this behavior,
    RegisterProberApp has to be called with flag 3 set (0x04). From
    RegisterProberApp to the time this command is sent, the application can send
    commands but can't receive commands. This is necessary because some application
    have to communicate with others during initialization and can not handle
    commands properly during this time.  The command group is necessary because of
    architectural reasons (By design, the command receiver does not now the sender
    of a command).
    Status: internal
    ----------
    Parameters:
        CommandGroup:str = ""
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("InitializationDone",CommandGroup)


def CloseTableView():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Closes the TableView application.
    Status: internal
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("CloseTableView")


def StepChuckSite(Site="", UseLabel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Steps the wafer Chuck stage to the requested Site no. of the Chuck table view.
    If no Site number is specified the Chuck will step automatically to the next
    logical site location. The first site in the table is site 1. A label can also
    be specified to move to the first table point with the matching label.
    Status: internal
    ----------
    Parameters:
        Site:str = "-1"
        UseLabel:int = 0
    ----------
    Response:
        SiteRet:int
    ----------
    Command Timeout: 60000
    """
    rsp = MessageServerInterface.sendSciCommand("StepChuckSite",Site,UseLabel)
    return int(rsp[0])

def StepChuckSubsite(Site="", UseLabel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Steps the wafer Chuck stage to the requested Subsite no. of the Chuck subsite
    table view. If no Subsite number is specified the Chuck will step automatically
    to the next logical site location. The first site in the table is site 1. A
    label can also be specified to move to the first table point with the matching
    label.
    Status: internal
    ----------
    Parameters:
        Site:str = "-1"
        UseLabel:int = 0
    ----------
    Response:
        SiteRet:int
    ----------
    Command Timeout: 60000
    """
    rsp = MessageServerInterface.sendSciCommand("StepChuckSubsite",Site,UseLabel)
    return int(rsp[0])

def StepScopeSite(Site="", UseLabel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Steps the microscope stage to the requested Site no. of the Scope table view. If
    no Site number is specified the Scope will step automatically to the next
    logical site location. The first site in the table is site 1. A label can also
    be specified to move to the first table point with the matching label.
    Status: internal
    ----------
    Parameters:
        Site:str = "-1"
        UseLabel:int = 0
    ----------
    Response:
        SiteRet:int
    ----------
    Command Timeout: 60000
    """
    rsp = MessageServerInterface.sendSciCommand("StepScopeSite",Site,UseLabel)
    return int(rsp[0])

def StepProbeSite(Probe="", Site="", UseLabel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Steps the specified probe to the requested Site no. of the Probe no table view.
    If no Site number is specified the Positioner will step automatically to the
    next logical site location. The first site in the table is site 1. A label can
    also be specified to move to the first table point with the matching label.
    Status: internal
    ----------
    Parameters:
        Probe:int = -1
        Site:str = "-1"
        UseLabel:int = 0
    ----------
    Response:
        ProbeRet:int
        SiteRet:int
    ----------
    Command Timeout: 60000
    """
    rsp = MessageServerInterface.sendSciCommand("StepProbeSite",Probe,Site,UseLabel)
    global StepProbeSite_Response
    if not "StepProbeSite_Response" in globals(): StepProbeSite_Response = namedtuple("StepProbeSite_Response", "ProbeRet,SiteRet")
    return StepProbeSite_Response(int(rsp[0]),int(rsp[1]))

def ReadChuckSitePosition(ID="", UseLabel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the actual Chuck site position. The first site in the table is site 1. A
    label can also be specified to read the XY position of the first table entry
    with the matching label.
    Status: internal
    ----------
    Parameters:
        ID:str = "-1"
        UseLabel:int = 0
    ----------
    Response:
        Site:int
        X:Decimal
        Y:Decimal
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("ReadChuckSitePosition",ID,UseLabel)
    global ReadChuckSitePosition_Response
    if not "ReadChuckSitePosition_Response" in globals(): ReadChuckSitePosition_Response = namedtuple("ReadChuckSitePosition_Response", "Site,X,Y")
    return ReadChuckSitePosition_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def ReadScopeSitePosition(ID="", UseLabel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the site position of the specified probe. The first site in the table is
    site 1. A label can also be specified to read the XY position of the first table
    entry with the matching label.
    Status: internal
    ----------
    Parameters:
        ID:str = "-1"
        UseLabel:int = 0
    ----------
    Response:
        Site:int
        X:Decimal
        Y:Decimal
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("ReadScopeSitePosition",ID,UseLabel)
    global ReadScopeSitePosition_Response
    if not "ReadScopeSitePosition_Response" in globals(): ReadScopeSitePosition_Response = namedtuple("ReadScopeSitePosition_Response", "Site,X,Y")
    return ReadScopeSitePosition_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def ReadProbeSitePosition(Probe="", ID="", UseLabel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the site position of the specified probe. The first site in the table is
    site 1. A label can also be specified to read the XY position of the first table
    entry with the matching label.
    Status: internal
    ----------
    Parameters:
        Probe:int = -1
        ID:str = "-1"
        UseLabel:int = 0
    ----------
    Response:
        ProbeRet:int
        Site:int
        X:Decimal
        Y:Decimal
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("ReadProbeSitePosition",Probe,ID,UseLabel)
    global ReadProbeSitePosition_Response
    if not "ReadProbeSitePosition_Response" in globals(): ReadProbeSitePosition_Response = namedtuple("ReadProbeSitePosition_Response", "ProbeRet,Site,X,Y")
    return ReadProbeSitePosition_Response(int(rsp[0]),int(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]))

def ReadChuckSubsitePosition(ID="", UseLabel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the Chuck subsite position. The first site in the table is site 1. A
    label can also be specified to read the XY position of the first table entry
    with the matching label.
    Status: internal
    ----------
    Parameters:
        ID:str = "-1"
        UseLabel:int = 0
    ----------
    Response:
        Site:int
        X:Decimal
        Y:Decimal
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("ReadChuckSubsitePosition",ID,UseLabel)
    global ReadChuckSubsitePosition_Response
    if not "ReadChuckSubsitePosition_Response" in globals(): ReadChuckSubsitePosition_Response = namedtuple("ReadChuckSubsitePosition_Response", "Site,X,Y")
    return ReadChuckSubsitePosition_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def StepFirstDie(ClearBins="", RecalcRoute=""):
    """
    Steps the Chuck to the first die of the wafer map. Returns the row and column
    number of the actual die location after the move is completed. If ClearBins is
    1, all binning data will be cleared from dies. If yes the route will be
    recalculated. All dies marked to skip during the last test (marked to skip with
    SetDieStatus) will be eliminated from the route.
    Status: published
    ----------
    Parameters:
        ClearBins:int = 1
        RecalcRoute:int = 1
    ----------
    Response:
        DieX:int
        DieY:int
        CurSite:int
        LastSiteIndex:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepFirstDie",ClearBins,RecalcRoute)
    global StepFirstDie_Response
    if not "StepFirstDie_Response" in globals(): StepFirstDie_Response = namedtuple("StepFirstDie_Response", "DieX,DieY,CurSite,LastSiteIndex")
    return StepFirstDie_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def StepNextDie(CDieX="", CDieY="", Site=""):
    """
    Steps the chuck to the specified x,y die location of the wafer map. If no
    command data is passed, the chuck automatically steps to the next logical wafer
    map die location. Returns the row and column number of the actual die location
    after the move is completed. In addition, the SubDie location, and total number
    of SubDies is also returned.  If Site (i.e. SubDie) is -1, the chuck will move
    to SubDie 0, on the next die; in this case, the first 2 parameters are ignored.
    If sent without parameters, it will literally 'step to the next die'. When using
    this command from shared code, use SendWithoutParameter().
    Status: published
    ----------
    Parameters:
        CDieX:int = 0
        CDieY:int = 0
        Site:int = 0
    ----------
    Response:
        RDieX:int
        RDieY:int
        CurSite:int
        LastSiteIndex:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepNextDie",CDieX,CDieY,Site)
    global StepNextDie_Response
    if not "StepNextDie_Response" in globals(): StepNextDie_Response = namedtuple("StepNextDie_Response", "RDieX,RDieY,CurSite,LastSiteIndex")
    return StepNextDie_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def BinMapDie(Bin="", CDieX="", CDieY=""):
    """
    Assigns the bin information to the wafer map at the current die, unless a row
    and column is specified. Inks the device if the real time inking option (of the
    wafer map) is enabled.
    Status: published
    ----------
    Parameters:
        Bin:int = 0
        CDieX:int = 0
        CDieY:int = 0
    ----------
    Response:
        RDieX:int
        RDieY:int
    ----------
    Command Timeout: 30000
    Example:BinMapDie 1
    """
    rsp = MessageServerInterface.sendSciCommand("BinMapDie",Bin,CDieX,CDieY)
    global BinMapDie_Response
    if not "BinMapDie_Response" in globals(): BinMapDie_Response = namedtuple("BinMapDie_Response", "RDieX,RDieY")
    return BinMapDie_Response(int(rsp[0]),int(rsp[1]))

def AssignMapBins(Bins=""):
    """
    Assigns the pass or fail information to the actual bin value. Redundant to
    SetBinCode.
    Status: published
    ----------
    Parameters:
        Bins:str = ""
    ----------
    Command Timeout: 10000
    Example:AssignMapBins PFFFFFF
    """
    MessageServerInterface.sendSciCommand("AssignMapBins",Bins)


def StepFailedBack():
    """
    Steps the Chuck back the number of consecutive failed dies (goes back to the
    last known good die) and returns the number of consecutive failed dies.
    Status: published
    ----------
    Response:
        DieIndex:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepFailedBack")
    return int(rsp[0])

def StepFailedForward():
    """
    Steps the Chuck forward the number of consecutive failed dies (goes to next
    untested die).
    Status: published
    ----------
    Response:
        DieIndex:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepFailedForward")
    return int(rsp[0])

def ReadMapPosition(Pos="", FromPos=""):
    """
    Returns the actual Wafer Map Chuck position. The SubDie collection is 1-based,
    the first value is 1, not 0.     CurSite returns the currently selected Subdie
    (1-based) or 0 if no Subdie is currently selected. This command (i.e.
    ReadMapPosition) has been included for legacy support.       ReadMapPosition2 is
    the preferred method for reading Wafer Map Chuck position.
    Status: published
    ----------
    Parameters:
        Pos:int = 0
        FromPos:str = "R"
    ----------
    Response:
        DieX:int
        DieY:int
        XFromHome:Decimal
        YFromHome:Decimal
        CurSite:int
        LastSiteIndex:int
        CurDie:int
        DiesCount:int
        CurCluster:int
        ClustersCount:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("ReadMapPosition",Pos,FromPos)
    global ReadMapPosition_Response
    if not "ReadMapPosition_Response" in globals(): ReadMapPosition_Response = namedtuple("ReadMapPosition_Response", "DieX,DieY,XFromHome,YFromHome,CurSite,LastSiteIndex,CurDie,DiesCount,CurCluster,ClustersCount")
    return ReadMapPosition_Response(int(rsp[0]),int(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]),int(rsp[7]),int(rsp[8]),int(rsp[9]))

def ReadMapYield():
    """
    Returns the actual wafer map yield data information.
    Status: published
    ----------
    Response:
        TotalDies:int
        TestedDies:int
        Passed:int
        Failed:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("ReadMapYield")
    global ReadMapYield_Response
    if not "ReadMapYield_Response" in globals(): ReadMapYield_Response = namedtuple("ReadMapYield_Response", "TotalDies,TestedDies,Passed,Failed")
    return ReadMapYield_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def BinStepDie(Bin="", CDieX="", CDieY="", Site=""):
    """
    Bins the current die and steps the chuck to the next selected die location of
    the wafer map (default) or steps to the specified Column and Row position, if
    these values are passed.  In contrast to StepNextDie, the BinStepDie command
    will only step from die to die while staying on the current subdie. It will not
    step through the subdies so it cannot be used for subdie stepping.
    Status: published
    ----------
    Parameters:
        Bin:int = 0
        CDieX:int = 0
        CDieY:int = 0
        Site:int = 0
    ----------
    Response:
        RDieX:int
        RDieY:int
        CurSite:int
        LastSiteIndex:int
    ----------
    Command Timeout: 6000000
    Example:BinStepDie 1
    """
    rsp = MessageServerInterface.sendSciCommand("BinStepDie",Bin,CDieX,CDieY,Site)
    global BinStepDie_Response
    if not "BinStepDie_Response" in globals(): BinStepDie_Response = namedtuple("BinStepDie_Response", "RDieX,RDieY,CurSite,LastSiteIndex")
    return BinStepDie_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def SetMapHome(DieX="", DieY=""):
    """
    If the command has no parameters it sets the current position as home position
    both for the wafer map and for the Chuck. Otherwise, it changes the wafer map
    home position using the given die coordinates.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetMapHome",DieX,DieY)


def SaveMapFile(FileName="", FileType=""):
    """
    Saves current map file with specified name.
    Status: published
    ----------
    Parameters:
        FileName:str = ""
        FileType:str = "m"
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SaveMapFile",FileName,FileType)


def SetWaferMapMode(Mode=""):
    """
    Enables or disables an external mode for the application. In the external mode,
    all controls are disabled. The application handles all its remote commands in
    both modes. Special interactive modes can also be turned on.
    Status: published
    ----------
    Parameters:
        Mode:str = ""
    ----------
    Response:
        ModeType:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("SetWaferMapMode",Mode)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def GetWaferMapMode(ModeType=""):
    """
    Returns whether the application is in external mode or not.
    Status: published
    ----------
    Parameters:
        ModeType:str = ""
    ----------
    Response:
        Mode:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetWaferMapMode",ModeType)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetWaferNum(Number=""):
    """
    Specifies the wafer number.
    Status: published
    ----------
    Parameters:
        Number:str = "0"
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetWaferNum",Number)


def GetWaferNum():
    """
    Returns the wafer number for the current wafer.
    Status: published
    ----------
    Response:
        Number:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetWaferNum")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetWaferID(ID=""):
    """
    Specifies the ID for the current wafer.
    Status: published
    ----------
    Parameters:
        ID:str = "0"
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetWaferID",ID)


def GetWaferID():
    """
    Returns the wafer ID for the current wafer.
    Status: published
    ----------
    Response:
        ID:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetWaferID")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetProductID(ID=""):
    """
    Specifies the product ID for the current wafer.
    Status: published
    ----------
    Parameters:
        ID:str = "0"
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetProductID",ID)


def GetProductID():
    """
    Displays the product ID for the current wafer.
    Status: published
    ----------
    Response:
        ID:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetProductID")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def DoInkerRun():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Instructs the Wafer Map to perform an ink run on the current wafer. Returns the
    number of dies which were inked during the inker run.
    Status: internal
    ----------
    Response:
        InkedDies:int
    ----------
    Command Timeout: 30000
    """
    rsp = MessageServerInterface.sendSciCommand("DoInkerRun")
    return int(rsp[0])

def CloseWaferMap():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Closes the Wafer Map application.
    Status: internal
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("CloseWaferMap")


def GetNumSelectedDies():
    """
    Gets the number of dies in the map which are selected for probing.
    Status: published
    ----------
    Response:
        SelectedDies:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetNumSelectedDies")
    return int(rsp[0])

def GetSelectedDieCoords(Die=""):
    """
    Given the index of a selected die in the range [1..NumSelectedDies], returns the
    column and row indices for the selected die.
    Status: published
    ----------
    Parameters:
        Die:int = 0
    ----------
    Response:
        DieX:int
        DieY:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSelectedDieCoords",Die)
    global GetSelectedDieCoords_Response
    if not "GetSelectedDieCoords_Response" in globals(): GetSelectedDieCoords_Response = namedtuple("GetSelectedDieCoords_Response", "DieX,DieY")
    return GetSelectedDieCoords_Response(int(rsp[0]),int(rsp[1]))

def StepNextDieOffset(XOffset="", YOffset="", CDieX="", CDieY=""):
    """
    Moves to a user-specified offset within a die. The optional col row params can
    be used to specify the die. If they are omitted, WaferMap moves to the specified
    offset within the next selected die.
    Status: published
    ----------
    Parameters:
        XOffset:Decimal = 0
        YOffset:Decimal = 0
        CDieX:int = 0
        CDieY:int = 0
    ----------
    Response:
        RDieX:int
        RDieY:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepNextDieOffset",XOffset,YOffset,CDieX,CDieY)
    global StepNextDieOffset_Response
    if not "StepNextDieOffset_Response" in globals(): StepNextDieOffset_Response = namedtuple("StepNextDieOffset_Response", "RDieX,RDieY")
    return StepNextDieOffset_Response(int(rsp[0]),int(rsp[1]))

def ReadMapPosition2(Pos="", FromPos=""):
    """
    Returns the actual Wafer Map Chuck position. The SubDie collection is 0-based,
    the first value is 0, not 1. CurSite returns the currently selected Subdie
    (0-based) or -1 if no Subdie is currently selected.  This command is the
    preferred method for reading Wafer Map Chuck position.
    Status: published
    ----------
    Parameters:
        Pos:int = 0
        FromPos:str = "R"
    ----------
    Response:
        DieX:int
        DieY:int
        XFromHome:Decimal
        YFromHome:Decimal
        CurSite:int
        LastSiteIndex:int
        CurDie:int
        DiesCount:int
        CurCluster:int
        ClustersCount:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("ReadMapPosition2",Pos,FromPos)
    global ReadMapPosition2_Response
    if not "ReadMapPosition2_Response" in globals(): ReadMapPosition2_Response = namedtuple("ReadMapPosition2_Response", "DieX,DieY,XFromHome,YFromHome,CurSite,LastSiteIndex,CurDie,DiesCount,CurCluster,ClustersCount")
    return ReadMapPosition2_Response(int(rsp[0]),int(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]),int(rsp[7]),int(rsp[8]),int(rsp[9]))

def DeleteSubDie2(Site=""):
    """
    Deletes selected subdie. The SubDie collection is 0-based, the first value is 0,
    not 1.       This command is the preferred method for deleting a selected
    subdie.
    Status: published
    ----------
    Parameters:
        Site:int = 0
    ----------
    Response:
        SitesCount:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("DeleteSubDie2",Site)
    return int(rsp[0])

def DeleteAllSubDie():
    """
    Deletes all subdies for all dies.
    Status: published
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("DeleteAllSubDie")


def GetDieLabel(DieX="", DieY=""):
    """
    Returns a label from the wafer map at the current die, unless a row and column
    are specified.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
    ----------
    Response:
        Label:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieLabel",DieX,DieY)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetDieLabel(Label="", DieX="", DieY=""):
    """
    Assigns a label to the wafer map at the current die, unless a row and column are
    specified.
    Status: published
    ----------
    Parameters:
        Label:str = ""
        DieX:int = 0
        DieY:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetDieLabel",Label,DieX,DieY)


def StepNextSubDie(Site=""):
    """
    Steps the Chuck to the specified SubDie number relative to the current die
    origin of the wafer map. Returns the SubDie number of the actual die location
    after the move is completed and the total number of subdies.
    Status: published
    ----------
    Parameters:
        Site:int = 0
    ----------
    Response:
        CurSite:int
        LastSiteIndex:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepNextSubDie",Site)
    global StepNextSubDie_Response
    if not "StepNextSubDie_Response" in globals(): StepNextSubDie_Response = namedtuple("StepNextSubDie_Response", "CurSite,LastSiteIndex")
    return StepNextSubDie_Response(int(rsp[0]),int(rsp[1]))

def OpenWaferMap(FileName=""):
    """
    Opens a Wafer Map supported file (.map,.vsd,.stv,.bct,.dpt).
    Status: published
    ----------
    Parameters:
        FileName:str = ""
    ----------
    Command Timeout: 240000
    """
    MessageServerInterface.sendSciCommand("OpenWaferMap",FileName)


def SetDieResult(Result="", DieX="", DieY=""):
    """
    Assigns a measurement result to the wafer map at the current die, unless a row
    and column are specified.
    Status: published
    ----------
    Parameters:
        Result:str = ""
        DieX:int = 0
        DieY:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetDieResult",Result,DieX,DieY)


def GetDieResult(DieX="", DieY=""):
    """
    Returns a measurement result from the wafer map at the current die, unless a row
    and column are specified.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
    ----------
    Response:
        Result:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieResult",DieX,DieY)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetDieMapResult(Result="", DieX="", DieY="", Site=""):
    """
    Assigns a measurement result to the wafer die map at the current die and the
    current subdie, unless a subdie, row and column are specified. The SubDie
    collection is 0-based, the first value is 0, not 1.
    Status: published
    ----------
    Parameters:
        Result:str = ""
        DieX:int = 0
        DieY:int = 0
        Site:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetDieMapResult",Result,DieX,DieY,Site)


def GetDieMapResult(DieX="", DieY="", Site=""):
    """
    Returns a measurement result from the wafer map at the current die and current
    subdie, unless a row, column and subdie are specified. The SubDie collection is
    0-based, the first value is 0, not 1.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
        Site:int = 0
    ----------
    Response:
        Result:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieMapResult",DieX,DieY,Site)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def BinSubDie(Bin="", CDieX="", CDieY="", Site=""):
    """
    Assigns the bin information for the current subdie in the current die, unless a
    subdie, row and column are specified. The SubDie collection is 0-based, the
    first value is 0, not 1.
    Status: published
    ----------
    Parameters:
        Bin:int = 0
        CDieX:int = 0
        CDieY:int = 0
        Site:int = 0
    ----------
    Response:
        RDieX:int
        RDieY:int
        CurSite:int
        LastSiteIndex:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("BinSubDie",Bin,CDieX,CDieY,Site)
    global BinSubDie_Response
    if not "BinSubDie_Response" in globals(): BinSubDie_Response = namedtuple("BinSubDie_Response", "RDieX,RDieY,CurSite,LastSiteIndex")
    return BinSubDie_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def SetSubDieData(Site="", X="", Y="", Label=""):
    """
    Sets up SubDie data. The SubDie collection is 0-based, the first value is 0, not
    1.
    Status: published
    ----------
    Parameters:
        Site:int = 0
        X:Decimal = 0
        Y:Decimal = 0
        Label:str = ""
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSubDieData",Site,X,Y,Label)


def GetSubDieData(Site=""):
    """
    Returns the information of a SubDie. The SubDie collection is 0-based, the first
    value is 0, not 1.
    Status: published
    ----------
    Parameters:
        Site:int = 0
    ----------
    Response:
        CurSite:int
        X:Decimal
        Y:Decimal
        Label:str
        Layout:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSubDieData",Site)
    global GetSubDieData_Response
    if not "GetSubDieData_Response" in globals(): GetSubDieData_Response = namedtuple("GetSubDieData_Response", "CurSite,X,Y,Label,Layout")
    return GetSubDieData_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),str(rsp[3]),str("" if len(rsp) < 5 else ' '.join(rsp[4:])))

def GetMapHome():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command reads the home die location of the Wafer Map.
    Status: internal
    ----------
    Response:
        DieX:int
        DieY:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetMapHome")
    global GetMapHome_Response
    if not "GetMapHome_Response" in globals(): GetMapHome_Response = namedtuple("GetMapHome_Response", "DieX,DieY")
    return GetMapHome_Response(int(rsp[0]),int(rsp[1]))

def GetMapDims():
    """
    Returns the parameters for the current wafer.
    Status: published
    ----------
    Response:
        MapType:str
        XIndex:Decimal
        YIndex:Decimal
        Columns:int
        Rows:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetMapDims")
    global GetMapDims_Response
    if not "GetMapDims_Response" in globals(): GetMapDims_Response = namedtuple("GetMapDims_Response", "MapType,XIndex,YIndex,Columns,Rows")
    return GetMapDims_Response(str(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),int(rsp[3]),int(rsp[4]))

def SetWaferMapParams(Diameter="", DieWidth="", DieHeight="", FlatLength="", FlatAngle="", XOffset="", YOffset="", EdgeArea=""):
    """
    Creates the circle wafer with specified parameters. If parameter is omitted,
    then zero is used. For this version of the command, units for XOffset and
    YOffset are percentages.
    Status: published
    ----------
    Parameters:
        Diameter:Decimal = 200
        DieWidth:Decimal = 10000
        DieHeight:Decimal = 10000
        FlatLength:Decimal = 20
        FlatAngle:int = 0
        XOffset:Decimal = 0
        YOffset:Decimal = 0
        EdgeArea:Decimal = 0
    ----------
    Command Timeout: 240000
    """
    MessageServerInterface.sendSciCommand("SetWaferMapParams",Diameter,DieWidth,DieHeight,FlatLength,FlatAngle,XOffset,YOffset,EdgeArea)


def SetRectMapParams(DieWidth="", DieHeight="", Columns="", Rows=""):
    """
    Creates the rectangle wafer with specified parameters.
    Status: published
    ----------
    Parameters:
        DieWidth:Decimal = 0
        DieHeight:Decimal = 0
        Columns:int = 0
        Rows:int = 0
    ----------
    Command Timeout: 240000
    """
    MessageServerInterface.sendSciCommand("SetRectMapParams",DieWidth,DieHeight,Columns,Rows)


def StepToDie(DieNumber="", Site=""):
    """
    Steps the Chuck to the die location specified by the die number of the wafer
    map. If no command data is passed, the Chuck automatically steps to the next
    logical wafer map die location. Returns the row and column number of the actual
    die location after the move is completed. In addition, the SubDie location and
    total number of SubDies is also returned.
    Status: published
    ----------
    Parameters:
        DieNumber:int = -1
        Site:int = 0
    ----------
    Response:
        RDieX:int
        RDieY:int
        CurSite:int
        LastSiteIndex:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepToDie",DieNumber,Site)
    global StepToDie_Response
    if not "StepToDie_Response" in globals(): StepToDie_Response = namedtuple("StepToDie_Response", "RDieX,RDieY,CurSite,LastSiteIndex")
    return StepToDie_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def GetMapOrientation(UseOrientationCornerForShift=""):
    """
    Returns parameters of the map coordinate system.
    Status: published
    ----------
    Parameters:
        UseOrientationCornerForShift:int = 0
    ----------
    Response:
        Orientation:int
        OriginShiftX:int
        OriginShiftY:int
        UseAlphas:int
        UseIOs:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetMapOrientation",UseOrientationCornerForShift)
    global GetMapOrientation_Response
    if not "GetMapOrientation_Response" in globals(): GetMapOrientation_Response = namedtuple("GetMapOrientation_Response", "Orientation,OriginShiftX,OriginShiftY,UseAlphas,UseIOs")
    return GetMapOrientation_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]))

def SetMapOrientation(Orientation="", OriginShiftX="", OriginShiftY="", UseAlphas="", UseIOs="", UseOrientationCornerForShift=""):
    """
    Sets up new map origin and new coordinate system after that.
    Status: published
    ----------
    Parameters:
        Orientation:int = 0
        OriginShiftX:int = 0
        OriginShiftY:int = 0
        UseAlphas:int = 0
        UseIOs:int = 1
        UseOrientationCornerForShift:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetMapOrientation",Orientation,OriginShiftX,OriginShiftY,UseAlphas,UseIOs,UseOrientationCornerForShift)


def SetDieStatus(DieX="", DieY="", Status=""):
    """
    Sets the die status.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
        Status:str = ""
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetDieStatus",DieX,DieY,Status)


def GetDieStatus(DieX="", DieY=""):
    """
    Gets the die status.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
    ----------
    Response:
        Status:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieStatus",DieX,DieY)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetSubDieStatus(Site="", Status=""):
    """
    Sets the SubDie status. The SubDie collection is 0-based, the first value is 0,
    not 1.
    Status: published
    ----------
    Parameters:
        Site:int = 0
        Status:str = "0"
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSubDieStatus",Site,Status)


def GetSubDieStatus(Site=""):
    """
    Returns the SubDie status. The SubDie collection is 0-based, the first value is
    0, not 1.
    Status: published
    ----------
    Parameters:
        Site:int = 0
    ----------
    Response:
        Status:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSubDieStatus",Site)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def GetBinCode(Bin=""):
    """
    Returns the binning information for a specific bin code.
    Status: published
    ----------
    Parameters:
        Bin:int = 0
    ----------
    Response:
        Chars:str
        Color:int
        Status:str
        Inker1:int
        Inker2:int
        Inker3:int
        Inker4:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetBinCode",Bin)
    global GetBinCode_Response
    if not "GetBinCode_Response" in globals(): GetBinCode_Response = namedtuple("GetBinCode_Response", "Chars,Color,Status,Inker1,Inker2,Inker3,Inker4")
    return GetBinCode_Response(str(rsp[0]),int(rsp[1]),str(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]))

def SetBinCode(Bin="", Chars="", Color="", Status="", Inker1="", Inker2="", Inker3="", Inker4=""):
    """
    Appends the Bin information to a bin code.
    Status: published
    ----------
    Parameters:
        Bin:int = 0
        Chars:str = ""
        Color:int = 0
        Status:str = ""
        Inker1:int = 0
        Inker2:int = 0
        Inker3:int = 0
        Inker4:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetBinCode",Bin,Chars,Color,Status,Inker1,Inker2,Inker3,Inker4)


def GetDieDataAsNum(CDieIndex=""):
    """
    Returns the Die Information in the Row Column format. If the Die Number is
    invalid it returns an error. If the Die Number is absent it uses the current die
    on the wafer.
    Status: published
    ----------
    Parameters:
        CDieIndex:int = 0
    ----------
    Response:
        RDieIndex:int
        DieX:int
        DieY:int
        Bin:int
        Result:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieDataAsNum",CDieIndex)
    global GetDieDataAsNum_Response
    if not "GetDieDataAsNum_Response" in globals(): GetDieDataAsNum_Response = namedtuple("GetDieDataAsNum_Response", "RDieIndex,DieX,DieY,Bin,Result")
    return GetDieDataAsNum_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),str("" if len(rsp) < 5 else ' '.join(rsp[4:])))

def SetDieDataAsNum(DieIndex="", Bin="", Result=""):
    """
    Sets the Die Information. If the Die Number is invalid it returns an error.
    Status: published
    ----------
    Parameters:
        DieIndex:int = 0
        Bin:int = 0
        Result:str = ""
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetDieDataAsNum",DieIndex,Bin,Result)


def GetSubDieDataAsNum(CDieIndex="", Site=""):
    """
    Returns the information of a SubDie. The SubDie collection is 0-based, the first
    value is 0, not 1.
    Status: published
    ----------
    Parameters:
        CDieIndex:int = 0
        Site:int = 0
    ----------
    Response:
        RDieIndex:int
        DieX:int
        DieY:int
        CurSite:int
        Bin:int
        Result:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSubDieDataAsNum",CDieIndex,Site)
    global GetSubDieDataAsNum_Response
    if not "GetSubDieDataAsNum_Response" in globals(): GetSubDieDataAsNum_Response = namedtuple("GetSubDieDataAsNum_Response", "RDieIndex,DieX,DieY,CurSite,Bin,Result")
    return GetSubDieDataAsNum_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),str("" if len(rsp) < 6 else ' '.join(rsp[5:])))

def SetSubDieDataAsNum(DieIndex="", Site="", Bin="", Result=""):
    """
    Sets up SubDie data. The SubDie collection is 0-based, the first value is 0, not
    1.
    Status: published
    ----------
    Parameters:
        DieIndex:int = 0
        Site:int = 0
        Bin:int = 0
        Result:str = ""
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSubDieDataAsNum",DieIndex,Site,Bin,Result)


def GetDieDataAsColRow(CDieX="", CDieY=""):
    """
    Returns the Die Information in the Row Column format. If the Die Number is
    invalid it returns an error. If the Die Column and Row are absent it uses the
    current die on the wafer.
    Status: published
    ----------
    Parameters:
        CDieX:int = 0
        CDieY:int = 0
    ----------
    Response:
        DieIndex:int
        RDieX:int
        RDieY:int
        Bin:int
        Result:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieDataAsColRow",CDieX,CDieY)
    global GetDieDataAsColRow_Response
    if not "GetDieDataAsColRow_Response" in globals(): GetDieDataAsColRow_Response = namedtuple("GetDieDataAsColRow_Response", "DieIndex,RDieX,RDieY,Bin,Result")
    return GetDieDataAsColRow_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),str("" if len(rsp) < 5 else ' '.join(rsp[4:])))

def SetDieDataAsColRow(DieX="", DieY="", Bin="", Result=""):
    """
    Sets the Data in the Row Column format. If the Die is invalid it returns an
    error.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
        Bin:int = 0
        Result:str = ""
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetDieDataAsColRow",DieX,DieY,Bin,Result)


def GetSubDieDataAsColRow(CDieX="", CDieY="", Site=""):
    """
    Returns the information of a SubDie. The SubDie collection is 0-based, the first
    value is 0, not 1.
    Status: published
    ----------
    Parameters:
        CDieX:int = 0
        CDieY:int = 0
        Site:int = 0
    ----------
    Response:
        DieIndex:int
        RDieX:int
        RDieY:int
        CurSite:int
        Bin:int
        Result:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSubDieDataAsColRow",CDieX,CDieY,Site)
    global GetSubDieDataAsColRow_Response
    if not "GetSubDieDataAsColRow_Response" in globals(): GetSubDieDataAsColRow_Response = namedtuple("GetSubDieDataAsColRow_Response", "DieIndex,RDieX,RDieY,CurSite,Bin,Result")
    return GetSubDieDataAsColRow_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),str("" if len(rsp) < 6 else ' '.join(rsp[5:])))

def SetSubDieDataAsColRow(DieX="", DieY="", Site="", Bin="", Result=""):
    """
    Sets up SubDie data. The SubDie collection is 0-based, the first value is 0, not
    1.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
        Site:int = 0
        Bin:int = 0
        Result:str = ""
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSubDieDataAsColRow",DieX,DieY,Site,Bin,Result)


def SelectAllDiesForProbing(DoSelectAll="", DoEdgeDies=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Enables all dies.
    Status: internal
    ----------
    Parameters:
        DoSelectAll:int = 0
        DoEdgeDies:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SelectAllDiesForProbing",DoSelectAll,DoEdgeDies)


def GetMapName():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the current Wafer Map Filename.
    Status: internal
    ----------
    Response:
        Name:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetMapName")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetLotID(ID=""):
    """
    Specifies the ID for the current wafer.
    Status: published
    ----------
    Parameters:
        ID:str = ""
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetLotID",ID)


def GetLotID():
    """
    Returns the Lot ID for the current wafer.
    Status: published
    ----------
    Response:
        ID:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetLotID")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def StepFirstCluster(ClearBins="", RecalcRoute=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Steps the Chuck to the first die cluster of the cluster map. If clusters are not
    defined, the first Die is used. Returns the row and column information of the
    actual cluster and die location after the move is completed. Switches to remote
    control if the "Disable Velox" flag is set in the external options window.
    Status: internal
    ----------
    Parameters:
        ClearBins:int = 1
        RecalcRoute:int = 1
    ----------
    Response:
        ClusterX:int
        ClusterY:int
        ClusterIndex:int
        IncompleteCluster:int
        DieX:int
        DieY:int
        DieIndex:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepFirstCluster",ClearBins,RecalcRoute)
    global StepFirstCluster_Response
    if not "StepFirstCluster_Response" in globals(): StepFirstCluster_Response = namedtuple("StepFirstCluster_Response", "ClusterX,ClusterY,ClusterIndex,IncompleteCluster,DieX,DieY,DieIndex")
    return StepFirstCluster_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]))

def StepNextCluster(CClusterX="", CClusterY=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Steps the Chuck to the specified x,y cluster die location of the cluster map. If
    no command data is passed, the Chuck automatically steps to the next logical
    cluster map location. If clusters are not defined, the Die information is used.
    Returns the row and column number of the actual die location after the move is
    completed.
    Status: internal
    ----------
    Parameters:
        CClusterX:int = 0
        CClusterY:int = 0
    ----------
    Response:
        RClusterX:int
        RClusterY:int
        ClusterIndex:int
        IncompleteCluster:int
        DieX:int
        DieY:int
        DieIndex:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepNextCluster",CClusterX,CClusterY)
    global StepNextCluster_Response
    if not "StepNextCluster_Response" in globals(): StepNextCluster_Response = namedtuple("StepNextCluster_Response", "RClusterX,RClusterY,ClusterIndex,IncompleteCluster,DieX,DieY,DieIndex")
    return StepNextCluster_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]))

def SetMapRoute(MoveMode="", StartColumn="", StartRow="", MoveParam=""):
    """
    Specifies the Move Path for the Probe Station inside the Wafer Map. Optimization
    is done for the shortest move way for the station.
    Status: published
    ----------
    Parameters:
        MoveMode:str = "B"
        StartColumn:str = "L"
        StartRow:str = "T"
        MoveParam:str = "H"
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetMapRoute",MoveMode,StartColumn,StartRow,MoveParam)


def GetMapRoute():
    """
    Returns the specified move path for the Probe Station inside the Wafer Map.
    Status: published
    ----------
    Response:
        MoveMode:str
        StartColumn:str
        StartRow:str
        MoveParam:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetMapRoute")
    global GetMapRoute_Response
    if not "GetMapRoute_Response" in globals(): GetMapRoute_Response = namedtuple("GetMapRoute_Response", "MoveMode,StartColumn,StartRow,MoveParam")
    return GetMapRoute_Response(str(rsp[0]),str(rsp[1]),str(rsp[2]),str("" if len(rsp) < 4 else ' '.join(rsp[3:])))

def SetClusterParams(UseClusters="", ClusterWidth="", ClusterHeight="", TestIncomplete=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Specifies the clusters parameters.
    Status: internal
    ----------
    Parameters:
        UseClusters:int = 0
        ClusterWidth:int = 1
        ClusterHeight:int = 1
        TestIncomplete:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetClusterParams",UseClusters,ClusterWidth,ClusterHeight,TestIncomplete)


def GetClusterParams():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns current clusters parameters.
    Status: internal
    ----------
    Response:
        UseClusters:int
        ClusterWidth:int
        ClusterHeight:int
        TestIncomplete:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetClusterParams")
    global GetClusterParams_Response
    if not "GetClusterParams_Response" in globals(): GetClusterParams_Response = namedtuple("GetClusterParams_Response", "UseClusters,ClusterWidth,ClusterHeight,TestIncomplete")
    return GetClusterParams_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def NewWaferMap():
    """
    Deletes current wafer map, sub dies and binning information; then creates new
    wafer map with defaults parameters.
    Status: published
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("NewWaferMap")


def AddSubDie(X="", Y="", Label=""):
    """
    Adds new subdie at the end of the table.
    Status: published
    ----------
    Parameters:
        X:Decimal = 0
        Y:Decimal = 0
        Label:str = ""
    ----------
    Response:
        SitesCount:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("AddSubDie",X,Y,Label)
    return int(rsp[0])

def DeleteSubDie(Site=""):
    """
    Deletes selected subdie. The SubDie collection is 1-based, the first value is 1,
    not 0. If 0 is passed in as the subdie index, Wafer Map will delete all subdies
    for all dies.This command (i.e. DeleteSubDie) has been included for legacy
    support.       DeleteSubDie2 is the preferred method for deleting a selected
    subdie. DeleteAllSubDie is the preferred method for deleting all subdies for all
    dies.
    Status: published
    ----------
    Parameters:
        Site:int = 0
    ----------
    Response:
        SitesCount:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("DeleteSubDie",Site)
    return int(rsp[0])

def GetNumSelectedClusters():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Gets the number of clusters in the map which are selected for probing.
    Status: internal
    ----------
    Response:
        SelectedClusters:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetNumSelectedClusters")
    return int(rsp[0])

def GetSelectedClusterCoords(ClusterIndex=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Given the index of a selected cluster in the range [1..NumSelectedClusters],
    returns the column and row indices for the selected cluster.
    Status: internal
    ----------
    Parameters:
        ClusterIndex:int = 0
    ----------
    Response:
        ClusterX:int
        ClusterY:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSelectedClusterCoords",ClusterIndex)
    global GetSelectedClusterCoords_Response
    if not "GetSelectedClusterCoords_Response" in globals(): GetSelectedClusterCoords_Response = namedtuple("GetSelectedClusterCoords_Response", "ClusterX,ClusterY")
    return GetSelectedClusterCoords_Response(int(rsp[0]),int(rsp[1]))

def GetClusterDieStatus(ClusterX="", ClusterY="", DieX="", DieY=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Gets the die status in the cluster. Die coordinates are internal for the cluster
    using the wafer map coordinate system. (0,0) die in the cluster is left top
    corner (whether this die exists or not).
    Status: internal
    ----------
    Parameters:
        ClusterX:int = 0
        ClusterY:int = 0
        DieX:int = 0
        DieY:int = 0
    ----------
    Response:
        Status:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetClusterDieStatus",ClusterX,ClusterY,DieX,DieY)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetClusterDieStatus(ClusterX="", ClusterY="", DieX="", DieY="", Status=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the die status in the cluster. Die coordinates are internal for the cluster
    using the wafer map coordinate system. (0,0) die in the cluster is left top
    corner (whether this die exists or not).
    Status: internal
    ----------
    Parameters:
        ClusterX:int = 0
        ClusterY:int = 0
        DieX:int = 0
        DieY:int = 0
        Status:str = ""
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetClusterDieStatus",ClusterX,ClusterY,DieX,DieY,Status)


def OpenBinCodeTable(FileName=""):
    """
    Opens a Bin Code Table file (.bct) with the specified name.
    Status: published
    ----------
    Parameters:
        FileName:str = ""
    ----------
    Command Timeout: 240000
    """
    MessageServerInterface.sendSciCommand("OpenBinCodeTable",FileName)


def SaveBinCodeTable(FileName=""):
    """
    Saves bin code table to a file with the specified name.
    Status: published
    ----------
    Parameters:
        FileName:str = ""
    ----------
    Command Timeout: 240000
    """
    MessageServerInterface.sendSciCommand("SaveBinCodeTable",FileName)


def SetBinTableSize(BinsSize=""):
    """
    Sets size of the bin code table. This is the size of bins used in statistics and
    binning.
    Status: published
    ----------
    Parameters:
        BinsSize:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetBinTableSize",BinsSize)


def GetBinTableSize():
    """
    Gets size of the bin code table.
    Status: published
    ----------
    Response:
        BinsSize:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetBinTableSize")
    return int(rsp[0])

def StepFailedClusterBack():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Steps the Chuck the consecutive failed clusters back (goes back to the last
    known good cluster) and returns the number of consecutive failed clusters.
    Status: internal
    ----------
    Response:
        FailedClusters:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepFailedClusterBack")
    return int(rsp[0])

def StepFailedClusterForward():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Steps the Chuck the consecutive failed clusters forward and returns the number
    of consecutive failed clusters (goes to next untested cluster).
    Status: internal
    ----------
    Response:
        FailedClusters:int
    ----------
    Command Timeout: 6000000
    """
    rsp = MessageServerInterface.sendSciCommand("StepFailedClusterForward")
    return int(rsp[0])

def GoToWaferHome():
    """
    Moves the Chuck to the wafer home position.
    Status: published
    ----------
    Command Timeout: 6000000
    """
    MessageServerInterface.sendSciCommand("GoToWaferHome")


def GetWaferInfo():
    """
    Returns a number of all units marked to test. Note that TestSites is a number of
    all sites for all dies.
    Status: published
    ----------
    Response:
        ClustersCount:int
        DiesCount:int
        SitesCount:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetWaferInfo")
    global GetWaferInfo_Response
    if not "GetWaferInfo_Response" in globals(): GetWaferInfo_Response = namedtuple("GetWaferInfo_Response", "ClustersCount,DiesCount,SitesCount")
    return GetWaferInfo_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]))

def GetClusterInfo(Cluster=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns a number of all dies and sites marked to test in the given cluster.
    Status: internal
    ----------
    Parameters:
        Cluster:int = 0
    ----------
    Response:
        DiesCount:int
        SitesCount:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetClusterInfo",Cluster)
    global GetClusterInfo_Response
    if not "GetClusterInfo_Response" in globals(): GetClusterInfo_Response = namedtuple("GetClusterInfo_Response", "DiesCount,SitesCount")
    return GetClusterInfo_Response(int(rsp[0]),int(rsp[1]))

def GetDieInfo(Die=""):
    """
    Returns a number of sites marked to test in the given die.
    Status: published
    ----------
    Parameters:
        Die:int = 0
    ----------
    Response:
        SitesCount:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieInfo",Die)
    return int(rsp[0])

def SetActiveLayer(Layer=""):
    """
    Sets new active layer.
    Status: published
    ----------
    Parameters:
        Layer:str = ""
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetActiveLayer",Layer)


def GetActiveLayer():
    """
    Returns current active layer.
    Status: published
    ----------
    Response:
        Layer:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetActiveLayer")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetDieRefPoint(RefX="", RefY=""):
    """
    Sets a new reference point for the die. This point is NOT used for die stepping,
    nor for subdie stepping. When using the "Chuck Position from Home" Wafer Map GUI
    setting, the Die Reference Point can be set to be more representative of the
    actual reference location within the die. A setting of (0.0, 0.0) is defined as
    the upper left corner of the die. All subdie coordinates are relative to upper
    left corner of the die.
    Status: published
    ----------
    Parameters:
        RefX:Decimal = 0
        RefY:Decimal = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetDieRefPoint",RefX,RefY)


def GetDieRefPoint():
    """
    Returns current reference point for the die. For details see SetDieRefPoint
    command.
    Status: published
    ----------
    Response:
        RefX:Decimal
        RefY:Decimal
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieRefPoint")
    global GetDieRefPoint_Response
    if not "GetDieRefPoint_Response" in globals(): GetDieRefPoint_Response = namedtuple("GetDieRefPoint_Response", "RefX,RefY")
    return GetDieRefPoint_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def ClearAllBins():
    """
    Clears all binning data in the wafer map.
    Status: published
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("ClearAllBins")


def SetWindowState(State="", Window=""):
    """
    Has sense in the application only (not for ActiveX controls). It shows or hides
    a window. All parameters are case-insensitive.
    Status: published
    ----------
    Parameters:
        State:str = "s"
        Window:str = "setup"
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetWindowState",State,Window)


def SetCurrentBin(Bin="", ButtonStatus=""):
    """
    Sets the current bin for the application. Second parameter allows to enable or
    disable "Mark with Bin" mode in the application.
    Status: published
    ----------
    Parameters:
        Bin:int = 0
        ButtonStatus:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetCurrentBin",Bin,ButtonStatus)


def GetCurrentBin():
    """
    Returns the current bin in the application.
    Status: published
    ----------
    Response:
        Bin:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetCurrentBin")
    return int(rsp[0])

def ReadClusterPosition(Pos="", FromPos=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the actual wafer map cluster position. If the cluster probing is
    disabled, the command will assume a cluster of size 1x1.
    Status: internal
    ----------
    Parameters:
        Pos:int = 0
        FromPos:str = "R"
    ----------
    Response:
        ClusterX:int
        ClusterY:int
        ClusterIndex:int
        DieX:int
        DieY:int
        DieIndex:int
        ClusterWidth:int
        ClusterHeight:int
        EnabledDies:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("ReadClusterPosition",Pos,FromPos)
    global ReadClusterPosition_Response
    if not "ReadClusterPosition_Response" in globals(): ReadClusterPosition_Response = namedtuple("ReadClusterPosition_Response", "ClusterX,ClusterY,ClusterIndex,DieX,DieY,DieIndex,ClusterWidth,ClusterHeight,EnabledDies")
    return ReadClusterPosition_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]),int(rsp[7]),str("" if len(rsp) < 9 else ' '.join(rsp[8:])))

def GetWaferMapParams():
    """
    Returns the circle wafer parameters. For this version of the command, units for
    XOffset and YOffset are percentages.
    Status: published
    ----------
    Response:
        Diameter:Decimal
        DieWidth:Decimal
        DieHeight:Decimal
        FlatLength:Decimal
        FlatAngle:int
        XOffset:Decimal
        YOffset:Decimal
        EdgeArea:Decimal
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetWaferMapParams")
    global GetWaferMapParams_Response
    if not "GetWaferMapParams_Response" in globals(): GetWaferMapParams_Response = namedtuple("GetWaferMapParams_Response", "Diameter,DieWidth,DieHeight,FlatLength,FlatAngle,XOffset,YOffset,EdgeArea")
    return GetWaferMapParams_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),int(rsp[4]),Decimal(rsp[5]),Decimal(rsp[6]),Decimal(rsp[7]))

def GetRectMapParams():
    """
    Creates a rectangular Wafer Map with specified parameters.
    Status: published
    ----------
    Response:
        DieWidth:Decimal
        DieHeight:Decimal
        Columns:int
        Rows:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetRectMapParams")
    global GetRectMapParams_Response
    if not "GetRectMapParams_Response" in globals(): GetRectMapParams_Response = namedtuple("GetRectMapParams_Response", "DieWidth,DieHeight,Columns,Rows")
    return GetRectMapParams_Response(Decimal(rsp[0]),Decimal(rsp[1]),int(rsp[2]),int(rsp[3]))

def AddSubDieWithLayout(X="", Y="", Layout="", Label=""):
    """
    Adds new subdie at the end of the table with the specified Motorized Positioner
    Layout.
    Status: published
    ----------
    Parameters:
        X:Decimal = 0
        Y:Decimal = 0
        Layout:str = ""
        Label:str = ""
    ----------
    Response:
        SitesCount:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("AddSubDieWithLayout",X,Y,Layout,Label)
    return int(rsp[0])

def GetZProfilingStatus():
    """
    Returns a status of the Z-Profiling process. If this status is true it means the
    process is started.
    Status: published
    ----------
    Response:
        Started:int
    ----------
    Command Timeout: 10000
    Example:GetZProfilingStatus
    """
    rsp = MessageServerInterface.sendSciCommand("GetZProfilingStatus")
    return int(rsp[0])

def SyncMapHome(X="", Y=""):
    """
    Tries to find an appropriate position in the wafer for the current Chuck
    position. X and Y describe the Chuck position of the wafer center relatively to
    the Chuck zero position. If the wafer position is found the command sets it as
    the wafer map home position and sets the current Chuck position as the Chuck
    home position. If there is no corresponding wafer position the command returns
    error 701. Command is used by Auto Align for the BuildMap feature.
    Status: published
    ----------
    Parameters:
        X:Decimal = 0
        Y:Decimal = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SyncMapHome",X,Y)


def SetWaferProfileOptions(ProfileSensor="", SearchSpeed="", Gap="", SuccessRatio="", ProfDistX="", ProfDistY=""):
    """
    Sets some Wafer Map profiling options remotely.
    Status: published
    ----------
    Parameters:
        ProfileSensor:str = "e"
        SearchSpeed:Decimal = 50
        Gap:Decimal = 10
        SuccessRatio:Decimal = 75
        ProfDistX:Decimal = 0
        ProfDistY:Decimal = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetWaferProfileOptions",ProfileSensor,SearchSpeed,Gap,SuccessRatio,ProfDistX,ProfDistY)


def GetWaferProfileOptions():
    """
    Returns predefined settings of the Wafer Map profiling options.
    Status: published
    ----------
    Response:
        ProfileSensor:str
        SearchSpeed:Decimal
        Gap:Decimal
        SuccessRatio:Decimal
        ProfDistX:Decimal
        ProfDistY:Decimal
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetWaferProfileOptions")
    global GetWaferProfileOptions_Response
    if not "GetWaferProfileOptions_Response" in globals(): GetWaferProfileOptions_Response = namedtuple("GetWaferProfileOptions_Response", "ProfileSensor,SearchSpeed,Gap,SuccessRatio,ProfDistX,ProfDistY")
    return GetWaferProfileOptions_Response(str(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),Decimal(rsp[5]))

def StartWaferProfiling(DoContinue=""):
    """
    Starts the Z-Profiling process. To determine the current profiling state, use
    GetWaferProfilingStatus command.
    Status: published
    ----------
    Parameters:
        DoContinue:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("StartWaferProfiling",DoContinue)


def GetWaferProfilingStatus():
    """
    Returns status of the Z-Profiling process. If this status is true, the process
    is started.
    Status: published
    ----------
    Response:
        Started:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetWaferProfilingStatus")
    return int(rsp[0])

def StopWaferProfiling():
    """
    Stops the Z-Profiling process.
    Status: published
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("StopWaferProfiling")


def DoWaferProfiling():
    """
    Profiles the wafer and downloads the Z-Profile to the Kernel. Points to be
    profiled are auto-generated when "Load Z-Profile from Map File" is false.
    Status: published
    ----------
    Command Timeout: 36000000
    """
    MessageServerInterface.sendSciCommand("DoWaferProfiling")


def DoWaferProfilingOffAxis():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Profiles the wafer and returns a status of the profiling as an error code.
    Executes profiling using the off axis camera
    Status: internal
    ----------
    Command Timeout: 36000000
    """
    MessageServerInterface.sendSciCommand("DoWaferProfilingOffAxis")


def GetSubDieLabel(DieX="", DieY="", Site=""):
    """
    Returns a label from the wafer map at the current die and current subdie, unless
    a row, column, and subdie are specified. The SubDie collection is 0-based, the
    first value is 0, not 1.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
        Site:int = 0
    ----------
    Response:
        Label:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSubDieLabel",DieX,DieY,Site)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetSubDieLabel(Label="", DieX="", DieY="", Site=""):
    """
    Assigns a label to the wafer map at the current die and the current subdie,
    unless a subdie, row, and column are specified. The SubDie collection is
    0-based, the first value is 0, not 1.
    Status: published
    ----------
    Parameters:
        Label:str = ""
        DieX:int = 0
        DieY:int = 0
        Site:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSubDieLabel",Label,DieX,DieY,Site)


def GetSubDieLabelAsNum(CDieIndex="", Site=""):
    """
    Returns a label from the wafer map the current die and the current subdie,
    unless a subdie, and die number are specified. The SubDie collection is 0-based,
    the first value is 0, not 1.
    Status: published
    ----------
    Parameters:
        CDieIndex:int = 0
        Site:int = 0
    ----------
    Response:
        Label:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSubDieLabelAsNum",CDieIndex,Site)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetSubDieLabelAsNum(Label="", CDieIndex="", Site=""):
    """
    Assigns a label to the wafer map at the current die and the current subdie,
    unless a subdie, and die number are specified. The SubDie collection is 0-based,
    the first value is 0, not 1.
    Status: published
    ----------
    Parameters:
        Label:str = ""
        CDieIndex:int = 0
        Site:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSubDieLabelAsNum",Label,CDieIndex,Site)


def GetDieLabelAsNum(CDieIndex=""):
    """
    Returns a label from the wafer map at the current die, unless a die number is
    specified.
    Status: published
    ----------
    Parameters:
        CDieIndex:int = 0
    ----------
    Response:
        Label:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieLabelAsNum",CDieIndex)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetDieLabelAsNum(Label="", CDieIndex=""):
    """
    Assigns a label to the wafer map at the current die, unless a die number is
    specified.
    Status: published
    ----------
    Parameters:
        Label:str = ""
        CDieIndex:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetDieLabelAsNum",Label,CDieIndex)


def GetHomeDieOffset():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the XY offset from the reference position of the Home Die to wafer
    center in Chuck coordinates.
    Status: internal
    ----------
    Response:
        X:Decimal
        Y:Decimal
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetHomeDieOffset")
    global GetHomeDieOffset_Response
    if not "GetHomeDieOffset_Response" in globals(): GetHomeDieOffset_Response = namedtuple("GetHomeDieOffset_Response", "X,Y")
    return GetHomeDieOffset_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def SaveZProfileFile(FileName=""):
    """
    Saves the current Z-Profile table to the specified .prf file.
    Status: published
    ----------
    Parameters:
        FileName:str = ""
    ----------
    Response:
        NumberOfPoints:int
        NumberOfEPoints:int
    ----------
    Command Timeout: 10000
    Example:SaveZProfileFile Profile1.prf
    """
    rsp = MessageServerInterface.sendSciCommand("SaveZProfileFile",FileName)
    global SaveZProfileFile_Response
    if not "SaveZProfileFile_Response" in globals(): SaveZProfileFile_Response = namedtuple("SaveZProfileFile_Response", "NumberOfPoints,NumberOfEPoints")
    return SaveZProfileFile_Response(int(rsp[0]),int(rsp[1]))

def ReadZProfile():
    """
    Uploads the Z-Profile from the Kernel to the Wafer Map Z-Profile table. Returns
    the number of points.
    Status: published
    ----------
    Response:
        NumberOfPoints:int
    ----------
    Command Timeout: 10000
    Example:ReadZProfile
    """
    rsp = MessageServerInterface.sendSciCommand("ReadZProfile")
    return int(rsp[0])

def SetZProfile():
    """
    Downloads the current Z-Profile table to the Kernel. Returns a number of written
    points.
    Status: published
    ----------
    Response:
        NumberOfPoints:int
    ----------
    Command Timeout: 10000
    Example:SetZProfile
    """
    rsp = MessageServerInterface.sendSciCommand("SetZProfile")
    return int(rsp[0])

def StopZProfiling():
    """
    Stops the profiling process.
    Status: published
    ----------
    Command Timeout: 10000
    Example:StopZProfiling
    """
    MessageServerInterface.sendSciCommand("StopZProfiling")


def OpenZProfileFile(FileName=""):
    """
    Loads the file into the Wafer Map Z-Profile table, but does not download it to
    the Kernel. Use SetZProfile to download.
    Status: published
    ----------
    Parameters:
        FileName:str = ""
    ----------
    Response:
        NumberOfPoints:int
        NumberOfEPoints:int
    ----------
    Command Timeout: 240000
    Example:OpenZProfileFile Profile1.prf
    """
    rsp = MessageServerInterface.sendSciCommand("OpenZProfileFile",FileName)
    global OpenZProfileFile_Response
    if not "OpenZProfileFile_Response" in globals(): OpenZProfileFile_Response = namedtuple("OpenZProfileFile_Response", "NumberOfPoints,NumberOfEPoints")
    return OpenZProfileFile_Response(int(rsp[0]),int(rsp[1]))

def StartZProfiling():
    """
    Starts the Z-Profiling process (see ZProfileWafer). To determine the current
    profiling state, use GetZProfilingStatus.
    Status: published
    ----------
    Command Timeout: 10000
    Example:StartZProfiling
    """
    MessageServerInterface.sendSciCommand("StartZProfiling")


def ZProfileWafer():
    """
    Performs Z-Profilng for the points defined in the Z-Profile table, downloads the
    new Z-Profile to the Kernel, and returns the number of tested points.
    Status: published
    ----------
    Response:
        NumberOfPoints:int
        NumberOfEPoints:int
    ----------
    Command Timeout: 36000000
    Example:ZProfileWafer
    """
    rsp = MessageServerInterface.sendSciCommand("ZProfileWafer")
    global ZProfileWafer_Response
    if not "ZProfileWafer_Response" in globals(): ZProfileWafer_Response = namedtuple("ZProfileWafer_Response", "NumberOfPoints,NumberOfEPoints")
    return ZProfileWafer_Response(int(rsp[0]),int(rsp[1]))

def SetWaferMapParams2(Diameter="", DieWidth="", DieHeight="", FlatLength="", FlatAngle="", XOffset="", YOffset="", EdgeArea=""):
    """
    Creates the circle wafer with specified parameters. If parameter is omitted,
    then zero is used. For this version of the command, units for XOffset and
    YOffset are microns.
    Status: published
    ----------
    Parameters:
        Diameter:Decimal = 200
        DieWidth:Decimal = 10000
        DieHeight:Decimal = 10000
        FlatLength:Decimal = 20
        FlatAngle:int = 0
        XOffset:Decimal = 0
        YOffset:Decimal = 0
        EdgeArea:Decimal = 0
    ----------
    Command Timeout: 240000
    """
    MessageServerInterface.sendSciCommand("SetWaferMapParams2",Diameter,DieWidth,DieHeight,FlatLength,FlatAngle,XOffset,YOffset,EdgeArea)


def GetWaferMapParams2():
    """
    Returns the circle wafer parameters. For this version of the command, units for
    XOffset and YOffset are microns.
    Status: published
    ----------
    Response:
        Diameter:Decimal
        DieWidth:Decimal
        DieHeight:Decimal
        FlatLength:Decimal
        FlatAngle:int
        XOffset:Decimal
        YOffset:Decimal
        EdgeArea:Decimal
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetWaferMapParams2")
    global GetWaferMapParams2_Response
    if not "GetWaferMapParams2_Response" in globals(): GetWaferMapParams2_Response = namedtuple("GetWaferMapParams2_Response", "Diameter,DieWidth,DieHeight,FlatLength,FlatAngle,XOffset,YOffset,EdgeArea")
    return GetWaferMapParams2_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),int(rsp[4]),Decimal(rsp[5]),Decimal(rsp[6]),Decimal(rsp[7]))

def SetWaferTestAngle(Angle=""):
    """
    This command sets the Wafer Test Angle. This is different from the notch angle
    and allows rotating the Wafer Map.
    Status: published
    ----------
    Parameters:
        Angle:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetWaferTestAngle",Angle)


def GetWaferTestAngle():
    """
    This returns the Wafer Test Angle. This is different from the notch angle and
    allows rotating the Wafer Map.
    Status: published
    ----------
    Response:
        Angle:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetWaferTestAngle")
    return int(rsp[0])

def LoadPreMappedDiesTable(FileName="", ClearMap=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Loads the Pre-Mapped Dies Table file with specified name.
    Status: internal
    ----------
    Parameters:
        FileName:str = ""
        ClearMap:int = 1
    ----------
    Command Timeout: 240000
    """
    MessageServerInterface.sendSciCommand("LoadPreMappedDiesTable",FileName,ClearMap)


def GetPreMappedDieInfo(DieX="", DieY=""):
    """
    This command is valid when a PreMapped Dies Table has been loaded. Returns
    values at the current die, unless a column (M_pnDieX) and row (M_pnDieY) are
    specified.  Returns actual (as measured during the Pre-Mapping) x, y, z, and
    theta die positions. Also returns whether or not Z and Theta are being used.
    This command is only valid when a Pre-Mapped Dies Table has been loaded. If a
    PreMapped Dies Table has NOT been loaded, ERR_IllegalParameters (715) is
    returned.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
    ----------
    Response:
        UseZ:int
        UseTheta:int
        ActualX:Decimal
        ActualY:Decimal
        ActualZ:Decimal
        Theta:Decimal
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetPreMappedDieInfo",DieX,DieY)
    global GetPreMappedDieInfo_Response
    if not "GetPreMappedDieInfo_Response" in globals(): GetPreMappedDieInfo_Response = namedtuple("GetPreMappedDieInfo_Response", "UseZ,UseTheta,ActualX,ActualY,ActualZ,Theta")
    return GetPreMappedDieInfo_Response(int(rsp[0]),int(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),Decimal(rsp[5]))

def GetDieResultAsNum(CDieIndex=""):
    """
    Returns a measurement result from the wafer map at the current die, unless a die
    number is specified.
    Status: published
    ----------
    Parameters:
        CDieIndex:int = 0
    ----------
    Response:
        Result:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieResultAsNum",CDieIndex)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetDieResultAsNum(Result="", CDieIndex=""):
    """
    Assigns a measurement result to the wafer map at the current die, unless a die
    number is specified.
    Status: published
    ----------
    Parameters:
        Result:str = ""
        CDieIndex:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetDieResultAsNum",Result,CDieIndex)


def GetDieMapResultAsNum(CDieIndex="", Site=""):
    """
    Returns a measurement result from the wafer map the current die and the current
    subdie, unless a subdie and die number are specified. The SubDie collection is
    0-based, the first value is 0, not 1.
    Status: published
    ----------
    Parameters:
        CDieIndex:int = 0
        Site:int = 0
    ----------
    Response:
        Result:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetDieMapResultAsNum",CDieIndex,Site)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetDieMapResultAsNum(Result="", CDieIndex="", Site=""):
    """
    Assigns a measurement result to the wafer die map at the current die at the
    current subdie, unless a subdie and die number are specified. The SubDie
    collection is 0-based, the first value is 0, not 1.
    Status: published
    ----------
    Parameters:
        Result:str = ""
        CDieIndex:int = 0
        Site:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetDieMapResultAsNum",Result,CDieIndex,Site)


def MapEdgeDies(Enable=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Enables or disables edge dies for test
    Status: internal
    ----------
    Parameters:
        Enable:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("MapEdgeDies",Enable)


def AddSubDieWithLayoutPosition(X="", Y="", Label="", P1X="", P1Y="", P1InUse="", P2X="", P2Y="", P2InUse="", P3X="", P3Y="", P3InUse="", P4X="", P4Y="", P4InUse="", P5X="", P5Y="", P5InUse="", P6X="", P6Y="", P6InUse=""):
    """
    Adds new subdie at the end of the table with the Motorized Positioner Layout
    corresponding to the positions. The Layout must already exist.
    Status: published
    ----------
    Parameters:
        X:Decimal = 0
        Y:Decimal = 0
        Label:str = ""
        P1X:Decimal = 0
        P1Y:Decimal = 0
        P1InUse:int = 1
        P2X:Decimal = 0
        P2Y:Decimal = 0
        P2InUse:int = 1
        P3X:Decimal = 0
        P3Y:Decimal = 0
        P3InUse:int = 1
        P4X:Decimal = 0
        P4Y:Decimal = 0
        P4InUse:int = 1
        P5X:Decimal = 0
        P5Y:Decimal = 0
        P5InUse:int = 1
        P6X:Decimal = 0
        P6Y:Decimal = 0
        P6InUse:int = 1
    ----------
    Response:
        SitesCount:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("AddSubDieWithLayoutPosition",X,Y,Label,P1X,P1Y,P1InUse,P2X,P2Y,P2InUse,P3X,P3Y,P3InUse,P4X,P4Y,P4InUse,P5X,P5Y,P5InUse,P6X,P6Y,P6InUse)
    return int(rsp[0])

def GetSpectrumData(DataPath=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Allows access to read any data item in Spectrum explorer.     GetSpectrumData
    AlignWafer/ProjectData/Mark1/ChuckPosition/X     GetSpectrumData Chuck
    Camera/Camera Settings/Shutter
    Status: internal
    ----------
    Parameters:
        DataPath:str = ""
    ----------
    Response:
        Value:str
    ----------
    Command Timeout: 10000
    Example:GetSpectrumData Chuck Camera/Camera Settings/Shutter
    """
    rsp = MessageServerInterface.sendSciCommand("GetSpectrumData",DataPath)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetSpectrumData(PathAndValue=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Allows changing any data item in Spectrum explorer. Works independent of access
    level. SetSpectrumData AlignWafer/ProjectData/Mark1/ChuckPosition/X=1000
    SetSpectrumData Chuck Camera/Camera Settings/Shutter=17
    Status: internal
    ----------
    Parameters:
        PathAndValue:str = ""
    ----------
    Command Timeout: 6000
    Example:SetSpectrumData Scope Camera/Camera Settings/Shutter=17
    """
    MessageServerInterface.sendSciCommand("SetSpectrumData",PathAndValue)


def ReadVMPosition(ToolName="", XY="", Z="", Model=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command reads the current Chuck and microscope position and sets them as
    new model or Chuck and microscope positions.     within Spectrum Vision.
    Status: internal
    ----------
    Parameters:
        ToolName:str = ""
        XY:int = 1
        Z:int = 0
        Model:int = -1
    ----------
    Command Timeout: 60000
    Example:ReadVMPosition AlignWafer 1 0 0
    """
    MessageServerInterface.sendSciCommand("ReadVMPosition",ToolName,XY,Z,Model)


def MoveToVMPosition(ToolName="", XYChuck="", ZChuck="", XYScope="", ZScope="", Model=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command moves to trained stages positions of a requested tool. Supported
    tools are AutoAlign, AlignWafer and ReAlignWizard.
    Status: internal
    ----------
    Parameters:
        ToolName:str = ""
        XYChuck:int = 1
        ZChuck:int = 1
        XYScope:int = 0
        ZScope:int = 0
        Model:int = -1
    ----------
    Command Timeout: 120000
    Example:MoveToVMPosition AlignWafer 1 0 0 0 0
    """
    MessageServerInterface.sendSciCommand("MoveToVMPosition",ToolName,XYChuck,ZChuck,XYScope,ZScope,Model)


def DetectWaferHeight(SetStartPosition="", Synchronize="", ChuckX="", ChuckY=""):
    """
    Synchronizes Chuck and top camera in X, Y and Z. Then the wafer surface is
    focused on the trained Chuck position or the manual adjusted reference position.
    Status: published
    ----------
    Parameters:
        SetStartPosition:int = 0
        Synchronize:int = 0
        ChuckX:Decimal = -1
        ChuckY:Decimal = -1
    ----------
    Response:
        PositionX:Decimal
        PositionY:Decimal
        WaferHeight:Decimal
        SynchGap:Decimal
        ZOffset:Decimal
        Stage:str
    ----------
    Command Timeout: 300000
    Example:DetectWaferHeight 0 1
    """
    rsp = MessageServerInterface.sendSciCommand("DetectWaferHeight",SetStartPosition,Synchronize,ChuckX,ChuckY)
    global DetectWaferHeight_Response
    if not "DetectWaferHeight_Response" in globals(): DetectWaferHeight_Response = namedtuple("DetectWaferHeight_Response", "PositionX,PositionY,WaferHeight,SynchGap,ZOffset,Stage")
    return DetectWaferHeight_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),str("" if len(rsp) < 6 else ' '.join(rsp[5:])))

def SetG85FileOptions(BinDataFormat="", NullBin="", DataDelimiter="", UseSubdieData="", SubdieIndex=""):
    """
    Set G85 file data format options.
    Status: published
    ----------
    Parameters:
        BinDataFormat:str = "Decimal"
        NullBin:str = "255"
        DataDelimiter:str = ","
        UseSubdieData:int = 0
        SubdieIndex:int = 0
    ----------
    Command Timeout: 100000
    """
    MessageServerInterface.sendSciCommand("SetG85FileOptions",BinDataFormat,NullBin,DataDelimiter,UseSubdieData,SubdieIndex)


def SetSubDieDataWithLayout(Site="", X="", Y="", Layout="", Label=""):
    """
    Sets up SubDie data with layout name. The SubDie collection is 0-based, the
    first value is 0, not 1.
    Status: published
    ----------
    Parameters:
        Site:int = 0
        X:Decimal = 0
        Y:Decimal = 0
        Layout:str = ""
        Label:str = ""
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSubDieDataWithLayout",Site,X,Y,Layout,Label)


def CheckSpectrumPlugin(Plugin=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command checks if a tool is trained and returns a string of error/warning
    messages including information about what is not trained, setup for the tool to
    run.
    Status: internal
    ----------
    Parameters:
        Plugin:str = ""
    ----------
    Response:
        PluginAvailable:int
        Message:str
    ----------
    Command Timeout: 10000
    Example:CheckSpectrumPlugin AlignWafer
    """
    rsp = MessageServerInterface.sendSciCommand("CheckSpectrumPlugin",Plugin)
    global CheckSpectrumPlugin_Response
    if not "CheckSpectrumPlugin_Response" in globals(): CheckSpectrumPlugin_Response = namedtuple("CheckSpectrumPlugin_Response", "PluginAvailable,Message")
    return CheckSpectrumPlugin_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def AutoAlign(SetValue="", SkipSettingHome=""):
    """
    Executes the AutoAlign tool to do a theta alignment of the wafer with optional
    index calculation or thermal expansion measurement. The command will update home
    if home was trained. It will only move to its trained chuck/scope position
    before starting the alignment if the option "MoveToTrainedXYPosition" and/or
    "MoveToTrainedZPosition" is true.
    Status: published
    ----------
    Parameters:
        SetValue:int = 0
        SkipSettingHome:int = 0
    ----------
    Command Timeout: 300000
    Example:AutoAlign 1
    """
    MessageServerInterface.sendSciCommand("AutoAlign",SetValue,SkipSettingHome)


def SetCameraQuiet(Active=""):
    """
    Activates/deactivates the camera quiet mode. (Applies only to CM300/SUMMIT200
    stations.)     The camera quiet mode deactivates the Chuck, Platen and Contact
    View camera and triggers a digital output     which connects/disconnects these
    cameras firewire/USB connection to the PC.
    Status: published
    ----------
    Parameters:
        Active:int = 0
    ----------
    Command Timeout: 60000
    Example:SetCameraQuiet 1
    """
    MessageServerInterface.sendSciCommand("SetCameraQuiet",Active)


def SetRefDieOffset(RefDieCol="", RefDieRow="", RefDieDistToCentreX="", RefDieDistToCentreY=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command is based on the SetMapOrientation command. It allows shifting the
    center of the Home die to the center of the wafer.
    Status: internal
    ----------
    Parameters:
        RefDieCol:int = 0
        RefDieRow:int = 0
        RefDieDistToCentreX:Decimal = 0
        RefDieDistToCentreY:Decimal = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetRefDieOffset",RefDieCol,RefDieRow,RefDieDistToCentreX,RefDieDistToCentreY)


def GetUsePositionerSubdie():
    """
    Returns whether or not Wafer Map is configured to use motorized positioners for
    subdie stepping.
    Status: published
    ----------
    Response:
        UsePositionerSubdie:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetUsePositionerSubdie")
    return int(rsp[0])

def SetSelectiveDieAlignmentMode(UseSelectiveDieAlignment=""):
    """
    Enable/disable the selective die alignment mode.
    Status: published
    ----------
    Parameters:
        UseSelectiveDieAlignment:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSelectiveDieAlignmentMode",UseSelectiveDieAlignment)


def GetSelectiveDieAlignmentMode():
    """
    Returns the selective die alignment mode status.
    Status: published
    ----------
    Response:
        UseSelectiveDieAlignment:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSelectiveDieAlignmentMode")
    return int(rsp[0])

def SetSelectiveDieAlignmentDieStatus(DieX="", DieY="", DoAlign=""):
    """
    Enable/disable selective die alignment for the given die.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
        DoAlign:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSelectiveDieAlignmentDieStatus",DieX,DieY,DoAlign)


def GetSelectiveDieAlignmentDieStatus(DieX="", DieY=""):
    """
    Get the selective die alignment status for the given die.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
    ----------
    Response:
        DoAlign:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSelectiveDieAlignmentDieStatus",DieX,DieY)
    return int(rsp[0])

def SetSelectiveDieSoakingMode(UseSelectiveDieSoaking=""):
    """
    Enable/disable the selective die soaking mode.
    Status: published
    ----------
    Parameters:
        UseSelectiveDieSoaking:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSelectiveDieSoakingMode",UseSelectiveDieSoaking)


def GetSelectiveDieSoakingMode():
    """
    Returns the selective die soaking mode status.
    Status: published
    ----------
    Response:
        UseSelectiveDieSoaking:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSelectiveDieSoakingMode")
    return int(rsp[0])

def SetSelectiveDieSoakingDieStatus(DieX="", DieY="", DoSoaking=""):
    """
    Enable/disable selective die soaking for the given die.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
        DoSoaking:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetSelectiveDieSoakingDieStatus",DieX,DieY,DoSoaking)


def GetSelectiveDieSoakingDieStatus(DieX="", DieY=""):
    """
    Get the selective die soaking status for the given die.
    Status: published
    ----------
    Parameters:
        DieX:int = 0
        DieY:int = 0
    ----------
    Response:
        DoSoaking:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSelectiveDieSoakingDieStatus",DieX,DieY)
    return int(rsp[0])

def GetVisionAssistedSteppingActive():
    """
    Command to tell if Vision Assisted Stepping is active.
    Status: published
    ----------
    Response:
        Active:int
    ----------
    Command Timeout: 10000
    Example:GetVisionAssistedSteppingActive
    """
    rsp = MessageServerInterface.sendSciCommand("GetVisionAssistedSteppingActive")
    return int(rsp[0])

def SetVisionAssistedSteppingActive(Activate=""):
    """
    Command to set if Vision Assisted Stepping is active. Command can be used to
    e.g. deactivate Vision Assisted Stepping     programmatically in case it is no
    longer used.     When activating Vision Assisted Stepping, the command will
    return an error in case it is not possible (e.g. not trained)
    Status: published
    ----------
    Parameters:
        Activate:int = 0
    ----------
    Command Timeout: 10000
    Example:SetVisionAssistedSteppingActive 1
    """
    MessageServerInterface.sendSciCommand("SetVisionAssistedSteppingActive",Activate)


def SetUsePositionerSubdie(UsePositionerSubdie=""):
    """
    Sets whether or not Wafer Map is configured to use motorized positioners for
    subdie stepping.
    Status: published
    ----------
    Parameters:
        UsePositionerSubdie:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetUsePositionerSubdie",UsePositionerSubdie)


def GetLocalSubDieStatus(Site="", DieX="", DieY=""):
    """
    Returns the Die Local SubDie status, per-die basis.
    Status: published
    ----------
    Parameters:
        Site:int = 0
        DieX:int = 0
        DieY:int = 0
    ----------
    Response:
        CurSite:int
        Status:int
        RDieX:int
        RDieY:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetLocalSubDieStatus",Site,DieX,DieY)
    global GetLocalSubDieStatus_Response
    if not "GetLocalSubDieStatus_Response" in globals(): GetLocalSubDieStatus_Response = namedtuple("GetLocalSubDieStatus_Response", "CurSite,Status,RDieX,RDieY")
    return GetLocalSubDieStatus_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def GetLocalSubDieStatusAsNum(Site="", DieIndex=""):
    """
    Returns the Die Local SubDie status, per-die basis.
    Status: published
    ----------
    Parameters:
        Site:int = 0
        DieIndex:int = 0
    ----------
    Response:
        CurSite:int
        RStatus:int
        RDieIndex:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetLocalSubDieStatusAsNum",Site,DieIndex)
    global GetLocalSubDieStatusAsNum_Response
    if not "GetLocalSubDieStatusAsNum_Response" in globals(): GetLocalSubDieStatusAsNum_Response = namedtuple("GetLocalSubDieStatusAsNum_Response", "CurSite,RStatus,RDieIndex")
    return GetLocalSubDieStatusAsNum_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]))

def SetLocalSubDieStatus(Site="", Status="", DieX="", DieY=""):
    """
    Enables Local SubDies and sets the Die Local SubDie status, per-die basis.
    Status: published
    ----------
    Parameters:
        Site:int = 0
        Status:int = 1
        DieX:int = 0
        DieY:int = 0
    ----------
    Response:
        CurSite:int
        RStatus:int
        RDieX:int
        RDieY:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("SetLocalSubDieStatus",Site,Status,DieX,DieY)
    global SetLocalSubDieStatus_Response
    if not "SetLocalSubDieStatus_Response" in globals(): SetLocalSubDieStatus_Response = namedtuple("SetLocalSubDieStatus_Response", "CurSite,RStatus,RDieX,RDieY")
    return SetLocalSubDieStatus_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def SetLocalSubDieStatusAsNum(Site="", Status="", DieIndex=""):
    """
    Enables Local SubDies and sets the Die Local SubDie status, per-die basis.
    Status: published
    ----------
    Parameters:
        Site:int = 0
        Status:int = 1
        DieIndex:int = 0
    ----------
    Response:
        CurSite:int
        RStatus:int
        RDieIndex:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("SetLocalSubDieStatusAsNum",Site,Status,DieIndex)
    global SetLocalSubDieStatusAsNum_Response
    if not "SetLocalSubDieStatusAsNum_Response" in globals(): SetLocalSubDieStatusAsNum_Response = namedtuple("SetLocalSubDieStatusAsNum_Response", "CurSite,RStatus,RDieIndex")
    return SetLocalSubDieStatusAsNum_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]))

def AlignWafer(TrackPosition=""):
    """
    Performs a two-point alignment and moves Chuck to the trained align position. XY
    correction is made afterwards to calculate the new home position.
    Status: published
    ----------
    Parameters:
        TrackPosition:int = 0
    ----------
    Response:
        ThetaOffset:Decimal
    ----------
    Command Timeout: 120000
    Example:AlignWafer
    """
    rsp = MessageServerInterface.sendSciCommand("AlignWafer",TrackPosition)
    return Decimal(rsp[0])

def AlignChip():
    """
    Performs a single or two point alignment and moves the current chip to the
    trained aligned position in Theta (in degrees) and X, Y (in microns). The
    current chip is assumed to be in the region of interest when the command is
    called.
    Status: published
    ----------
    Response:
        ThetaOffset:Decimal
        XOffset:Decimal
        YOffset:Decimal
    ----------
    Command Timeout: 180000
    Example:AlignChip
    """
    rsp = MessageServerInterface.sendSciCommand("AlignChip")
    global AlignChip_Response
    if not "AlignChip_Response" in globals(): AlignChip_Response = namedtuple("AlignChip_Response", "ThetaOffset,XOffset,YOffset")
    return AlignChip_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def FindFocus(StepCount="", Range=""):
    """
    Determines the Z axis position where an object in the region of interest is in
    focus. First output parameter is the Z axis value in microns from zero of the
    new focus height. Second output parameter is the used stage to perform focus
    search.
    Status: published
    ----------
    Parameters:
        StepCount:int = -1
        Range:Decimal = -1
    ----------
    Response:
        ZPosition:Decimal
        Stage:str
    ----------
    Command Timeout: 120000
    Example:FindFocus 50 500
    """
    rsp = MessageServerInterface.sendSciCommand("FindFocus",StepCount,Range)
    global FindFocus_Response
    if not "FindFocus_Response" in globals(): FindFocus_Response = namedtuple("FindFocus_Response", "ZPosition,Stage")
    return FindFocus_Response(Decimal(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def AlignAux(AuxSiteID=""):
    """
    Performs an automated AUX Site alignment in XYZ. Tool can correct reference
    position and Contact Height for the given AUX Site.
    Status: published
    ----------
    Parameters:
        AuxSiteID:int = 0
    ----------
    Command Timeout: 300000
    Example:AlignAux 1
    """
    MessageServerInterface.sendSciCommand("AlignAux",AuxSiteID)


def FindFeature(Model="", ReturnDistanceFromModelOrigin="", UseSingleImageAcquisition=""):
    """
    Search user-defined models. Up to 40 different models can be trained. After
    training, these models can be searched on screen either by direct user
    interaction or from external applications with a remote command. The remote
    command returns the X/Y-Positions, angle (degree) and score value (0 - 1.0) for
    each instance of the model found in the region of interest.
    Status: published
    ----------
    Parameters:
        Model:int = 1
        ReturnDistanceFromModelOrigin:int = 0
        UseSingleImageAcquisition:int = 1
    ----------
    Response:
        Data:str
    ----------
    Command Timeout: 10000
    Example:FindFeature 1
    """
    rsp = MessageServerInterface.sendSciCommand("FindFeature",Model,ReturnDistanceFromModelOrigin,UseSingleImageAcquisition)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def CloseSpectrum():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    CloseSpectrum closes the Spectrum Vision application. Used internally by
    CommonCommands during Project loading. Does save configuration data but does not
    save project data.
    Status: internal
    ----------
    Command Timeout: 10000
    Example:CloseSpectrum
    """
    MessageServerInterface.sendSciCommand("CloseSpectrum")


def SnapImage(MountPos="", FullPath="", SnapShotMode="", DecimationFactor=""):
    """
    Saves the currently displayed image to the specified file. The image is stored
    in the requested file format (bmp, jpg or png). By default. it will save the raw
    camera image and an image with the overlays that are currently visible on the
    camera view. Using a parameter, one can decide to only save either raw image,
    overlay image or both. By Specifying 'ALL' as the mount position, the captured
    screenshot will consist of the currently selected camera layout without
    providing the raw image. If MountPos and FullPath are empty then the current
    camera view with overlays is copied to the clipboard.
    Status: published
    ----------
    Parameters:
        MountPos:str = "Scope"
        FullPath:str = "Image.bmp"
        SnapShotMode:int = 2
        DecimationFactor:int = 1
    ----------
    Command Timeout: 60000
    Example:SnapImage Scope C:/Temp/Image.bmp
    """
    MessageServerInterface.sendSciCommand("SnapImage",MountPos,FullPath,SnapShotMode,DecimationFactor)


def SetCameraView(Name="", Zoom="", LiveVideo="", WindowState=""):
    """
    Switches the desired video window of Spectrum as foreground and active view. The
    camera view can be determined over a tool name or the camera mount position. The
    second parameter defines the displays zoom factor to be used. Third parameter is
    used to toggle the live video. Last parameter can be used to maximize a window
    or to simply remove temporary on-screen items.
    Status: published
    ----------
    Parameters:
        Name:str = ""
        Zoom:int = 0
        LiveVideo:int = 2
        WindowState:int = 1
    ----------
    Command Timeout: 10000
    Example:SetCameraView AlignWafer 0 2 2
    """
    MessageServerInterface.sendSciCommand("SetCameraView",Name,Zoom,LiveVideo,WindowState)


def SetCameraLight(Name="", State="", Shutter="", Gain="", Brightness="", Contrast="", Sharpness="", Illumination=""):
    """
    Switches the light of the chosen camera on or off. Light values of -1 will cause
    that the parameter is not affected.
    Status: published
    ----------
    Parameters:
        Name:str = ""
        State:int = 0
        Shutter:Decimal = -1
        Gain:Decimal = -1
        Brightness:int = -1
        Contrast:int = -1
        Sharpness:int = -1
        Illumination:int = -1
    ----------
    Command Timeout: 10000
    Example:SetCameraLight AlignWafer 1 20 5
    """
    MessageServerInterface.sendSciCommand("SetCameraLight",Name,State,Shutter,Gain,Brightness,Contrast,Sharpness,Illumination)


def ShowWizard(ToolName="", MountPosition=""):
    """
    Starts the wizard of a given tool on the display defined in the tool settings.
    Additionally it can start a wizard for training single models with the syntax
    e.g. ShowWizard FindFeature/ProjectData/Features/Feature1/Model For the tools
    MeasureOnScreen, Calibrate and CameraOrigin you can specify a mount position
    e.g. ShowWizard Calibrate Platen
    Status: published
    ----------
    Parameters:
        ToolName:str = ""
        MountPosition:str = ""
    ----------
    Response:
        Canceled:int
    ----------
    Command Timeout: 10000000
    Example:ShowWizard AlignWafer
    """
    rsp = MessageServerInterface.sendSciCommand("ShowWizard",ToolName,MountPosition)
    return int(rsp[0])

def ProbeToPadAlign(Position=""):
    """
    Sets a new Home position. The command is used during ReAlign to search the
    trained home reference model and to calculate the new xy home position.
    Status: published
    ----------
    Parameters:
        Position:str = "H"
    ----------
    Response:
        XOffsetWafer:Decimal
        YOffsetWafer:Decimal
    ----------
    Command Timeout: 120000
    Example:ProbeToPadAlign H
    """
    rsp = MessageServerInterface.sendSciCommand("ProbeToPadAlign",Position)
    global ProbeToPadAlign_Response
    if not "ProbeToPadAlign_Response" in globals(): ProbeToPadAlign_Response = namedtuple("ProbeToPadAlign_Response", "XOffsetWafer,YOffsetWafer")
    return ProbeToPadAlign_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def ReadOcrString():
    """
    Reads the wafer ID string from the wafer's surface. Returns the read ID as
    string. Requires IDTools license.
    Status: published
    ----------
    Response:
        OcrString:str
    ----------
    Command Timeout: 60000
    Example:ReadOcrString
    """
    rsp = MessageServerInterface.sendSciCommand("ReadOcrString")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ReadBarCode():
    """
    Reads the wafers barcode and decodes it to a string. Requires IDTools license.
    Status: published
    ----------
    Response:
        BarCodeString:str
    ----------
    Command Timeout: 60000
    Example:ReadBarCode
    """
    rsp = MessageServerInterface.sendSciCommand("ReadBarCode")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def Read2DMatrixCode():
    """
    Reads the wafers matrix code and decodes it to a string. Requires IDTools
    license.
    Status: published
    ----------
    Response:
        MatrixCodeString:str
    ----------
    Command Timeout: 60000
    Example:Read2DMatrixCode
    """
    rsp = MessageServerInterface.sendSciCommand("Read2DMatrixCode")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ReadQRCode():
    """
    Reads the wafers qr code and decodes it to a string. Requires IDTools license.
    Status: published
    ----------
    Response:
        QRCodeString:str
    ----------
    Command Timeout: 60000
    Example:ReadQRCode
    """
    rsp = MessageServerInterface.sendSciCommand("ReadQRCode")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetSpectrumRemote(Activate=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Activates the Spectrum remote mode. In this mode all user interface elements are
    hidden and disabled. This is used when Spectrum is hosted inside VeloxPro.
    Status: internal
    ----------
    Parameters:
        Activate:int = 1
    ----------
    Command Timeout: 10000
    Example:SetSpectrumRemote 1
    """
    MessageServerInterface.sendSciCommand("SetSpectrumRemote",Activate)


def GetCameraLight(Name=""):
    """
    Returns light properties of chosen camera.
    Status: published
    ----------
    Parameters:
        Name:str = ""
    ----------
    Response:
        MountPosition:str
        State:int
        Shutter:Decimal
        Gain:Decimal
        Brightness:int
        Contrast:int
        Sharpness:int
        Illumination:int
    ----------
    Command Timeout: 10000
    Example:GetCameraLight Scope
    """
    rsp = MessageServerInterface.sendSciCommand("GetCameraLight",Name)
    global GetCameraLight_Response
    if not "GetCameraLight_Response" in globals(): GetCameraLight_Response = namedtuple("GetCameraLight_Response", "MountPosition,State,Shutter,Gain,Brightness,Contrast,Sharpness,Illumination")
    return GetCameraLight_Response(str(rsp[0]),int(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]),int(rsp[7]))

def GetCameraView(Name=""):
    """
    Returns the present camera view state of a desired tool or active view.
    Status: published
    ----------
    Parameters:
        Name:str = ""
    ----------
    Response:
        MountPosition:str
        Zoom:int
        LiveVideo:int
        WindowState:int
    ----------
    Command Timeout: 10000
    Example:GetCameraView AlignWafer
    """
    rsp = MessageServerInterface.sendSciCommand("GetCameraView",Name)
    global GetCameraView_Response
    if not "GetCameraView_Response" in globals(): GetCameraView_Response = namedtuple("GetCameraView_Response", "MountPosition,Zoom,LiveVideo,WindowState")
    return GetCameraView_Response(str(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def GetPattern(ToolName="", ModelName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Transforms the specific model of a demanded tool into a bitmap. This bitmap will
    be stored in the same folder as the project file.     The command was originally
    required by ReAlignWizard and is currently no longer in use.
    Status: internal
    ----------
    Parameters:
        ToolName:str = ""
        ModelName:str = ""
    ----------
    Response:
        BitmapPath:str
    ----------
    Command Timeout: 30000
    Example:GetPattern AlignWafer Model1
    """
    rsp = MessageServerInterface.sendSciCommand("GetPattern",ToolName,ModelName)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ShowPosition(MountPosition="", DistPositionX="", DistPositionY=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the ChuckCenter under a given camera. When no camera mount position is
    given, Spectrum uses active view. If there is an Offset different from zero,
    this position will be moved under the camera.
    Status: internal
    ----------
    Parameters:
        MountPosition:str = ""
        DistPositionX:Decimal = 0
        DistPositionY:Decimal = 0
    ----------
    Command Timeout: 60000
    Example:ShowPosition Scope
    """
    MessageServerInterface.sendSciCommand("ShowPosition",MountPosition,DistPositionX,DistPositionY)


def GetCameraHomePosition():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the home die coordinates when the home die is under the alignment camera
    (for instance, the top camera).     Command was used during TrainReAlign to get
    the start position for Z-Profiling. Command is no longer used.
    Status: internal
    ----------
    Response:
        XPosition:Decimal
        YPosition:Decimal
        ZPosition:Decimal
    ----------
    Command Timeout: 10000
    Example:GetCameraHomePosition
    """
    rsp = MessageServerInterface.sendSciCommand("GetCameraHomePosition")
    global GetCameraHomePosition_Response
    if not "GetCameraHomePosition_Response" in globals(): GetCameraHomePosition_Response = namedtuple("GetCameraHomePosition_Response", "XPosition,YPosition,ZPosition")
    return GetCameraHomePosition_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def SynchronizeCamera(MountPos="", SynchronizeXY="", SynchronizeZ=""):
    """
    Synchronizes the Platen camera with the calibration mark. The mark is mounted on
    the Chuck camera. The Chuck must be moved to get the mark in view of the
    specified camera.
    Status: published
    ----------
    Parameters:
        MountPos:str = "Platen"
        SynchronizeXY:int = 0
        SynchronizeZ:int = 0
    ----------
    Response:
        XPosition:Decimal
        YPosition:Decimal
        ZPosition:Decimal
    ----------
    Command Timeout: 240000
    Example:SynchronizeCamera Platen 1 1
    """
    rsp = MessageServerInterface.sendSciCommand("SynchronizeCamera",MountPos,SynchronizeXY,SynchronizeZ)
    global SynchronizeCamera_Response
    if not "SynchronizeCamera_Response" in globals(): SynchronizeCamera_Response = namedtuple("SynchronizeCamera_Response", "XPosition,YPosition,ZPosition")
    return SynchronizeCamera_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def ProbeCardOCS(UpdateZ="", MeasureBothGroups=""):
    """
    Determines the Chuck XYZ axis position where the probe tips of the Probe Card
    are in focus. The output parameter is the Z axis value in microns from zero of
    the new focus height.
    Status: published
    ----------
    Parameters:
        UpdateZ:int = 1
        MeasureBothGroups:int = 1
    ----------
    Response:
        ZPosition:Decimal
    ----------
    Command Timeout: 360000
    Example:ProbeCardOCS 1
    """
    rsp = MessageServerInterface.sendSciCommand("ProbeCardOCS",UpdateZ,MeasureBothGroups)
    return Decimal(rsp[0])

def MoveChuckAutoXY(XPosition="", YPosition="", XSubsiteOffset="", YSubsiteOffset="", SoakTime="", DoVisionAlign=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command is sent by Wafer Map to trigger AutoXY, AutoZ or VueTrack for each die
    move. Autonomous Assistant must be activated/trained before command can be used.
    Response is X, Y relative distance of adjustment from requested position.
    Status: internal
    ----------
    Parameters:
        XPosition:Decimal = 0
        YPosition:Decimal = 0
        XSubsiteOffset:Decimal = 0
        YSubsiteOffset:Decimal = 0
        SoakTime:Decimal = -1
        DoVisionAlign:int = 1
    ----------
    Response:
        XOffset:Decimal
        YOffset:Decimal
    ----------
    Command Timeout: 6000000
    Example:MoveChuckAutoXY 5000 10000
    """
    rsp = MessageServerInterface.sendSciCommand("MoveChuckAutoXY",XPosition,YPosition,XSubsiteOffset,YSubsiteOffset,SoakTime,DoVisionAlign)
    global MoveChuckAutoXY_Response
    if not "MoveChuckAutoXY_Response" in globals(): MoveChuckAutoXY_Response = namedtuple("MoveChuckAutoXY_Response", "XOffset,YOffset")
    return MoveChuckAutoXY_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def VueTrackAlign(FullVueTrackAlign=""):
    """
    Alignment for the next wafer when using VueTrack.
    Status: published
    ----------
    Parameters:
        FullVueTrackAlign:int = 1
    ----------
    Command Timeout: 6000000
    Example:VueTrackAlign
    """
    MessageServerInterface.sendSciCommand("VueTrackAlign",FullVueTrackAlign)


def MoveChuckReAlign(XPosition="", YPosition="", XSubsiteOffset="", YSubsiteOffset="", SoakTime="", PostReAlignSoakTime="", DoVisionAlign=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command is sent by Wafer Map to trigger ReAlign at Die for each die move.
    ReAlign must be trained before command can be used. Response is X, Y relative
    distance of adjustment from requested position.
    Status: internal
    ----------
    Parameters:
        XPosition:Decimal = 0
        YPosition:Decimal = 0
        XSubsiteOffset:Decimal = 0
        YSubsiteOffset:Decimal = 0
        SoakTime:Decimal = -1
        PostReAlignSoakTime:Decimal = -1
        DoVisionAlign:int = 1
    ----------
    Response:
        XOffset:Decimal
        YOffset:Decimal
    ----------
    Command Timeout: 6000000
    Example:MoveChuckReAlign 5000 10000
    """
    rsp = MessageServerInterface.sendSciCommand("MoveChuckReAlign",XPosition,YPosition,XSubsiteOffset,YSubsiteOffset,SoakTime,PostReAlignSoakTime,DoVisionAlign)
    global MoveChuckReAlign_Response
    if not "MoveChuckReAlign_Response" in globals(): MoveChuckReAlign_Response = namedtuple("MoveChuckReAlign_Response", "XOffset,YOffset")
    return MoveChuckReAlign_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def AutoFocusEVue(DistBelow="", DistAbove="", XOffsetCenter="", YOffsetCenter=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command is only used internally for software testing and for providing backwards
    compatibility with SCPI legacy commands. It executes a focus search using the
    eVue focus drive.
    Status: internal
    ----------
    Parameters:
        DistBelow:Decimal = 0
        DistAbove:Decimal = 0
        XOffsetCenter:int = 0
        YOffsetCenter:int = 0
    ----------
    Response:
        FocusScore:Decimal
        ZPosition:Decimal
    ----------
    Command Timeout: 30000
    Example:AutoFocusEVue 200 200 0 0
    """
    rsp = MessageServerInterface.sendSciCommand("AutoFocusEVue",DistBelow,DistAbove,XOffsetCenter,YOffsetCenter)
    global AutoFocusEVue_Response
    if not "AutoFocusEVue_Response" in globals(): AutoFocusEVue_Response = namedtuple("AutoFocusEVue_Response", "FocusScore,ZPosition")
    return AutoFocusEVue_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def AutoAlignOffAxis(SetValue=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Executes the ReAlign Wafer Alignment tool to do a theta alignment of the wafer
    with optional index calculation or thermal expansion measurement. AutoAlign is
    performed using the Platen camera. Only supported for systems with off-axis
    camera.
    Status: internal
    ----------
    Parameters:
        SetValue:int = 0
    ----------
    Command Timeout: 300000
    Example:AutoAlignOffAxis 1
    """
    MessageServerInterface.sendSciCommand("AutoAlignOffAxis",SetValue)


def FindFocusOffAxis(StepCount="", Range=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Determines the Z axis position where an object in the region of interest is in
    focus. First output parameter is the Z axis value in microns from zero of the
    new focus height. Second output parameter is the used stage to perform focus
    search. Focus search is performed using the Platen camera. Only supported for
    systems with off-axis camera.
    Status: internal
    ----------
    Parameters:
        StepCount:int = -1
        Range:Decimal = -1
    ----------
    Response:
        ZPosition:Decimal
        Stage:str
    ----------
    Command Timeout: 120000
    Example:FindFocusOffAxis 50 500
    """
    rsp = MessageServerInterface.sendSciCommand("FindFocusOffAxis",StepCount,Range)
    global FindFocusOffAxis_Response
    if not "FindFocusOffAxis_Response" in globals(): FindFocusOffAxis_Response = namedtuple("FindFocusOffAxis_Response", "ZPosition,Stage")
    return FindFocusOffAxis_Response(Decimal(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def AlignAuxOffAxis(AuxSiteID=""):
    """
    Performs an automated AUX Site alignment in XYZ using the Off Axis camera. Tool
    can correct reference position and Contact Height for the given AUX Site.
    Status: published
    ----------
    Parameters:
        AuxSiteID:int = 0
    ----------
    Command Timeout: 300000
    Example:AlignAuxOffAxis 1
    """
    MessageServerInterface.sendSciCommand("AlignAuxOffAxis",AuxSiteID)


def FindFocusPlaten(StepCount="", Range=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Determines the Z axis position where an object in the region of interest is in
    focus. First output parameter is the Z axis value in microns from zero of the
    new focus height. Second output parameter is the used stage to perform focus
    search. Uses the FindFocus tool settings but always the Platen camera -
    independent of the FindFocus mount. This command is used on e.g. BlueRay systems
    that have a platen camera but can't use ReAlign/DetectWaferHeight as they don't
    have an upward looking camera.
    Status: internal
    ----------
    Parameters:
        StepCount:int = -1
        Range:Decimal = -1
    ----------
    Response:
        ZPosition:Decimal
        Stage:str
    ----------
    Command Timeout: 120000
    Example:FindFocusPlaten 50 500
    """
    rsp = MessageServerInterface.sendSciCommand("FindFocusPlaten",StepCount,Range)
    global FindFocusPlaten_Response
    if not "FindFocusPlaten_Response" in globals(): FindFocusPlaten_Response = namedtuple("FindFocusPlaten_Response", "ZPosition,Stage")
    return FindFocusPlaten_Response(Decimal(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def AlignChipOffAxis():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Performs a single or two point alignment and moves the current chip to the
    trained aligned position in Theta (in degrees) and X, Y (in microns). This
    command is using the off axis platen camera with functionality of ReAlign.
    Status: internal
    ----------
    Response:
        ThetaOffset:Decimal
        XOffset:Decimal
        YOffset:Decimal
    ----------
    Command Timeout: 180000
    Example:AlignChipOffAxis
    """
    rsp = MessageServerInterface.sendSciCommand("AlignChipOffAxis")
    global AlignChipOffAxis_Response
    if not "AlignChipOffAxis_Response" in globals(): AlignChipOffAxis_Response = namedtuple("AlignChipOffAxis_Response", "ThetaOffset,XOffset,YOffset")
    return AlignChipOffAxis_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def SelectAZoomLens(Lens=""):
    """
    Selects 1 of 4 symbolic lenses (4 classified coarse ranges).
    Status: published
    ----------
    Parameters:
        Lens:int = 1
    ----------
    Command Timeout: 10000
    Example:SelectAZoomLens 1
    """
    MessageServerInterface.sendSciCommand("SelectAZoomLens",Lens)


def GetAZoomLens():
    """
    Returns 1 of 4 symbolic lenses, coarse ranges.
    Status: published
    ----------
    Response:
        Lens:int
    ----------
    Command Timeout: 5000
    Example:GetAZoomLens
    """
    rsp = MessageServerInterface.sendSciCommand("GetAZoomLens")
    return int(rsp[0])

def AZoomSetupDialog():
    """
    Opens the operator panel. In this window you can change the settings for all
    defined lenses.
    Status: published
    ----------
    Command Timeout: 5000
    Example:AZoomSetupDialog
    """
    MessageServerInterface.sendSciCommand("AZoomSetupDialog")


def MoveAZoomFocus(Focus="", Ref=""):
    """
    Changes the focus magnitude.
    Status: published
    ----------
    Parameters:
        Focus:int = 100
        Ref:str = "R"
    ----------
    Response:
        RetFocus:int
    ----------
    Command Timeout: 10000
    Example:MoveAZoomFocus 100
    """
    rsp = MessageServerInterface.sendSciCommand("MoveAZoomFocus",Focus,Ref)
    return int(rsp[0])

def ReadAZoomFocus():
    """
    Returns the focus magnitude.
    Status: published
    ----------
    Response:
        Focus:int
    ----------
    Command Timeout: 5000
    Example:ReadAZoomFocus
    """
    rsp = MessageServerInterface.sendSciCommand("ReadAZoomFocus")
    return int(rsp[0])

def MoveAZoomVelocity(Direction="", Velocity=""):
    """
    Moves the A-Zoom using the set focus speed.
    Status: published
    ----------
    Parameters:
        Direction:str = ""
        Velocity:int = 100
    ----------
    Response:
        RetVelocity:Decimal
    ----------
    Command Timeout: 240000
    Example:MoveAZoomVelocity + 67
    """
    rsp = MessageServerInterface.sendSciCommand("MoveAZoomVelocity",Direction,Velocity)
    return Decimal(rsp[0])

def StopAZoom():
    """
    Stops the A-Zoom movements.
    Status: published
    ----------
    Command Timeout: 5000
    Example:StopAZoom
    """
    MessageServerInterface.sendSciCommand("StopAZoom")


def SetAZoomLight(Light=""):
    """
    Switches all lights ON or OFF. ON means the values defined by the current lens.
    1 switches the light on, 0 switches the light off. Without parameter toggles
    between on an off.
    Status: published
    ----------
    Parameters:
        Light:int = 0
    ----------
    Command Timeout: 5000
    Example:SetAZoomLight 1
    """
    MessageServerInterface.sendSciCommand("SetAZoomLight",Light)


def CloseAZoom():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Closes the OpticalControl application. Used during Project File handling.
    Status: internal
    ----------
    Command Timeout: 5000
    Example:CloseAZoom
    """
    MessageServerInterface.sendSciCommand("CloseAZoom")


def OCLightVal(Value="", Channel="", Segment=""):
    """
    Set the brightness of given channel and segment to the given value.
    Status: published
    ----------
    Parameters:
        Value:int = 0
        Channel:int = 1
        Segment:int = 1
    ----------
    Command Timeout: 5000
    Example:OCLightVal 128 1 4
    """
    MessageServerInterface.sendSciCommand("OCLightVal",Value,Channel,Segment)


def OCLightOn(On="", Channel=""):
    """
    Switch the light (if it has segments then all) in a given channel ON or OFF.
    Switch ON - that means: light to the before adjusted brightness.
    Status: published
    ----------
    Parameters:
        On:int = 0
        Channel:int = 1
    ----------
    Command Timeout: 5000
    Example:OCLightOn 1 1
    """
    MessageServerInterface.sendSciCommand("OCLightOn",On,Channel)


def OCSetZoomLevel(Zoom="", Motor=""):
    """
    Set logical zoom factor for given motor (if has more then one, else to the one)
    Status: published
    ----------
    Parameters:
        Zoom:int = 0
        Motor:int = 1
    ----------
    Command Timeout: 5000
    Example:OCSetZoomLevel 50 1
    """
    MessageServerInterface.sendSciCommand("OCSetZoomLevel",Zoom,Motor)


def OCGetZoomLevel(Motor=""):
    """
    Get logical zoom factor for given motor (if has more then one, else to the one)
    Status: published
    ----------
    Parameters:
        Motor:int = 1
    ----------
    Response:
        Zoom:int
    ----------
    Command Timeout: 5000
    Example:OCGetZoomLevel 1
    """
    rsp = MessageServerInterface.sendSciCommand("OCGetZoomLevel",Motor)
    return int(rsp[0])

def StartReAlignTemperature(TargetTemperature="", ThetaAlignOnFinish="", ContactOnFinish=""):
    """
    Starts temperature ramping using ReAlign. ReAlign will re-adjust the probes and
    wafer during ramping to the new target temperature. Command returns immediately.
    The status of temperature ramping must be checked using the
    GetReAlignTemperatureStatus command.
    Status: published
    ----------
    Parameters:
        TargetTemperature:Decimal = 0
        ThetaAlignOnFinish:int = 0
        ContactOnFinish:int = 0
    ----------
    Command Timeout: 10000
    Example:StartReAlignTemperature 150
    """
    MessageServerInterface.sendSciCommand("StartReAlignTemperature",TargetTemperature,ThetaAlignOnFinish,ContactOnFinish)


def StopReAlignTemperature():
    """
    Stops temperature ramping using ReAlign.
    Status: published
    ----------
    Command Timeout: 10000
    Example:StopReAlignTemperature
    """
    MessageServerInterface.sendSciCommand("StopReAlignTemperature")


def GetReAlignTemperatureStatus():
    """
    Returns the status of the current temperature ramping using ReAlign process.
    Status: published
    ----------
    Response:
        StatusId:int
        StatusStr:str
    ----------
    Command Timeout: 300000
    Example:GetReAlignTemperatureStatus
    """
    rsp = MessageServerInterface.sendSciCommand("GetReAlignTemperatureStatus")
    global GetReAlignTemperatureStatus_Response
    if not "GetReAlignTemperatureStatus_Response" in globals(): GetReAlignTemperatureStatus_Response = namedtuple("GetReAlignTemperatureStatus_Response", "StatusId,StatusStr")
    return GetReAlignTemperatureStatus_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def ReAlign(Repeats="", Mode="", AlignProbeCard="", AdjustContact=""):
    """
    Performs an automatic realignment of the wafer. This includes measuring the
    needle drift XYZ, aligning the wafer, measuring Chuck expansion, measuring Chuck
    drift XYZ and optionally a Z-Profile. Alternatively the tool performs a
    ProbeToDie Alignment to correct the needle position for the current die. Command
    returns once ReAlign is finished or aborted because of an error.
    Status: published
    ----------
    Parameters:
        Repeats:int = 1
        Mode:str = "H"
        AlignProbeCard:int = 2
        AdjustContact:int = 2
    ----------
    Response:
        XOffsetWafer:Decimal
        YOffsetWafer:Decimal
        ZOffsetWafer:Decimal
        XOffsetCard:Decimal
        YOffsetCard:Decimal
        ZOffsetCard:Decimal
    ----------
    Command Timeout: 1000000
    Example:ReAlign 2 H 0 0
    """
    rsp = MessageServerInterface.sendSciCommand("ReAlign",Repeats,Mode,AlignProbeCard,AdjustContact)
    global ReAlign_Response
    if not "ReAlign_Response" in globals(): ReAlign_Response = namedtuple("ReAlign_Response", "XOffsetWafer,YOffsetWafer,ZOffsetWafer,XOffsetCard,YOffsetCard,ZOffsetCard")
    return ReAlign_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),Decimal(rsp[5]))

def NextWafer():
    """
    Starts the ReAlign training routine.
    Status: published
    ----------
    Response:
        Canceled:int
    ----------
    Command Timeout: 60000000
    Example:NextWafer
    """
    rsp = MessageServerInterface.sendSciCommand("NextWafer")
    return int(rsp[0])

def StartReAlign(Repeats="", Mode="", AlignProbeCard="", AdjustContact=""):
    """
    Starts an automatic realignment of the wafer. This includes measuring the needle
    drift XYZ, aligning the wafer, measuring Chuck expansion, measuring Chuck drift
    XYZ and optionally a Z-Profile. Alternatively the tool performs a ProbeToPad
    Alignment to correct the needle position for the current die. Command returns
    immediately. The status of the asynchronous ReAlign execution must be checked
    using the GetReAlignStatus command.
    Status: published
    ----------
    Parameters:
        Repeats:int = 1
        Mode:str = "H"
        AlignProbeCard:int = 2
        AdjustContact:int = 2
    ----------
    Command Timeout: 60000
    Example:StartReAlign 2 H 0 0
    """
    MessageServerInterface.sendSciCommand("StartReAlign",Repeats,Mode,AlignProbeCard,AdjustContact)


def StopReAlign():
    """
    Stops the ReAlign procedure.
    Status: published
    ----------
    Command Timeout: 120000
    Example:StopReAlign
    """
    MessageServerInterface.sendSciCommand("StopReAlign")


def GetReAlignStatus():
    """
    Returns a status of the ReAlign procedure and the error code of the last
    execution. If the return value is true, ReAlign is running.
    Status: published
    ----------
    Response:
        Running:int
        LastError:int
    ----------
    Command Timeout: 60000
    Example:GetReAlignStatus
    """
    rsp = MessageServerInterface.sendSciCommand("GetReAlignStatus")
    global GetReAlignStatus_Response
    if not "GetReAlignStatus_Response" in globals(): GetReAlignStatus_Response = namedtuple("GetReAlignStatus_Response", "Running,LastError")
    return GetReAlignStatus_Response(int(rsp[0]),int(rsp[1]))

def EnableOverlay(Overlay=""):
    """
    Allows activating the overlay of the probe tips for the Platen camera.
    Status: published
    ----------
    Parameters:
        Overlay:int = 0
    ----------
    Command Timeout: 10000
    Example:EnableOverlay 0
    """
    MessageServerInterface.sendSciCommand("EnableOverlay",Overlay)


def SwitchOffset(Offset="", MoveToWaferFocus=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Switches the offset compensation. Applicable for MicroAlign stations only.
    Status: internal
    ----------
    Parameters:
        Offset:int = 0
        MoveToWaferFocus:int = 1
    ----------
    Command Timeout: 60000
    Example:SwitchOffset 1
    """
    MessageServerInterface.sendSciCommand("SwitchOffset",Offset,MoveToWaferFocus)


def MoveEvueFocusStage(EvueZ="", EvueVelocity=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the eVue focus stage to a specified position. Implemented for supporting
    SCPI legacy command.
    Status: internal
    ----------
    Parameters:
        EvueZ:Decimal = 0
        EvueVelocity:Decimal = 100
    ----------
    Command Timeout: 30000
    Example:MoveEvueFocusStage 1000
    """
    MessageServerInterface.sendSciCommand("MoveEvueFocusStage",EvueZ,EvueVelocity)


def GetEvueFocusStagePos(PosRef=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the current position of the eVue focus stage. Implemented for supporting
    SCPI legacy command.
    Status: internal
    ----------
    Parameters:
        PosRef:str = "Zero"
    ----------
    Response:
        EvueZ:Decimal
    ----------
    Command Timeout: 10000
    Example:GetEvueFocusStagePos
    """
    rsp = MessageServerInterface.sendSciCommand("GetEvueFocusStagePos",PosRef)
    return Decimal(rsp[0])

def RunEvueAutoExpose(UseCB=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command runs the AutoExpose function for the eVue. Implemented for supporting
    SCPI legacy command.
    Status: internal
    ----------
    Parameters:
        UseCB:int = 1
    ----------
    Command Timeout: 20000
    Example:RunEvueAutoExpose 1
    """
    MessageServerInterface.sendSciCommand("RunEvueAutoExpose",UseCB)


def GetEvueZoomLevel():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Valid only with the eVue microscope that is connected to Velox.     On eVue
    systems, this command, returns values ranging from 0.5 to 5.0 for a 10x system
    and 0.5 to 20.0 for a 40x system.
    Status: internal
    ----------
    Response:
        Zoom:Decimal
    ----------
    Command Timeout: 10000
    Example:GetEvueZoomLevel
    """
    rsp = MessageServerInterface.sendSciCommand("GetEvueZoomLevel")
    return Decimal(rsp[0])

def SetEvueZoomLevel(Zoom=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Valid only with the eVue microscope or an A-Zoom microscope that is connected to
    Velox. On eVue systems, this command sets the proper CCD zoom level to the
    appropriate optical path.
    Status: internal
    ----------
    Parameters:
        Zoom:Decimal = 0
    ----------
    Command Timeout: 10000
    Example:SetEvueZoomLevel 2.0
    """
    MessageServerInterface.sendSciCommand("SetEvueZoomLevel",Zoom)


def StartAutomationTemperature(TargetTemperature="", ThetaAlignOnFinish="", ContactOnFinish="", AlignOnFinish=""):
    """
    Starts temperature ramping using Autonomous Assistant. The Autonomous Assistant
    (mostly VueTrack) will re-adjust the probes and wafer during ramping to the new
    target temperature.
    Status: published
    ----------
    Parameters:
        TargetTemperature:Decimal = 0
        ThetaAlignOnFinish:int = 0
        ContactOnFinish:int = 0
        AlignOnFinish:int = 1
    ----------
    Command Timeout: 10000
    Example:StartAutomationTemperature 150
    """
    MessageServerInterface.sendSciCommand("StartAutomationTemperature",TargetTemperature,ThetaAlignOnFinish,ContactOnFinish,AlignOnFinish)


def StopAutomationTemperature():
    """
    Stops temperature ramping using Autonomous Assistant.
    Status: published
    ----------
    Command Timeout: 10000
    Example:StopAutomationTemperature
    """
    MessageServerInterface.sendSciCommand("StopAutomationTemperature")


def GetAutomationTemperatureStatus():
    """
    Returns the status of the current temperature ramping using Autonomous Assistant
    process.
    Status: published
    ----------
    Response:
        StatusId:int
        StatusStr:str
    ----------
    Command Timeout: 300000
    Example:GetAutomationTemperatureStatus
    """
    rsp = MessageServerInterface.sendSciCommand("GetAutomationTemperatureStatus")
    global GetAutomationTemperatureStatus_Response
    if not "GetAutomationTemperatureStatus_Response" in globals(): GetAutomationTemperatureStatus_Response = namedtuple("GetAutomationTemperatureStatus_Response", "StatusId,StatusStr")
    return GetAutomationTemperatureStatus_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def GetAutomationActive():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command to read from Spectrum Vision if Autonomous Assistant (AutoXY, AutoZ or
    VueTrack) is active. Command is used     by Wafer Map to read if it must send
    MoveChuckAutoXY instead of MoveChuck
    Status: internal
    ----------
    Response:
        Active:int
    ----------
    Command Timeout: 10000
    Example:GetAutomationActive
    """
    rsp = MessageServerInterface.sendSciCommand("GetAutomationActive")
    return int(rsp[0])

def AutomationNeedleSearch(ProbeIndex="", MoveScope=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    VueTrack vision search of the given probe tip index.
    Status: internal
    ----------
    Parameters:
        ProbeIndex:int = 1
        MoveScope:int = 1
    ----------
    Response:
        XOffset:Decimal
        YOffset:Decimal
        ZOffset:Decimal
        XYMatchScore:Decimal
        ZMatchScore:Decimal
    ----------
    Command Timeout: 60000
    Example:AutomationNeedleSearch 1 1
    """
    rsp = MessageServerInterface.sendSciCommand("AutomationNeedleSearch",ProbeIndex,MoveScope)
    global AutomationNeedleSearch_Response
    if not "AutomationNeedleSearch_Response" in globals(): AutomationNeedleSearch_Response = namedtuple("AutomationNeedleSearch_Response", "XOffset,YOffset,ZOffset,XYMatchScore,ZMatchScore")
    return AutomationNeedleSearch_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]))

def AutomationReferenceSearch():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    AutomationReferenceSearch exposes the functionality of searching the Autonomous
    Assistant reference target via remote command
    Status: internal
    ----------
    Response:
        XOffset:Decimal
        YOffset:Decimal
        ZOffset:Decimal
        XYMatchScore:Decimal
    ----------
    Command Timeout: 60000
    Example:AutomationReferenceSearch
    """
    rsp = MessageServerInterface.sendSciCommand("AutomationReferenceSearch")
    global AutomationReferenceSearch_Response
    if not "AutomationReferenceSearch_Response" in globals(): AutomationReferenceSearch_Response = namedtuple("AutomationReferenceSearch_Response", "XOffset,YOffset,ZOffset,XYMatchScore")
    return AutomationReferenceSearch_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]))

def MovePositionersSafe():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the configured motorized Positioners to a safe position
    Status: internal
    ----------
    Command Timeout: 60000
    Example:MovePositionersSafe
    """
    MessageServerInterface.sendSciCommand("MovePositionersSafe")


def SetConstantContactMode(IsOn="", ForceLastCorrection=""):
    """
    Starts Constant Contact mode using Autonomous Assistant. The Autonomous
    Assistant will re-adjust the wafer during ramping to the new target temperature.
    Status: published
    ----------
    Parameters:
        IsOn:int = 0
        ForceLastCorrection:int = 0
    ----------
    Command Timeout: 10000
    Example:SetConstantContactMode 1
    """
    MessageServerInterface.sendSciCommand("SetConstantContactMode",IsOn,ForceLastCorrection)


def GetConstantContactModeStatus():
    """
    Returns the status of the current ConstantContact Autonomous Assistant process.
    Status: published
    ----------
    Response:
        StatusId:int
        StatusStr:str
    ----------
    Command Timeout: 10000
    Example:GetConstantContactModeStatus
    """
    rsp = MessageServerInterface.sendSciCommand("GetConstantContactModeStatus")
    global GetConstantContactModeStatus_Response
    if not "GetConstantContactModeStatus_Response" in globals(): GetConstantContactModeStatus_Response = namedtuple("GetConstantContactModeStatus_Response", "StatusId,StatusStr")
    return GetConstantContactModeStatus_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def SetAutomationActive(Activate=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command to set if Autonomous Assistant (AutoXY, AutoZ or VueTrack) is active.
    Command can be used to e.g. deactivate Autonomous Assistant     programmatically
    in case it is no longer used.     When activating Autonomous Assistant, the
    command will return an error in case it is not possible (e.g. not trained)
    Status: internal
    ----------
    Parameters:
        Activate:int = 0
    ----------
    Command Timeout: 10000
    Example:SetAutomationActive 1
    """
    MessageServerInterface.sendSciCommand("SetAutomationActive",Activate)


def AutomationSearchCurrentDie():
    """
    Performs an Autonomous Assistant search and position correction using the
    current Chuck position. Response is X, Y relative distance of adjustment.
    Status: published
    ----------
    Response:
        XOffset:Decimal
        YOffset:Decimal
    ----------
    Command Timeout: 6000000
    Example:AutomationSearchCurrentDie
    """
    rsp = MessageServerInterface.sendSciCommand("AutomationSearchCurrentDie")
    global AutomationSearchCurrentDie_Response
    if not "AutomationSearchCurrentDie_Response" in globals(): AutomationSearchCurrentDie_Response = namedtuple("AutomationSearchCurrentDie_Response", "XOffset,YOffset")
    return AutomationSearchCurrentDie_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def PreMapWafer():
    """
    PreMapWafer finds actual singulated die locations and updates positions used by
    Wafer Map.
    Status: published
    ----------
    Response:
        NumberOfDies:int
    ----------
    Command Timeout: 14400000
    Example:PreMapWafer
    """
    rsp = MessageServerInterface.sendSciCommand("PreMapWafer")
    return int(rsp[0])

def ISSProbeAlign():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Performs an probe to pad operation on the ISS with two RF Positioners.
    Status: internal
    ----------
    Command Timeout: 6000000
    Example:ISSProbeAlign
    """
    MessageServerInterface.sendSciCommand("ISSProbeAlign")


def FindWaferCenter(NoManualRecovery=""):
    """
    FindWaferCenter finds the center of the wafer using edge detection.
    Status: published
    ----------
    Parameters:
        NoManualRecovery:int = 0
    ----------
    Response:
        ChuckX:Decimal
        ChuckY:Decimal
    ----------
    Command Timeout: 300000
    Example:FindWaferCenter
    """
    rsp = MessageServerInterface.sendSciCommand("FindWaferCenter",NoManualRecovery)
    global FindWaferCenter_Response
    if not "FindWaferCenter_Response" in globals(): FindWaferCenter_Response = namedtuple("FindWaferCenter_Response", "ChuckX,ChuckY")
    return FindWaferCenter_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def LocateHomeDie(NoManualRecovery=""):
    """
    LocateHomeDie finds the center of the wafer using edge detection and sets the
    home position.
    Status: published
    ----------
    Parameters:
        NoManualRecovery:int = 0
    ----------
    Response:
        ChuckX:Decimal
        ChuckY:Decimal
    ----------
    Command Timeout: 300000
    Example:LocateHomeDie
    """
    rsp = MessageServerInterface.sendSciCommand("LocateHomeDie",NoManualRecovery)
    global LocateHomeDie_Response
    if not "LocateHomeDie_Response" in globals(): LocateHomeDie_Response = namedtuple("LocateHomeDie_Response", "ChuckX,ChuckY")
    return LocateHomeDie_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def DeletePositionerLayout(LayoutName="", ProbeID=""):
    """
    Delete the specified layout. If LayoutName is 'All' then all layouts are
    deleted. If optional ProbeID parameter is set, it removes just that probe from
    the layout.
    Status: published
    ----------
    Parameters:
        LayoutName:str = ""
        ProbeID:int = 0
    ----------
    Command Timeout: 10000
    Example:DeletePositionerLayout "layout1"
    """
    MessageServerInterface.sendSciCommand("DeletePositionerLayout",LayoutName,ProbeID)


def CapturePositionerLayout(LayoutName="", ProbeID=""):
    """
    Capture the specified layout. If optional ProbeID parameter is set, it captures
    just that probe from the layout.
    Status: published
    ----------
    Parameters:
        LayoutName:str = ""
        ProbeID:int = 0
    ----------
    Command Timeout: 30000
    Example:CapturePositionerLayout "layout1"
    """
    MessageServerInterface.sendSciCommand("CapturePositionerLayout",LayoutName,ProbeID)


def MoveToPositionerLayout(LayoutName=""):
    """
    Move to the probes to specified layout which are offsets from the trained
    positions.
    Status: published
    ----------
    Parameters:
        LayoutName:str = ""
    ----------
    Command Timeout: 300000
    Example:MoveToPositionerLayout "layout1"
    """
    MessageServerInterface.sendSciCommand("MoveToPositionerLayout",LayoutName)


def ResetAutomation():
    """
    Reset Autonomous Assistant data back to trained values.
    Status: published
    ----------
    Command Timeout: 10000
    Example:ResetAutomation
    """
    MessageServerInterface.sendSciCommand("ResetAutomation")


def GetWaferCenter():
    """
    GetWaferCenter returns the Chuck location (zero based) of the wafer center. It
    returns 0 0 if FindWaferCenter has not been executed for the current wafer.
    Status: published
    ----------
    Response:
        ChuckX:Decimal
        ChuckY:Decimal
    ----------
    Command Timeout: 10000
    Example:GetWaferCenter
    """
    rsp = MessageServerInterface.sendSciCommand("GetWaferCenter")
    global GetWaferCenter_Response
    if not "GetWaferCenter_Response" in globals(): GetWaferCenter_Response = namedtuple("GetWaferCenter_Response", "ChuckX,ChuckY")
    return GetWaferCenter_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def AutomationRFProbeSearch(ImageFilename=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the distance in X,Y between the center tips of the RF probes.
    Status: internal
    ----------
    Parameters:
        ImageFilename:str = ""
    ----------
    Response:
        X:Decimal
        Y:Decimal
    ----------
    Command Timeout: 10000
    Example:AutomationRFProbeSearch
    """
    rsp = MessageServerInterface.sendSciCommand("AutomationRFProbeSearch",ImageFilename)
    global AutomationRFProbeSearch_Response
    if not "AutomationRFProbeSearch_Response" in globals(): AutomationRFProbeSearch_Response = namedtuple("AutomationRFProbeSearch_Response", "X,Y")
    return AutomationRFProbeSearch_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def StartAutoRFCalibration():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Starts the Auto RF calibration sequence.
    Status: internal
    ----------
    Command Timeout: 10000
    Example:StartAutoRFCalibration
    """
    MessageServerInterface.sendSciCommand("StartAutoRFCalibration")


def StopAutoRFCalibration():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Stops the currently running Auto RF calibration.
    Status: internal
    ----------
    Command Timeout: 10000
    Example:StopAutoRFCalibration
    """
    MessageServerInterface.sendSciCommand("StopAutoRFCalibration")


def GetAutoRFCalibrationStatus():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the status of the Auto RF calibration sequence.
    Status: internal
    ----------
    Response:
        StatusId:int
        StatusStr:str
    ----------
    Command Timeout: 10000
    Example:GetAutoRFCalibrationStatus
    """
    rsp = MessageServerInterface.sendSciCommand("GetAutoRFCalibrationStatus")
    global GetAutoRFCalibrationStatus_Response
    if not "GetAutoRFCalibrationStatus_Response" in globals(): GetAutoRFCalibrationStatus_Response = namedtuple("GetAutoRFCalibrationStatus_Response", "StatusId,StatusStr")
    return GetAutoRFCalibrationStatus_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def GetEvueVersion(Index=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the version numbers for eVue driver and eVue firmwares.
    Status: internal
    ----------
    Parameters:
        Index:int = 0
    ----------
    Response:
        EvueVersionDriver:int
        EvueVersionMastodon:int
        EvueVersionDaughter:int
        EvueVersionStonehenge:int
        EvueVersionBluestone:int
        EvueVersionBlackPill:int
    ----------
    Command Timeout: 10000
    Example:GetEvueVersion
    """
    rsp = MessageServerInterface.sendSciCommand("GetEvueVersion",Index)
    global GetEvueVersion_Response
    if not "GetEvueVersion_Response" in globals(): GetEvueVersion_Response = namedtuple("GetEvueVersion_Response", "EvueVersionDriver,EvueVersionMastodon,EvueVersionDaughter,EvueVersionStonehenge,EvueVersionBluestone,EvueVersionBlackPill")
    return GetEvueVersion_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]))

def GetEvueFocusStageRange():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the minimum and maximum position of the eVue focus stage.
    Status: internal
    ----------
    Response:
        EvueZMax:Decimal
        EvueZMin:Decimal
    ----------
    Command Timeout: 10000
    Example:GetEvueFocusStageRange
    """
    rsp = MessageServerInterface.sendSciCommand("GetEvueFocusStageRange")
    global GetEvueFocusStageRange_Response
    if not "GetEvueFocusStageRange_Response" in globals(): GetEvueFocusStageRange_Response = namedtuple("GetEvueFocusStageRange_Response", "EvueZMax,EvueZMin")
    return GetEvueFocusStageRange_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def GetCameraScale(Name=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the micron to pixel ratio of requested mount.
    Status: internal
    ----------
    Parameters:
        Name:str = ""
    ----------
    Response:
        ScaleX:Decimal
        ScaleY:Decimal
        PixelX:Decimal
        PixelY:Decimal
    ----------
    Command Timeout: 10000
    Example:GetCameraScale
    """
    rsp = MessageServerInterface.sendSciCommand("GetCameraScale",Name)
    global GetCameraScale_Response
    if not "GetCameraScale_Response" in globals(): GetCameraScale_Response = namedtuple("GetCameraScale_Response", "ScaleX,ScaleY,PixelX,PixelY")
    return GetCameraScale_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]))

def SetTestParameterData(Index="", StartBin="", NumBins="", LowLimit="", HighLimit="", Name="", EnabledForAnalysis="", AnalysisLowLimit="", AnalysisHighLimit=""):
    """
    Sets the Test Parameter data.
    Status: published
    ----------
    Parameters:
        Index:int = 0
        StartBin:int = 0
        NumBins:int = 0
        LowLimit:Decimal = 0
        HighLimit:Decimal = 1
        Name:str = ""
        EnabledForAnalysis:int = 0
        AnalysisLowLimit:Decimal = 0
        AnalysisHighLimit:Decimal = 1
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetTestParameterData",Index,StartBin,NumBins,LowLimit,HighLimit,Name,EnabledForAnalysis,AnalysisLowLimit,AnalysisHighLimit)


def GetTestParameterData(Index=""):
    """
    Sets the Test Parameter data.
    Status: published
    ----------
    Parameters:
        Index:int = 0
    ----------
    Response:
        StartBin:int
        NumBins:int
        LowLimit:Decimal
        HighLimit:Decimal
        Name:str
        EnabledForAnalysis:int
        AnalysisLowLimit:Decimal
        AnalysisHighLimit:Decimal
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetTestParameterData",Index)
    global GetTestParameterData_Response
    if not "GetTestParameterData_Response" in globals(): GetTestParameterData_Response = namedtuple("GetTestParameterData_Response", "StartBin,NumBins,LowLimit,HighLimit,Name,EnabledForAnalysis,AnalysisLowLimit,AnalysisHighLimit")
    return GetTestParameterData_Response(int(rsp[0]),int(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),str(rsp[4]),int(rsp[5]),Decimal(rsp[6]),Decimal(rsp[7]))

def SetTestParameterValueAsNum(TestParamIndex="", Value="", SequenceNumber="", Site=""):
    """
    Sets the Test Parameter value for a given Die/SubDie.
    Status: published
    ----------
    Parameters:
        TestParamIndex:int = 0
        Value:Decimal = 0
        SequenceNumber:int = -1
        Site:int = -1
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetTestParameterValueAsNum",TestParamIndex,Value,SequenceNumber,Site)


def SetTestParameterValueAsColRow(TestParamIndex="", Value="", DieX="", DieY="", Site=""):
    """
    Sets the Test Parameter value for a given Die/SubDie.
    Status: published
    ----------
    Parameters:
        TestParamIndex:int = 0
        Value:Decimal = 0
        DieX:int = 0
        DieY:int = 0
        Site:int = -1
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetTestParameterValueAsColRow",TestParamIndex,Value,DieX,DieY,Site)


def GetTestParameterValueAsNum(TestParamIndex="", SequenceNumber="", Site=""):
    """
    Sets the Test Parameter value for a given Die/SubDie.
    Status: published
    ----------
    Parameters:
        TestParamIndex:int = 0
        SequenceNumber:int = -1
        Site:int = -1
    ----------
    Response:
        SequenceNumberResponse:int
        Value:Decimal
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetTestParameterValueAsNum",TestParamIndex,SequenceNumber,Site)
    global GetTestParameterValueAsNum_Response
    if not "GetTestParameterValueAsNum_Response" in globals(): GetTestParameterValueAsNum_Response = namedtuple("GetTestParameterValueAsNum_Response", "SequenceNumberResponse,Value")
    return GetTestParameterValueAsNum_Response(int(rsp[0]),Decimal(rsp[1]))

def GetTestParameterValueAsColRow(TestParamIndex="", DieX="", DieY="", Site=""):
    """
    Sets the Test Parameter value for a given Die/SubDie.
    Status: published
    ----------
    Parameters:
        TestParamIndex:int = 0
        DieX:int = 0
        DieY:int = 0
        Site:int = -1
    ----------
    Response:
        DieXResponse:int
        DieYResponse:int
        Value:Decimal
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetTestParameterValueAsColRow",TestParamIndex,DieX,DieY,Site)
    global GetTestParameterValueAsColRow_Response
    if not "GetTestParameterValueAsColRow_Response" in globals(): GetTestParameterValueAsColRow_Response = namedtuple("GetTestParameterValueAsColRow_Response", "DieXResponse,DieYResponse,Value")
    return GetTestParameterValueAsColRow_Response(int(rsp[0]),int(rsp[1]),Decimal(rsp[2]))

def DeleteAllTestParameters():
    """
    Deletes all the Test Parameters.
    Status: published
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("DeleteAllTestParameters")


def SetTestParameterForDisplay(TestParamIndex=""):
    """
    Sets the Test Parameter bins to show on the Wafer Display.
    Status: published
    ----------
    Parameters:
        TestParamIndex:int = 0
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetTestParameterForDisplay",TestParamIndex)


def NewTesterProject(LotID="", TileID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command informs the tester that a new Lot/Tile is to be tested. The tester
    responds with the correct project name for the test. This is needed because the
    Probe Station needs to verify that the correct project is loaded. In case no
    valid project is available, the command is returned with an error.
    Status: internal
    ----------
    Parameters:
        LotID:str = ""
        TileID:str = ""
    ----------
    Response:
        ProjectName:str
    ----------
    Command Timeout: 30000
    Example:NewTesterProject Lot01 Tile01
    """
    rsp = MessageServerInterface.sendSciCommand("NewTesterProject",LotID,TileID)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def StartMeasurement(DieColumn="", DieRow="", ActiveDies="", SubDieIndex=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command tells the tester to begin measuring (Needles are in correct
    position and in contact). The command is responded when the measurement has
    finished. The response string holds the binning information separated by comma.
    For deactivated dies, a bin value of '0' should be responded.
    Status: internal
    ----------
    Parameters:
        DieColumn:int = 0
        DieRow:int = 0
        ActiveDies:str = ""
        SubDieIndex:int = 0
    ----------
    Response:
        BinNumbers:str
    ----------
    Command Timeout: 100000
    Example:StartMeasurement 1 1 1 0
    """
    rsp = MessageServerInterface.sendSciCommand("StartMeasurement",DieColumn,DieRow,ActiveDies,SubDieIndex)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def EndOfWafer():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command tells the tester, that the test of the current substrate has
    finished. It enables the tester application to save measurement data and/or
    prepare for the next substrate.
    Status: internal
    ----------
    Command Timeout: 30000
    Example:EndOfWafer
    """
    MessageServerInterface.sendSciCommand("EndOfWafer")


def EndOfLot():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command tells the tester, that the test of the current lot has finished. It
    enables the tester application to save measurement data and/or prepare for the
    next lot.
    Status: internal
    ----------
    Command Timeout: 30000
    Example:EndOfLot
    """
    MessageServerInterface.sendSciCommand("EndOfLot")


def VerifyProductID(ProductID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command informs the tester about the ProductID that is to be tested. The
    tester can respond with an error in case the ProductID is not allowed for
    testing.
    Status: internal
    ----------
    Parameters:
        ProductID:str = ""
    ----------
    Command Timeout: 30000
    Example:VerifyProductID Product123
    """
    MessageServerInterface.sendSciCommand("VerifyProductID",ProductID)


def VerifyLotID(LotID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command informs the tester about the LotID that is to be tested. The tester
    can respond with an error in case the LotID is not allowed for testing.
    Status: internal
    ----------
    Parameters:
        LotID:str = ""
    ----------
    Command Timeout: 30000
    Example:VerifyLotID Lot123
    """
    MessageServerInterface.sendSciCommand("VerifyLotID",LotID)


def VerifySubstrateID(SubstrateID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command informs the tester about the SubstrateID that is to be tested. The
    tester can respond with an error in case the SubstrateID is not allowed for
    testing.
    Status: internal
    ----------
    Parameters:
        SubstrateID:str = ""
    ----------
    Command Timeout: 30000
    Example:VerifySubstrateID Substrate123
    """
    MessageServerInterface.sendSciCommand("VerifySubstrateID",SubstrateID)


def VerifyProbecard(ProbeCard="", Touchdowns=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command informs the tester about the ProbecardID and touchdowns that is
    used for testing. The tester can respond with an error in case the Probecard is
    not allowed for testing.
    Status: internal
    ----------
    Parameters:
        ProbeCard:str = ""
        Touchdowns:int = 0
    ----------
    Command Timeout: 30000
    Example:VerifyProbecard Probecard123 10596
    """
    MessageServerInterface.sendSciCommand("VerifyProbecard",ProbeCard,Touchdowns)


def VerifyUserID(User=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command informs the tester about the User ID. The tester can respond with
    an error in case the User ID is not allowed for testing.
    Status: internal
    ----------
    Parameters:
        User:str = ""
    ----------
    Command Timeout: 30000
    Example:VerifyUserID User123
    """
    MessageServerInterface.sendSciCommand("VerifyUserID",User)


def TesterAbort():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command informs the tester that the job was aborted and no more test will
    happen.
    Status: internal
    ----------
    Command Timeout: 30000
    Example:TesterAbort
    """
    MessageServerInterface.sendSciCommand("TesterAbort")


def VerifySOTReady():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command informs the tester that a wafer is ready for testing which will
    immediately start. This command is sent in the recipe sequence "Verify
    SOTReady".
    Status: internal
    ----------
    Command Timeout: 30000
    Example:VerifySOTReady
    """
    MessageServerInterface.sendSciCommand("VerifySOTReady")


def VerifyWaferStart(SubstrateID="", CassettePlace="", LotID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command is sent in the VeloxPro recipe sequence "Verify Wafer Start" and
    informs the tester about the current wafer on the Chuck.
    Status: internal
    ----------
    Parameters:
        SubstrateID:str = ""
        CassettePlace:str = ""
        LotID:str = ""
    ----------
    Command Timeout: 30000
    Example:VerifyWaferStart Wafer01 1 Lot01
    """
    MessageServerInterface.sendSciCommand("VerifyWaferStart",SubstrateID,CassettePlace,LotID)


def TesterCassetteInfo(CassetteCmd=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command will be sent after the user selected which wafers are to be tested.
    It contains a string which represents the state of each wafer: 0 = empty, 1 =
    full (and selected), 2 = error (e.g. double slotted), 3 = unknown, 4 =
    deselected
    Status: internal
    ----------
    Parameters:
        CassetteCmd:str = ""
    ----------
    Response:
        CassetteRsp:str
    ----------
    Command Timeout: 30000
    Example:TesterCassetteInfo 0000001110000000010010111
    """
    rsp = MessageServerInterface.sendSciCommand("TesterCassetteInfo",CassetteCmd)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def VerifyProject(ProjectName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command is sent after selecting a project file in the VeloxPro product
    setup page. The command sends the name of the project to tester for
    verification.
    Status: internal
    ----------
    Parameters:
        ProjectName:str = ""
    ----------
    Command Timeout: 30000
    Example:VerifyProject C:/Users/Public/Documents/Velox/Projects/Test.spp
    """
    MessageServerInterface.sendSciCommand("VerifyProject",ProjectName)


def TesterAbortWafer():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command informs the tester that the test for the current wafer was aborted
    and no more tests will happen with the current wafer. The job will continue
    though.
    Status: internal
    ----------
    Command Timeout: 30000
    Example:TesterAbortWafer
    """
    MessageServerInterface.sendSciCommand("TesterAbortWafer")


def StartScript(ScriptName=""):
    """
    Starts the script and returns the response immediately.
    Status: published
    ----------
    Parameters:
        ScriptName:str = ""
    ----------
    Command Timeout: 10000
    Example:StartScript myscript
    """
    MessageServerInterface.sendSciCommand("StartScript",ScriptName)


def GetRunStatus(ScriptName=""):
    """
    Command returns information about Communicator status.
    Status: published
    ----------
    Parameters:
        ScriptName:str = ""
    ----------
    Response:
        Running:int
        LastError:int
        Title:str
    ----------
    Command Timeout: 5000
    Example:GetRunStatus
    """
    rsp = MessageServerInterface.sendSciCommand("GetRunStatus",ScriptName)
    global GetRunStatus_Response
    if not "GetRunStatus_Response" in globals(): GetRunStatus_Response = namedtuple("GetRunStatus_Response", "Running,LastError,Title")
    return GetRunStatus_Response(int(rsp[0]),int(rsp[1]),str("" if len(rsp) < 3 else ' '.join(rsp[2:])))

def CloseCommunicator():
    """
    Command closes the program. Used during ProjectFile handling.
    Status: published
    ----------
    Command Timeout: 10000
    Example:CloseCommunicator
    """
    MessageServerInterface.sendSciCommand("CloseCommunicator")


def DoScript(ScriptName=""):
    """
    Executes the script and returns the response afterwards.
    Status: published
    ----------
    Parameters:
        ScriptName:str = ""
    ----------
    Command Timeout: 10000000
    Example:DoScript myscript
    """
    MessageServerInterface.sendSciCommand("DoScript",ScriptName)


def ReadKernelData(SilentMode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Reads Kernel Data to KernelSetup (Left Program pane).
    Status: internal
    ----------
    Parameters:
        SilentMode:int = 0
    ----------
    Command Timeout: 300000
    Example:ReadKernelData 0
    """
    MessageServerInterface.sendSciCommand("ReadKernelData",SilentMode)


def SaveKernelDataAs(FileName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Saves Kernel Data (Left Program pane) to File. An existing File will be
    overwritten. If the Folder does not exist, it will be created
    Status: internal
    ----------
    Parameters:
        FileName:str = ""
    ----------
    Command Timeout: 10000
    Example:SaveKernelDataAs C:/Temp/RCConfigSample1.xml
    """
    MessageServerInterface.sendSciCommand("SaveKernelDataAs",FileName)


def LoadConfigFile(FileName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Loads File Data to KernelSetup (Right Program pane).
    Status: internal
    ----------
    Parameters:
        FileName:str = ""
    ----------
    Command Timeout: 10000
    Example:LoadConfigFile C:/Temp/RCConfigSample1.xml
    """
    MessageServerInterface.sendSciCommand("LoadConfigFile",FileName)


def ReplaceKernelDataByFileData(SilentMode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Replaces Kernel Data (Left pane) by File Data (Right pane).
    Status: internal
    ----------
    Parameters:
        SilentMode:int = 0
    ----------
    Command Timeout: 300000
    Example:ReplaceKernelDataByFileData 0
    """
    MessageServerInterface.sendSciCommand("ReplaceKernelDataByFileData",SilentMode)


def ReplaceFileTreeByKernelData(SilentMode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Replaces File Tree (Right pane) by Kernel Data (Left pane).
    Status: internal
    ----------
    Parameters:
        SilentMode:int = 0
    ----------
    Command Timeout: 300000
    Example:ReplaceFileTreeByKernelData 0
    """
    MessageServerInterface.sendSciCommand("ReplaceFileTreeByKernelData",SilentMode)


def SaveFileTreeAs(FileName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Saves File Tree (Right pane) to File. An existing File will be overwritten. If
    the Folder does not exist, it will be created.
    Status: internal
    ----------
    Parameters:
        FileName:str = ""
    ----------
    Command Timeout: 10000
    Example:SaveFileTreeAs C:/Temp/RCConfigSample2.xml
    """
    MessageServerInterface.sendSciCommand("SaveFileTreeAs",FileName)


def HeatChuck(Temperature="", Unit="", ReduceContact=""):
    """
    Sets a new target temperature and starts the heating or cooling of the Chuck. An
    answer to the command will be returned after reaching the given temperature and
    waiting the soak time or an unexpected interrupt of the process. Given back is
    the already reached temperature.
    Status: published
    ----------
    Parameters:
        Temperature:Decimal = 25
        Unit:str = "Celsius"
        ReduceContact:int = 1
    ----------
    Response:
        RespTemperature:Decimal
        RespUnit:str
    ----------
    Command Timeout: 36000000
    Example:HeatChuck 61.3 C
    """
    rsp = MessageServerInterface.sendSciCommand("HeatChuck",Temperature,Unit,ReduceContact)
    global HeatChuck_Response
    if not "HeatChuck_Response" in globals(): HeatChuck_Response = namedtuple("HeatChuck_Response", "RespTemperature,RespUnit")
    return HeatChuck_Response(Decimal(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def SetHeaterTemp(Temperature="", Unit="", UseContactSafety=""):
    """
    Sets a new target temperature and starts the heating or cooling of the thermal
    Chuck. The new target temperature is returned immediately as the command does
    not wait until heating is complete.
    Status: published
    ----------
    Parameters:
        Temperature:Decimal = 25
        Unit:str = "Celsius"
        UseContactSafety:int = 1
    ----------
    Response:
        RespTemperature:Decimal
        RespUnit:str
    ----------
    Command Timeout: 60000
    Example:SetHeaterTemp 55.5 C
    """
    rsp = MessageServerInterface.sendSciCommand("SetHeaterTemp",Temperature,Unit,UseContactSafety)
    global SetHeaterTemp_Response
    if not "SetHeaterTemp_Response" in globals(): SetHeaterTemp_Response = namedtuple("SetHeaterTemp_Response", "RespTemperature,RespUnit")
    return SetHeaterTemp_Response(Decimal(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def GetHeaterTemp(Unit="", ExternalHeaterID=""):
    """
    Reads the current temperature of the Chuck and determines the status of the
    thermal system.
    Status: published
    ----------
    Parameters:
        Unit:str = "Celsius"
        ExternalHeaterID:int = 0
    ----------
    Response:
        RespTemperature:Decimal
        RespUnit:str
        Status:str
    ----------
    Command Timeout: 60000
    Example:GetHeaterTemp C
    """
    rsp = MessageServerInterface.sendSciCommand("GetHeaterTemp",Unit,ExternalHeaterID)
    global GetHeaterTemp_Response
    if not "GetHeaterTemp_Response" in globals(): GetHeaterTemp_Response = namedtuple("GetHeaterTemp_Response", "RespTemperature,RespUnit,Status")
    return GetHeaterTemp_Response(Decimal(rsp[0]),str(rsp[1]),str("" if len(rsp) < 3 else ' '.join(rsp[2:])))

def EnableHeaterHoldMode(HoldMode=""):
    """
    Switches the Thermal Chuck devices hold mode on or off. In hold mode the Chuck
    is heated with a constant current to avoid noise from the temperature control.
    The hold mode can be enabled only in HoldReady state.
    Status: published
    ----------
    Parameters:
        HoldMode:int = 1
    ----------
    Response:
        RespHoldMode:int
    ----------
    Command Timeout: 60000
    Example:EnableHeaterHoldMode 1
    """
    rsp = MessageServerInterface.sendSciCommand("EnableHeaterHoldMode",HoldMode)
    return int(rsp[0])

def StopHeatChuck():
    """
    Stops a pending heating or cooling process. If the device is not at temperature,
    the actual temperature is set as target temperature.
    Status: published
    ----------
    Command Timeout: 60000
    Example:StopHeatChuck
    """
    MessageServerInterface.sendSciCommand("StopHeatChuck")


def GetDewPointTemp(Unit=""):
    """
    Returns the current dew point temperature if a dew point sensor is connected.
    Status: published
    ----------
    Parameters:
        Unit:str = "Celsius"
    ----------
    Response:
        RespTemperature:Decimal
        RespUnit:str
    ----------
    Command Timeout: 60000
    Example:GetDewPointTemp C
    """
    rsp = MessageServerInterface.sendSciCommand("GetDewPointTemp",Unit)
    global GetDewPointTemp_Response
    if not "GetDewPointTemp_Response" in globals(): GetDewPointTemp_Response = namedtuple("GetDewPointTemp_Response", "RespTemperature,RespUnit")
    return GetDewPointTemp_Response(Decimal(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def GetTemperatureChuckOptions():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the currently set thermal Chuck options.
    Status: internal
    ----------
    Response:
        UseSoakTime:int
        Unused:int
        CurrConnection:int
        MinTemperature:Decimal
        MaxTemperature:Decimal
        UsePurge:int
        UseDynamicSoakTime:int
        UseFixedDieSoakTime:int
        UseDynamicDieSoakTime:int
        UseEcoMode:int
        PurgeOnChamberDoor:int
        ForceBypassPurge:int
        DoorClosedTime:int
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("GetTemperatureChuckOptions")
    global GetTemperatureChuckOptions_Response
    if not "GetTemperatureChuckOptions_Response" in globals(): GetTemperatureChuckOptions_Response = namedtuple("GetTemperatureChuckOptions_Response", "UseSoakTime,Unused,CurrConnection,MinTemperature,MaxTemperature,UsePurge,UseDynamicSoakTime,UseFixedDieSoakTime,UseDynamicDieSoakTime,UseEcoMode,PurgeOnChamberDoor,ForceBypassPurge,DoorClosedTime")
    return GetTemperatureChuckOptions_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),int(rsp[5]),int(rsp[6]),int(rsp[7]),int(rsp[8]),int(rsp[9]),int(rsp[10]),int(rsp[11]),int(rsp[12]))

def SetTemperatureChuckOptions(UseFixedWaferSoak="", Unused="", CurrConnection="", UsePurge="", UseDynamicWaferSoak="", UseFixedDieSoakTime="", UseDynamicDieSoakTime="", UseEcoMode="", PurgeOnChamberDoor="", ForceBypassPurge="", DoorClosedTime=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command is used to change the currently set thermal Chuck options.
    Status: internal
    ----------
    Parameters:
        UseFixedWaferSoak:int = -1
        Unused:int = -1
        CurrConnection:int = -1
        UsePurge:int = -1
        UseDynamicWaferSoak:int = -1
        UseFixedDieSoakTime:int = -1
        UseDynamicDieSoakTime:int = -1
        UseEcoMode:int = -1
        PurgeOnChamberDoor:int = -1
        ForceBypassPurge:int = -1
        DoorClosedTime:int = -1
    ----------
    Response:
        UseFixedWaferSoakRsp:int
        SyncTempRsp:int
        CurrConnectionRsp:int
        UsePurgeRsp:int
        UseDynamicWaferSoakRsp:int
        UseFixedDieSoakTimeRsp:int
        UseDynamicDieSoakTimeRsp:int
        UseEcoModeRsp:int
        PurgeOnChamberDoorRsp:int
        ForceBypassPurgeRsp:int
        DoorClosedTimeRsp:int
    ----------
    Command Timeout: 300000
    Example:SetTemperatureChuckOptions 1 0 1 1 1 1 1
    """
    rsp = MessageServerInterface.sendSciCommand("SetTemperatureChuckOptions",UseFixedWaferSoak,Unused,CurrConnection,UsePurge,UseDynamicWaferSoak,UseFixedDieSoakTime,UseDynamicDieSoakTime,UseEcoMode,PurgeOnChamberDoor,ForceBypassPurge,DoorClosedTime)
    global SetTemperatureChuckOptions_Response
    if not "SetTemperatureChuckOptions_Response" in globals(): SetTemperatureChuckOptions_Response = namedtuple("SetTemperatureChuckOptions_Response", "UseFixedWaferSoakRsp,SyncTempRsp,CurrConnectionRsp,UsePurgeRsp,UseDynamicWaferSoakRsp,UseFixedDieSoakTimeRsp,UseDynamicDieSoakTimeRsp,UseEcoModeRsp,PurgeOnChamberDoorRsp,ForceBypassPurgeRsp,DoorClosedTimeRsp")
    return SetTemperatureChuckOptions_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),int(rsp[4]),int(rsp[5]),int(rsp[6]),int(rsp[7]),int(rsp[8]),int(rsp[9]),int(rsp[10]))

def GetHeaterSoak():
    """
    Returns the current soak time values in seconds and the soaking status.
    Status: published
    ----------
    Response:
        FixedWaferSoakTime:int
        FixedWaferSoakStatus:int
        DynamicWaferSoakTime:Decimal
        DynamicWaferSoakStatus:int
        FixedDieSoakTime:Decimal
        DynamicDieSoakTime:Decimal
        FixedDieSoakStatus:int
        DynamicDieSoakStatus:int
    ----------
    Command Timeout: 60000
    Example:GetHeaterSoak
    """
    rsp = MessageServerInterface.sendSciCommand("GetHeaterSoak")
    global GetHeaterSoak_Response
    if not "GetHeaterSoak_Response" in globals(): GetHeaterSoak_Response = namedtuple("GetHeaterSoak_Response", "FixedWaferSoakTime,FixedWaferSoakStatus,DynamicWaferSoakTime,DynamicWaferSoakStatus,FixedDieSoakTime,DynamicDieSoakTime,FixedDieSoakStatus,DynamicDieSoakStatus")
    return GetHeaterSoak_Response(int(rsp[0]),int(rsp[1]),Decimal(rsp[2]),int(rsp[3]),Decimal(rsp[4]),Decimal(rsp[5]),int(rsp[6]),int(rsp[7]))

def SetHeaterSoak(FixedWaferSoakTime="", DynamicWaferSoakTime="", FixedDieSoakTime="", DynamicDieSoakTime=""):
    """
    Sets the new soak time values. The unit of the values is seconds. If soak time
    is actually running, it may be affected by the change.
    Status: published
    ----------
    Parameters:
        FixedWaferSoakTime:int = 60
        DynamicWaferSoakTime:Decimal = -1
        FixedDieSoakTime:Decimal = -1
        DynamicDieSoakTime:Decimal = -1
    ----------
    Command Timeout: 60000
    Example:SetHeaterSoak 60
    """
    MessageServerInterface.sendSciCommand("SetHeaterSoak",FixedWaferSoakTime,DynamicWaferSoakTime,FixedDieSoakTime,DynamicDieSoakTime)


def EnableHeaterStandby(Standby=""):
    """
    Switches the power save (standby) mode of the device on or off. If the device is
    in power save mode, setting and reading temperatures switches off the power save
    mode automatically.
    Status: published
    ----------
    Parameters:
        Standby:int = 1
    ----------
    Response:
        RespStandby:int
    ----------
    Command Timeout: 60000
    Example:EnableHeaterStandby 1
    """
    rsp = MessageServerInterface.sendSciCommand("EnableHeaterStandby",Standby)
    return int(rsp[0])

def ReadTemperatureChuckStatus():
    """
    Returns values of the thermal Chuck status. The status byte gives information
    about the current controller's action. The dew point sensor status encapsulates
    information, if such a sensor is connected and if the actual dew point
    difference temperature is readable (active). It can be used for purge control.
    Soak time left (in seconds) is used when soak time is actually running.
    Status: published
    ----------
    Response:
        Status:str
        DPSensor:int
        SoakTimeLeft:int
        HasEcoMode:int
    ----------
    Command Timeout: 60000
    Example:ReadTemperatureChuckStatus
    """
    rsp = MessageServerInterface.sendSciCommand("ReadTemperatureChuckStatus")
    global ReadTemperatureChuckStatus_Response
    if not "ReadTemperatureChuckStatus_Response" in globals(): ReadTemperatureChuckStatus_Response = namedtuple("ReadTemperatureChuckStatus_Response", "Status,DPSensor,SoakTimeLeft,HasEcoMode")
    return ReadTemperatureChuckStatus_Response(str(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def GetTargetTemp(Unit=""):
    """
    Reads the target temperature of the Chuck.
    Status: published
    ----------
    Parameters:
        Unit:str = "Celsius"
    ----------
    Response:
        RespTemperature:Decimal
        RespUnit:str
    ----------
    Command Timeout: 60000
    Example:GetTargetTemp C
    """
    rsp = MessageServerInterface.sendSciCommand("GetTargetTemp",Unit)
    global GetTargetTemp_Response
    if not "GetTargetTemp_Response" in globals(): GetTargetTemp_Response = namedtuple("GetTargetTemp_Response", "RespTemperature,RespUnit")
    return GetTargetTemp_Response(Decimal(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def SetThermoWindow(Window=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command sets the window for the target temperature which is the window in which
    a station is assumed to be at temp. Only supported on Nucleus stations.
    Status: internal
    ----------
    Parameters:
        Window:Decimal = 1
    ----------
    Response:
        RespWindow:Decimal
    ----------
    Command Timeout: 60000
    Example:SetThermoWindow 2.0
    """
    rsp = MessageServerInterface.sendSciCommand("SetThermoWindow",Window)
    return Decimal(rsp[0])

def GetThermoWindow():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command returns the current Thermal window which is the window in which a
    station is assumed to be at temp. Only supported on Nucleus stations.
    Status: internal
    ----------
    Response:
        RespWindow:Decimal
    ----------
    Command Timeout: 60000
    Example:GetThermoWindow
    """
    rsp = MessageServerInterface.sendSciCommand("GetThermoWindow")
    return Decimal(rsp[0])

def SendThermoCommand(Command=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sends a command string to the thermal Chuck using the thermal Chuck protocol and
    returns the thermal Chucks response as command response. This command can be
    used to access thermal Chuck features that are not exposed as standalone SCI
    commands. Command is currently implemented for ERS and ATT Chucks.
    Status: internal
    ----------
    Parameters:
        Command:str = ""
    ----------
    Response:
        Response:str
    ----------
    Command Timeout: 5000
    Example:SendThermoCommand RH
    """
    rsp = MessageServerInterface.sendSciCommand("SendThermoCommand",Command)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ReadAuxStatus(AuxID=""):
    """
    Returns the status of a single AUX site.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
    ----------
    Response:
        AuxIDEcho:int
        FlagsMode:int
        Comp:str
        PresetHeight:str
        AuxSiteType:str
    ----------
    Command Timeout: 10000
    Example:ReadAuxStatus 1
    """
    rsp = MessageServerInterface.sendSciCommand("ReadAuxStatus",AuxID)
    global ReadAuxStatus_Response
    if not "ReadAuxStatus_Response" in globals(): ReadAuxStatus_Response = namedtuple("ReadAuxStatus_Response", "AuxIDEcho,FlagsMode,Comp,PresetHeight,AuxSiteType")
    return ReadAuxStatus_Response(int(rsp[0]),int(rsp[1]),str(rsp[2]),str(rsp[3]),str("" if len(rsp) < 5 else ' '.join(rsp[4:])))

def ReadAuxPosition(AuxID="", Unit="", PosRef="", Comp=""):
    """
    Returns the actual AUX sites position in X, Y and Z. With AUX ID set to 0, the
    position is read for the Chuck stage. If no AUX ID is given, it tries to read
    the position from the active site.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        Unit:str = "Microns"
        PosRef:str = "Home"
        Comp:str = "Technology"
    ----------
    Response:
        AuxIDEcho:int
        X:Decimal
        Y:Decimal
        Z:Decimal
    ----------
    Command Timeout: 10000
    Example:ReadAuxPosition 1 Y Z
    """
    rsp = MessageServerInterface.sendSciCommand("ReadAuxPosition",AuxID,Unit,PosRef,Comp)
    global ReadAuxPosition_Response
    if not "ReadAuxPosition_Response" in globals(): ReadAuxPosition_Response = namedtuple("ReadAuxPosition_Response", "AuxIDEcho,X,Y,Z")
    return ReadAuxPosition_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]))

def ReadAuxHeights(AuxID="", Unit=""):
    """
    Returns the actual technology heights from an AUX site. If AUX ID is set to 0,
    all response values are read from Chuck stage. If no AUX ID is given, it tries
    to read the heights from the active site.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        Unit:str = "Microns"
    ----------
    Response:
        AuxIDEcho:int
        Contact:Decimal
        Overtravel:Decimal
        AlignDist:Decimal
        SepDist:Decimal
    ----------
    Command Timeout: 10000
    Example:ReadAuxHeights 1 Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadAuxHeights",AuxID,Unit)
    global ReadAuxHeights_Response
    if not "ReadAuxHeights_Response" in globals(): ReadAuxHeights_Response = namedtuple("ReadAuxHeights_Response", "AuxIDEcho,Contact,Overtravel,AlignDist,SepDist")
    return ReadAuxHeights_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]))

def SetAuxMode(AuxID="", Overtravel=""):
    """
    Modes manage the way a stage behaves when it is in Contact Height. AUX site mode
    holds only a single flag. Flags can be turned on by using the value 1 or turned
    off by using the value 0. If you do not want to change the flag - use the value
    of 2. If AUX ID is set to 0, all flags are set for Chuck stage. AUX site will
    move an additional overtravel on every contact move.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        Overtravel:int = 2
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 10000
    Example:SetAuxMode 1 2
    """
    rsp = MessageServerInterface.sendSciCommand("SetAuxMode",AuxID,Overtravel)
    return int(rsp[0])

def SetAuxHome(AuxID="", Mode="", Unit="", XValue="", YValue=""):
    """
    Sets the AUX sites Home position in X and Y. It defines the origin of the AUX
    sites coordinate system for later movements. Usually this position is identical
    to the die home position.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        Mode:str = "0"
        Unit:str = "Microns"
        XValue:Decimal = 0
        YValue:Decimal = 0
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 10000
    Example:SetAuxHome 1 0 Y
    """
    rsp = MessageServerInterface.sendSciCommand("SetAuxHome",AuxID,Mode,Unit,XValue,YValue)
    return int(rsp[0])

def SetAuxIndex(AuxID="", XValue="", YValue="", Unit=""):
    """
    Sets the AUX sites index size. If AUX ID is set to 0, index size is set for
    Chuck stage.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        XValue:Decimal = 0
        YValue:Decimal = 0
        Unit:str = "Microns"
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 10000
    Example:SetAuxIndex 1 1000. 1000. Y
    """
    rsp = MessageServerInterface.sendSciCommand("SetAuxIndex",AuxID,XValue,YValue,Unit)
    return int(rsp[0])

def SetAuxHeight(AuxID="", PresetHeight="", Mode="", Unit="", Value=""):
    """
    Sets the AUX sites Contact Height and corresponding gaps for Overtravel,
    alignment and separation height. A Contact Height search gap for contact search
    with edge sensor can also be set. This search gap is always identical for all
    AUX sites. Without any optional parameters the command sets Contact Height to
    the current position.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        PresetHeight:str = "Contact"
        Mode:str = "0"
        Unit:str = "Microns"
        Value:Decimal = 0
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 10000
    Example:SetAuxHeight 1 C 0 Y
    """
    rsp = MessageServerInterface.sendSciCommand("SetAuxHeight",AuxID,PresetHeight,Mode,Unit,Value)
    return int(rsp[0])

def ReadAuxIndex(AuxID="", Unit=""):
    """
    Returns the actual AUX sites index values. If AUX ID is set to 0, the index size
    is read from Chuck stage. If no AUX ID is given, it tries to read the index from
    the active site.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        Unit:str = "Microns"
    ----------
    Response:
        AuxIDEcho:int
        IndexX:Decimal
        IndexY:Decimal
    ----------
    Command Timeout: 10000
    Example:ReadAuxIndex 1 Y
    """
    rsp = MessageServerInterface.sendSciCommand("ReadAuxIndex",AuxID,Unit)
    global ReadAuxIndex_Response
    if not "ReadAuxIndex_Response" in globals(): ReadAuxIndex_Response = namedtuple("ReadAuxIndex_Response", "AuxIDEcho,IndexX,IndexY")
    return ReadAuxIndex_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def SetAuxThetaHome(AuxID="", Mode="", Unit="", Position=""):
    """
    Sets the AUX sites theta home position. It defines the origin of the AUX sites
    theta coordinate system for later movements. If AUX ID is set to 0, theta home
    position is set for Chuck stage.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        Mode:str = "0"
        Unit:str = "Microns"
        Position:Decimal = 0
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 10000
    Example:SetAuxThetaHome 1 0
    """
    rsp = MessageServerInterface.sendSciCommand("SetAuxThetaHome",AuxID,Mode,Unit,Position)
    return int(rsp[0])

def EnableOffset(Stage="", Enable="", Move=""):
    """
    Enables or disables the Offset XY compensation for the selected stage. If the
    compensation holds an offset different from zero, the Chuck is automatically
    moved the distance of the offset. The Chuck also moves automatically to a safe
    height. The move can be disabled by the third parameter. This may put the stage
    outside the software fence.
    Status: published
    ----------
    Parameters:
        Stage:str = "Chuck"
        Enable:int = 1
        Move:int = 1
    ----------
    Command Timeout: 60000
    Example:EnableOffset C 1
    """
    MessageServerInterface.sendSciCommand("EnableOffset",Stage,Enable,Move)


def SetOffset(Stage="", OffsetX="", OffsetY=""):
    """
    Sets the offset values for the Offset XY compensation for the selected stage.
    The changes take effect immediately. Note that the Offset XY compensation must
    be enabled for the values to take effect. The compensation is enabled or
    disabled using EnableOffset command.
    Status: published
    ----------
    Parameters:
        Stage:str = "Chuck"
        OffsetX:Decimal = 0
        OffsetY:Decimal = 0
    ----------
    Command Timeout: 5000
    Example:SetOffset C 100000.0 0.0
    """
    MessageServerInterface.sendSciCommand("SetOffset",Stage,OffsetX,OffsetY)


def GetOffsetInfo(Stage=""):
    """
    Gets information about the Offset XY compensation of the selected stage,
    including the stored offset values and whether the compensation is enabled or
    disabled.
    Status: published
    ----------
    Parameters:
        Stage:str = "Chuck"
    ----------
    Response:
        Enable:int
        OffsetX:Decimal
        OffsetY:Decimal
    ----------
    Command Timeout: 5000
    Example:GetOffsetInfo C
    """
    rsp = MessageServerInterface.sendSciCommand("GetOffsetInfo",Stage)
    global GetOffsetInfo_Response
    if not "GetOffsetInfo_Response" in globals(): GetOffsetInfo_Response = namedtuple("GetOffsetInfo_Response", "Enable,OffsetX,OffsetY")
    return GetOffsetInfo_Response(int(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]))

def SetSwitchPosition(Stage="", AuxSite="", X="", Y=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the switch position of a stage. This is the position to move to if an AUX
    Site gets active. This is only supported for the Chuck and it's aux sites. Aux
    index 0 means wafer site, 1 means aux site 1 and so on.
    Status: internal
    ----------
    Parameters:
        Stage:str = "Chuck"
        AuxSite:int = 0
        X:Decimal = 0
        Y:Decimal = 0
    ----------
    Command Timeout: 5000
    Example:SetSwitchPosition C 0 5000 5000
    """
    MessageServerInterface.sendSciCommand("SetSwitchPosition",Stage,AuxSite,X,Y)


def MoveAuxSite(AuxID=""):
    """
    Moves the Chuck to the position of a given AUX site. A safe height is used for
    the move. If AUX ID is set to 0, the target of the move is the wafer site.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 60000
    Example:MoveAuxSite 1
    """
    rsp = MessageServerInterface.sendSciCommand("MoveAuxSite",AuxID)
    return int(rsp[0])

def SetAuxSiteCount(AuxSiteCount=""):
    """
    Sets the number of available AUX sites. For preparing for example two cal
    Chucks, the count must be set to 2. For the changes to take effect the system
    needs to be restarted.
    Status: published
    ----------
    Parameters:
        AuxSiteCount:int = 0
    ----------
    Command Timeout: 10000
    Example:SetAuxSiteCount 2
    """
    MessageServerInterface.sendSciCommand("SetAuxSiteCount",AuxSiteCount)


def GetAuxSiteCount():
    """
    Reads the number of available AUX sites and the ID of the actual active AUX
    site. If this is 0, the Chuck stage is currently active.
    Status: published
    ----------
    Response:
        AuxSiteCount:int
        ActualAuxSite:int
    ----------
    Command Timeout: 10000
    Example:GetAuxSiteCount
    """
    rsp = MessageServerInterface.sendSciCommand("GetAuxSiteCount")
    global GetAuxSiteCount_Response
    if not "GetAuxSiteCount_Response" in globals(): GetAuxSiteCount_Response = namedtuple("GetAuxSiteCount_Response", "AuxSiteCount,ActualAuxSite")
    return GetAuxSiteCount_Response(int(rsp[0]),int(rsp[1]))

def SetAuxSiteName(AuxID="", AuxSiteName=""):
    """
    Sets the description of an AUX site. With AUX ID zero, the description of the
    wafer site can be set.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        AuxSiteName:str = ""
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 10000
    Example:SetAuxSiteName 1 AUX Site 1
    """
    rsp = MessageServerInterface.sendSciCommand("SetAuxSiteName",AuxID,AuxSiteName)
    return int(rsp[0])

def GetAuxSiteName(AuxID=""):
    """
    This command reads the description of an AUX site. If AUX ID is set to 0, the
    description of the Chuck stage is given back. If no AUX ID is given, it tries to
    read from the active site.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
    ----------
    Response:
        AuxIDEcho:int
        AuxSiteName:str
    ----------
    Command Timeout: 10000
    Example:GetAuxSiteName 1
    """
    rsp = MessageServerInterface.sendSciCommand("GetAuxSiteName",AuxID)
    global GetAuxSiteName_Response
    if not "GetAuxSiteName_Response" in globals(): GetAuxSiteName_Response = namedtuple("GetAuxSiteName_Response", "AuxIDEcho,AuxSiteName")
    return GetAuxSiteName_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def CleanProbeTip(AuxID=""):
    """
    Starts a probe tip cleaning on the given AUX site. The cleaning algorithm is
    dependent from the type of the AUX site and from the duration and the cleaning
    count that is set in configuration. The cleaning algorithm includes both a move
    to the pad site and a move back to the source site.
    Status: published
    ----------
    Parameters:
        AuxID:str = "-1"
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 300000
    Example:CleanProbeTip 1
    """
    rsp = MessageServerInterface.sendSciCommand("CleanProbeTip",AuxID)
    return int(rsp[0])

def SetAuxSiteType(AuxID="", AuxSiteType=""):
    """
    Sets the type for a given AUX site. It depends on the type of the AUX site, if
    there is a cleaning algorithm available. It is not possible to set the type of
    the wafer site (AUX site 0).
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        AuxSiteType:str = "AuxUnknown"
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 10000
    Example:SetAuxSiteType 1 G
    """
    rsp = MessageServerInterface.sendSciCommand("SetAuxSiteType",AuxID,AuxSiteType)
    return int(rsp[0])

def SetCleaningParams(AuxID="", Count="", Time=""):
    """
    Sets the cleaning parameters for a given AUX site. It is not possible to set the
    cleaning parameters of the wafer site (AUX site 0). If no AUX ID is given, it
    tries to set the parameters of the active site.   The cleaning count defines,
    how much times the cleaning is performed repeatedly. The cleaning time defines,
    how much   milliseconds the needles wait in cleaning position during each
    cleaning cycle.
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
        Count:int = 1
        Time:int = 0
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 10000
    Example:SetCleaningParams 1 5 1000
    """
    rsp = MessageServerInterface.sendSciCommand("SetCleaningParams",AuxID,Count,Time)
    return int(rsp[0])

def GetCleaningParams(AuxID=""):
    """
    Reads the cleaning parameters of a given AUX site. It is not possible to read
    cleaning parameters of the wafer site (AUX site 0).
    Status: published
    ----------
    Parameters:
        AuxID:int = -1
    ----------
    Response:
        AuxIDEcho:int
        Count:int
        Time:int
        Remaining:int
    ----------
    Command Timeout: 30000
    Example:GetCleaningParams
    """
    rsp = MessageServerInterface.sendSciCommand("GetCleaningParams",AuxID)
    global GetCleaningParams_Response
    if not "GetCleaningParams_Response" in globals(): GetCleaningParams_Response = namedtuple("GetCleaningParams_Response", "AuxIDEcho,Count,Time,Remaining")
    return GetCleaningParams_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]))

def UpdateAuxSitePositions(AuxID="", XOffset="", YOffset=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Rotate the switch, home and fence positions to match the current Chuck theta
    angle and adjust Home/Switch by XY offset. Should only be used for Aux sites
    that don't move theta.
    Status: internal
    ----------
    Parameters:
        AuxID:int = -1
        XOffset:Decimal = 0
        YOffset:Decimal = 0
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 5000
    Example:UpdateAuxSitePositions 1
    """
    rsp = MessageServerInterface.sendSciCommand("UpdateAuxSitePositions",AuxID,XOffset,YOffset)
    return int(rsp[0])

def ResetCleaningPosition(AuxID="", OffsetX="", OffsetY=""):
    """
    Resets the cleaning position to the beginning of the cleaning AUX Site (home).
    Status: published
    ----------
    Parameters:
        AuxID:str = "-1"
        OffsetX:Decimal = 0
        OffsetY:Decimal = 0
    ----------
    Response:
        AuxIDEcho:int
    ----------
    Command Timeout: 10000
    Example:ResetCleaningPosition 5
    """
    rsp = MessageServerInterface.sendSciCommand("ResetCleaningPosition",AuxID,OffsetX,OffsetY)
    return int(rsp[0])

def BnR_EchoData(ControllerID="", TestCmd=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Test Command for the Controller Communication. It is like a ping command. The
    given text string is returned unchanged.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        TestCmd:str = "Test"
    ----------
    Response:
        TestRsp:str
    ----------
    Command Timeout: 5000
    Example:BnR_EchoData 1 Hello World
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_EchoData",ControllerID,TestCmd)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def BnR_ReportKernelVersion(ControllerID="", Module=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the actual version information of the controller software.   The
    'Version' value contains version number and revision level of the actual
    implementation.   The text string contains a code description, version number
    and the revision date.   The 'Module' byte is optional (default is K).
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Module:str = "A"
    ----------
    Response:
        Version:Decimal
        Description:str
    ----------
    Command Timeout: 5000
    Example:BnR_ReportKernelVersion 1 K
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_ReportKernelVersion",ControllerID,Module)
    global BnR_ReportKernelVersion_Response
    if not "BnR_ReportKernelVersion_Response" in globals(): BnR_ReportKernelVersion_Response = namedtuple("BnR_ReportKernelVersion_Response", "Version,Description")
    return BnR_ReportKernelVersion_Response(Decimal(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def BnR_GetStationType(ControllerID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns information about the connected station.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
    ----------
    Response:
        StationType:str
        Type:str
    ----------
    Command Timeout: 5000
    Example:BnR_GetStationType 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetStationType",ControllerID)
    global BnR_GetStationType_Response
    if not "BnR_GetStationType_Response" in globals(): BnR_GetStationType_Response = namedtuple("BnR_GetStationType_Response", "StationType,Type")
    return BnR_GetStationType_Response(str(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def BnR_ResetController(ControllerID="", Mode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Restarts the BnR controller.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Mode:str = "X"
    ----------
    Command Timeout: 10000
    Example:BnR_ResetController 1
    """
    MessageServerInterface.sendSciCommand("BnR_ResetController",ControllerID,Mode)


def BnR_GetControllerType(ControllerID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the controller type (e.g. CM300, PositionerBox) and the controller
    generation (1, 2)
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
    ----------
    Response:
        ControllerType:str
        ControllerGeneration:int
    ----------
    Command Timeout: 5000
    Example:BnR_GetControllerType 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetControllerType",ControllerID)
    global BnR_GetControllerType_Response
    if not "BnR_GetControllerType_Response" in globals(): BnR_GetControllerType_Response = namedtuple("BnR_GetControllerType_Response", "ControllerType,ControllerGeneration")
    return BnR_GetControllerType_Response(str(rsp[0]),int(rsp[1]))

def BnR_SetOutput(ControllerID="", Channel="", State="", PulseTime=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Controls the Velox output channel signals. It can be used to activate/deactivate
    outputs.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Channel:str = "DO_WaferVacuum"
        State:int = 0
        PulseTime:int = 0
    ----------
    Command Timeout: 5000
    Example:BnR_SetOutput 1 1000 1 2000
    """
    MessageServerInterface.sendSciCommand("BnR_SetOutput",ControllerID,Channel,State,PulseTime)


def BnR_GetOutput(ControllerID="", Channel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the state of an output channel. By using the string identifier DO_ALL, a
    string list of all outputs is returned in addition
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Channel:str = "DO_WaferVacuum"
    ----------
    Response:
        State:int
        AllOutputs:str
    ----------
    Command Timeout: 5000
    Example:BnR_GetOutput 1 DO_WaferVacuum
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetOutput",ControllerID,Channel)
    global BnR_GetOutput_Response
    if not "BnR_GetOutput_Response" in globals(): BnR_GetOutput_Response = namedtuple("BnR_GetOutput_Response", "State,AllOutputs")
    return BnR_GetOutput_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def BnR_GetInput(ControllerID="", Channel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the state of an input channel. By using the string identifier DI_ALL, a
    string list of all outputs is returned in addition
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Channel:str = "DI_MotorPower"
    ----------
    Response:
        State:int
        AllInputs:str
    ----------
    Command Timeout: 5000
    Example:BnR_GetInput 1 DI_MotorPower
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetInput",ControllerID,Channel)
    global BnR_GetInput_Response
    if not "BnR_GetInput_Response" in globals(): BnR_GetInput_Response = namedtuple("BnR_GetInput_Response", "State,AllInputs")
    return BnR_GetInput_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def BnR_SetAnalogOutput(ControllerID="", Channel="", OutputPercent=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets an analog output channel to a given value.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Channel:str = "AO_PurgeDewPoint"
        OutputPercent:Decimal = 50
    ----------
    Command Timeout: 5000
    Example:BnR_SetAnalogOutput 1 AO_PurgeDewPoint 50
    """
    MessageServerInterface.sendSciCommand("BnR_SetAnalogOutput",ControllerID,Channel,OutputPercent)


def BnR_GetAnalogIO(ControllerID="", Channel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the current value of an analog output or input.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Channel:str = "AO_PurgeDewPoint"
    ----------
    Response:
        Value:Decimal
        UnderOverflow:int
    ----------
    Command Timeout: 5000
    Example:BnR_GetAnalogIO 1 AO_PurgeDewPoint
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetAnalogIO",ControllerID,Channel)
    global BnR_GetAnalogIO_Response
    if not "BnR_GetAnalogIO_Response" in globals(): BnR_GetAnalogIO_Response = namedtuple("BnR_GetAnalogIO_Response", "Value,UnderOverflow")
    return BnR_GetAnalogIO_Response(Decimal(rsp[0]),int(rsp[1]))

def BnR_GetStartupStatus(ControllerID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the startup status of the BnR controller to determine if the controller
    is properly booted or still starting.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
    ----------
    Response:
        StartupStatus:str
        AdditionalStatusInfo:str
    ----------
    Command Timeout: 5000
    Example:BnR_GetStartupStatus 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetStartupStatus",ControllerID)
    global BnR_GetStartupStatus_Response
    if not "BnR_GetStartupStatus_Response" in globals(): BnR_GetStartupStatus_Response = namedtuple("BnR_GetStartupStatus_Response", "StartupStatus,AdditionalStatusInfo")
    return BnR_GetStartupStatus_Response(str(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def BnR_GetControllerData(ControllerID=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Gets controller data from the B&R controller. Currently used for init
    information.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
    ----------
    Command Timeout: 10000
    Example:BnR_GetControllerData 1
    """
    MessageServerInterface.sendSciCommand("BnR_GetControllerData",ControllerID)


def BnR_GetDataIterator(ControllerID="", ShowAll=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns a data stream handle which represents a data stream of setup parameters
    and requires the BnR_GetNextDatum command.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        ShowAll:int = 0
    ----------
    Response:
        IdentityToken:int
        SizeNoAll:int
    ----------
    Command Timeout: 5000
    Example:BnR_GetDataIterator 1 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetDataIterator",ControllerID,ShowAll)
    global BnR_GetDataIterator_Response
    if not "BnR_GetDataIterator_Response" in globals(): BnR_GetDataIterator_Response = namedtuple("BnR_GetDataIterator_Response", "IdentityToken,SizeNoAll")
    return BnR_GetDataIterator_Response(int(rsp[0]),int(rsp[1]))

def BnR_GetNextDatum(ControllerID="", IdentityToken=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the next parameter from the data stream. Fields are separated by a
    colon. Structure of the response parameter Value:
    Path_Path:Name:Description:Value
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        IdentityToken:int = 0
    ----------
    Response:
        IsLastDatum:int
        DatumCode:int
        PathNameDescrValue:str
    ----------
    Command Timeout: 10000
    Example:BnR_GetNextDatum 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetNextDatum",ControllerID,IdentityToken)
    global BnR_GetNextDatum_Response
    if not "BnR_GetNextDatum_Response" in globals(): BnR_GetNextDatum_Response = namedtuple("BnR_GetNextDatum_Response", "IsLastDatum,DatumCode,PathNameDescrValue")
    return BnR_GetNextDatum_Response(int(rsp[0]),int(rsp[1]),str("" if len(rsp) < 3 else ' '.join(rsp[2:])))

def BnR_SetDatum(ControllerID="", PathNameAndValue=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the value of a parameter. An empty parameter string saves the whole
    configuration to non-volatile memory. Fields are separated by a colon.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        PathNameAndValue:str = ""
    ----------
    Command Timeout: 20000
    Example:BnR_SetDatum 1 Chuck_XAxisData:CurrentMaximal:70
    """
    MessageServerInterface.sendSciCommand("BnR_SetDatum",ControllerID,PathNameAndValue)


def BnR_GetDatum(ControllerID="", PathName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns a value string. The Value string consists of the value and the
    description. The Locator only consists of the path and the name. All fields are
    separated by a colon.  Structure of the command parameter Locator:
    Path_Path:Name Structure of the response parameter Value: Value:Description
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        PathName:str = ""
    ----------
    Response:
        DatumCode:int
        ValueDesc:str
    ----------
    Command Timeout: 5000
    Example:BnR_GetDatum 1 Chuck_XAxisData:CurrentMaximal
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetDatum",ControllerID,PathName)
    global BnR_GetDatum_Response
    if not "BnR_GetDatum_Response" in globals(): BnR_GetDatum_Response = namedtuple("BnR_GetDatum_Response", "DatumCode,ValueDesc")
    return BnR_GetDatum_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def BnR_GetPosition(ControllerID="", Stage="", Unit=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the current positions for the X,Y,Z (or T) axis for the specified stage
    as well as the commanded positions.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        Unit:str = "Microns"
    ----------
    Response:
        XorT:Decimal
        Y:Decimal
        Z:Decimal
        CommandedXorT:Decimal
        CommandedY:Decimal
        CommandedZ:Decimal
    ----------
    Command Timeout: 5000
    Example:BnR_GetPosition 1 C
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetPosition",ControllerID,Stage,Unit)
    global BnR_GetPosition_Response
    if not "BnR_GetPosition_Response" in globals(): BnR_GetPosition_Response = namedtuple("BnR_GetPosition_Response", "XorT,Y,Z,CommandedXorT,CommandedY,CommandedZ")
    return BnR_GetPosition_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),Decimal(rsp[5]))

def BnR_Move(ControllerID="", Stage="", XValue="", YValue="", VelX="", VelY="", WaitFinished="", TargetIsFence=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command executes a XY movement for a specified stage. This can be either a
    blocking or non blocking move.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        XValue:Decimal = 0
        YValue:Decimal = 0
        VelX:Decimal = 0
        VelY:Decimal = 0
        WaitFinished:int = 1
        TargetIsFence:int = 1
    ----------
    Response:
        X:Decimal
        Y:Decimal
    ----------
    Command Timeout: 60000
    Example:BnR_Move 1 C 5000 5000 100 100 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_Move",ControllerID,Stage,XValue,YValue,VelX,VelY,WaitFinished,TargetIsFence)
    global BnR_Move_Response
    if not "BnR_Move_Response" in globals(): BnR_Move_Response = namedtuple("BnR_Move_Response", "X,Y")
    return BnR_Move_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def BnR_MoveZ(ControllerID="", Stage="", ZValue="", Vel="", Dec="", WaitFinished=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the stage Z axis to a new position.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        ZValue:Decimal = 0
        Vel:Decimal = 0
        Dec:Decimal = 0
        WaitFinished:int = 1
    ----------
    Response:
        Z:Decimal
    ----------
    Command Timeout: 600000
    Example:BnR_MoveZ 1 C 12000 100 100 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_MoveZ",ControllerID,Stage,ZValue,Vel,Dec,WaitFinished)
    return Decimal(rsp[0])

def BnR_ScanMoveZ(ControllerID="", Stage="", ZDistance="", TriggerEveryNthCycle="", Vel=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command executes a scan movement of the Z axis that sets a digital output
    every couple microns to trigger e.g. a camera. After the move is finished, the
    command returns a list of Z heights at which the digital output was set.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        ZDistance:Decimal = 1000
        TriggerEveryNthCycle:int = 2
        Vel:Decimal = 10
    ----------
    Command Timeout: 300000
    Example:BnR_ScanMoveZ 1 C 1000 6 10
    """
    MessageServerInterface.sendSciCommand("BnR_ScanMoveZ",ControllerID,Stage,ZDistance,TriggerEveryNthCycle,Vel)


def BnR_MoveT(ControllerID="", TValue="", Vel="", WaitFinished=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Executes a movement of the theta axis, either blocking or non blocking
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        TValue:Decimal = 0
        Vel:Decimal = 0
        WaitFinished:int = 1
    ----------
    Response:
        T:Decimal
    ----------
    Command Timeout: 60000
    Example:BnR_MoveT 1 1.003 10 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_MoveT",ControllerID,TValue,Vel,WaitFinished)
    return Decimal(rsp[0])

def BnR_StopAxis(ControllerID="", Stage="", FlagsStop=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Stops 1... all axes of a stage
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        FlagsStop:int = 15
    ----------
    Command Timeout: 5000
    Example:BnR_StopAxis 1 C 7
    """
    MessageServerInterface.sendSciCommand("BnR_StopAxis",ControllerID,Stage,FlagsStop)


def BnR_InitAxis(ControllerID="", Stage="", FlagsInit="", FlagsDirection="", FlagsInitInPlace="", LowOrHighLimitX="", LowOrHighLimitY="", LowOrHighLimitZ="", LowOrHighLimitTh="", InitInPlaceMoveRangeX="", InitInPlaceMoveRangeY="", InitInPlaceMoveRangeZ="", InitInPlaceMoveRangeTh=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Machine Coordinate System: X Y Z Theta  - _FlagsInit_: X, Y, Z, Theta -
    _FlagsDirection_: X, Y, Z, Theta (true means plus direction) -
    _FlagsInitInPlace_: X, Y, Z, Theta   All flags can be accessed by indirect
    members. Initializes the stage and resets current coordinate system. Should be
    used only in cases when the reported coordinates do not correspond to real
    position of mechanics. Init in Place performs the initialization without any
    movements.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        FlagsInit:int = 0
        FlagsDirection:int = 0
        FlagsInitInPlace:int = 0
        LowOrHighLimitX:Decimal = 0
        LowOrHighLimitY:Decimal = 0
        LowOrHighLimitZ:Decimal = 0
        LowOrHighLimitTh:Decimal = 0
        InitInPlaceMoveRangeX:Decimal = 0
        InitInPlaceMoveRangeY:Decimal = 0
        InitInPlaceMoveRangeZ:Decimal = 0
        InitInPlaceMoveRangeTh:Decimal = 0
    ----------
    Command Timeout: 300000
    Example:BnR_InitAxis 1 C 7
    """
    MessageServerInterface.sendSciCommand("BnR_InitAxis",ControllerID,Stage,FlagsInit,FlagsDirection,FlagsInitInPlace,LowOrHighLimitX,LowOrHighLimitY,LowOrHighLimitZ,LowOrHighLimitTh,InitInPlaceMoveRangeX,InitInPlaceMoveRangeY,InitInPlaceMoveRangeZ,InitInPlaceMoveRangeTh)


def BnR_GetAxisState(ControllerID="", Stage="", Axis=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command returns the state of an axis (disabled/standstill/errorstop/stoppin
    g/homing/continuousmotion/discretemotion/synchronizedmotion)
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        Axis:str = "XAxis"
    ----------
    Response:
        State:str
        AdditionalStateInfo:str
    ----------
    Command Timeout: 5000
    Example:BnR_GetAxisState 1 C X
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetAxisState",ControllerID,Stage,Axis)
    global BnR_GetAxisState_Response
    if not "BnR_GetAxisState_Response" in globals(): BnR_GetAxisState_Response = namedtuple("BnR_GetAxisState_Response", "State,AdditionalStateInfo")
    return BnR_GetAxisState_Response(str(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def BnR_GetAxisStatus(ControllerID="", Stage="", Axis=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command returns some axis status information
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        Axis:str = "XAxis"
    ----------
    Response:
        Initialized:int
        PositiveEndlimit:int
        NegativeEndlimit:int
    ----------
    Command Timeout: 5000
    Example:BnR_GetAxisStatus 1 C X
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetAxisStatus",ControllerID,Stage,Axis)
    global BnR_GetAxisStatus_Response
    if not "BnR_GetAxisStatus_Response" in globals(): BnR_GetAxisStatus_Response = namedtuple("BnR_GetAxisStatus_Response", "Initialized,PositiveEndlimit,NegativeEndlimit")
    return BnR_GetAxisStatus_Response(int(rsp[0]),int(rsp[1]),int(rsp[2]))

def BnR_SetQuietMode(ControllerID="", Stage="", QuietMode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command to enable the quiet mode for a stage (quiet turns motors powerless)
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        QuietMode:int = 0
    ----------
    Command Timeout: 5000
    Example:BnR_SetQuietMode 1 C 1
    """
    MessageServerInterface.sendSciCommand("BnR_SetQuietMode",ControllerID,Stage,QuietMode)


def BnR_GetQuietMode(ControllerID="", Stage=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command to query the quiet mode for a stage
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
    ----------
    Response:
        QuietMode:int
    ----------
    Command Timeout: 5000
    Example:BnR_GetQuietMode 1 C
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetQuietMode",ControllerID,Stage)
    return int(rsp[0])

def BnR_GetInternalAxisInfo(ControllerID="", Stage="", Axis="", InfoType=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command returns various axis information, dependent on the InfoType
    parameter
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        Axis:str = "XAxis"
        InfoType:str = "StallInfo"
    ----------
    Response:
        RspString:str
    ----------
    Command Timeout: 5000
    Example:BnR_GetInternalAxisInfo 1 C X
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_GetInternalAxisInfo",ControllerID,Stage,Axis,InfoType)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def BnR_MoveAxis(ControllerID="", Stage="", Axis="", Value="", Vel="", Dec="", WaitFinished=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command allows moving a single axis to and e.g. in case of X does not
    trigger a Y movement
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        Axis:str = "XAxis"
        Value:Decimal = 0
        Vel:Decimal = 0
        Dec:Decimal = 0
        WaitFinished:int = 1
    ----------
    Response:
        PositionAfterMove:Decimal
    ----------
    Command Timeout: 60000
    Example:BnR_MoveAxis 1 C X 20000 100 100 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_MoveAxis",ControllerID,Stage,Axis,Value,Vel,Dec,WaitFinished)
    return Decimal(rsp[0])

def BnR_MoveZCombined(ControllerID="", ChuckTargetZ="", WaitFinished="", ForcedAbsVelocity=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Move Chuck-Z and (by fixed factor) Scope X, Y and Z
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        ChuckTargetZ:Decimal = 0
        WaitFinished:int = 1
        ForcedAbsVelocity:int = 0
    ----------
    Response:
        ChuckZ:Decimal
        ScopeX:Decimal
        ScopeY:Decimal
        ScopeZ:Decimal
    ----------
    Command Timeout: 600000
    Example:BnR_MoveZCombined 1 17592.5 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_MoveZCombined",ControllerID,ChuckTargetZ,WaitFinished,ForcedAbsVelocity)
    global BnR_MoveZCombined_Response
    if not "BnR_MoveZCombined_Response" in globals(): BnR_MoveZCombined_Response = namedtuple("BnR_MoveZCombined_Response", "ChuckZ,ScopeX,ScopeY,ScopeZ")
    return BnR_MoveZCombined_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]))

def BnR_SyncMove(ControllerID="", Stage="", XValue="", YValue="", Vel="", WaitFinished=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command executes a XY movement for a specified stage. This can be either a
    blocking or non blocking move.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        Stage:str = "Chuck"
        XValue:Decimal = 0
        YValue:Decimal = 0
        Vel:Decimal = 0
        WaitFinished:int = 1
    ----------
    Response:
        X:Decimal
        Y:Decimal
    ----------
    Command Timeout: 60000
    Example:BnR_SyncMove 1 C 5000 5000 100 1
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_SyncMove",ControllerID,Stage,XValue,YValue,Vel,WaitFinished)
    global BnR_SyncMove_Response
    if not "BnR_SyncMove_Response" in globals(): BnR_SyncMove_Response = namedtuple("BnR_SyncMove_Response", "X,Y")
    return BnR_SyncMove_Response(Decimal(rsp[0]),Decimal(rsp[1]))

def BnR_SearchEdgeSensor(ControllerID="", SearchEndPos="", Velocity=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Performs a search move until the search end position is reached or the edge
    sensor triggers. If the edge sensor triggers during the move, the trigger
    position is returned.Otherwise, an edge sensor not found error is returned.
    Status: internal
    ----------
    Parameters:
        ControllerID:int = 1
        SearchEndPos:Decimal = 0
        Velocity:Decimal = 0
    ----------
    Response:
        EdgeSensorTriggerPos:Decimal
    ----------
    Command Timeout: 300000
    Example:BnR_SearchEdgeSensor 1 42000 5
    """
    rsp = MessageServerInterface.sendSciCommand("BnR_SearchEdgeSensor",ControllerID,SearchEndPos,Velocity)
    return Decimal(rsp[0])

def ProcessStationGetStatus():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns process station status (UNKNOWN, IDLE, BUSY, ERROR, PAUSED, Not
    Initialized) and error code with error message when error.
    Status: internal
    ----------
    Response:
        Status:str
        SubstratePresent:int
        LastError:int
        UseLoaderModule:int
        WaferSizes:str
        StatusMessage:str
        IsLoaderJobRunning:int
    ----------
    Command Timeout: 25000
    Example:ProcessStationGetStatus
    """
    rsp = MessageServerInterface.sendSciCommand("ProcessStationGetStatus")
    global ProcessStationGetStatus_Response
    if not "ProcessStationGetStatus_Response" in globals(): ProcessStationGetStatus_Response = namedtuple("ProcessStationGetStatus_Response", "Status,SubstratePresent,LastError,UseLoaderModule,WaferSizes,StatusMessage,IsLoaderJobRunning")
    return ProcessStationGetStatus_Response(str(rsp[0]),int(rsp[1]),int(rsp[2]),int(rsp[3]),str(rsp[4]),str(rsp[5]),int(rsp[6]))

def ProcessStationInit():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Initialize process station machine. This is not the Probe Station init it is a
    fast program initialization. Only applies to fully auto systems.
    Status: internal
    ----------
    Command Timeout: 2400000
    Example:ProcessStationInit
    """
    MessageServerInterface.sendSciCommand("ProcessStationInit")


def ProcessStationFinish():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Finishes a process station process. This resets some internal test information
    for the Probe Station. Some data is only reset in case this command is sent
    after the last wafer in the job was tested. Only applies to fully auto systems.
    Status: internal
    ----------
    Command Timeout: 7500000
    Example:ProcessStationFinish
    """
    MessageServerInterface.sendSciCommand("ProcessStationFinish")


def ProcessStationPrepareForLoad():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Command moves the Chuck of the Probe Station to the secondary load position and
    if available also checks the table level sensor. Only applies to fully auto
    systems.
    Status: internal
    ----------
    Command Timeout: 120000
    Example:ProcessStationPrepareForLoad
    """
    MessageServerInterface.sendSciCommand("ProcessStationPrepareForLoad")


def ProcessStationLoadComplete():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Moves the Chuck out of the load position and checks if a wafer is placed. Only
    applies to fully auto systems.
    Status: internal
    ----------
    Command Timeout: 60000
    Example:ProcessStationLoadComplete
    """
    MessageServerInterface.sendSciCommand("ProcessStationLoadComplete")


def ProcessStationPrepareForUnLoad():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    The module should do whatever is necessary to prepare the current wafer for
    unload. Typically this includes things such as moving lift pins and opening
    doors.
    Status: internal
    ----------
    Command Timeout: 1200000
    Example:ProcessStationPrepareForUnLoad
    """
    MessageServerInterface.sendSciCommand("ProcessStationPrepareForUnLoad")


def ProcessStationUnLoadComplete():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    The module should so whatever is necessary after a wafer is unloaded. This may
    for example include closing doors.
    Status: internal
    ----------
    Command Timeout: 60000
    Example:ProcessStationUnLoadComplete
    """
    MessageServerInterface.sendSciCommand("ProcessStationUnLoadComplete")


def ProcessStationLoadRecipe(ForceReOpenProject="", ProjectFileName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    The recipe is a zipped archive that includes all project data. This command
    tells the device to load the recipe.
    Status: internal
    ----------
    Parameters:
        ForceReOpenProject:int = 0
        ProjectFileName:str = ""
    ----------
    Command Timeout: 60000
    Example:ProcessStationLoadRecipe 1 SampleProject.spp
    """
    MessageServerInterface.sendSciCommand("ProcessStationLoadRecipe",ForceReOpenProject,ProjectFileName)


def ProcessStationVerifyRecipe(ProjectFileName=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Requests that the device verify that the recipe given can be executed on the
    device. It should check that the recipe is correctly formed and conforms to the
    hardware of the device. It should not check for transient things such as whether
    there is sufficient media or facilities available. those kinds of checks should
    be done in PrepareForProcess
    Status: internal
    ----------
    Parameters:
        ProjectFileName:str = ""
    ----------
    Response:
        Verified:int
        ErrorDescription:str
    ----------
    Command Timeout: 60000
    Example:ProcessStationVerifyRecipe SampleProject.spp
    """
    rsp = MessageServerInterface.sendSciCommand("ProcessStationVerifyRecipe",ProjectFileName)
    global ProcessStationVerifyRecipe_Response
    if not "ProcessStationVerifyRecipe_Response" in globals(): ProcessStationVerifyRecipe_Response = namedtuple("ProcessStationVerifyRecipe_Response", "Verified,ErrorDescription")
    return ProcessStationVerifyRecipe_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def ProcessStationStartRecipe(CurrentWaferInJob="", TotalWafersInJob=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Tells VeloxPro to start the current recipe. The station will switch to error if
    an error occurs. If VeloxPro recipe execution is currently paused, this command
    tells the system to continue execution.
    Status: internal
    ----------
    Parameters:
        CurrentWaferInJob:int = -1
        TotalWafersInJob:int = -1
    ----------
    Command Timeout: 25000
    Example:ProcessStationStartRecipe 1
    """
    MessageServerInterface.sendSciCommand("ProcessStationStartRecipe",CurrentWaferInJob,TotalWafersInJob)


def ProcessStationStopRecipe():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Tells the device to stop the current recipe. The station will switch to error if
    an error occurs.
    Status: internal
    ----------
    Command Timeout: 25000
    Example:ProcessStationStopRecipe
    """
    MessageServerInterface.sendSciCommand("ProcessStationStopRecipe")


def ProcessStationRecoverError():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Tells the module to do whatever is necessary to recover from an error condition.
    Status: internal
    ----------
    Command Timeout: 60000
    Example:ProcessStationRecoverError
    """
    MessageServerInterface.sendSciCommand("ProcessStationRecoverError")


def ProcessStationGetWaferResult():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Get substrate information from process station controller application.
    Status: internal
    ----------
    Response:
        Result:str
        PercentDone:Decimal
        AllowSkipWafer:int
        TestInformation:str
    ----------
    Command Timeout: 25000
    Example:ProcessStationGetWaferResult
    """
    rsp = MessageServerInterface.sendSciCommand("ProcessStationGetWaferResult")
    global ProcessStationGetWaferResult_Response
    if not "ProcessStationGetWaferResult_Response" in globals(): ProcessStationGetWaferResult_Response = namedtuple("ProcessStationGetWaferResult_Response", "Result,PercentDone,AllowSkipWafer,TestInformation")
    return ProcessStationGetWaferResult_Response(str(rsp[0]),Decimal(rsp[1]),int(rsp[2]),str("" if len(rsp) < 4 else ' '.join(rsp[3:])))

def QueryWaferInfo():
    """
    Returns information about the wafer that is currently on the Probe Station. It
    will return an error when there is no wafer currently on the Chuck.
    Status: published
    ----------
    Response:
        Size:int
        Angle:Decimal
        ID:str
        LotID:str
        ProductID:str
    ----------
    Command Timeout: 25000
    Example:QueryWaferInfo
    """
    rsp = MessageServerInterface.sendSciCommand("QueryWaferInfo")
    global QueryWaferInfo_Response
    if not "QueryWaferInfo_Response" in globals(): QueryWaferInfo_Response = namedtuple("QueryWaferInfo_Response", "Size,Angle,ID,LotID,ProductID")
    return QueryWaferInfo_Response(int(rsp[0]),Decimal(rsp[1]),str(rsp[2]),str(rsp[3]),str("" if len(rsp) < 5 else ' '.join(rsp[4:])))

def ProcessStationPauseRecipe():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the process station to PAUSE mode
    Status: internal
    ----------
    Command Timeout: 25000
    Example:ProcessStationPauseRecipe
    """
    MessageServerInterface.sendSciCommand("ProcessStationPauseRecipe")


def GetProbingStatus():
    """
    Retrieves the current status of the Probe Station. If probing status is
    AtFirstDie the tester can take control.
    Status: published
    ----------
    Response:
        Status:str
    ----------
    Command Timeout: 25000
    Example:GetProbingStatus
    """
    rsp = MessageServerInterface.sendSciCommand("GetProbingStatus")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ProceedProbing():
    """
    Tells the Probe Station to proceed the recipe when current status is AtFirstDie.
    Status: published
    ----------
    Command Timeout: 25000
    Example:ProceedProbing
    """
    MessageServerInterface.sendSciCommand("ProceedProbing")


def GetCassetteStatus(Cassette=""):
    """
    Provides all available wafer information. It returns a set of data for each
    wafer in either cassette. The data contains the cassette and the slot number
    where the wafer is located, the status of the wafer and identification
    information.
    Status: published
    ----------
    Parameters:
        Cassette:int = 0
    ----------
    Response:
        CassetteStatus:str
    ----------
    Command Timeout: 25000
    Example:GetCassetteStatus 0
    """
    rsp = MessageServerInterface.sendSciCommand("GetCassetteStatus",Cassette)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def QueryWaferID(Module="", Slot=""):
    """
    Queries the wafer ID of a given module and slot.
    Status: published
    ----------
    Parameters:
        Module:str = "Robot"
        Slot:int = 0
    ----------
    Response:
        ID:str
    ----------
    Command Timeout: 25000
    Example:QueryWaferID Cassette1 1
    """
    rsp = MessageServerInterface.sendSciCommand("QueryWaferID",Module,Slot)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def UpdateWaferID(Module="", Slot="", ID=""):
    """
    Overrides the wafer ID of the given module and slot. If the wafer id is empty
    and the module is a Loadport, the id will be read by the idreader if possible.
    This process behaves as follows:  - the current wafer id is reset - if the read-
    wafer-process would be delayed (e.g. there is already a   wafer on the idreader)
    the process will be aborted and an error         will be returned - if the id-
    reading fails, the process behaves like a normal inventory  triggered by the UI:
    skip (returns success), abort (returns error)      or "ask user". It is
    recommended to use either skip or abort for        remote id reading.  If the
    module is a Loadport and the slot is set to -1, a regular inventory will be
    triggered. This behaves similar to an inventory triggered by the UI: The ID
    won't be reset and already scanned wafers won't be reset. Setting an ID
    explicitly with slot -1 is an error:  - Okay, read id of wafer in slot 3 even if
    it is already set: UpdateWaferID Cassette1 3 - Okay, set id of wafer in slot 3
    to XYZ123: UpdateWaferID Cassette1 3 XYZ123 - Okay, start full inventory:
    UpdateWaferID Cassette1 -1  - Error: UpdateWaferID Cassette1 -1 XYZ123
    Status: published
    ----------
    Parameters:
        Module:str = "Robot"
        Slot:int = 0
        ID:str = ""
    ----------
    Command Timeout: 1500000
    Example:UpdateWaferID Cassette1 1 Wafer01
    """
    MessageServerInterface.sendSciCommand("UpdateWaferID",Module,Slot,ID)


def ConfirmRecipe(ProjectFileName=""):
    """
    Queries whether the given project/flow name is a valid project/flow at the Probe
    Station.  Using file and folder names without white spaces is recommended. For
    folders and files with white spaces use quotation marks for the path.  Example
    for using white spaces:  ConfirmRecipe
    "C:/Users/Public/Documents/Velox/Projects/White Spaces.spp"
    Status: published
    ----------
    Parameters:
        ProjectFileName:str = ""
    ----------
    Response:
        Verified:int
        ErrorDescription:str
    ----------
    Command Timeout: 25000
    Example:ConfirmRecipe C:/Temp/Test.spp
    """
    rsp = MessageServerInterface.sendSciCommand("ConfirmRecipe",ProjectFileName)
    global ConfirmRecipe_Response
    if not "ConfirmRecipe_Response" in globals(): ConfirmRecipe_Response = namedtuple("ConfirmRecipe_Response", "Verified,ErrorDescription")
    return ConfirmRecipe_Response(int(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def StartWaferJob(RecipeName="", WaferIDs=""):
    """
    Creates and starts a new job by specifying the flow/spp file and the wafers to
    be included in the job.
    Status: published
    ----------
    Parameters:
        RecipeName:str = ""
        WaferIDs:str = ""
    ----------
    Response:
        JobID:str
    ----------
    Command Timeout: 25000
    Example:StartWaferJob C:/Users/Public/Documents/Velox/Test.flow 1;1 2;1
    """
    rsp = MessageServerInterface.sendSciCommand("StartWaferJob",RecipeName,WaferIDs)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def GetJobParams(JobID=""):
    """
    Get job information for a specific job ID including the flow file and the list
    of wafers.
    Status: published
    ----------
    Parameters:
        JobID:str = ""
    ----------
    Response:
        RecipeName:str
        WaferIDs:str
    ----------
    Command Timeout: 25000
    Example:GetJobParams 1
    """
    rsp = MessageServerInterface.sendSciCommand("GetJobParams",JobID)
    global GetJobParams_Response
    if not "GetJobParams_Response" in globals(): GetJobParams_Response = namedtuple("GetJobParams_Response", "RecipeName,WaferIDs")
    return GetJobParams_Response(str(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def JobStatus(JobID=""):
    """
    Retrieves the status of a specific job by its ID. If the status is ErrorWaiting,
    an error string is returned.
    Status: published
    ----------
    Parameters:
        JobID:str = ""
    ----------
    Response:
        Status:str
        JobStatusInfo:str
    ----------
    Command Timeout: 25000
    Example:JobStatus 1
    """
    rsp = MessageServerInterface.sendSciCommand("JobStatus",JobID)
    global JobStatus_Response
    if not "JobStatus_Response" in globals(): JobStatus_Response = namedtuple("JobStatus_Response", "Status,JobStatusInfo")
    return JobStatus_Response(str(rsp[0]),str("" if len(rsp) < 2 else ' '.join(rsp[1:])))

def AbortJob(JobID="", Unload=""):
    """
    Aborts the job given by the job ID. The status of the job will be set to
    "Aborted". The "Unload" parameter defines whether the wafer remains on the Chuck
    or not. If no JobID is specified (or is set to -1), the currently running
    probing job will be aborted.
    Status: published
    ----------
    Parameters:
        JobID:str = ""
        Unload:int = 0
    ----------
    Command Timeout: 25000
    Example:AbortJob 2 1
    """
    MessageServerInterface.sendSciCommand("AbortJob",JobID,Unload)


def ProcessStationCloseApplication(NoUserPrompt=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Closes the VeloxPro application.
    Status: internal
    ----------
    Parameters:
        NoUserPrompt:int = 0
    ----------
    Command Timeout: 25000
    Example:ProcessStationCloseApplication
    """
    MessageServerInterface.sendSciCommand("ProcessStationCloseApplication",NoUserPrompt)


def UnloadWafer():
    """
    Unloads a Wafer from the Chuck to its origin. If no origin is known, the first
    free Slot of a loadport will be chosen. A Wafer should be on the Chuck.
    Status: published
    ----------
    Command Timeout: 1800000
    Example:UnloadWafer
    """
    MessageServerInterface.sendSciCommand("UnloadWafer")


def GetJobList(JobType=""):
    """
    Returns a string for the relevant JobIDs.
    Status: published
    ----------
    Parameters:
        JobType:str = "Probing"
    ----------
    Response:
        GetJobList:str
    ----------
    Command Timeout: 25000
    Example:GetJobList
    """
    rsp = MessageServerInterface.sendSciCommand("GetJobList",JobType)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ProceedJob(ProceedJob=""):
    """
    Continues a job that is waiting on an error (Job Status ErrorWaiting). The mode
    determines how the job continues.
    Status: published
    ----------
    Parameters:
        ProceedJob:str = "AbortJob"
    ----------
    Command Timeout: 25000
    Example:ProceedJob A
    """
    MessageServerInterface.sendSciCommand("ProceedJob",ProceedJob)


def QueryCassetteID(Cassette=""):
    """
    Returns the ID of a cassette that is placed on the load port. The loadport and
    the cassette must support RFID reading (additional hardware needed).
    Status: published
    ----------
    Parameters:
        Cassette:int = 1
    ----------
    Response:
        ID:str
    ----------
    Command Timeout: 25000
    Example:QueryCassetteID 1
    """
    rsp = MessageServerInterface.sendSciCommand("QueryCassetteID",Cassette)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def DockCassette(LoadPortId="", DockUndock=""):
    """
    Docks or undocks a cassette which is placed on a LoadPort (CM300 only). It will
    return an error if no cassette is placed: the LoadPort is not ready/available or
    the docking failed. The command will do the docking/undocking and return when
    this is done.
    Status: published
    ----------
    Parameters:
        LoadPortId:int = 0
        DockUndock:int = 0
    ----------
    Command Timeout: 60000
    Example:DockCassette 1 1
    """
    MessageServerInterface.sendSciCommand("DockCassette",LoadPortId,DockUndock)


def LoadWafer(LoadportID="", SlotID="", AlignmentAngle=""):
    """
    Load a wafer from a given loadport onto the prober. If no slot id is defined,
    the first available wafer with the lowest slot id will be loaded. If no loadport
    is defined, it will try to use the first loadport. If there is no suitable
    wafer, it will try the second.  Returns an error if the loading process fails or
    no suitable wafer is found.  To define an alignment angle and still use the
    "autoselect" behavior, use -1 for loadport and slot.
    Status: published
    ----------
    Parameters:
        LoadportID:int = -1
        SlotID:int = -1
        AlignmentAngle:Decimal = 0
    ----------
    Command Timeout: 600000
    Example:LoadWafer 1 1
    """
    MessageServerInterface.sendSciCommand("LoadWafer",LoadportID,SlotID,AlignmentAngle)


def UpdateCassetteStatus(Cassette=""):
    """
    Updates the cassette status with a simple scan.
    Status: published
    ----------
    Parameters:
        Cassette:int = 0
    ----------
    Response:
        CassetteStatus:str
    ----------
    Command Timeout: 1200000
    Example:UpdateCassetteStatus 1
    """
    rsp = MessageServerInterface.sendSciCommand("UpdateCassetteStatus",Cassette)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def TransportWafer(SourceLocation="", SourceSlot="", DestinationLocation="", DestinationSlot=""):
    """
    Transport a wafer from one location to another. This command behaves like the
    wafer-transport inside the LoaderModule. The Slot must always be set.
    Status: published
    ----------
    Parameters:
        SourceLocation:str = "Cassette1"
        SourceSlot:int = 1
        DestinationLocation:str = "Cassette1"
        DestinationSlot:int = 1
    ----------
    Command Timeout: 600000
    Example:TransportWafer Cassette1 1 PreAligner 1
    """
    MessageServerInterface.sendSciCommand("TransportWafer",SourceLocation,SourceSlot,DestinationLocation,DestinationSlot)


def ProcessWafer(Module="", ProcessParam=""):
    """
    "Process" a wafer on a given location. What is done depends on the current
    station:  - IDReader: read ID - PreAligner: align wafer (alignment angle
    mandatory) - Prober: Perform current recipe
    Status: published
    ----------
    Parameters:
        Module:str = "Cassette1"
        ProcessParam:str = ""
    ----------
    Command Timeout: 100000
    Example:ProcessWafer PreAligner 90.0
    """
    MessageServerInterface.sendSciCommand("ProcessWafer",Module,ProcessParam)


def GetIDReaderPos():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the current position of the IDReader
    Status: internal
    ----------
    Response:
        IDReaderPos:str
    ----------
    Command Timeout: 2000
    """
    rsp = MessageServerInterface.sendSciCommand("GetIDReaderPos")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetIDReaderPos(IDReaderPos=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Set the current position of the IDReader
    Status: internal
    ----------
    Parameters:
        IDReaderPos:str = "Bottom"
    ----------
    Command Timeout: 10000
    """
    MessageServerInterface.sendSciCommand("SetIDReaderPos",IDReaderPos)


def CryoCommand(Process=""):
    """
    CryoCommand controls automatic cooling and warm up.
    Status: published
    ----------
    Parameters:
        Process:str = "CD"
    ----------
    Command Timeout: 60000
    Example:CryoCommand CD
    """
    MessageServerInterface.sendSciCommand("CryoCommand",Process)


def CryoReadTemperature(Stage=""):
    """
    Reads the current temperature from sensor Chuck or Shield.
    Status: published
    ----------
    Parameters:
        Stage:str = "C"
    ----------
    Response:
        Temp:Decimal
    ----------
    Command Timeout: 10000
    Example:CryoReadTemperature C
    """
    rsp = MessageServerInterface.sendSciCommand("CryoReadTemperature",Stage)
    return Decimal(rsp[0])

def CryoSetTemperature(Stage="", Temp=""):
    """
    Sets temperature value for TIC Chuck or Shield. (Only available in process state
    'Idle' or 'Cold'.)
    Status: published
    ----------
    Parameters:
        Stage:str = "C"
        Temp:Decimal = 320
    ----------
    Command Timeout: 10000
    Example:CryoSetTemperature C 70.5
    """
    MessageServerInterface.sendSciCommand("CryoSetTemperature",Stage,Temp)


def CryoStartRefill(Stage=""):
    """
    Enables refill. (Only available in process state 'Idle'.)
    Status: published
    ----------
    Parameters:
        Stage:str = "C"
    ----------
    Command Timeout: 10000
    Example:CryoStartRefill C
    """
    MessageServerInterface.sendSciCommand("CryoStartRefill",Stage)


def CryoStopRefill(Stage=""):
    """
    Disables refill. (Only available in process state 'Idle'.)
    Status: published
    ----------
    Parameters:
        Stage:str = "C"
    ----------
    Command Timeout: 10000
    Example:CryoStopRefill C
    """
    MessageServerInterface.sendSciCommand("CryoStopRefill",Stage)


def CryoReadState():
    """
    Reads current state.
    Status: published
    ----------
    Response:
        State:str
    ----------
    Command Timeout: 10000
    """
    rsp = MessageServerInterface.sendSciCommand("CryoReadState")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def CryoMoveBBPark():
    """
    Moves the black body to parking position.
    Status: published
    ----------
    Command Timeout: 60000
    """
    MessageServerInterface.sendSciCommand("CryoMoveBBPark")


def CryoMoveBBWork(NbrPosition=""):
    """
    Moves the black body to working position.
    Status: published
    ----------
    Parameters:
        NbrPosition:int = 1
    ----------
    Command Timeout: 60000
    Example:CryoMoveBBWork 1
    """
    MessageServerInterface.sendSciCommand("CryoMoveBBWork",NbrPosition)


def CryoMoveShutter(Position="", Shutter=""):
    """
    Moves one of the two shutters.
    Status: published
    ----------
    Parameters:
        Position:str = "C"
        Shutter:int = 1
    ----------
    Command Timeout: 60000
    Example:CryoMoveShutter F 1
    """
    MessageServerInterface.sendSciCommand("CryoMoveShutter",Position,Shutter)


def CryoMoveScopeWork():
    """
    Moves the microscope to working position.
    Status: published
    ----------
    Command Timeout: 60000
    """
    MessageServerInterface.sendSciCommand("CryoMoveScopeWork")


def CryoMoveScopePark():
    """
    Moves the microscope to parking position.
    Status: published
    ----------
    Command Timeout: 60000
    """
    MessageServerInterface.sendSciCommand("CryoMoveScopePark")


def CryoReadPressure():
    """
    Reads the current pressure of the vacuum chamber.
    Status: published
    ----------
    Response:
        Pressure:Decimal
    ----------
    Command Timeout: 60000
    """
    rsp = MessageServerInterface.sendSciCommand("CryoReadPressure")
    return Decimal(rsp[0])

def CryoReadFillLevel(Stage="", Unit=""):
    """
    Reads the current fill level from Chuck or Shield dewar bottle in liter or
    percent.
    Status: published
    ----------
    Parameters:
        Stage:str = "C"
        Unit:str = "L"
    ----------
    Response:
        FillLevel:Decimal
    ----------
    Command Timeout: 10000
    Example:CryoReadFillLevel C L
    """
    rsp = MessageServerInterface.sendSciCommand("CryoReadFillLevel",Stage,Unit)
    return Decimal(rsp[0])

def GetAllCassetteRecipes():
    """
    Returns a list of all available cassette recipe names.
    Status: published
    ----------
    Response:
        GetAllCassetteRecipes:str
    ----------
    Command Timeout: 2000
    Example:GetAllCassetteRecipes
    """
    rsp = MessageServerInterface.sendSciCommand("GetAllCassetteRecipes")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def GetMTransSWLimits():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command gets the software limits for full range and top hat modes of the
    Elite microscope. Only applies to Elite station.
    Status: internal
    ----------
    Response:
        XPositiveFull:Decimal
        XNegativeFull:Decimal
        XPositveTopHat:Decimal
        XNegativeTopHat:Decimal
        YPositiveFull:Decimal
        YNegativeFull:Decimal
        YPositveTopHat:Decimal
        YNegativeTopHat:Decimal
    ----------
    Command Timeout: 10000
    Example:GetMTransSWLimits
    """
    rsp = MessageServerInterface.sendSciCommand("GetMTransSWLimits")
    global GetMTransSWLimits_Response
    if not "GetMTransSWLimits_Response" in globals(): GetMTransSWLimits_Response = namedtuple("GetMTransSWLimits_Response", "XPositiveFull,XNegativeFull,XPositveTopHat,XNegativeTopHat,YPositiveFull,YNegativeFull,YPositveTopHat,YNegativeTopHat")
    return GetMTransSWLimits_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),Decimal(rsp[5]),Decimal(rsp[6]),Decimal(rsp[7]))

def SetMTransSWLimits(XPositiveFull="", XNegativeFull="", XPositveTopHat="", XNegativeTopHat="", YPositiveFull="", YNegativeFull="", YPositveTopHat="", YNegativeTopHat=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command sets the software limits for full range and top hat modes of the
    Elite microscope. Only applies to Elite station.
    Status: internal
    ----------
    Parameters:
        XPositiveFull:Decimal = 38100
        XNegativeFull:Decimal = -38100
        XPositveTopHat:Decimal = 20000
        XNegativeTopHat:Decimal = -20000
        YPositiveFull:Decimal = 38100
        YNegativeFull:Decimal = -38100
        YPositveTopHat:Decimal = 20000
        YNegativeTopHat:Decimal = -20000
    ----------
    Command Timeout: 10000
    Example:SetMTransSWLimits
    """
    MessageServerInterface.sendSciCommand("SetMTransSWLimits",XPositiveFull,XNegativeFull,XPositveTopHat,XNegativeTopHat,YPositiveFull,YNegativeFull,YPositveTopHat,YNegativeTopHat)


def GetSoftwareStop():
    """
    Get the state of the software stop.
    Status: published
    ----------
    Response:
        StopState:int
    ----------
    Command Timeout: 1000
    """
    rsp = MessageServerInterface.sendSciCommand("GetSoftwareStop")
    return int(rsp[0])

def MoveZCombinedSetStatus(Status="", Message=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Used to set the system either in off, on, error or locked state.  For lock, a
    key is required. To unlock this key, doe a 'SetStatus' with the same key. So,
    SetStatus without message means enable/ recover from error, with message it
    means unlock. If the system wasn't enabled or in error state before an unlock,
    it will remain in this state after the unlock.
    Status: internal
    ----------
    Parameters:
        Status:str = "Off"
        Message:str = ""
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("MoveZCombinedSetStatus",Status,Message)


def GetTemperaturePresets():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the temperature presets.
    Status: internal
    ----------
    Response:
        Preset1:Decimal
        Preset2:Decimal
        Preset3:Decimal
        Preset4:Decimal
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("GetTemperaturePresets")
    global GetTemperaturePresets_Response
    if not "GetTemperaturePresets_Response" in globals(): GetTemperaturePresets_Response = namedtuple("GetTemperaturePresets_Response", "Preset1,Preset2,Preset3,Preset4")
    return GetTemperaturePresets_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]))

def GetScopeWorkingStage():
    """
    Get the currently active ScopeWorkingStage or -1 if unknown. Normally, this
    should be the same as the currently active ScopeSilo
    Status: published
    ----------
    Response:
        ScopeWorkingStage:int
    ----------
    Command Timeout: 5000
    Example:GetScopeWorkingStage
    """
    rsp = MessageServerInterface.sendSciCommand("GetScopeWorkingStage")
    return int(rsp[0])

def DisplayMessage(MessageToShow=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    This command displays a one-line message on the probe station screen. The
    message remains until you press Enter or click OK on the message box.
    Status: internal
    ----------
    Parameters:
        MessageToShow:str = ""
    ----------
    Command Timeout: 10000000
    """
    MessageServerInterface.sendSciCommand("DisplayMessage",MessageToShow)


def ShowSetupDialog(SetupDialogType="", Options=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Show Setup Dialog based on enum SetupDialogType(CleaningManager,
    AuxSiteWizard,...)
    Status: internal
    ----------
    Parameters:
        SetupDialogType:str = "CleaningManager"
        Options:str = ""
    ----------
    Command Timeout: 30000
    Example:ShowSetupDialog CleaningManager
    """
    MessageServerInterface.sendSciCommand("ShowSetupDialog",SetupDialogType,Options)


def GeteVueZoomPresets():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the eVue magnification preset values.
    Status: internal
    ----------
    Response:
        Preset1:Decimal
        Preset2:Decimal
        Preset3:Decimal
        Preset4:Decimal
        Preset5:Decimal
    ----------
    Command Timeout: 10000
    Example:GeteVueZoomPresets
    """
    rsp = MessageServerInterface.sendSciCommand("GeteVueZoomPresets")
    global GeteVueZoomPresets_Response
    if not "GeteVueZoomPresets_Response" in globals(): GeteVueZoomPresets_Response = namedtuple("GeteVueZoomPresets_Response", "Preset1,Preset2,Preset3,Preset4,Preset5")
    return GeteVueZoomPresets_Response(Decimal(rsp[0]),Decimal(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]))

def GetCassetteRecipe(Cassette=""):
    """
    Returns the cassette recipe name of the cassette station.
    Status: published
    ----------
    Parameters:
        Cassette:int = 1
    ----------
    Response:
        CassetteRecipe:str
    ----------
    Command Timeout: 2000
    Example:GetCassetteRecipe 1
    """
    rsp = MessageServerInterface.sendSciCommand("GetCassetteRecipe",Cassette)
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def ProbeStationVerify():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Verify probe station communications
    Status: internal
    ----------
    Response:
        VerifyMessage:str
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("ProbeStationVerify")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetPerformanceMode(Mode=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Set the performance mode in use by remote command. If this feature is not
    supported and the mode is anything but Standard, an error is returned.
    Status: internal
    ----------
    Parameters:
        Mode:str = "Standard"
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("SetPerformanceMode",Mode)


def SeteVueZoomPresets(Preset1="", Preset2="", Preset3="", Preset4="", Preset5=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the eVue magnification preset values.
    Status: internal
    ----------
    Parameters:
        Preset1:Decimal = 0.5
        Preset2:Decimal = 1
        Preset3:Decimal = 2
        Preset4:Decimal = 3
        Preset5:Decimal = 4
    ----------
    Command Timeout: 10000
    Example:SeteVueZoomPresets
    """
    MessageServerInterface.sendSciCommand("SeteVueZoomPresets",Preset1,Preset2,Preset3,Preset4,Preset5)


def GetSoakAtContactEnabled():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns whether or not soak at Contact is enabled.
    Status: internal
    ----------
    Response:
        Enabled:int
    ----------
    Command Timeout: 1000
    Example:GetSoakAtContactEnabled
    """
    rsp = MessageServerInterface.sendSciCommand("GetSoakAtContactEnabled")
    return int(rsp[0])

def SetScopeWorkingStage(ScopeWorkingStage=""):
    """
    Move to the target working stage
    Status: published
    ----------
    Parameters:
        ScopeWorkingStage:int = -1
    ----------
    Command Timeout: 30000
    Example:SetScopeWorkingStage 1
    """
    MessageServerInterface.sendSciCommand("SetScopeWorkingStage",ScopeWorkingStage)


def GetPerformanceMode():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Get the currently configured performance mode. If this feature is not supported
    on a station, Standard will be returned
    Status: internal
    ----------
    Response:
        Mode:str
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("GetPerformanceMode")
    return str("" if len(rsp) < 1 else ' '.join(rsp))

def SetCassetteRecipe(Cassette="", RecipeName=""):
    """
    Set the cassette recipe name of the cassette station.
    Status: published
    ----------
    Parameters:
        Cassette:int = 1
        RecipeName:str = ""
    ----------
    Command Timeout: 2000
    Example:SetCassetteRecipe 1 recipeName
    """
    MessageServerInterface.sendSciCommand("SetCassetteRecipe",Cassette,RecipeName)


def MoveZCombinedGetStatus():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Get the current status of the combined-z-move-system
    Status: internal
    ----------
    Response:
        Status:str
        PlatenSafe:int
        Height:Decimal
        HeightMax:Decimal
        HeightRelative:Decimal
        SafeHeight:Decimal
        Message:str
    ----------
    Command Timeout: 5000
    """
    rsp = MessageServerInterface.sendSciCommand("MoveZCombinedGetStatus")
    global MoveZCombinedGetStatus_Response
    if not "MoveZCombinedGetStatus_Response" in globals(): MoveZCombinedGetStatus_Response = namedtuple("MoveZCombinedGetStatus_Response", "Status,PlatenSafe,Height,HeightMax,HeightRelative,SafeHeight,Message")
    return MoveZCombinedGetStatus_Response(str(rsp[0]),int(rsp[1]),Decimal(rsp[2]),Decimal(rsp[3]),Decimal(rsp[4]),Decimal(rsp[5]),str("" if len(rsp) < 7 else ' '.join(rsp[6:])))

def GeteVueLicense():
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Returns the type of licensed eVue model. Could be 40x and Pro.
    Status: internal
    ----------
    Response:
        IseVue40x:int
        IseVuePro:int
    ----------
    Command Timeout: 10000
    Example:GeteVueLicense
    """
    rsp = MessageServerInterface.sendSciCommand("GeteVueLicense")
    global GeteVueLicense_Response
    if not "GeteVueLicense_Response" in globals(): GeteVueLicense_Response = namedtuple("GeteVueLicense_Response", "IseVue40x,IseVuePro")
    return GeteVueLicense_Response(int(rsp[0]),int(rsp[1]))

def SetTemperaturePresets(Preset1="", Preset2="", Preset3="", Preset4=""):
    """
    ***WARNING: internal command. Do not use without explicit instructions from FormFactor***
    Sets the temperature presets.
    Status: internal
    ----------
    Parameters:
        Preset1:Decimal = 0
        Preset2:Decimal = 0
        Preset3:Decimal = 0
        Preset4:Decimal = 0
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("SetTemperaturePresets",Preset1,Preset2,Preset3,Preset4)


def LoadScopeFenceConfiguration(Enable="", Path=""):
    """
    Load a previously saved Scope-Fence-configuration or remove the current
    configuration
    Status: published
    ----------
    Parameters:
        Enable:int = 0
        Path:str = ""
    ----------
    Command Timeout: 5000
    """
    MessageServerInterface.sendSciCommand("LoadScopeFenceConfiguration",Enable,Path)


def SetSoftwareStop(StopState=""):
    """
    Set the state of the software stop.
    Status: published
    ----------
    Parameters:
        StopState:int = 0
    ----------
    Command Timeout: 1000
    """
    MessageServerInterface.sendSciCommand("SetSoftwareStop",StopState)


#End of module
