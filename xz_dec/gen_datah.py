
import lzma
import sys
#TODO:use high-quality compression
escape_table = {c: c.decode() if c[0]<128 and chr(c[0]).isprintable() else "\\"+oct(ord(c))[2:].rjust(3, "0")  for c in (c.to_bytes(1, "big") for c in range(256))}
escape_table.update({b"\\":r"\\", b'"': r'\"', b"?": r"\?"})
escape_table = tuple(escape_table[key] for key in sorted(escape_table.keys()))

def escape(str):
    return "".join(escape_table[c] for c in str)

with open(sys.argv[1], "rb") as infp:
    compressed = lzma.compress(infp.read())

with open("data.h", "w") as outfp:
    outfp.write('#include <stdint.h>\nstatic const uint8_t in[]="{}";\n'.format(escape(compressed)))
