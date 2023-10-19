# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.

# MIT License

# Copyright (c) 2021 Axel Fischer und Felix Kaschura GbR ("SweepMe!")

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

# Contribution: We like to thank Heliatek GmbH/Dr. Ivan Ramirez for providing the initial version of this driver.

# SweepMe! device class
# Type: LockIn
# Device: ZurichInstruments MFLI


from FolderManager import addFolderToPATH
addFolderToPATH()  # needed to import zhinst from libs folder of this device class

from zhinst import ziPython as ziP

from EmptyDeviceClass import EmptyDevice
import numpy as np
import time

__api_level__ = 6  # developed on 6


class Device(EmptyDevice):
    
    description = """
                    Zurich Instruments MF in lock-in config (MFLI)).
                    The MF are multi function instruments. Unless simulataneous measurements are required
                    recommended to end session and declare a new device in other config after
                    <br>
                    Features:
                    <ul><li>supports synchronous measurements with 1 demodulator </li>
                    <li>easy extension to 4 demodulators (MD option)</li>
                    <li>supports single getSample and dataAcquisitionModule streaming (improvements needed) </li>
                    <li>supports auto ranging </li>
                    <li>supports auto settling time ("auto : settle_val"). The lockin will wait until val/val_at_inf_wait (settle_val [0,1)) is reached. For filter order 8a nd 0.99 this corresponds to 16 TCs</li>
                    <li>supports dynamic TC based on R eg "0.1 <- 1e-8 -> 0.15 <- 1e-9 -> 0.25 <- 1e-10"   </li>
                    <li>does not support output</li>
                    <li>USB comm requires driver install (see getting started in docu)</li></ul>
                    """

    def __init__(self):
        
        EmptyDevice.__init__(self)
        
        self.shortname = "MFLI"
        self._demods = [1, 4]  # 4 with MD option
       
        self.daq = None
        self.devID = "no dev selected"
        self.in_ch = None
        
        self.variables = ["R", "Theta", "TC"]
        self.units = ["A|V", "deg.", "s"]
        self.plottype = [True, True, True]  # True to plot data
        self.savetype = [True, True, True]  # True to save data
        
        self.filters = ["6dB", "12dB", "18dB", "24dB", "30dB", "36dB", "42dB", "48dB"]

        # https://blogs.zhinst.com/kivanc/2020/02/20/choose-the-right-tool-to-acquire-lock-in-data/
        self.daq_methods = ["single", "poll", "daqModule"]
        self.daq_method = "single"
        
        self.R, self.Phi = None, None
        self.time_const = None
        
    def find_ports(self):
        """use ZI api to find IDs of all devices it can access - USB comm requires driver install"""
        dev_explorer = ziP.ziDiscovery()
        devs = dev_explorer.findAll()

        return devs

    def set_GUIparameter(self):
        
        gui_parameter = {
            "Input": ["I", "V", "diff V"],
            "Slope": ["6dB", "12dB", "18dB", "24dB", "30dB", "36dB", "42dB", "48dB"],
            "TimeConstant": ["0.200",
                             "0.1 < 1e-8 > 0.15 < 1e-9 > 0.25 < 1e-10 > 0.5 < 1e-11 > 2 < 1e-12 > 5",
                             "0.1 < 1e-3 > 0.15 < 1e-4 > 0.25 < 1e-5 > 0.25 < 1e-6 > 0.5 < 1e-8 > 2 < 1e-10 > 5"],
            "WaitTimeConstants": 'auto : 0.99',
            "Coupling": ["AC", "DC"],
            "Ground": ["Float", "Ground"],
            "Source": ["Internal", "Aux In 1", "Aux In 2"],
            "Sensitivity": ["Auto", "Auto optimise"],
            "Gain": ["Determined by inst meas range"],
            "OscillatorFrequency": ""
        }
                        
        return gui_parameter
    
    def get_GUIparameter(self, parameter={}):

        self.devID = str(parameter["Port"]).lower()
        self.ref = parameter["Source"]
        self.filter = self.filters.index(parameter["Slope"]) + 1  # calc filter order
        self.pars = parameter
        
        # process waiting time input
        inpt = parameter["WaitTimeConstants"].replace(" ", "").split("auto:")  # gives list ["", 0.99] or list [val]
        self.is_number(inpt[-1], "Input Error. Wait time not numeric or of type 'auto : num_val' " +
                                 " num_val = lockin settle value 0<=val<1)")  # check for error
        settle_val = float(inpt[-1])  # works also if input is float
        if len(inpt) == 2 and 0 <= settle_val < 1:  # if input =  "auto : x" with 0<=x<1
            settle_val = self.calc_settle_time(self.filter, settle_val)
        parameter["WaitTimeConstants"] = settle_val
                
        self.auto_range = True if parameter['Sensitivity'].startswith('Auto') else False
        self.auto_range = True if parameter['Sensitivity'] == 'Auto optimise' else False
        
        # process TC input
        if self.is_number(parameter["TimeConstant"], "", raise_=False):
            parameter["TimeConstant"] = float(parameter["TimeConstant"])
            self.TCs_list = parameter["TimeConstant"]
        else:
            input_str = parameter["TimeConstant"].replace("<", "|").replace(">", "|")
            self.TCs_list = np.array(input_str.split("|")[::2], dtype=float)
            self.TCs_Rlist = np.array(input_str.split("|")[1::2], dtype=float)
            self.TCs_Rlist = np.append(self.TCs_Rlist, [0])  # deal with values lower than last given R
            self.TCs_list = np.append(self.TCs_list, self.TCs_list[-1])  # for R lower than last input use last given TC
            if not self.TCs_list.dtype == self.TCs_Rlist.dtype == float:
                raise IOERROR("ZI MFLI %s: input error in TimeConstant field, check read me for expected fmt"
                              % self.devID)
            elif not np.all(self.TCs_Rlist[:-1] >= self.TCs_Rlist[1:]):
                raise Warning("ZI MFLI %s: R values not descending in TimeConstant field, "
                              "may result in unexpected behaviour" % self.devID)

        self.pars = parameter

    """ here, semantic standard functions are defined """

    def connect(self):
    
        dev_explorer = ziP.ziDiscovery()
        dev_explorer.find(self.devID)
        cpars = dev_explorer.get(self.devID)  # devID came from findAll --> will work
        if cpars['apilevel'] != __api_level__:
            print("MFLI lockin warning: api level {0} does not match driver level (6)".format(cpars['apilevel']))
        
        self.daq = ziP.ziDAQServer(cpars['serveraddress'], cpars['serverport'], cpars['apilevel'])  # make API session
        self.daq.connectDevice(self.devID, cpars['interfaces'][0])  # blocking
    
    def disconnect(self):
        if self.daq:
            self.daq.disconnectDevice(self.devID)

    def initialize(self):
        pass
        
    def deinitialize(self):
        """return lockin to 0.1s
        only works for single demod model for now (dm_indx set to 0)"""
    
        self.daq.set([['/%s/demods/%d/timeconstant' % (self.devID, 0), 0.1]])
        self.daq.sync() 

    def configure(self):
        """apply meas settigns for the MFLI with single demodulator
        think this needs some overaul for MFLI-MD """
        
        print("Configuring lockin")
        print("ZI MFLI INFO: settle time = %.2f [TC]s" % self.pars["WaitTimeConstants"])
        dm_indx = 0  # demod index (0-3 for MD option, 0 for std)
        in_ch = 1 if self.pars["Input"] == "I" else 0  # input channel I|A
        
        self.time_const = self.TCs_list if type(self.TCs_list) == float else 0.1  # start at 0.1 since dont know R val

        settings = [
                    ['/%s/demods/%d/enable' % (self.devID, dm_indx), 1],
                    ['/%s/demods/%d/adcselect' % (self.devID, dm_indx), in_ch],
                    ['/%s/demods/%d/order' % (self.devID, dm_indx), self.filter],
                    ['/%s/demods/%d/timeconstant' % (self.devID, dm_indx), self.time_const],
                    # ['/%s/demods/%d/oscselect' % (self.devID, dm_indx), 1],  # not needed without MD option
                    ['/%s/demods/%d/harmonic' % (self.devID, dm_indx), 1],  # scale lockin freq down by int
                    # ['/%s/extrefs/0/enable' % self.devID, 0],  # MFLI MD only?
                    ['/%s/sigins/%d/float' % (self.devID, in_ch), int(self.pars["Ground"] == "FLOAT")]]
        
        if self.ref != "Internal":
            ref_ch = 8 if self.ref == "Aux In 1" else 9
            settings += [
                ['/%s/extrefs/0/enable' % self.devID, 1],  # not sure needed
                ['/%s/demods/1/adcselect' % self.devID, ref_ch]
            ]
        else:
            self.is_number(self.pars['OscillatorFrequency'], "Osc freq not numeric")
            settings += [['/%s/extrefs/0/enable' % self.devID, 0],
                         ['/%s/oscs/0/freq' % self.devID, float(self.pars['OscillatorFrequency'])]]

        if in_ch == 0:  # voltage options
            settings += [
                ['/%s/sigins/0/ac' % self.devID, int(self.pars["Coupling"] == "AC")],
                ['/%s/sigins/0/diff' % self.devID, int(self.pars["Input"] == "diff V")],
                ["/%s/SIGINS/0/ON" % self.devID, 1],
                ["/%s/SIGINS/0/AUTORANGE" % self.devID, int(self.auto_range)]
            ]
            self._range = self.daq.getDouble("/%s/sigins/0/RANGE" % self.devID)
        else:  # current channel
            settings += [
                ["/%s/currins/0/ON" % self.devID, 1],
                ["/%s/currins/0/AUTORANGE" % self.devID, int(self.auto_range)]
            ]
            self._range = self.daq.getDouble("/%s/currins/0/RANGE" % self.devID)

        print("ZI Lockin range: %.2e [A|V]" % self._range)
        
        print("ZI MFLI settings:", settings)
        self.daq.set(settings)
        print("letting lockin settle")
        # time.sleep(1) \shpuld be done
        self.daq.sync()

    def reconfigure(self, x, y):
        print("RECONFIG CALLED")

    def adapt(self):
        """called at each meas point irrespective of branch"""
        # setup daq
        if type(self.TCs_list) != float:
            self.update_tc()  # smart measurements with auto integration
        time.sleep(self.pars["WaitTimeConstants"] * self.time_const)

    # unclear whether works for currin or only sigin
    # def autorange(self):
    #     """use zhinst convenience func rather than write our own"""
    #     # channel = 1 if self.pars["Input"] == "I" else 0#input channel I|A
    #     sigin_autorange(self.daq, self.devID, 0) #channel is int

    def measure(self):
        """synchronous (blocking) measurement operation based on zi's poll daq method"""
        
        if self.optimise_range:
            self.optimise_range()

        # print range change info to user
        if self.pars["Input"] == "I":
            range_ = self.daq.get("/%s/currins/0/RANGE" % self.devID)[self.devID]
        else:
            range_ = self.daq.getDouble("/%s/SIGINS/0/RANGE" % self.devID)
            
        if not range_ == self._range:
            self._range = range_
            print("ZI Lockin range set to %.2e [A|V]" % self._range)
    
        if self.daq_method == "single":
            dat = self.daq.getSample('/%s/demods/0/sample' % self.devID)
            self.R = float(np.sqrt(dat["x"]**2 + dat["y"]**2))
            self.Phi = float(dat["phase"])
            return self.R, self.Phi
            
        elif self.daq_method == "daqModule":
            return self.sweep_time()

        elif self.daq_method == "poll":
            raise NotImplementedError("the Zi poll is not implemented - please use daqModule")
    
    def call(self):
        
        # probably getdouble, getdouble, getint at the right addresses/nodes
        return [self.R, self.Phi, self.time_const]  # replace with a list of values corresponding to defined variables

    """ here, additional convenience functions are defined """
    
    def calc_BW(self, time_constant, filter_order):  # nep or 3dB?
        """conversion between BW and time_constant following section 6.2 of MFLI manual"""
        
        filt_corr = [1, 0.6436, 0.5098, 0.4350, 0.3856, 0.3499, 0.3226, 0.3008]
        return filt_corr[filter_order-1]/(2*np.pi*time_constant)

    def calc_settle_time(self, filter_order, settle_val=0.99):
        """calculate the settling time in tcs of the lockin to reach
        a settle_value between 0 and 1* the steadystate (inf wait) value"""
        
        # calc response (after blog pot)
        times = np.linspace(0, 20, 101)  # in tcs
        
        response = [1-np.exp(-times)]
        resp_term, last_term = 1, 1
        
        for k in range(1, filter_order):
            last_term = last_term*times/k
            resp_term += last_term
            response.append(1-np.exp(-times)*resp_term)
        
        ind = np.abs(response[-1]-settle_val).argmin()
        return times[ind]

    def is_number(self, x, error_, raise_=True):
        """check something is a number"""
        
        try:
            float(x)
            return True
        except ValueError:
            if raise_:
                raise TypeError("ZI MFLI %s: " % self.devID + error_)
            else:
                return False

    def optimise_range(self):
        """check whether the range is really the lowest one available
        There is an issue with ZI's autorange algorithm probably to do with the
        transimpedance amp's variable input impedance. 
        The signal also changes with transimpedance imput amp so use carefully ..."""
        # max sig and min sig return the max signal as prop of range
        max_sig = self.daq.getDouble("/%s/CURRINS/0/max" % self.devID)
        min_sig = self.daq.getDouble("/%s/CURRINS/0/min" % self.devID)
        # in principle can only go down if <0.1.
        # In practice this isn't true, perhaps because the perf depends on the gain
        if not abs(min_sig) < 0.22 and max_sig < 0.22:
            return
        
        self.daq.setDouble('/%s/currins/0/range' % self.devID, self._range / 10)
        max_sig = self.daq.getDouble("/%s/CURRINS/0/max" % self.devID)
        min_sig = self.daq.getDouble("/%s/CURRINS/0/min" % self.devID)
        if max_sig > 1 or abs(min_sig) > 1:
            print("Overload trying to optimise range")
            self.daq.setDouble('/%s/currins/0/range' % self.devID, self._range)
        else:
            self._range /= 10
            print("ZI Lockin range: %.2e [A|V]" % self._range)
            
        # print("RANGE INFO", "%.3e"%self._range, "%.3e"%max_sig, "%.3e"%min_sig)#

    def update_tc(self):
        """for dynamic integration times, set your own ranges. will miss one point - not suited for big jumps"""
        previous = self.time_const
        if not self.R:
            return 0.1  # no meas yet
        # find appropriate tc
        ind = np.where(self.TCs_Rlist < self.R)[0][0]
        self.time_const = self.TCs_list[ind]

        if previous != self.time_const:
            dm_indx = 0
            self.daq.set([['/%s/demods/%d/timeconstant' % (self.devID, dm_indx), self.time_const]])
            self.daq.sync() 
        return

    def sweep_time(self):
        """ implementation of the daqmodule. for full streaming a pyqt signal
        should be emitted to the main"""
        self.daq_module.set('preview', 1)
        self.daq_module.execute()
        timeout = 50 * self.pars["TimeConstant"]
        t0_measurement = time.time()
        # The maximum time to wait before reading out new data.
        while not self.daq_module.finished():
            t0_loop = time.time()
            if time.time() - t0_measurement > timeout:
                raise Exception("Timeout after {} s - recording not complete. Are the streaming nodes enabled? "
                                "Has a valid signal_path been specified?".format(timeout))
            # result = self.daq_module.read(True)#flatten neseted dict or die
            # print(result)
            progress = float(self.daq_module.progress()[0])
            print(str(progress*100)+"%")
            # We don't need to update too quickly.
            time.sleep(timeout/150)
            print('meas time: ', time.time() - t0_measurement)
            result = self.daq_module.read(True)  # true flattens array
            time.sleep(0.3)
            dat_keys = [key for key in result.keys() if key.startswith('/%s/demods/0/' % self.devID)]
            dat = {key: value for key, value in result.items() if key in dat_keys}  # a nested dict mess
            
            print('settings:', dat[dat_keys[0]][0])
            print("array length:", len(dat[dat_keys[0]][0]["value"][0]))

            # print([key if key.find("%s"self.devID)>=0 for key in in result.keys()])
            self.daq_module.unsubscribe('/%s/demods/0/sample.r' % self.devID)
            self.daq_module.unsubscribe('/%s/demods/0/sample.r.avg' % self.devID)
            self.daq_module.unsubscribe('/%s/demods/0/sample.theta' % self.devID)
            self.daq_module.unsubscribe('/%s/demods/0/sample.theta.avg' % self.devID)
            return dat
