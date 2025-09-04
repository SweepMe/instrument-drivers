### Kern Balance driver

The driver supports all balances, scales, and terminals from  Kern&Sohn that use the KERN communicaton protocol (KCP). 
As a fallback it also supports older balances that use the communication protocol using the commands t,w, and s (tws).

**Models with KCP:** KIB-TM, KFB-TM, KFN    
**Models with tws protocol:**  572, 573, KB, DS, FKB, FKT, IKT, PKT

**Communication:**

* RS232 or USB (with USB-RS232 adapter)
* Baudrate 9600 (in most cases this should be factory default)
* 8 databits
* 1 stopbit
* parity None

Some models require to set the communication protocol to KCP. This can be done in the instrument menu.
For example, go to instrument menu "P9 Prt" -> "oPt" -> "ModE" and  select "KCP"    
Please switch of any automatic sending of data as needed for using a printer. This will otherwise interfere with the communication.

**Handling of the SweepMe! driver:**    
* Select the weight unit (g, kg)     
* The option "Read stabilized" must be checked if the returned value should be a stabilized weight. Then the
driver waits until the balance indicates a stable weight. Attention: This does not work with all old models that use the old command set 
* The driver returns whether the reading is stable, also in case the weight is immediately returned.  
* The option "Initial tare" triggers the tare function at the beginning of a run to zero the level
* The option "Initial zero" triggers the zero function at the  beginning of a run in order to create a new zero reference level.
* One can return a flow rate by selecting a time base (e.g. g/s, kg/min, ...) as a convenience function. 
The driver calculates the flow rate from the difference of the last two readings.

