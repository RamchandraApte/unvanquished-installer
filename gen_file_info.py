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

from urllib.request import urlopen, Request
import csv
import io
#download_dir_url = "http://internode.dl.sourceforge.net/project/unvanquished/Assets/"
download_dir_url = "http://127.0.0.1:8080/installer/"
# See http://stackoverflow.com/questions/107405/how-do-you-send-a-head-http-request-in-python
class HeadRequest(Request):
    def get_method(self):
        return "HEAD"

with urlopen(download_dir_url + "md5sums0.10") as f:
    md5sums = f.read()
md5sums_csv = csv.reader(
    io.StringIO(md5sums.decode()), dialect="excel-tab")
 #= tuple(row[0] for row in md5sums_csv)

with open("file_names.csv") as input_file, open("file_info.csv", "w") as output_file:
    file_names_csv = csv.reader(input_file, dialect="excel-tab")
    output_csv = csv.writer(output_file, dialect="excel-tab")
    for (filename, name), (*_, md5sum) in zip(file_names_csv, md5sums_csv):
        print(filename)
        with urlopen(HeadRequest(download_dir_url+filename)) as f:
            content_length = int(f.headers["Content-Length"])
            output_csv.writerow((filename, name, content_length, md5sum))
