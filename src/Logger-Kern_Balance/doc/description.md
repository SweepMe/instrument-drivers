### KERN Balance driver

The driver supports all balances, scales, and terminals from KERN&SOHN that use the KERN communication protocol (KCP).
As a fallback it also supports older balances that use the communication protocol using the commands t,w, and s (tws).

**Models with KCP:** KIB-TM, KFB-TM, KFN, PCB

**Models with tws protocol:**  572, 573, KB, DS, FKB, FKT, IKT, PKT

**Communication:**

* Supported interfaces:
  * RS232 (COM port)
  * USB via USB-RS232 adapter (virtual COM port) 
  * Ethernet (with serial-to-Ethernet adapter)
* COM port settings:
  * Baudrate 9600 (in most cases this should be factory default)
  * 8 databits
  * 1 stopbit
  * parity None
* Ethernet settings:
  * Factory default IP address: 192.168.178.150
  * Factory default subnet mask: 255.255.255.0
  * Fixed TCP port: 23
  * Please note that the IP address can be changed and could be different.
  * Exemplary port string as used in the Logger module: "192.168.178.150:23" 

Some models require to set the communication protocol to KCP. This can be done in the instrument menu.
For example, go to instrument menu "P9 Prt" -> "oPt" -> "ModE" and  select "KCP".
Please switch of any automatic sending of data as used for working with a printer. 
This will otherwise interfere with the communication.

**Handling of the SweepMe! driver:**    
* Select the weight unit (g, kg). The unit will be also sent to the balance if supported.
* The option "Read stabilized" must be checked if the returned value should be a stabilized weight. Then the
driver waits until the balance indicates a stable weight. In some cases, the timestamp of the Time module might not match
the exact time of the reading because the balance needs some time to stabilize.
* The driver returns whether the reading is stable, also in case the weight is immediately returned.
* The option "Initial tare" triggers the tare function at the beginning of a run to zero the level.
* The option "Initial zero" triggers the zero function at the beginning of a run in order to create a new zero reference level.
* One can return a flow rate by selecting a time base (e.g. g/s, kg/min, ...) as a convenience function.
The driver calculates the flow rate from the difference of the last two readings.
* During a run, the tare and zero functions can be triggered via the actions "tare" and "zero".