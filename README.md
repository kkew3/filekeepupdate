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

- If the file has never been downloaded from URL, download it and record the
  hash.
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
  the latest download in cache area and prompt the user to update manually
  (strictly speaking there's no _prompt_, but a warning return code
  `LOCAL_CHANGE_REMOTE_CHANGE`, as specified in `fkupdate.__doc__`)


## Motivation

To manage lecture slides, tutorials, extra exercises, etc. downloaded from
course website, in which case the lecturer might update the material on course
website, and meanwhile I'd like to annotate locally on the downloaded PDFs.


## Dependencies

- at least `python-3.5.2`

There should be no assumption on the underlying operating system (Windows 10,
FreeBSD, Ubuntu, etc.). There should be no extra package dependencies.


## Notice

Although there's certainly some basic tests, the code has not been tested
_thoroughly_ and probably won't ever be.



# fmgr

This is a quite simple client software based on `fkupdate` currently being
used by me. I put it up here in case anyone else has similar requirements.


## Introduction

> Copied from `fmgr.__doc__`

A simple command line interface.

If a directory contains `.name_url.json`, running this script under that
directory will do batch maintenance according to the filenames and URLs on
the JSON file. `updatehist_file`, `cachedir` will be created automatically.
The hash algorithm will be `algorithm`.

## Demo

	$ # prepare a .name_url.json for demo
	$ echo '[["fft.pdf", "http://www.cs.cmu.edu/afs/andrew/scs/cs/15-463/2001/pub/www/notes/fourier/fourier.pdf"]]' > .name_url.json
	$ # or to make `fmgr.py` an executable and call it directly ...
	$ python3 fmgr.py
	$ ls
	fft.pdf
	$ ls -A
	.cache  .downloads.json  fft.pdf  .name_url.json
	$ ls -A .cache
	$ cat .downloads.json
	{"fft.pdf": "64fe6ff40fc4935b20a5f89195822a25868420404e0dc3692353166640d6b9af"}

Now see how `fmgr.py` responses.

Simulated situation 1:

	$ # setup simulation
	$ sed -i'.bak' 's/http/ttp/' .name_url.json
	$ # response
	$ python3 fmgr.py
	fft.pdf: Not remotely available but found local copy; is the Internet connected? or is the URL changed?
	$ # teardown simulation
	$ mv .name_url.json{.bak,}

Simulated situation 2:

	$ # setup simulation -- no setup, just run `fmgr.py` again
	$ python3 fmgr.py
	$ # no output; everything is going well

Simulated situation 3:

	$ # setup simulation -- updated remotely
	$ sed -i'.bak' 's|http://www.cs.cmu.edu/afs/andrew/scs/cs/15-463/2001/pub/www/note    s/fourier/fourier.pdf|http://www.wisdom.weizmann.ac.il/~naor/COURSE/fft-lecture.pdf|' .name_url.json
	$ python3 fmgr.py
	$ # no output; update the file silently
	$ # teardown simulation
	$ mv .name_url.json{.bak,}

Simulated situation 4:

	$ # setup simulation -- updated remotely and modified locally
	$ sed -i'.bak' 's|http://www.cs.cmu.edu/afs/andrew/scs/cs/15-463/2001/pub/www/note    s/fourier/fourier.pdf|http://www.wisdom.weizmann.ac.il/~naor/COURSE/fft-lecture.pdf|' .name_url.json
	$ dd if=/dev/zero bs=1 count=1 >> fft.pdf
	1+0 records in
	1+0 records out
	1 byte copied, 7.5353e-05 s, 13.3 kB/s
	$ python3 fmgr.py
	fft.pdf: Update available under .cache but local copy has already been modified
	$ ls .cache
	fft.pdf
