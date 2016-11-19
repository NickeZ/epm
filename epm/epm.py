"""EPM"""
from __future__ import print_function
import argparse
import os
import re
import subprocess
import shlex
import getpass

import pkg_resources
from string import Template

MANIFEST_FILE = 'Epm.toml'
LOCK_FILE = 'Epm.lock'

def main(args):
    """Main function"""

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands', dest='command')
    parser_new = subparsers.add_parser('new', help='Create a new project')
    parser_new.add_argument('path')
    parser_init = subparsers.add_parser('init', help='Create a new project in an existing direectory')
    parser_build = subparsers.add_parser('build', help='Compile project')
    parser_run = subparsers.add_parser('run', help='Run project')
    parser_clean = subparsers.add_parser('clean', help='Delete compiled files')
    parser_update = subparsers.add_parser('update', help='Update dependencies in {}'.format(LOCK_FILE))

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
    elif args.command == 'init':
        try:
            init(os.getcwd())
        except Exception as why:
            print('Failed to initialize project: {}'.format(why))
    else:
        print("Command not implemented")

    return 0

class git_version:
    """Returns git version if git is installed, None if git isn't installed"""
    def __init__(self):
        null = open(os.devnull, 'w')
        try:
            version = subprocess.check_output(shlex.split('git --version'), stderr=null)
            self.version = version.split()
        except IOError:
            self.version = None
    def __call__(self):
        return self.version


def init(path):
    """Create a new project in current working dir"""
    # Abort if there already is a manifest file
    if find_manifest_file(path):
        raise ValueError('Already in an EPM project')

    # Initialize git repository
    if not os.path.isdir(os.path.join(path, '.git')) and git_version():
        status = subprocess.call('cd {}; git init'.format(path), shell=True)
        if status:
            raise Exception('Failed to run git init')

    # Generate git ignore file
    if git_version():
        ignorefile_template = pkg_resources.resource_string(__name__, "resources/templates/gitignore")
        with open(os.path.join(path, '.gitignore'), 'w') as ignorefile:
            ignorefile.write(ignorefile_template)

    # Generate Makefile
    makefile_template = pkg_resources.resource_string(__name__, "resources/templates/Makefile")
    with open(os.path.join(path, 'Makefile'), 'w') as makefile:
        makefile.write(makefile_template)

    # Generate manifestfile
    epm_template = pkg_resources.resource_string(__name__, "resources/templates/Epm.toml")
    name = getpass.getuser()
    email = '{}@{}'.format(name, "localhost")
    if git_version():
        name = subprocess.check_output(shlex.split('git config user.name'))
        email = subprocess.check_output(shlex.split('git config user.email'))
    with open(os.path.join(path, MANIFEST_FILE), 'w') as manifestfile:
        manifestfile.write(Template(epm_template).substitute(
            name=path,
            author='{} <{}>'.format(name.strip(), email.strip()),
        ))


def new(path):
    """Create new project in path"""
    # Abort on wrong input, we accept A-Z, a-z, dash '-' and underscore '_'
    if re.search(r'[^A-Za-z0-9\-_]', path):
        raise ValueError('Found invalid characters in project name')

    # Abort if there already is a manifest file
    fullpath = os.path.join(os.getcwd(), path)
    if find_manifest_file(fullpath):
        raise ValueError('Already in an EPM project')

    # Create project directory
    os.mkdir(path)

    # Initialize project in created directory
    init(fullpath)

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

def build():
    """Build project"""
    manifestfile = find_manifest_file(os.getcwd())
    if manifestfile:
        projectdir = os.path.dirname(manifestfile)
        subprocess.call('cd {}; make'.format(projectdir), shell=True)
    else:
        raise Exception('Could not find {} file'.format(MANIFEST_FILE))

def clean():
    """Clean up project"""
    print('clean')
