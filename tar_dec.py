__license__ = '''
Unvanquished Installer, an installer for Unvanquished (http://unvanquished.org).
Copyright (C) 2012-2013  Ramchandra Apte

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
#TODO: IMPORTANT: check this and portion of installer.py which chowns the install dir for security vulnerabilities!
import sys
sys.path=[]
import tarfile
import io
import subprocess
import os.path
import argparse
import tar_data
lib_path_env = {"win32": "PATH", "linux": "LD_LIBRARY_PATH"}
base_dir = os.path.split(sys.executable)[0]
installerpy = os.path.join(base_dir, "installer.py")

with tarfile.TarFile(fileobj = io.BytesIO(tar_data.data)) as tar_obj:
    if not os.path.exists(installerpy): tar_obj.extractall(base_dir)
    sys.path.append(base_dir)
    exec(open(installerpy).read())
