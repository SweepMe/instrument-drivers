# This Device Class is published under the terms of the MIT License.
# Required Third Party Libraries, which are included in the Device Class
# package for convenience purposes, may have a different license. You can
# find those in the corresponding folders or contact the maintainer.
#
# MIT License
#
# Copyright (c) 2024 SweepMe! GmbH (sweep-me.net)
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


# SweepMe! driver
# * Module: Spectrometer
# * Instrument: Ocean Optics USB spectrometers


import os
import numpy as np
from pysweepme.ErrorMessage import error
from pysweepme.FolderManager import addFolderToPATH

od_api_imported = False
od_path_variable = "OCEANDIRECT_HOME"
api_path_defined = od_path_variable in os.environ
if api_path_defined:
    od_path = os.environ[od_path_variable] + os.sep + "Python"
    # Adding the OceanDirect Python API module to the environment so it can be imported
    addFolderToPATH(od_path)

    try:
        from oceandirect import OceanDirectAPI
        od_api_imported = True
    except ImportError:
        error()

from pysweepme.EmptyDeviceClass import EmptyDevice


class Device(EmptyDevice):

    def __init__(self):

        super().__init__()
        
        self.shortname = "OceanDirect"
        
        self.variables = ["Wavelength", "Intensity", "Integration time"]
        self.plottype = [True, True, True]
        self.savetype = [True, True, True]

        self.calibrationfolder = self.get_folder("CALIBRATIONS")

        self.trigger_modes = {
            "Normal": 0,
            "External Software Trigger": 1,
            "External Synchronization Trigger": 2,
            "Hardware Trigger": 3,
            "Single-Shot Trigger": 4,
        }

        self.unique_ocean_direct_api_identifier = "OceanOptics_OceanDirectAPI"

    def find_ports(self):

        self.check_oceandirect_api()

        # get OceanDirectAPI instance that is shared across multiple driver instances (independent of the model)
        self.od = self.restore_parameter(self.unique_ocean_direct_api_identifier)
        if self.od is None:
            self.od = OceanDirectAPI.OceanDirectAPI()
            self.store_parameter(self.unique_ocean_direct_api_identifier, self.od)

        number_devices = self.od.find_usb_devices()
        # print("Found devices:", number_devices)

        dev_ids = self.od.get_device_ids()

        # print("Device IDs:", dev_ids)

        ports = []
       
        for dev_id in dev_ids:

            spectrometer = self.od.open_device(dev_id)
            serial_number = spectrometer.get_serial_number()
            model = spectrometer.get_model()

            port_serial_number = model + " - " + serial_number
            ports.append(port_serial_number)

            self.unique_spectrometer_identifier = "OceanDirectAPI_spectrometer_" + port_serial_number
            self.store_parameter(self.unique_spectrometer_identifier, spectrometer)

            # spectrometer.close_device()
            # od.close_device(dev_id)

        # print("Ports:", ports)

        if len(ports) == 0:
            self.message_Box(
                "No spectrometer found! Please make sure it is connected and the OceanDirect API is installed.")

        # returns a list of ports
        return ports

    # Remains for later in case calibration will be added
    """
    def get_CalibrationFile_properties(self, port):
        # returns two string
        # 1 file ending
        # 2 string in file_name

        # Example: USB4F05021_040309.IrradCal

        serialno = str(port[str(port).find(":") + 1:-1])

        if serialno == "":
            serialno = "noserialnumber"

        return [".IrradCal", serialno]
    """

    def set_GUIparameter(self):
        gui_parameter = {
            "SweepMode": ["None", "Integration time in s"],
            # "IntegrationTimeAutomatic": False,
            "IntegrationTime": 0.1,
            "Average": 1,
            "Trigger": list(self.trigger_modes.keys()),
            "TriggerDelay": 0.0,
        }

        return gui_parameter

    def get_GUIparameter(self, parameter={}):
        self.integration_time = parameter["IntegrationTime"]
        # self.automatic = parameter.get("IntegrationTimeAutomatic", False)
        self.integration_time_automatic_max = parameter.get("IntegrationTimeMax", 10.0)
        self.sweep_mode = parameter["SweepMode"]
        self.average = parameter["Average"]
        self.port_serial_number = parameter["Port"]
        self.calibration = parameter.get("Calibration", "")
        self.trigger_mode = parameter["Trigger"]
        self.trigger_delay = parameter.get("TriggerDelay", 0.0)
        
        if self.calibration == "" or self.calibration == "None":
            self.units = ["nm", "", "s"]
        else:
            self.units = ["nm", "µJ", "s"]  # TODO: check unit intensity according to calibration

    def connect(self):

        self.check_oceandirect_api()

        if self.port_serial_number == "":
            msg = "Please use 'Find ports' and select a found spectrometer!"
            raise Exception(msg)

        # get OceanDirectAPI instance that is shared across multiple driver instances (independent of the model)
        self.od = self.restore_parameter(self.unique_ocean_direct_api_identifier)
        if self.od is None:
            self.od = OceanDirectAPI.OceanDirectAPI()
            self.store_parameter(self.unique_ocean_direct_api_identifier, self.od)

        # get Spectrometer instance that is shared across multiple driver instances for each serial number
        self.unique_spectrometer_identifier = "OceanDirectAPI_spectrometer_" + self.port_serial_number

        self.spectrometer = self.restore_parameter(self.unique_spectrometer_identifier)
        if self.spectrometer is None:
            serial_number = self.port_serial_number.split(" - ")[1]
            # print("serial_number: ", serial_number)
            self.spectrometer = self.od.from_serial_number(serial_number)
            # self.spectrometer.open_device()
            self.store_parameter(self.unique_spectrometer_identifier, self.spectrometer)

    def disconnect(self):
        pass
        
    def initialize(self):

        # Print/Logs some details about the spectrometer
        # self.spectrometer.details()

        self.dark_pixel_indices = self.spectrometer.get_electric_dark_pixel_indices()
        # print("dark: ", self.dark_pixel_indices)

        self.integration_time_min = self.spectrometer.get_minimum_integration_time()
        self.integration_time_max = self.spectrometer.get_maximum_integration_time()

        self.acquisition_delay_min = self.spectrometer.get_acquisition_delay_minimum()
        self.acquisition_delay_max = self.spectrometer.get_acquisition_delay_maximum()

        # Integration time
        integration_time = float(self.integration_time)
        self.set_integration_time(integration_time)

        # Averages
        self.average = int(self.average)
        self.spectrometer.set_scans_to_average(self.average)

        # Trigger
        index = self.trigger_modes[self.trigger_mode]
        self.spectrometer.set_trigger_mode(index)

        # Acquisition delay
        self.trigger_delay = float(self.trigger_delay)
        self.set_acquisition_delay(self.trigger_delay)

        # Electric dark correction
        # self.spectrometer.set_electric_dark_correction_usage(False)

        # Wavelengths
        self.wavelengths = self.get_wavelengths()

        # Remains for later in case calibration will be added
        """
        if self.calibration != "" and self.calibration != "None":
            calibration_file = self.calibrationfolder + os.sep + self.calibration

            if not calibration_file.endswith(".IrradCal"):
                calibration_file += ".IrradCal"
            
            IrradCal=np.loadtxt(calibration_file, skiprows=9)  # Ocean Optics file
            self.calibration_array = IrradCal[:,1]
        else:
            self.calibration_array = np.ones(self.spectrometer.pixels)
       
        if self.spectrometer.pixels != len(self.calibration_array):
            self.stopMeasurement = "Check your calibration file. Number of pixels is not equal to the pixels your spectrometer has."
        """

    def apply(self):
    
        if self.sweep_mode.startswith("Integration time"):

            integration_time = float(self.value)
            self.set_integration_time(integration_time)

    def measure(self):

        self.intensities = self.get_intensities()

    def call(self):

        return [self.wavelengths, self.intensities, self.integration_time]


    def check_oceandirect_api(self):

        if not api_path_defined:
            msg = "Path to OceanDirect API not found. Please install OceanDirect API before using the driver."
            raise Exception(msg)

        if not od_api_imported:
            msg = "Unable to import OceanDirect API. Please install OceanDirect API before using the driver."
            raise Exception(msg)

    def get_wavelengths(self):
        """ Returns list of wavelenghts after removing dark pixels """

        wavelengths = self.spectrometer.get_wavelengths()
        wavelengths = np.delete(wavelengths, self.dark_pixel_indices)

        return wavelengths

    def get_intensities(self):
        """ Returns intensity values after removing dark pixels """

        # alternatives
        # intensities = self.spectrometer.get_nonlinearity_corrected_spectrum1()
        # intensities = self.spectrometer.get_nonlinearity_corrected_spectrum2()

        intensities = self.spectrometer.get_formatted_spectrum()
        intensities = np.delete(intensities, self.dark_pixel_indices)

        return intensities

    def get_integration_time(self):
        """ Returns integration time in s """
        return self.spectrometer.get_integration_time() / 1e6  # from µs to s
        
    def set_integration_time(self, integration_time):
        """ Sets integration time in s and checks for min/max limits """

        integration_time = float(integration_time) * 1e6  # from s to µs

        if integration_time < self.integration_time_min:
            integration_time = self.integration_time_min
            debug("Integration time below minimum integration time.")
        elif integration_time > self.integration_time_max:
            integration_time = self.integration_time_max
            debug("Integration time above maximum integration time.")

        self.spectrometer.set_integration_time(int(integration_time))

    def set_acquisition_delay(self, acquisition_delay):
        """ Sets acquisition delay in s and checks for min/max limits """

        acquisition_delay = float(acquisition_delay) * 1e6  # from s to µs

        if acquisition_delay < self.acquisition_delay_min:
            acquisition_delay = self.acquisition_delay_min
            debug("Acquisition_delay below minimum acquisition_delay.")
        elif acquisition_delay > self.acquisition_delay_max:
            acquisition_delay = self.acquisition_delay_max
            debug("Acquisition_delay above maximum acquisition_delay.")

        self.spectrometer.set_acquisition_delay(int(acquisition_delay))
