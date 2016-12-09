"""Publish"""
import tempfile
import subprocess
import os
import siphash
import requests

from .util import pretty_print, load_project_config
from .constants import SIPHASH_KEY, EPM_SERVER

def publish(path):
    """Publish"""
    config = load_project_config(path)
    name = config['project']['name']
    version = config['project']['version']
    pretty_print('Packing', name)
    tmpdir = tempfile.mkdtemp()
    archivename = os.path.join(tmpdir, '{}-{}.tar.gz'.format(name, version))
    subprocess.call(
        'LC_ALL=C tar \
        --create \
        --exclude=target \
        --exclude-backups \
        --exclude-vcs \
        --sort=name \
        --owner=root \
        --group=root \
        --numeric-owner \
        * | gzip --no-name > {}'.format(archivename),
        shell=True,
    )
    #print('Will upload the following files:')
    #subprocess.call('tar --list --file {}'.format(archivename), shell=True)
    with open(archivename, 'rb') as archive:
        chksum = siphash.SipHash_2_4(SIPHASH_KEY, archive.read()).hexdigest()

    files = {'project': open(archivename, 'rb')}
    requests.put('{}/api/v1/packages/new'.format(EPM_SERVER), files=files)
    print('Filename: {}'.format(archivename))
    print('Checksum: {}'.format(chksum))
