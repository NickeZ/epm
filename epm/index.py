"""Index"""
import json

def load_epm_index():
    """Load the EPM index of modules"""
    return json.loads("""[
            {"name": "asyn", "vers": "4.21.0", "compat":"patch", "deps": []},
            {"name": "asyn", "vers": "4.23.0", "compat":"patch", "deps": []},
            {"name": "asyn", "vers": "4.27.0", "compat":"patch", "deps": []},
            {"name": "andor", "vers": "2.20.0", "compat":"minor", "deps": []},
            {"name": "andor", "vers": "2.21.3", "compat":"minor", "deps": []},
            {"name": "andor", "vers": "2.21.5", "compat":"minor", "deps": []},
            {"name": "andor", "vers": "2.21.8", "compat":"minor", "deps": []},
            {"name": "andor", "vers": "2.22.0", "compat":"minor", "deps": []}
            ]""")
