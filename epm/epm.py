"""EPM"""
from __future__ import print_function
import argparse
import os
import sys
import re
import subprocess
import shlex
import getpass
import urllib.request
import shutil
import multiprocessing
#import pprint

from string import Template
import pkg_resources
import toml

# Ignore unused imports while developing
# pylint: disable=unused-import
from .util import git_version, find_manifest_file, get_epics_host_arch, pretty_print, pretty_eprint
from .constants import MANIFEST_FILE, LOCK_FILE, EPM_DIR, CACHE_DIR, EPM_SERVER

#pylint: disable=invalid-name
settings = {}

def main():
    #pylint: disable=broad-except
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

    read_settings_file()

    manifestfile = find_manifest_file(os.getcwd())
    projectdir = None
    if manifestfile:
        projectdir = os.path.dirname(manifestfile)

    try:
        if args.command == 'new':
            new(args.path, args.ioc)
        elif args.command == 'build':
            build(projectdir)
        elif args.command == 'clean':
            clean(projectdir)
        elif args.command == 'init':
            init(os.getcwd(), args.ioc)
        elif args.command == 'toolchain':
            if args.toolchain_command == 'list':
                print('list')
        else:
            print("Command not implemented")
        return 1
    except Exception as why:
        pretty_eprint('Error', '{}'.format(why))
    return 0

def read_settings_file():
    """Reads the settings file"""
    #pylint: disable=global-statement
    global settings
    configfile = os.path.expanduser("~/.epm/config.toml")
    if os.path.isfile(configfile):
        with open(configfile) as tomlfile:
            settings = toml.loads(tomlfile.read())
    else:
        generate_default_config()


def generate_default_config():
    """Generates the default config file"""
    #pylint: disable=global-statement
    global settings
    settings = {'default-host-triple': '3.15.4-{}'.format(get_epics_host_arch())}
    configfile = os.path.expanduser("~/.epm/config.toml")
    if not os.path.isdir(os.path.dirname(configfile)):
        os.mkdir(os.path.dirname(configfile))
    with open(configfile, 'wb') as tomlfile:
        tomlfile.write(toml.dumps(settings).encode('utf-8'))

def create_template(target, resource, substitutions=None):
    """Generate a template with substitutions from a resource"""
    # Get resource
    tmpl_in = pkg_resources.resource_string(
        __name__,
        resource,
    ).decode('utf-8')

    # Don't create file if it exists
    if os.path.isfile(target):
        return

    # Write template
    with open(target, 'wb') as target_file:
        target_file.write(
            Template(tmpl_in).substitute(substitutions).encode('utf-8')
        )


def init(path, ioc):
    """Create a new project in current working dir"""
    init_priv(path, ioc)
    pretty_print('Created', 'EPICS project')

def init_priv(path, ioc):
    """Create a new project in path"""
    # Abort if there already is a manifest file
    if find_manifest_file(path):
        raise ValueError('Already in an EPM project')

    # Initialize git repository
    if not os.path.isdir(os.path.join(path, '.git')) and git_version():
        try:
            subprocess.check_output('cd {}; git init'.format(path), shell=True)
        except subprocess.CalledProcessError as why:
            raise Exception('Failed to run git init: {}'.format(why))

    # Generate git ignore file
    if git_version():
        create_template(
            os.path.join(path, '.gitignore'),
            'resources/templates/gitignore',
        )

    # Generate Makefile (GNUmakefile if Makefile exists)
    makefile = 'Makefile'
    if os.path.isfile(os.path.join(path, 'Makefile')):
        makefile = 'GNUmakefile'

    create_template(
        os.path.join(path, makefile),
        'resources/templates/Makefile'
    )

    # Generate manifestfile
    name = getpass.getuser()
    email = u'{}@{}'.format(name, "localhost")
    if git_version():
        try:
            name = subprocess.check_output(
                shlex.split('git config user.name')
            ).decode('utf-8').strip()
            email = subprocess.check_output(
                shlex.split('git config user.email')
            ).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            raise Exception('Git is installed but not configured, username or email missing')
    create_template(
        os.path.join(path, MANIFEST_FILE),
        "resources/templates/Epm.toml",
        {
            'name': os.path.basename(path),
            'author': '{} <{}>'.format(name, email)
        }
    )

    os.mkdir(os.path.join(path, 'src'))
    os.mkdir(os.path.join(path, 'db'))
    if ioc:
        os.mkdir(os.path.join(path, 'startup'))
        create_template(
            os.path.join(path, 'startup', 'st.cmd'),
            "resources/templates/st.cmd"
        )
    else:
        libname = os.path.basename(path)
        create_template(
            os.path.join(path, 'src', '{}.c'.format(libname)),
            "resources/templates/library.c",
            {'name': libname}
        )

        create_template(
            os.path.join(path, 'db', '{}.db'.format(libname)),
            "resources/templates/library.template",
            {'name': libname}
        )


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
    init_priv(fullpath, ioc)

    pretty_print('Created', 'EPICS project "{}"'.format(path))

def build(path):
    """Build project"""
    (epicsv, hostarch) = get_epics_version_and_host_arch()
    verify_prerequisites(hostarch)
    verify_toolchain(epicsv, hostarch)
    if path:
        project = os.path.basename(path)
        epics_compile(project, path, hostarch)
    else:
        raise Exception('Could not find {}'.format(MANIFEST_FILE))

REQUIRED_APPS = [
    'gcc',
    'c++',
    'xsubpp',
    'podchecker',
]
REQUIRED_DEVS = [
    '/usr/include/boost',
    '/usr/include/readline/readline.h',
]

SATISFIES = {
    'centos7': {
        'gcc': 'gcc',
        'c++': 'gcc-c++',
        'xsubpp': 'perl-ExtUtils-ParseXs',
        'podchecker': 'perl-Pod-Checker',
        '/usr/include/boost': 'boost-devel',
        '/usr/include/readline/readline.h': 'readline-devel',
    },
    'ubuntu1604': {
        'gcc': 'gcc',
        'c++': 'g++',
        'xsubpp': 'libextutils-xspp-perl',
        'podchecker': 'perl',
        '/usr/include/boost': 'libboost-dev',
        '/usr/include/readline/readline.h': 'libreadline-dev',
    },
}

def verify_prerequisites(hostarch):
    """Look for all prerequisites on system"""
    missing = set()
    for app in REQUIRED_APPS:
        try:
            subprocess.check_output('which {}'.format(app), shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError:
            missing.add(app)
    for header in REQUIRED_DEVS:
        if not os.path.exists(header):
            missing.add(header)

    if not missing:
        return

    if 'centos7' in hostarch:
        pretty_eprint('Error', 'Please run `sudo yum install {}`'.format(
            ' '.join([SATISFIES['centos7'][x] for x in missing])))
        raise Exception('Missing dependencies')
    elif 'ubuntu1604' in hostarch:
        pretty_eprint(
            'Error',
            'Please do `sudo apt install {}`'.format(
                ' '.join([SATISFIES['ubuntu1604'][x] for x in missing])))
        raise Exception('Missing dependencies')

def verify_toolchain(epicsversion, hostarch):
    """Checks if we have the toolchain, otherwise downloads and compiles"""
    toolchains_dir = os.path.join(EPM_DIR, 'toolchains')
    if not os.path.isdir(toolchains_dir):
        os.mkdir(toolchains_dir)
    toolchain_dir = os.path.join(toolchains_dir, 'base-{}-{}'.format(epicsversion, hostarch))
    if not os.path.isdir(toolchain_dir):
        os.mkdir(toolchain_dir)
        archive = 'base-{}.tar.gz'.format(epicsversion)
        target = '{}-{}.tar.gz'.format(epicsversion, hostarch)
        base_name = 'EPICS Base {}'.format(epicsversion)
        target_name = 'Toolchain {}'.format(hostarch)
        fetch(base_name, archive)
        fetch(target_name, target)
        unpack(base_name, archive, toolchain_dir)
        unpack(target_name, target, toolchain_dir)
        epics_compile('{}-{}'.format(base_name, hostarch), toolchain_dir, hostarch)

def fetch(name, archive):
    """Fetch archive from http server"""
    pretty_print('Downloading', name)
    if not os.path.isdir(CACHE_DIR):
        os.mkdir(CACHE_DIR)
    (local_filename, headers) = urllib.request.urlretrieve('{}/{}'.format(EPM_SERVER, archive))
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

def get_epics_version_and_host_arch():
    """Get the default compiler"""
    return settings['default-host-triple'].split('-', 1)

def clean(path):
    """Clean up project"""
    pretty_print('Cleaning', os.path.basename(path))
    if path:
        subprocess.call('cd {}; make clean'.format(path), shell=True)
    else:
        raise Exception('Could not find {}'.format(MANIFEST_FILE))
