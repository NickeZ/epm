"""Define build"""
import os
#import subprocess

from .constants import MANIFEST_FILE
from .util import load_project_config, epics_compile
from .system_deps import check_system_prerequisites
from .toolchain import check_toolchain

def build(settings, path):
    """Build project"""
    (epicsv, hostarch) = get_epics_version_and_host_arch(settings)
    check_system_prerequisites(hostarch)
    check_toolchain(epicsv, hostarch)
    project_conf = load_project_config(path)
    check_dependencies()
    if path:
        project = os.path.basename(path)
        epics_compile(project, path, hostarch)
    else:
        raise Exception('Could not find {}'.format(MANIFEST_FILE))

def check_dependencies():
    """Check deps"""
    #Look in lockfile
    #check if deps are installed
    #otherwise install from index

def get_epics_version_and_host_arch(settings):
    """Get the default compiler"""
    return settings['default-host-triple'].split('-', 1)
