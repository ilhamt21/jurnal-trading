# Bot CRT Sesi New York

Tahap 1: **backtest**. Bot live (notifikasi Telegram dan eksekusi) dibangun setelah hasil backtest meyakinkan.

## Aturan yang diprogram (semua jam = waktu New York)

| # | Aturan | Contoh SELL |
|---|---|---|
| 1 | Referensi: high/low candle **H4 05:00** | high 05:00–09:00 |
| 2 | Salah satu candle **H1 09:00–12:00** menyapu high/low referensi. Sisi yang tersapu pertama menentukan bias | sapu HIGH → SELL |
| 3 | Candle H1 itu close searah bias **dan** kembali ke dalam range | close bearish, di bawah high |
| 4 | Target = **swing H1 terdekat** (fractal 3 candle; swing bersih diutamakan, equal lows/highs dipakai kalau tidak ada) | swing low terdekat |
| 5 | Dari swing target sampai candle sweep **tidak ada FVG berlawanan** di H1 | tidak ada FVG bullish |
| 6 | Entry = close candle H1 sweep | |
| 7 | SL = high/low **candle M30 terakhir** + buffer (default 1 pip) | high M30 + 1 pip |
| 8 | Target harus **≥ 1R**, kalau kurang dilewati | |
| 9 | 2 order × 0,25%: A TP 1:1. Setelah A kena, SL B pindah ke **breakeven** | |
| 10 | **Semua posisi ditutup jam 13:00** (close H4 09:00) | |

Asumsi backtest: kalau satu candle menyentuh SL dan TP sekaligus, dianggap kena SL dulu. Data yang lebih kecil (M5/M1) membuat hasilnya lebih akurat.

## Mengambil data dari MetaTrader 5 (gratis, akun demo pun bisa)

1. Buka MT5 di PC → menu **View → Symbols** (Ctrl+U) → tab **Bars**.
2. Pilih **EURUSD**, timeframe **M5** (atau M1/M15/M30), isi rentang tanggal → **Request**.
3. Klik **Export Bars** → simpan sebagai `.csv`.

Zona waktu server broker ditebak otomatis dari jam buka pasar hari Minggu. Rentang tanggal sebaiknya mencakup paling tidak satu akhir pekan.

## Menjalankan

```bash
pip install pandas
python -m bot.backtest EURUSD_M5.csv --from 2026-10-28 --to 2026-11-04
```

Opsi penting:

| Opsi | Default | Arti |
|---|---|---|
| `--source-tz` | `auto` | `auto`, `ny+7`, `UTC`, `Asia/Jakarta`, … |
| `--sl-buffer` | `1.0` | buffer SL dalam pips |
| `--pip` | `0.0001` | ukuran pip (pair JPY: `0.01`) |
| `--balance` / `--risk` | `10000` / `0.5` | untuk hitung lot dan persentase hasil |

## Tes

```bash
python -m unittest bot.test_strategy -v
```

Tesnya memakai setup A+ 4 Nov 2026 (entry 178.317, SL 178.482, TP1 178.152).
