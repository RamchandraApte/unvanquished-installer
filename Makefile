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

# TODO: make compilation optimized
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