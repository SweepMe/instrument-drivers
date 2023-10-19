# -*- coding: utf-8 -*-
"""
Zurich Instruments LabOne Python API Example

Demonstrate how to save and load Zurich Instruments device settings
asynchronously using the ziDeviceSettings class.

Note: This example is intended for experienced users who require a non-blocking
(asynchronous) interface for loading and saving settings. In general, the
utility functions save_settings() and load_settings() are more appropriate; see
`example_save_device_settings_simple`.

"""

# Copyright 2016 Zurich Instruments AG

from __future__ import print_function
import time
import os
import zhinst.utils


def run_example(device_id, settings_file_path=None):
    """
    Run the example: Connect to a Zurich Instruments instrument, save the
    instrument's settings to file, toggle the signal output enable and reload
    the settings file.

    Note: This example is intended for experienced users who require a
    non-blocking (asynchronous) interface for loading and saving settings. In
    general, the utility functions save_settings() and load_settings() are more
    appropriate; see `example_save_device_settings_simple'.

    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev2006` or `uhf-dev2006`.

      setting_file_path (str, optional): Specify the path where to save the
        settings file.


    Returns:

      filename (str) : the name (with path) of the XML file where the settings
         were saved.

    Raises:

      RuntimeError: If the device is not "discoverable" from the API.

    See the "LabOne Programming Manual" for further help, available:
      - On Windows via the Start-Menu:
        Programs -> Zurich Instruments -> Documentation
      - On Linux in the LabOne .tar.gz archive in the "Documentation"
        sub-folder.

    """

    apilevel_example = 6  # The API level supported by this example.
    # Call a zhinst utility function that returns:
    # - an API session `daq` in order to communicate with devices via the data server.
    # - the device ID string that specifies the device branch in the server's node hierarchy.
    (daq, device, _) = zhinst.utils.create_api_session(device_id, apilevel_example)
    zhinst.utils.api_server_version_check(daq)

    timestr = time.strftime("%Y%m%d_%H%M%S")
    filename_noext = timestr + '_example_save_device_settings_expert'  # Change this to the filename you want to save.

    device_settings = daq.deviceSettings()
    device_settings.set('device', device)
    device_settings.set('filename', filename_noext)
    if settings_file_path:
        device_settings.set('path', settings_file_path)
    # Set the path to '.' save to the current directory.
    # device_settings.set('path', '.')
    # NOTE: in this case, this example will have to be executed from a folder
    # where you have write access.

    toggle_device_setting(daq, device)

    # Save the instrument's current settings.
    print("Saving settings...")
    device_settings.set('command', 'save')
    device_settings.execute()
    while not device_settings.finished():
        time.sleep(0.2)
    print("Done.")

    data = device_settings.get('path')
    path = data['path'][0]
    filename_full_path = os.path.join(path, filename_noext) + '.xml'
    assert os.path.isfile(filename_full_path), "Failed to save settings file '%s'" % filename_full_path
    print("Saved file '{}'.".format(filename_full_path))

    toggle_device_setting(daq, device)

    # Load the settings.
    print("Loading settings...")
    device_settings.set('command', 'save')
    device_settings.execute()
    while not device_settings.finished():
        time.sleep(0.2)
    print("Done.")

    return filename_full_path


def toggle_device_setting(daq, device):
    """
    Toggle a setting on the device: If it's enabled, disable the setting, and
    vice versa.
    """
    path = '/%s/sigouts/0/on' % device
    is_enabled = daq.getInt(path)
    print("Toggling setting '{}'.".format(path))
    daq.setInt(path, not is_enabled)
    daq.sync()
