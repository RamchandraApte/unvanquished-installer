unvanquished-installer
======================
 Warning: This README is being created, not done yet.
Pre-requisite building:
Download the latest version of Python from http://python.org/download/releases/ (currently: http://python.org/ftp/python/3.3.2/Python-3.3.2.tar.xz)
To build Python:
    ./configure CPPFLAGS=-static -libgcc-static #Make the Python build static
    make -j2 #Replace 2 with the number of cores
    sudo make altinstall #Install Python, without overwriting system Python

Build instructions: insert shared libraries which are needed by the installer into ./dist/ and then run `make`
The executable is at ./installer.
