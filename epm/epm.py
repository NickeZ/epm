"""EPM"""
from __future__ import print_function

import argparse
def main(args):
    """Main function"""

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands', dest='command')
    parser_new = subparsers.add_parser('new', help='Create a new project')
    parser_build = subparsers.add_parser('build', help='Compile project')
    parser_clean = subparsers.add_parser('clean', help='Delete compiled files')

    parser_new.add_argument('project-name')

    args = parser.parse_args(args)

    if args.command == 'new':
        print('new')
    elif args.command == 'build':
        print('build')
    elif args.command == 'clean':
        print('clean')

    return 0
