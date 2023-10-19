# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2019, 2021 Axel Fischer (sweep-me.net)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# The files LeapC.dll and LeapCSharp.NET4.5.dll are not covered by the above license

# SweepMe! device class
# Type: Logger
# Device: Leap Motion


# needed to find dlls in Device Class folder
import FolderManager as FoMa
FoMa.addFolderToPATH()

from ErrorMessage import error, debug


from EmptyDeviceClass import EmptyDevice # Class comes with SweepMe!

class Device(EmptyDevice):

    description =   """
                    <h4>LEAP motion sensor</h4>
                    <p>The LEAP motion sensor is a device that can track the motion of your hands using two cameras working in the near infra-red range.</p>
                    <p>&nbsp;</p>
                    <p><strong>Features:</strong></p>
                    <ul>
                    <li>Track the main point of your left and/or right hand.</li>
                    <li>Returning x,y,z coordinates in mm with respect to the central point on the top surface of the sensor.</li>
                    <li>Plug&amp;play: No need to configure something after loading your setting.</li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Requirements:</strong></p>
                    <ul>
                    <li>LeapCSharp.NET4.5.dll and LeapC.dll are not distributed with this Device Class and must be put yourself into the folder 'libs' of this Device Class or into public SweepMe! folder 'ExternalLibraries'.&nbsp;</li>
                    <li>Both dll files are part of the Softwar development kit, e.g. 'Leap Motion Orion 3.2.1':<br /><a href="https://developer.leapmotion.com/releases/leap-motion-orion-321">https://developer.leapmotion.com/releases/leap-motion-orion-321</a></li>
                    </ul>
                    <p>&nbsp;</p>
                    <p><strong>Known issues:</strong></p>
                    <ul>
                    <li>If your hand is not detected, splay out your fingers to help the sensor recognizing your hand.</li>
                    <li>If you turn around your hand by 180&deg;, a left hand can become a right hand and vice versa.</li>
                    </ul>
                    """

    def __init__(self):
        EmptyDevice.__init__(self)
        
        self.shortname = "LeapMotion" # short name will be shown in the sequencer                

        
    def get_GUIparameter(self, parameter):
    
        self.variables = [] # defines as much variables you want
        self.units = [] # make sure that units and variables have the same amount
        self.plottype = []   # True to plot data, corresponding to self.variables
        self.savetype = []   # True to save data, corresponding to self.variables
        
        if parameter["Right hand"]:
            self.variables.extend(["Right hand x", "Right hand y", "Right hand z", "Right hand grab strength"])
            self.units.extend(["mm", "mm", "mm", ""])
            self.plottype.extend([True, True, True, True])
            self.savetype.extend([True, True, True, True])
            
        if parameter["Left hand"]:
            self.variables.extend(["Left hand x", "Left hand y", "Left hand z", "Left hand grab strength"])
            self.units.extend(["mm", "mm", "mm", ""])
            self.plottype.extend([True, True, True, True])
            self.savetype.extend([True, True, True, True])
            
        self.righthand = parameter["Right hand"]
        self.lefthand = parameter["Left hand"]
        
        
    def set_GUIparameter(self):
    
        # add keys and values to generate GUI elements in the Parameters-Box
        
        GUIparameter = {
                        "Right hand": True,   # Boolean creates a CheckBox
                        "Left hand": True,
                        }

        ### Tip:
        ### Make sure that you do not use special strings such as 'Port', 'Device', 'Data', 'Description', or 'Parameters'
        ### These strings have special meaning and should not be overwritten. 
        
        return GUIparameter
      
    def find_Ports(self):

        import clr
        try:
            lib = clr.AddReference("LeapCSharp.NET4.5")
        except:
            error("The libraries <b>LeapCSharp.NET4.5.dll</b> and <b>LeapC.dll</b> cannot be loaded. Please put these files into the public SweepMe! folder 'ExternalLibraries' or into the 'libs' folder of this Device class. Both files can be acquired via the LEAP motion SDK.")
            return ["Unable to load LeapCSharp.NET4.5.dll"]
        
        
        from Leap import Controller #, DeviceList, Frame
        
        self.controller = Controller()
        
        if self.controller.IsConnected and not self.controller.Devices.IsEmpty:
            return [str(self.controller.Devices.ActiveDevice)]
        else:
            return ["No Leap motion sensor found!"]
            
            
        # self.controller.FailedDevices().IsEmpty

   
    
    #### ----------------------------------------------------------------------------------------------------------------------
    
    #### here functions start that are called by SweepMe! during a measurement
    
        
    def connect(self):
    
        import clr
        try:
            lib = clr.AddReference("LeapCSharp.NET4.5")
        except:
            error("The libraries <b>LeapCSharp.NET4.5.dll</b> and <b>LeapC.dll</b> cannot be loaded. Please put these files into the public SweepMe! folder 'ExternalLibraries' or into the 'libs' folder of this Device class. Both files can be acquired via the LEAP motion SDK.")
            self.stop_Measurement("The libraries <b>LeapCSharp.NET4.5.dll</b> and <b>LeapC.dll</b> cannot be loaded. Please put these files into the public SweepMe! folder 'ExternalLibraries' or into the 'libs' folder of this Device class. Both files can be acquired via the LEAP motion SDK.")
            return False
            
        from Leap import Controller #, DeviceList, Frame
        
        self.controller = Controller()
        
        # print(self.controller)
        # print(self.controller.IsConnected)
        # print(self.controller.IsServiceConnected)
        # print(self.controller.Frame())
        # print(self.controller.FrameReady"())
        # print(self.controller.InternalFrameReady"())
        
                  
      
        
    def request_result(self):
            

        self.frame = self.controller.Frame() # get last frame
        # print(frame)
        # print(frame.Id)
        
        
    def process_data(self):
    
        self.results = []
    
        hands = list(self.frame.Hands)
        
        # hand.GrabStrength
        right = None
        left = None
    
        # lets check which hands are detected
        for hand in hands:
        
            if hand.IsRight:
                right = hand
            
            if hand.IsLeft:
                left = hand
         
        # add values for right hand if requested and available
        if self.righthand:
            if not right is None:
                vector = right.PalmPosition
                # print(vector.x, vector.y, vector.z)
                self.results.extend([vector.x, vector.y, vector.z, right.GrabStrength])
                
            else:
                self.results.extend([float('nan'), float('nan'), float('nan'), float('nan')])

        # add values for left hand if requested and available
        if self.lefthand:
            if not left is None:
                vector = left.PalmPosition
                # print(vector.x, vector.y, vector.z)
                self.results.extend([vector.x, vector.y, vector.z, left.GrabStrength])
                
            else:
                self.results.extend([float('nan'), float('nan'), float('nan'), float('nan')])
            
 
    def call(self):

        return self.results
