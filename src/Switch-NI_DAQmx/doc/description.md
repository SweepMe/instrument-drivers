# SweepMe! instrument driver: Switch-NI_DAQ

This driver integrates **National Instruments DAQ (NI-DAQmx)** analog output channels into the SweepMe! **Switch** module.  
It allows you to set and sweep voltages on NI DAQ analog output (AO) channels..

---

## Features
- Control **analog output channels (AO)** of NI DAQ devices.
- Voltage sweep support via **SweepEditor** or other variables selected in the field **Sweep Value**.
- User-defined minimum and maximum voltage ranges.
- Automatic detection of connected NI DAQ devices.

## Handling
- Use "Find Ports" button to search for connected devices and select your device based on its serial number.
- Insert the identifier of the analog channel in the field "Analog channel", e.g 'ao0'.
- Set the desired voltage range in the fields "Min voltage" and "Max voltage". If the voltage does not match an available voltage range, the next higher one will be used.

---

## Acknowledgements
The driver uses the **Python package**: [`nidaqmx`](https://nidaqmx-python.readthedocs.io/en/latest/)  
