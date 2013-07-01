#!/usr/bin/env python


import collections
import flask
import itertools
import os
import yaml

app = flask.Flask(__name__)


@app.route('/')
def dupes():

    settings = None

    with open('settings.yaml') as f:
        settings = yaml.load(f)

    assert settings is not None
    assert 'path' in settings
    assert os.path.isdir(settings['path'])

    file_sizes = iter_sizes(settings['path'])
    get_size = lambda filesize: filesize.size
    file_sizes = sorted(file_sizes, key=get_size, reverse=True)
    size_groups = itertools.groupby(file_sizes, key=get_size)
    dupes = iter_dupes(size_groups)
    return flask.render_template('same_sizes.html', root=settings['path'],
                                 dupes=dupes)


def iter_sizes(path):
    for root, _, files in os.walk(path):
        for filepath in files:
            path = os.path.join(root, filepath)
            yield FileSize(size=os.path.getsize(path),
                           path=path.decode('utf-8'))


def iter_dupes(size_groups):

    for size, path_group in size_groups:
        filesizes = tuple(path_group)
        if len(filesizes) > 1:
            yield SizeGroup(size, filesizes)


FileSize = collections.namedtuple('FileSize', ('size', 'path'))

SizeGroup = collections.namedtuple('SizeGroup', ('size', 'filesizes'))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
