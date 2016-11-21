"""Utilites used by EPM"""
import os
import subprocess
import shlex
import platform

from .constants import MANIFEST_FILE

def memoize(function):
    """Decorator that caches function calls"""
    memo = {}
    def wrapper(*args):
        """Wrapper"""
        if args in memo:
            return memo[args]
        else:
            retval = function(*args)
            memo[args] = retval
        return retval
    return wrapper

@memoize
def git_version():
    """Returns git version if git is installed, None if git isn't installed"""
    null = open(os.devnull, 'w')
    try:
        version = subprocess.check_output(shlex.split('git --version'), stderr=null)
        return version.split()
    except IOError:
        return None

def dirs_to_root(path):
    """A generator that yields the full path to each directory all the way back to root."""
    yield path + os.path.sep
    while len(path) > 1:
        (path, _) = path.rsplit(os.path.sep, 1)
        yield path + os.path.sep

def find_manifest_file(path):
    """Find the manifest file. Start from path and then search upwards."""
    for path in dirs_to_root(path):
        manifestfile = os.path.join(path, MANIFEST_FILE)
        if os.path.isfile(manifestfile):
            return path
    return None

def get_epics_host_arch():
    """Try to figure out the host architecture."""
    #pylint: disable=deprecated-method
    (dist, version, _) = platform.linux_distribution()
    dist = dist.lower()
    if dist:
        if 'centos' in dist:
            return 'centos{}-{}'.format(version[0], platform.machine())
        elif 'scientific linux' in dist:
            return 'SL{}-{}'.format(version[0], platform.machine())
        elif 'ubuntu' in dist:
            return '{}{}-{}'.format(dist, version.replace('.', ''), platform.machine())
        elif 'debian' in dist:
            return '{}{}-{}'.format(dist, version[0], platform.machine())
    return '{}-{}'.format(platform.system().lower(), platform.machine())

def pretty_print(action, message):
    """Prints a line a little bit prettier"""
    print('\x1b[1m{:>12}\x1b[0m {}'.format(action, message))

def pretty_eprint(action, message):
    """Prints a line a little bit prettier"""
    print('\x1b[1;31m{}: \x1b[0m {}'.format(action, message))
