# Zurich Instruments MFIA

Driver for the Zurich Instruments MFIA impedance analyzer. It also works with an MFLI that has
the MF-IA impedance analyzer option, as the driver enables the impedance unit explicitly.

The instrument is not addressed via a serial or GPIB port. The driver uses the LabOne API and
lists the device IDs (e.g. `dev1234`) that the LabOne Data Server can reach. LabOne must be
installed and its Data Server must be running.

## DC bias

The DC bias across the device under test can come from three different sources, selected with
the **BiasSource** field. This matters for C-V measurements, where the bias is the swept quantity.

### Internal

The internal bias source of the instrument is used, nodes `/dev.../imps/0/bias/enable` and
`/dev.../imps/0/bias/value`. No cabling is needed.

The usable range is limited by the input stage. In 4-terminal mode the bias is restricted to
roughly +/-3 V by the common mode input range of the voltage inputs. In 2-terminal mode the
voltage inputs are not connected, so a larger bias is possible.

### Aux Output (cable to Aux In 1)

A larger bias range is reached by using an Auxiliary Output as a DC source and adding it to the
Signal Output. This requires a cable on the front panel:

1. connect the selected **Aux Output** to **Aux Input 1**

The driver then sets the Auxiliary Output to Manual mode (`outputselect = -1`, `preoffset = 0`,
`scale = 1`), writes the bias to `/dev.../auxouts/n/offset`, and switches on
`/dev.../sigouts/0/add`, which adds the signal present at Aux Input 1 to the Signal Output.

Notes:

* Aux Input 1 is the only input that the add path reads, so the cable always ends there. The
  **BiasAuxOutput** field only selects which Auxiliary Output the cable starts at.
* The sum of AC drive amplitude and DC bias must stay inside the 10 V full scale of the Signal
  Output, which leaves about 9 V of usable DC bias.
* With a differential output the added signal acts as a common mode offset.

### External

The bias is supplied by a separate instrument, for example an SMU or a bias tee. The driver does
not change any bias node of the MFIA, and it cannot sweep the bias. Sweep the bias with the driver
of the instrument that supplies it. The returned "Voltage bias" value is not a number in this case.

## Limits

* The absolute current through the device under test must stay below 10 mA in all configurations.
* None of the bias sources can source a current. Selecting "Current bias in A" raises an error.
* A bias larger than the damage threshold of the instrument requires an external bias tee.

## Returned values

| Variable | Unit | Description |
| --- | --- | --- |
| R | Ohm | real part of the impedance |
| X | Ohm | imaginary part of the impedance |
| Frequency | Hz | measurement frequency |
| Voltage bias | V | DC bias read back from the selected bias source |

## Further reading

* MFIA user manual, node tree: <https://docs.zhinst.com/mfia_user_manual/node_definitions.html>
* MFIA user manual, Impedance Analyzer tab:
  <https://docs.zhinst.com/mfia_user_manual/functional_description/impedance_analyzer.html>
* DC biased impedance measurements using an external bias tee:
  <https://www.zhinst.com/americas/en/blogs/dc-biased-impedance-measurements-using-external-bias-tee/>
