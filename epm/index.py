"""Index"""
import os
import json

from .constants import INDEX_DIR

def get_index_entries(package):
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
