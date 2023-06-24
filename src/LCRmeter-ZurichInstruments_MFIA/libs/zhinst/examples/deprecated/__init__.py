# -*- coding: utf-8 -*-
"""
Zurich Instruments LabOne Python API Deprecated Examples.

The examples in this package are marked as deprecated since they use Modules
that will at some point be discontinued: The SW Trigger Module (RecorderModule
class) and Spectrum Module (ZoomFFTModule class). These modules have been
superseded by the Data Acquisition Module; please refer to the examples in
zhinst.examples.common that use the DataAcquisitionModule class.
"""

import zhinst.examples.deprecated.example_swtrigger_edge
import zhinst.examples.deprecated.example_swtrigger_grid
import zhinst.examples.deprecated.example_swtrigger_grid_average
import zhinst.examples.deprecated.example_swtrigger_trackingedge
import zhinst.examples.deprecated.example_spectrum

__all__ = ["example_swtrigger_edge",
           "example_swtrigger_grid",
           "example_swtrigger_grid_average",
           "example_swtrigger_trackingedge",
           "example_spectrum"]

del zhinst
