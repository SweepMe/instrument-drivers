import pysweepme  # use "pip install pysweepme" in cmd to install pysweepme
import os

## Create a driver instance using 'get_device' with three arguments:
## 1. name of the driver
## 2. folder of the driver
## 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::15::INSTR", "169.254.55.24"

## The name of the driver where this example file is in. Next line retrieve it automatically. You can enter it manually as well.
driver_name = os.path.dirname(os.path.dirname((os.path.abspath(__file__)))).split(os.sep)[-1]

## The path of the driver where this example file is in. Next line retrieve it automatically. You can enter it manually as well.
driver_path = os.path.dirname((os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))  

port_string = "127.0.0.1"

## Make an instance of the device
SemiP = pysweepme.get_device(driver_name, driver_path, port_string)



## Now you can use functions (methods) availabe in the driver. SweepMe drivers usually have two groups of methods: first, the semantic methods,
## which are called by SweepMe itself for each measurement point (if the method is defined in the driver.), second, convenience methods,
## which are wrapping the instruments commands and are used in semantic functions. You can call either of them depending on your need.
## A full list of semantic methods are available at SweepMe's wiki.
## https://wiki.sweep-me.net/wiki/Sequencer_procedure

## In this example, connect() and disconnect() are semantic functions.

SemiP.connect()

answer = SemiP.get_xy_position()
print(answer)

SemiP.switch_motor("1")

SemiP.move_die("5", "2")

SemiP.switch_motor("0")

SemiP.disconnect()
