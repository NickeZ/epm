#!/usr/bin/python3
"""Helper program to generate os specific epics host architectures"""
import argparse
import sys
import platform
from string import Template
import pkg_resources

CONFIG_FILES = [
    'CONFIG.Common.{0}',
    'CONFIG.{0}.Common',
    'CONFIG.{0}.{0}',
    'CONFIG_SITE.Common.{0}',
    'CONFIG_SITE.{0}.Common']

def main():
    """Main function"""
    parser = argparse.ArgumentParser()
    parser.add_argument('os')
    args = parser.parse_args(sys.argv[1:])

    generic_epics_arch = '{}-{}'.format(platform.system().lower(), platform.machine())

    for config in CONFIG_FILES:
        tmpl_filename = config.format('linuxos')
        tmpl_in = pkg_resources.resource_string(
            __name__,
            'resources/{}'.format(tmpl_filename)
        ).decode('utf-8')

        config_filename = config.format(args.os)
        with open(config_filename, 'wb') as outfile:
            outfile.write(Template(tmpl_in).substitute(
                linuxos=args.os,
                genericlinux=generic_epics_arch,
                ).encode('utf-8'))

if __name__ == '__main__':
    sys.exit(main())
