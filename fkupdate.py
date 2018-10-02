# TODO Unfinished code -- well, almost finished
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

import hashlib
import shutil
import json
from urllib import request
import urllib.error
from typing import Optional, Dict


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
    except urllib.error.HTTPError:
        return None


def attempt_update(localfile: str, orighash: Optional[str],
                   latest_download: Optional[str],
                   algorithm: str) -> Tuple[int, Optional[str]]:
    """
    Attempt to update the local file with the latest downloaded file, by
    comparing the original hash of the local file and that of the latest
    downloaded file. No actual file system operation will be performed.

    :param localfile: the local file path
    :param orighash: the hash of the local file once it's downloaded; or None
           if the file has never been downloaded
    :param latest_download: the latest downloaded file; or None if the file
           cannot be downloaded for some reason
    :param algorithm: the hash algorithm    
    :return: the int return code; and the new hash if the return code is 0, or
             ``None`` if the return code is non-zero
    """
    if (orighash, latest_download) == (None, None):
        return NO_LOCAL_NO_REMOTE, None
    if latest_download is None:
        return HAS_LOCAL_NO_REMOTE, None
    latest_hash = hash_of_file(latest_download, algorithm=algorithm)
    if orig_hash == latest_hash:
        return NO_REMOTE_CHANGE, None
    if orig_hash == hash_of_file(localfile, algorithm=algorithm):
        return UPDATED, latest_hash
    return LOCAL_CHANGE_REMOTE_CHANGE, None


def update(localfile: str, orighash: Optional[str],
           latest_download: Optional[str],
           algorithm: str) -> Union[int, str]:
    """
    Update the local file if necessary in file system. This function will make
    an internal call to ``attempt_update``. When ``attempt_update`` returns a
    string, i.e. the updated hash, ``localfile`` will be replaced by
    ``latest_download`` and ``latest_download`` will be removed.

    The parameters and the return are the same as that in ``attempt_update``.
    """
    ret, update = attempt_update(localfile, orighash, latest_download, algorithm)
    if ret == UPDATED:
        os.replace(latest_download, localfile)
    return ret, update


def maintain_batch(basedir: str, cachedir: str, names: str,
                   name2url: Dict[str, str], name2hash: Dict[str, str],
                   algorithm: str) -> Tuple[Dict[str, str], List[int]]:
    """
    Maintain a batch of files to be downloaded to the same local directory.

    :param basedir: the directory where the files to stay locally
    :param cachedir: the directory where to download the latest edition
    :param names: a list of base filenames to be managed
    :param name2url: a dictionary mapping local base filename to URL
    :param name2hash: a dictionary mapping local base filename to the hash of
           it once it was downloaded
    :param algorithm: the hash algorithm used
    :return: a dictionary which can be used to update ``name2hash``, and a
             list of int return codes for each file (according to ``names``)
    """
    pass
