# fkupdate

## Abstract

This repository provides simple utility to keep local file update with URL.


## Use case

> Copied from `fkupdate.__doc__`

This module tries to tackle the use case where there is a potentially
changing remote repository of files, and the user downloads the file to local
host with potentially local changes. However, the user hopes to get warning
about file updates at the repository end so that he/she could update to the
latest edition and adapt his/her change to the new file.

Besides two utility functions `hash_of_file` and `download`, this module
provides `attempt_update` for virtual management (i.e. no actual file system
operation) and `update` for actual file system operation. Moreover, there's
a wrapper function that maintain a directory of files in batch.


## Usage

There's no standalone software. The user is expected to add whatever command
line interface over the module `fkupdate`. In the near future, if I have time,
I will make it available on `pip`.


## Mechanism

- If the file has never downloaded from URL, download it.
- If the file has been downloaded before (with hash recorded), and if the
  latest downloaded file has the same hash as the recorded one, remove the
  latest download.
- If the file has been downloaded before (with hash recorded), and if the
  latest downloaded file has different hash with the recorded one, and if the
  hash of current local file is the same as the recorded hash, update current
  local copy.
- If the file has been downloaded before (with hash recorded), and if the
  latest downloaded file has different hash with the recorded one, and if the
  hash of current local file is different from the recorded hash, then save
  the latest download in cache area and prompt the user to update manually.


## Motivation

To manage lecture slides, tutorials, extra exercises, etc. downloaded from
course website, in which case the lecturer might update the material on course
website, and meanwhile I'd like to annotate locally on the downloaded PDFs.


## Dependencies

- at least `python-3.5.2`

There should be no assumption on the underlying operating system (Windows 10,
FreeBSD, Ubuntu, etc.). There should be no extra package dependencies.


## Notice

The code has not been tested thoroughly and probably won't ever be.
