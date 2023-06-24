
import ctypes # to communicate with the LotHW.dll library
import time   # to wait on each scan wavelength
import struct # to check if we're on 64 bit or 32 bit python

import lotcontrol.lot_errors as lot_errors
import lotcontrol.lot_tokens as lot_tokens

#verbosity 
ERROR = 1
WARNING = 2
INFO = 3
VERBOSE = 4

class LotControl():
    """ medium level Monochromator API for LOT monochromators
        compatible with 32 and 64 bit python 2 and 3, uses LotHW.dll.

        Simplest usage: 
        >>> m = LotControl(configuration_filepath_string)
        >>> m(400) # sends monochromator(s) to 400nm, 
        >>>      #then waits 0.5s (the default). Returns when done.
        >>> m(400,10) # sends monochromator to 400nm, then waits 10s.
    """

    error_strings = [None, "ERROR:", "Warning: ", "info: "]
    dllpath32_default = r"C:\Program Files (x86)\LOT\dlls\LotHW_stdcall.dll"
    dllpath64_default = r"C:\Program Files (x86)\LOT\dlls\LotHW64.dll"
    default_is_cdll = False

    def __init__(self, configuration_file, dllpath=None, cdll=default_is_cdll, 
        connect = True, initialise = True, verbosity=ERROR):
        """ initialise, loading the library at dllpath (or defaults). If this 
            library is compiled using the cdll calling convention, set
            cdll to True. Optionally you can suppress connecting to the 
            monochromators and initialising them with the connect and 
            initialise variables respectively.
        """
        self.verbosity = verbosity
        self.open = False
        if dllpath is None:
            python_architecture = struct.calcsize("P")*8
            assert python_architecture in (32,64), "This version of python is a strange architecure."
            if python_architecture == 64:
                self.__verbose_print ("This is a 64 bit version of python", INFO)
                dllpath = self.dllpath64_default
            else:
                self.__verbose_print ("This is a 32 bit version of python", INFO)
                dllpath = self.dllpath32_default
        self.__load_library(dllpath, cdll)

        self.configuration_file = configuration_file

        if connect:
            self.connect()

        if initialise:
            self.initialise()

    def __call__(self, wavelength, sleeptime=0.5):
        """ convenience alias of select_wavelength(...)
        """
        self.select_wavelength(wavelength, post_move_sleep_time=sleeptime)

    def __del__(self):
        self.__verbose_print("deleting LotControl instance", VERBOSE)
        if self.open:
            self.close()


    def __check_result(self, result, buffer=None, buffer_failure_value=None):
        """ makes sure that the last result returned zero, and if not finds
            and raises the appropriate exception. Optionally can make sure that
            the value of a buffer does not correspond to an error value.
        """
        self.last_result = result
        if buffer is not None and buffer.value == buffer_failure_value:
            raise ValueError("The buffer came back with an unexpected value ["+str(buffer.value)+"]")
        if result != 0:
            raise lot_errors.lookup_exception(result)
        return

    def __verbose_print(self, string, level=1):
        """ conditionally prints a string if the level is lower than the 
            class's verbosity level. 
        """
        if self.verbosity>=level:
            if type(level) == int and 0<level<len(self.error_strings):
                preface = self.error_strings[level]
            else:
                preface = ""
            print (preface+str(string))

    def __ok(self):
        """ Convenience function that prints "ok" at the highest known 
            verbosity
        """
        self.__verbose_print("ok\n", VERBOSE)

    def __load_library(self, dllpath, cdll):
        try:
            if cdll:
                self.dll = ctypes.CDLL(dllpath)
            else:
                self.dll = ctypes.WinDLL(dllpath)
        except:
            print ("Unable to load library.")
            raise

    @staticmethod
    def __clean_list(list):
        """ separates the comma separated string returned by the dll
            into multiple substrings
        """
        return list.strip(',').split(',')

    @staticmethod
    def __compound_index(iterable_index):
        """ turn an index consisting of several elements into a single
            integer by treating each element from the back as a successive
            power of ten and adding the result.
        """
        if type(iterable_index) == int:
            return iterable_index
        total = 0
        for index_power, index_value in enumerate(iterable_index[::-1]):
            total += index_value * 10**index_power
        return total


    def __retrieve_buffer(self, function,max_length=128, buffer_failure_value = None, args=tuple()):
        """ calls a function with a buffer, interprets the result
        """
        buffer = ctypes.create_string_buffer(128)
        self.__check_result(function(buffer, *args), buffer, buffer_failure_value)
        return buffer.value.decode("ascii")

    def version(self):
        """ Retrieve LotHW library version string
        """
        self.__verbose_print("Retrieving LotHW version number:", INFO)
        result = self.__retrieve_buffer(self.dll.LOT_version, buffer_failure_value="")
        self.__verbose_print(result, INFO)
        self.__ok()
        return result

    def get_comms_list(self):
        """ Retrieve configuration comms list.
        """
        self.__verbose_print("Retrieving LotHW comms list:", INFO)
        result = self.__retrieve_buffer(self.dll.LOT_get_comms_list, buffer_failure_value="")
        self.__verbose_print(result, INFO)
        self.__ok()
        return self.__clean_list(result)

    def get_hardware_list(self):
        """ Retrieve configuration hardware list.
        """
        self.__verbose_print("Retrieving LotHW hardware list:", INFO)
        result = self.__retrieve_buffer(self.dll.LOT_get_hardware_list, buffer_failure_value="")
        self.__verbose_print(result, INFO)
        self.__ok()
        return self.__clean_list(result)

    def get_hardware_type(self, id_string):
        """ Retrieve hardware type (integer).
        """
        id_bytes = id_string.encode("ascii")  
        id_char_p = ctypes.c_char_p(id_bytes)
        result_integer = ctypes.c_int()

        self.__verbose_print("Retrieving LotHW hardware type for "+id_string, INFO)
        self.__check_result(self.dll.LOT_get_hardware_type(id_char_p, ctypes.byref(result_integer)))
        result = lot_tokens.lookup_token(result_integer.value)
        self.__verbose_print(result, INFO)
        self.__ok()
        return result

    def initialise(self):
        """ Initialise monochromators
        """
        self.__verbose_print("Initialising Monochromators", INFO)
        self.__check_result(self.dll.LOT_initialise())
        self.__ok()

    def select_wavelength(self, wavelength, post_move_sleep_time=None):
        """ Move monochromators to certain wavelength, optionally waiting 
            post_move_sleep_time seconds after a successful move.
        """
        wavelength_c_double = ctypes.c_double(wavelength) 
        self.__check_result(self.dll.LOT_select_wavelength(wavelength_c_double))
        self.__verbose_print("Moving to "+str(wavelength)+" nm...", VERBOSE)
        if not (post_move_sleep_time is None):
            self.__verbose_print("sleeping...", VERBOSE)
            time.sleep(post_move_sleep_time) # wait 0.5 seconds for the sensors to settle

        self.__ok()

    def connect(self):
        """ load configuration file and open connections to the monochromators
            but do not initialise them yet.
        """
        self.__verbose_print("Connecting to monochromators using "+self.configuration_file, INFO)
        configfile_bytes = self.configuration_file.encode("ascii")   # convert the string from maybe unicode to bytes in case we're on python3
        configfile_chars = ctypes.c_char_p(configfile_bytes)# create a pointer to that string of bytes that the library can write to.
        if self.open:
            self.__verbose_print("already connected", WARNING)
            self.close()
        self.__check_result(self.dll.LOT_build_system_model(configfile_chars))
        self.open = True
        self.__ok()

    def close(self):
        """ close the connection to the monochromators.
        """
        self.__verbose_print("Closing connection", INFO)
        if not self.open:
            self.__verbose_print("cannot close connection: already closed", WARNING)
            return
        self.__check_result(self.dll.LOT_close())
        self.open=False
        self.__ok()

    def get(self, hardware_id, token, index=0):
        """ Retrieve hardware setting for a hardware_id and token (strings) 
            and, if required, an index (integer)
        """
        id_bytes = hardware_id.encode("ascii")
        id_char_p = ctypes.c_char_p(id_bytes)
        value = ctypes.c_double(0)
        index = self.__compound_index(index)
        self.__verbose_print("Retrieving hardware setting "+str(token)+" for "+hardware_id+" "+str(index), INFO)
        if type(token)!=int:
            token = lot_tokens.lookup_token(token)
        self.__check_result(self.dll.LOT_get(id_char_p, token, index, ctypes.byref(value)))
        result = value.value
        self.__verbose_print(result, INFO)
        self.__ok()
        return result

    def get_str(self, hardware_id, token, index=0):
        """ Retrieve hardware setting STRING for a hardware_id and token
            (strings) and, if required, an index (integer)
        """
        id_bytes = hardware_id.encode("ascii")
        id_char_p = ctypes.c_char_p(id_bytes)
        return_str = ctypes.create_string_buffer(128)
        index = self.__compound_index(index)
        self.__verbose_print("Retrieving hardware string "+str(token)+" for "+hardware_id+" "+str(index), INFO)
        if type(token)!=int:
            token = lot_tokens.lookup_token(token)
        self.__check_result(self.dll.LOT_get_str(id_char_p, token, index, return_str))
        result = return_str.value.decode("ascii")
        self.__verbose_print(result, INFO)
        self.__ok()
        return result

    def set(self, hardware_id, token, value, index=0):
        """ Set hardware setting for a hardware_id and token (strings)
            and, if required, an index (integer)
        """
        id_bytes = hardware_id.encode("ascii")
        id_char_p = ctypes.c_char_p(id_bytes)
        value_d = ctypes.c_double(value)
        index = self.__compound_index(index)
        self.__verbose_print("Setting hardware setting"+str(token)+" for "+hardware_id+" "+str(index) + " to "+str(value), INFO)
        if type(token)!=int:
            token = lot_tokens.lookup_token(token)
        self.__check_result(self.dll.LOT_set(id_char_p, ctypes.c_int(token), ctypes.c_int(index), ctypes.byref(value_d)))
        self.__ok()
        return 

    def set_str(self, hardware_id, token, value, index=0):
        """ Set hardware string setting for a hardware_id and token (strings)
            and, if required, an index (integer)
        """
        id_bytes = hardware_id.encode("ascii")
        id_char_p = ctypes.c_char_p(id_bytes)
        value_bytes = value.encode("ascii")
        value_c_str = ctypes.c_char_p(value_bytes)
        index = self.__compound_index(index)
        self.__verbose_print("Setting hardware string "+str(token)+" for "+hardware_id+" "+str(index) + " to "+value, INFO)
        if type(token)!=int:
            token = lot_tokens.lookup_token(token)
        self.__check_result(self.dll.LOT_set_str(id_char_p, ctypes.c_int(token), index, value_c_str))
        self.__ok()
        return

    def recalibrate(self, mono_id, index, reported_wavelength, actual_wavelength):
        """ calculate a new calibration value (Zord) that can later 
            be allied with the set function.
        """        
        mono_id_bytes = mono_id.encode("ascii")
        mono_id_c_char_p = ctypes.c_char_p(mono_id_bytes)
        index_c = ctypes.c_int(self.__compound_index(index))
        wavelength_c = ctypes.c_double(reported_wavelength)
        correct_wavelength_c = ctypes.c_double(actual_wavelength)
        old_zord = ctypes.c_int(0)
        new_zord = ctypes.c_int(0)

        old_zord_pointer = ctypes.pointer(old_zord)
        new_zord_pointer = ctypes.pointer(new_zord)

        self.__check_result(self.dll.LOT_recalibrate(mono_id_c_char_p, index_c, wavelength_c, correct_wavelength_c, old_zord_pointer, new_zord_pointer))
        return (old_zord.value, new_zord.value)

    def get_last_error(self):
        """ Retrieves the last error that occured in the library as a python
            exception.
        """ 
        error_code = ctypes.c_int(0)
        address = ctypes.c_long(0)
        error_message_buffer = ctypes.create_string_buffer(128)
        self.__verbose_print("Retrieving last error", INFO)
        self.__check_result(self.dll.LOT_get_last_error(ctypes.byref(error_code), error_message_buffer, ctypes.byref(address)))
        message = error_message_buffer.value.decode("ascii")

        self.__verbose_print("Error Code: "+str(error_code.value)+" Message: "+message+" address: "+str(address.value), INFO)
        error_type = lot_errors.lookup_exception(error_code.value)(message+'(address '+str(address.value)+')')
        error_type.address = address.value
        self.__ok()
        return error_type

    def get_mono_items(self, mono_id):
        """ retrieve the available hardware objects that belong to the 
            monochromator.
        """
        mono_id_bytes = mono_id.encode("ascii")
        mono_id_c_str = ctypes.c_char_p(mono_id_bytes)
        list_buffer = ctypes.create_string_buffer(128)
        
        self.__verbose_print("Retrieving mono items for "+mono_id, INFO)
        self.__check_result(self.dll.LOT_get_mono_items(mono_id_c_str, list_buffer))
        message = list_buffer.value.decode("ascii")
        self.__verbose_print("Result: "+ message, INFO)
        self.__ok()

        return self.__clean_list(message)

    def save_setup(self):
        """ save changes to the setup file we opened at the beginning.
        """
        self.__verbose_print("Saving setup", INFO)
        self.__check_result(self.dll.LOT_save_setup())
        self.__ok()

    def set_c_group(self, group):
        """ Select a group in the system model.
        """
        self.__verbose_print("Setting c group to "+str(group), INFO)
        self.__check_result(self.dll.LOT_set_c_group(group))

    def get_hardware(self):
        hardware_names = self.get_hardware_list()
        hardware_types = [self.get_hardware_type(hw) for hw in hardware_names]

        hw = {}

        for hwname, hwtype in zip(hardware_names, hardware_types):
            hw[hwname] = {"type":hwtype}
            if hwtype == "lotMono":
                items = self.get_mono_items(hwname)
                hw[hwname]["mono_items"] = {}
                for itemname in items:
                    itemtype = self.get_hardware_type(itemname)
                    hw[hwname]["mono_items"][itemname] = {"type": itemtype}

        return hw

    def info(self):
        """ print some information about the monochromators.
        """
        hw = self.get_hardware()
        self.recursive_print_dict(hw)

        #self.get("MonochromatorCurrentWL")

    @staticmethod
    def recursive_print_dict(d, depth=0):
        for key in list(sorted(d.keys()))[::-1]:
            value = d[key]
            if type(value) == dict:
                print ("| "*depth+str(key)+":")
                LotControl.recursive_print_dict(value, depth+1)
            else:
                print ("| "*depth+key+": "+value)
        if depth == 0: print ()