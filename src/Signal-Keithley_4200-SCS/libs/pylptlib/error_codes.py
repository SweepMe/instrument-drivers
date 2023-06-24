# error codes adapted from the ATV K4200
# github repository https://github.com/ATV-GmbH/AtvK4200Lpt/tree/master/source

ERROR_CODES = {
    2802:
    "RPM: Invalid Configuration Requested",
    2803:
    "RPM: Invalid Configuration Requested",
    2804:
    "RPM: Invalid Configuration Requested",
    2805:
    "RPM: Invalid Configuration Requested",
    2806:
    "RPM: Invalid Configuration Requested",
    2807:
    "RPM: Invalid Configuration Requested",
    2801:
    "RPM: Returned ID Error Response",
    2800:
    "RPM: Command Response Timeout",
    2702:
    "PMU: Temperature Within Normal Range",
    2701:
    "PMU: High Temperature Limit Exceeded",
    1905:
    "PMU: Measure Program Error",
    1904:
    "PMU: Source Program Error",
    1902:
    "PMU: Transmission to analog from digital error",
    1901:
    "PMU: Handshake from analog to digital error",
    1900:
    "PMU: DA Communication Timeout",
    400:
    "PMU: Invalid Attributes in SW Command",
    401:
    "PMU: Invalid Attributes in SW Command",
    402:
    "PMU: Invalid Attributes in SW Command",
    100:
    "LPTLib is executing function %s on instrument ID %d.",
    55:
    "%s is no longer in thermal shutdown.",
    54:
    "%s VXIBus device busy (command ID %04x). Timed out after %g seconds.",
    53: ("%s VXIbus transaction recovered after %u timeouts.Model 4200A-SCS Parameter Analyzer"
         "Reference Manual Section 13: LPT library function reference"),
    52:
    "%s VXIbus transaction (command ID %04x) timed out after %g seconds.",
    51:
    "Interlock reset.",
    50:
    "Interlock tripped.",
    40:
    "%s",
    24:
    "Config %d-%d complete for %s (%d).",
    23:
    "Config %d-%d starting for %s (%d).",
    22:
    "Binding %s (%d) to driver %s.",
    21:
    "Loading driver %s.",
    20:
    "Preloading model code %08x (%s).",
    15:
    "Executor started.",
    14:
    "%s channel closed.",
    13:
    "%s channel starting.",
    12:
    "TAPI services shutting down.",
    11:
    "Starting TAPI services.",
    9:
    "System configuration complete.",
    8:
    "System configuration starting.",
    4:
    "System initialization complete.",
    1:
    "The call was successful (no error).",
    0:
    "The call was successful (no error).",
    -4:
    "Too many instruments in configuration file %s.",
    -5:
    "Memory allocation failure.",
    -6:
    "Memory allocation error during configuration with configuration file %s.",
    -20:
    "Command not executed because a previous error was encountered.",
    -21:
    "Tester is in a fatal error state.",
    -22:
    "Fatal condition detected while in testing state.",
    -23:
    "Execution aborted by user.",
    -24:
    "Too many arguments.",
    -25:
    "%s is unavailable because it is in use by another test station.",
    -40:
    "%s.",
    -87:
    "Can not load library %s.",
    -88:
    "Invalid configuration file %s.",
    -89:
    "Duplicate IDs.",
    -90:
    "Duplicate instrument addresses in configuration file %s.",
    -91:
    "Duplicate instrument slots in configuration file %s.",
    -93:
    "Unrecognized/missing interface for %s in configuration file %s.",
    -94:
    "Unrecognized/missing PCI slot number for %s in configuration file %s.",
    -95:
    "Unrecognized/missing GPIB address for %s in configuration file %s.",
    -96:
    "GPIB Address out of range for %s was %i in configuration file %s.",
    -97:
    "PCI slot number out of range for %s was %i in configuration file %s.",
    -98:
    "Error attempting to load driver for model %s in configuration file %s.",
    -99:
    "Unrecognized/missing instrument ID in configuration file %s.",
    -100:
    "Invalid connection count, number of connections passed was %d.",
    -101:
    "Argument #%d is not a pin in the current configuration.",
    -102:
    "Multiple connections on %s.",
    -103:
    ("Dangerous connection using %s. Section 13: LPT library function reference Model 4200A-SCS"
     "Parameter Analyzer Reference Manual"),
    -104:
    "Unrecognized instrument or terminal not connected to matrix, argument #%d.",
    -105:
    "No pathway assigned to argument #%d.",
    -106:
    "Path %d previously allocated.",
    -107:
    "Not enough pathways to complete connection.",
    -108:
    "Argument #%d is not defined by configuration.",
    -109:
    "Illegal test station: %d.",
    -110:
    "A ground connection MUST be made.",
    -111:
    "Instrument low connection MUST be made.",
    -113:
    "There are no switching instruments in the system configuration.",
    -114:
    "Illegal connection.",
    -115:
    "Operation not allowed on a connected pin: %d.",
    -116:
    "No physical bias path from %s to %s.",
    -117:
    "Connection cannot be made because a required bus is in use.",
    -118:
    "Cannot switch to high current mode while sources are active.",
    -119:
    "Pin %d in use.",
    -120:
    "Illegal connection between %s and GNDU.",
    -121:
    "Too many calls were made to trigXX.",
    -122:
    "Illegal value for parameter #%d.",
    -124:
    "Sweep/Scan measure table overflow.",
    -126:
    "Insufficient user RAM for dynamic allocation.",
    -129:
    "Timer not enabled.",
    -137:
    "Invalid value for modifier.",
    -138:
    "Too many points specified in array.",
    -139:
    "An error was encountered while accessing the file %s.",
    -140:
    "%s unavailable while slaved to %s.",
    -141:
    "Timestamp not available because no measurement was made.",
    -142:
    "Cannot bind, instruments are incompatible.",
    -143:
    "Cannot bind, services unavailable or in use.",
    -152:
    "Function not supported by %s (%d).",
    -153:
    "Instrument with ID %d is not in the current configuration.",
    -154:
    "Unknown instrument name %s.",
    -155:
    "Unknown instrument ID %i.",
    -158:
    "VXI device in slot %d failed selftest (mfr ID: %04x, model number: %04x).",
    -159:
    "VME device with logical address %d is either non-VXI or non-functional.",
    -160:
    "Measurement cannot be performed because the source is not operational.",
    -161:
    "Instrument in slot %d has non-functional dual-port RAM.",
    -164:
    "VXI device in slot %d statically addressed at reserved address %d.",
    -165:
    "Service not supported by %s (%d).",
    -166:
    "Instrument with model code %08x is not recognized.",
    -167:
    "Invalid instrument attribute %s.",
    -169:
    "Instrument %s is not in the current configuration.",
    -190:
    "Ill-formed connection.",
    -191:
    "Mode conflict.",
    -192:
    "Instrument sense connection MUST be made.",
    -200: ("Force value too big for highest range %g.Model 4200A-SCS Parameter Analyzer"
           "Reference Manual Section 13: LPT library function reference"),
    -202:
    "I-limit value %g too small for specified range.",
    -203:
    "I-limit value %g too large for specified range.",
    -204:
    "I-range value %g too large for specified range.",
    -206:
    "V-limit value %g too large for specified range.",
    -207:
    "V-range value %g too large for specified range.",
    -213:
    "Value too big for range selection, %g.",
    -218:
    "Safe operating area for device exceeded.",
    -221:
    "Thermal shutdown has occurred on device %s.",
    -224:
    "Limit value %g too large for specified range.",
    -230:
    "V-limit value %g too small for specified range.",
    -231:
    "Range too small for force value.",
    -233:
    "Cannot force when not connected.",
    -235:
    "C-range value %g too large for specified range.",
    -236:
    "G-range value %g too large for specified range.",
    -237:
    "No bias source.",
    -238:
    "VMTR not allocated to make the measurement.",
    -239:
    "Timeout occurred attempting measurement.",
    -240:
    "Power Limited to 20 W. Check voltage and current range settings.",
    -250:
    "IEEE-488 time out during data transfer for addr %d.",
    -252:
    "No IEEE-488 interface in configuration.",
    -253:
    "IEEE-488 secondary address %d invalid for device.",
    -254:
    "IEEE-488 invalid primary address: %d.",
    -255:
    "IEEE-488 receive buffer overflow for address %d.",
    -261:
    "No SMU found, kelvin connection test not performed.",
    -262:
    "SRU not responding.",
    -263:
    "DMM not connected to SRU.",
    -264:
    "GPIB communication problem.",
    -265:
    "SRU not mechanically calibrated.",
    -266:
    "Invalid SRU command.",
    -267:
    "SRU hardware problem.",
    -268:
    "SRU kelvin connection problem.",
    -269:
    "SRU general error.",
    -270:
    "Floating point divide by zero.",
    -271:
    "Floating point log of zero or negative number.",
    -272:
    "Floating point square root of negative number.",
    -273:
    "Floating point pwr of negative number.",
    -280:
    "Label #%d not defined.",
    -281:
    "Label #%d redefined.",
    -282:
    "Invalid label ID #%d.",
    -301:
    "PCI ID read back on send error, slot.",
    -455:
    "Protocol version mismatch.",
    -510:
    "No command byte available (read) or SRQ not asserted.",
    -511:
    "CAC conflict.",
    -512:
    "Not CAC.",
    -513: ("Not SAC.Section 13: LPT library function reference Model 4200A-SCS Parameter Analyzer"
           " Reference Manual"),
    -514:
    "IFC abort.",
    -515:
    "GPIB timed out.",
    -516:
    "Invalid function number.",
    -517:
    "TCT timeout.",
    -518:
    "No listeners on bus.",
    -519:
    "Driver problem.",
    -520:
    "Bad slot number.",
    -521:
    "No listen address.",
    -522:
    "No talk address.",
    -523:
    "IBUP Software configuration error.",
    -524:
    "No utility function.",
    -550:
    "EEPROM checksum error in %s: %s.",
    -551:
    "EEPROM read error in %s: %s.",
    -552:
    "EEPROM write error in %s: %s.",
    -553:
    "%s returned unexpected error code %d.",
    -601:
    "System software internal error contact the factory.",
    -602:
    "Module load error: %s.",
    -603:
    "Module format error: %s.",
    -604:
    "Module not found: %s.",
    -610:
    "Could not start %s.",
    -611:
    "Network error.",
    -612:
    "Protocol error.",
    -620:
    "Driver load error. Could not load %s.",
    -621:
    "Driver configuration function not found. Driver is %s.",
    -640:
    "%s serial number %s failed diagnostic test %d.",
    -641:
    "%s serial number %s failed diagnostic test %d with a fatal fault.",
    -650:
    "Request to open unknown channel type %08x.",
    -660:
    "Invalid group ID %d.",
    -661:
    "Invalid test ID %d.",
    -662:
    "Ill-formed list.",
    -663:
    "Executor is busy.",
    -664:
    "Invalid unit ID %d.",
    -701:
    "Error configuring serial port %s.",
    -702:
    "Error opening serial port %s.",
    -703:
    "Call kspcfg before using kspsnd or ksprcv.",
    -704:
    "Error reading serial port.",
    -705:
    "Timeout reading serial port.",
    -706:
    "Terminator not received before read buffer filled.",
    -707:
    "Error closing serial port %s.",
    -801:
    "Exception code %d reported from VPU in slot %d, channel %d.",
    -802:
    "VPU in slot %d has reached thermal limit.",
    -803:
    "Start and stop values for defined segmented arb violate minimum slew rate.",
    -804:
    "Function not valid in the present pulse mode.",
    -805:
    "Too many points specified in array.",
    -806: ("Not enough points specified in array.Model 4200A-SCS Parameter Analyzer Reference"
           "Manual Section 13: LPT library function reference"),
    -807:
    "Function not supported by 4200-VPU.",
    -808:
    "Solid state relay control values ignored for 4200-VPU.",
    -809:
    "Time Per Point must be between %g and %g.",
    -810:
    "Attempts to control VPU trigger output are ignored by the 4200-VPU.",
    -811:
    "Measure range not valid for %s.",
    -812:
    "WARNING: Sequence %d, segment %d. Cannot measure with PGUs/VPUs.",
    -820:
    "PMU segment start value %gV at index %d does not match previous segment stop value of %gV.",
    -821:
    "PMU segment stop time (%g) greater than segment duration (%g)",
    -822:
    "PMU sequence error for entry %d. Start value %gV does not match previous stop value of %gV.",
    -823:
    "Start and stop window was specified for PMU segment %d, but no measurement type was set.",
    -824:
    "Measurement type was specified for PMU segment %d, but start and stop window is invalid.",
    -825:
    "%s set to post to column %s. Cannot fetch data that was registered as real-time.",
    -826:
    "Cannot execute PMU test. No channels defined.",
    -827:
    "Invalid pulse timing parameters in PMU Pulse IV test.",
    -828:
    "Maximum number of segments per PMU channel exceeded (%d).",
    -829:
    "The sum of base and amplitude voltages (%gV) exceeds maximum (%gV) for present range.",
    -830:
    "Pulse waveform configuration exceeded output limits. Increase pulse period or reduce amplitude or total time of pulsing.",
    -831:
    "Maximum number of samples per channel (%d) exceeded for PMU%d-CH%d.",
    -832:
    "Pulse slew rate is too low. Increase pulse amplitude or reduce pulse rise and fall time.",
    -833:
    "Invalid trigger source for PIV test.",
    -834:
    "Invalid pulse timing parameters.",
    -835:
    "Using the specified sample rate of %g samples/s, the time (%g) for sequence %d is too short for a measurement.",
    -836:
    "WARNING: Sequence %d, segment %d is attempting to measure while solid state relay is open. Disabling measurement.",
    -837:
    "No RPM connected to channel %d of PMU in slot %d.",
    -838:
    "Timing parameters specify a pulse that is too short for a measurement using %g samples/s.",
    -839:
    "Timing parameters contain measurement segments that are too short to measure using %g samples/s.",
    -840: ("SSR cannot be opened when using RPM ranges. Please change SSR array to enable relay or "
           "select PMU measure range."),
    -841: ("WARNING: SSR is open on segment immediately preceding sequence %d. "
           "Measurement will be invalid for 25 �s while relay settles."),
    -842:
    "This test has exceeded the system power limit by %g watts.",
    -843:
    "Step size of %g is not evenly divisible by 10 ns.",
    -844:
    "Invalid combination of start %g1, stop %g2 and step %g3.",
    -845:
    "No pulse sweeper was configured - Test will not run.",
    -846:
    "Maximum Source Voltage Reached: Requested voltage across DUT resistance exceeds maximum voltage available.",
    -847:
    "Output was not configured - Test will not run.",
    -848: ("Sweep step count mismatch for the sweeping channels. All sweeping channels must"
           " have same # of steps.Section 13: LPT library function reference Model 4200A-SCS "
           "Parameter Analyzer Reference Manual"),
    -849:
    "ILimit command is not supported for RPM in slot %d, channel %d.",
    -850:
    "Sample Rate mismatch. All channels in test must have the sample rate.",
    -851:
    "Invalid PxU stepper/sweeper configuration.",
    -900:
    "Environment variable KI_PRB_CONFIG is not set. The prober drivers will be inaccessible.",
    -901:
    "Environment variable KI_PRB_CONFIG contains an invalid path. The prober drivers will be inaccessible.",
    -902:
    "Prober configuration file not found. File was %s. The prober drivers will be inaccessible.",
    -903:
    "Unable to copy the prober configuration %s to %s. The prober driver many not be available."
}
