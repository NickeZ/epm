"""Keep constants here to avoid circular dependnecies of python modules..."""
import os

MANIFEST_FILE = 'Epm.toml'
LOCK_FILE = 'Epm.lock'
EPM_DIR = os.path.expanduser('~/.epm')
CACHE_DIR = os.path.join(EPM_DIR, 'tmp')
INDEX_DIR = os.path.join(CACHE_DIR, 'index')
EPM_SERVER = 'https://epics.ncic.se'
SIPHASH_KEY = bytearray.fromhex('9664 06fe 676f 1a04 b799 059f cff6 a9a8')
