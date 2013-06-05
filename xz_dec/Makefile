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
#
# Author: Ramchandra Apte <maniandram01>, Lasse Collin <lasse.collin@tukaani.org>
# This program is based on the Makefile provided
# in XZ Embedded, which is a simple XZ decoder command line tool
# by Lasse Collin <lasse.collin@tukaani.org> in the public domain.

RM = rm -f
XZ_SRC=/home/ramchandra/Downloads/xz-embedded-20120222
VPATH=$(XZ_SRC)/linux/include/linux $(XZ_SRC)/linux/lib/xz $(XZ_SRC)/userspace
XZ_DEC=xzminidec
COMMON_OBJS = $(XZ_DEC).o xz_crc32.o xz_dec_stream.o xz_dec_lzma2.o xz_dec_bcj.o
CPPFLAGS = -g -I$(XZ_SRC)/linux/include/linux -I$(XZ_SRC)/userspace -DXZ_DEC_X86 -DXZ_DEC_ANY_CHECK -Wall -Wextra -O0
CC=cc

all: $(XZ_DEC)
data.h: gen_datah.py ../tar_dec_dist/tar_dec
	python3.3 gen_datah.py ../tar_dec_dist/tar_dec
.PHONY: clean
.depend: $(COMMON_OBJS:.o=.c)
	$(CC) $(CPPFLAGS) -MM $^>./.depend
-include .depend
$(XZ_DEC): $(COMMON_OBJS)

clean:
	-$(RM) $(COMMON_OBJS) $(XZ_DEC).o .depend
