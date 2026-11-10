# Riset Nikkei 225 (JP225) untuk trading harian

> **STATUS: AWAL — belum diverifikasi dengan harga yang bisa ditradingkan.**
> Semua angka di sini dari **cash index Nikkei 225** (harian, 2006–Nov 2024), bukan dari CFD JP225 Exness.
> Harga *open* cash index punya masalah "stale open" (lihat bagian 6). Angka strategi gap kemungkinan **terlalu bagus**.
> Langkah wajib berikutnya: uji ulang dengan data JP225 M5/H1 dari MT5 Exness.

## 1. Data

| Data | Periode | Catatan |
|---|---|---|
| Nikkei 225 cash, harian OHLC | Mei 2006 – Nov 2024 (4.540 hari) | Gabungan 4 file Yahoo Finance dari repo GitHub publik; di periode tumpang tindih close identik |
| S&P 500 close harian | 2000 – 2023 | Untuk korelasi "Wall Street semalam" |
| USD/JPY H1 Dukascopy | 2007 – Mar 2023 | Harga 09:00 dan 15:00 JST |

Yahoo, Stooq, dan Dukascopy datafeed tidak bisa diakses dari lingkungan ini (diblokir / dibatasi), jadi belum ada data **intraday** Nikkei.

Gambar ringkasan: `nikkei-karakteristik.png`.

## 2. Karakteristik utama

1. **Hampir semua kenaikan terjadi semalam (overnight), bukan saat sesi Tokyo.**
   2006–2024: gap close→open kumulatif **+173%**, intraday open→close kumulatif **−49%**.
   Hari dengan intraday naik hanya 49,5%. Beli saat Tokyo buka dan tutup sore hari = melawan arus jangka panjang.
2. **Gap adalah ciri utama.** Median |gap| ±0,5%. **21% hari gap ≥1%**, hanya 25% hari gap <0,25%.
   Gap mengikuti Wall Street semalam (korelasi 0,58) dan USD/JPY semalam (0,54).
3. **Gap kecil ditutup, gap besar lanjut.**
   - |gap| <0,25%: tertutup di hari itu 80%.
   - |gap| 0,5–1%: tertutup 30%, lanjut 50% (acak).
   - |gap| 1–2%: tertutup hanya 10%, **lanjut searah gap 67%**, rata-rata intraday searah gap +0,56%.
4. **Volatilitas**: median range harian ±1% (2017/2019 ±0,7%, 2008 1,9%). Sekitar 2× GBP/USD. Ekor gemuk: 4% hari bergerak >3%, 45 hari >5%. Terburuk 5 Agu 2024 −12,4%, lalu +10,2% besoknya.
5. **Tidak ada momentum harian**: autokorelasi return lag-1 −0,04 (sedikit mean-reversion). Filter EMA20/EMA50 **tidak** membantu intraday (di atas EMA20 justru rata-rata intraday −0,02%).
6. **Hari**: Senin intraday terlemah (−0,05%, naik 47%). **Bulan**: Agustus (−1,0%) dan Januari (−0,7%) lemah; November (+2,3%), April (+2,1%), Desember (+1,6%) kuat.
7. **Candle**: median body 50% dari range, 40% hari body ≥60% ("trend day"), doji 9%. Close di 20% atas range 26% hari, di 20% bawah 22%.
8. **Intraday Nikkei searah USD/JPY** pada sesi yang sama (korelasi 0,41): yen melemah → Nikkei naik.

## 3. Uji strategi harian (daily OHLC, belum ada SL intraday yang presisi)

**Gap-lanjut**: |gap| ≥ ambang → entry di open searah gap, SL = close kemarin (gap tertutup), exit di close. R = hasil / ukuran gap. Jika SL dan close bagus di hari yang sama → dihitung SL.

| Ambang gap | Trade/thn | Win | Rata-rata R | Setelah spread 0,05% | Tahun positif |
|---|---|---|---|---|---|
| ≥0,5% | 129 | 55% | +0,22 | | |
| ≥0,75% | 87 | 61% | +0,29 | | |
| **≥1,0%** | 54 | 67% | **+0,39** | +0,35 | 19/19 |
| **≥1,25%** | 32 | 72% | **+0,50** | +0,47 | 18/19 |
| ≥1,5% | 15 | 75% | +0,61 | | |

- 2020–2024 saja (≥1%): 237 trade, win 66%, +0,35R. Buy dan sell sama baiknya.
- Filter: S&P semalam searah (+0,41 vs +0,27), USD/JPY semalam searah (+0,40 vs +0,25). Filter EMA tidak membantu.
- SL lebih lebar (1,5× gap) menurunkan R.
- **Gap-fade** (lawan gap kecil 0,2–0,8%, target close kemarin): **rugi** (−0,04 s/d −0,20R).
- Buy open–sell close tanpa syarat: rugi.

## 4. Kenapa angka ini belum boleh dipercaya ("stale open")

Open cash index Nikkei dihitung jam 09:00 dari harga pembukaan 225 saham. Banyak saham belum match di detik pertama, jadi harga *open* index memakai close kemarin untuk saham-saham itu. Akibatnya:
- gap tercatat **lebih kecil** dari gap yang sebenarnya;
- sisa gap muncul di menit-menit pertama dan tercatat sebagai "intraday lanjut searah gap".

Ini membuat strategi gap-lanjut tampak lebih bagus daripada kenyataan. Korelasi intraday vs gap (+0,24) sebagian bisa berasal dari artefak ini.

**Bukti artefaknya nyata di data ini:**
- Gap tercatat tidak pernah melebihi ±2,6% dalam 18 tahun, padahal ada 180 hari dengan |close−close| >3%.
- Saat S&P semalam bergerak ≥3% (90 hari), median |gap| tercatat hanya 1,47% tetapi median |close−close| 2,46%.
- 5 Agu 2024: open tercatat −1,8%, close −12,4%. 6 Agu 2024: open tercatat +2,0% **dan open = low hari itu**, close +10,2%. Futures/CFD saat itu sudah dibuka jauh lebih tinggi; "intraday +8%" di cash index sebagian besar sebenarnya gap.

Artinya sebagian "lanjutan gap" pada tabel di bagian 3 adalah gap itu sendiri yang terlambat tercatat. Berapa besar porsinya hanya bisa dihitung dengan data CFD/futures.

Di **CFD JP225** (buka ±23 jam) tidak ada "gap" jam 09:00 JST, karena harganya sudah bergerak saat sesi AS. Versi yang bisa diuji di JP225: **pergerakan 15:15 JST (tutup Tokyo kemarin) → 09:00 JST ≥1% → trading searah selama sesi Tokyo** dengan SL/TP intraday sebenarnya.

## 5. Yang dibutuhkan untuk lanjut

Ekspor dari MT5 Exness dengan `ExportDataBacktest.mq5`:
- `InpSymbols` = `JP225,USDJPY` (nama persis seperti di Market Watch, mis. `JP225m`),
- `InpFrom` = 2016, M5 dan H1,
- kirim `JP225_M5.csv`, `JP225_H1.csv`, `info_server.txt`, dan spesifikasi simbol (spread, swap, jam trading).

Rencana uji di data Exness:
1. Verifikasi jam server vs jam Tokyo (09:00 JST = 00:00 UTC) dan cek hari ekstrem (5 Agu 2024).
2. Ulangi uji gap/overnight-lanjut dengan harga CFD sebenarnya + SL/TP M5, per tahun.
3. Breakout range 60 menit pertama Tokyo, dengan dan tanpa filter USD/JPY.
4. Pullback EMA di H1 sebagai pembanding.
