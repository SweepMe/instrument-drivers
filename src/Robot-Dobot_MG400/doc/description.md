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

---

### Connection:

- Connect to the robot via DobotStudioPro and set: Configuration -> Remote Control -> Current Mode = **TCP/IP Secondary Development**. Otherwise, the robot might not respond to commands from this driver.
- In DobotStudioPro, set the robot to **Enabled**
- Now the robot should be ready to receive commands from this driver.

---

### Usage:

- Insert numbers into the **Axes fields** `x, y, z, r`. For more complex procedures, use the parameter syntax `{...}` to hand over values from other fields.
- If the object attached to the robot is heavy, set the **payload mass** and optionally the **eccentric distance** of the object.
- The Robot module works best in combination with add-on modules such as **ReadValues** or **TableValues**, where you create a list of `x, y, z, r` values and hand them over to the Robot module using the parameter syntax `{...}`.
- Home position is fixed at `x = 350 mm`, `y = 0 mm`, `z = 0 mm`, `r = 0 deg`.
- **Jump mode**: When activated, the robot will make all lateral and rotational movements at the given movement height.

---

### Coordinates:

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


### Error messages:

- The driver reads the robot alarms via `GetErrorID()` after each movement and reports them with their official
  Dobot descriptions, e.g. "Controller alarm 17: Inverse kinematics error with no solution" or
  "Controller alarm 112: Collision detection stop".
- Command responses are checked for their error code. For example, if the robot is in alarm or emergency-stop
  state, the driver reports this instead of running into an unexplained timeout.
- Alarms are cleared automatically at the start of each run. To clear an alarm manually, use DobotStudioPro.

### Troubleshooting connection problems:

If the driver cannot connect at the start of a run, check the following:

1. **Robot still booting**: after power-on, the controller needs about one minute before it accepts TCP
   connections. Wait and start the run again.
2. **Remote control mode**: the robot accepts the TCP connection but does not answer commands if
   Configuration -> Remote Control -> Current Mode is not set to **TCP/IP Secondary Development** in
   DobotStudioPro.
3. **Network configuration**: the PC needs a static IP address in the robot's subnet (e.g. `192.168.1.5`,
   subnet mask `255.255.255.0`, when using the first Ethernet port with the fixed address `192.168.1.6`).
4. **Port blocked by another program**: only close DobotStudioPro after setting the remote control mode, and
   make sure no other program (e.g. a Python script) is still connected to ports 29999/30003. A connection
   that was not closed properly (e.g. after a crash) can block the port until the controller frees it —
   restarting the robot helps in this case.
5. **Old firmware**: controller firmware below **1.6.0.0** has a known issue where the TCP ports occasionally
   fail to connect or accept commands. If connecting fails repeatedly, update the robot firmware.

If a movement does not finish and the driver reports a blocked motion queue, the queue can be reopened by
sending `ClearError()` and `Continue()` on port 29999, or by restarting the robot.

### Known Issues

- If DobotStudioPro cannot connect to the robot and displays the message "9090 port is occupied by other processes, DobotLink failed to open":
  1. Close DobotStudioPro.
  2. Open Windows Command Prompt as Administrator.
  3. Run the command: `netstat -ano | findstr :9090` to check which process is using port 9090.
  4. The desired output should be empty. If not, note the PID (last column) of the process using port 9090, e.g. 12345.
  5. Run the command: `taskkill /PID 12345 /F` (replace 12345 with the PID you noted).
  6. Verify that port 9090 is now free by running the command from step 3 again.
  7. Restart DobotStudioPro and try to connect to the robot again.
