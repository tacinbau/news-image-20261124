[![news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/tacinbau/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/tacinbau/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124)

# The World in One Image — 24 November 2026

A program that draws one front-page-style image summing up the world
news of Tuesday 24 November 2026, and writes it to
`$MAKEFUN_OUTPUT_DIR/entry.png`.

## How it works

`main.py` is pure Python 3 standard library (no network, no third-party
packages). It draws a 1024x1024 PNG with a hand-written 5x7 bitmap font
and a hand-written PNG encoder (`zlib` + `struct` only), so the image is
produced by the program itself on every run. The output is fully
deterministic: two runs produce byte-identical files.

## The six stories

1. **COP31 collapses** — no climate pact in Antalya; the first UN climate
   summit to fail since 2009.
2. **Huang back at Nvidia** — the board reinstates Jensen Huang as CEO;
   shares jump about 30%.
3. **24 dead in factory fire** — candy plant blaze in Banten, Indonesia;
   about 30 still missing.
4. **War spreads at sea** — a Russian ship hit off Libya; the Kyiv region
   struck in drone attacks.
5. **Chess crown on the line** — Gukesh defends his world title against
   Sindarov; play opens in Geneva.
6. **India–Nepal pact** — Modi and PM Shah sign 8 deals; a Rs 15,000
   crore aid package.

The footer ticker adds: UK sanctions on Myanmar generals, the India–New
Zealand Test drawn in Wellington, and a supermoon meeting the Pleiades
tonight.

## Run it

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## License

MIT — see `LICENSE`.
