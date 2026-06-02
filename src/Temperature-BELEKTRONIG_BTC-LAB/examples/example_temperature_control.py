import pysweepme  # install pysweepme using command line: pip install pysweepme
import time


# The path of folder where the driver is in - not the folder where the main.py is is.
# Please change if you use the driver in your project
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  

# The COM port of the instrument.
# Please change if it is another one.
port_string = "COM3"

# btc is a SweepMe! driver object that is created with a single function
btc = pysweepme.get_driver("Temperature-BELEKTRONIG_BTC-LAB", driver_path, port_string)
print(btc)

# reading out the configuration of the BTC-LAB controller
dc = btc.get_device_configuration()
print("Device configuration:", dc)

# Let's display some help about the set_mode command before we use it
help(btc.set_mode)

# change to heat&cool mode
btc.set_mode(3)

# set setpoint temperature in °C
btc.set_setpoint_temperature(50)

# reading temperature 10 times
for i in range(10):
    time.sleep(0.25)
    t = btc.get_temperature()
    o = btc.get_output()
    print(i,t,o)
    
# going back to read-only mode
btc.set_mode(0)
