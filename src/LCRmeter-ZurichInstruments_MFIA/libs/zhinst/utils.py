# -*- coding: utf-8 -*-
"""
Zurich Instruments LabOne Python API Utility Functions.

This module provides basic utility functions for:

- Creating an API session by connecting to an appropriate Data Server.

- Detecting devices.

- Loading and saving device settings.

- Loading data saved by either the Zurich Instruments LabOne User Interface or
  ziControl into Python as numpy structured arrays.
"""

# Copyright 2018 Zurich Instruments AG.

from __future__ import print_function
import re
import warnings
import os
import time
try:
    # load_labone_mat() requires scipy.io.loadmat()
    import scipy.io
except ImportError as e:
    # No fallback. No complaints upon importing zhinst.utils, handle/raise
    # exception when the function load_labone_mat() is called.
    __SCIPY_IMPORT_ERROR = e
import numpy as np
import zhinst.ziPython


def create_api_session(device_serial, maximum_supported_apilevel, required_devtype=r".*", required_options=None,
                       required_err_msg=''):
    """Create an API session for the specified device.

    Args:

      device_serial (str): A string specifying the device serial number. For
        example, 'uhf-dev2123' or 'dev2123'.

      maximum_supported_apilevel (int): The maximum API Level that is supported
        by the code where the returned API session will be used. The maximum API
        Level you may use is defined by the device class. HF2 only supports API
        Level 1 and other devices support API Level 5. You should try to use the
        maximum level possible to enable extended API features.

     required_devtype (str): The required device type, e.g., 'HF2LI' or
       'MFLI'. This is given by the value of the device node
       '/devX/features/devtype' or the 'devicetype' discovery property. Raise an
       exception if the specified device_serial's devtype does not match the
       `required_devtype`.

     required_options (list of str|None): The required device option set. E.g.,
       ['MF', 'PID'].  This is given by the value of the device node
       '/devX/features/options' or the 'options' discovery property. Raise an
       exception if the specified device_serial's option set does contain the
       `required_options`.

     required_error_msg (str) : An additional error message to print if either
       the device specified by the `device_serial` is not the `required_devtype`
       or does not have the `required_options`.

    Returns:

      daq (ziDAQServer): An instance of the ziPython.ziDAQServer class
        (representing an API session connected to a Data Server).

      device (str): The device's ID, this is the string that specifies the
        device's node branch in the data server's node tree.


      props (dict): The device's discovery properties as returned by the
        ziDiscovery get() method.

    """

    # Create an instance of the ziDiscovery class.
    d = zhinst.ziPython.ziDiscovery()

    # Determine the device identifier from it's ID.
    device_id = d.find(device_serial).lower()

    # Get the device's connectivity properties.
    props = d.get(device_id)
    print("Discovered device `", device_id, "`: ", props['devicetype'], " with options ",
          ', '.join(props['options']), ".", sep="")

    if not props['discoverable']:
        raise RuntimeError("The specified device `{}` is not discoverable from the API. Please ensure the device "
                           "is powered-on and visible using the LabOne User Interface.".format(device_serial))

    if not re.search(required_devtype, props['devicetype']):
        raise Exception("Required device type not satisfied. Device type `{}` does not match the required device type:"
                        "`{}`. {}".format(props['devicetype'], required_devtype, required_err_msg))

    if required_options:
        assert isinstance(required_options, list), "The keyword argument must be a list of string each entry" \
            "specifying a device option."

        def regex_option_diff(required_options, device_options):
            """Return the options in required_options (as regex) that are not found in the
            device_options list.

            """
            missing_options = []
            for option in required_options:
                if not re.search(option, '/'.join(device_options)):
                    missing_options += required_options
            return missing_options
        if 'AWG' in props['devicetype']:
            # Note(16.12 for UHFAWG, 18.05 for HDAWG): This maintains backwards compatibility of this function.
            installed_options = props['options'] + ['AWG']
        else:
            installed_options = props['options']
        missing_options = regex_option_diff(required_options, installed_options)
        if missing_options:
            raise Exception("Required option set not satisfied. The specified device `{}` has the `{}` options "
                            "installed but is missing the required options `{}`. {}".
                            format(device_id, props['options'], missing_options, required_err_msg))

    # The maximum API level supported by the device class, e.g., MF.
    apilevel_device = props['apilevel']

    # Ensure that we connect on an compatible API Level (from where create_api_session() was called).
    apilevel = min(apilevel_device, maximum_supported_apilevel)
    # See the LabOne Programming Manual for an explanation of API levels.

    # Create a connection to a Zurich Instruments Data Server (an API session)
    # using the device's default connectivity properties.
    print("Creating an API session for device `", device_id, "` on `", props['serveraddress'], "`, `",
          props['serverport'], "` with apilevel `", apilevel, "`.", sep="")

    daq = zhinst.ziPython.ziDAQServer(props['serveraddress'], props['serverport'], apilevel)

    if not props['connected']:
        print("Will try to connect device `", props['deviceid'], "` on interface ", props['interfaces'][0], ".", sep='')
        daq.connectDevice(props['deviceid'], props['interfaces'][0])

    return (daq, device_id, props)


def api_server_version_check(daq):
    """
    Issue a warning and return False if the release version of the API used in the session (daq) does not have the same
    release version as the Data Server (that the API is connected to). If the versions match return True.

    Args:

      daq (ziDAQServer): An instance of the ziPython.ziDAQServer class
        (representing an API session connected to a Data Server).

    Returns:

      Bool: Returns True if the versions of API and Data Server match, otherwise returns False.
    """
    api_version = daq.version()
    api_revision = daq.revision()
    server_version = daq.getString('/zi/about/version')
    server_revision = daq.getInt('/zi/about/revision')
    if api_version != server_version:
        message = ("There is a mismatch between the versions of the API and Data Server. The API reports version `{}' "
                   "(revision: {}) whilst the Data Server has version `{}' (revision {}). See the ``Compatibility'' "
                   "Section in the LabOne Programming Manual for more information.".format(
                       api_version, api_revision, server_version, server_revision))
        warnings.warn(message)
        return False
    return True


def default_output_mixer_channel(discovery_props, output_channel=0):
    """Return an instrument's default output mixer channel based on the specified
    `devicetype` and `options` discovery properties and the hardware output
    channel.

    This utility function is used by the ziPython examples and returns a node
    available under the /devX/sigouts/0/{amplitudes,enables}/ branches.

    Args:

      discovery_props (dict): A device's discovery properties as returned by
        ziDiscovery's get() method.

      output_channel (int, optional): The zero-based index of the hardware
        output channel for which to return an output mixer channel.

    Returns:

      output_mixer_channel (int): The zero-based index of an available signal
      output mixer channel.

    Raises:

      Exception: If an invalid signal input index was provided.

    """

    # The logic below assumes the device type is one of the following.
    assert discovery_props['devicetype'] in ['HF2IS', 'HF2LI', 'UHFLI', 'UHFAWG', 'UHFQA', 'MFIA', 'MFLI'], \
        "Unknown device type: {}.".format(discovery_props['devicetype'])

    if re.match(r'UHF(LI|AWG)', discovery_props['devicetype']) and ('MF' not in discovery_props['options']):
        if output_channel == 0:
            return 3
        if output_channel == 1:
            return 7
        raise Exception("Invalid output channel `{}`, UHF Instruments have two signal "
                        "ouput channels (0, 1).".format(output_channel))

    if re.match(r'UHFQA', discovery_props['devicetype']):
        if output_channel == 0:
            return 0
        if output_channel == 1:
            return 1
        raise Exception("Invalid output channel `{}`, UHF Instruments have two signal "
                        "ouput channels (0, 1).".format(output_channel))

    if re.match(r'HF2LI', discovery_props['devicetype']) and ('MF' not in discovery_props['options']):
        if output_channel == 0:
            return 6
        if output_channel == 1:
            return 7
        raise Exception("Invalid output channel `{}`, HF2 Instruments have two signal output"
                        "channels (0, 1).".format(output_channel))

    if re.match(r'(MFLI|MFIA)', discovery_props['devicetype']) and ('MD' not in discovery_props['options']):
        if output_channel == 0:
            return 1
        raise Exception("Invalid output channel `{}`, MF Instruments have one signal output channel (0)."
                        .format(output_channel))
    return 0


def autoDetect(daq, exclude=None):
    """
    Return a string containing the first device ID (not in the exclude list)
    that is attached to the Data Server connected via daq, an instance of the
    ziPython.ziDAQServer class.

    Args:

      daq (ziDAQServer): An instance of the ziPython.ziDAQServer class
        (representing an API session connected to a Data Server).

      exclude (list of str, optional): A list of strings specifying devices to
        exclude. autoDetect() will not return the name of a device in this
        list.

    Returns:

      A string specifying the first device ID not in exclude.

    Raises:

      RunTimeError: If no device was found.
      RunTimeError: If daq is not an instance of ziPython.ziDAQServer.

    Example:

      zhinst.utils
      daq = zhinst.utils.autoConnect()
      device = zhinst.utils.autoDetect(daq)
    """
    if not isinstance(daq, zhinst.ziPython.ziDAQServer):
        raise RuntimeError("First argument must be an instance of ziPython.ziDAQServer")
    nodes = daq.listNodes('/', 0)
    devs = [node for node in nodes if re.match("dev*", node, re.IGNORECASE)]
    if exclude is None:
        exclude = []
    if not isinstance(exclude, list):
        exclude = [exclude]
    exclude = [x.lower() for x in exclude]
    devs = [dev for dev in devs if dev.lower() not in exclude]
    if not devs:
        raise RuntimeError("No Device found. Make sure that the device is connected to the host via USB or Ethernet "
                           "and that it is switched on. It may also be necessary to issue a connectDevice command.")
    # Found at least one device -> selection valid.
    # Select the first one
    device = devs[0].lower()
    print("autoDetect selected the device", device, "for the measurement.")
    return device


def devices(daq):
    """
    Return a list of strings containing the device IDs that are attached to the
    Data Server connected via daq, an instance of the ziPython.ziDAQServer
    class. Returns an empty list if no devices are found.

    Args:

      daq (ziDAQServer): An instance of the ziPython.ziDAQServer class
        (representing an API session connected to a Data Server).

    Returns:

      A list of strings of connected device IDs. The list is empty if no devices
      are detected.

    Raises:

      RunTimeError: If daq is not an instance of ziPython.ziDAQServer.

    Example:

      import zhinst.utils
      daq = zhinst.utils.autoConnect()  # autoConnect not supported for MFLI devices
      device = zhinst.utils.autoDetect(daq)

    """
    if not isinstance(daq, zhinst.ziPython.ziDAQServer):
        raise RuntimeError("First argument must be an instance of ziPython.ziDAQServer")
    nodes = daq.listNodes('/', 0)
    devs = [node for node in nodes if re.match("dev*", node, re.IGNORECASE)]
    devs = list(x.lower() for x in list(devs))
    return devs


def autoConnect(default_port=None, api_level=None):
    """
    Try to connect to a Zurich Instruments Data Server with an attached
    available UHF or HF2 device.

    Important: autoConnect() does not support MFLI devices.

    Args:

      default_port (int, optional): The default port to use when connecting to
        the Data Server (specify 8005 for the HF2 Data Server and 8004 for the
        UHF Data Server).

      api_level (int, optional): The API level to use, either 1, 4 or 5. HF2 only
        supports Level 1, Level 5 is recommended for UHF and MFLI devices.

    Returns:

      ziDAQServer: An instance of the ziPython.ziDAQServer class that is used
        for communication to the Data Server.

    Raises:

      RunTimeError: If no running Data Server is found or no device is found
        that is attached to a Data Server.x

    If default_port is not specified (=None) then first try to connect to a HF2,
    if no server devices are found then try to connect to an UHF. This behaviour
    is useful for the API examples. If we cannot connect to a server and/or
    detect a connected device raise a RunTimeError.

    If default_port is 8004 try to connect to a UHF; if it is 8005 try to
    connect to an HF2. If no server and device is detected on this port raise
    a RunTimeError.
    """
    if default_port is None:
        default_port = 8005
        secondary_port = 8004
    elif default_port in [8004, 8005]:
        # If a port is specified, then don't try to connect to a secondary port
        secondary_port = None
    else:
        error_msg = "autoConnect(): input argument default_port (%d) must be either 8004 or 8005." % default_port
        raise RuntimeError(error_msg)
    if api_level is None:
        # Note: level 1 used by default for both UHF and HF2, otherwise
        # backwards compatibility not maintained.
        api_level = 1

    port_device = {8005: 'HF2', 8004: 'UHFLI or MFLI'}
    port_valid_api_levels = {8005: [1], 8004: [1, 4, 5, 6]}
    port_exception = {}
    try:
        assert api_level in port_valid_api_levels[default_port], \
            "Invalid API level (`%d`) specified for port %d (%s devices), valid API Levels: %s." \
            % (api_level, default_port, port_device[default_port], port_valid_api_levels[default_port])
        daq = zhinst.ziPython.ziDAQServer('localhost', default_port, api_level)
        devs = devices(daq)
        assert devs, "Successfully connected to the server on port `%d`, API level `%d` but devices() \
returned an empty list: No devices are connected to this PC." % (default_port, api_level)
        # We have a server running and a device, we're done
        print("autoConnect connected to a server on port", default_port, "using API level", api_level, ".")
        return daq
    except (RuntimeError, AssertionError) as e:
        port_exception[default_port] = e

    error_msg_no_dev = "Please ensure that the correct Zurich Instruments server is running for your device and that \
your device is connected to the server (try connecting first via the User Interface)."

    # If default_port is specified as an input argument, then secondary_port is
    # None. If we got here we had no success on default_port: raise an error.
    if secondary_port is None:
        error_msg = "autoConnect(): failed to connect to a running server or failed to find a device connected to the \
server on port %d (used for %s devices). %s The exception was: %s" \
            % (default_port, port_device[default_port], error_msg_no_dev, port_exception[default_port])
        raise RuntimeError(error_msg)

    try:
        assert api_level in port_valid_api_levels[secondary_port], \
            "Invalid API level specified for port %d (%s devices), valid API Levels: %s." \
            % (secondary_port, port_device[secondary_port], port_valid_api_levels[secondary_port])
        daq = zhinst.ziPython.ziDAQServer('localhost', secondary_port, api_level)
        devs = devices(daq)
        assert devs, "Successfully connected to the server on port `%d`, API level `%d` but devices() \
returned an empty list: No devices are connected to this PC." % (secondary_port, api_level)
        # We have a server running and a device, we're done
        print("autoConnect connected to a server on port", default_port, "using API level", api_level, ".")
        return daq
    except (RuntimeError, AssertionError):
        port_exception[secondary_port] = e

    # If we got here we failed to connect to a device. Raise a RunTimeError.
    error_msg = "autoConnect(): failed to connect to a running server or failed to find a device connected to the \
server. %s The exception on port %d (used for %s devices) was: %s The exception on port %d (used for %s devices) \
was: %s" % (error_msg_no_dev, default_port, port_device[default_port], port_exception[default_port],
            secondary_port, port_device[secondary_port], port_exception[secondary_port])
    raise RuntimeError(error_msg)


def sigin_autorange(daq, device, in_channel):
    """Perform an automatic adjustment of the signal input range based on the
    measured input signal. This utility function starts the functionality
    implemented in the device's firmware and waits until it has completed. The
    range is set by the firmware based on the measured input signal's amplitude
    measured over approximately 100 ms.

    Requirements:

      A devtype that supports autorange functionality on the firmware level,
      e.g., UHFLI, MFLI, MFIA.

    Arguments:

      daq (instance of ziDAQServer): A ziPython API session.

      device (str): The device ID on which to perform the signal input autorange.

      in_channel (int): The index of the signal input channel to autorange.

    Raises:

      AssertionError: If the functionality is not supported by the device or an
        invalid in_channel was specified.

      RunTimeError: If autorange functionality does not complete within the
        timeout.

    Example:

      import zhinst.utils
      device_serial = 'dev2006'
      (daq, _, _) = zhinst.utils.create_api_session(device_serial, 5)
      input_channel = 0
      zhinst.utils.sigin_autorange(daq, device_serial, input_channel)

    """
    autorange_path = '/{}/sigins/{}/autorange'.format(device, in_channel)
    assert any(re.match(autorange_path, node, re.IGNORECASE) for node in daq.listNodes(autorange_path, 7)), \
        "The signal input autorange node `{}` was not returned by listNodes(). ".format(autorange_path) + \
        "Please check that: The device supports autorange functionality (HF2 does not), the device " + \
        "`{}` is connected to the Data Server and that the specified input channel `{}` is correct.".format(
            device, in_channel)
    daq.setInt(autorange_path, 1)
    daq.sync()  # Ensure the value has taken effect on device before continuing
    # The node /device/sigins/in_channel/autorange has the value of 1 until an
    # appropriate range has been configured by the device, wait until the
    # autorange routing on the device has finished.
    t0 = time.time()
    timeout = 30
    while daq.getInt(autorange_path):
        time.sleep(0.010)
        if time.time() - t0 > timeout:
            raise RuntimeError("Signal input autorange failed to complete after after %.f seconds." % timeout)
    return daq.getDouble('/{}/sigins/{}/range'.format(device, in_channel))


def get_default_settings_path(daq):
    """
    Return the default path used for settings by the ziDeviceSettings module.

    Arguments:

      daq (instance of ziDAQServer): A ziPython API session.

    Returns:

      settings_path (str): The default ziDeviceSettings path.
    """
    device_settings = daq.deviceSettings()
    settings_path = device_settings.get('path')['path'][0]
    device_settings.clear()
    return settings_path


def load_settings(daq, device, filename):
    """
    Load a LabOne settings file to the specified device. This function is
    synchronous; it will block until loading the settings has finished.

    Arguments:

      daq (instance of ziDAQServer): A ziPython API session.

      device (str): The device ID specifying where to load the settings,
      e.g., 'dev123'.

      filename (str): The filename of the xml settings file to load. The
      filename can include a relative or full path.

    Raises:

      RunTimeError: If loading the settings times out.

    Examples:

      import zhinst.utils as utils
      daq = utils.autoConnect()
      dev = utils.autoDetect(daq)

      # Then, e.g., load settings from a file in the current directory:
      utils.load_settings(daq, dev, 'my_settings.xml')
      # Then, e.g., load settings from the default LabOne settings path:
      filename = 'default_ui.xml'
      path = utils.get_default_settings_path(daq)
      utils.load_settings(daq, dev, path + os.sep + filename)
    """
    path, filename = os.path.split(filename)
    filename_noext = os.path.splitext(filename)[0]
    device_settings = daq.deviceSettings()
    device_settings.set('device', device)
    device_settings.set('filename', filename_noext)
    if path:
        device_settings.set('path', path)
    else:
        device_settings.set('path', '.' + os.sep)
    device_settings.set('command', 'load')
    try:
        device_settings.execute()
        t0 = time.time()
        timeout = 60
        while not device_settings.finished():
            time.sleep(0.05)
            if time.time() - t0 > timeout:
                raise RuntimeError("Unable to load device settings after %.f seconds." % timeout)
    finally:
        device_settings.clear()


def save_settings(daq, device, filename):
    """
    Save settings from the specified device to a LabOne settings file. This
    function is synchronous; it will block until saving the settings has
    finished.

    Arguments:

      daq (instance of ziDAQServer): A ziPython API session.

      device (str): The device ID specifying where to load the settings,
      e.g., 'dev123'.

      filename (str): The filename of the LabOne xml settings file. The filename
      can include a relative or full path.

    Raises:

      RunTimeError: If saving the settings times out.

    Examples:

      import zhinst.utils as utils
      daq = utils.autoConnect()
      dev = utils.autoDetect(daq)

      # Then, e.g., save settings to a file in the current directory:
      utils.save_settings(daq, dev, 'my_settings.xml')

      # Then, e.g., save settings to the default LabOne settings path:
      filename = 'my_settings_example.xml'
      path = utils.get_default_settings_path(daq)
      utils.save_settings(daq, dev, path + os.sep + filename)
    """
    path, filename = os.path.split(filename)
    filename_noext = os.path.splitext(filename)[0]
    device_settings = daq.deviceSettings()
    device_settings.set('device', device)
    device_settings.set('filename', filename_noext)
    if path:
        device_settings.set('path', path)
    else:
        device_settings.set('path', '.' + os.sep)
    device_settings.set('command', 'save')
    try:
        device_settings.execute()
        t0 = time.time()
        timeout = 60
        while not device_settings.finished():
            time.sleep(0.05)
            if time.time() - t0 > timeout:
                raise RuntimeError("Unable to save device settings after %.f seconds." % timeout)
    finally:
        device_settings.clear()


# The names correspond to the data in the columns of a CSV file saved by the
# LabOne User Interface. These are the names of demodulator sample fields.
LABONE_DEMOD_NAMES = ('chunk', 'timestamp', 'x', 'y', 'freq', 'phase', 'dio', 'trigger', 'auxin0', 'auxin1')
LABONE_DEMOD_FORMATS = ('u8', 'u8', 'f8', 'f8', 'f8', 'f8', 'u4', 'u4', 'f8', 'f8')
# The dtype to provide when creating a numpy array from LabOne demodulator data
LABONE_DEMOD_DTYPE = list(zip(LABONE_DEMOD_NAMES, LABONE_DEMOD_FORMATS))

# The names correspond to the data in the columns of a CSV file saved by the
# ziControl User Interface. These are the names of demodulator sample fields.
ZICONTROL_NAMES = ('t', 'x', 'y', 'freq', 'dio', 'auxin0', 'auxin1')
ZICONTROL_FORMATS = ('f8', 'f8', 'f8', 'f8', 'u4', 'f8', 'f8')
# The dtype to provide when creating a numpy array from ziControl-saved demodulator data
ZICONTROL_DTYPE = list(zip(ZICONTROL_NAMES, ZICONTROL_FORMATS))


def load_labone_demod_csv(fname, column_names=LABONE_DEMOD_NAMES):
    """
    Load a CSV file containing demodulator samples as saved by the LabOne User
    Interface into a numpy structured array.

    Arguments:

      fname (file or str): The file or filename of the CSV file to load.

      column_names (list or tuple of str, optional): A list (or tuple) of column
      names to load from the CSV file. Default is to load all columns.

    Returns:

      sample (numpy ndarray): A numpy structured array of shape (num_points,)
      whose field names correspond to the column names in the first line of the
      CSV file. num_points is the number of lines in the CSV file - 1.

    Example:

      import zhinst.utils
      sample = zhinst.utils.load_labone_demod_csv('dev2004_demods_0_sample_00000.csv', ('timestamp', 'x', 'y'))
      import matplotlib.pyplot as plt
      import numpy as np
      plt.plot(sample['timestamp'], np.abs(sample['x'] + 1j*sample['y']))
    """
    assert set(column_names).issubset(LABONE_DEMOD_NAMES), \
        'Invalid name in ``column_names``, valid names are: %s' % str(LABONE_DEMOD_NAMES)
    cols = [col for col, dtype in enumerate(LABONE_DEMOD_DTYPE) if dtype[0] in column_names]
    dtype = [dt for dt in LABONE_DEMOD_DTYPE if dt[0] in column_names]
    sample = np.genfromtxt(fname, delimiter=';', dtype=dtype, usecols=cols, skip_header=1)
    return sample


def load_labone_csv(fname):
    """
    Load a CSV file containing generic data as saved by the LabOne User
    Interface into a numpy structured array.

    Arguments:

      filename (str): The filename of the CSV file to load.

    Returns:

      sample (numpy ndarray): A numpy structured array of shape (num_points,)
      whose field names correspond to the column names in the first line of the
      CSV file. num_points is the number of lines in the CSV file - 1.

    Example:

      import zhinst.utils
      # Load the CSV file of PID error data (node: /dev2004/pids/0/error)
      data = zhinst.utils.load_labone_csv('dev2004_pids_0_error_00000.csv')
      import matplotlib.pyplot as plt
      # Plot the error
      plt.plot(data['timestamp'], data['value'])
    """
    data = np.genfromtxt(fname, delimiter=';', dtype=None, names=True)
    return data


def load_labone_mat(filename):
    """
    A wrapper function for loading a MAT file as saved by the LabOne User
    Interface with scipy.io's loadmat() function. This function is included
    mainly to document how to work with the data structure return by
    scipy.io.loadmat().

    Arguments:

      filename (str): the name of the MAT file to load.

    Returns:

      data (dict): a nested dictionary containing the instrument data as
      specified in the LabOne User Interface. The nested structure of ``data``
      corresponds to the path of the data's node in the instrument's node
      hierarchy.

    Further comments:

      The MAT file saved by the LabOne User Interface (UI) is a Matlab V5.0 data
      file. The LabOne UI saves the specified data using native Matlab data
      structures in the same format as are returned by commands in the LabOne
      Matlab API. More specifically, these data structures are nested Matlab
      structs, the nested structure of which correspond to the location of the
      data in the instrument's node hierarchy.

      Matlab structs are returned by scipy.io.loadmat() as dictionaries, the
      name of the struct becomes a key in the dictionary. However, as for all
      objects in MATLAB, structs are in fact arrays of structs, where a single
      struct is an array of shape (1, 1). This means that each (nested)
      dictionary that is returned (corresponding to a node in node hierarchy) is
      loaded by scipy.io.loadmat as a 1-by-1 array and must be indexed as
      such. See the ``Example`` section below.

      For more information please refer to the following link:
      http://docs.scipy.org/doc/scipy/reference/tutorial/io.html#matlab-structs

    Example:

      device = 'dev88'
      # See ``Further explanation`` above for a comment on the indexing:
      timestamp = data[device][0,0]['demods'][0,0]['sample'][0,0]['timestamp'][0]
      x = data[device][0,0]['demods'][0,0]['sample'][0,0]['x'][0]
      y = data[device][0,0]['demods'][0,0]['sample'][0,0]['y'][0]
      import matplotlib.pyplot as plt
      import numpy as np
      plt.plot(timestamp, np.abs(x + 1j*y))

      # If multiple demodulator's are saved, data from the second demodulator,
      # e.g., is accessed as following:
      x = data[device][0,0]['demods'][0,1]['sample'][0,0]['x'][0]
    """
    try:
        data = scipy.io.loadmat(filename)
        return data
    except (NameError, AttributeError):
        print("\n\n *** Please install the ``scipy`` package and verify you can use scipy.io.loadmat() "
              "in order to use zhinst.utils.load_labone_mat. *** \n\n")
        print("Whilst calling import scipy.io an exception was raised with the message: ", str(__SCIPY_IMPORT_ERROR))
        print("Whilst calling scipy.io.loadmat() the following exception was raised:")
        raise
    except Exception as e:
        print("Unexpected exception", str(e))
        raise


def load_zicontrol_csv(filename, column_names=ZICONTROL_NAMES):
    """
    Load a CSV file containing demodulator samples as saved by the ziControl
    User Interface into a numpy structured array.

    Arguments:

      filename (str): The file or filename of the CSV file to load.

      column_names (list or tuple of str, optional): A list (or tuple) of column
      names (demodulator sample field names) to load from the CSV file. Default
      is to load all columns.

    Returns:

      sample (numpy ndarray): A numpy structured array of shape (num_points,)
      whose field names correspond to the field names of a ziControl demodulator
      sample. num_points is the number of lines in the CSV file - 1.

    Example:

      import zhinst.utils
      sample = zhinst.utils.load_labone_csv('Freq1.csv', ('t', 'x', 'y'))
      import matplotlib.plt as plt
      import numpy as np
      plt.plot(sample['t'], np.abs(sample['x'] + 1j*sample['y']))
    """
    assert set(column_names).issubset(ZICONTROL_NAMES), \
        'Invalid name in ``column_names``, valid names are: %s' % str(ZICONTROL_NAMES)
    cols = [col for col, dtype in enumerate(ZICONTROL_DTYPE) if dtype[0] in column_names]
    dtype = [dt for dt in ZICONTROL_DTYPE if dt[0] in column_names]
    sample = np.genfromtxt(filename, delimiter=',', dtype=dtype, usecols=cols)
    return sample


def load_zicontrol_zibin(filename, column_names=ZICONTROL_NAMES):
    """
    Load a ziBin file containing demodulator samples as saved by the ziControl
    User Interface into a numpy structured array. This is for data saved by
    ziControl in binary format.

    Arguments:

      filename (str): The filename of the .ziBin file to load.

      column_names (list or tuple of str, optional): A list (or tuple) of column
      names to load from the CSV file. Default is to load all columns.

    Returns:

      sample (numpy ndarray): A numpy structured array of shape (num_points,)
      whose field names correspond to the field names of a ziControl demodulator
      sample. num_points is the number of sample points saved in the file.

    Further comments:

      Specifying a fewer names in ``column_names`` will not result in a speed-up
      as all data is loaded from the binary file by default.

    Example:

      import zhinst.utils
      sample = zhinst.utils.load_zicontrol_zibin('Freq1.ziBin')
      import matplotlib.plt as plt
      import numpy as np
      plt.plot(sample['t'], np.abs(sample['x'] + 1j*sample['y']))
    """
    assert set(column_names).issubset(ZICONTROL_NAMES), \
        'Invalid name in ``column_names``, valid names are: %s.' % str(ZICONTROL_NAMES)
    sample = np.fromfile(filename, dtype='>f8')
    rem = np.size(sample) % len(ZICONTROL_NAMES)
    assert rem == 0, "Incorrect number of data points in ziBin file, " + \
        "the number of data points must be divisible by the number of demodulator fields."
    n = np.size(sample) / len(ZICONTROL_NAMES)
    sample = np.reshape(sample, (n, len(ZICONTROL_NAMES))).transpose()
    cols = [col for col, dtype in enumerate(ZICONTROL_DTYPE) if dtype[0] in column_names]
    dtype = [dt for dt in ZICONTROL_DTYPE if dt[0] in column_names]
    sample = np.core.records.fromarrays(sample[cols, :], dtype=dtype)
    return sample


def check_for_sampleloss(timestamps):
    """
    Check whether timestamps are equidistantly spaced, it not, it is an
    indication that sampleloss has occurred whilst recording the demodulator
    data.

    This function assumes that the timestamps originate from continuously saved
    demodulator data, during which the demodulator sampling rate was not
    changed.

    Arguments:

      timestamp (numpy array): a 1-dimensional array containing
      demodulator timestamps

    Returns:

      idx (numpy array): a 1-dimensional array indicating the indices in
      timestamp where sampleloss has occurred. An empty array is returned in no
      sampleloss was present.
    """
    # If the second difference of the timestamps is zero, no sampleloss has occurred
    index = np.where(np.diff(timestamps, n=2) > 0.1)[0] + 1
    # Find the true dtimestamps (determined by the configured sampling rate)
    dtimestamp = np.nan
    for i in range(0, np.shape(timestamps)[0]):
        # Take the sampling rate from a point where sample loss has not
        # occurred.
        if i not in index:
            dtimestamp = timestamps[i + 1] - timestamps[i]
            break
    assert not np.isnan(dtimestamp)
    for i in index:
        warnings.warn("Sample loss detected at timestamps={} (index: {}, {} points).".format(
            timestamps[i], i, (timestamps[i + 1] - timestamps[i])/dtimestamp))
    return index


def bwtc_scaling_factor(order):
    """Return the appropriate scaling factor for bandwidth to timeconstant
    converstion for the provided demodulator order.

    """
    scale = 0.0
    if order == 1:
        scale = 1.0
    elif order == 2:
        scale = 0.643594
    elif order == 3:
        scale = 0.509825
    elif order == 4:
        scale = 0.434979
    elif order == 5:
        scale = 0.385614
    elif order == 6:
        scale = 0.349946
    elif order == 7:
        scale = 0.322629
    elif order == 8:
        scale = 0.300845
    else:
        raise RuntimeError('Error: Order (%d) must be between 1 and 8.\n' % order)
    return scale


def bw2tc(bandwidth, order):
    """Convert the demodulator 3 dB bandwidth to its equivalent timeconstant for the
    specified demodulator order.

    Inputs:

      bandwidth (double): The demodulator 3dB bandwidth to convert.

      order (int): The demodulator order (1 to 8) for which to convert the
      bandwidth.

    Output:

      timeconstant (double): The equivalent demodulator timeconstant.

    """
    scale = bwtc_scaling_factor(order)
    timeconstant = scale/(2*np.pi*bandwidth)
    return timeconstant


def tc2bw(timeconstant, order):
    """Convert the demodulator timeconstant to its equivalent 3 dB bandwidth for the
    specified demodulator order.

    Inputs:

      timeconstant (double): The equivalent demodulator timeconstant.

      order (int): The demodulator order (1 to 8) for which to convert the
      bandwidth.

    Output:

      bandwidth (double): The demodulator 3dB bandwidth to convert.

    """
    scale = bwtc_scaling_factor(order)
    bandwidth = scale/(2*np.pi*timeconstant)
    return bandwidth


def systemtime_to_datetime(systemtime):
    """
    Convert the LabOne "systemtime" returned in LabOne data headers from
    microseconds since Unix epoch to a datetime object with microsecond
    precision.

    Example:

      import zhinst.examples as ziex
      import zhinst.utils as ziutils
      data = ziex.common.example_sweeper.run_example('dev2006')
      systemtime = data[0][0]['header']['systemtime'][0]
      t_datetime = ziutils.systemtime_to_datetime(systemtime)
      t_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
    """
    import datetime
    systemtime_sec, systemtime_microsec = divmod(systemtime, 1e6)
    # Create a datetime object from epoch timestamp with 0 microseconds.
    t = datetime.datetime.fromtimestamp(systemtime_sec)
    # Set the number of microseconds in the datetime object.
    t = t.replace(microsecond=int(systemtime_microsec))
    return t


def disable_everything(daq, device):
    """
    Put the device in a known base configuration: disable all extended
    functionality; disable all streaming nodes.

    Output:

      settings (list): A list of lists as provided to ziDAQServer's set()
      command. Each sub-list forms a nodepath, value pair. This is a list of
      nodes configured by the function and may be reused.

    Warning: This function is intended as a helper function for the API's
    examples and it's signature or implementation may change in future releases.
    """
    node_branches = daq.listNodes('/{}/'.format(device), 0)
    settings = []
    if node_branches == []:
        print('Device', device, 'is not connected to the data server.')
        return settings

    if 'AUCARTS' in node_branches:
        settings.append(['/{}/aucarts/*/enable'.format(device), 0])
    if 'AUPOLARS' in node_branches:
        settings.append(['/{}/aupolars/*/enable'.format(device), 0])
    if 'AWGS' in node_branches:
        settings.append(['/{}/awgs/*/enable'.format(device), 0])
    if 'BOXCARS' in node_branches:
        settings.append(['/{}/boxcars/*/enable'.format(device), 0])
    if 'CNTS' in node_branches:
        settings.append(['/{}/cnts/*/enable'.format(device), 0])
    # CURRINS
    if daq.listNodes('/{}/currins/0/float'.format(device), 0) != []:
        settings.append(['/{}/currins/*/float'.format(device), 0])
    if 'DIOS' in node_branches:
        settings.append(['/{}/dios/*/drive'.format(device), 0])
    if 'DEMODS' in node_branches:
        settings.append(['/{}/demods/*/enable'.format(device), 0])
        settings.append(['/{}/demods/*/trigger'.format(device), 0])
        settings.append(['/{}/demods/*/sinc'.format(device), 0])
        settings.append(['/{}/demods/*/oscselect'.format(device), 0])
        settings.append(['/{}/demods/*/harmonic'.format(device), 1])
        settings.append(['/{}/demods/*/phaseshift'.format(device), 0])
    if 'EXTREFS' in node_branches:
        settings.append(['/{}/extrefs/*/enable'.format(device), 0])
    if 'IMPS' in node_branches:
        settings.append(['/{}/imps/*/enable'.format(device), 0])
    if 'INPUTPWAS' in node_branches:
        settings.append(['/{}/inputpwas/*/enable'.format(device), 0])
    if daq.listNodes('/{}/mods/0/enable'.format(device), 0) != []:
        # HF2 without the MOD Option has an empty MODS branch.
        settings.append(['/{}/mods/*/enable'.format(device), 0])
    if 'OUTPUTPWAS' in node_branches:
        settings.append(['/{}/outputpwas/*/enable'.format(device), 0])
    if daq.listNodes('/{}/pids/0/enable'.format(device), 0) != []:
        # HF2 without the PID Option has an empty PID branch.
        settings.append(['/{}/pids/*/enable'.format(device), 0])
    if daq.listNodes('/{}/plls/0/enable'.format(device), 0) != []:
        # HF2 without the PLL Option still has the PLLS branch.
        settings.append(['/{}/plls/*/enable'.format(device), 0])
    if 'SIGINS' in node_branches:
        settings.append(['/{}/sigins/*/ac'.format(device), 0])
        settings.append(['/{}/sigins/*/imp50'.format(device), 0])
        sigins_children = daq.listNodes('/{}/sigins/0/'.format(device), 0)
        for leaf in ['DIFF', 'FLOAT']:
            if leaf in sigins_children:
                settings.append(['/{}/sigins/*/{}'.format(device, leaf.lower()), 0])
    if 'SIGOUTS' in node_branches:
        settings.append(['/{}/sigouts/*/on'.format(device), 0])
        settings.append(['/{}/sigouts/*/enables/*'.format(device), 0])
        settings.append(['/{}/sigouts/*/offset'.format(device), 0.0])
        sigouts_children = daq.listNodes('/{}/sigouts/0/'.format(device), 0)
        for leaf in ['ADD', 'DIFF', 'IMP50']:
            if leaf in sigouts_children:
                settings.append(['/{}/sigouts/*/{}'.format(device, leaf.lower()), 0])
        if 'PRECOMPENSATION' in sigouts_children:
            settings.append(['/{}/sigouts/*/precompensation/enable'.format(device), 0])
            settings.append(['/{}/sigouts/*/precompensation/highpass/*/enable'.format(device), 0])
            settings.append(['/{}/sigouts/*/precompensation/exponentials/*/enable'.format(device), 0])
            settings.append(['/{}/sigouts/*/precompensation/bounces/*/enable'.format(device), 0])
            settings.append(['/{}/sigouts/*/precompensation/fir/enable'.format(device), 0])
    if 'SCOPES' in node_branches:
        settings.append(['/{}/scopes/*/enable'.format(device), 0])
        if daq.listNodes('/{}/scopes/0/segments/enable'.format(device), 0) != []:
            settings.append(['/{}/scopes/*/segments/enable'.format(device), 0])
        if daq.listNodes('/{}/scopes/0/stream/enables/0'.format(device), 0) != []:
            settings.append(['/{}/scopes/*/stream/enables/*'.format(device), 0])
    if 'TRIGGERS' in node_branches:
        settings.append(['/{}/triggers/out/*/drive'.format(device), 0])
    daq.set(settings)
    daq.sync()
    return settings


def convert_awg_waveform(wave1, wave2=None, markers=None):
    """
    Converts one or multiple arrays with waveform data to the native AWG
    waveform format (interleaved waves and markers as uint16).

    Waveform data can be provided as integer (no conversion) or floating point
    (range -1 to 1) arrays.

    Arguments:

      wave1 (array): Array with data of waveform 1.
      wave2 (array): Array with data of waveform 2.
      markers (array): Array with marker data.

    Returns:

      The converted uint16 waveform is returned.
    """
    wave2_uint = None
    marker_uint = None
    mode = 0

    # Prepare waveforms
    def uint16_waveform(wave):
        wave = np.asarray(wave)
        if np.issubdtype(wave.dtype, np.floating):
            return np.asarray((np.power(2, 15) - 1) * wave, dtype=np.uint16)
        return np.asarray(wave, dtype=np.uint16)

    wave1_uint = uint16_waveform(wave1)
    mode += 1

    if wave2 is not None:
        if len(wave2) != len(wave1):
            raise Exception("wave1 and wave2 have different length. They should have the same length.")
        wave2_uint = uint16_waveform(wave2)
        mode += 2

    if markers is not None:
        if len(markers) != len(wave1):
            raise Exception("wave1 and marker have different length. They should have the same length.")
        marker_uint = np.array(markers, dtype=np.uint16)
        mode += 4

    # Merge waveforms
    waveform_data = None
    if mode == 1:
        waveform_data = wave1_uint
    elif mode == 3:
        waveform_data = np.vstack((wave1_uint, wave2_uint)).reshape((-2,), order='F')
    elif mode == 4:
        waveform_data = marker_uint
    elif mode == 5:
        waveform_data = np.vstack((wave1_uint, marker_uint)).reshape((-2,), order='F')
    elif mode == 6:
        waveform_data = np.vstack((wave2_uint, marker_uint)).reshape((-2,), order='F')
    elif mode == 7:
        waveform_data = np.vstack((wave1_uint, wave2_uint, marker_uint)).reshape((-2,), order='F')
    else:
        waveform_data = []

    return waveform_data


def parse_awg_waveform(wave_uint, channels=1, markers_present=False):
    """
    Converts a received waveform from the AWG waveform node into floating point
    and separates its contents into the respective waves (2 waveform waves and 1
    marker wave), depending on the input.

    Arguments:

      wave (array): A uint16 array from the AWG waveform node.
      channels (int): Number of channels present in the wave.
      markers_present (bool): Indicates if markers are interleaved in the wave.

    Returns:

      Three separated arrays are returned. The waveforms are scaled to be in the
      range [-1 and 1]. If no data is present the respective array is empty.
    """

    from collections import namedtuple

    # convert uint16 to int16
    wave_int = np.array(wave_uint, dtype=np.int16)

    parsed_waves = namedtuple('deinterleaved_waves', ['wave1', 'wave2', 'markers'])

    wave1 = []
    wave2 = []
    markers = []

    interleaved_frames = channels
    if markers_present:
        interleaved_frames += 1

    deinterleaved = [wave_int[idx::interleaved_frames] for idx in range(interleaved_frames)]

    deinterleaved[0] = deinterleaved[0]/(np.power(2, 15)-1)
    if channels == 2:
        deinterleaved[1] = deinterleaved[1]/(np.power(2, 15)-1)

    wave1 = deinterleaved[0]
    if channels == 2:
        wave2 = deinterleaved[1]
    if markers_present:
        markers = deinterleaved[-1]

    return parsed_waves(wave1, wave2, markers)
