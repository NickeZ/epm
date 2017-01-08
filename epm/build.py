"""Define build"""
import os
#import subprocess

from .constants import MANIFEST_FILE, CACHE_DIR, BUILDDIR, DEPDIR
from .util import load_project_config, epics_compile, verify, apifetch, unpack
from .system_deps import check_system_prerequisites
from .toolchain import check_toolchain
from . import index


def build_dep(module, hostarch, version, depdir):
    """Build a dependency"""
    chksum = index.get_chksum(module, version)
    get = 'v1/packages/{}/{}'.format(module, chksum)
    apifetch('{} {}'.format(module, version), get)
    #print(verify(archive, chksum))
    archive = os.path.join(CACHE_DIR, index.archivename(module, version))
    moddir = os.path.join(depdir, '{}-{}'.format(module, version))
    unpack(module, archive, moddir)
    epics_compile(module, moddir, hostarch)

def check_dependencies(deps, hostarch, depdir):
    """Check deps"""
    for (dep, version) in deps.items():
        if not os.path.isdir(os.path.join(depdir, '{}-{}'.format(dep, version))):
            build_dep(dep, hostarch, version, depdir)
    raise Exception("stop")

def get_epics_version_and_host_arch(settings):
    """Get the default compiler.
    Returns toolchain without base, ubuntu1604-x86_64 for example
    """
    return settings['default-host-triple'].split('-', 1)

def build(settings, release, path):
    """Build project"""
    (epicsv, hostarch) = get_epics_version_and_host_arch(settings)
    check_system_prerequisites(hostarch)
    check_toolchain(epicsv, hostarch)
    project_conf = load_project_config(path)
    if release:
        depdir = os.path.join(path, BUILDDIR, 'release', DEPDIR)
    else:
        depdir = os.path.join(path, BUILDDIR, 'debug', DEPDIR)
    check_dependencies(project_conf['dependencies'], hostarch, depdir)
    project = os.path.basename(path)
    epics_compile(project, path, hostarch)
