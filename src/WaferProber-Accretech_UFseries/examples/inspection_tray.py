import pysweepme  # use "pip install pysweepme" in command line to install
import os
import time

driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  

# port_string = "GPIB0::1::INSTR"
port_string = "GPIB3::6::INSTR"

uf = pysweepme.get_driver(driver_name, driver_path, port_string)

uf.connect()  # needed to create an AccretechProber instance inside the driver instance

uf.print_info()  # prints out general static information

uf.print_status()  # prints out the current system status

# Check whether cassette is sensed
cassette_status = uf.prober.request_cassette_status()
if cassette_status == "000000":
    # Wafer sensing "jw" command
    uf.prober.sense_wafers()

# Load wafer from inspection tray - "LI" command
uf.prober.load_inspection_wafer_aligned()

uf.print_status()

# Move to specified die
uf.prober.move_specified_die(135, 136)  # die at coordinate x, y

uf.print_die_info()

if not uf.prober.is_chuck_contacted():
    uf.prober.z_up()  # Chuck up

uf.print_status()

time.sleep(1)

uf.prober.z_down()  # Chuck down

# Unload to inspection tray
uf.prober.unload_to_inspection_tray()

uf.print_status()

# Reset alarm
uf.prober.reset_alarm()
