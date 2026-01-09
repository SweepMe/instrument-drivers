# Robot Dobot MG400

This driver can be used to control **x, y, z** and **r (rotation)** of a Dobot MG400 tabletop robot.  

---

### Requirements:

- To use this driver, you need to update the robot firmware to **1.5.4 or higher**. The driver has been tested with firmware version **1.5.6** and **1.7.0**.
- The MG400 has two Ethernet ports. The first one uses a fixed IP address of **192.168.1.6**, and the second one has a variable IP address of **192.168.2.6** as factory default.  
  To connect with the robot, your computer needs a static IP address that can be set via Windows network connections:  
  1. Right-click on your Ethernet network adapter -> **Properties**  
  2. Tab **Network** -> **Internet Protocol Version 4 (TCP/IPv4)** -> **Properties**  
  3. Select **Static IP Address** and **255.255.255.0** as subnet mask.  
     Use an address that is different from the robot but in the same subnet, e.g., `192.168.1.5` if using the first Ethernet port.
- Connect to the robot via DobotStudioPro and set: Configuration -> Remote Control -> Current Mode = **TCP/IP Secondary Development**. Otherwise, the robot might not respond to commands from this driver.

---

### Usage:

- Insert numbers into the **Axes fields** `x, y, z, r`. For more complex procedures, use the parameter syntax `{...}` to hand over values from other fields.
- If the object attached to the robot is heavy, set the **payload mass** and optionally the **eccentric distance** of the object.
- The Robot module works best in combination with add-on modules such as **ReadValues** or **TableValues**, where you create a list of `x, y, z, r` values and hand them over to the Robot module using the parameter syntax `{...}`.
- Home position is fixed at `x = 350 mm`, `y = 0 mm`, `z = 0 mm`, `r = 0 deg`.
- **Jump mode**: When activated, the robot will make all lateral and rotational movements at the given movement height.

---

### Coordinates:

- **Home position**: `x = 350.0 mm`, `y = 0.0 mm`, `z = 0.0 mm`, `r = 0 deg`
- **x**: horizontal direction of the robot arm in the home position
- **y**: horizontal direction perpendicular to x
- **z**: vertical direction perpendicular to x and y
- **r**: rotation angle in deg (0.0 to 720.0)

---

### Parameters:

- **Go home at start**: moves the robot at the beginning of a run to the fixed home position.
- **Go home at end**: moves the robot at the end of a run to the fixed home position.
- **Global speed factor** affects all moves: 1-100
- **Acceleration factor**: 1-100
- **Speed factor**: the speed of a linear move in the range 1-100. It can be changed at each step using the parameter syntax.

---

### Caution:

- The home position is fixed and independent of an individual position set in Dobot Studio Pro. Please check whether **Go home before or after the run** works for you.


### Known Issues

- If DobotStudioPro cannot connect to the robot and displays the message "9090 port is occupied by other processes, DobotLink failed to open":
  1. Close DobotStudioPro.
  2. Open Windows Command Prompt as Administrator.
  3. Run the command: `netstat -ano | findstr :9090` to check which process is using port 9090.
  4. The desired output should be empty. If not, note the PID (last column) of the process using port 9090, e.g. 12345.
  5. Run the command: `taskkill /PID 12345 /F` (replace 12345 with the PID you noted).
  6. Verify that port 9090 is now free by running the command from step 3 again.
  7. Restart DobotStudioPro and try to connect to the robot again.
