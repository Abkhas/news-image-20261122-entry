# news-image-20261122 — v1 (morning edition)

One image summing up Sunday 22 November 2026's world news: 33 stories,
7 regions, drawn in code.

- `main.py` — the entrypoint (stdlib only): copies `entry.png` to
  `$MAKEFUN_OUTPUT_DIR/entry.png`.
- `draw_n22.py` — the renderer (needs Pillow locally only): draws the whole
  front page and writes `entry.png`. Run it twice to check the output is
  byte-identical.
- `entry.png` — the image: 1024x1024, deterministic, under 1 MiB.

Run: `python3 draw_n22.py` then `MAKEFUN_OUTPUT_DIR=out python3 main.py`.
