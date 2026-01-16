# AdvancedMicrofluidics LSPone-Series

## Setup

This driver communicates with AdvancedMicrofluidics LSPone-Series pumps using the `amfTools` library. It might be compatible with other products (RVMFS, RVMLP, SPRM, and LSPone) aswell. It requires an installation of ftd2xx64.dll, which can be found here: https://ftdichip.com/drivers/d2xx-drivers/

## Parameters

- **Volume**: Use positive values to pump in, and negative values to dispense.
- **Flow rate**: Flow in µl/min set by the user. 
- **Valve**: Target valve index (integer).
- **Valve mode**: Movement strategy for valve changes: *Shortest Way*, *Clockwise*, or *Counter-Clockwise*.
- **Speed**: The device has 3 speed modes that can be used to set the flow rate.
- **Syringe volume**: Syringe capacity in µl used for flow-rate calculations.
- **Plunger force**: Force profile for the plunger.
- **Microstep resolution**: Motor microstep configuration used for precise positioning.
- **Wait for pump finish**: When enabled, the driver will block further sequencer steps until the pump operation completes. Disable this option if you want to run measurements while pumping.
- **Empty on start**: If enabled, the pump will empty any residual liquid in valve 1 at the start of the sequence.

## Returned Variables

- **Valve position** — current valve index (integer).
- **Flow rate** — measured flow rate converted to the user-selected units.
- **Plunger current** — motor/plunger current reported by the device (unit depends on device firmware; displayed as provided).

## Behavior & Notes

- The driver normalizes flow rates to `µl/min` internally and converts values for display and configuration according to the selected volume/time units.
- You can use the `ParameterSyntax` (F3) to vary volume and flow rate parameters dynamically during a sequence.
- The start of the pump is currently triggered in `signin` using the configured volume (see `pump_volume`). See the wiki (F1) for details on the sequencer procedure.
