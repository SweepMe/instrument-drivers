# VS-10 module of LakeShore M81

- Provide a precision voltage source (up to 10 V, 100 mA) using the VS-10 module of the LakeShore M81 Synchronous Source Measure System.
- Three physical source channels (S1, S2 and S3) are available in the M81. Install the VS-10 in one of them and select the corresponding channel number in SweepMe!.

## Features implemented in this driver

- **Shape**: DC, Sine, Triangle, Square
- **Frequency**: Settable for all non-DC shapes. Frequency bounds are module- and range-dependent; the driver enforces `> 0` and leaves module-specific bounds to the device.
- **Duty**: For Square and Triangle shapes the duty cycle can be set (0.0–1.0; device supports 0.001–0.999 increments) via `SOURce#:DCYCle`. Duty values 0 and 1 produce DC-like waveforms.
- **Ranging**:
  - Auto ranging: For all shapes
  - Manual DC range: For all shapes
  - Manual AC range: For all non-DC shapes  
  Available ranges: 10 V, 1 V, 100 mV, 10 mV
- **Advanced settings**:
  - **Sync**: enable/disable sync + source and phase for non-DC shapes.
  - **Current protection level**: DC protection. This is a DC-limited protection (does not limit >100 Hz AC components). Default is 100 mA.
  - **High / Low voltage output software limits**: Bounds are -10 V .. +10 V. When shape ≠ DC, the limit is applied to (offset + amplitude).

## Behavior notes

- The VS-10 supports separate AC and DC ranges. When Auto is selected the module will pick the lowest range that supports the configured amplitude and offset. Use Manual range only if you know the desired performance window.
- The hardware current protection is a **DC** limit and will not limit high-frequency (>100 Hz) currents. If AC components exceed the DC limit, the protection may not respond as expected.
- Duty values of 0 or 1 produce constant waveforms (sawtooth/saturated). Use values inside 0.001–0.999 for periodic shapes.