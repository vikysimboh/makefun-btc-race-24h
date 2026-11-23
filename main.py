#!/usr/bin/env python3
"""Donchian breakout bot for the make.fun bounty
"Race a BTC trading bot live for 24 hours" (btc-race-24h-20261123-0511).

Strategy, in plain words: ride the trend, cut the loss.
- Buy all-in when the latest close breaks above the highest close of the
  previous 120 minutes (a 2-hour Donchian breakout).
- Sell everything when the latest close falls 2% under the close the
  buy was decided on, or 2% under the highest close seen since the buy
  (a trailing stop).
- Otherwise hold. No position, no trade: cash earns nothing, so the bot
  waits for a real breakout instead of churning on one-minute noise.

Why this shape: a full-size round trip pays roughly 40 bps in fees,
slippage and pool impact on this pool, so one-minute EMA crosses bleed
money (the kit's own ema-cross baseline loses $114.83 on the dev window
on 76 trades). One decisive trade per trend costs one round trip and
keeps the drawdown small. The bot never reads the wall clock, the
environment or any randomness: its orders are a pure function of the
closes it has been sent, so two runs on the same bars answer the same.

Runs on Python 3.13, standard library only, through the vendored
agent-fun/bars-replay/v1 shim in vendor/makefun_bars.py (a byte-for-byte
copy of the kit's sdk/makefun_bars.py).
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
LOOKBACK = 120          # minutes of closes forming the breakout channel
STOP_BPS = 200          # 2% hard stop under the buy-decision close
TRAIL_BPS = 200         # 2% trailing stop under the peak close since entry
MAX_SLIPPAGE_BPS = 200  # 2% cap on the move from the latest close

# Closes seen so far (ints, the bar's "c" at its price scale), oldest first.
_closes = []
# Close the open buy was decided on, and the highest close since it.
_buy_close = None
_peak_close = None


def _reset_position():
    global _buy_close, _peak_close
    _buy_close = None
    _peak_close = None


def on_batch(state, batch):
    """The orders decided on this bar; [] for none."""
    global _buy_close, _peak_close
    if state.warming_up:
        return []
    bar = state.latest.get(SYMBOL)
    if bar is None:
        return []
    close = int(bar["c"])
    _closes.append(close)

    holding = state.positions.get(SYMBOL)
    held_qty = holding.qty if holding is not None else 0

    if held_qty > 0:
        # We hold: watch the exits.
        if _peak_close is None or close > _peak_close:
            _peak_close = close
        stop_price = _buy_close * (10000 - STOP_BPS) // 10000 if _buy_close else None
        trail_price = _peak_close * (10000 - TRAIL_BPS) // 10000 if _peak_close else None
        if (stop_price is not None and close < stop_price) or (
            trail_price is not None and close < trail_price
        ):
            _reset_position()
            return [
                {
                    "side": "sell",
                    "symbol": SYMBOL,
                    "qty": held_qty,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                }
            ]
        return []

    # Flat: wait for a breakout above the last 120 closes.
    if len(_closes) <= LOOKBACK:
        return []
    highest = max(_closes[-LOOKBACK - 1 : -1])
    if close > highest:
        _buy_close = close
        _peak_close = close
        return [
            {
                "side": "buy",
                "symbol": SYMBOL,
                "notional_quote_units": state.cash,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }
        ]
    return []


makefun_bars.run(on_batch)
