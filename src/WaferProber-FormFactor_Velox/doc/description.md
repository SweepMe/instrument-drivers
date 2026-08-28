# WaferProber FormFactor Velox

This driver controls the prober functions of FormFactor Velox wafer probers through the Velox Message Server.
The probe plan is not defined in SweepMe! but taken from the wafer map that is currently loaded in Velox: SweepMe!
reads the selected wafers, dies and subsites and steps through them, contacting the wafer at every measurement point.

---

### Requirements:

- The Velox software must be installed and running on the prober PC. The driver talks to its Message Server, so
  Velox has to be started before the measurement.
- No additional Python packages have to be installed. The `velox` package ships with the driver in its `libs`
  folder.
- The SweepMe! port manager is not used. The **Port** field carries the address of the Message Server instead of a
  COM or GPIB resource, and the default socket is `1412`.
- A loader module is only required for wafer handling. Everything else works on a system without a loader.

---

### Usage:

1. Load the wafer map in Velox and select the dies and subsites that are to be probed. The driver never changes
   the selection, it only reads it.
2. Add a **WaferProber** module and select this driver.
3. Set **Port**. Press **Find Ports** to get `localhost` and the remote-control template as suggestions.
4. Press **Update**. The driver reads the probe plan from Velox and fills the wafer, die and subsite tables, and
   reports the wafer geometry, which fills the fields of the **Map** tab.
5. Choose the sweep values of the module. **Die table** and **Subsite table** step through the entries that were
   just read; **Current wafer** stays on the wafer that is loaded.

During the run, for every measurement point the driver moves the chuck to separation, steps to the die and the
subsite, and moves the chuck back to contact. With a loader connected, a change of the wafer sweep value unloads
the current wafer and loads the next one first.

At the start of a branch the driver switches the loader to remote mode, and restores local mode at the end. When
the branch is finished, the chuck is moved to separation — or, if a wafer sweep with a loader was used, the wafer
is unloaded.

---

### Parameters:

- **Port**: address of the Velox Message Server.
  - `localhost` when SweepMe! runs on the same PC as Velox.
  - `IP:xxx.xxx.xxx.xxx; Port:xxxx` to reach a remote Velox PC on a specific socket.
  - A plain address such as `192.168.0.10` is also accepted and uses socket `1412`.
- **Load angle**: angle in degrees by which a wafer is rotated while it is loaded. Only has an effect on systems
  with a loader, as it is passed to the loader together with the load command.

---

### Measurement Output:

- **Wafer**: wafer ID as reported by the prober. Empty on systems that report no ID.
- **Die**: die position of the current die in the format `x,y`.
- **Subsite**: number of the current subsite. `-1` while no subsite is selected.

All three are read back from the prober at every measurement point rather than repeated from the set value, so
the saved data shows where the prober actually was.

---

### Note on the wafer geometry:

`get_wafer_geometry()` reports diameter, die pitch, notch position and the die-numbering origin, which the
WaferProber module uses to fill in the **Map** tab. The values come from `GetMapDims`, `GetWaferMapParams2` and
`GetMapOrientation`.

The notch position uses the encoding that Velox documents for `:prob:waf:ori` — `0` is bottom, `90` is left, `180`
is top and `270` is right. This is not the mathematical convention, so the values must not be reused as angles.

Values that the loaded map does not carry, or that this Velox version does not support, are reported as `None`
instead of raising, so a partial answer is still usable.

---

### Note on the contact state:

`get_contact_state()` reports whether the probes are currently touching the wafer, which drives the contact
indicator of the wafer-map panel. It is read from `ReadChuckStatus().PresetHeight`, where `C` means contact and `O`
means overtravel.

It is deliberately not read from the `IsContactSet` bit of the same command, despite the name: that bit only
states that a contact height has been taught, not that the chuck is currently at it.

---

### Known limitations:

- **The wafer table stays empty without a loader.** The wafer list is read from the cassette, so on a system with
  no loader module the driver returns only dies and subsites. The wafer-map panel then shows no wafer before the
  run starts; set the module's sweep value for the wafer to **Current wafer** to see the dies of the loaded wafer
  right away.
- **Wafer loading is untested.** `load_wafer()` is implemented against the documented commands but has not been
  verified on a system with a loader. The slot is searched in the cassette status; with two cassettes the port
  that is selected may not be the intended one.
- **Subsite labels are prefixed with their number**, for example `#1 Subdie Label A`. Velox allows several
  subsites to carry the same label, and the number keeps the entries of the subsite table distinguishable.
- **The die-numbering origins `upper_right` and `lower_right` are reported but cannot be shown.** The Map tab
  offers only the top-left and bottom-left conventions, so for the two right-hand origins the setting is left
  untouched rather than set to a wrong value.
- **Contacting is not optional.** Every measurement point ends with the chuck at contact height; there is no
  parameter to probe without contacting.
