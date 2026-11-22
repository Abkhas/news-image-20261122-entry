#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261122, v3c (legibility-first
under the 3-gate doctrine: paid-winner structure + 300px eye-check
first, duel as confirmation only).

The v3c image is drawn by draw_n22v3c.py in this same session and saved
next to this file as entry.png (1024x1024, Sunday 22 November 2026 world
news: 24 stories -- 3 heroes + 9 grid cards + 12 ALSO ON lines -- with a
verification-status chip on every card and every line, a 92px masthead
date, a DATE CHECK labelled READ THIS FIRST on the left of the bottom
band, a sources footer, and a world map with separated numbered pins).
This program's only job is to place that exact file at the grader's
output path.

Standard library only. No network, no randomness, no writes other than
the single copy: both grader runs produce identical bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGE = os.path.join(HERE, "entry.png")
LIMIT = 1048576


def run():
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    if not os.path.isfile(IMAGE):
        raise SystemExit("missing %s" % IMAGE)
    nbytes = os.path.getsize(IMAGE)
    if nbytes > LIMIT:
        raise SystemExit("entry.png is %d bytes, over the %d limit"
                         % (nbytes, LIMIT))
    os.makedirs(target_dir, exist_ok=True)
    dest = os.path.join(target_dir, "entry.png")
    shutil.copyfile(IMAGE, dest)
    print("wrote %s (%d bytes)" % (dest, nbytes))
    return 0


if __name__ == "__main__":
    sys.exit(run())
