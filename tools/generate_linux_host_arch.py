#!/usr/bin/python3
"""Helper program to generate os specific epics host architectures"""
import argparse
import os
import sys
import platform
import subprocess
import tempfile
from string import Template
import pkg_resources

CONFIG_FILES = [
    'CONFIG.Common.{0}',
    'CONFIG.{0}.Common',
    'CONFIG.{0}.{0}']

CONFIG_FILES_DEBUG = CONFIG_FILES + [
    'CONFIG_SITE.{0}.{0}']

CONFIG_FILES_HOST = CONFIG_FILES + [
    'CONFIG_SITE.Common.{0}',
    'CONFIG_SITE.{0}.Common']

CONFIG_FILES_CROSS = [
    'CONFIG.{0}.{1}']

OSDIR = os.path.join('configure', 'os')

def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('os')
    args = parser.parse_args(sys.argv[1:])

    generic_epics_arch = '{}-{}'.format(platform.system().lower(), platform.machine())

    tmpdir = tempfile.mkdtemp()

    osdir = os.path.join(tmpdir, OSDIR)

    if not os.path.isdir(osdir):
        os.makedirs(osdir)

    generate_files(
        osdir,
        args.os,
        generic_epics_arch,
        CONFIG_FILES_HOST
    )
    generate_files(
        osdir,
        '{}-debug'.format(args.os),
        '{}-debug'.format(generic_epics_arch),
        CONFIG_FILES_DEBUG
    )
    generate_files_cross(
        osdir,
        args.os,
        '{}-debug'.format(args.os),
        generic_epics_arch,
        '{}-debug'.format(generic_epics_arch),
        CONFIG_FILES_CROSS
    )
    subprocess.call('tar cf {}.tar.gz configure -C {}'.format(args.os, tmpdir), shell=True)

def generate_files(osdir, epics_arch, generic_epics_arch, config_files):
    """Generate epics_arch with includes of generic_epics_arch"""
    for config in config_files:
        tmpl_filename = config.format('linuxos')
        tmpl_in = pkg_resources.resource_string(
            __name__,
            'resources/{}'.format(tmpl_filename)
        ).decode('utf-8')

        config_filename = os.path.join(osdir, config.format(epics_arch))
        with open(config_filename, 'wb') as outfile:
            outfile.write(Template(tmpl_in).substitute(
                linuxos=epics_arch,
                genericlinux=generic_epics_arch,
                generictarget=generic_epics_arch,
                ).encode('utf-8'))

def generate_files_cross(osdir, epics_arch, target_arch, generic_epics_arch, generic_target_arch,
                         config_files):
    """Generate epics_arch with includes of generic_epics_arch"""
    for config in config_files:
        tmpl_filename = config.format('linuxos', 'linuxos')
        tmpl_in = pkg_resources.resource_string(
            __name__,
            'resources/{}'.format(tmpl_filename)
        ).decode('utf-8')

        config_filename = os.path.join(osdir, config.format(epics_arch, target_arch))
        with open(config_filename, 'wb') as outfile:
            outfile.write(Template(tmpl_in).substitute(
                linuxos=epics_arch,
                targetos=target_arch,
                genericlinux=generic_epics_arch,
                generictarget=generic_target_arch,
                ).encode('utf-8'))

if __name__ == '__main__':
    sys.exit(main())
