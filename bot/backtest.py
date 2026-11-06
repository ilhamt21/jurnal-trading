"""Backtest strategi CRT sesi New York dari file CSV.

Contoh:
    python -m bot.backtest data/EURUSD_M5.csv --from 2026-10-28 --to 2026-11-04

Lihat bot/README.md untuk cara mengambil data dari MetaTrader 5.
"""

from __future__ import annotations

import argparse
from datetime import date

from .data import load_bars
from .strategy import Params, lot_size, run


def main(argv=None):
    ap = argparse.ArgumentParser(description="Backtest CRT sesi New York")
    ap.add_argument("csv", help="file candle (M1/M5/M15/M30), ekspor MT5 atau CSV biasa")
    ap.add_argument("--source-tz", default="auto",
                    help="zona waktu data: auto (default), ny+7, UTC, Asia/Jakarta, ...")
    ap.add_argument("--from", dest="start", type=date.fromisoformat)
    ap.add_argument("--to", dest="end", type=date.fromisoformat)
    ap.add_argument("--pip", type=float, default=0.0001, help="ukuran pip (JPY: 0.01)")
    ap.add_argument("--sl-buffer", type=float, default=1.0, help="buffer SL dalam pips")
    ap.add_argument("--min-rr", type=float, default=1.0, help="target swing minimal (R), boleh desimal")
    ap.add_argument("--min-sl", type=float, default=3.0, help="SL minimal (pips); lebih kecil -> setup batal")
    ap.add_argument("--spread", type=float, default=1.0, help="spread (pips) dihitung sebagai biaya")
    ap.add_argument("--tp-rr", type=float, default=1.0, help="TP Order A (R), boleh desimal, misal 1.5")
    ap.add_argument("--runner-close", type=int, default=None,
                    help="VARIASI: jam (NY) Order B ditutup, misal 17. Default ikut jam 13:00")
    ap.add_argument("--no-m30-filter", action="store_true",
                    help="VARIASI: matikan filter CRT M30 yang melawan arah")
    ap.add_argument("--h4-open-filter", action="store_true",
                    help="VARIASI: SELL hanya di atas open H4 sesi, BUY di bawahnya")
    ap.add_argument("--max-trigger-h1", type=int, default=4,
                    help="VARIASI: pemicu hanya dari H1 ke-1..N di dalam sesi (default 4 = semua)")
    ap.add_argument("--balance", type=float, default=10_000)
    ap.add_argument("--risk", type=float, default=0.5, help="risiko total per setup (%%)")
    ap.add_argument("--pip-value", type=float, default=10.0, help="nilai 1 pip per 1 lot (USD)")
    a = ap.parse_args(argv)

    p = Params(pip=a.pip, sl_buffer_pips=a.sl_buffer, min_rr=a.min_rr, tp_rr=a.tp_rr,
               min_sl_pips=a.min_sl, spread_pips=a.spread,
               runner_close_hour=a.runner_close,
               m30_counter_filter=not a.no_m30_filter,
               h4_open_filter=a.h4_open_filter, max_trigger_h1=a.max_trigger_h1)
    base = load_bars(a.csv, a.source_tz)
    results = run(base, p, a.start, a.end)

    print(f"Data: {base.index[0]:%Y-%m-%d %H:%M} s/d {base.index[-1]:%Y-%m-%d %H:%M} (jam New York)\n")
    for r in results:
        print(f"{r.day:%a %d %b %Y}  {r.status}")
        for n in r.notes:
            print(f"    - {n}")
        if r.setup:
            s = r.setup
            sl_pips = s.risk / p.pip
            lots = lot_size(a.balance, a.risk / 2, sl_pips, a.pip_value)
            print(f"    {s.side} entry {s.entry:.5f} @ {s.entry_time:%H:%M} | SL {s.sl:.5f} ({sl_pips:.1f} pips)"
                  f" | TP1 {s.tp1:.5f} | swing {s.target:.5f} ({s.target_rr:.2f}R)")
            print(f"    lot: 2 x {lots:.2f}")
            print(f"    Order A: {r.exit_a:<12} {r.r_a:+.2f}R   Order B: {r.exit_b:<12} {r.r_b:+.2f}R"
                  f"   -> total {r.r_total * a.risk:+.2f}%")
        print()

    trades = [r for r in results if r.status == "TRADE"]
    print("=" * 60)
    print(f"Hari dicek      : {len(results)}")
    print(f"Setup valid     : {len(trades)}")
    if trades:
        tp1 = sum(1 for r in trades if r.exit_a.startswith("TP1"))
        sl = sum(1 for r in trades if r.exit_a.startswith("SL"))
        timeout = len(trades) - tp1 - sl
        total_pct = sum(r.r_total for r in trades) * a.risk
        print(f"Kena TP1 (1:1)  : {tp1}")
        print(f"Kena SL         : {sl}")
        print(f"Tutup jam 13:00 : {timeout}")
        print(f"Hasil total     : {total_pct:+.2f}% dari saldo")
    skipped = {}
    for r in results:
        if r.status != "TRADE":
            skipped[r.status] = skipped.get(r.status, 0) + 1
    if skipped:
        print("Dilewati        : " + ", ".join(f"{k} x{v}" for k, v in sorted(skipped.items())))


if __name__ == "__main__":
    main()
