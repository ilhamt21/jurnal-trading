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
| 7 | SL = high/low **candle M30 terakhir** + buffer. Kalau M30 itu menyapu low/high M30 sebelumnya dan close melawan arah, **tunggu maks 2 candle M30** yang close searah bias (tanpa menembus ujung sweep); entry di close candle itu, SL di high/low-nya. Tidak ada konfirmasi = batal | high M30 + 1 pip |
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
| `--min-sl 3` | SL minimal dalam pips (default 3); lebih kecil -> setup batal |
| `--spread 1` | Spread dalam pips (default 1) dihitung sebagai biaya |

## Indikator sinyal H1 + Telegram

File: `bot/tradingview/crt_signal_h1.pine`. Memberi sinyal **BUY/SELL sampai level H1** (sweep H4, close H1 kembali ke range, filter FVG, target swing H1). Entry dan SL di M30 dieksekusi sendiri.

1. **Buat bot Telegram:** buka Telegram, chat **@BotFather**, kirim `/newbot`, ikuti petunjuk, lalu simpan **token**-nya (rahasia, jangan dibagikan).
2. **Cari Chat ID:** kirim pesan apa saja ke bot Anda, lalu buka di browser `https://api.telegram.org/bot<TOKEN>/getUpdates`. Angka di `"chat":{"id": ... }` adalah Chat ID.
3. **Pasang indikator** di chart M30 atau H1, buka Settings, isi **Telegram Chat ID**.
4. **Buat alert** (ikon jam): Condition = **CRT H1 Sinyal → Any alert() function call**. Di tab Notifications centang **Webhook URL** dan isi `https://api.telegram.org/bot<TOKEN>/sendMessage`. Expiration: open-ended.
5. Ulangi langkah 3–4 untuk setiap pair yang ingin dipantau (satu alert per pair).
| `--h4-open-filter` | VARIASI: SELL hanya kalau entry di atas open H4 sesi, BUY di bawahnya |
| `--max-trigger-h1 2` | VARIASI: pemicu hanya dari H1 ke-1 dan ke-2 di dalam sesi |

### Monitor likuiditas (di indikator sinyal H1)

Indikator melacak level likuiditas dan statusnya (**fresh** = belum ditembus sejak terbentuk):
high/low harian (PDH/PDL, beberapa hari ke belakang), high/low minggu lalu (PWH/PWL), high/low sesi Asia dan London, serta equal highs/lows dari swing H1.

- **Tabel kiri bawah:** level yang tersapu di candle H1 terakhir yang sudah close, dan 3 level fresh terdekat di atas dan di bawah harga.
- **Garis putus-putus:** level fresh (merah = atas, hijau = bawah). Garis hilang begitu level tersapu.
- **Sinyal/notifikasi** menyebutkan level fresh yang tersapu di sisi sweep selama sesi berjalan.
- **Filter opsional:** "minimal level fresh tersapu di sisi sweep" (0 = mati).

## Indikator candle pembalikan C1 → C2

File: `bot/tradingview/reversal_candle.pine`. Bisa dipakai di timeframe apa pun.

- **Pembalikan bullish:** C1 bearish, C2 menyapu low C1 lalu close bullish kembali di atas low C1. Bearish kebalikannya.
- **Kekuatan:** 1 = sweep & tolak, 2 = close melewati 50% C1, 3 = close melewati open C1 (body C1 ditelan).
- **Bedah timeframe kecil (otomatis):** urutan OHLC/OLHC C2, sub-candle tempat high/low terbentuk, dan apakah C1 "berakhir lemah".
- **Tabel kanan bawah:** jumlah pembalikan per kekuatan dan seberapa sering C3 melanjutkan arahnya.
- **Alert:** saat C2 close (sinyal final), dan opsional alert dini saat C2 masih berjalan.
