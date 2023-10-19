# -*- coding: utf-8 -*-
"""
Zurich Instruments LabOne Python API Example.

Demonstrate how to perform a Fast Fourier Transform on demodulator data using
the Spectrum Analyser Module, which corresponds to ziPython's ziDAQZoomFFT
class.

"""

# Copyright 2016 Zurich Instruments AG

from __future__ import print_function
import time
import numpy as np
import zhinst.utils


def run_example(device_id, amplitude=0.1, do_plot=False):
    """
    Run the example: Perform a zoom FFT using ziPython's ziDAQZoomFFT module.

    Requirements:

      Hardware configuration: Connect signal output 1 to signal input 1 with a
      BNC cable.

    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev2006` or `uhf-dev2006`.

      amplitude (float, optional): The amplitude to set on the signal output.

      do_plot (bool, optional): Specify whether to plot the zoomFFT. Default is
        no plot output.

    Returns:

      sample (list of dict): A list of demodulator sample dictionaries. Each
        entry in the list correspond to the result of a single zoomFFT.

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
    frequency = 400e3
    time_constant = 8e-5
    exp_setting = [['/%s/sigins/%d/ac'             % (device, in_channel), 0],
                   ['/%s/sigins/%d/imp50'          % (device, in_channel), 0],
                   ['/%s/sigins/%d/range'          % (device, in_channel), 2*amplitude],
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
    # Some other device-type dependent configuration may be required. For
    # example, disable the signal inputs `diff` and the signal outputs `add` for
    # HF2 instruments.
    if props['devicetype'].startswith('HF2'):
        exp_setting.append(['/%s/sigins/%d/diff'      % (device, in_channel), 0])
        exp_setting.append(['/%s/sigouts/%d/add'      % (device, out_channel), 0])
    daq.set(exp_setting)

    # Wait for the demodulator filter to settle
    timeconstant_set = daq.getDouble('/%s/demods/%d/timeconstant' % (device, demod_index))
    time.sleep(10*timeconstant_set)

    # Perform a global synchronisation between the device and the data server:
    # Ensure that 1. the settings have taken effect on the device before issuing
    # the poll() command and 2. clear the API's data buffers. Note: the sync()
    # must be issued after waiting for the demodulator filter to settle above.
    daq.sync()

    # Create an instance of the Spectrum Analyser Module (ziDAQZoomFFT class).
    zoomfft = daq.zoomFFT()

    # Configure the module's parameters.
    # Set the device that will be used for the spectrum analyser - this parameter must be set.
    zoomfft.set('device', device)
    # Select FFT(X + iY).
    zoomfft.set('mode', 0)
    # Disable overlap mode.
    zoomfft.set('overlap', 0)
    # Use a Hann windowing function in the FFT:
    # 0=Rectangular, 1=Hann, 2=Hamming, 3=Blackman Harris,
    # 16=Exponential, 17=Cosine, 18=Cosine squared.
    zoomfft.set('window', 1)
    # Return absolute frequencies instead of relative to 0.
    zoomfft.set('absolute', 1)
    # The number of lines is 2**bits.
    zoomfft.set('bit', 16)
    # The number of zoomFFT's to perform.
    loopcount = 2
    zoomfft.set('loopcount', loopcount)

    # Now subscribe to the nodes from which data will be recorded. Note, this is
    # not the subscribe from ziDAQServer; it is a Module subscribe. The Spectrum
    # Analyzer Module needs to subscribe to the nodes it will return data for.
    path = '/%s/demods/%d/sample' % (device, demod_index)
    zoomfft.subscribe(path)

    # Start the zoomFFT.
    zoomfft.execute()

    start = time.time()
    timeout = 60  # [s]
    print("Will perform", loopcount, "zoomFFTs.")
    while not zoomfft.finished():
        time.sleep(0.2)
        # Please note: progress() and finish() works for first zoomFFT, but
        # It's a known issue that it doesn't update for subsequent zoomFFTs
        progress = zoomfft.progress()
        print("Individual zoomFFT progress: {:.2%}.".format(progress[0]), end="\r")

        # We could read intermediate data calculated by the Module using read()
        # data = zoomfft.read()...
        # and process it:
        # if device in data:
        # ...
        if (time.time() - start) > timeout:
            # If for some reason the zoomFFT is blocking, force the end of the
            # measurement.
            print("\nzoomFFT still not finished, forcing finish...")
            zoomfft.finish()
    print("")

    # Read the zoomFFT data. this command can also be executed whilst the
    # zoomFFT is still being calculated (before finished() is True), in this
    # case zoomFFT data up to that time point is returned. it's still
    # necessary to issue read() at the end to fetch the rest.
    return_flat_data_dict = True
    data = zoomfft.read(return_flat_data_dict)
    zoomfft.unsubscribe(path)

    # Check that the dictionary returned is non-empty.
    assert data, "read() returned an empty data dictionary, did you subscribe to any paths?"
    # Note: data could be empty if no data arrived, e.g., if the demods were
    # disabled or had rate 0.
    assert path in data, "data dictionary has no key '%s'" % path
    samples = data[path]
    print("Returned zoomFFT data contains", len(samples), "FFTs.")
    assert len(samples) == loopcount, \
        "The zoomFFT returned an unexpected number of FFTs: `%d`. Expected: `%d`." % (len(samples), loopcount)
    print("Number of lines in the first zoomFFT: {:d}.".format(len(samples[0][0]['grid'])))

    if do_plot:
        import matplotlib.pyplot as plt
        plot_idx = 0
        print("Will plot result of the zoomFFT result {:d}.".format(plot_idx))
        frequencies = samples[plot_idx][0]['grid']/1e3
        r = samples[plot_idx][0]['r']
        filter_data = samples[plot_idx][0]['filter']

        _, (ax1, ax2) = plt.subplots(2)
        ax1.set_title('Spectrum Analyser Module Result')
        # Plot in dBV (=dBVRMS), r is in VRMS and and signal output amplitude is Vpp.
        ax1.plot(frequencies, 20*np.log10(r*np.sqrt(2)/amplitude))
        ax1.grid(True)
        ax1.set_xlabel('Frequency (kHz)')
        ax1.set_ylabel('FFT(R) (dBV)')
        ax1.autoscale(True, 'both', True)

        ax2.plot(frequencies, 20*np.log10((r/filter_data)*np.sqrt(2)/amplitude))
        ax2.grid(True)
        ax2.set_xlabel('Frequency (kHz)')
        ax2.set_ylabel('FFT(R) (dBV)\n with Demod Filter Compensation')
        ax2.autoscale(True, 'both', True)

        plt.show()

    return samples
