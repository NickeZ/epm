"""EPM"""
from __future__ import print_function
import argparse
import os
import sys

# External deps
import toml

# Ignore unused imports while developing
# pylint: disable=unused-import
from .util import git_version, find_manifest_file, get_epics_host_arch, pretty_print, pretty_eprint
from .constants import MANIFEST_FILE, LOCK_FILE, EPM_DIR, CACHE_DIR, EPM_SERVER
from .new import new, init
from .build import build
from .update import update
from .clean import clean
from .system_deps import check_system_prerequisites
from .publish import publish
from . import index

def run(command, args, settings, projectdir):
    """Run command"""
    res = 0
    if command == 'new':
        new(args.path, args.ioc)
    elif command == 'init':
        init(os.getcwd(), args.ioc)
    elif command == 'toolchain':
        if args.toolchain_command == 'list':
            print('list')
    elif command in ('build', 'clean', 'update', 'publish') and projectdir:
        if command == 'build':
            index.pull()
            build(settings, args.release, projectdir)
        elif command == 'clean':
            clean(projectdir)
        elif command == 'update':
            index.pull()
            update(projectdir)
        elif command == 'publish':
            publish(projectdir)
    elif command in ('build', 'clean', 'update', 'publish'):
        pretty_eprint('Error', 'Failed to find project directory')
        res = 1
    else:
        print("Command not implemented")
        res = 1
    return res

def main():
    """Main function"""
    # pylint: disable=too-many-locals, too-many-statements
    parser = argparse.ArgumentParser(
        description='An EPICS Package Manager',
        epilog="See 'epm help <command>' for more information...",
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug prints',
    )

    subparsers = parser.add_subparsers(
        title='commands',
        dest='command',
        metavar='command',
    )

    p_new = subparsers.add_parser(
        'new',
        help='Create a new project'
    )
    p_new.add_argument('path')
    p_new.add_argument('--ioc', action='store_true')

    p_init = subparsers.add_parser(
        'init',
        help='Create a new project in an existing direectory'
    )
    p_init.add_argument('--ioc', action='store_true')

    p_build = subparsers.add_parser(
        'build',
        help='Compile project'
    )
    p_build.add_argument('--target')
    p_build.add_argument(
        '--release',
        help='Build a release version with optimizations',
        action='store_true',
    )

    p_run = subparsers.add_parser(
        'run',
        help='Run project'
    )
    p_run.add_argument('--target')

    p_clean = subparsers.add_parser(
        'clean',
        help='Delete compiled files'
    )
    p_clean.add_argument('--target')

    p_update = subparsers.add_parser(
        'update',
        help='Update dependencies in {}'.format(LOCK_FILE)
    )
    p_update.add_argument('--verbose')

    p_publish = subparsers.add_parser(
        'publish',
        help='Package and upload module'
    )

    p_install = subparsers.add_parser(
        'install',
        help='Install module'
    )
    p_install.add_argument(
        'module',
        nargs='*',
        help='Module to install'
    )

    p_toolchain = subparsers.add_parser(
        'toolchain',
        help='Administrate toolchains'
    )
    p_t_sub = p_toolchain.add_subparsers(
        title='commands',
        dest='toolchain_command'
    )
    p_t_list = p_t_sub.add_parser(
        'list',
        help='List available toolchains'
    )
    p_t_list.add_argument(
        'placeholder',
        nargs='*',
        help='Module to install'
    )

    args = parser.parse_args(sys.argv[1:])

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Read the config file from user home directory. Create if needed
    try:
        settings = read_config()
    except toml.TomlDecodeError:
        pretty_eprint('Error', 'Failed to parse toml in config file')
        sys.exit(1)
    if not settings:
        settings = generate_default_config()
    if not settings:
        pretty_eprint('Error', 'Failed to generate config file')
        sys.exit(1)

    # Find a manifest file in this folder or any parent folder
    manifestfile = find_manifest_file(os.getcwd())
    if manifestfile:
        projectdir = os.path.dirname(manifestfile)
    else:
        projectdir = None

    # pylint: disable=broad-except
    # Cath all exceptions and print a more user-friendly error if we are not in debug
    if args.debug:
        return run(args.command, args, settings, projectdir)
    else:
        try:
            return run(args.command, args, settings, projectdir)
        except Exception as why:
            pretty_eprint('Error', '{}'.format(why))
            return 1

def read_config():
    """Reads the settings file"""
    configfile = os.path.expanduser("~/.epm/config.toml")
    if os.path.isfile(configfile):
        try:
            with open(configfile) as tomlfile:
                return toml.loads(tomlfile.read())
        except IOError:
            return None
    else:
        return None

def generate_default_config():
    """Generates the default config file"""
    settings = {'default-host-triple': '3.15.4-{}'.format(get_epics_host_arch())}
    configfile = os.path.expanduser("~/.epm/config.toml")
    if not os.path.isdir(os.path.dirname(configfile)):
        os.mkdir(os.path.dirname(configfile))
    try:
        with open(configfile, 'wb') as tomlfile:
            tomlfile.write(toml.dumps(settings).encode('utf-8'))
        return settings
    except IOError:
        return None
