"""EPM"""
from __future__ import print_function
import argparse
import os
import sys
import re
import subprocess
import shlex
import getpass

from string import Template
import pkg_resources

from .util import git_version, find_manifest_file
from .constants import MANIFEST_FILE, LOCK_FILE

#pylint: disable=broad-except
def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands', dest='command')
    parser_new = subparsers.add_parser('new', help='Create a new project')
    parser_new.add_argument('path')
    parser_new.add_argument('--ioc')
    parser_init = subparsers.add_parser('init',
                                        help='Create a new project in an existing direectory')
    parser_init.add_argument('--ioc')
    parser_build = subparsers.add_parser('build', help='Compile project')
    parser_build.add_argument('--target')
    parser_run = subparsers.add_parser('run', help='Run project')
    parser_run.add_argument('--target')
    parser_clean = subparsers.add_parser('clean', help='Delete compiled files')
    parser_clean.add_argument('--target')
    parser_update = subparsers.add_parser('update',
                                          help='Update dependencies in {}'.format(LOCK_FILE))
    parser_update.add_argument('--verbose')

    args = parser.parse_args(sys.argv[1:])

    if args.command == 'new':
        try:
            new(args.path)
        except Exception as why:
            print('Error: {}'.format(why))
    elif args.command == 'build':
        try:
            build()
        except Exception as why:
            print('Error: {}'.format(why))
    elif args.command == 'clean':
        try:
            clean()
        except Exception as why:
            print('Error: {}'.format(why))
    elif args.command == 'init':
        try:
            init(os.getcwd())
        except Exception as why:
            print('Error: {}'.format(why))
    else:
        print("Command not implemented")
        return 1

    return 0


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
        ignorefile_template = pkg_resources.resource_string(__name__,
                                                            "resources/templates/gitignore")
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
            name=os.path.basename(path),
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

def build():
    """Build project"""
    manifestfile = find_manifest_file(os.getcwd())
    if manifestfile:
        projectdir = os.path.dirname(manifestfile)
        subprocess.call('cd {}; make'.format(projectdir), shell=True)
    else:
        raise Exception('Could not find {}'.format(MANIFEST_FILE))

def clean():
    """Clean up project"""
    manifestfile = find_manifest_file(os.getcwd())
    if manifestfile:
        projectdir = os.path.dirname(manifestfile)
        subprocess.call('cd {}; make clean'.format(projectdir), shell=True)
    else:
        raise Exception('Could not find {}'.format(MANIFEST_FILE))
