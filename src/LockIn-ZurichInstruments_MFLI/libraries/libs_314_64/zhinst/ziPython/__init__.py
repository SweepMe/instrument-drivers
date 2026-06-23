"""ziPython compatibility layer. Use `zhinst.core` instead.

.. deprecated:: 22.08
   Functionality was moved to :mod:`zhinst.core`. This module is a
   compatibility layer to ease migration.

"""

import warnings
from zhinst.core import *
from zhinst.core import __version__

warnings.warn(
    "The zhinst.ziPython package has been renamed to zhinst.core. "
    "Please adjust your import statements accordingly.",
    DeprecationWarning,
)
