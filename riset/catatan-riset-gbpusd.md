# Catatan Riset Strategi C1 → H6 → Entry 05:00 NY (GBP/USD)

> **STATUS: TIDAK VALID (ditutup).** Uji 2026 (Jan–Jun, data Exness, aturan tidak diubah):
> Reversal −2,0R (11 trade), Breakout inside range −4,1R (10 trade), gabungan −6,1R, drawdown −11,1R.
> Keuntungan 2024–2026 hampir seluruhnya berasal dari satu tahun tren (2025). Tidak ada edge yang
> bertahan di berbagai kondisi pasar. Jangan dipakai untuk trading real.

Ringkasan semua uji yang sudah dilakukan, termasuk kesalahan yang sudah dikoreksi.
Angka di sini adalah angka **setelah koreksi** (lihat bagian "Koreksi").

## 1. Data dan konvensi waktu

| Data | Periode | Catatan |
|---|---|---|
| Dukascopy H1 (GBPUSD, EURUSD, USDJPY, AUDUSD, NZDUSD, USDCAD, USDCHF, XAUUSD, XAGUSD) | 2007 – Mar 2023 | Jam sudah benar (New York) |
| Dukascopy M5/M1 | 2007 – 2023 | **Banyak bolong** → jangan dipakai untuk memilih hari |
| Exness (broker sendiri) GBPUSD H1 | Mei 2018 – Jul 2026 | Diekspor dengan `ExportDataBacktest.mq5` |
| Exness GBPUSD M5 | Jun 2025 – Jul 2026 | |
| Exness USDJPY H1 / M5 | 2023 – Nov 2025 / Jul 2024 – Nov 2025 | M5 terpotong 100.000 bar |
| Kalender news (Forex Factory) | 2010 – Jan 2026 | Label dampak tidak selalu akurat → dilengkapi daftar news utama |

**Hari trading = 17:00 – 17:00 New York.** H6 = 17–23, 23–05, 05–11, 11–17 NY.

**Jam data Exness (sudah diverifikasi dengan Dukascopy dan lonjakan NFP):**
- Sebelum ±Juli 2024: jam server = jam London − 1 jam.
- Sejak akhir 2024: jam server = UTC (GMT+0).
- Akibatnya candle D1/H6 bawaan MT5 Exness **tidak** sama dengan candle versi New York.

| Momen | Jam NY | UTC (musim panas / dingin) | WIB (musim panas / dingin) |
|---|---|---|---|
| Daily buka / tutup posisi | 17:00 | 21:00 / 22:00 | 04:00 / 05:00 |
| H6-2 close = entry | 05:00 | 09:00 / 10:00 | 16:00 / 17:00 |

## 2. Aturan dasar

1. C1 = candle Daily kemarin. C1 bullish → cari SELL, C1 bearish → cari BUY.
2. H6-2 (23:00–05:00 NY) close berbalik arah dari C1.
3. Entry di close H6-2 (05:00 NY) atau limit order (lihat versi).
4. SL di luar wick H6-2 (+1 pip, + spread untuk SELL).
5. Tutup jam 13:00 atau 17:00 NY kalau SL/TP belum kena.

## 3. Versi yang teruji (GBP/USD)

| Versi | Filter | Entry / TP / tutup | Trade/thn | Hasil |
|---|---|---|---|---|
| Dasar | – | close / 1,2R / 17:00 | ±120 | ±0R (impas) |
| **A** | news besar USD + wick C1 ≥30% | limit 50% / 2R / 13:00 | ±14 | 2018–25: +0,28R/trade (t≈2,1); 2010–17: −0,05R |
| **C (bulanan)** | news besar USD + wick ≥40% | limit 25% / 1R / 17:00 | ±10 | win ±61% (2018–25 ±68%), +0,18R |
| **Ketat** | news USD + wick ≥50% | limit 50% / 2,5R / 13:00 | ±7–8 | uji+validasi: +0,26R; 13 dari 16 tahun untung |
| **Super selektif** | news USD + wick ≥80% | limit 50% / 1R / 17:00 | ±0,6 | 9 dari 9 menang (2010–2025); terlalu sedikit untuk pasti (WR sebenarnya ±66–100%) |
| Mingguan | news USD + wick ≥10% | limit 25% / 2,5R / 17:00 | ±58 | +0,08R, win ±38% (total ±+4,7R/thn) |

**Hubungan frekuensi vs kualitas:** makin sering trading, rata-rata per trade makin turun.
Wick C1 ≥60% → WR 63%; ≥70% → WR 76% (±2/thn); ≥80% → 100% (9 trade).

**2022** adalah tahun lemah hampir di semua versi (tren USD sangat kuat).

## 4. Yang tidak bekerja / tidak cukup

- Entry jam 23:00 NY (H6-1) dan entry saat Daily buka (17:00 NY) → rugi jangka panjang.
- Versi jam UTC (entry 05:00 UTC) → impas/rugi.
- Pair lain dengan aturan sama: EURUSD, AUDUSD, NZDUSD, USDCAD, USDCHF, XAU, XAG, GBPJPY, EURJPY, EURCAD, GBPCAD → di bawah GBPUSD / rugi.
  - Kandidat: **EURGBP** (sintetis) positif di dua periode → perlu dicek dengan data Exness asli.
  - USDJPY: tipis (±+0,05R).
- Target high/low C1 (lanjutan arah C1), RR 1:1 dengan patokan wick → rugi.
- 4 metode standar (Donchian 20/10 & 55/20, London breakout, breakout PDH/PDL) di GBPUSD → rugi di 2023–2026.
- Trend following hanya konsisten di **USDJPY dan emas** (Donchian 55/20, ±+0,25–0,3R, sedikit trade).
- Filter ML (meta-labeling) di strategi pairs EURUSD/GBPUSD → tidak membantu.
- Frekuensi dinaikkan 10× (8 instrumen × 3 jam entry) → edge hilang.

## 5. Koreksi (penting)

1. **Selection bias:** hasil awal "+0,27R/trade, win 62%" hanya memakai hari dengan data M5 Dukascopy lengkap. Hari yang terbuang ternyata rugi. Sudah dikoreksi.
2. **Jam data Exness:** sempat dianggap GMT+0 sepanjang waktu → candle bergeser 1 jam di sebagian periode, sehingga Exness dan Dukascopy tampak sangat berbeda. Setelah diperbaiki: 99% setup memberi hasil sama.
3. Klaim "perbedaan broker bisa menghapus profit" → **ditarik**; penyebabnya bug zona waktu.
4. Filter wick ≥30% ditemukan dari data yang sempat bias.
5. **Data getdata.finance (GBPUSD M1 Mar–Sep 2026) tidak valid**: dibanding data Exness, levelnya berbeda 10–190 pip pada jam yang sama (korelasi perubahan hanya 0,84). Kesimpulan "uji 2026" yang memakai data ini **ditarik**. Untuk 2026 hanya pakai data Exness.

## 5b. Strategi inside range Senin–Selasa (breakout)

- Syarat: open & close Selasa di dalam high–low Senin (wick boleh keluar).
- Rabu: stop order di high/low Senin; Kamis: high/low tertinggi–terendah Senin–Rabu; tidak terpicu = skip; tutup Jumat close.
- ±24 minggu valid per tahun (GBPUSD).
- Breakout terkonfirmasi H4 (candle H4 NY close di luar range, SL tengah range, TP 1,5R): 2025 +0,67R/trade (win 71%), tapi 2018–2024 −0,04R.
- Hasil bergantung kondisi pasar: menang di tahun tren kuat (2022: −1.437 pip, 2025: +965 pip; win ±70%), kalah di tahun menyamping (2024: −209 pip, range harian terkecil 80 pip; win 33%).
- Bukan karena perubahan jam server Exness (konversi jam sudah dicek; broker sama di semua tahun).
- Cocok dipasangkan dengan strategi reversal (yang lemah di tahun tren).

## 6. Pelajaran metodologi

- Pakai data lengkap; jangan ada hari yang terbuang diam-diam.
- Verifikasi jam data terhadap acuan independen (rilis news / sumber lain) sebelum analisis.
- Tetapkan aturan dulu, lalu uji; sisihkan periode yang tidak disentuh (uji/validasi).
- Laporkan rentang kemungkinan, bukan satu angka; curigai hasil yang terlalu bagus.

## 7. Langkah berikutnya yang tertunda

- EA MT5 / indikator TradingView untuk versi A, C, Ketat, dan Super selektif (alert + bisa di-backtest sendiri di Strategy Tester Exness).
- Ekspor data Exness EURGBP (dan GBPJPY, EURJPY) dengan `ExportDataBacktest.mq5` untuk cek kandidat EURGBP.
- Uji forward di akun demo dengan risiko kecil, catat di jurnal.

## 8. Strategi EMA (Weekly EMA20 → Daily EMA10/20 → H1)

- Aturan: bias dari close Weekly terakhir vs EMA 20; Daily kemarin close di atas (BUY) / di bawah (SELL) EMA 10 dan 20;
  H1: harga turun (BUY) / naik (SELL) dulu melewati open harian 17:00 NY, lalu candle H1 close kembali melewati open
  antara 02:00–11:00 NY → entry di close. Spread 1 pip. Contoh: `contoh-strategi-ema.png`.
- 2026 (Jan–Jun, Exness): 57 trade. Optimasi RR (0,5–5), SL (low dip / candle entry / tetap 15–30 pip), tahan 1–5 hari:
  terbaik **SL di bawah low dip, RR 2–2,25, tutup 17:00 NY → +0,13 s/d +0,19R/trade**, win ±47%, DD −6R.
  **Target +0,5R tidak tercapai** dengan RR saja. Daftar trade: `ema-trades-2026.csv`.
- Konfigurasi yang sama 2018–2025: 857 trade, −0,05R/trade (−40,8R), hanya 2022 dan 2024 positif.
- Filter sesi / ukuran risiko / arah: tidak ada yang konsisten di 2026 dan 2018–2025.
