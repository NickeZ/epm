"""EPM"""
from __future__ import print_function
import argparse
import os
import sys
import re
import subprocess
import shlex
import getpass
#import pprint

from string import Template
import pkg_resources

from .util import git_version, find_manifest_file
from .constants import MANIFEST_FILE, LOCK_FILE

#pylint: disable=broad-except
def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands', dest='command')
    p_new = subparsers.add_parser('new', help='Create a new project')
    p_new.add_argument('path')
    p_new.add_argument('--ioc', action='store_true')
    p_init = subparsers.add_parser('init',
                                   help='Create a new project in an existing direectory')
    p_init.add_argument('--ioc', action='store_true')
    p_build = subparsers.add_parser('build', help='Compile project')
    p_build.add_argument('--target')
    p_run = subparsers.add_parser('run', help='Run project')
    p_run.add_argument('--target')
    p_clean = subparsers.add_parser('clean', help='Delete compiled files')
    p_clean.add_argument('--target')
    p_update = subparsers.add_parser('update',
                                     help='Update dependencies in {}'.format(LOCK_FILE))
    p_update.add_argument('--verbose')
    p_install = subparsers.add_parser('install', help='Install module')
    p_install.add_argument('module', nargs='*',
                           help='Module to install')
    p_toolchain = subparsers.add_parser('toolchain', help='Administrate toolchains')
    p_t_sub = p_toolchain.add_subparsers(title='commands', dest='toolchain_command')
    p_t_list = p_t_sub.add_parser('list', help='List available toolchains')
    p_t_list.add_argument('placeholder', nargs='*',
                          help='Module to install')

    args = parser.parse_args(sys.argv[1:])

    if args.command == 'new':
        try:
            new(args.path, args.ioc)
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
            init(os.getcwd(), args.ioc)
        except Exception as why:
            print('Error: {}'.format(why))
    elif args.command == 'toolchain':
        if args.toolchain_command == 'list':
            print('list')
    else:
        print("Command not implemented")
        return 1

    return 0


def init(path, ioc):
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
        with open(os.path.join(path, '.gitignore'), 'wb') as ignorefile:
            ignorefile.write(ignorefile_template)

    # Generate Makefile
    makefile_template = pkg_resources.resource_string(__name__, "resources/templates/Makefile")
    with open(os.path.join(path, 'Makefile'), 'wb') as makefile:
        makefile.write(makefile_template)

    # Generate manifestfile
    epm_template = pkg_resources.resource_string(__name__, "resources/templates/Epm.toml").decode('utf-8')
    name = getpass.getuser()
    email = '{}@{}'.format(name, "localhost")
    if git_version():
        name = subprocess.check_output(shlex.split('git config user.name')).decode('utf-8').strip()
        email = subprocess.check_output(shlex.split('git config user.email')).decode('utf-8').strip()
    with open(os.path.join(path, MANIFEST_FILE), 'wb') as manifestfile:
        manifestfile.write(Template(epm_template).substitute(
            name=os.path.basename(path),
            author='{} <{}>'.format(name, email),
        ).encode('utf-8'))

    os.mkdir(os.path.join(path, 'src'))
    os.mkdir(os.path.join(path, 'db'))
    if ioc:
        os.mkdir(os.path.join(path, 'startup'))
        stcmd_template = pkg_resources.resource_string(__name__, "resources/templates/st.cmd")
        with open(os.path.join(path, 'startup', 'st.cmd'), 'wb') as stcmd:
            stcmd.write(stcmd_template)
    else:
        libname = os.path.basename(path)
        src_template = pkg_resources.resource_string(__name__, "resources/templates/library.c").decode('utf-8')
        with open(os.path.join(path, 'src', '{}.c'.format(libname)), 'wb') as libfile:
            libfile.write(Template(src_template).substitute(
                name=libname,
            ).encode('utf-8'))

        db_template = pkg_resources.resource_string(__name__, "resources/templates/library.template").decode('utf-8')
        with open(os.path.join(path, 'db', '{}.db'.format(libname)), 'wb') as dbfile:
            dbfile.write(Template(db_template).substitute(
                name=libname,
            ).encode('utf-8'))



def new(path, ioc):
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
    init(fullpath, ioc)

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
