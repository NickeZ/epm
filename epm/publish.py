"""Publish"""
import tempfile
import subprocess
import os
import hashlib

from .util import pretty_print

def publish(path):
    """Publish"""
    name = os.path.basename(path)
    pretty_print('Packing', name)
    tmpdir = tempfile.mkdtemp()
    archivename = os.path.join(tmpdir, 'project.tar.gz')
    subprocess.call(
        'LC_ALL=C tar \
        --create \
        --exclude=target \
        --exclude=".[^/]*" \
        --exclude-backups \
        --exclude-vcs \
        --sort=name \
        --owner=root \
        --group=root \
        --numeric-owner \
        * | gzip --no-name > {}'.format(archivename),
        shell=True,
    )
    print('Will upload the following files:')
    subprocess.call('tar --list --file {}'.format(archivename), shell=True)
    # Calculate hash like git does it
    with open(archivename, 'rb') as archive:
        #filesize = os.path.getsize(archivename)
        #chksum = hashlib.sha1(b'blob {}' + str(filesize).encode('utf-8') + b'\0' + archive.read())
        chksum = hashlib.sha1(archive.read())
    print('Checksum: {}'.format(chksum.hexdigest()))
