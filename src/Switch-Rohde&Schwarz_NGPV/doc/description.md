# Rohde & Schwarz NGPV Series Power Supply

The **Rohde & Schwarz NGPV series** of power supply is a strange beast. They are 19" rack power supplies which were also available with an additional shell as standalone devices, and both versions were available without any controls for pure remote operation as well.  

The NGPV series is mentioned in their 1984 catalog without any *new* labels and still listed in their 2004/2005 catalogue without any discontinuation notice, so it was in production for over **20 years**. It seems that it has its roots in the late 70s or early 80s and that it was a kind of first-contact to **GPIB** for R&S.

---

## Frontplate Operation

To better understand how the driver works, one needs to have a look at the frontplate of the instrument and understand how it operates:

![NGPV Front Panel](NGPV%20front%20panel.jpeg)

- **Red box**: You use the levers on the rotating numerical counter to set a voltage and current compliance limit.  
- After pressing the **ENTER** key, the value gets transmitted to the **LED display** in the green box. This is the setting that the PSU will use for its output.  
- The actual output voltage and current are measured/read back via the **analogue needle displays** in the blue box.

---

## Input Processing

It is now apparent how the unit can process input from a **mechanical counter** as well as **digital values via GPIB**:  
- Both get transmitted to the LED display as the only source for the output values.  
- The mechanical counter setting (red box) is not processed at any point but just when the **ENTER** key is pressed. After that, it remains where it is without being reconsidered by the instrument again.  

---

## Current Modes and Decimal Points

The instrument has **two different current modes** that offer different maximum values and resolutions. Because of this, there is no fixed decimal point position on the mechanical counter.  

From the GPIB programming section of the manual:  
- The instrument expects just a **4-digit number for voltage** and a **3-digit number for current**.  
- It will ignore any decimal points, commas, or milliampere "m"s.  
- When operating the instrument, you must watch where the decimal point is *virtually* depending on the chosen current mode.

Within the driver, the solution is to:  
- Convert the given values to a numerical full-value while respecting the expected input format.  
- Use a **nested dictionary** that requires the operator to first choose which NGPV model to control.  
  - Then, the operator is offered the choice of the available current modes per NGPV model, which link to a **formatting rule** applied to the compliance input.  
- In the same way, but with a simpler dictionary, the given NGPV model version is used to hand over the right formatting rule for the input voltage.  

---

There is a quirk:  
- All models (with one exception) will stop operating if the voltage entered resembles their model ID (e.g. `300V` for the NGPV 300).  
- Because they could not make the mechanical counter allow `299.9V` and `300.0V` but not `399.9V`, they just maxed out each instrument at *minus one last digit*, e.g. `299.9V` instead of `300V`.  

I considered creating a dictionary for the maximum values and adding a model-dependent check before each applied value. But in the end, this would unnecessarily slow down the code, since it’s easy to remember.  

Also, the instrument will set the output to `0V` natively and start blinking its display if the requested voltage is above its maximum limit. So, no harm is done here.

---
