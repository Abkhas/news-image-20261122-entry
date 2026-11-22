#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261122, v1 (morning edition).

Copies the pre-drawn entry.png (1024x1024, Sunday 22 November 2026 world
news, rendered in this session by draw_n22.py) into the grader's output
directory. Standard library only, no network, no randomness: both runs
write the same bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    target = os.path.join(out_dir, "entry.png")
    size = os.path.getsize(SOURCE)
    if size < 1 or size > MAX_BYTES:
        raise SystemExit("entry.png is %d bytes, outside 1..%d"
                         % (size, MAX_BYTES))
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(SOURCE, target)
    print("wrote %s (%d bytes)" % (target, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
