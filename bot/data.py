"""Memuat data candle dari file CSV dan mengubah jamnya ke waktu New York.

Format yang didukung:
- Ekspor MetaTrader 5 (Symbols -> Bars -> Export):
  <DATE>  <TIME>  <OPEN>  <HIGH>  <LOW>  <CLOSE>  ...
- CSV biasa dengan kolom waktu (time/datetime/timestamp/date [+ time])
  dan kolom open, high, low, close.

Semua waktu di dalam program disimpan sebagai jam dinding New York tanpa
zona waktu (naive), karena seluruh aturan strategi memakai jam New York.
"""

from __future__ import annotations

import pandas as pd

NY = "America/New_York"


def _read_raw(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8-sig") as f:
        head = f.readline()

    if "<DATE>" in head.upper():
        df = pd.read_csv(path, sep="\t")
        df.columns = [c.strip("<>").lower() for c in df.columns]
        ts = pd.to_datetime(
            df["date"].astype(str) + " " + df.get("time", "00:00:00").astype(str),
            format="%Y.%m.%d %H:%M:%S",
            errors="coerce",
        )
    else:
        sep = ";" if head.count(";") > head.count(",") else ","
        df = pd.read_csv(path, sep=sep)
        df.columns = [c.strip().lower() for c in df.columns]
        for name in ("datetime", "timestamp", "time", "date"):
            if name in df.columns:
                if name == "date" and "time" in df.columns:
                    ts = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str))
                else:
                    col = df[name]
                    if pd.api.types.is_numeric_dtype(col):
                        unit = "ms" if col.iloc[0] > 1e11 else "s"
                        ts = pd.to_datetime(col, unit=unit)
                    else:
                        ts = pd.to_datetime(col)
                break
        else:
            raise ValueError("Kolom waktu tidak ditemukan (time/datetime/timestamp/date).")

    out = pd.DataFrame(
        {c: pd.to_numeric(df[c], errors="coerce") for c in ("open", "high", "low", "close")}
    )
    if getattr(ts.dt, "tz", None) is not None:
        ts = ts.dt.tz_convert("UTC").dt.tz_localize(None)
    out.index = pd.DatetimeIndex(ts, name="time")
    out = out.dropna().sort_index()
    return out[~out.index.duplicated(keep="last")]


def detect_offset_from_ny(index: pd.DatetimeIndex) -> int:
    """Tebak selisih jam server broker terhadap jam New York.

    Pasar forex buka setiap Minggu pukul 17:00 New York. Bar pertama setelah
    libur akhir pekan dipakai sebagai patokan. Kebanyakan broker MT5 memakai
    jam server = New York + 7 jam.
    """
    gaps = index.to_series().diff() > pd.Timedelta(hours=24)
    opens = index[gaps.values]
    if len(opens) == 0:
        raise ValueError(
            "Tidak bisa menebak zona waktu: data tidak memuat pembukaan pasar "
            "setelah akhir pekan. Isi --source-tz secara manual (contoh: UTC "
            "atau ny+7)."
        )
    offsets = []
    for t in opens:
        # Pembukaan pasar = hari Minggu 17:00 New York sebelum bar ini.
        days_back = (t.weekday() - 6) % 7  # Minggu = 6
        sunday = (t - pd.Timedelta(days=days_back)).normalize()
        if days_back == 0 and t.hour < 17:
            sunday -= pd.Timedelta(days=7)
        ny_open = sunday + pd.Timedelta(hours=17)
        offsets.append(round((t - ny_open) / pd.Timedelta(hours=1)))
    return int(pd.Series(offsets).mode().iloc[0])


def to_ny(df: pd.DataFrame, source_tz: str = "auto") -> pd.DataFrame:
    """Ubah index ke jam dinding New York (naive).

    source_tz:
      "auto"   -> ditebak dari jam buka pasar (cocok untuk ekspor MT5)
      "ny+7"   -> jam server = New York + 7 (format umum broker MT5)
      nama IANA, contoh "UTC", "Asia/Jakarta"
    """
    df = df.copy()
    src = source_tz.strip().lower()
    if src == "auto":
        src = f"ny{detect_offset_from_ny(df.index):+d}"
    if src.startswith("ny"):
        hours = int(src[2:] or 0)
        df.index = df.index - pd.Timedelta(hours=hours)
    else:
        idx = df.index.tz_localize(source_tz, ambiguous="NaT", nonexistent="shift_forward")
        df.index = idx.tz_convert(NY).tz_localize(None)
        df = df[df.index.notna()]
    df.index.name = "time"
    return df


def load_bars(path: str, source_tz: str = "auto") -> pd.DataFrame:
    return to_ny(_read_raw(path), source_tz)


def resample(df: pd.DataFrame, rule: str) -> pd.DataFrame:
    """Gabungkan candle kecil menjadi candle lebih besar (label = jam buka)."""
    agg = df.resample(rule, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    return agg.dropna()
