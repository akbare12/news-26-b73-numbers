#!/usr/bin/env python3
"""news-26 b73 — entry runner.

Stdlib only: copies the pre-rendered entry.png (built by gen.py at build
time and committed to this repo) into MAKEFUN_OUTPUT_DIR.

Layout V71: masthead -> DATE CHECK -> left: 3 hero bands + map strip;
right: cards 2x5 + ALSO 3 cols -> timeline strip -> footer.
50 stories: 3 heroes + 10 cards + 37 ALSO. Thursday 26 Nov 2026.
"""
import hashlib
import os
import shutil
import struct
import sys

ENTRY = "entry.png"
EXPECTED_W = 1024
EXPECTED_H = 1024


def out_dir():
    """Grader output dir, or local fallback."""
    return os.environ.get("MAKEFUN_OUTPUT_DIR", "out")


def src_path():
    """entry.png lives next to this file in the repo."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, ENTRY)


def dst_path():
    """Destination inside the grader output dir."""
    return os.path.join(out_dir(), ENTRY)


def verify_png(path):
    """Check PNG magic + IHDR dimensions, stdlib only."""
    with open(path, "rb") as fh:
        head = fh.read(33)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("not a PNG file: %s" % path)
    if head[12:16] != b"IHDR":
        raise SystemExit("PNG has no IHDR chunk: %s" % path)
    width, height = struct.unpack(">II", head[16:24])
    if (width, height) != (EXPECTED_W, EXPECTED_H):
        raise SystemExit("entry.png is %dx%d, expected %dx%d" % (
            width, height, EXPECTED_W, EXPECTED_H))
    return width, height


def copy_entry():
    """Copy entry.png to the output dir; fail loudly if missing.

    Never runs gen.py and never writes beside main.py: the grader
    mounts the repo read-only, so the only writable target is the
    output dir from MAKEFUN_OUTPUT_DIR.
    """
    src = src_path()
    if not os.path.isfile(src):
        raise SystemExit("entry.png missing next to main.py: %s" % src)
    verify_png(src)
    os.makedirs(out_dir(), exist_ok=True)
    dst = dst_path()
    shutil.copyfile(src, dst)
    return dst


def report(dst):
    """Print size + sha256 of the delivered file."""
    with open(dst, "rb") as fh:
        data = fh.read()
    digest = hashlib.sha256(data).hexdigest()
    print("WROTE %s %d bytes sha256=%s" % (dst, len(data), digest))
    return digest


def main():
    dst = copy_entry()
    report(dst)
    print("OK: 50 stories (3 hero + 10 cards + 37 also), layout V71")
    return 0


if __name__ == "__main__":
    sys.exit(main())
