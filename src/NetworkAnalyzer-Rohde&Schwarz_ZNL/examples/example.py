import os
import pysweepme  # use "pip install pysweepme" in command line to install

# create a driver instance using 'get_driver' with three arguments:
# 1. name of the driver
# 2. folder of the driver
# 3. Port identifier string as used in SweepMe!, e.g. "GPIB0::15::INSTR"

# the name of the driver where this example file is in

""" connect to device """
driver_path = os.path.dirname(__file__)
if driver_path.endswith("pysweepme"):
    driver_path = os.path.dirname(driver_path)
driver_name = os.path.basename(driver_path)
port_str = "GPIB0::1::INSTR"
print(driver_name, driver_path)
znl = pysweepme.get_driver(driver_name, driver_path, port_str)

identification = znl.get_identification()
print("Connection check, ZNL identification:", identification)


""" basic functions tests """
window_n = 1
channel_n = 1

# window on off

znl.set_display_window_enabled(state=0, win_number=window_n)
input("CHECK window 1 off, press enter after")

znl.set_display_window_enabled(state=1, win_number=window_n)
print("window back on")

# trace operations
znl.make_param_trace("S11", trace_name="Auto", ch=1)
tr_names = [f"TrC{channel_n}_S11"]
znl.display_traces(tr_names, win_num=window_n)

input("CHECK S11 trace created and displayed, press enter after")
znl.delete_all_traces()
input("CHECK S11 trace deleted, press enter after")

# znl.set_data_transfer_format()
