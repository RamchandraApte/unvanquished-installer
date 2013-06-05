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

import io
import tarfile
import os
raw_tar = io.BytesIO()

with  tarfile.TarFile(mode = "w", fileobj=raw_tar) as tarfp:
    tarfp.add("dist", arcname = os.curdir)
raw_tar.seek(0)
with open("tar_data.py", "w") as outfp:
    outfp.write("# -*- coding: latin-1 -*-\ndata = {}\n".format(str(raw_tar.read())))