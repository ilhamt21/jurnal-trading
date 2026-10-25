# Jurnal Trading (web + Android, tersinkron)

Satu kode untuk dua tempat:

- **Web:** `https://<username>.github.io/jurnal-trading/`, dibuat otomatis oleh GitHub Pages dari folder `web/`.
- **Android:** APK di menu **Releases**, juga dibuat otomatis. Isinya halaman yang sama dari folder `web/`.

Keduanya login ke **Supabase** dengan email dan password yang sama, jadi datanya selalu sama. Setiap perangkat menyimpan salinan data sendiri, sehingga tetap bisa dipakai tanpa internet. Perubahan dikirim begitu online lagi, dan perangkat lain menerimanya saat aplikasi dibuka, saat aplikasi kembali dilihat, atau setiap 1 menit.

## Isi folder

| File | Fungsi |
|---|---|
| `web/index.html` | Aplikasi jurnal (web dan Android) |
| `web/config.js` | **Alamat dan kunci Supabase Anda.** Diisi sekali. |
| `supabase.sql` | Perintah untuk membuat tabel di Supabase. Dijalankan sekali. |
| `app/` | Pembungkus Android |
| `.github/workflows/build-apk.yml` | Membuat APK dan mempublikasikan web setiap ada perubahan |

## Pengaturan sekali saja

1. **Supabase:** daftar di supabase.com → New project → SQL Editor → tempel isi `supabase.sql` → Run.
2. Salin **Project URL** dan **anon / publishable key** dari Project Settings → API Keys, lalu isi ke `web/config.js` di GitHub.
3. **GitHub:** Settings → General → ubah repository menjadi **Public** (GitHub Pages gratis hanya untuk repo publik). Lalu Settings → Pages → Source: **GitHub Actions**.

Catatan: setelah repo publik, kode dan file kunci tanda tangan aplikasi (`app/jurnal.keystore`) bisa dilihat orang. Data jurnal Anda **tidak** ada di repo, semuanya di Supabase dan dilindungi login. Kunci tanda tangan hanya bisa dipakai untuk membuat APK tiruan, yang tetap harus Anda pasang sendiri.

## Memperbarui

1. Ganti `web/index.html` dengan versi baru.
2. Naikkan `versionCode` di `app/build.gradle`.
3. Commit. Web langsung ikut terbarui. APK baru muncul di Releases dan bisa dipasang di atas versi lama tanpa kehilangan data.
