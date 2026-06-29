"""fast, simple packet creation and parsing."""
from __future__ import absolute_import
from __future__ import division
import sys

__author__ = 'Sebastian Block'
__author_email__ = 'sebastian.block@world-wi.de'
__license__ = 'MIT'
__url__ = 'https://codeberg.org/paperwork/python-ethernetip'
__version__ = '1.1.2'

from .ethernetip import *

# Note: list() is used to get a copy of the dict in order to avoid
# "RuntimeError: dictionary changed size during iteration"
# exception in Python 3 caused by _mod_init() funcs that load another modules
for name, mod in list(sys.modules.items()):
    if name.startswith('dpkt.') and hasattr(mod, '_mod_init'):
        mod._mod_init()
