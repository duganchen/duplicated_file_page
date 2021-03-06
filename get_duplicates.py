#!/usr/bin/env python


import collections
import flask
import itertools
import os
import yaml
import zlib

app = flask.Flask(__name__)


@app.route('/')
def same_files():

    settings = None

    with open(os.path.join(os.path.dirname(__file__), 'settings.yaml')) as f:
        settings = yaml.load(f)

    assert settings is not None
    assert 'path' in settings
    assert os.path.isdir(settings['path'])

    file_keys = iter_keys(settings['path'], key=os.path.getsize)
    get_key = lambda filekey: filekey.key
    file_keys = sorted(file_keys, key=get_key, reverse=True)
    key_groups = itertools.groupby(file_keys, key=get_key)
    dupes = iter_dupes(key_groups)

    if flask.request.args.get('checksum') is None:
        return flask.render_template('same_sizes.html', keys='sizes',
                                     root=settings['path'], dupes=dupes)

    # If checksums are desired, flatten what we have into a list of paths,
    # checksum them, group them by checksum, and remove duplicates.
    checksummed = sorted(iter_checksums(dupes), key=lambda x: x.key)
    checksum_groups = itertools.groupby(checksummed, key=lambda x: x.key)
    dupes = iter_dupes(checksum_groups)

    return flask.render_template('same_checksums.html', keys='checksums',
                                 root=settings['path'], dupes=dupes)


def iter_keys(path, key):
    for root, _, files in os.walk(path):
        for filepath in files:
            path = os.path.join(root, filepath)
            yield FileKey(key=key(path),
                          path=path.decode('utf-8'))


def iter_dupes(key_groups):

    for key, key_group in key_groups:
        filekeys = tuple(key_group)
        if len(filekeys) > 1:
            yield KeyGroup(key, filekeys)


def iter_checksums(dupe_groups):
    for group in dupe_groups:
        for filekey in group.filekeys:
            yield FileKey(key=checksum(filekey.path), path=filekey.path)


def checksum(path):
    with open(path, 'rb') as f:
        # You're expected to clear out the obvious large files before turning
        # checksumming on.
        return zlib.adler32(f.read())


FileKey = collections.namedtuple('FileKey', ('key', 'path'))
KeyGroup = collections.namedtuple('KeyGroup', ('key', 'filekeys'))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
