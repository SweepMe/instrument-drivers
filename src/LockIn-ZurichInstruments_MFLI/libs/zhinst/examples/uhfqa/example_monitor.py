# -*- coding: utf-8 -*-
""" Run a basic test of the input averager.
"""

# Copyright 2018 Zurich Instruments AG

from __future__ import print_function
import time
import textwrap

import zhinst.utils

from .common import initialize_device, acquisition_poll


def run_example(device_id, vector_length=4000, monitor_length=4000, num_averages=256, do_plot=True):
    """ Run a basic test of the input averager.

    The example plays gaussian waveforms on each output using the AWG and runs
    the monitor to record them.

    Requirements:

      - Connect signal output 1 to signal input 1.
      - Connect signal output 2 to signal input 2.

    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev2006` or `uhf-dev2006`.

      vector_length (int): Length of the output waveform.

      do_plot (bool, optional): Specify whether to plot the polled data.

    Returns:

      data (dict): Measurement result.

    """
    apilevel_example = 6  # The API level supported by this example.
    # Call a zhinst utility function that returns:
    # - an API session `daq` in order to communicate with devices via the data server.
    # - the device ID string that specifies the device branch in the server's node hierarchy.
    # - the device's discovery properties.
    required_devtype = 'UHFQA'
    required_options = None
    daq, device, _ = zhinst.utils.create_api_session(device_id, apilevel_example,
                                                     required_devtype=required_devtype,
                                                     required_options=required_options)

    # Perform initialization for UHFQA examples
    initialize_device(daq, device)

    # Configure AWG to output gaussian pulses on output 1 and 2
    awg_program = textwrap.dedent("""\
    const LENGTH = ${LENGTH};
    wave w = gauss(LENGTH, LENGTH/2, LENGTH/8);

    var loop_cnt = getUserReg(0);
    var wait_time = 0;

    repeat(loop_cnt) {
      setTrigger(0);
      playWave(w, -w);
      wait(50);
      setTrigger(AWG_MONITOR_TRIGGER);
      setTrigger(0);
      waitWave();
      wait(1000);
    }
    """).replace('${LENGTH}', '{:d}'.format(vector_length))

    # Provide number of averages in user register
    daq.setDouble('/{:s}/awgs/0/userregs/0'.format(device), num_averages)

    # Create an instance of the AWG module
    awgModule = daq.awgModule()
    awgModule.set('device', device)
    awgModule.set('index', 0)
    awgModule.execute()

    # Transfer the AWG sequence program. Compilation starts automatically.
    awgModule.set('compiler/sourcestring', awg_program)
    while awgModule.getInt('compiler/status') == -1:
        time.sleep(0.1)

    # Ensure that compilation was successful
    assert awgModule.getInt('compiler/status') != 1

    # Enable outputs
    daq.setInt('/{:s}/sigouts/*/on'.format(device), 1)

    # Setup monitor
    daq.setInt('/{:s}/qas/0/monitor/averages'.format(device), num_averages)
    daq.setInt('/{:s}/qas/0/monitor/length'.format(device), monitor_length)
    monitor_length = daq.getInt('/{:s}/qas/0/monitor/length'.format(device))

    # Now we're ready for readout. Enable monitor and start acquisition.
    daq.setInt('/{:s}/qas/0/monitor/reset'.format(device), 1)
    daq.setInt('/{:s}/qas/0/monitor/enable'.format(device), 1)
    daq.sync()

    # Subscribe to monitor waves
    paths = []
    for channel in range(2):
        path = '/{:s}/qas/0/monitor/inputs/{:d}/wave'.format(device, channel)
        paths.append(path)
    daq.subscribe(paths)

    # Arm the device
    daq.asyncSetInt('/{:s}/awgs/0/single'.format(device), 1)
    daq.syncSetInt('/{:s}/awgs/0/enable'.format(device), 1)

    # Perform acquisition
    print('Acquiring data...')
    data = acquisition_poll(daq, paths, monitor_length)
    print('Done.')

    # Stop monitor
    daq.unsubscribe(paths)
    daq.setInt('/{:s}/qas/0/monitor/enable'.format(device), 0)

    if do_plot:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.set_title('Input averager results after {:d} measurements'.format(num_averages))
        ax.set_ylabel('Amplitude (a.u.)')
        ax.set_xlabel('Sample (#)')
        for path, samples in data.items():
            ax.plot(samples, label='Readout {}'.format(path))
        plt.legend(loc='best')
        fig.set_tight_layout(True)
        plt.show()

    return data
