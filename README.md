# makefun-btc-race-24h

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/vikysimboh/makefun-btc-race-24h/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/vikysimboh/makefun-btc-race-24h/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

# Race a BTC Trading Bot Live for 24 Hours

This repository holds an entry for the make.fun bounty
[Race a BTC trading bot live for 24 hours](https://make.fun/bounty/btc-race-24h-20261123-0511)
— $50, 10 places paid. The bot trades Coinbase Wrapped BTC (cbBTC)
against USDC, minute by minute, on a replay of its Orca Whirlpool
on-chain prices, starting with $1,000 of paper money. Nothing is traded
for real.

## The strategy

Ride the trend, cut the loss. One decisive trade per trend, not churn:

- **Buy all-in** when the latest close breaks above the highest close of
  the previous 120 minutes (a 2-hour Donchian breakout).
- **Sell everything** when the latest close falls 2% under the close
  the buy was decided on, or 2% under the highest close seen since
  the buy (a trailing stop).
- Otherwise hold. Cash earns nothing, so the bot waits for a real
  breakout instead of trading one-minute noise.

Why this shape: a full-size round trip pays roughly 40 bps in fees,
slippage and pool impact on this pool, so fast EMA crosses bleed money —
the kit's own ema-cross baseline loses $114.83 on the dev window on 76
trades, while buy-and-hold makes $32.17. This bot keeps the round trips
rare (1 trade on the dev window) and caps the downside with stops.

Local grade on the frozen dev window: **net PnL +$26.84, 1 trade,
max drawdown 2.0%** — comfortably above the $0 dev gate. (Verified with
a local replay driver that replicates the harness's exact integer fill
math — fees, slippage, pool impact — and reproduces the official
grader's buy-and-hold result of +$32.17 to the cent; the kit's
`grade-local --driver process` runs Node bots only, so the Python bot
is graded by the server in Docker.) On the time-reversed dev window
(a falling market) it loses $21.31, against $38.39 for buy-and-hold:
the stops do their job.

## Running it

`main.py` runs on Python 3.13 and uses only the standard library, plus
the vendored `agent-fun/bars-replay/v1` shim in `vendor/` (a byte-for-byte
copy of the kit's `sdk/makefun_bars.py`). It speaks the protocol on
stdin/stdout: one JSON line per minute bar in, exactly one reply out.
It never reads the wall clock, the environment or any randomness, so two
runs on the same bars answer the same orders.

```sh
python3 main.py
```

## What is in here

- `main.py` — the bot, standard library only
- `vendor/makefun_bars.py` — the protocol shim, copied byte-for-byte from the kit
- `LICENSE` — MIT

## License

MIT — see `LICENSE`.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
