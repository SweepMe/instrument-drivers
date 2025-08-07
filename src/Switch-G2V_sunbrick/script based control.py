import time

from g2vsunbrick import G2VSunbrick
from pysweepme import get_port
import serial


port_string = "COM9"
spectrum_file_name_cyan = r"C:\Users\Public\Documents\SweepMe!\CustomFiles\Heliatek\Spektren\489nm-LED_Tuerkis_100%.spectrum"
spectrum_file_name_red = r"C:\Users\Public\Documents\SweepMe!\CustomFiles\Heliatek\Spektren\687+719nm-LED_Rot_100%.spectrum"
# sweepme_port = get_port(port_string)
# print(type(sweepme_port.port))
serial_obj = serial.Serial(port_string)

try:
    print(type(serial_obj))
    brick = G2VSunbrick(serial_obj)

    print("Sunbrick {id} connected to port {port}".format(id=brick.brick_id,
    port=serial_obj.port))

    print("Sunbrick {id} has an avg temperature of {tmp}°C".format(id=brick.brick_id,
    tmp=brick.get_avg_temperature()))

    brick.set_spectrum(spectrum_file_name_cyan)
    brick.set_intensity_factor(100)
    # print("Finished loading {sf} into Sunbrick {id}".format(id = brick.brick_id, sf =
    # spectrum_file_name))
    spectrum_data_cyan = brick.get_spectrum()

    brick.set_spectrum(spectrum_file_name_red)
    spectrum_data_red = brick.get_spectrum()

    for channel in range(36):
        print(spectrum_data_cyan[channel], spectrum_data_red[channel])


    time.sleep(10)
    brick.turn_off()
except:
    pass
finally:
    serial_obj.close()