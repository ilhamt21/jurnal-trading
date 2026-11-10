# Seasonality (pola kalender) — uji 11 instrumen

Data: Dukascopy H1 → harian (EURUSD, GBPUSD, USDJPY, AUDUSD, NZDUSD, USDCAD, USDCHF, XAUUSD, XAGUSD; 2007–Mar 2023), GBPUSD disambung Exness s/d Jul 2026, Nikkei 2006–2024, S&P 500 2005–2023.
Grid: 48 tanggal mulai (tgl 1/8/15/22 tiap bulan) × 7 lama tahan (5–60 hari trading) × BUY/SELL × 11 instrumen = 7.392 jendela. Exit berdasarkan waktu (close harian).
Pemilihan di tahun ≤2015, pembuktian di 2016+.

## Peringatan utama
- Dari 7.392 jendela, 13 punya WR 100% di 2007–2015. **Secara kebetulan saja diperkirakan muncul 15.** Di 2016+ WR mereka rata-rata hanya 59%.
- Jadi "WR 90% di masa lalu" sendirian tidak berarti apa-apa. Yang dicari: WR tinggi di periode latih DAN validasi, dan punya alasan ekonomi.

## Yang lolos dua periode (WR latih ≥85% & validasi ≥80%)

| Instrumen | Mulai | Tahan | Arah | WR total | Rata-rata | Terburuk | Alasan |
|---|---|---|---|---|---|---|---|
| **XAUUSD** | 22 Des | 20 hari | BUY | **88% (14/16)** | +3,7% | −1,4% (close), −4,3% intraperiode | Musiman emas Jan: permintaan India/Tiongkok, rebalancing awal tahun; dikenal luas |
| XAGUSD | 22 Des | 20 hari | BUY | 86% (12/14) | +5,2% | −1,2% / −7,0% | Ikut emas, lebih liar |
| USDCHF | 15 Nov | 60 hari | SELL | 94% (15/16) | +1,6% | −6,5% | Tidak ada alasan jelas; satu tahun rugi besar |
| NZDUSD | 22 Des | 5 hari | BUY | 93% (14/15) | +1,1% | −0,2% | Akhir tahun likuiditas tipis; gerak kecil |
| SP500 | 8 Mar | 40 hari | BUY | 89% (17/19) | +4,7% | −4,8% / −18,5% (2020) | Tren naik saham jangka panjang |

**Yang paling layak: emas BUY 22 Desember, tahan ±20 hari trading (s/d ±20 Januari).** 16 tahun: 14 menang. Dengan SL 3% (close harian): WR 81%, rata-rata +3,2%, rugi maks −3%.
Nikkei: tidak ada jendela yang bertahan (15 Des 5 hari: 100% di latih, 50% di validasi).

## Catatan
- Emas 2016–2025 tren naik kuat → WR BUY ikut terangkat. 2024 dan 2025 belum diuji (data Dukascopy berhenti Mar 2023) → perlu ekspor XAUUSD dari Exness.
- 1 trade/tahun = 16 sampel. WR "88%" sebenarnya rentang ±65–97%.
- Risiko per trade harus kecil: pergerakan intraperiode bisa −4% walau akhirnya untung.
