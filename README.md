# The World in One Page — Thursday 26 November 2026

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/akbare12/news-26-b73-numbers/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/akbare12/news-26-b73-numbers/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image summing up the world news of Thursday 26 November 2026 — **50 stories**:
3 heroes, 10 cards, 37 ALSO items.

## The day in brief

- **Macy's 100th Thanksgiving Parade postponed** — first weather delay ever,
  as a storm brings 60 mph gusts to New York; rescheduled to Saturday 28 Nov.
- **IRGC claims 2 tankers hit by mines** in the Strait of Hormuz near Khasab,
  one a supertanker carrying 2M barrels; Brent $93.8.
- **Tariff shock fades as markets rebound** — STOXX +1.6% as the 14-partner
  salvo looks milder than feared; China 20%.

Tags: `[C]` CONFIRMED · `[R]` REPORTED · `[CL]` CLAIM / 25 NOV EVENT.
`[CL]` items are 25 Nov events, labelled as such; the DATE CHECK band says so
explicitly and lists the stories left out (COP31 no-deal, Dow above 50,000,
Huawei verdict — all older dates).

## Layout V71

Masthead → DATE CHECK (2 lines) → left 45%: three hero bands stacked, map
strip with 12 pins below → right 55%: cards 2×5 above, ALSO in 3 columns
below → timeline strip → footer with tag legend and sources.

## Files

- `gen.py` — renders `entry.png` (1024×1024) with Pillow at build time.
  Asserts check the 3+10+37 count, duplicate scan, banned phrases,
  tag rules, pin/label geometry and a red-pixel scan of map labels.
- `main.py` — stdlib only: copies the committed `entry.png` into
  `MAKEFUN_OUTPUT_DIR`. Never runs `gen.py`.
- `entry.png` — the rendered front page.

## Verification

- `entry.png`: 220763 bytes
- sha256: `35eec9acd4ba4b9536500d25301edf94f12a9bfce1c88d80ff7448bcb589d9c2`
- Size: 1024×1024
- Story count: 3 heroes + 10 cards + 37 ALSO = 50
- Stdlib-venv simulation: `main.py` runs with no Pillow installed, from a
  different cwd, against a read-only repo copy, and reproduces `entry.png`
  byte-for-byte (sha256 match, exit 0).

Reproduce locally:

```sh
python3 gen.py          # renders entry.png, runs all asserts
python3 -m venv /tmp/sim-venv && /tmp/sim-venv/bin/python main.py
# sim: MAKEFUN_OUTPUT_DIR=<empty dir> from another cwd, repo copy read-only
```
