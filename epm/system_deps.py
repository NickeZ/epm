"""System dependencies"""
import os
import subprocess

from .util import pretty_eprint

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
        'xsubpp': 'perl-ExtUtils-ParseXS',
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

def check_system_prerequisites(hostarch):
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
    else:
        pretty_eprint('Warning', 'Unknown platform, could not check dependencies')
