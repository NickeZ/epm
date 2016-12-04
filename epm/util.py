"""Utilites used by EPM"""
import os
import subprocess
import multiprocessing
import shlex
import shutil
import platform
import urllib.request

#External deps
import toml

from .constants import MANIFEST_FILE, CACHE_DIR, EPM_SERVER

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

def load_project_config(path):
    """Opens project manifest file and returns configuration"""
    with open(os.path.join(path, MANIFEST_FILE), 'r') as manifest:
        return toml.loads(manifest.read())

def fetch(name, archive):
    """Fetch archive from http server"""
    pretty_print('Downloading', name)
    (local_filename, headers) = urllib.request.urlretrieve('{}/{}'.format(EPM_SERVER, archive))
    if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)
    shutil.copy(local_filename, os.path.join(CACHE_DIR, archive))

def unpack(name, archive, target):
    """Unpack archive"""
    pretty_print('Unpacking', name)
    subprocess.check_output('tar --extract --file {} -C {}'.format(
        os.path.join(CACHE_DIR, archive),
        target
    ), shell=True)

def epics_compile(name, path, hostarch):
    """Compile with EPICS_HOST_ARCH"""
    pretty_print('Compiling', name)
    cur_env = os.environ.copy()
    cur_env["EPICS_HOST_ARCH"] = hostarch
    cores = multiprocessing.cpu_count() + 1
    subprocess.check_output('cd {}; make -j{}'.format(path, cores),
                            env=cur_env,
                            shell=True,
                            stderr=subprocess.STDOUT)
