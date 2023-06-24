# -*- coding: utf-8 -*-
"""
Demonstrate how to synchronize 2 or more MFLI
instruments or 2 or more UHFLI instruments using the MDS capability of LabOne.
It also measures the temporal response of demodulator filters of both
both instruments using the Data Acquisition (DAQ) Module.

Copyright 2008-2018 Zurich Instruments AG
"""

from __future__ import print_function
import time
import zhinst.utils


def run_example(device_ids, do_plot=False, synchronize=True):
    """
    Run the example: Capture demodulator data from two devices using the Data Acquisition module.
    The devices are first synchronized using the MultiDeviceSync Module.

    Hardware configuration:
    The cabling of the instruments must follow the MDS cabling depicted in
    the MDS tab of LabOne.
    Additionally, Signal Out 1 of the master device is split into Signal In 1 of the master and slave.

    Arguments:

      device_ids (list): The IDs of the devices to run the example with. For
        example, ["dev3352","dev3562"]. The first device is the master.
        NOTE The devices must be of the same type, either 2 or more UHF or 2 or more MF instruments.

      do_plot (bool, optional): Specify whether to plot the data acquisition. Default is no
        plot output.

     synchronize (bool, optional): Specify if multi-device synchronization will
        be started and stopped before and after the data acquisition

    Returns:

      data (dict): A dictionary with all the data as returend from the sweeper
        module. It contains all the demodulator data dictionaries and some
        metainformation about the data acquisition.


    See the "LabOne Programming Manual" for further help, available:
      - On Windows via the Start-Menu:
        Programs -> Zurich Instruments -> Documentation
      - On Linux in the LabOne .tar.gz archive in the "Documentation"
        sub-folder.
    """

    # Check if the master device ID exists
    if (not isinstance(device_ids, list)) or (not device_ids):
        raise Exception("No value for master_id specified. The first argument to the "
                        "example should contain at least 2 device IDs, "
                        "e.g. ['dev2006', 'dev2007'] or ['uhf-dev2006', 'uhf-dev2007'].")

    # Check if the slave device ID exists
    if len(device_ids) < 2:
        raise Exception("No value for slave_id specified. The first argument to the "
                        "example should contain at least 2 device IDs, "
                        "e.g. ['dev2006', 'dev2007'] or ['uhf-dev2006', 'uhf-dev2007'].")

    #  Connection to the data server and devices

    # Connection to the local server 'localhost' ^= '127.0.0.1'
    apilevel = 6
    daq = zhinst.ziPython.ziDAQServer('localhost', 8004, apilevel)
    discovery = zhinst.ziPython.ziDiscovery()

    # Master and slave device ID
    props = []
    for device_id in device_ids:
        device_serial = discovery.find(device_id).lower()
        props.append(discovery.get(device_serial))
    devices = props[0]['deviceid']
    for prop in props[1:]:
        devices += ","+prop['deviceid']
    # Switching between MFLI and UHFLI
    device_type = props[0]['devicetype']
    for prop in props[1:]:
        if prop['devicetype'] != device_type:
            raise Exception("This example needs 2 or more MFLI instruments or 2 or more UHFLI instruments."
                            "Mixing device types is not possible")

    for prop in props:
        if prop['devicetype'] == 'UHFLI':
            daq.connectDevice(prop['deviceid'], prop['interfaces'][0])
        else:
            daq.connectDevice(prop['deviceid'], '1GbE')

    # Disable all available outputs, demods, ...
    for prop in props:
        zhinst.utils.disable_everything(daq, prop['deviceid'])

    #  Device synchronization
    if synchronize:
        print("Synchronizing devices %s ...\n" % devices)
        mds = daq.multiDeviceSyncModule()
        mds.set('start', 0)
        mds.set('group', 0)
        mds.execute()
        mds.set('devices', devices)
        mds.set('start', 1)

        timeout = 20
        start = time.time()
        status = 0
        while status != 2:
            time.sleep(0.2)
            status = mds.getInt('status')
            if status == -1:
                raise Exception('Error during device sync')
            if (time.time() - start) > timeout:
                raise Exception('Timeout during device sync')

        print("Devices successfully synchronized.")

    # Device settings
    demod_c = 0  # demod channel, for paths on the device
    out_c = 0  # signal output channel
    # Get the value of the instrument's default Signal Output mixer channel.
    prop = discovery.get(props[0]['deviceid'])
    out_mixer_c = zhinst.utils.default_output_mixer_channel(prop, out_c)
    in_c = 0  # signal input channel
    osc_c = 0  # oscillator

    time_constant = 1.0e-3  # [s]
    demod_rate = 10e3  # [Sa/s]
    filter_order = 8
    osc_freq = 1e3  # [Hz]
    out_amp = 0.600   # [V]

    # Master device settings
    master = props[0]['deviceid'].lower()
    daq.setInt('/%s/sigouts/%d/on' % (master, out_c), 1)
    daq.setDouble('/%s/sigouts/%d/range' % (master, out_c), 1)
    daq.setDouble('/%s/sigouts/%d/amplitudes/%d' % (master, out_c, out_mixer_c), out_amp)
    daq.setDouble('/%s/demods/%d/phaseshift' % (master, demod_c), 0)
    daq.setInt('/%s/demods/%d/order' % (master, demod_c), filter_order)
    daq.setDouble('/%s/demods/%d/rate' % (master, demod_c), demod_rate)
    daq.setInt('/%s/demods/%d/harmonic' % (master, demod_c), 1)
    daq.setInt('/%s/demods/%d/enable' % (master, demod_c), 1)
    daq.setInt('/%s/demods/%d/oscselect' % (master, demod_c), osc_c)
    daq.setInt('/%s/demods/%d/adcselect' % (master, demod_c), in_c)
    daq.setDouble('/%s/demods/%d/timeconstant' % (master, demod_c), time_constant)
    daq.setDouble('/%s/oscs/%d/freq' % (master, osc_c), osc_freq)
    daq.setInt('/%s/sigins/%d/imp50' % (master, in_c), 1)
    daq.setInt('/%s/sigins/%d/ac' % (master, in_c), 0)
    daq.setDouble('/%s/sigins/%d/range' % (master, in_c), out_amp/2)
    daq.setDouble('/%s/sigouts/%d/enables/%d' % (master, out_c, out_mixer_c), 0)
    # Slave device settings
    for prop in props[1:]:
        slave = prop['deviceid'].lower()
        daq.setDouble('/%s/demods/%d/phaseshift' % (slave, demod_c), 0)
        daq.setInt('/%s/demods/%d/order' % (slave, demod_c), filter_order)
        daq.setDouble('/%s/demods/%d/rate' % (slave, demod_c), demod_rate)
        daq.setInt('/%s/demods/%d/harmonic' % (slave, demod_c), 1)
        daq.setInt('/%s/demods/%d/enable' % (slave, demod_c), 1)
        daq.setInt('/%s/demods/%d/oscselect' % (slave, demod_c), osc_c)
        daq.setInt('/%s/demods/%d/adcselect' % (slave, demod_c), in_c)
        daq.setDouble('/%s/demods/%d/timeconstant' % (slave, demod_c), time_constant)
        daq.setDouble('/%s/oscs/%d/freq' % (slave, osc_c), osc_freq)
        daq.setInt('/%s/sigins/%d/imp50' % (slave, in_c), 1)
        daq.setInt('/%s/sigins/%d/ac' % (slave, in_c), 0)
        daq.setDouble('/%s/sigins/%d/range' % (slave, in_c), out_amp/2)
    # Synchronization
    daq.sync()
    time.sleep(1)

    #  measuring the transient state of demodulator filters using DAQ module

    # DAQ module
    # Create a Data Acquisition Module instance, the return argument is a handle to the module
    daq_module = daq.dataAcquisitionModule()
    # Configure the Data Acquisition Module
    # Device on which trigger will be performed
    daq_module.set('device', master)
    # The number of triggers to capture (if not running in endless mode).
    daq_module.set('count', 1)
    daq_module.set('endless', 0)
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
    grid_mode = 2
    daq_module.set('grid/mode', grid_mode)
    #   type
    #     NO_TRIGGER = 0
    #     EDGE_TRIGGER = 1
    #     DIGITAL_TRIGGER = 2
    #     PULSE_TRIGGER = 3
    #     TRACKING_TRIGGER = 4
    #     HW_TRIGGER = 6
    #     TRACKING_PULSE_TRIGGER = 7
    #     EVENT_COUNT_TRIGGER = 8
    daq_module.set('type', 1)
    #   triggernode, specify the triggernode to trigger on.
    #     SAMPLE.X = Demodulator X value
    #     SAMPLE.Y = Demodulator Y value
    #     SAMPLE.R = Demodulator Magnitude
    #     SAMPLE.THETA = Demodulator Phase
    #     SAMPLE.AUXIN0 = Auxilliary input 1 value
    #     SAMPLE.AUXIN1 = Auxilliary input 2 value
    #     SAMPLE.DIO = Digital I/O value
    triggernode = '/%s/demods/%d/sample.r' % (master, demod_c)
    daq_module.set('triggernode', triggernode)
    #   edge:
    #     POS_EDGE = 1
    #     NEG_EDGE = 2
    #     BOTH_EDGE = 3
    daq_module.set('edge', 1)
    demod_rate = daq.getDouble('/%s/demods/%d/rate' % (master, demod_c))
    # Exact mode: To preserve our desired trigger duration, we have to set
    # the number of grid columns to exactly match.
    trigger_duration = time_constant*30
    sample_count = demod_rate*trigger_duration
    daq_module.set('grid/cols', sample_count)
    # The length of each trigger to record (in seconds).
    daq_module.set('duration', trigger_duration)
    daq_module.set('delay', -trigger_duration/4)
    # Do not return overlapped trigger events.
    daq_module.set('holdoff/time', 0)
    daq_module.set('holdoff/count', 0)
    daq_module.set('level', out_amp/6)
    # The hysterisis is effectively a second criteria (if non-zero) for triggering
    # and makes triggering more robust in noisy signals. When the trigger `level`
    # is violated, then the signal must return beneath (for positive trigger edge)
    # the hysteresis value in order to trigger.
    daq_module.set('hysteresis', 0.01)
    # synchronizing the settings
    daq.sync()

    #  Recording

    # Subscribe to the demodulators
    daq_module.unsubscribe('*')
    master_subscribe_node = '/%s/demods/%d/sample.r' % (master, demod_c)
    daq_module.subscribe(master_subscribe_node)
    for prop in props[1:]:
        slave_subscribe_node = '/%s/demods/%d/sample.r' % (prop['deviceid'], demod_c)
        daq_module.subscribe(slave_subscribe_node)

    # Execute the module
    daq_module.execute()
    # Send a trigger
    daq.setDouble('/%s/sigouts/%d/enables/%d' % (master, out_c, out_mixer_c), 1)

    # wait for the acquisition to be finished
    while not daq_module.finished():
        time.sleep(1)
        print("Progress {:.2%}".format(daq_module.progress()[0]), end="\r")

    # Read the result
    result = daq_module.read(True)

    # Turn off the trigger
    daq.setDouble('/%s/sigouts/%d/enables/%d' % (master, out_c, out_mixer_c), 0)
    # Finish the DAQ module
    daq_module.finish()

    #  Extracting and plotting the data

    if do_plot:

        # Master data
        master_clockbase = daq.getDouble('/%s/clockbase' % master)
        timestamp = result[master_subscribe_node][0]['timestamp']
        master_time = (timestamp[0] - float(timestamp[0][0])) / master_clockbase
        demod_r_master = result[master_subscribe_node][0]['value'][0]
        # Plotting
        import matplotlib.pyplot as plt

        _, (ax1, ax2) = plt.subplots(2)
        ax1.plot(master_time*1E3, demod_r_master*1E3, color='blue')
        ax1.set_ylabel('Amplitude [mV]', fontsize=12, color='k')
        ax1.legend(['Master'])
        ax1.set_title('Transient Measurement by DAQ Module')
        ax1.grid(True)

        # Slave data
        for prop in props[1:]:
            slave = prop['deviceid'].lower()
            slave_subscribe_node = '/%s/demods/%d/sample.r' % (slave, demod_c)
            slave_clockbase = daq.getDouble('/%s/clockbase' % slave)
            slave_timestamp = result[slave_subscribe_node][0]['timestamp']
            slave_time = (slave_timestamp[0] - float(slave_timestamp[0][0])) / slave_clockbase
            slave_demod_r = result[slave_subscribe_node][0]['value'][0]

            ax2 = plt.subplot(2, 1, 2)
            ax2.plot(slave_time*1E3, slave_demod_r*1E3, color='red')
            ax2.legend(['Slaves'])
            ax2.set_xlabel('Time [ms]', fontsize=12, color='k')
            ax2.set_ylabel('Amplitude [mV]', fontsize=12, color='k')
            ax2.grid(True)

        _, (ax1, ax2) = plt.subplots(2)
        ax1.plot(master_time*1E3, demod_r_master*1E3, color='blue')

        for prop in props[1:]:
            slave = prop['deviceid'].lower()
            slave_subscribe_node = '/%s/demods/%d/sample.r' % (slave, demod_c)
            slave_clockbase = daq.getDouble('/%s/clockbase' % slave)
            slave_timestamp = result[slave_subscribe_node][0]['timestamp']
            slave_time = (slave_timestamp[0] - float(slave_timestamp[0][0])) / slave_clockbase
            slave_demod_r = result[slave_subscribe_node][0]['value'][0]
            ax1.plot(slave_time*1E3, slave_demod_r*1E3, color='red')
        ax1.set_ylabel('Amplitude [mV]', fontsize=12, color='k')
        ax1.legend(['Master', 'Slaves'])
        ax1.set_title('Transient Measurement by DAQ Module')
        ax1.grid(True)

        for prop in props[1:]:
            slave = prop['deviceid'].lower()
            slave_subscribe_node = '/%s/demods/%d/sample.r' % (slave, demod_c)
            slave_clockbase = daq.getDouble('/%s/clockbase' % slave)
            slave_timestamp = result[slave_subscribe_node][0]['timestamp']
            slave_time = (slave_timestamp[0] - float(slave_timestamp[0][0])) / slave_clockbase
            ax2.plot(slave_time*1E3, (master_time - slave_time)*1E3, color='green')
        ax2.set_title('Time Difference between Master and Slaves')
        ax2.set_xlabel('Time [ms]', fontsize=12, color='k')
        ax2.set_ylabel('Time difference [ms]', fontsize=12, color='k')
        ax2.grid(True)

        plt.tight_layout()
        plt.draw()

        plt.show()

    return result
