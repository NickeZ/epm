"""Utilites used by EPM"""
import os
import subprocess
import shlex

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
    subprocess.call(shlex.split('echo call>>/tmp/niklas'))
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

