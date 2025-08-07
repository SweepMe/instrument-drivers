import time

# add the parent folder to path as it contains the libs folder
from pathlib import Path

from pysweepme import FolderManager as FoMa

FoMa.addFolderToPATH(str(Path.cwd().parent))

# install pysweepme and g2vsunbrick before running the script
from g2vsunbrick import G2VSunbrick
from pysweepme import get_port

port_string = "COM9"
spectrum_file_name = r"C:\Users\Public\Documents\SweepMe!\CustomFiles\my_spectrum.spectrum"
port = get_port(port_string)

brick = G2VSunbrick(port.port)
print(f"Sunbrick {brick.brick_id} has an avg temperature of {brick.get_avg_temperature()}°C")

brick.set_spectrum(spectrum_file_name)
brick.set_intensity_factor(100)

time.sleep(10)
brick.turn_off()
port.close()
