# -*- coding: utf-8 -*-
"""
Zurich Instruments LabOne Python API Example

Python API Example for the Data Acquisition Module. This example demonstrates
how to record data from an instrument continuously (without triggering).

Note: This example does not perform any device configuration. If the streaming
nodes corresponding to the signal_paths are not enabled, no data will be
recorded.
"""

# Copyright 2018 Zurich Instruments AG

from __future__ import print_function
import time
import numpy as np
import zhinst.utils
from zhinst.ziPython import ziListEnum


def run_example(device_id, do_plot=False, filename=None):
    """
    Run the example: Record data continuously in 0.2 s chunks for 5 seconds
    using the Data Acquisition Module.

    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev2006` or `uhf-dev2006`.

      do_plot (bool, optional): Specify whether to plot the recorded
        data. Default is no plot output.

      filename (str, optional): If specified, additionally save the data to a
        directory structure/filename specified by filename.

    Returns:

      data (dict): A dictionary whose keys are the subscribed signal paths. Each
        value is a list which contains all the signal bursts for the signal path
        as returned by the Data Acquisition Module's read() function. Note: Do
        not increase TOTAL_DURATION without removing this continuous save.

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
    (daq, device, _) = zhinst.utils.create_api_session(device_id, apilevel_example)
    zhinst.utils.api_server_version_check(daq)

    # The list of signal paths that we would like to record in the module.
    demod_path = '/{}/demods/0/sample'.format(device)
    signal_paths = []
    signal_paths.append(demod_path + '.x')  # The demodulator X output.
    signal_paths.append(demod_path + '.y')  # The demodulator Y output.
    # It's also possible to add signals from other node paths:
    # signal_paths.append('/%s/demods/1/sample.r' % (device))

    # Check the device has demodulators.
    flags = ziListEnum.recursive | ziListEnum.absolute | ziListEnum.streamingonly
    streaming_nodes = daq.listNodes('/{}'.format(device), flags)
    if demod_path.upper() not in streaming_nodes:
        print("Device {} does not have demodulators. Please modify the example to specify".format(device),
              "a valid signal_path based on one or more of the following streaming nodes: ",
              "{}".format('\n'.join(streaming_nodes)))
        raise Exception("Demodulator streaming nodes unavailable - see the message above for more information.")

    # Defined the total time we would like to record data for and its sampling rate.
    # total_duration: Time in seconds: This examples stores all the acquired data in the `data` dict - remove this
    # continuous storing in read_data_update_plot before increasing the size of total_duration!
    total_duration = 5
    module_sampling_rate = 30000  # Number of points/second
    burst_duration = 0.2  # Time in seconds for each data burst/segment.
    num_cols = int(np.ceil(module_sampling_rate*burst_duration))
    num_bursts = int(np.ceil(total_duration/burst_duration))

    # Create an instance of the Data Acquisition Module.
    daq_module = daq.dataAcquisitionModule()

    # Configure the Data Acquisition Module.
    # Set the device that will be used for the trigger - this parameter must be set.
    daq_module.set("device", device)

    # Specify continuous acquisition (type=0).
    daq_module.set("type", 0)

    # 'grid/mode' - Specify the interpolation method of
    #   the returned data samples.
    #
    # 1 = Nearest. If the interval between samples on the grid does not match
    #     the interval between samples sent from the device exactly, the nearest
    #     sample (in time) is taken.
    #
    # 2 = Linear interpolation. If the interval between samples on the grid does
    #     not match the interval between samples sent from the device exactly,
    #     linear interpolation is performed between the two neighbouring
    #     samples.
    #
    # 4 = Exact. The subscribed signal with the highest sampling rate (as sent
    #     from the device) defines the interval between samples on the DAQ
    #     Module's grid. If multiple signals are subscribed, these are
    #     interpolated onto the grid (defined by the signal with the highest
    #     rate, "highest_rate"). In this mode, duration is
    #     read-only and is defined as num_cols/highest_rate.
    daq_module.set("grid/mode", 2)
    # 'count' - Specify the number of bursts of data the
    #   module should return (if endless=0). The
    #   total duration of data returned by the module will be
    #   count*duration.
    daq_module.set("count", num_bursts)
    # 'duration' - Burst duration in seconds.
    #   If the data is interpolated linearly or using nearest neighbout, specify
    #   the duration of each burst of data that is returned by the DAQ Module.
    daq_module.set("duration", burst_duration)
    # 'grid/cols' - The number of points within each duration.
    #   This parameter specifies the number of points to return within each
    #   burst (duration seconds worth of data) that is
    #   returned by the DAQ Module.
    daq_module.set("grid/cols", num_cols)

    if filename is not None:
        # 'save/fileformat' - The file format to use for the saved data.
        #    0 - Matlab
        #    1 - CSV
        daq_module.set('save/fileformat', 1)
        # 'save/filename' - Each file will be saved to a
        # new directory in the Zurich Instruments user directory with the name
        # filename_NNN/filename_NNN/
        daq_module.set('save/filename', filename)
        # 'save/saveonread' - Automatically save the data
        # to file each time read() is called.
        daq_module.set('save/saveonread', 1)

    data = {}
    # A dictionary to store all the acquired data.
    for signal_path in signal_paths:
        print("Subscribing to", signal_path)
        daq_module.subscribe(signal_path)
        data[signal_path] = []

    clockbase = float(daq.getInt("/{}/clockbase".format(device)))
    if do_plot:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.set_xlabel('Time ($s$)')
        ax.set_ylabel('Subscribed signals')
        ax.set_xlim([0, total_duration])
        plt.ion()

    ts0 = np.nan
    read_count = 0

    def read_data_update_plot(data, timestamp0):
        """
        Read the acquired data out from the module and plot it. Raise an
        AssertionError if no data is returned.
        """
        data_read = daq_module.read(True)
        returned_signal_paths = [signal_path.lower() for signal_path in data_read.keys()]
        progress = daq_module.progress()[0]
        # Loop over all the subscribed signals:
        for signal_path in signal_paths:
            if signal_path.lower() in returned_signal_paths:
                # Loop over all the bursts for the subscribed signal. More than
                # one burst may be returned at a time, in particular if we call
                # read() less frequently than the burst_duration.
                for index, signal_burst in enumerate(data_read[signal_path.lower()]):
                    if np.any(np.isnan(timestamp0)):
                        # Set our first timestamp to the first timestamp we obtain.
                        timestamp0 = signal_burst['timestamp'][0, 0]
                    # Convert from device ticks to time in seconds.
                    t = (signal_burst['timestamp'][0, :] - timestamp0)/clockbase
                    value = signal_burst['value'][0, :]
                    if do_plot:
                        ax.plot(t, value)
                    num_samples = len(signal_burst['value'][0, :])
                    dt = (signal_burst['timestamp'][0, -1] - signal_burst['timestamp'][0, 0])/clockbase
                    data[signal_path].append(signal_burst)
                    print("Read: ", read_count, ", progress: {0:.2f}%".format(100*progress), ". Burst ", index, ": ",
                          signal_path, " contains ", num_samples, " spanning {0:.2f} s.".format(dt), sep="")
            else:
                # Note: If we read before the next burst has finished, there may be no new data.
                # No action required.
                pass

        # Update the plot.
        if do_plot:
            ax.set_title("Progress of data acquisition: {0:.2f}%.".format(100*progress))
            plt.pause(0.01)
            fig.canvas.draw()
        return data, timestamp0

    # Start recording data.
    daq_module.execute()

    # Record data in a loop with timeout.
    timeout = 1.5*total_duration
    t0_measurement = time.time()
    # The maximum time to wait before reading out new data.
    t_update = 0.9*burst_duration
    while not daq_module.finished():
        t0_loop = time.time()
        if time.time() - t0_measurement > timeout:
            raise Exception("Timeout after {} s - recording not complete. Are the streaming nodes enabled? "
                            "Has a valid signal_path been specified?".format(timeout))
        data, ts0 = read_data_update_plot(data, ts0)
        read_count += 1
        # We don't need to update too quickly.
        time.sleep(max(0, t_update - (time.time() - t0_loop)))

    # There may be new data between the last read() and calling finished().
    data, _ = read_data_update_plot(data, ts0)

    # Before exiting, make sure that saving to file is complete (it's done in the background)
    # by testing the 'save/save' parameter.
    timeout = 1.5*total_duration
    t0 = time.time()
    while daq_module.getInt('save/save') != 0:
        time.sleep(0.1)
        if time.time() - t0 > timeout:
            raise Exception("Timeout after {} s before data save completed.".format(timeout))

    if not do_plot:
        print("Please run with `do_plot=True` to see dynamic plotting of the acquired signals.")

    return data
