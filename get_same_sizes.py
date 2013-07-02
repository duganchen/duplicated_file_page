#!/usr/bin/env python


import collections
import flask
import itertools
import os
import yaml

app = flask.Flask(__name__)


@app.route('/sizes')
def same_sizes():
    return get_duplicates(template='same_sizes.html', key=os.path.getsize)


def get_duplicates(template, key):
    settings = None

    with open(os.path.join(os.path.dirname(__file__), 'settings.yaml')) as f:
        settings = yaml.load(f)

    assert settings is not None
    assert 'path' in settings
    assert os.path.isdir(settings['path'])

    file_keys = iter_keys(settings['path'], key=key)
    get_key = lambda filekey: filekey.key
    file_keys = sorted(file_keys, key=get_key, reverse=True)
    key_groups = itertools.groupby(file_keys, key=get_key)
    dupes = iter_dupes(key_groups)
    return flask.render_template(template, root=settings['path'],
                                 dupes=dupes)


def iter_keys(path, key):
    for root, _, files in os.walk(path):
        for filepath in files:
            path = os.path.join(root, filepath)
            yield FileKey(key=key(path),
                          path=path.decode('utf-8'))


def iter_dupes(key_groups):

    for key, path_group in key_groups:
        filekeys = tuple(path_group)
        if len(filekeys) > 1:
            yield KeyGroup(key, filekeys)


FileKey = collections.namedtuple('FileKey', ('key', 'path'))
KeyGroup = collections.namedtuple('KeyGroup', ('key', 'filekeys'))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
