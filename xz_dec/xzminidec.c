/*
 *
 * Uvanquished Installer, an installer for Unvanquished (http://unvanquished.org).
 * Copyright (C) 2012-2013  Ramchandra Apte
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * Decodes the xz-compressed tar_dec binary and runs it.
 *
 * Author: Ramchandra Apte <maniandram01>, Lasse Collin <lasse.collin@tukaani.org>
 * This program is based on the xzminidec example program provided
 * in XZ Embedded, which is a simple XZ decoder command line tool
 * by Lasse Collin <lasse.collin@tukaani.org> in the public domain.
 */

#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdlib.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include "xz.h"
#include "data.h"
static uint8_t out[BUFSIZ];

int main(int argc, char **argv, char *envp[])
{
	struct xz_buf b;
	struct xz_dec *s;
	enum xz_ret ret;
	const char *msg;

	if (argc >= 2 && strcmp(argv[1], "--help") == 0) {
		fputs("Uncompress a .xz file from stdin to stdout.\n"
				"Arguments other than `--help' are ignored.\n",
				stdout);
		return 0;
	}

	xz_crc32_init();

	/*
	 * Support up to 64 MiB dictionary. The actually needed memory
	 * is allocated once the headers have been parsed.
	 */
	s = xz_dec_init(XZ_DYNALLOC, 1 << 26);
	if (s == NULL) {
		msg = "Memory allocation failed\n";
		goto error;
	}

	b.in = in;
	b.in_pos = 0;
	b.in_size = BUFSIZ;
	b.out = out;
	b.out_pos = 0;
	b.out_size = BUFSIZ;
//     TODO add error checking
        char temp_dir_name[] = "/tmp/unv_installer_XXXXXX"; /* TODO: find tmpdir, don't assume it is /tmp */
        mkdtemp(temp_dir_name);
        char temp_file_name[256];
        sprintf(temp_file_name, "%s/installer", temp_dir_name);
        FILE* temp_fp = fopen(temp_file_name, "w");
        while (true) {
		ret = xz_dec_run(s, &b);
		/*So that xz_dec_run will consume another BUFSIZ bytes (it reads from b.in_pos till b.in_size)*/
                if (fwrite(b.out, 1, b.out_pos, temp_fp) != b.out_pos) {
                        msg = "Write error\n";
                        goto error;
                    }

		if (ret == XZ_OK){
                    b.in_size+=BUFSIZ;
                    b.out_pos=0;
                    continue;
                }

#ifdef XZ_DEC_ANY_CHECK
		if (ret == XZ_UNSUPPORTED_CHECK) {
			fputs(argv[0], stderr);
			fputs(": ", stderr);
			fputs("Unsupported check; not verifying "
					"file integrity\n", stderr);
			continue;
		}
#endif

		switch (ret) {
		case XZ_STREAM_END:
			xz_dec_end(s);
                        chmod(temp_file_name, S_IRUSR|S_IWUSR|S_IXUSR|S_IRGRP|S_IXGRP|S_IROTH|S_IXOTH);
                        fclose(temp_fp);
                        printf("%s\n", temp_file_name);
                        int i = 0;
                        while (envp[i] != NULL){
                            i++;
                        }
                        char **env = malloc((i+1)*sizeof(char *));
                        memcpy(env, envp, i*sizeof(char *));
                        char var[256];
                        sprintf(var, "LD_LIBRARY_PATH=%s", temp_dir_name);
                        env[i] = var;
                        env[i+1] = (char*) NULL;
//                         {"LD_LIBRARY_PATH=", (char *) NULL};
                        execle(temp_file_name, temp_file_name, (char*) NULL, env);
                        printf("Weird\n");
                        return 1;  /*Will only occur if execl call failed.*/

		case XZ_MEM_ERROR:
			msg = "Memory allocation failed\n";
			goto error;

		case XZ_MEMLIMIT_ERROR:
			msg = "Memory usage limit reached\n";
			goto error;

		case XZ_FORMAT_ERROR:
			msg = "Not a .xz file\n";
			goto error;

		case XZ_OPTIONS_ERROR:
			msg = "Unsupported options in the .xz headers\n";
			goto error;

		case XZ_DATA_ERROR:
		case XZ_BUF_ERROR:
			msg = "File is corrupt\n";
			goto error;

		default:
			msg = "Bug!\n";
			goto error;
		}
	}


error:
	xz_dec_end(s);
	fputs(argv[0], stderr);
	fputs(": ", stderr);
	fputs(msg, stderr);
	return 1;
}
