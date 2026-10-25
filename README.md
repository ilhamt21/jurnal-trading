# Jurnal Trading untuk Android

Aplikasi ini berisi jurnal trading yang sama dengan versi web. Bedanya, aplikasi ini berjalan **offline** di HP Anda. Trade, akun, payout, dan screenshot disimpan di dalam aplikasi.

APK tidak perlu dibuat sendiri di komputer. GitHub yang membuatnya secara otomatis dan gratis.

## Membuat APK (sekali saja, sekitar 10 menit)

1. Buat akun gratis di https://github.com, lalu login.
2. Klik **+** (kanan atas) → **New repository**.
   - Nama: `jurnal-trading`
   - Pilih **Private**, supaya kunci tanda tangan aplikasi tidak bisa dilihat orang lain.
   - Klik **Create repository**.
3. Di halaman repository yang masih kosong, klik **uploading an existing file**.
4. Ekstrak file ZIP ini di komputer. Buka folder `JurnalTrading`, pilih **semua isinya**, lalu seret ke halaman GitHub.
   - Folder `.github` tersembunyi di beberapa komputer. Pastikan folder itu ikut terunggah. Di Windows: File Explorer → View → centang "Hidden items".
5. Klik **Commit changes**.
6. Buka tab **Actions**. Proses "Build APK" akan berjalan sekitar 5–8 menit. Tunggu sampai tanda hijau ✓ muncul.
7. Buka halaman repository → **Releases** (kolom kanan) → **Jurnal Trading v1** → klik file `JurnalTrading-1.apk`.

## Memasang di HP

1. Buka halaman **Releases** dari browser HP (login GitHub dulu karena repository-nya Private), lalu unduh file `.apk`.
2. Buka file tersebut. Android akan meminta izin "Instal aplikasi tidak dikenal" untuk browser Anda. Izinkan.
3. Ketuk **Pasang**. Ikon **Jurnal Trading** akan muncul di layar utama.

Kalau muncul peringatan Play Protect, pilih **Tetap pasang**. Aplikasi ini tidak berasal dari Play Store, jadi Android tidak mengenalnya.

## Memindahkan data dari versi web

1. Di jurnal versi web: tab **Trade** → **Cadangkan**. File `.json` akan tersimpan.
2. Kirim file itu ke HP, misalnya lewat Google Drive, Telegram, atau kabel USB.
3. Di aplikasi: tab **Trade** → **Pulihkan** → pilih file tersebut.

Semua trade, akun, payout, dan screenshot akan ikut pindah.

## Penting: cadangkan secara rutin

Data aplikasi hanya tersimpan di HP. Kalau aplikasi dihapus atau HP hilang, datanya ikut hilang.

Biasakan menekan **Cadangkan** seminggu sekali. File cadangan tersimpan di folder **Download/JurnalTrading**. Salin file itu ke Google Drive.

## Memperbarui aplikasi

Kalau ada versi baru dari jurnal:

1. Ganti file `app/src/main/assets/index.html` di GitHub dengan file yang baru. Caranya: buka file itu di GitHub → ikon pensil → tempel isi baru, atau unggah ulang.
2. Di `app/build.gradle`, naikkan `versionCode` (misalnya 1 → 2) dan `versionName` (misalnya "1.0" → "1.1").
3. Commit. GitHub akan membuat APK baru di Releases.
4. Pasang APK baru itu di atas aplikasi lama. **Data tidak hilang**, karena semua versi ditandatangani dengan kunci yang sama (`app/jurnal.keystore`). Jangan hapus atau ganti file kunci tersebut.
