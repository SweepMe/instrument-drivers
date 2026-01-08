# AdvancedMicrofluidics LSPone-series

## Setup

This driver communicates with AdvancedMicrofluidics LSPone-series pumps using the `amfTools` library. It might be compatible with other products (RVMFS, RVMLP, SPRM, and LSPone) aswell.

## Parameters

- **Volume**: Total volume (displayed and entered by the user). The driver stores volume in µl by default.
- **Volume unit**: Unit for the displayed volume (e.g. `µl`, `ml`, `l`); the driver converts between units automatically.
- **Flow rate**: Flow set by the user. It uses the **Volume unit** and **Time unit** selected by the user.
- **Time unit**: Unit for flow rate time base (e.g. `s`, `min`).
- **Valve**: Target valve index (integer).
- **Valve mode**: Movement strategy for valve changes: *Shortest Way*, *Clockwise*, or *Counter-Clockwise*.
- **Speed**: Drive speed profile (user-facing labels map to device-specific numeric modes).
- **Syringe volume**: Syringe capacity in µl used for flow-rate calculations.
- **Plunger force**: Force profile for the plunger; mapped to device-specific modes.
- **Microstep resolution**: Motor microstep configuration used for precise positioning.
- **Wait for pump finish**: When enabled, the driver will block further sequencer steps until the pump operation completes. Disable this option if you want to run measurements while pumping.

## Returned Variables

- **Valve position** — current valve index (integer).
- **Flow rate** — measured flow rate converted to the user-selected units.
- **Plunger current** — motor/plunger current reported by the device (unit depends on device firmware; displayed as provided).

## Behavior & Notes

- The driver normalizes flow rates to `µl/min` internally and converts values for display and configuration according to the selected volume/time units.
- You can use the `ParameterSyntax` (F3) to vary volume and flow rate parameters dynamically during a sequence.
- The start of the pump is currently triggered in `signin` using the configured volume (see `pump_volume`). See the wiki (F1) for details on the sequencer procedure.
