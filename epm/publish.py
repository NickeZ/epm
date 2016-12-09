"""Publish"""
import tempfile
import subprocess
import os
import shutil
import siphash
import requests

from .util import pretty_print, pretty_eprint, load_project_config
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
    response = requests.put('{}/api/v1/packages/new'.format(EPM_SERVER), files=files)
    print('Filename: {}'.format(archivename))
    print('Checksum: {}'.format(chksum))
    if response.status_code == 200:
        r = response.json()
        if 'data' in r and 'chksum' in r['data'] and r['data']['chksum'].encode('utf-8') == chksum:
            pretty_print('Uploaded', 'Finished uploading {}'.format(name))
            shutil.rmtree(tmpdir)
            return

    pretty_eprint('Error', 'Failed to upload')
