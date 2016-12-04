"""Update"""

# External deps
import semver

from .matching import wildcard_match, caret_match, tilde_match, compat_match
from .index import load_epm_index
from .util import load_project_config, pretty_print

#python2 compat
try:
    basestring
except NameError:
    #pylint: disable=invalid-name
    basestring = str

#def update(path):
#    """Look for updated packages"""
#    # Update index
#
#    # Check if there are newer compatible
#    pass

def update(path):
    """Look for updated packages"""
    epm_index = load_epm_index()
    project_conf = load_project_config(path)
    if 'dependencies' in project_conf.keys():
        deps = project_conf['dependencies']
    else:
        deps = {}

def update_dependencies(deps, index):
    """Installs all dependencies"""
    for (dependency, required) in deps.items():
        if isinstance(required, dict):
            print('{} complex'.format(dependency))
        if isinstance(required, basestring):
            if "*" in required:
                print('{} wildcard'.format(dependency))
                version = find_latest_version(dependency, index, required, wildcard_match)
            elif "~" in required:
                print('{} tilde'.format(dependency))
                version = find_latest_version(dependency, index, required, tilde_match)
            elif "^" in required:
                print('{} caret'.format(dependency))
                version = find_latest_version(dependency, index, required, caret_match)
            else:
                print('{} compatibility'.format(dependency))
                version = find_latest_version_compat(dependency, index, required)
            pretty_print('Installing', '{} {}.{}.{}'.format(dependency, version.major, version.minor, version.patch))


# TODO(nc): Try to find exact match first.. compat may have changed in later verisons..
def find_latest_version_compat(name, index, matcher):
    """Find the latest version of index using compat_match"""
    for entry in reversed(index):
        if entry['name'] == name:
            version = semver.parse_version_info(entry['vers'])
            print((version, name, entry['compat']))
            if compat_match(version, matcher, entry['compat']):
                return version
    raise Exception("Dependency not found in index")

def find_latest_version(name, index, matcher, matcher_fun):
    """Find the latest version of index using matcher_fun"""
    for entry in reversed(index):
        if entry['name'] == name:
            version = semver.parse_version_info(entry['vers'])
            if matcher_fun(version, matcher):
                return version
    raise Exception("Dependency not found in index")
