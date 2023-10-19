# -*- coding: utf-8 -*-
"""
Zurich Instruments LabOne Python API Example

Python API Example for the Software Trigger (ziDAQRecorder) Core Module in Grid
Mode with averaging enabled. This example demonstrates how to obtain averaged
demodulator data when a demodulator's R value is larger than a specified
threshold using an edge trigger in Grid Mode.

The ziDAQRecorder Module implements software triggering which operates
analogously to the types of triggering found in laboratory oscilloscopes. The
ziDAQRecorder Module has a non-blocking (asynchronous) interface, it starts it's
own thread to communicate with the data server.

This example generates a 'beat' in the demodulator signal in order to simulate
'events' in the demodulator data. Signal segments of these events are then
recorded when the rising edge of the demodulator R value exceeds a certain
threshold.

Grid Mode enables interpolation of the triggered data onto the specified columns
of the grid and alignment of (num_rows) multiple triggers into the rows of the
grid. This example demonstrates the averaging functionality of Grid Mode which
is enabled when /0/grid/repetitions is > 1 and /0/grid/operation
is set to average. The SW Trigger Module triggers on different peaks in the
bi-modal beat generated in the demodulator data (check the Plotter in the LabOne
UI to see the original demod data) and the averaging operation averages the
peaks caught by the trigger.

Note: This example requires a feedback cable between Signal Output 1 and Signal
Input 1 and changes the signal output's amplitude in order to create a signal
upon which to trigger.

"""

# Copyright 2016 Zurich Instruments AG

from __future__ import print_function
import time
import numpy as np
import zhinst.utils


def run_example(device_id, do_plot=False, num_grids=3):
    """Run the example: Record averaged bursts of demodulator sample data when a
    demodulator's R becomes larger than a specified threshold using ziPython's
    Software Trigger (ziDAQRecorder) Module in Grid Mode. See this Module's
    docstring and inline comments for further explanation.

    Requirements:

      Hardware configuration: Connect signal output 1 to signal input 1 with a
      BNC cable.

    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev2006` or `uhf-dev2006`.

      num_grids (int, optional): The number of grids to record.

      do_plot (bool, optional): Specify whether to plot the recorded
        data. Default is no plot output.

    Returns:

      sample (list of dict): A list of demodulator samples. Each entry in the
        list is a dict containing a demodulator sample, each sample corresponds
        to a burst of demodulator data from each each trigger.

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
    # This example runs on any device type but requires either the Multifrequency
    # or Multidemodulator option.
    required_devtype = '.*LI|.*IA|.*IS'
    required_options = [r"MF|MFK|MD"]
    err_msg = "This example requires either an HF2/UHF Instrument with the Multifrequency (MF)" + \
              "Option installed or an MF Instrument with Multidemodulator (MD)" + \
              "Option installed. Note: The MF/MD Option is not a requirement to" + \
              "use the SW Trigger module itself, just to run this example."
    # Create an API session; connect to the correct Data Server for the device.
    err_msg = "This example only supports instruments with demodulators."
    (daq, device, props) = zhinst.utils.create_api_session(device_id, apilevel_example,
                                                           required_devtype=required_devtype,
                                                           required_options=required_options,
                                                           required_err_msg=err_msg)
    zhinst.utils.api_server_version_check(daq)

    # Enable ziPython's log, the lower the level the more verbose.
    daq.setDebugLevel(3)

    # Create a base configuration: Disable all available outputs, awgs, demods, scopes,...
    zhinst.utils.disable_everything(daq, device)

    # Now configure the instrument for this experiment. The following channels
    # and indices work on all device configurations. The values below may be
    # changed if the instrument has multiple input/output channels and/or either
    # the Multifrequency or Multidemodulator options installed.
    amplitude = 0.100
    out_channel = 0
    in_channel = 0
    frequency = 400e3
    trigger_demod_index = 0
    demod_rate = 25e3
    demod_order = 8
    demod_bandwidth = 10e3
    # A small timeconstant is required to see the interference between the
    # demodulators
    timeconstant = zhinst.utils.bw2tc(demod_bandwidth, demod_order)
    exp_setting = [['/%s/sigins/%d/ac'             % (device, in_channel), 0],
                   ['/%s/sigins/%d/imp50'          % (device, in_channel), 1],
                   ['/%s/sigins/%d/range'          % (device, in_channel), 6*amplitude],
                   ['/%s/demods/%d/enable'         % (device, trigger_demod_index), 1],
                   ['/%s/demods/%d/rate'           % (device, trigger_demod_index), demod_rate],
                   ['/%s/demods/%d/adcselect'      % (device, trigger_demod_index), in_channel],
                   ['/%s/demods/*/order'           % (device), demod_order],
                   ['/%s/demods/%d/timeconstant'   % (device, trigger_demod_index), timeconstant],
                   ['/%s/demods/0/oscselect'       % (device), 0],
                   ['/%s/demods/1/oscselect'       % (device), 1],
                   ['/%s/demods/2/oscselect'       % (device), 2],
                   ['/%s/demods/*/harmonic'        % (device), 1],
                   ['/%s/oscs/0/freq'              % (device), frequency],
                   ['/%s/oscs/1/freq'              % (device), frequency + 50],
                   ['/%s/oscs/2/freq'              % (device), frequency + 523],
                   ['/%s/sigouts/%d/on'            % (device, out_channel), 1],
                   ['/%s/sigouts/%d/range'         % (device, out_channel), 1],
                   ['/%s/sigouts/%d/enables/0'     % (device, out_channel), 1],
                   ['/%s/sigouts/%d/amplitudes/0'  % (device, out_channel), amplitude],
                   ['/%s/sigouts/%d/enables/1'     % (device, out_channel), 1],
                   ['/%s/sigouts/%d/amplitudes/1'  % (device, out_channel), amplitude],
                   ['/%s/sigouts/%d/enables/2'     % (device, out_channel), 1],
                   ['/%s/sigouts/%d/amplitudes/2'  % (device, out_channel), amplitude]]
    # Some other device-type dependent configuration may be required. For
    # example, disable the signal inputs `diff` and the signal outputs `add` for
    # HF2 instruments.
    if props['devicetype'].startswith('HF2'):
        exp_setting.append(['/%s/sigins/%d/diff'      % (device, in_channel), 0])
        exp_setting.append(['/%s/sigouts/%d/add'      % (device, out_channel), 0])
    daq.set(exp_setting)

    # Wait for the demodulator filter to settle.
    timeconstant_set = daq.getDouble('/%s/demods/%d/timeconstant' % (device, trigger_demod_index))
    time.sleep(10*timeconstant_set)

    # Perform a global synchronisation between the device and the data server:
    # Ensure that 1. the settings have taken effect on the device before issuing
    # the poll() command and 2. clear the API's data buffers. Note: the sync()
    # must be issued after waiting for the demodulator filter to settle above.
    daq.sync()

    # Create an instance of the Software Trigger Module (ziDAQRecorder class).
    trigger = daq.record()

    # Set the device that will be used for the trigger - this parameter must be set.
    trigger.set('device', device)
    # We will trigger on a positive edge of a demodulator sample R value.
    # /0/type (int):
    #   NO_TRIGGER = 0
    #   EDGE_TRIGGER = 1
    #   DIGITAL_TRIGGER = 2
    #   PULSE_TRIGGER = 3
    #   TRACKING_TRIGGER = 4
    #   HW_TRIGGER = 6
    #   TRACKING_PULSE_TRIGGER = 7
    #   EVENT_COUNT_TRIGGER = 8
    trigger.set('/0/type', 1)
    # /0/triggernode (char):
    #   Specify the trigger signal to trigger on. The trigger signal comprises
    #   of a device node path appended with a trigger field seperated by a dot.
    #   For demodulator samples, the following trigger fields are available:
    #   SAMPLE.X = Demodulator X value
    #   SAMPLE.Y = Demodulator Y value
    #   SAMPLE.R = Demodulator Magnitude
    #   SAMPLE.THETA = Demodulator Phase
    #   SAMPLE.AUXIN0 = Auxilliary input 1 value
    #   SAMPLE.AUXIN1 = Auxilliary input 2 value
    #   SAMPLE.DIO = Digital I/O value
    #   SAMPLE.TRIGINN = HW Trigger In N (where supported)
    #   SAMPLE.TRIGOUTN = HW Trigger Out N (where supported)
    #   SAMPLE.TRIGDEMOD1PHASE = Demod 1's oscillator's phase (MF, UHF)
    #   SAMPLE.TRIGDEMOD2PHASE = Demod 2's oscillator's phase (MF)
    #   SAMPLE.TRIGDEMOD4PHASE = Demod 4's oscillator's phase  (UHF)
    #   SAMPLE.TRIGAWGTRIGN = AWG Trigger N  (where supported)
    triggerpath = '/%s/demods/%d/sample' % (device, trigger_demod_index)
    triggernode = triggerpath + '.r'
    trigger.set('/0/triggernode', triggernode)
    # /0/edge (int):
    #   Specify which edge type to trigger on.
    #   POS_EDGE = 1
    #   NEG_EDGE = 2
    #   BOTH_EDGE = 3
    trigger.set('/0/edge', 1)
    # Note: We do not manually set 0/level and 0/hysteresis in
    # this example, rather we set the 0/findlevel parameter to 1 and let
    # the SW Trigger Module determine an appropriate level and hysteresis for us.
    #
    # 0/level (double):
    # The set the trigger level.
    trigger_level = 0.05
    print("Setting /0/level to {:.3f}.".format(trigger_level))
    trigger.set('/0/level', trigger_level)
    #
    # 0/hysteresis (double):
    #   The hysterisis is effectively a second criteria (if non-zero) for
    #   triggering and makes triggering more robust in noisy signals. When the
    #   trigger `level` is violated, then the signal must return beneath (for
    #   positive trigger edge) the hysteresis value in order to trigger.
    #
    trigger_hysteresis = 0.05*trigger_level
    print("Setting /0/hysteresis {:.3f}.".format(trigger_hysteresis))
    trigger.set('/0/hysteresis', trigger_hysteresis)
    # The size of the internal buffer used to store data, this should be larger
    # than trigger_duration.
    trigger_duration = 0.0035
    buffer_size = max(0.500, 1.1*trigger_duration)
    trigger.set('buffersize', buffer_size)
    # The length of time to record the data for each time we trigger.
    trigger.set('/0/duration', trigger_duration)
    trigger_delay = -0.5*trigger_duration
    trigger.set('/0/delay', trigger_delay)
    # Do not extend the size of the returned trigger frame if new triggers
    # arrive whilst recording a trigger.
    trigger.set('/0/retrigger', 0)
    # Do not return overlapped trigger events.
    trigger.set('/0/holdoff/time', trigger_duration)
    trigger.set('/0/holdoff/count', 0)

    # Unrequired parameters when 0/type is EDGE_TRIGGER:
    # trigger.set('/0/bitmask', 1)  % For DIGITAL_TRIGGER
    # trigger.set('/0/bits', 1)  % For DIGITAL_TRIGGER
    # trigger.set('/0/bandwidth', 10)  % For TRACKING_TRIGGER

    # SW Trigger Grid Mode configuration:
    # /0/grid/mode (int)
    #   Enable/disable grid mode:
    #     0: Disable grid mode.
    #     1: Enable with nearest neighbour interpolation for the column data.
    #     2: Enable with linear interpolation for the column data.
    trigger.set('/0/grid/mode', 2)
    # Note: /0/grid/operation is not relevant if repetitions is 1, see
    # below.
    # /0/grid/operation (int)
    #   If the number of repetitions > 1, either replace or average the data in
    #     the grid:
    #     0: Replace.
    #     1: Average.
    trigger.set('/0/grid/operation', 1)
    # /0/grid/repetitions (int)
    #   The number of times to perform 0/grid/operation.
    num_repetitions = 50
    trigger.set('/0/grid/repetitions', num_repetitions)
    # /0/grid/cols (int)
    #   Specify the number of columns in the grid's matrix. The data from each
    #     row is interpolated onto a grid with the specified number of columns.
    num_cols = 100
    trigger.set('/0/grid/cols', num_cols)
    # /0/grid/rows (int)
    #   Specify the number of rows in the grid's matrix. Each row is the data
    #   recorded from one trigger.
    num_rows = 100
    trigger.set('/0/grid/rows', num_rows)
    # /0/grid/direction (int)
    #   Specify the ordering of the data stored in the grid's matrix.
    #     0: Forward - the data in each row is ordered chronologically, e.g., the
    #       first data point in each row corresponds to the first timestamp in the
    #       trigger data.
    #     1: Reverse - the data in each row is ordered reverse chronologically,
    #       e.g., the first data point in each row corresponds to the last
    #       timestamp in the trigger data.
    #     2: Bidirectional - the ordering of the data alternates between Forward
    #        and Backward ordering from row-to-row. The first row is Forward ordered.
    trigger.set('/0/grid/direction', 0)

    # The number of grids to record (if not running in endless mode).
    # In grid mode, we will obtain 0/count grids. The total
    # number of triggers is equal to n = 0/count *
    # /0/grid/rows * /0/grid/repetitions
    trigger.set('/0/count', num_grids)

    # We will perform intermediate reads from the module. When a grid is
    # complete and read() is called, the data is removed from the module. We
    # have to manage saving of the finished grid ourselves if we perform
    # intermediate reads.
    data = {}
    data[triggerpath] = []

    # Subscribe to the device node paths we would like to record when the trigger criteria is met.
    pid_error_stream_path = '/%s/pids/0/stream/error' % device
    node_paths = daq.listNodes(pid_error_stream_path, 7)
    # If this node is present, then the instrument has the PID Option. In this
    # case additionally subscribe to a PID's error. Note, PID streaming nodes
    # not available on HF2 instruments.
    if pid_error_stream_path.upper() in node_paths:
        trigger.subscribe(pid_error_stream_path)
        daq.setDouble('/%s/pids/0/stream/rate' % device, 30e3)
        data[pid_error_stream_path] = []
    # Note: We subscribe to the trigger signal path last to ensure that we obtain
    # complete data on the other paths (known limitation). We must subscribe to
    # the trigger signal path.
    trigger.subscribe(triggerpath)

    if do_plot:
        z_min = np.inf
        z_max = -np.inf
        from mpl_toolkits.mplot3d import Axes3D  # pylint: disable=W0611 # unused-import (required by subplot projection='3d')
        from matplotlib import cm
        import matplotlib.pyplot as plt
        _, ax = plt.subplots(subplot_kw=dict(projection='3d'))

        x = np.linspace(trigger_delay, trigger_delay + trigger_duration, num_cols)
        y = np.arange(0, num_rows)
        xx, yy = np.meshgrid(x, y)  # pylint: disable=W0632
        # Initialize the image plot with NANs - we'll only update the img's data
        # in the loop.
        R = np.empty((num_rows, num_cols, ))
        R[:] = np.nan
        surf1 = ax.plot_surface(xx, yy, R, rstride=1, cstride=1, cmap=cm.coolwarm,  # pylint: disable=E1101
                                linewidth=0, antialiased=False)
        num_ticks = 5
        ticks = np.linspace(0, num_cols, num_ticks)
        ticklabels = ["{:0.3f}".format(trigger_delay + trigger_duration*tick/num_cols) for tick in ticks]
        ax.set_xticks(ticks)
        ax.set_xticklabels(ticklabels)
        ax.set_title('Averaged Demod $R$ Data plotted as a Matrix')
        ax.set_xlabel('Time, relative to trigger ($s$)')
        ax.set_ylabel('Grid row index')
        plt.ion()

    # Start the Software Trigger's thread. Ready to be triggered.
    trigger.execute()
    time.sleep(2.*buffer_size)

    flags = 0
    return_flat_data_dict = True
    num_finished_grids = 0
    timeout = 120  # [s]
    t0 = time.time()
    while not trigger.finished():
        # Read out the intermediate data captured by the SW Trigger.
        return_flat_data_dict = True
        data_read = trigger.read(return_flat_data_dict)
        if (triggerpath in data_read) and data_read[triggerpath]:
            # Note, if /0/count > 1 then more than one grid could be returned.
            num_grids_read = len(data_read[triggerpath])
            for i in range(num_grids_read):
                flags = data_read[triggerpath][i]['header']['flags']
                if flags & 1:
                    # The first bit of flags is set to 1 when the grid is complete and the
                    # configured number of operation repetitions have been formed.
                    num_finished_grids = num_finished_grids + 1
                    print("Finished grid {} of {}.".format(num_finished_grids, num_grids))
                    data[triggerpath].append(data_read[triggerpath][i])
                    if pid_error_stream_path in data_read:
                        # We only get PID data if the (non-HF2) device has the PID Option.
                        data[pid_error_stream_path].append(data_read[pid_error_stream_path][i])
            print('Overall progress: {}. Grid {} flags: {}.'.format(
                trigger.progress()[0], num_finished_grids, flags[0]))
            if do_plot:
                # Visualize the last grid's demodulator data (the demodulator used as
                # the trigger path) from the intermediate read(). Plot the updated
                # grid.
                R = np.abs(data_read[triggerpath][-1]['x'] + 1j*data_read[triggerpath][-1]['y'])
                surf1.remove()
                surf1 = ax.plot_surface(xx, yy, R, rstride=1, cstride=1, cmap=cm.coolwarm,  # pylint: disable=E1101
                                        linewidth=0, antialiased=False)
                R_max = np.nanmax(R)
                R_min = np.nanmin(R)
                if R_max > z_max:
                    z_max = R_max
                if R_min < z_min:
                    z_min = R_min
                ax.set_zlim(z_min, z_max)
                plt.draw()
        else:
            print("No update available since last read.")
        if do_plot:
            plt.pause(0.01)
        else:
            time.sleep(0.05)
        if time.time() - t0 > timeout:
            # Leave the loop if we're not obtaining triggers/grids quickly enough.
            if num_finished_grids == 0:
                # If we didn't even get one grid, stop the module, delete its
                # thread and raise an error.
                trigger.finish()
                raise RuntimeError("Failed to record any grids before timeout ({} seconds). ".format(timeout))
            print('Recorded {} grids. Loop timed-out after {} s before acquiring all {} grids.'.format(
                num_finished_grids, timeout, num_grids))
            break

    if not flags & 1:
        # The SW Trigger finished recording since performing the previous intermediate
        # read() in the loop: Do another read() to get the final data.
        print("SW Trigger finished since last intermediate read() in loop, reading out finished grid(s).")
        data_read = trigger.read(return_flat_data_dict)
        num_grids_read = len(data_read[triggerpath])
        for i in range(num_grids_read):
            flags = data_read[triggerpath][i]['header']['flags']
            if flags & 1:
                data[triggerpath].append(data_read[triggerpath][i])
                if pid_error_stream_path in data_read:
                    # We only get PID data if the (non-HF2) device has the PID Option.
                    data[pid_error_stream_path].append(data_read[pid_error_stream_path][i])
            if do_plot:
                R = np.abs(data_read[triggerpath][-1]['x'] + 1j*data_read[triggerpath][-1]['y'])
                surf1.remove()
                surf1 = ax.plot_surface(xx, yy, R, rstride=1, cstride=1, cmap=cm.coolwarm,  # pylint: disable=E1101
                                        linewidth=0, antialiased=False)
                plt.draw()

    # Stop the Module (this is also ok if trigger.finished() is True).
    trigger.finish()

    assert triggerpath in data, "Ooops, we didn't get any data for `{}`.".format(triggerpath)

    if do_plot:
        plt.ioff()
        print("Please close the figure to exit the example...")
        plt.show()

    return data
