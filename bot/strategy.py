"""Strategi CRT sesi New York.

Aturan (versi SELL, BUY kebalikannya). Semua jam = waktu New York.

1. Referensi  : high & low candle H4 05:00 (= H1 05:00-08:00).
2. Sweep      : salah satu candle H1 di jendela H4 09:00 (09:00-12:00)
                menembus HIGH referensi dan close BEARISH kembali di bawah
                high itu. Sisi yang tersapu pertama kali menentukan bias.
3. Target     : swing low H1 terdekat di bawah harga entry (fractal).
                Swing bersih diutamakan; equal lows dipakai kalau tidak ada.
4. Filter FVG : di H1, dari swing low itu sampai candle sweep, TIDAK BOLEH
                ada FVG bullish (high candle-1 < low candle-3).
5. Entry      : harga close candle H1 sweep.
6. SL         : high candle M30 terakhir sebelum entry (+ buffer).
7. Filter RR  : jarak entry -> target harus >= 1R.
8. Kelola     : 2 order @ setengah risiko. Order A TP 1:1. Begitu A kena TP,
                SL order B pindah ke entry (breakeven). Semua posisi
                ditutup saat candle H4 09:00 close (13:00).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta

import pandas as pd

from .data import resample


@dataclass
class Params:
    pip: float = 0.0001            # EURUSD: 0.0001, pair JPY: 0.01
    sl_buffer_pips: float = 1.0    # ditambahkan di atas/bawah candle M30 (pengganti spread)
    min_rr: float = 1.0            # target minimal (dalam R)
    ref_hour: int = 5              # candle H4 referensi
    window_hour: int = 9           # candle H4 tempat mencari sweep
    close_hour: int = 13           # semua posisi ditutup di jam ini
    swing_lookback: int = 48       # berapa candle H1 ke belakang mencari swing
    fractal_bars: int = 1          # jumlah candle di kiri/kanan untuk swing


@dataclass
class Setup:
    day: date
    side: str                 # "SELL" / "BUY"
    trigger_time: datetime    # jam buka candle H1 sweep
    entry_time: datetime
    entry: float
    sl: float
    tp1: float
    target: float             # swing terdekat
    target_time: datetime
    ref_high: float
    ref_low: float

    @property
    def risk(self) -> float:
        return abs(self.sl - self.entry)

    @property
    def target_rr(self) -> float:
        return abs(self.target - self.entry) / self.risk


@dataclass
class DayResult:
    day: date
    status: str                          # "TRADE" atau alasan dilewati
    notes: list[str] = field(default_factory=list)
    setup: Setup | None = None
    r_a: float | None = None             # hasil order A (dalam R)
    r_b: float | None = None             # hasil order B (dalam R)
    exit_a: str = ""
    exit_b: str = ""

    @property
    def r_total(self) -> float | None:
        # Masing-masing order memakai setengah risiko.
        if self.r_a is None:
            return None
        return (self.r_a + self.r_b) / 2


def _is_swing(h1: pd.DataFrame, i: int, n: int, low: bool, allow_equal: bool = False) -> bool:
    if i - n < 0 or i + n >= len(h1):
        return False
    col = h1["low"] if low else h1["high"]
    v = col.iloc[i]
    left = col.iloc[i - n:i]
    right = col.iloc[i + 1:i + n + 1]
    # allow_equal: equal low/high dihitung swing (boleh sama dengan candle
    # kiri, tapi harus lebih ekstrem dari candle kanan).
    if low:
        ok_left = (v <= left).all() if allow_equal else (v < left).all()
        return bool(ok_left and (v < right).all())
    ok_left = (v >= left).all() if allow_equal else (v > left).all()
    return bool(ok_left and (v > right).all())


def _find_target(h1, trig_i, entry, side, p: Params):
    """Swing H1 terdekat (paling baru) di sisi target, sudah terkonfirmasi.

    Swing bersih diutamakan. Equal low/high baru dipakai kalau tidak ada
    swing bersih di bawah/atas harga entry.
    """
    for allow_equal in (False, True):
        found = _scan_target(h1, trig_i, entry, side, p, allow_equal)
        if found[0] is not None:
            return found
    return None, None


def _scan_target(h1, trig_i, entry, side, p: Params, allow_equal: bool):
    want_low = side == "SELL"
    start = max(0, trig_i - p.swing_lookback)
    for i in range(trig_i - p.fractal_bars, start - 1, -1):
        # konfirmasi fractal hanya boleh memakai candle sampai candle sweep
        if i + p.fractal_bars > trig_i:
            continue
        if _is_swing(h1, i, p.fractal_bars, low=want_low, allow_equal=allow_equal):
            price = h1["low"].iloc[i] if want_low else h1["high"].iloc[i]
            if (want_low and price < entry) or (not want_low and price > entry):
                return i, price
    return None, None


def _opposing_fvg(h1, from_i, to_i, side):
    """Cari FVG yang berlawanan arah entry di candle H1 from_i..to_i."""
    for i in range(from_i, to_i - 1):
        c1, c3 = h1.iloc[i], h1.iloc[i + 2]
        if side == "SELL" and c1["high"] < c3["low"]:      # FVG bullish
            return h1.index[i + 1], c1["high"], c3["low"]
        if side == "BUY" and c1["low"] > c3["high"]:       # FVG bearish
            return h1.index[i + 1], c3["high"], c1["low"]
    return None


def find_setup(day: date, h1: pd.DataFrame, m30: pd.DataFrame, p: Params) -> DayResult:
    day_start = datetime.combine(day, time(0))
    ref_start = day_start + timedelta(hours=p.ref_hour)
    win_start = day_start + timedelta(hours=p.window_hour)
    close_t = day_start + timedelta(hours=p.close_hour)

    ref = h1[(h1.index >= ref_start) & (h1.index < ref_start + timedelta(hours=4))]
    if len(ref) < 4:
        return DayResult(day, "DATA KURANG", [f"candle H1 referensi hanya {len(ref)}/4"])
    ref_high, ref_low = ref["high"].max(), ref["low"].min()

    window = h1[(h1.index >= win_start) & (h1.index < win_start + timedelta(hours=4))]
    if len(window) == 0:
        return DayResult(day, "DATA KURANG", ["tidak ada candle H1 di jendela 09:00"])

    res = DayResult(day, "TIDAK ADA SWEEP")
    bias = None
    for t, bar in window.iterrows():
        hi_swept = bar["high"] > ref_high
        lo_swept = bar["low"] < ref_low
        hhmm = t.strftime("%H:%M")

        if bias is None:
            if hi_swept and lo_swept:
                res.status = "DUA SISI TERSAPU"
                res.notes.append(f"H1 {hhmm} menyapu high dan low sekaligus")
                return res
            if hi_swept:
                bias = "SELL"
            elif lo_swept:
                bias = "BUY"
            else:
                continue
            res.notes.append(f"H1 {hhmm} menyapu {'HIGH' if bias == 'SELL' else 'LOW'} H4 05:00 -> bias {bias}")

        if bias == "SELL":
            if not hi_swept:
                continue
            if not (bar["close"] < bar["open"] and bar["close"] < ref_high):
                res.status = "CLOSE TIDAK VALID"
                res.notes.append(f"H1 {hhmm}: close tidak bearish / tidak kembali di bawah high")
                continue
        else:
            if not lo_swept:
                continue
            if not (bar["close"] > bar["open"] and bar["close"] > ref_low):
                res.status = "CLOSE TIDAK VALID"
                res.notes.append(f"H1 {hhmm}: close tidak bullish / tidak kembali di atas low")
                continue

        entry_time = t + timedelta(hours=1)
        if entry_time >= close_t:
            res.status = "TERLAMBAT"
            res.notes.append(f"H1 {hhmm}: konfirmasi pas jam tutup {p.close_hour}:00")
            continue

        entry = float(bar["close"])
        trig_i = h1.index.get_loc(t)

        last_m30 = m30[m30.index == entry_time - timedelta(minutes=30)]
        if len(last_m30) == 0:
            res.status = "DATA KURANG"
            res.notes.append(f"candle M30 {entry_time - timedelta(minutes=30):%H:%M} tidak ada")
            continue
        buf = p.sl_buffer_pips * p.pip
        sl = float(last_m30["high"].iloc[0] + buf) if bias == "SELL" else float(last_m30["low"].iloc[0] - buf)
        risk = abs(sl - entry)
        if risk <= 0:
            res.status = "SL TIDAK VALID"
            continue

        tgt_i, target = _find_target(h1, trig_i, entry, bias, p)
        if tgt_i is None:
            res.status = "TIDAK ADA SWING"
            res.notes.append(f"H1 {hhmm}: swing target tidak ditemukan")
            continue

        fvg = _opposing_fvg(h1, tgt_i, trig_i, bias)
        if fvg is not None:
            res.status = "ADA FVG"
            kind = "bullish" if bias == "SELL" else "bearish"
            res.notes.append(f"H1 {hhmm}: FVG {kind} di candle {fvg[0]:%d/%m %H:%M} ({fvg[1]:.5f}-{fvg[2]:.5f})")
            continue

        rr = abs(target - entry) / risk
        if rr < p.min_rr:
            res.status = "RR < 1"
            res.notes.append(f"H1 {hhmm}: target {target:.5f} hanya {rr:.2f}R (SL {risk / p.pip:.1f} pips)")
            continue

        tp1 = entry - risk if bias == "SELL" else entry + risk
        res.status = "TRADE"
        res.setup = Setup(
            day=day, side=bias, trigger_time=t.to_pydatetime(), entry_time=entry_time.to_pydatetime(),
            entry=entry, sl=sl, tp1=tp1, target=float(target),
            target_time=h1.index[tgt_i].to_pydatetime(), ref_high=float(ref_high), ref_low=float(ref_low),
        )
        return res
    return res


def simulate(res: DayResult, base: pd.DataFrame, p: Params) -> DayResult:
    """Jalankan trade di candle data dasar (makin kecil timeframe-nya makin akurat).

    Kalau satu candle menyentuh SL dan TP sekaligus, dianggap SL duluan
    (asumsi paling konservatif).
    """
    s = res.setup
    close_t = datetime.combine(s.day, time(p.close_hour))
    bars = base[(base.index >= s.entry_time) & (base.index < close_t)]
    sell = s.side == "SELL"
    R = s.risk

    def r_of(price):
        return ((s.entry - price) if sell else (price - s.entry)) / R

    a_open = b_open = True
    sl_b = s.sl
    for t, bar in bars.iterrows():
        adverse = bar["high"] if sell else bar["low"]
        favor = bar["low"] if sell else bar["high"]
        hit = (lambda lvl: adverse >= lvl) if sell else (lambda lvl: adverse <= lvl)
        reach = (lambda lvl: favor <= lvl) if sell else (lambda lvl: favor >= lvl)

        a_tp_now = False
        if a_open:
            if hit(s.sl):
                res.r_a, res.exit_a, a_open = -1.0, f"SL {t:%H:%M}", False
            elif reach(s.tp1):
                res.r_a, res.exit_a, a_open = 1.0, f"TP1 {t:%H:%M}", False
                a_tp_now = True
        if b_open and hit(sl_b):
            res.r_b = r_of(sl_b)
            res.exit_b = ("BE " if sl_b == s.entry else "SL ") + f"{t:%H:%M}"
            b_open = False
        if a_tp_now:
            sl_b = s.entry  # breakeven berlaku mulai candle berikutnya
        if not a_open and not b_open:
            break

    last_close = float(bars["close"].iloc[-1]) if len(bars) else s.entry
    if a_open:
        res.r_a, res.exit_a = r_of(last_close), f"tutup {p.close_hour}:00"
    if b_open:
        res.r_b, res.exit_b = r_of(last_close), f"tutup {p.close_hour}:00"
    return res


def run(base: pd.DataFrame, p: Params, start: date | None = None, end: date | None = None) -> list[DayResult]:
    m30 = resample(base, "30min")
    h1 = resample(base, "1h")
    days = sorted({d for d in h1.index.date})
    out = []
    for d in days:
        if d.weekday() >= 5:
            continue
        if (start and d < start) or (end and d > end):
            continue
        r = find_setup(d, h1, m30, p)
        if r.status == "TRADE":
            r = simulate(r, base, p)
        out.append(r)
    return out


def lot_size(balance: float, risk_pct: float, sl_pips: float,
             pip_value_per_lot: float = 10.0, step: float = 0.01) -> float:
    """Lot untuk satu order. Dibulatkan ke bawah supaya risiko tidak lewat batas.

    pip_value_per_lot = 10 USD untuk EURUSD (akun USD).
    """
    raw = balance * risk_pct / 100 / (sl_pips * pip_value_per_lot)
    return max(0.0, int(raw / step + 1e-9) * step)
