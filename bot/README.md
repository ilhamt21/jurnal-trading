# Bot CRT Sesi New York

Tahap 1: **backtest**. Bot live (notifikasi Telegram dan eksekusi) dibangun setelah hasil backtest meyakinkan.

## Aturan yang diprogram (semua jam = waktu New York)

| # | Aturan | Contoh SELL |
|---|---|---|
| 1 | Referensi: high/low candle **H4 05:00** | high 05:00–09:00 |
| 2 | Salah satu candle **H1 09:00–12:00** menyapu high/low referensi. Sisi yang tersapu pertama menentukan bias | sapu HIGH → SELL |
| 3 | Candle H1 itu close searah bias **dan** kembali ke dalam range | close bearish, di bawah high |
| 4 | Target = **swing H1 terdekat** (fractal 3 candle; swing bersih diutamakan, equal lows/highs dipakai kalau tidak ada) | swing low terdekat |
| 5 | Dari swing target sampai candle sweep **tidak ada FVG berlawanan** di H1, **sekecil apa pun**, termasuk FVG yang candle tengahnya candle swing | tidak ada FVG bullish |
| 6 | Entry = close candle H1 sweep | |
| 7 | SL = high/low **candle M30 terakhir** + buffer (default 1 pip). **Batal** kalau M30 itu menyapu low/high M30 sebelumnya dan close melawan arah | high M30 + 1 pip |
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

## Variasi untuk diuji (bukan aturan utama)

| Opsi | Arti |
|---|---|
| `--runner-close 17` | Order A tetap ditutup jam 13:00, **Order B ditahan sampai jam 17:00** (atau jam lain) |

Contoh perbandingan: jalankan sekali tanpa opsi, sekali dengan `--runner-close 17`, lalu bandingkan hasil totalnya.

## Backtest di TradingView (Pine Script)

File: `bot/tradingview/crt_ny.pine`, dengan aturan yang sama dengan bot Python.

1. Buka TradingView di **browser/desktop** (bukan aplikasi HP) → chart pair yang diuji → timeframe **M30**.
2. Buka **Pine Editor** di bawah → hapus isinya → tempel seluruh isi `crt_ny.pine` → **Save** → **Add to chart**.
3. Klik ikon gear (Settings) indikator → isi **Ukuran pip** (pair JPY: `0.01`).
4. Buka tab **Strategy Tester** → aktifkan **Deep Backtesting** (Premium), pilih rentang 5 tahun → **Generate report**.
5. Hasil utama dibaca dari **tabel di pojok kanan atas chart** (dalam R, per tahun). Angka dolar di Strategy Tester hanya akurat untuk pair dengan quote USD (EURUSD, GBPUSD, AUDUSD, …).

Di Settings, **Sesi** bisa dipilih: `09:00 saja (SOP)` (default) atau `Semua H4 (tiap 4 jam)`, yang memakai setiap candle H4 (01, 05, 09, 13, 17, 21 NY) sebagai referensi untuk candle H4 berikutnya dan menutup posisi saat candle H4 sesi itu close.

Label abu-abu di chart menunjukkan setup yang dibatalkan beserta alasannya (FVG berlawanan, RR < 1, terlambat, dua sisi tersapu).
| `--no-m30-filter` | Matikan filter CRT M30 yang melawan arah (untuk perbandingan) |
| `--tp-rr 1.5` | TP Order A di 1,5R (boleh desimal). Default 1 = TP 1:1 |
| `--min-rr 1.2` | Target swing minimal 1,2R (boleh desimal) |
