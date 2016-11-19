"""EPM"""
from __future__ import print_function
import argparse
import os
import re
import subprocess

import pkg_resources

MANIFEST_FILE = 'Epm.toml'

def main(args):
    """Main function"""

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands', dest='command')
    parser_new = subparsers.add_parser('new', help='Create a new project')
    parser_build = subparsers.add_parser('build', help='Compile project')
    parser_clean = subparsers.add_parser('clean', help='Delete compiled files')

    parser_new.add_argument('path')

    args = parser.parse_args(args)

    if args.command == 'new':
        try:
            new(args.path)
        except Exception as why:
            print('Failed to create new project: {}'.format(why))
    elif args.command == 'build':
        try:
            build()
        except Exception as why:
            print('Failed to build project: {}'.format(why))
    elif args.command == 'clean':
        try:
            clean()
        except Exception as why:
            print('Failed to build project: {}'.format(why))

    return 0

def new(path):
    """Create new project in path"""
    # Cleanup the input we accept A-Z, a-z, dash '-' and underscore '_'
    if re.search(r'[^A-Za-z0-9\-_]', path):
        raise ValueError('Found invalid characters in project name')

    os.mkdir(path)

    status = subprocess.call('cd {}; git init'.format(path), shell=True)
    if status:
        raise Exception('Failed to run git init')

    subprocess.call('touch {}/.gitignore'.format(path), shell=True)
    subprocess.call('echo "include ${{EPICS_ENV_PATH}}" >> {}/Makefile'.format(path), shell=True)
    my_data = pkg_resources.resource_string(__name__, "Epm.toml")
    subprocess.call('touch {}/Epm.toml'.format(path), shell=True)

def dirs_to_root(path):
    """A generator that yields the full path to each directory all the way back to root."""
    yield path + os.path.sep
    while len(path) > 1:
        (path, _) = path.rsplit(os.path.sep, 1)
        yield path + os.path.sep

def find_toml_file(path):
    """Find the toml file. Start from path and then search upwards."""
    for path in dirs_to_root(path):
        tomlfile = os.path.join(path, MANIFEST_FILE)
        if os.path.isfile(tomlfile):
            return path
    return None

def build():
    """Build project"""
    tomlfile = find_toml_file(os.getcwd())
    if tomlfile:
        projectdir = os.path.dirname(tomlfile)
        subprocess.call('cd {}; make'.format(projectdir), shell=True)
    else:
        raise Exception('Could not find Epm.toml file')

def clean():
    """Clean up project"""
    print('clean')
