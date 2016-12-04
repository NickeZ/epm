"""Clean"""
import subprocess
import os

from .util import pretty_print, pretty_eprint
from .constants import MANIFEST_FILE

def clean(path):
    """Clean up project"""
    pretty_print('Cleaning', os.path.basename(path))
    if path:
        status = subprocess.call('cd {}; make clean'.format(path), shell=True)
        if status != 0:
            pretty_eprint('Error', 'Failed to clean up project')
    else:
        raise Exception('Could not find {}'.format(MANIFEST_FILE))
