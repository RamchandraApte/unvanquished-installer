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

PYUIC = pyuic4
PY_SRC_DIR= ~/Downloads/Python-3*
PYTHON = $(PY_SRC_DIR)/python
LN = ln
RM = rm
# TODO: make compilation optimized
# TODO: upgrade system and use newer packages

all: run  Makefile
ui_installer.py: installer.ui
	$(PYUIC) installer.ui -o ui_installer.py
installer.py: ui_installer.py
tar_data.py: gen_tar_data.py installer.py dist
	$(RM) -f dist/installer.py
	$(LN) installer.py dist/installer.py
	$(PYTHON) gen_tar_data.py
tar_dec_dist: tar_data.py tar_dec.py installer.py
	$(PYTHON) $(PY_SRC_DIR)/Tools/freeze/freeze.py -X PyQt4 -o tar_dec_dist tar_dec.py -m installer -m encodings.idna -m encodings.ascii -m encodings.utf_8

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
