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

## Indikator reversal multi-timeframe

File: `bot/tradingview/reversal_mtf.pine`. Pilihan rantai (1 HTF = 4 MTF, 1 MTF = 4 LTF): **Daily → H6 → M90** atau **H4 → H1 → M15**. Pasang di chart M90 (atau M15), atau timeframe yang lebih kecil.

- **Sinyal reversal bullish:** C2 menyapu low C1, lalu candle MTF (H6/H1) close kembali di atas low C1 **dan** di atas open C2. Bearish kebalikannya.
- **Skor 0–10** dari ciri reversal: C1 berlawanan arah, close C1 dekat ekstrem, C1 berakhir lemah, C1 klimaks, low/high C1 = ekstrem 5 candle, sweep, sweep di awal candle, pemicu MTF, FVG di TF kecil, perubahan struktur TF kecil. Checklist muncul di label.
- **Tabel kanan bawah:** jumlah sinyal per kelompok skor, dan berapa persen C2 akhirnya close searah reversal.
- **Candle bayangan MTF:** setiap candle H6 (mode Daily) atau H1 (mode H4) digambar sebagai candle transparan besar (body + wick) di belakang candle kecil, bernomor, dengan tulisan "sweep" dan "PEMICU". Opsional candle bayangan HTF (Daily/H4). Garis putus-putus = awal candle HTF.
- **Alert:** saat sinyal muncul, dan opsional saat sweep terjadi.
- **Sinyal ENTRY (lebih awal dari sinyal reversal):**
  1. Candle MTF (H6/H1) menyapu high C1 lalu close bearish kembali di bawahnya → **bias SELL**.
  2. Di candle MTF berikutnya, candle kecil (M90/M15) menyapu high candle kecil sebelumnya. High yang menyamai high sebelumnya (selisih ≤ toleransi, default 1 pip) tetap dihitung sweep.
  3. Dalam maks 2 candle kecil, ada yang close bearish **di bawah open MTF** dan di bawah high yang disapu → **ENTRY**. SL di atas ujung sweep (+ buffer), target low C1, RR minimal bisa diatur. BUY kebalikannya.
  Semua sinyal dihitung **di candle yang baru close** (contoh: M90 06:30 close jam 08:00 → label ENTRY langsung di candle 06:30), tidak menunggu candle berikutnya.
  Tabel kanan atas: hasil simulasi ENTRY (jumlah trade, % menang, total R; posisi ditutup saat candle HTF close).

## Indikator candle HTF + referensi

File: `bot/tradingview/htf_candles.pine`. Pasang di chart **M15**. Candle HTF dibentuk dari candle chart sendiri, jadi H6 dan M90 tetap terlihat walaupun timeframe itu tidak dibuka di chart.

- **Rantai:** `Daily - H6 - M90` atau `H4 - H1 - M15` (kelompok M15 tidak ditampilkan karena sama dengan chart).
- **Panel kanan** (M90 → H6 → Daily): candle per tingkat (tampil ya/tidak, jumlah 1–10, jam NY). Semua garis horizontal (open, C1 / H4 05:00, likuiditas, 4 M90) digambar di panel ini, mulai dari candle-nya sampai ujung panel; riwayat hari sebelumnya tetap di chart.
- **Garis open** per tingkat (style, tebal, warna): open Daily/H4, semua open H6/H1 di dalam HTF yang berjalan, open M90.
- **Rantai Daily:** garis high/low C1 sampai Daily close, high/low Daily 3 hari ke belakang, garis high/low 4 M90 terakhir yang sudah close (bergulir).
- **Rantai H4:** garis high/low H4 05:00 sampai H4 09:00 close (13:00 NY), PDH/PDL dan sesi Asia 20–00, London 02–05, NY AM 07–11, NY PM 13:30–16 (3 hari ke belakang). Level yang sudah tersapu: samar / sama / disembunyikan.
- **Riwayat C1 / H4 05:00:** default hanya hari ini, bisa sampai 7 hari.
- **Garis vertikal** opening Daily dan Weekly, jumlah hari/minggu dan style bisa diatur.
