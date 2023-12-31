# -*- coding: utf-8 -*-
"""
Zurich Instruments LabOne Python API Example

Python API Example for the Data Acquisition Core Module. This
example demonstrates how to obtain bursts of demodulator data when a
demodulator's R value is larger than a threshold (defined above the lowpass
filtered value of the demodulator's R) value using an tracking edge trigger.

The Module implements software triggering which operates
analogously to the types of triggering found in laboratory oscilloscopes. The
Data Acquisition Module has a non-blocking (asynchronous) interface, it starts it's
own thread to communicate with the data server.

Note: This example requires a feedback cable between Signal Output 1 and Signal
Input 1 and changes the signal output's amplitude in order to create a signal
upon which to trigger.

"""

# Copyright 2016 Zurich Instruments AG

from __future__ import print_function
import time
import numpy as np
import zhinst.utils


def run_example(device_id, amplitude=0.25, do_plot=False):
    """
    Run the example: Record bursts of demodulator sample data when a
    demodulator's R becomes larger than a specified threshold and a tracking
    trigger using ziPython's Data Acquisition Module.

    Requirements:

      Hardware configuration: Connect signal output 1 to signal input 1 with a
      BNC cable.

    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev2006` or `uhf-dev2006`.

      amplitude (float, optional): The amplitude to set on the signal output.

      do_plot (bool, optional): Specify whether to plot the recorded
        data. Default is no plot output.

    Returns:

      data (dict): The data structure as returnd by the Data Acuisition Module's
        read() command. The dictionary contains the values of the module's
        parameters, the data returned by the module and the software trigger's
        lowpass filter values.

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
    err_msg = "This example only supports instruments with demodulators."
    (daq, device, props) = zhinst.utils.create_api_session(device_id, apilevel_example,
                                                           required_devtype='.*LI|.*IA|.*IS',
                                                           required_err_msg=err_msg)
    zhinst.utils.api_server_version_check(daq)

    # Create a base configuration: Disable all available outputs, awgs, demods, scopes,...
    zhinst.utils.disable_everything(daq, device)

    # Now configure the instrument for this experiment. The following channels
    # and indices work on all device configurations. The values below may be
    # changed if the instrument has multiple input/output channels and/or either
    # the Multifrequency or Multidemodulator options installed.
    out_channel = 0
    out_mixer_channel = zhinst.utils.default_output_mixer_channel(props)
    in_channel = 0
    demod_index = 0
    osc_index = 0
    demod_rate = 10e3
    time_constant = 0.01
    frequency = 400e3
    exp_setting = [['/%s/sigins/%d/ac'             % (device, in_channel), 0],
                   ['/%s/sigins/%d/imp50'          % (device, in_channel), 0],
                   ['/%s/sigins/%d/range'          % (device, in_channel), 3*amplitude],
                   ['/%s/demods/%d/enable'         % (device, demod_index), 1],
                   ['/%s/demods/%d/rate'           % (device, demod_index), demod_rate],
                   ['/%s/demods/%d/adcselect'      % (device, demod_index), in_channel],
                   ['/%s/demods/%d/order'          % (device, demod_index), 4],
                   ['/%s/demods/%d/timeconstant'   % (device, demod_index), time_constant],
                   ['/%s/demods/%d/oscselect'      % (device, demod_index), osc_index],
                   ['/%s/demods/%d/harmonic'       % (device, demod_index), 1],
                   ['/%s/oscs/%d/freq'             % (device, osc_index), frequency],
                   ['/%s/sigouts/%d/on'            % (device, out_channel), 1],
                   ['/%s/sigouts/%d/enables/%d'    % (device, out_channel, out_mixer_channel), 1],
                   ['/%s/sigouts/%d/range'         % (device, out_channel), 1],
                   ['/%s/sigouts/%d/amplitudes/%d' % (device, out_channel, out_mixer_channel), amplitude]]
    daq.set(exp_setting)

    # Wait for the demodulator filter to settle.
    time.sleep(10*time_constant)

    # Create an instance of the Data Acquisition Module class).
    daq_module = daq.dataAcquisitionModule()

    # Below we will generate num_pulses pulses on the signal outputs in order to
    # demonstrate the triggering functionality. We'll configure the Software
    # Trigger's threshold according to these levels.
    sigouts_high = 1.5*amplitude
    sigouts_low = 1.0*amplitude
    num_pulses = 20

    # Configure the Data Acquisition Module.
    # Set the device that will be used for the trigger - this parameter must be set.
    daq_module.set('device', device)
    # We will trigger on the demodulator sample's R value.
    trigger_path = '/%s/demods/%d/sample.r' % (device, demod_index)
    triggernode = trigger_path
    daq_module.set('triggernode', triggernode)
    # Use an edge trigger.
    daq_module.set('type', 4)  # 4 = tracking edge
    daq_module.set('bandwidth', 2)
    # Trigger on the positive edge.
    daq_module.set('edge', 1)  # 1 = positive
    # The set the trigger level.
    trigger_level = (sigouts_high - sigouts_low)/5
    print("Setting level to {:.3f}.".format(trigger_level))
    daq_module.set('level', trigger_level)
    # Set the trigger hysteresis to a percentage of the trigger level: This
    # ensures that triggering is robust in the presence of noise. The trigger
    # becomes armed when the signal passes through the hysteresis value and will
    # then actually trigger if the signal additionally passes through the
    # trigger level. The hysteresis value is applied negatively for a positive
    # edge trigger relative to the trigger level (positively for a negative edge
    # trigger).
    trigger_hysteresis = 0.5*trigger_level
    print("Setting hysteresis {:.3f}.".format(trigger_hysteresis))
    daq_module.set('hysteresis', trigger_hysteresis)
    # The number of times to trigger.
    trigger_count = int(num_pulses/2)
    daq_module.set('count', trigger_count)
    daq_module.set('holdoff/count', 0)
    daq_module.set('holdoff/time', 0.100)
    trigger_delay = -0.050
    daq_module.set('delay', trigger_delay)
    demod_rate = daq.getDouble('/%s/demods/%d/rate' % (device, demod_index))
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
    daq_module.set('grid/mode', 4)
    # The length of time to record each time we trigger
    trigger_duration = 0.300
    daq_module.set('duration', trigger_duration)
    # To keep our desired duration we must calculate the number of samples so that it
    # fits with the demod sampling rate. Otherwise in exact mode, it will be adjusted to fit.
    sample_count = int(demod_rate * trigger_duration)
    daq_module.set('grid/cols', sample_count)
    trigger_duration = daq_module.getDouble('duration')
    # The size of the internal buffer used to record triggers (in seconds), this
    # should be larger than trigger_duration.
    buffer_size = daq_module.getInt('buffersize')

    # We subscribe to the same demodulator sample we're triggering on, but we
    # could additionally subscribe to other node paths.
    signal_path = '/%s/demods/%d/sample.r' % (device, demod_index)
    daq_module.subscribe(signal_path)

    # Start the Data Acquisition's thread.
    daq_module.execute()
    time.sleep(2*buffer_size)

    # Generate some pulses on the signal outputs by changing the signal output
    # mixer's amplitude. This is for demonstration only and is not necessary to
    # configure the module, we simply generate a signal upon which we can trigger.
    daq.setDouble('/%s/sigouts/%d/amplitudes/%d' % (device, out_channel, out_mixer_channel),
                  sigouts_low)
    daq.sync()
    time.sleep(0.5)
    for i in range(num_pulses):
        daq.setDouble('/%s/sigouts/%d/amplitudes/%d' % (device, out_channel, out_mixer_channel),
                      sigouts_low*(1 + 0.05*np.random.uniform(-1, 1, 1)[0]))
        daq.sync()
        time.sleep(0.2)
        daq.setDouble('/%s/sigouts/%d/amplitudes/%d' % (device, out_channel, out_mixer_channel),
                      sigouts_high*(1 + 0.05*np.random.uniform(-1, 1, 1)[0]))
        daq.sync()
        time.sleep(0.1)
        # Check and display the progress.
        progress = daq_module.progress()
        print("Data Acquisition Module progress (acquiring {:d} triggers): {:.2%}.".format(
            trigger_count, progress[0]), end="\r")
        # Check whether the Data Acquisition Module has finished.
        if daq_module.finished():
            print("\nTrigger is finished.")
            break
    print("")
    daq.setDouble('/%s/sigouts/%d/amplitudes/%d' % (device, out_channel, out_mixer_channel), sigouts_low)

    # Wait for the Data Acquisition's buffers to finish processing the triggers.
    time.sleep(2*buffer_size)

    # Read the Data Acquisition's data, this command can also be executed before
    # daq_module.finished() is True. In that case data recorded up to that point in
    # time is returned and we would still need to issue read() at the end to
    # fetch the rest of the data.
    return_flat_data_dict = True
    data = daq_module.read(return_flat_data_dict)

    # Stop the Module (this is also ok if daq_module.finished() is True).
    daq_module.finish()

    # Check that the dictionary returned is non-empty.
    assert data, "read() returned an empty data dictionary, did you subscribe to any paths?"
    # Note: data could be empty if no data arrived, e.g., if the demods were
    # disabled or had rate 0
    assert signal_path in data, "no data recorded: data dictionary has no key `{}`.".format(signal_path)
    samples = data[signal_path]
    print("Data Acquisition's read() returned {} signal segments.".format(len(samples)))
    assert len(samples) == trigger_count, \
        "Unexpected number of signal segments returned: `{}`. Expected: `{}`.".format(len(samples), trigger_count)

    # Get the sampling rate of the device's ADCs, the device clockbase.
    clockbase = float(daq.getInt('/%s/clockbase' % device))
    # Use the clockbase to calculate the duration of the first signal segment's
    # demodulator data, the segments are accessed by indexing `samples`.
    dt_seconds = (samples[0]['timestamp'][0][-1] - samples[0]['timestamp'][0][0])/clockbase
    print("The first signal segment contains {:.3f} seconds of demodulator data.".format(dt_seconds))

    if do_plot and samples:

        import matplotlib.pyplot as plt
        import matplotlib.cm as cm
        _, ax = plt.subplots()
        # Plot some relevant Data Acquisition parameters.
        ax.axvline(0.0, linewidth=2, linestyle='--', color='k', label="Trigger time")
        ax.axvline(trigger_delay, linewidth=2, linestyle='--', color='grey', label='delay')
        ax.axvline(trigger_duration + trigger_delay, linewidth=2, linestyle=':', color='k',
                   label='duration + delay')
        ax.axhline(trigger_level, linewidth=2, linestyle='-', color='k', label='level')
        ax.axhline(trigger_level - trigger_hysteresis, linewidth=2, linestyle='-.', color='k',
                   label='hysteresis')
        ax.axvspan(trigger_delay, trigger_duration + trigger_delay, alpha=0.2, color='grey')
        ax.axhspan(trigger_level, trigger_level - trigger_hysteresis, alpha=0.5, color='grey')
        # Plot the signal segments returned by the Data Acquisition.
        colors = cm.rainbow(np.linspace(0, 1, len(samples)))
        for i, sample in enumerate(samples):
            # Align the triggers using their trigger timestamps which are stored in the chunk header "changed"
            # timestamp. This is the timestamp of the last acquired trigger. Note that with the new software trigger,
            # the trigger timestamp has the trigger offset added to it, so we need to subtract it to get the sample and
            # trigger timestamps to align.
            trigger_ts = sample['header']['changedtimestamp'] - int(sample['header']['gridcoloffset'] * clockbase)
            t = (sample['timestamp'] - float(trigger_ts))/clockbase
            ax.plot(t[0], sample['value'][0], color=colors[i])

            # Plot the tracking trigger's lowpass filter values. This allows us
            # to verify that the filter's bandwidth (bandwidth) is
            # configured appropriately.
            lowpass_path = '/%s/trigger/lowpass' % device
            t_lowpass = (data[lowpass_path][i]['timestamp'] - float(trigger_ts))/clockbase
            value_lowpass = data[lowpass_path][i]['value']
            ax.plot(t_lowpass[0], value_lowpass[0], '--', color=colors[i])

        ax.grid(True)
        ax.set_title(("Data Acquisition's read() returned {} segments of demodulator data\n".format(len(samples)),
                      "each with a duration of {:.3f} seconds".format(trigger_duration)))
        ax.set_xlabel('Time, relative to the trigger time ($s$)')
        ax.set_ylabel(r'Demodulator R ($V_\mathrm{RMS}$)')
        ax.set_ylim([round(0.5*amplitude, 2), round(1.5*amplitude, 2)])
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, fontsize='small')
        plt.draw()
        plt.show()

    return data
