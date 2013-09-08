unvanquished-installer
======================
This is my installer for [Unvanquished] [1]

Warning: This README is not done yet.

Pre-requisite building:
[Download] [2] the latest version of Python and extract the archive.

To build Python:

    ./configure CPPFLAGS=-static -libgcc-static # Make the Python build static
    make -j2 # Replace 2 with the number of cores
    sudo make altinstall # Install Python, without overwriting system Python

Some additional patches are required, run

    patch -i python.patch
    wget http://bugs.python.org/file28537/issue16047-1.patch
    patch -i issue16047.patch # (Available from http://bugs.python.org/file28537/issue16047-1.patch) 

Build instructions for installer: Set `PY_SRC_DIR` in the Makefile for the installer to the directory containing the source of Python. Insert shared libraries which are needed by the installer into ./dist/ and then run `make`
The executable is at ./installer.

[1]: http://unvanquished.org       "Unvanquished"
[2]: http://python.org/download/releases/ "Download"
