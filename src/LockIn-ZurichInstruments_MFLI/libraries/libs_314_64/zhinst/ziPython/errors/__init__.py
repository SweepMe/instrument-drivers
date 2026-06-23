import warnings
from zhinst.core.errors import *

warnings.warn(
    "The zhinst.ziPython package has been renamed to zhinst.core. "
    "Please adjust your import statements accordingly.",
    DeprecationWarning,
)
