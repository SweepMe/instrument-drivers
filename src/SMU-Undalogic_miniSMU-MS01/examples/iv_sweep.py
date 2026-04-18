"""
Hardware I-V sweep example for the Undalogic miniSMU MS01 driver with pysweepme.

Demonstrates the onboard voltage sweep, which provides consistent timing
and higher throughput than a software-driven point-by-point sweep.
"""

import json
import os
import pysweepme  # use "pip install pysweepme" in command line to install
import time

# Automatically resolve the driver name and path from this example's location
driver_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).split(os.sep)[-1]
driver_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# For USB: use the COM port, e.g. "COM3"
# For WiFi: use "TCPIP0::<ip>::3333::SOCKET", e.g. "TCPIP0::192.168.1.100::3333::SOCKET"
port_string = "COM3"

smu = pysweepme.get_driver(driver_name, driver_path, port_string)

# Verify connection
identity = smu.get_identification()
print(f"Connected to: {identity}")

# Configure the sweep: 0 V to 1 V, 100 points, 50 ms dwell per point
channel = 1
smu.set_source_mode(channel, "FVMI")
smu.set_sweep_parameters(channel, start=0.0, end=1.0, points=100, dwell_ms=50)

# Execute the sweep
print("Starting I-V sweep...")
smu.execute_sweep(channel)

# Poll for completion with timeout
timeout_s = 30.0
start_time = time.time()

while True:
    if time.time() - start_time > timeout_s:
        print("Sweep timed out!")
        break

    status_str = smu.get_sweep_status(channel)
    parts = status_str.split(",")
    status = parts[0]
    if status == "COMPLETED":
        print("Sweep complete.")
        break
    elif status == "ABORTED":
        print("Sweep aborted!")
        break
    elif status == "RUNNING" and len(parts) >= 5:
        progress = int(parts[1]) / int(parts[2]) * 100
        print(f"  Progress: {progress:.0f}%")
    time.sleep(0.5)

# Retrieve and display results
raw_data = smu.get_sweep_data(channel)
sweep_json = json.loads(raw_data)
data_points = sweep_json.get("data", [])

print(f"\n{'Voltage (V)':>12}  {'Current (A)':>14}")
print("-" * 28)
for point in data_points:
    print(f"{point['v']:12.6f}  {point['i']:14.9f}")
