import pysweepme  # use "pip install pysweepme" in cmd to install pysweepme
import os
import time

# Create a driver instance using 'get_driver' with three arguments:
# 1. name of the driver
# 2. folder of the drivers
# 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::15::INSTR", "169.254.55.24"

# The name of the driver where this example file is in. Next line retrieve it automatically. 
# You can enter it manually as well.
driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]

# The path of the driver where this example file is in. Next line retrieve it automatically. 
# You can enter it manually as well.
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  

# Here you need to specify the port used for communication.
# The SENTIO driver supports GPIB, socket and NI VISA communication interfaces.
# port_str = "GPIB0::14::INSTR"  # for GPIB
# port_str = "127.0.0.1:35555"  # for socket
port_str = "TCPIP0::127.0.0.1::35555::SOCKET"  # for VISA runtime

# Make an instance of the device
Sentio = pysweepme.get_driver(driver_name, driver_path, port_str)

# needed to create the communication object Sentio.prober
Sentio.connect()

num_dies = Sentio.prober.map_get_num_dies()
for i in range(num_dies):

    # separate
    Sentio.prober.move_chuck_separation()
    
    # go to next die
    Sentio.prober.map_step_die_seq(i) 

    # contact
    Sentio.prober.move_chuck_contact()
    
    # do something here after the contacting the die

# separate at end
Sentio.prober.move_chuck_separation()

Sentio.disconnect()
