# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
# 
# Copyright (c) 2022 SweepMe! GmbH
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

# SweepMe! device class
# Type: Signal
# Device: Stanford Research DG535



from EmptyDeviceClass import EmptyDevice

class Device(EmptyDevice):
    
    """
    <p><strong>Keywords:</strong> Delay pulse generator, Stanford Research Systems</p>
    <p>&nbsp;</p>
    <p><strong>Communication:</strong></p>
    <ul>
    <li>Default GPIB address is 15</li>
    </ul>
    <p>&nbsp;</p>
    <p><strong>Usage:</strong></p>
    <ul>
    <li>For each delay output (T0, A, B, C, D) a Signal module must be added to the sequencer.</li>
    <li>Channels are defined like "A -&gt; T0" which means that delay output A is configured with a delay time referenced to T0.</li>
    <li>Amplitude and offset can only be set if the Waveform is 'Variable". Please make sure that amplitude and offset do not lead to signals larger than 4 V.</li>
    <li>If there are several Signal modules in one branch, the lowest one will set the trigger mode and the frequency if internal trigger is used.</li>
    <li>Frequency will only bet set when trigger mode is set to "Internal".</li>
    </ul>
    """

    def __init__(self):
    
        EmptyDevice.__init__(self)
        
        self.shortname = 'DG535'
       
        self.port_manager = True
        self.port_types = ['GPIB']
        #self.port_identifications = ['']

        """ 
        Integer - Channel assignments
        
        0 Trigger Input
        1 T0 Output
        2 A Output
        3 B Output
        4 AB and -AB Outputs
        5 C Output
        6 D Output
        7 CD and -CD Outputs
        """

        self.channels_dict = {
                            "TI": 0,  # Trigger Input
                            "T0": 1,  # T0 Output
                            "A":  2,  # A Output
                            "B":  3,  # B Output
                            "AB": 4,  # AB and -AB Outputs
                            "C":  5,  # C Output
                            "D":  6,  # D Output
                            "CD": 7,  # CD and -CD Outputs
                            }
                            
        self.channels_dict_inv = {
                            0: "TI",  # Trigger Input
                            1: "T0",  # T0 Output
                            2: "A",   # A Output
                            3: "B",   # B Output
                            4: "AB",  # AB and -AB Outputs
                            5: "C",   # C Output
                            6: "D",   # D Output
                            7: "CD",  # CD and -CD Outputs
                            }
                            
                            
        self.waveforms_dict = {
                              "TTL normal":   0,
                              "TTL inverted": 0, 
                              "NIM normal":   1,
                              "NIM inverted": 1,
                              "ECL normal":   2,
                              "ECL inverted": 2,
                              "Variable":     3,
                              }
        
        self.impedances_dict = {
                                "50 Ohm": 0, 
                                "High-Z": 1,
                                }

        self.triggers_dict = {
                            "Internal":         0,
                            "External":  1,
                            "Single-Shot":      2,
                            # "Burst":          3,
                            }

        c = ["T0", "A", "B", "C", "D"]
        self.channels_list = []
        for x in c:
            for y in c:
                if x != "T0" and x!=y:
                    self.channels_list.append("%s -> %s" % (x,y))
        self.channels_list += ["AB", "CD"]
        self.channels_list = ["T0"] + self.channels_list

    def set_GUIparameter(self):
        
        GUIparameter = {
                        "Channel":  self.channels_list,
                        "SweepMode": ["None", "Delay in s"],  # "Frequency [Hz]", "Period [s]", "HiLevel [V]", "LoLevel [V]", "Phase [deg]",  "Delay [s]", "Pulse width [s]", "Duty cycle [%]"],
                        "Waveform": list(self.waveforms_dict.keys()),
                        
                        "PeriodFrequency" : ["Frequency in Hz:", "Period in s:"],
                        "PeriodFrequencyValue": 1000,
                        
                        "AmplitudeHiLevel" : ["Amplitude in V:"],
                        "OffsetLoLevel" : ["Offset in V:"],
                        "AmplitudeHiLevelValue": 1.0,
                        "OffsetLoLevelValue": 0.0,
                        "DelayPhase": ["Delay in s:"],
                        "DelayPhaseValue": 0.0,
                        # "DutyCyclePulseWidth": ["DutyCycle [%]", "PulseWidth [s]"], 
                        # "DutyCyclePulseWidthValue": 50,
                        "Impedance" : list(self.impedances_dict.keys()),
                        "Trigger": list(self.triggers_dict.keys()),
                        }
                        
        return GUIparameter               

    def get_GUIparameter(self, parameter={}):

        channel_list                     = parameter["Channel"].split(" -> ")
        
        self.channel = channel_list[0]
        
        if len(channel_list) == 2:
            self.ref_channel = channel_list[1]
        else:
            self.ref_channel = None  # this is the case for AB and CD
        
        self.sweep_mode                  = parameter['SweepMode'] 
        self.waveform                    = parameter['Waveform'] 
        self.periodfrequency             = parameter['PeriodFrequency' ]
        self.periodfrequencyvalue        = float(parameter['PeriodFrequencyValue'])
        # self.amplitudehilevel          = parameter['AmplitudeHiLevel']
        self.amplitudehilevelvalue       = float(parameter['AmplitudeHiLevelValue'])
        # self.offsetlolevel             = parameter['OffsetLoLevel']
        self.offsetlolevelvalue          = float(parameter['OffsetLoLevelValue'])
        # self.dutycyclepulsewidth       = parameter['DutyCyclePulseWidth']
        # self.dutycyclepulsewidthvalue  = float(parameter['DutyCyclePulseWidthValue'])
        # self.delayphase                = parameter['DelayPhase']
        self.delayvalue                  = parameter['DelayPhaseValue']
        self.impedance                   = parameter['Impedance']
        self.trigger_type                = parameter['Trigger']
        

        if self.sweep_mode == 'None':
            self.variables =[]
            self.units =    []
            self.plottype = []     # True to plot data
            self.savetype = []     # True to save data
            
        else:
            self.variables = [self.sweep_mode.replace(" ", "").split("in")[0]]
            self.units = [self.sweep_mode.replace(" ", "").split("in")[1]]
            self.plottype = [True] # True to plot data
            self.savetype = [True] # True to save data
            
    """ Here semantic standard functions start """

    def initialize(self):
        self.clear_instrument()
        
        
        # Early exceptions if driver is misconfigured
        if self.ref_channel is None:  # AB, CD, and T0               
            if self.sweep_mode == "Delay in s":   
                raise Exception("A delay sweep cannot be done for channels AB, CD, and T0")
        
        
    def deinitialize(self):
        pass
                
    def configure(self):

        # Delay
        if not self.ref_channel is None:  # excluding AB, CD, and T0
            self.set_delay(self.channel, self.ref_channel, self.delayvalue)
        else:
            if self.delayvalue != 0.0:
                raise Exception("A delay cannot be set for channels AB, CD, and T0")

        
        # Polarity
        if self.channel in ["A", "B", "C", "D", "T0"]:  # only delay output ports
            if not self.waveform == "Variable":
                self.set_output_polarity(self.channel, int("normal" in self.waveform))
            
        # Output mode
        self.set_output_mode(self.channel, self.waveforms_dict[self.waveform])
        
        # Impedance
        self.set_impedance(self.channel, self.impedances_dict[self.impedance])

        # Amplitude:
        if self.waveform == "Variable":
            self.set_output_amplitude(self.channel, self.amplitudehilevelvalue)

        # Offset
        if self.waveform == "Variable":
            self.set_output_offset(self.channel, self.offsetlolevelvalue)

        # Trigger rate
        if self.trigger_type == "Internal":
            if self.periodfrequency == "Frequency in Hz:":
                self.set_trigger_rate(0,self.periodfrequencyvalue)
            elif self.periodfrequency == "Period in s:":
                self.set_trigger_rate(0,1.0/self.periodfrequencyvalue)
            else:
                raise Exception("Neither 'Frequency in Hz' nor 'Period in s' selected.")

        # Comment: We might have to wait a bit to let the new frequency settle as this can take up to 2s
        # according to the manual

        if self.sweep_mode == "None":
            # Trigger mode
            self.set_trigger_mode(self.triggers_dict[self.trigger_type])

    def unconfigure(self):
        self.set_trigger_mode(2)  # Single shot trigger i.e. no trigger

    def apply(self):

        if self.sweep_mode == 'Delay in s':
            # Delay
            if not self.ref_channel is None:  # excluding AB, CD, and T0
                self.set_delay(self.channel, self.ref_channel, float(self.value))
                    
            self.set_trigger_mode(self.triggers_dict[self.trigger_type])

    def measure(self):

        if self.trigger_type == "Single-Shot":
            self.trigger_single()

    def call(self):

        if self.sweep_mode == 'Delay in s':
            delay = float(self.get_delay(self.channel)[0])
            return [delay]
        else:
            return []
            
                   
                   
    """ Here, convenience functions start """
              
    def clear_instrument(self):
    
        """ 
        resets the instrument to default values
        """
           
        self.port.write("CL")
                   
    def set_display_string(self, text):
    
        """ 
        sets the display string. 
        
        Parameters:
            text(str): The text to be displayed with max. 20 characters
        
        """
        
        text = text.replace(" ", "_")[:20]  # maximum 20 characters
        
        if len(text)>1:
            self.port.write("DS %s" % str(text))
        else:
            self.port.write("DS")  # clear display string

    def clear_display_string(self):
    
        """
        clears the display string
        """       
        
        self.port.write("DS")
                   
    def set_delay(self, channel, ref_channel, delay_time):
    
        """
        Delay can be set for channels "A", "B", "C", "D".
        Delay time can be changed in steps of 5 ps. 
        The DG535 will automatically round to the next multiple of 5 ps.
        Maximum delay is 1000 s minus 5 ps.
        
        Parameters:
            channel(int)      -> options are "A", "B", "C", "D"
            ref_channel(int)  -> options are "TO" "A", "B", "C", "D"
            delay_time(float)  
        """
    
        if not channel in ["A","B","C","D"]:
            raise ValueError("Delay can only be set for channels 'A', 'B', 'C', and 'D'.")
    
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
          
        if ref_channel in self.channels_dict:
            ref_channel = self.channels_dict[ref_channel]
         
        # delay time is sent with ps resolution
        self.port.write("DT %i,%i,%1.12f" % (int(channel), int(ref_channel), float(delay_time) ) )
        
    def get_delay(self, channel):

        """\
        get the reference channel and delay time for the fiven output decay channel 
        
        Parameters:
            channel (int, str): Channel being "A", "B", "C", "D"
        
        Returns:
            float: Delay time in s
            str: Reference channel
        """
        
        if not channel in ["A","B","C","D"]:
            raise ValueError("Delay can only be queried for channels 'A', 'B', 'C', and 'D'.")
        
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]      
    
        self.port.write("DT %i" % (int(channel)))
        
        answer = self.port.read()
        
        ref_channel = self.channels_dict_inv[int(answer.split(",")[0])]
        delay_time  = float(answer.split(",")[1])
        
        self.channels_dict_inv
        
        return  delay_time, ref_channel
        
        
    def set_impedance(self, channel, mode):
    
        """
        channel = 0 -> External trigger impedance
        channel = 1 or "T0" -> T0 Output
        channel = 2 or "A"  -> A Output
        channel = 3 or "B"  -> B Output
        channel = 4 or "AB" -> AB and -AB Outputs
        channel = 5 or "C"  -> C Output
        channel = 6 or "D"  -> D Output
        channel = 7 or "CD" -> CD and -CD Outputs

        mode = 0 -> 50 Ohm load
        mode = 1 -> high-Z load
        """
    
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
           
        self.port.write("TZ %i,%i" % (int(channel), int(mode)) )
        
    def get_impedance(self, channel):

        """
        channel = 0 -> External trigger impedance
        channel = 1 or "T0" -> T0 Output
        channel = 2 or "A"  -> A Output
        channel = 3 or "B"  -> B Output
        channel = 4 or "AB" -> AB and -AB Outputs
        channel = 5 or "C"  -> C Output
        channel = 6 or "D"  -> D Output
        channel = 7 or "CD" -> CD and -CD Outputs
        """
        
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
            
        self.port.write("TZ %i" % (int(channel)) )
        
        answer = self.port.read()
        
        return int(answer)
        
    def set_output_mode(self, channel, mode):
    
        """
        mode = 0 -> TTL 0-4V
        mode = 1 -> NIM
        mode = 2 -> ECL
        mode = 3 -> Var (variable amplitude and offset)
        """
    
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
        else: 
            raise ValueError("Channel '%s' unknown." % channel)
            
        self.port.write("OM %i,%i" % (int(channel), int(mode)) )    
            
            
    def get_output_mode(self, channel):
    
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
        else: 
            raise ValueError("Channel '%s' unknown." % channel)
            
        self.port.write("OM %i" % (int(channel)) ) 
        
        answer = self.port.read()
        
        return int(answer)
            
    def set_output_amplitude(self, channel, amplitude):
    
        """
        amplitude must be chosen so that offset + amplitude is not higher than 4.0 V
        """
    
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
        else: 
            raise ValueError("Channel '%s' unknown." % channel)
            
        self.port.write("OA %i,%1.3f" % (int(channel), float(amplitude)) )    
            
            
    def get_output_amplitude(self, channel):
    
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
        else: 
            raise ValueError("Channel '%s' unknown." % channel)
            
        self.port.write("OA %i" % (int(channel)) ) 
        
        answer = self.port.read()
        
        return float(answer)
        
        
    def set_output_offset(self, channel, offset):
    
        """
        offset must be chosen so that offset + amplitude is not higher than 4.0 V
        
        Parameters:
            channel (int,str)
            offset (float)
        """
    
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
        else: 
            raise ValueError("Channel '%s' unknown." % channel)
            
        self.port.write("OO %i,%1.3f" % (int(channel), float(offset)) )    
            
            
    def get_output_offset(self, channel):
    
        """
        get the offset value for the given delay output channel
        
        Parameters:
            channel (int,str)
            
        Returns:
            offset (float)
        """
    
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
        else: 
            raise ValueError("Channel '%s' unknown." % channel)
            
        self.port.write("OO %i" % (int(channel)) ) 
        
        answer = self.port.read()
        
        return float(answer)        
        
        
    def set_output_polarity(self, channel, polarity):
    
        """
        Sets the output polarity
        
        Parameters:
            channel(str)
            polarity(int)
                0 -> inverted 
                1 -> normal
        """
    
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
        else: 
            raise ValueError("Channel '%s' unknown." % channel)
            
        self.port.write("OP %i,%i" % (int(channel), int(polarity)) )    
            
            
    def get_output_polarity(self, channel):
    
        """
        Gets the output polarity of the given channel
        
        Parameters:
            channel(str)
            
        Returns:
            polarity(int)
                0 -> inverted 
                1 -> normal
        """
    
        if channel in self.channels_dict:
            channel = self.channels_dict[channel]
        else: 
            raise ValueError("Channel '%s' unknown." % channel)
            
        self.port.write("OP %i" % (int(channel)) ) 
        
        answer = self.port.read()
        
        return int(answer)
        
        
    def set_trigger_mode(self, mode):
    
        """
        Sets the trigger mode
        
        Parameters:
            mode(int)
                0 -> Internal
                1 -> External
                2 -> Single shot
                3 -> Burst
        """

        self.port.write("TM %i" % (int(mode)))
        
    def get_trigger_mode(self):
    
        """
        Get the trigger mode
        
        Returns:
            mode(int)
                0 -> Internal
                1 -> External
                2 -> Single shot
                3 -> Burst
        """

        self.port.write("TM")
        answer = self.port.read()
        return int(answer)
        
    def trigger_single(self, count = 1):
    
        """
        sends a single trigger if the instrument is in single shot mode "TM2"
        
        Parameters:
            count(int) ->mMultiple triggers can be sent using a count value larger than 1, default = 1
        """

        self.port.write("SS" + "; SS" * (int(count)-1))
        
        
    def set_trigger_rate(self, mode, rate):
    
        """
        Sets the trigger rate for the given mode
        
        Parameters:
            mode(int)
                0 -> internal trigger rate
                1 -> burst trigger rate
        
            rate(float) -> Rate is given in Hz
        """
        
        self.port.write("TR %i,%1.4f" % (int(mode), float(rate)) )

    def get_trigger_rate(self, mode):
    
        """
        get the trigger rate for the give mode
        
        Returns:
            mode(int)
                0 -> internal trigger rate
                1 -> burst trigger rate
        """
    
        self.port.write("TR %i" % (int(mode)) )
        answer = self.port.read()
        return float(answer)

    def set_trigger_slope(self, mode):

        """
        Set the trigger slope
        
        Parameters:
            mode(int)
                0 -> falling edge
                1 -> rising edge
        """

        self.port.write("TS %i" % (int(mode)))

    def get_trigger_slope(self):
    
        """
        get the trigger slope
        
        Returns:
            mode(int):
                 0 -> falling edge
                 1 -> rising edge
        """

        self.port.write("TS")
        answer = self.port.read()
        return int(answer)
        
        
                   
