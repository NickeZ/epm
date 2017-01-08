"""Index"""
import os
import json
import subprocess

from .constants import INDEX_DIR

def get_entries(package):
    """Get all the entries a package has in the index.
    Returns the list with the latest entries first
    """
    result = []
    try:
        with open(os.path.join(INDEX_DIR, 'packages', package)) as package_file:
            for line in package_file:
                result.append(json.loads(line))
        return reversed(result)
    except IOError:
        return []

def get_entry(package, version):
    """Get a package-version entry from the index"""
    entries = get_entries(package)
    for entry in entries:
        if entry['vers'] == version:
            return entry
    return None

def archivename(package, version):
    """Create the archive name from index info"""
    metadata = get_entry(package, version)
    if metadata:
        return '{}-{}-{}.tar.gz'.format(package, version, metadata['chksum'])
    return None

def get_chksum(package, version):
    """Get chksum from index"""
    metadata = get_entry(package, version)
    if metadata:
        return metadata['chksum']
    return None

def pull():
    """Pull latest index changes"""
    subprocess.call('cd {}; git pull'.format(INDEX_DIR), shell=True)
