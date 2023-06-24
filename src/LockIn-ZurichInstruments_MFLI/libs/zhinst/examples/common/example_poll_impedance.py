# -*- coding: utf-8 -*-
"""
Zurich Instruments LabOne Python API Example

Demonstrate how to obtain impedance data using ziDAQServer's blocking
(synchronous) poll() command.
"""

# Copyright 2018 Zurich Instruments AG

from __future__ import print_function
import time
import numpy as np
import zhinst.utils
from .example_autoranging_impedance import run_example as run_autoranging_example


def run_example(device_id, do_plot=False):
    """
    Run the example: Connect to the device specified by device_id and obtain
    impedance data using ziDAQServer's blocking (synchronous) poll() command.

    Requirements:

      Hardware configuration: Connect signal output 1 to signal input 1 with a
      BNC cable.

    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev3006` or `mf-dev3006`.

      amplitude (float, optional): The amplitude to set on the signal output.

      do_plot (bool, optional): Specify whether to plot the polled data. Default
        is no plot output.

    Returns:

      sample (dict of numpy arrays): The impedance sample dictionary as returned
      by poll.

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
    # - the device's discovery properties.
    err_msg = "This example only supports instruments with IA option."
    (daq, device, _) = zhinst.utils.create_api_session(device_id, apilevel_example,
                                                       required_options=['IA'],
                                                       required_err_msg=err_msg)
    zhinst.utils.api_server_version_check(daq)

    # Create a base configuration: Disable all available outputs, awgs, demods, scopes,...
    zhinst.utils.disable_everything(daq, device)

    # We use the auto-range example to perform some basic device configuration
    # and wait until signal input ranges have been configured by the device.
    run_autoranging_example(device)

    # Subscribe to the impedance sample node path.
    imp_index = 0
    path = '/%s/imps/%d/sample' % (device, imp_index)
    daq.subscribe(path)

    # Sleep for demonstration purposes: Allow data to accumulate in the data
    # server's buffers for one second: poll() will not only return the data
    # accumulated during the specified poll_length, but also for data
    # accumulated since the subscribe() or the previous poll.
    sleep_length = 1.0
    # For demonstration only: We could, for example, be processing the data
    # returned from a previous poll().
    time.sleep(sleep_length)

    # Poll the subscribed data from the data server. Poll will block and record
    # for poll_length seconds.
    poll_length = 0.1  # [s]
    poll_timeout = 500  # [ms]
    poll_flags = 0
    poll_return_flat_dict = True
    data = daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)

    # Unsubscribe from all paths.
    daq.unsubscribe('*')

    # Check the dictionary returned is non-empty
    assert data, "poll() returned an empty data dictionary, did you subscribe to any paths?"

    # The data returned is a dictionary of dictionaries that reflects the node's path.
    # Note, the data could be empty if no data had arrived, e.g., if the imps
    # were disabled or had transfer rate 0.
    assert path in data, "The data dictionary returned by poll has no key `%s`." % path

    # Access the impedance sample using the node's path. For more information
    # see the data structure documentation for ZIImpedanceSample in the LabOne
    # Programming Manual.
    impedance_sample = data[path]

    # Get the sampling rate of the device's ADCs, the device clockbase in order
    # to convert the sample's timestamps to seconds.
    clockbase = float(daq.getInt('/%s/clockbase' % device))

    dt_seconds = (impedance_sample['timestamp'][-1] - impedance_sample['timestamp'][0])/clockbase
    num_samples = len(impedance_sample['timestamp'])
    print("poll() returned {} samples of impedance data spanning {:.3f} seconds.".format(num_samples, dt_seconds))
    print("Average measured resitance: {} Ohm.".format(np.mean(impedance_sample['param0'])))
    print("Average measured capacitance: {} F.".format(np.mean(impedance_sample['param1'])))

    if do_plot:
        import matplotlib.pyplot as plt

        # Convert timestamps from ticks to seconds via clockbase.
        t = (impedance_sample['timestamp'] - impedance_sample['timestamp'][0])/clockbase

        plt.close('all')
        # Create plot
        _, ax = plt.subplots(2, sharex=True)
        ax[0].plot(t, impedance_sample['param0'])
        ax[0].set_title('Impedance Parameters')
        ax[0].grid(True)
        ax[0].set_ylabel(r'Resistance ($\Omega$)')
        ax[0].autoscale(enable=True, axis='x', tight=True)

        ax[1].plot(t, impedance_sample['param1'])
        ax[1].grid(True)
        ax[1].set_ylabel(r'Capacitance (F)')
        ax[1].set_xlabel('Time (s)')
        ax[1].autoscale(enable=True, axis='x', tight=True)

        plt.draw()
        plt.show()

    return data
