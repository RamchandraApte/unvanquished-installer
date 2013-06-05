# Unvanquished Installer, an installer for Unvanquished (http://unvanquished.org).
# Copyright (C) 2012-2013  Ramchandra Apte
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# EXCLUDES=-X _frozen_importlib -X __main__ -X _bisect -X _bz2 -X _codecs -X _collections -X _csv -X _datetime -X _frozen_importlib -X _functools -X _hashlib -X _heapq -X _imp -X _io -X _locale -X _posixsubprocess -X _random -X _socket -X _sre -X _ssl -X _string -X _struct -X _sysconfigdata -X _thread -X _warnings -X _weakref -X _weakrefset -X abc -X argparse -X array -X atexit -X base64 -X binascii -X bisect -X builtins -X bz2 -X calendar -X codecs -X collections -X collections.abc -X contextlib -X copy -X copyreg -X csv -X datetime -X email -X email._encoded_words -X email._parseaddr -X email._policybase -X email.base64mime -X email.charset -X email.encoders -X email.errors -X email.feedparser -X email.header -X email.iterators -X email.message -X email.parser -X email.quoprimime -X email.utils -X encodings -X encodings.aliases -X encodings.idna -X encodings.latin_1 -X encodings.utf_8 -X errno -X fcntl -X fnmatch -X functools -X gc -X genericpath -X gettext -X glob -X grp -X hashlib -X heapq -X http -X http.client -X installer -X io -X itertools -X keyword -X linecache -X locale -X marshal -X math -X operator -X os -X os.path -X posix -X posixpath -X pwd -X quopri -X random -X re -X readline -X reprlib -X select -X shutil -X signal -X sip -X site -X socket -X sre_compile -X sre_constants -X sre_parse -X ssl -X stat -X string -X stringprep -X struct -X subprocess -X sys -X sysconfig -X tar_data -X tar_dec -X tarfile -X tempfile -X textwrap -X threading -X time -X token -X tokenize -X traceback -X types -X ui_installer -X unicodedata -X urllib -X urllib.error -X urllib.parse -X urllib.request -X urllib.response -X uu -X warnings -X weakref -X zipimport
# TODO: make compilation optimized
# TODO: add license
# TODO: upgrade system and use newer packages
all: run  Makefile
tar_data.py: gen_tar_data.py dist
	python3.3 gen_tar_data.py
tar_dec_dist: tar_data.py tar_dec.py installer.py
	/usr/local/bin/python3.3 ~/py/Tools/freeze/freeze.py $(EXCLUDES) -X PyQt4 -o tar_dec_dist tar_dec.py -m installer -m encodings.idna -m encodings.ascii

compile: tar_dec_dist
	$(MAKE) -C tar_dec_dist
xz_dec: compile
	$(MAKE) -C xz_dec
	cp xz_dec/xzminidec installer
run: xz_dec
	./installer

.PHONY: clean
clean:
	rm -rf tar_dec_dist/
	$(MAKE) -C xz_dec clean