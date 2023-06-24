# -*- coding: utf-8 -*-
"""
Zurich Instruments LabOne Python API Example

Demonstrate how to perform a frequency sweep on two synchronized devices using
the MultiDeviceSync Module and ziDAQSweeper class/Sweeper Module.
"""

# Copyright 2018 Zurich Instruments AG

from __future__ import print_function
import time
import zhinst.utils


def run_example(device_ids, amplitude=0.1, do_plot=False, synchronize=True):
    """
    Run the example: Perform a frequency sweep on two devices and record
    demodulator data using ziPython's ziDAQSweeper module. The devices are first
    synchronized using the MultiDeviceSync Module, then the sweep is executed
    before stopping the synchronization.

    Requirements:

      Hardware configuration:
      The cabling of the instruments must follow the MDS cabling
      pictured in the MDS tab of LabOne.
      Additionally, connect signal output 1 of the first device (master) to
      signal input 1 of both devices using a splitter.

    Arguments:

      device_ids (list): The IDs of the devices to run the example with. For
        example, ["dev3352","dev3562"].

      amplitude (float, optional): The amplitude to set on the signal output.

      do_plot (bool, optional): Specify whether to plot the sweep. Default is no
        plot output.

     synchronize (bool, optional): Specify if multi-device synchronization will
        be started and stopped before and after the sweep

    Returns:

      data (dict): A dictionary with all the data as returend from the sweeper
        module. It contains all the demodulator data dictionaries and some
        metainformation about the sweep.


    See the "LabOne Programming Manual" for further help, available:
      - On Windows via the Start-Menu:
        Programs -> Zurich Instruments -> Documentation
      - On Linux in the LabOne .tar.gz archive in the "Documentation"
        sub-folder.
    """

    # Call a zhinst utility function that returns:
    # - an API session `daq` in order to communicate with devices via the data server.
    # - the device ID string that specifies the device branch in the server's node hierarchy.
    # - the device's discovery properties.
    # This example can't run with HF2 Instruments or instruments without the DIG option.
    apilevel_example = 6  # The API level supported by this example.
    required_devtype = r'UHFLI|MF|HF2'  # Regular expression of supported instruments.
    required_options = {}  # No special options required.
    required_err_msg = "This example requires HF2, UHFLI or MF instruments."
    (daq, device, _) = zhinst.utils.create_api_session(device_ids[0], apilevel_example,
                                                       required_devtype=required_devtype,
                                                       required_options=required_options,
                                                       required_err_msg=required_err_msg)
    for device in device_ids:
        daq.connectDevice(device, '1GbE')
    daq.sync()

    zhinst.utils.api_server_version_check(daq)

    # Create a base configuration on all devices: Disable all available outputs, awgs, demods, scopes,...
    for device in device_ids:
        zhinst.utils.disable_everything(daq, device)

    # Now configure the instrument for this experiment. The following channels
    # and indices work on all device configurations. The values below may be
    # changed if the instrument has multiple input/output channels and/or either
    # the Multifrequency or Multidemodulator options installed.
    out_channel = 0
    out_mixer_channel = 0
    in_channel = 0
    demod_index = 0
    osc_index = 0
    demod_rate = 10e3
    time_constant = 0.01
    for device in device_ids:
        exp_setting = [['/%s/sigins/%d/ac'             % (device, in_channel), 0],
                       ['/%s/sigins/%d/range'          % (device, in_channel), 2*amplitude],
                       ['/%s/demods/%d/enable'         % (device, demod_index), 1],
                       ['/%s/demods/%d/rate'           % (device, demod_index), demod_rate],
                       ['/%s/demods/%d/adcselect'      % (device, demod_index), in_channel],
                       ['/%s/demods/%d/order'          % (device, demod_index), 4],
                       ['/%s/demods/%d/timeconstant'   % (device, demod_index), time_constant],
                       ['/%s/demods/%d/oscselect'      % (device, demod_index), osc_index],
                       ['/%s/demods/%d/harmonic'       % (device, demod_index), 1],
                       ['/%s/sigouts/%d/on'            % (device, out_channel), 1],
                       ['/%s/sigouts/%d/enables/%d'    % (device, out_channel, out_mixer_channel), 1],
                       ['/%s/sigouts/%d/range'         % (device, out_channel), 2*amplitude],
                       ['/%s/sigouts/%d/amplitudes/%d' % (device, out_channel, out_mixer_channel), amplitude]]
        daq.set(exp_setting)

    # Perform a global synchronisation between the device and the data server:
    # Ensure that 1. the settings have taken effect on the device before issuing
    # the poll() command and 2. clear the API's data buffers.
    daq.sync()

    # prepare devices string to tell the sync module which devices should be synchronized (should not contain spaces)
    devices = device_ids[0]
    for device in device_ids[1:]:
        devices += ","+device

    # Here we synchronize all the devices as defined in the comma separated string "devices"
    if synchronize:
        print("Synchronizing")
        multiDeviceSyncModule = daq.multiDeviceSyncModule()
        multiDeviceSyncModule.set('start', 0)
        multiDeviceSyncModule.set('group', 0)
        multiDeviceSyncModule.execute()
        multiDeviceSyncModule.set('devices', devices)
        multiDeviceSyncModule.set('start', 1)

        timeout = 10
        tstart = time.time()
        while True:
            time.sleep(0.2)
            status = multiDeviceSyncModule.getInt('status')
            assert status != -1, "Error during device sync"
            if status == 2:
                break
            assert time.time() - tstart < timeout, "Timeout during device sync"

    print("Start sweeper")
    # Create an instance of the Sweeper Module (ziDAQSweeper class).
    sweeper = daq.sweep()
    # Configure the Sweeper Module's parameters.
    # Set the device that will be used for the sweep - this parameter must be set.
    sweeper.set('device', device_ids[0])
    # Specify the `gridnode`: The instrument node that we will sweep, the device
    # setting corresponding to this node path will be changed by the sweeper.
    sweeper.set('gridnode', 'oscs/%d/freq' % osc_index)
    # Set the `start` and `stop` values of the gridnode value interval we will use in the sweep.
    sweeper.set('start', 100)
    sweeper.set('stop', 500e3)
    # Set the number of points to use for the sweep, the number of gridnode
    # setting values will use in the interval (`start`, `stop`).
    samplecount = 100
    sweeper.set('samplecount', samplecount)
    # Specify logarithmic spacing for the values in the sweep interval.
    sweeper.set('xmapping', 1)
    # Automatically control the demodulator bandwidth/time constants used.
    # 0=manual, 1=fixed, 2=auto
    # Note: to use manual and fixed, bandwidth has to be set to a value > 0.
    sweeper.set('bandwidthcontrol', 2)
    # Sets the bandwidth overlap mode (default 0). If enabled, the bandwidth of
    # a sweep point may overlap with the frequency of neighboring sweep
    # points. The effective bandwidth is only limited by the maximal bandwidth
    # setting and omega suppression. As a result, the bandwidth is independent
    # of the number of sweep points. For frequency response analysis bandwidth
    # overlap should be enabled to achieve maximal sweep speed (default: 0). 0 =
    # Disable, 1 = Enable.
    sweeper.set('bandwidthoverlap', 0)

    # Sequential scanning mode (as opposed to binary or bidirectional).
    sweeper.set('scan', 0)
    # We don't require a fixed settling/time since there is no DUT
    # involved in this example's setup (only a simple feedback cable), so we set
    # this to zero. We need only wait for the filter response to settle,
    # specified via settling/inaccuracy.
    sweeper.set('settling/time', 0)
    # The settling/inaccuracy' parameter defines the settling time the
    # sweeper should wait before changing a sweep parameter and recording the next
    # sweep data point. The settling time is calculated from the specified
    # proportion of a step response function that should remain. The value
    # provided here, 0.001, is appropriate for fast and reasonably accurate
    # amplitude measurements. For precise noise measurements it should be set to
    # ~100n.
    # Note: The actual time the sweeper waits before recording data is the maximum
    # time specified by settling/time and defined by settling/inaccuracy.
    sweeper.set('settling/inaccuracy', 0.001)
    # Set the minimum time to record and average data to 10 demodulator
    # filter time constants.
    sweeper.set('averaging/tc', 10)
    # Minimal number of samples that we want to record and average is 100. Note,
    # the number of samples used for averaging will be the maximum number of
    # samples specified by either averaging/tc or averaging/sample.
    sweeper.set('averaging/sample', 10)

    # Now subscribe to the nodes from which data will be recorded. Note, this is
    # not the subscribe from ziDAQServer; it is a Module subscribe. The Sweeper
    # Module needs to subscribe to the nodes it will return data for.x
    paths = []
    for device in device_ids:
        paths.append('/%s/demods/%d/sample' % (device, demod_index))
    for path in paths:
        sweeper.subscribe(path)

    # Start the Sweeper's thread.
    sweeper.execute()

    start = time.time()
    timeout = 60  # [s]
    while not sweeper.finished():  # Wait until the sweep is complete, with timeout.
        time.sleep(0.5)
        progress = sweeper.progress()
        print("Individual sweep progress: {:.2%}.".format(progress[0]), end="\n")
        # Here we could read intermediate data via:
        # data = sweeper.read(True)...
        # and process it while the sweep is completing.
        # if device in data:
        # ...
        if (time.time() - start) > timeout:
            # If for some reason the sweep is blocking, force the end of the
            # measurement.
            print("\nSweep still not finished, forcing finish...")
            sweeper.finish()
    print("")

    # Read the sweep data. This command can also be executed whilst sweeping
    # (before finished() is True), in this case sweep data up to that time point
    # is returned. It's still necessary still need to issue read() at the end to
    # fetch the rest.
    return_flat_dict = True
    data = sweeper.read(return_flat_dict)
    for path in paths:
        sweeper.unsubscribe(path)

    # Check the dictionary returned is non-empty.
    assert data, "read() returned an empty data dictionary, did you subscribe to any paths?"
    # Note: data could be empty if no data arrived, e.g., if the demods were
    # disabled or had rate 0.
    for path in paths:
        assert path in data, "No sweep data in data dictionary: it has no key '%s'" % path

    if do_plot:
        import matplotlib.pyplot as plt
        _, ax = plt.subplots()

        for path in paths:
            samples = data[path]
            for sample in samples:
                frequency = sample[0]['frequency']
                R = sample[0]['r']
                ax.plot(frequency, R)

        ax.set_title('Results from %d devices.' % len(device_ids))
        ax.grid(True)
        ax.set_xlabel('Frequency ($Hz$)')
        ax.set_ylabel(r'Demodulator R ($V_\mathrm{RMS}$)')
        ax.set_xscale('log')

        plt.draw()
        plt.show()

    if synchronize:
        print("Teardown: Clearing the multiDeviceSyncModule.")
        multiDeviceSyncModule.set('start', 0)
        timeout = 2
        tstart = time.time()
        while True:
            time.sleep(0.1)
            status = multiDeviceSyncModule.getInt('status')
            assert status != -1, "Error during device sync stop"
            if status == 0:
                break
            if time.time() - tstart > timeout:
                print("Warning: Timeout during device sync stop. The devices might still be synchronized.")
                break

    return data
