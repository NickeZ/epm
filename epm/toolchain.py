"""Handle toolchains"""

import os

from .constants import EPM_DIR
from .util import fetch, unpack, epics_compile

def check_toolchain(epicsversion, hostarch):
    """Checks if we have the toolchain, otherwise downloads and compiles"""
    toolchains_dir = os.path.join(EPM_DIR, 'toolchains')
    if not os.path.isdir(toolchains_dir):
        os.mkdir(toolchains_dir)
    toolchain_dir = os.path.join(toolchains_dir, 'base-{}-{}'.format(epicsversion, hostarch))
    if not os.path.isdir(toolchain_dir):
        archive = 'base-{}.tar.gz'.format(epicsversion)
        target = '{}-{}.tar.gz'.format(epicsversion, hostarch)
        base_name = 'EPICS Base {}'.format(epicsversion)
        target_name = 'Toolchain {}'.format(hostarch)
        fetch(base_name, archive)
        fetch(target_name, target)
        os.mkdir(toolchain_dir)
        unpack(base_name, archive, toolchain_dir)
        unpack(target_name, target, toolchain_dir)
        epics_compile('{}-{}'.format(base_name, hostarch), toolchain_dir, hostarch)
