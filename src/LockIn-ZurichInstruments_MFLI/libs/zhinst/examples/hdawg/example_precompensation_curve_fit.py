"""
Zurich Instruments LabOne Python API Example

Demonstrate how to connect to a Zurich Instruments HDAWG and
use the precompensation module to fit filter parameters for a
measured signal
"""

# Copyright 2019 Zurich Instruments AG

from __future__ import print_function
import time
import numpy as np
import zhinst.ziPython


def get_precompensated_signal(module_handle, input_signal, amplitude, timeconstant):
    """
    Uploads the input_signal to the precompensationAdvisor module and returns the
    simulated forward transformed signal with an exponential filter(amplitude,timeconstant).
    """
    module_handle.set('exponentials/0/amplitude', amplitude)
    module_handle.set('exponentials/0/timeconstant', timeconstant)
    module_handle.set("wave/input/inputvector", input_signal)
    return np.array(module_handle.get("wave/output/forwardwave", True)['/wave/output/forwardwave'][0]['x'])


def run_example(device_id, do_plot=True):
    """
    Run the example: Connect to a Zurich Instruments HDAWG. The example uploads a signal to
    the precompensationAdvisor module and reads back the filtered signal. This functionality
    is used to feed a fitting algorithm for fitting filter parameters.

    Requirements:
      HDAWG


    Arguments:

      device_id (str): The ID of the device to run the example with. For
        example, `dev8050`.

      do_plot (bool, optional): Specify whether to plot the initial, target and fitted signals.


    See the "LabOne Programming Manual" for further help, available:
      - On Windows via the Start-Menu:
        Programs -> Zurich Instruments -> Documentation
      - On Linux in the LabOne .tar.gz archive in the "Documentation"
        sub-folder.
    """
    # Settings
    apilevel_example = 6  # The API level supported by this example.
    err_msg = "This example can only be ran on an HDAWG."
    # Call a zhinst utility function that returns:
    # - an API session `daq` in order to communicate with devices via the data server.
    # - the device ID string that specifies the device branch in the server's node hierarchy.
    # - the device's discovery properties.
    (daq, device, _) = zhinst.utils.create_api_session(device_id, apilevel_example, required_devtype='HDAWG',
                                                       required_err_msg=err_msg)
    zhinst.utils.api_server_version_check(daq)

    # Create a base configuration: Disable all available outputs, awgs, demods, scopes,...
    zhinst.utils.disable_everything(daq, device)

    pre = daq.precompensationAdvisor()

    sampling_rate = 2.4e9

    x, target_signal = generate_target_signal(sampling_rate=sampling_rate)
    actual_signal = generate_actual_signal(target_signal, sampling_rate=sampling_rate)

    # prepare the precompensationAdvisor module
    pre.set("exponentials/0/enable", 1)
    pre.set("wave/input/source", 3)
    pre.set("device", device_id)
    daq.setDouble("/" + device_id + "/system/clocks/sampleclock/freq", sampling_rate)
    # a short pause is needed for the precompensationAdvisor module to read
    # the updated the sampling rate from the device node
    time.sleep(0.05)
    sampling_rate = pre.getDouble("samplingfreq")

    # Fitting the parameters
    from lmfit import Model
    gmodel = Model(get_precompensated_signal, independent_vars=['module_handle', 'input_signal'])
    result = gmodel.fit(target_signal,
                        input_signal=actual_signal,
                        module_handle=pre,
                        amplitude=0.,
                        timeconstant=1e-4,
                        fit_kws={'epsfcn':  1e-3})  # 'epsfcn' is needed as filter parameters are discretized
                                                    # in precompensationAdvisor module, otherwise fitting will
                                                    # not converge

    print(result.fit_report())
    if do_plot:
        import matplotlib.pyplot as plt
        _, ax = plt.subplots()
        ax.plot(x, result.init_fit, 'k', label='initial signal')
        ax.plot(x, result.best_fit, 'r', label='fitted signal')
        ax.plot(x, target_signal, 'b', label='target signal')
        ax.legend()
        ax.ticklabel_format(axis='both', style='sci', scilimits=(-2, 2))
        ax.set_xlabel("time [s]")
        ax.set_ylabel("Amplitude")
        plt.show()


def generate_target_signal(min_x=-96, max_x=5904, sampling_rate=2.4e9):
    """Returns a step function with given length and sampling interval."""
    x_values = np.array(range(min_x, max_x))
    x_values = [element/sampling_rate for element in x_values]
    signal2 = np.array(np.concatenate((np.zeros(-min_x), np.ones(max_x))))
    return x_values, signal2


def generate_actual_signal(initial_signal, amp=0.4, tau=100e-9, sampling_rate=2.4e9):
    """
    generate "actual signal" through filtering the initial signal with
    an exponential filter and add noise
    """
    from scipy import signal
    # calculate a and b from amplitude and tau
    alpha = 1 - np.exp(-1/(sampling_rate*tau*(1+amp)))
    if amp >= 0.0:
        k = amp/(1+amp-alpha)
        a = [(1-k + k*alpha), -(1-k)*(1-alpha)]
    else:
        k = -amp/(1+amp)/(1-alpha)
        a = [(1 + k - k*alpha), -(1+k)*(1-alpha)]
    b = [1, -(1-alpha)]

    distorted_signal = np.array(signal.lfilter(b, a, initial_signal) +
                                0.01 * np.random.normal(size=initial_signal.size))
    return distorted_signal
