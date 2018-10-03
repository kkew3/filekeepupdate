#!/usr/bin/env python
"""
A simple command line interface.

If a directory contains ``.name_url.json``, running this script under that
directory will do batch maintenance according to the filenames and URLs on
the JSON file. ``updatehist_file``, ``cachedir`` will be created automatically.
The hash algorithm will be ``algorithm``.
"""

import logging
logging.basicConfig(level=logging.WARNING, format='%(message)s')

import json
import os
import sys

import fkupdate


nameurl_file = '.name_url.json'
updatehist_file = '.downloads.json'
cachedir = '.cache'
algorithm = 'sha256'

ret2lvl_msg = {
    fkupdate.UPDATED: (
        logging.INFO,
        '{}: Updated'),
    fkupdate.NO_REMOTE_CHANGE: (
        logging.INFO,
        '{}: No update'),
    fkupdate.LOCAL_CHANGE_REMOTE_CHANGE: (
        logging.WARNING,
        '{}: Update available under ' + cachedir + ' but local copy has '
        'already been modified'),
    fkupdate.NO_LOCAL_NO_REMOTE: (
        logging.INFO,
        '{}: Not available'),
    fkupdate.HAS_LOCAL_NO_REMOTE: (
        logging.WARNING,
        '{}: Not remotely available but found local copy; is the Internet '
        'connected? or is the URL changed?'),
}


if __name__ == '__main__':
    try:
        with open(nameurl_file) as infile:
            name_url = json.load(infile)
    except FileNotFoundError:
        sys.exit(0)

    try:
        with open(updatehist_file) as infile:
            name2hash = json.load(infile)
    except FileNotFoundError:
        name2hash = {f: None for f, _ in name_url}

    os.makedirs(cachedir, exist_ok=True)
    basedir = os.getcwd()

    r, u = fkupdate.maintain_batch(basedir, cachedir, name_url, name2hash,
                                   algorithm)
    name_ret = iter((f, x) for (f, _), x in zip(name_url, r))
    for f, x in name_ret:
        lvl, msg = ret2lvl_msg[x]
        msg = msg.format(f)
        logging.log(lvl, msg)

    name2hash.update(u)
    with open(updatehist_file, 'w') as outfile:
        json.dump(name2hash, outfile)

