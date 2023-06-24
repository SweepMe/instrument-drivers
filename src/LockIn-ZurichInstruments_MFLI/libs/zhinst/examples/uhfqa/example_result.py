# -*- coding: utf-8 -*-
""" Run a basic test of the result unit.
"""

# Copyright 2018 Zurich Instruments AG

from __future__ import print_function
import time
import textwrap
import numpy as np

import zhinst.utils

from .common import initialize_device, acquisition_poll
from .common import ResultLoggingSource


def run_example(device_id, result_length=2600, num_averages=1, do_plot=True):
    """ Run a basic test of the result unit.

    This example demonstrates how to use the result unit for acquiring data
    after weighted integration, rotation, and crosstalk suppression.

    A single non-zero coefficient in each weighting function is activated. As a
    consequence, the result unit will sample just a single input sample each
    time it is started. We then configure the AWG to output a bipolar square
    wave. The AWG plays the waveform in a loop for each measurement and all
    averages. The AWG sweeps the starting point of the integration for each
    measurement. The final result is that we record essentially the input
    waveform using the result unit. The step size corresponds to the wait time
    in the AWG, which is 4.44 ns. Finally, we configure a different coefficient
    for each of the 10 input channels to enable the user to differentiate the
    channels in the plot output.

    Requirements:

      - Connect signal output 1 to signal input 1.
      - Connect signal output 2 to signal input 2.

    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev2006` or `uhf-dev2006`.

      result_length (int): Number of measurements.

      num_averages (int): Number of averages per measurement.

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

    # Configure AWG
    awg_program = textwrap.dedent("""\
    const RATE = 0;
    const FS = 1.8e9*pow(2, -RATE);
    const LENGTH = 1.0e-6;
    const N = floor(LENGTH*FS);

    wave w = join(zeros(64), ones(10000), -ones(10000));

    setTrigger(AWG_INTEGRATION_ARM);
    var loop_cnt = getUserReg(0);
    var avg_cnt = getUserReg(1);
    var wait_delta = 1;

    repeat (avg_cnt) {
        var wait_time = 0;

        repeat(loop_cnt) {
            wait_time += wait_delta;
            playWave(w, w);
            wait(wait_time);
            setTrigger(AWG_INTEGRATION_TRIGGER + AWG_INTEGRATION_ARM);
            setTrigger(AWG_INTEGRATION_ARM);
            waitWave();
            wait(1024);
        }
    }

    setTrigger(0);
    """)

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

    # Apply a rotation on half the channels to get the imaginary part instead
    for i in range(5):
        daq.setComplex('/{:s}/qas/0/rotations/{:d}'.format(device, i), 1)
        daq.setComplex('/{:s}/qas/0/rotations/{:d}'.format(device, i+5), -1j)

    # Channels to test
    channels = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    # Configuration of weighted integration
    #
    # A single non-zero coefficient in each weighting function is activated.
    # As a consequence, the result unit will sample just a single input
    # sample each time it is started.
    weights = np.linspace(1.0, 0.1, 10)
    for i in channels:
        w = np.array([weights[i]])
        daq.setVector('/{:s}/qas/0/integration/weights/{}/real'.format(device, i), w)
        daq.setVector('/{:s}/qas/0/integration/weights/{}/imag'.format(device, i), w)

    daq.setInt('/{:s}/qas/0/integration/length'.format(device), 1)
    daq.setInt('/{:s}/qas/0/integration/mode'.format(device), 0)
    daq.setInt('/{:s}/qas/0/delay'.format(device), 0)

    # Provide result length and number of averages in user register
    daq.setDouble('/{:s}/awgs/0/userregs/0'.format(device), result_length)
    daq.setDouble('/{:s}/awgs/0/userregs/1'.format(device), num_averages)

    # Configure the result unit
    daq.setInt('/{:s}/qas/0/result/length'.format(device), result_length)
    daq.setInt('/{:s}/qas/0/result/averages'.format(device), num_averages)
    daq.setInt('/{:s}/qas/0/result/source'.format(device), ResultLoggingSource.TRANS)

    # Now we're ready for readout. Enable result unit and start acquisition.
    daq.setInt('/{:s}/qas/0/result/reset'.format(device), 1)
    daq.setInt('/{:s}/qas/0/result/enable'.format(device), 1)
    daq.sync()

    # Subscribe to result waves
    paths = []
    for ch in channels:
        path = '/{:s}/qas/0/result/data/{:d}/wave'.format(device, ch)
        paths.append(path)
    daq.subscribe(paths)

    # Arm the device
    daq.asyncSetInt('/{:s}/awgs/0/single'.format(device), 1)
    daq.syncSetInt('/{:s}/awgs/0/enable'.format(device), 1)

    # Perform acquisition
    print('Acquiring data...')
    data = acquisition_poll(daq, paths, result_length)
    print('Done.')

    # Stop result unit
    daq.unsubscribe(paths)
    daq.setInt('/{:s}/qas/0/result/enable'.format(device), 0)

    if do_plot:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(12, 4))
        ax.set_title('Result unit')
        ax.set_ylabel('Amplitude (a.u.)')
        ax.set_xlabel('Measurement (#)')
        for path, samples in data.items():
            ax.plot(samples, label='{}'.format(path))
        plt.legend(loc='best')
        fig.set_tight_layout(True)
        plt.show()

    return data
