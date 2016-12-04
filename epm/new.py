"""Define new and init functions"""
import os
import subprocess
import re
import shlex
import getpass

from string import Template
import pkg_resources

from .util import git_version, find_manifest_file, pretty_print
from .constants import MANIFEST_FILE

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

    # Generate manifest file
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

    # Generate a small hello world library / ioc
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

def init(path, ioc):
    """Create a new project in current working dir"""
    init_priv(path, ioc)
    pretty_print('Created', 'EPICS project')

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
