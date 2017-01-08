"""Clean"""
import os
import shutil

from .util import pretty_print, pretty_eprint
from .constants import BUILDDIR

def clean(path):
    """Clean up project"""
    pretty_print('Cleaning', os.path.basename(path))
    try:
        shutil.rmtree(os.path.join(path, BUILDDIR))
    except OSError:
        pretty_eprint('Error', 'Failed to clean up project')
