"""Uji strategi dengan contoh setup A+ (4 Nov 2026, JPY ~178, jam New York).

Jalankan: python -m unittest bot.test_strategy -v
"""

import os
import tempfile
import unittest
from datetime import date

import pandas as pd

from bot.data import load_bars
from bot.strategy import Params, find_setup, lot_size, run, simulate
from bot.data import resample

DAY = "2026-11-04"

# Candle H1 (open, high, low, close) mendekati screenshot.
H1 = {
    "01:00": (177.70, 177.80, 177.65, 177.75),
    "02:00": (177.75, 177.97, 177.70, 177.95),
    "03:00": (177.95, 178.06, 177.92, 177.96),
    "04:00": (177.96, 178.41, 177.94, 178.33),
    "05:00": (178.33, 178.37, 178.17, 178.33),
    "06:00": (178.33, 178.36, 178.20, 178.29),
    "07:00": (178.29, 178.36, 178.151, 178.27),   # swing low = target
    "08:00": (178.27, 178.465, 178.255, 178.355),  # high = high H4 05:00
    # 09:00 dipecah manual di M30 di bawah (sweep ke 178.482, close 178.317)
    # 10:00 dipecah manual (TP1 kena)
    "11:00": (178.00, 178.05, 177.73, 177.74),
    "12:00": (177.74, 177.86, 177.72, 177.84),
    "13:00": (177.84, 177.95, 177.80, 177.90),
}
M30_MANUAL = {
    "09:00": (178.355, 178.38, 178.33, 178.38),
    "09:30": (178.38, 178.482, 178.29, 178.317),   # SL = high ini
    "10:00": (178.317, 178.33, 178.10, 178.12),    # TP1 178.152 kena
    "10:30": (178.12, 178.15, 177.97, 178.00),
}


def build(h1=H1, m30=M30_MANUAL, day=DAY):
    rows = {}
    for hhmm, (o, h, l, c) in h1.items():
        t = pd.Timestamp(f"{day} {hhmm}")
        mid = round((o + c) / 2, 3)
        if c < o:   # bearish: high dulu, low belakangan
            rows[t] = (o, h, min(o, mid), mid)
            rows[t + pd.Timedelta(minutes=30)] = (mid, max(mid, c), l, c)
        else:
            rows[t] = (o, max(o, mid), l, mid)
            rows[t + pd.Timedelta(minutes=30)] = (mid, h, min(mid, c), c)
    for hhmm, v in m30.items():
        rows[pd.Timestamp(f"{day} {hhmm}")] = v
    df = pd.DataFrame.from_dict(rows, orient="index", columns=["open", "high", "low", "close"])
    return df.sort_index()


P = Params(pip=0.01, sl_buffer_pips=0.0)


class APlusExample(unittest.TestCase):
    def test_setup_detected(self):
        base = build()
        r = run(base, P)[0]
        self.assertEqual(r.status, "TRADE", r.notes)
        s = r.setup
        self.assertEqual(s.side, "SELL")
        self.assertEqual(s.entry_time.strftime("%H:%M"), "10:00")
        self.assertAlmostEqual(s.ref_high, 178.465)
        self.assertAlmostEqual(s.ref_low, 178.151)
        self.assertAlmostEqual(s.entry, 178.317)
        self.assertAlmostEqual(s.sl, 178.482)
        self.assertAlmostEqual(s.tp1, 178.152)
        self.assertAlmostEqual(s.target, 178.151)
        self.assertGreaterEqual(s.target_rr, 1.0)

    def test_trade_management(self):
        r = run(build(), P)[0]
        self.assertEqual(r.r_a, 1.0)
        self.assertTrue(r.exit_a.startswith("TP1 10:00"))
        # Order B jalan sampai 13:00, close 12:30 = 177.84
        self.assertTrue(r.exit_b.startswith("tutup"))
        self.assertAlmostEqual(r.r_b, (178.317 - 177.84) / 0.165, places=3)

    def test_bullish_fvg_invalidates(self):
        h1 = dict(H1)
        h1["07:00"] = (178.20, 178.25, 178.151, 178.24)  # high 07 < low 09 -> FVG bullish
        r = run(build(h1), P)[0]
        self.assertEqual(r.status, "ADA FVG", r.notes)

    def test_rr_below_one_skipped(self):
        r = run(build(), Params(pip=0.01, sl_buffer_pips=5.0))[0]
        self.assertEqual(r.status, "RR < 1", r.notes)

    def test_bullish_close_not_valid(self):
        m30 = dict(M30_MANUAL)
        m30["09:30"] = (178.38, 178.482, 178.29, 178.40)  # close di atas open -> bukan bearish
        r = run(build(m30=m30), P)[0]
        self.assertNotEqual(r.status, "TRADE")

    def test_breakeven_after_tp1(self):
        m30 = dict(M30_MANUAL)
        m30["10:30"] = (178.12, 178.33, 178.10, 178.30)  # balik ke entry setelah TP1
        r = run(build(m30=m30), P)[0]
        self.assertEqual(r.r_a, 1.0)
        self.assertEqual(r.r_b, 0.0)
        self.assertTrue(r.exit_b.startswith("BE"))

    def test_runner_variation_holds_order_b_longer(self):
        # Variasi: Order B ditahan sampai 17:00 -> tutup di close candle terakhir (13:30)
        r = run(build(), Params(pip=0.01, sl_buffer_pips=0.0, runner_close_hour=17))[0]
        self.assertEqual(r.r_a, 1.0)
        self.assertEqual(r.exit_b, "tutup 17:00")
        self.assertAlmostEqual(r.r_b, (178.317 - 177.90) / 0.165, places=3)

    def test_sl_hit(self):
        m30 = dict(M30_MANUAL)
        m30["10:00"] = (178.317, 178.50, 178.20, 178.45)
        r = run(build(m30=m30), P)[0]
        self.assertEqual(r.r_a, -1.0)
        self.assertEqual(r.r_b, -1.0)


# Contoh 2 dari user: pair NZD (~2.39), 4 Nov 2026. Sweep tipis oleh H1 11:00,
# target = swing low H1 08:00 (2.3912), BUKAN low candle H4 05:00 (2.3903).
NZD_H1 = {
    "01:00": (2.4020, 2.4025, 2.4000, 2.4003),
    "02:00": (2.4003, 2.4010, 2.3980, 2.3986),
    "03:00": (2.3986, 2.3990, 2.3960, 2.3967),
    "04:00": (2.3967, 2.3980, 2.3929, 2.3934),
    "05:00": (2.3934, 2.3943, 2.3903, 2.3936),
    "06:00": (2.3937, 2.3974, 2.3936, 2.3957),
    "07:00": (2.3957, 2.3971, 2.3946, 2.3962),
    "08:00": (2.3962, 2.3963, 2.3912, 2.3913),
    "09:00": (2.3913, 2.3955, 2.3913, 2.3941),
    "13:00": (2.3937, 2.3960, 2.3935, 2.3958),
}
NZD_M30 = {
    "10:00": (2.3941, 2.3969, 2.3932, 2.3961),   # high = C1 high (garis biru user)
    "10:30": (2.3961, 2.3966, 2.3944, 2.3944),
    "11:00": (2.3944, 2.3975, 2.3940, 2.3963),   # sweep high H4 05:00 (2.3974)
    "11:30": (2.3963, 2.3964, 2.3929, 2.3942),   # close bearish = entry
    "12:00": (2.3942, 2.3945, 2.3926, 2.3934),
    "12:30": (2.3934, 2.3940, 2.3930, 2.3937),
}


class NzdExample(unittest.TestCase):
    def test_target_is_nearest_h1_swing_not_h4_low(self):
        r = run(build(NZD_H1, NZD_M30), Params())[0]
        self.assertEqual(r.status, "TRADE", r.notes)
        s = r.setup
        self.assertEqual(s.side, "SELL")
        self.assertEqual(s.entry_time.strftime("%H:%M"), "12:00")
        self.assertAlmostEqual(s.entry, 2.3942)
        self.assertAlmostEqual(s.ref_low, 2.3903)
        self.assertAlmostEqual(s.target, 2.3912)
        self.assertEqual(s.target_time.strftime("%H:%M"), "08:00")

    def test_no_tp_closed_at_13(self):
        r = run(build(NZD_H1, NZD_M30), Params())[0]
        self.assertTrue(r.exit_a.startswith("tutup"))
        self.assertGreater(r.r_a, 0)

    def test_equal_lows_used_when_no_clean_swing(self):
        # Low H1 08:00 = 09:00 dan tidak ada swing bersih lain -> equal lows dipakai.
        h1 = dict(NZD_H1)
        h1["09:00"] = (2.3913, 2.3955, 2.3912, 2.3941)
        h1["05:00"] = (2.3934, 2.3943, 2.3925, 2.3936)   # hapus swing bersih 05:00
        h1["04:00"] = (2.3967, 2.3980, 2.3920, 2.3934)
        h1["03:00"] = (2.3986, 2.3990, 2.3915, 2.3967)
        h1["02:00"] = (2.4003, 2.4010, 2.3914, 2.3986)
        h1["01:00"] = (2.4020, 2.4025, 2.3913, 2.4003)
        r = run(build(h1, NZD_M30), Params())[0]
        self.assertEqual(r.status, "TRADE", r.notes)
        self.assertAlmostEqual(r.setup.target, 2.3912)

    def test_clean_swing_preferred_over_equal_lows(self):
        # Equal lows 08:00/09:00 (2.3912) lebih dekat, tapi swing bersih
        # 05:00 (2.3903) yang diutamakan.
        h1 = dict(NZD_H1)
        h1["09:00"] = (2.3913, 2.3955, 2.3912, 2.3941)
        h1["07:00"] = (2.3957, 2.3971, 2.3940, 2.3962)   # tanpa FVG 05:00-07:00
        r = run(build(h1, NZD_M30), Params())[0]
        self.assertEqual(r.status, "TRADE", r.notes)
        self.assertAlmostEqual(r.setup.target, 2.3903)


class M30CounterFilter(unittest.TestCase):
    # Kasus GBPUSD 3 Nov 2026: M30 terakhir sebelum entry SELL menyapu low
    # M30 sebelumnya lalu close bullish -> harga naik dulu, setup batal.
    def test_counter_m30_crt_cancels_sell(self):
        m30 = dict(NZD_M30)
        m30["11:30"] = (2.3930, 2.3950, 2.3935, 2.3942)  # low < low 11:00, close bullish
        r = run(build(NZD_H1, m30), Params())[0]
        self.assertEqual(r.status, "M30 MELAWAN", r.notes)

    def test_filter_can_be_disabled(self):
        m30 = dict(NZD_M30)
        m30["11:30"] = (2.3930, 2.3950, 2.3935, 2.3942)
        r = run(build(NZD_H1, m30), Params(m30_counter_filter=False))[0]
        self.assertNotEqual(r.status, "M30 MELAWAN")


class Helpers(unittest.TestCase):
    def test_lot_size_rounds_down(self):
        # $10.000, 0,25% = $25, SL 16,5 pips, $10/pip/lot -> 0,1515 -> 0,15
        self.assertAlmostEqual(lot_size(10_000, 0.25, 16.5), 0.15)

    def test_mt5_export_and_auto_timezone(self):
        # Jam server = NY + 7: pasar buka Minggu 17:00 NY = Senin 00:00 server.
        idx = pd.date_range("2026-11-02 00:00", periods=4, freq="30min")
        prev = pd.date_range("2026-10-30 22:00", periods=2, freq="30min")
        lines = ["<DATE>\t<TIME>\t<OPEN>\t<HIGH>\t<LOW>\t<CLOSE>\t<TICKVOL>\t<VOL>\t<SPREAD>"]
        for t in list(prev) + list(idx):
            lines.append(f"{t:%Y.%m.%d}\t{t:%H:%M:%S}\t1.1\t1.2\t1.0\t1.1\t10\t0\t5")
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
            f.write("\n".join(lines))
        try:
            df = load_bars(f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual(df.index[2], pd.Timestamp("2026-11-01 17:00"))


if __name__ == "__main__":
    unittest.main()
