"""Keep constants here to avoid circular dependnecies of python modules..."""
import os

MANIFEST_FILE = 'Epm.toml'
LOCK_FILE = 'Epm.lock'
EPM_DIR = os.path.expanduser('~/.epm')
CACHE_DIR = os.path.join(EPM_DIR, 'tmp')
EPM_SERVER = 'http://epics.esss.se:8000'
