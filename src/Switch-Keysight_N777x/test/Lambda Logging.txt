# This script runs a lambda logging measurement
# It uses the reference from looptool_sweep_copy.py
# written by Franz

import numpy as np
import time

from pysweepme import get_port


if __name__ == "__main__":
    laser = get_port(
        "COM3",
        {
            "timeout": 10,
            "EOL": "\n",
        },
    )

    sensor = get_port(
        "COM3",
    )

    # Check connection
    print(laser.query("*IDN?"))  # Print the laser ID
    print(sensor.query("*IDN?"))  # Print the sensor ID

    laser_slot = 1  # Change this to the correct slot number for your laser
    sensor_slot = 1  # Change this to the correct slot number for your detector
    detector_channel = 1

    # List parameters
    wavelength_start = 1350
    wavelength_step = 1
    wavelength_finish = 1550
    wavelength = np.arange(wavelength_start,wavelength_finish,wavelength_step) # nm
    points = len(wavelength)

    # Reset
    # TODO: this is not in the driver
    laser.write("*CLS")
    sensor.write("*CLS")

    time.sleep(1)  # Missing the is_busy() function

    # wavelength limits - only in here to test connection
    max_wl = float(laser.query(f"source{laser_slot}:wav? max")) * 1e9 - 1
    min_wl = float(laser.query(f"source{laser_slot}:wav? min")) * 1e9 + 1
    print(f"Wavelength limits: {min_wl} nm to {max_wl} nm")

    # restore presets
    # TODO: maybe this is missing in the driver
    laser.write(":SYSTem:PRESet")
    sensor.write(":SYSTem:PRESet")
    time.sleep(1)

    # TODO: resend all settings that are stored in self.command_queue

    # Trigger
    # TODO: Check which device needs which trigger settings - maybe need to be done for both
    laser.write("trigger:configuration 1")  #:TRIGger:CONFiguration
    sensor.write(f"trigger{sensor_slot}:input sme")  # PD will finish a function when input trigger is abled                          #:TRIGger[n][:CHANnel[m]]:INPut
    laser.write(f"trigger{laser_slot}:output stf")  # TLS will send a output trigger when sweep starts (input trigger generated)   #:TRIGger[n][:CHANnel[m]]:OUTPut

    # Sensor settings
    # set auto ranging on
    sensor.write(f"sense{sensor_slot}:chan{detector_channel}:power:range:auto 1")

    # set the unit of power: 0[dBm],1[W]                      #:SENSe[n]:[CHANnel[m]]:POWer:UNIT
    sensor.write(f"sense{sensor_slot}:chan{detector_channel}:power:unit {1}")

    # set senser wavelength centered at 1550 nm   #:SENSe[n]:[CHANnel[m]]:POWer:WAVelength
    sensor.write(f"sense{sensor_slot}:chan{detector_channel}:power:wavelength {1450}nm")

    # Laser settings
    # choose which path of tunable laser. output1 [low power high sens] output2 [high power] :OUTPut[n][:CHANnel[m]]:PATH
    laser.write(f"output{laser_slot}:path {1}")
    # set source power unit [:SOURce[n]][:CHANnel[m]]:POWer:UNIT
    laser.write(f'source{laser_slot}:power:unit {"DBM"}')

    # set laser power {unit will be according to the power unit set before}
    laser_power_mw = 10  # Set the desired laser power in mW
    laser.write(f"source{laser_slot}:power:level:immediate:amplitude1 {laser_power_mw}")
    laser.write(f"source{laser_slot}:power:level:immediate:amplitude2 {laser_power_mw}")

    # optional
    laser.write(f"output{laser_slot}:state ON")

    # Laser Lambda Logging settings
    laser.write("wavelength:sweep:mode continuous")

    # # only 0.5 5 40 allowed
    laser.write(f"wavelength:sweep:speed {5}nm/s")
    laser.write(f"wavelength:sweep:start {wavelength_start}nm")
    laser.write(f"wavelength:sweep:step:width {wavelength_step}nm")
    laser.write(f"wavelength:sweep:stop {wavelength_finish}nm")
    laser.write("wavelength:sweep:cycles 1") #Set the number of cycles

    # Detector Lambda Logging settings
    avg_time_s=1e-3
    PRIMARY_CHANNEL = 1  # TODO: What is this?
    # ,start #Enables Stability data acquistion and starts data acquistion
    sensor.write(f"sense{sensor_slot}:chan{PRIMARY_CHANNEL}:function:parameter:logging {points},{avg_time_s}")
    # ,start #Enables Stability data acquisition and starts data acquisition
    sensor.write(f"sense{sensor_slot}:chan{PRIMARY_CHANNEL}:function:state LOGG,start")  #:SENSe[n][:CHANnel[m]]:FUNCtion:STATe

    # TODO: check if this is for laser or sensor or both
    sensor.write("wavelength:sweep:state start") # Start wavelength sweep #[:SOURce[n]][:CHANnel[m]]:WAVelength:SWEep:[STATe]

    # wait for the laser to finish
    print("Waiting for sweep to finish")
    while True:
        # beware: the query returns a string containing the unicode line feed character
        status = laser.query(f"source{laser_slot}:wav:sweep:state?")[1]
        print(f"Laser still sweeping. Status: {status}")
        if status == "0":
            print("Laser sweep finished")
            break
        time.sleep(0.3)

    # Retrieve the data
    sensor.write(f"sense{sensor_slot}:chan{detector_channel}:function:result?")
    power_raw = sensor.port.read_raw()
    print(power_raw)
    # TODO: Check if this is for laser or sensor or both
    laser.write(f"sense{sensor_slot}:chan{PRIMARY_CHANNEL}:function:state LOGG,stop") # stop the lambda logging


