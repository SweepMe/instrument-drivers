# Robot Thorlabs NanoTrak

This driver can be used to control the **horizontal** and **vertical** position of a Thorlabs NanoTrak optical beam stabilization device via the Kinesis motion control software.

---

### Requirements:

- To use this driver, you need to install **Thorlabs Kinesis** software from the Thorlabs website.
- Kinesis must be **closed** when running this driver, as the driver communicates directly with the NanoTrak hardware.
- The NanoTrak device must be connected to your computer via USB

---

### Usage:

- Insert numbers into the **Axes fields** for `Horizontal` and `Vertical` positions. Valid range is **0 to 10 NT units**.
- The driver performs automatic **latching** before tracking to ensure stable position detection.
- For complex tracking procedures, use the **Tracking mode** parameter to select between Horizontal, Vertical, or Both axes.
- Set the **Circle diameter** parameter for the tracking routine (in NT units). Multiple diameters can be specified using comma-separated values.
- The **Tracking time** parameter specifies how long the device should track after reaching each diameter setting.
- Use **Feedback Source** to select the appropriate input signal (10V BNC, 5V BNC, 2V BNC, 1V BNC, or TIA).

---

### Coordinates:

- **Horizontal**: horizontal position in NT units (0.0 to 10.0)
- **Vertical**: vertical position in NT units (0.0 to 10.0)

---

### Parameters:

- **Channel**: select which channels to enable: **1**, **2**, or **1,2** (both channels).
- **Tracking mode**: select tracking axis: **Horizontal**, **Vertical**, or **Both**.
- **Tracking time in s**: duration in seconds to perform tracking at each circle diameter setting.
- **Circle diameter in NT**: diameter value(s) for the tracking routine. Multiple values can be comma-separated.
- **Go home at start**: moves the NanoTrak to the home position at the beginning of a run.
- **Home position**: the target home position in NT units, specified as `horizontal,vertical` (e.g., `1.0,1.0`). If empty, the home position is not updated.
- **Feedback Source**: input signal source (10V BNC, 5V BNC, 2V BNC, 1V BNC, or TIA).
- **Frequency in samples/rev**: oscillation frequency for the tracking routine (default: 100).
- **Gain**: loop gain for the tracking control (integer value, default: 1).
- **Control mode**: **Open Loop** or **Closed Loop** control.
- **Horizontal/Vertical phase compensation in °**: phase offset compensation in degrees for each axis.
- **Modular Rack**: enable if using a NanoTrak in a Thorlabs Modular Rack system.
- **Bay**: rack bay number when using a Modular Rack (default: 1).

---

### Caution:

- Positions outside the range **0-10 NT units** will be clipped to the nearest boundary, and the home position will not be updated. This can be used to maintain the optimal position after tracking.

---

### Known Issues:

- **Kinesis must be closed**: If Kinesis is running while using this driver, communication errors may occur. Close Kinesis completely before starting measurements.
- **Device not detected**: Ensure the NanoTrak device is properly connected via USB/Ethernet and powered on. Use Kinesis Device Manager to verify the device is recognized by your system.
- **TimeoutError during connection**: The driver will automatically retry the connection up to 2 times if a timeout occurs.
