"""
This module tries to tackle the use case where there is a potentially
changing remote repository of files, and the user downloads the file to local
host with potentially local changes. However, the user hopes to get warning
about file updates at the repository end so that he/she could update to the
latest edition and adapt his/her change to the new file.

Besides two utility functions ``hash_of_file`` and ``download``, this module
provides ``attempt_update`` for virtual management (i.e. no actual file system
operation) and ``update`` for actual file system operation.

Instruction on globally used int return codes:

    - NO_REMOTE_CHANGE:           the file is not updated remotely
    - LOCAL_CHANGE_REMOTE_CHANGE: the file is modified both locally and
                                  remotely
    - NO_LOCAL_NO_REMOTE:         the file hasn't been downloaded before and
                                  it's still not remotely available
    - HAS_LOCAL_NO_REMOTE:        the file has been downloaded before but it's
                                  not remotely available for some reason
"""

import os
import hashlib
import shutil
import json
from urllib import request
import urllib.error
import itertools
from typing import Optional, Dict, Tuple, List


# int return code used globally
UPDATED = 0  # (no local, has remote) or (no local change, has remote change)
NO_REMOTE_CHANGE = 1 << 0
LOCAL_CHANGE_REMOTE_CHANGE = 1 << 1
NO_LOCAL_NO_REMOTE = 1 << 2
HAS_LOCAL_NO_REMOTE = 1 << 3


def hash_of_file(filename: str, algorithm: str) -> str:
    hashbuf = hashlib.new(algorithm)
    with open(filename, 'rb') as infile:
        for cbuf in iter(lambda: infile.read(1048576), b''):
            hashbuf.update(cbuf)
    return hashbuf.hexdigest()


def download(filename: str, url: str) -> Optional[str]:
    """
    Download file from ``url`` to ``filename``. Returns ``None`` if
    ``HTTPError`` occurs.
    """
    try:
        with request.urlopen(url) as web:
            with open(filename, 'wb') as outfile:
                shutil.copyfileobj(web, outfile)
        return filename
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None


def attempt_update(localfile: str, orig_hash: Optional[str],
                   latest_download: Optional[str],
                   algorithm: str) -> Tuple[int, Optional[str]]:
    """
    Attempt to update the local file with the latest downloaded file, by
    comparing the original hash of the local file and that of the latest
    downloaded file. No actual file system operation will be performed.

    :param localfile: the local file path
    :param orig_hash: the hash of the local file once it's downloaded; or None
           if the file has never been downloaded
    :param latest_download: the latest downloaded file; or None if the file
           cannot be downloaded for some reason
    :param algorithm: the hash algorithm
    :return: the int return code; and the new hash if the return code is 0, or
             ``None`` if the return code is non-zero
    """
    if (orig_hash, latest_download) == (None, None):
        return NO_LOCAL_NO_REMOTE, None
    if latest_download is None:
        return HAS_LOCAL_NO_REMOTE, None
    latest_hash = hash_of_file(latest_download, algorithm=algorithm)
    if orig_hash is None:
        return UPDATED, latest_hash
    if orig_hash == latest_hash:
        return NO_REMOTE_CHANGE, None
    if orig_hash == hash_of_file(localfile, algorithm=algorithm):
        return UPDATED, latest_hash
    return LOCAL_CHANGE_REMOTE_CHANGE, None


def update(localfile: str, orig_hash: Optional[str],
           latest_download: Optional[str],
           algorithm: str) -> Tuple[int, Optional[str]]:
    """
    Update the local file if necessary in file system. This function will make
    an internal call to ``attempt_update``. When ``attempt_update`` returns a
    return code of ``UPDATED``, ``localfile`` will be replaced by
    ``latest_download`` and ``latest_download`` will be removed. When the
    returns code is ``NO_REMOTE_CHANGE``, the ``latest_download`` will be
    removed.

    The parameters and the return are the same as that in ``attempt_update``.
    """
    ret, dictupdates = attempt_update(localfile, orig_hash, latest_download, algorithm)
    if ret == UPDATED:
        os.replace(latest_download, localfile)
    elif ret == NO_REMOTE_CHANGE:
        os.remove(latest_download)
    return ret, dictupdates


# You may replace `itertools.starmap` in this function with `pool.starmap` for
# concurrency, since clearly this is an IO-bounded task.
def maintain_batch(basedir: str, cachedir: str,
                   name_url: List[Tuple[str, str]], name2hash: Dict[str, str],
                   algorithm: str) -> Tuple[List[int], Dict[str, str]]:
    """
    Maintain a batch of files to be downloaded to the same local directory.
    No argument will be changed in place. All arguments expecting a directory
    assume the existence of directories.

    Example usage::

        .. code-block::

            with open(cfgfile) as infile:
                name2hash = json.load(infile)
            ret, updates = maintain_batch(basedir, cachedir, name_url,
                                          name2hash, algorithm)
            name2hash.update(updates)
            with open(cfgfile, 'w') as outfile:
                json.dump(name2hash, outfile)


    :param basedir: the directory where the files to stay locally
    :param cachedir: the directory where to download the latest edition
    :param names: a list of base filenames to be managed
    :param name_url: a list of tuples of (base filename, URL)
    :param name2hash: a dictionary mapping local base filename to the hash of
           it once it was downloaded
    :param algorithm: the hash algorithm used
    :return: a list of int return codes for each file (according to the order
             of ``name_url``), and a dictionary which can be used to update
             ``name2hash``
    """
    if len(name_url) != len(name2hash):
        raise ValueError('length mismatch: name_url ({}) and name2hash ({})'
                         .format(len(name_url), len(name2hash)))
    # download the latest version to cachedir
    latestfile_url = iter((os.path.join(cachedir, f), u) for f, u in name_url)
    latestfiles = itertools.starmap(download, latestfile_url)
    # order `name2hash` in terms of `name_url` into a list of tuples
    name_hash = iter((f, name2hash[f]) for f, _ in name_url)
    # prepare arguments for `update` function and call it
    localfile_hash = iter((os.path.join(basedir, f), h) for f, h in name_hash)
    args = iter((l, h, d, algorithm) for (l, h), d in zip(localfile_hash, latestfiles))
    vals = list(itertools.starmap(update, args))  # evaluate here
    assert len(vals) == len(name_url)
    # collect return values
    retcodes = list(r for r, _ in vals)
    newhashes = iter(h for _, h in vals)
    name_newhash = iter((f, h) for (f, _), h in zip(name_url, newhashes)
                        if h is not None)
    name2hash_updates = dict(name_newhash)
    return retcodes, name2hash_updates
