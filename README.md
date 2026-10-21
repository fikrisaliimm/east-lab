# Profil Ganjar Fadillah — situs statis

Situs profil akademik, satu orang. Empat halaman, tanpa pustaka luar, tanpa build.
Data publikasi ditarik otomatis dari OpenAlex oleh GitHub Actions.

## Isi

| Berkas | Guna |
|---|---|
| `index.html` | Top — kabar: publikasi terbaru (otomatis) + kegiatan tetap |
| `publikasi.html` | Publications — publikasi terpilih, artikel, prosiding, buku, paten, ceramah, hibah |
| `profil.html` | Profiles — identitas, riwayat, penghargaan, organisasi, bidang keilmuan |
| `akses.html` | Access — lokasi dan kontak |
| `gaya.css` | seluruh tampilan |
| `data.js` | data publikasi (DIBUAT OTOMATIS — jangan disunting tangan) |
| `tools/ambil-openalex.py` | penarik data dari OpenAlex |
| `.github/workflows/perbarui.yml` | penjadwal mingguan |

## Cara memasang di GitHub Pages

Folder ini **sudah berupa repo git** (branch `main`, 5 commit). Yang belum ada
hanya alamat remote. Jadi ada dua jalan.

### Jalan A — lewat git (dianjurkan)

1. Buat repo **baru dan publik** di GitHub. Nama bebas, misal `profil-ganjar`.
   **Jangan** centang "Add a README", "Add .gitignore", atau "Choose a license" —
   nanti push ditolak karena riwayatnya bentrok. Biarkan kosong.
2. Jalankan:

```bash
cd "D:/Website/Profil-Ganjar"
git remote add origin https://github.com/<namapengguna>/profil-ganjar.git
git push -u origin main
```

3. Saat diminta, masuk lewat peramban (Git Credential Manager sudah aktif di
   mesin ini). Kalau muncul pilihan, pilih **sign in with your browser** —
   jangan menempel kata sandi akun, itu sudah tidak dipakai GitHub.
4. **Settings → Pages** → *Build and deployment* → Source: **Deploy from a branch**
   → Branch: `main`, folder `/ (root)` → **Save**.
5. Tunggu 1–2 menit, muat ulang halaman itu sampai muncul kotak
   "Your site is live at …". Alamat: `https://<namapengguna>.github.io/profil-ganjar/`

### Jalan B — lewat peramban saja (tanpa git)

1. Buat repo publik kosong seperti di atas.
2. **Add file → Upload files**, seret semua isi folder.
3. Yang sering terlewat: folder `.github` (berisi workflow). Windows Explorer
   menyembunyikannya — aktifkan **View → Show → Hidden items** dulu, atau
   unggah `.github/workflows/perbarui.yml` terpisah lewat
   **Add file → Create new file**, ketik nama `/.github/workflows/perbarui.yml`.
4. Commit, lalu lakukan langkah 4–5 di atas.

### Kalau halaman 404

- Pastikan repo **publik**. Pages gratis tidak aktif di repo privat.
- Pastikan berkas ada di **akar** repo (`index.html` sejajar `README.md`),
  bukan di dalam subfolder.
- Alamat harus diakhiri garis miring: `.../profil-ganjar/` — tanpa itu kadang 404.
- Butuh sampai 10 menit pada pemuatan pertama.


## Membuat data ikut memperbarui sendiri

Workflow sudah ada di `.github/workflows/perbarui.yml`. Bawaannya jalan
**tiap Senin 02.00 UTC (09.00 WIB)**, dan bisa dijalankan manual dari
tab **Actions → Perbarui data publikasi → Run workflow**.

Tidak ada setelan yang wajib. Yang dianjurkan:

**Kunci OpenAlex (gratis).** Tanpa kunci, setiap permintaan memakai satu jatah
harian bersama per alamat IP; server GitHub Actions berbagi IP dengan banyak
orang, jadi bisa kehabisan dan gagal. Cara:

1. Buka https://openalex.org/settings/api — minta kunci dengan surel
   `ganjar.fadillah@uii.ac.id` (atau surelmu).
2. Klik tautan konfirmasi yang dikirim ke surel.
3. Di repo: **Settings → Secrets and variables → Actions → New repository secret**.
   Nama: `OPENALEX_KEY`, isi: kuncinya.
4. Workflow sudah membacanya sebagai `secrets.OPENALEX_KEY`.

## Batas yang perlu diketahui

- **Bukan waktu nyata.** OpenAlex menarik dari Crossref dan penerbit. Artikel
  biasanya muncul 1–14 hari setelah terbit; prosiding konferensi bisa berbulan-bulan.
- **Satu profil penulis saja** (`A5026624986`). OpenAlex punya dua profil lain
  bernama sama berisi 1 karya; keduanya diabaikan. Karya yang keliru terdaftar
  di profil lain tidak akan tertangkap.
- **Paten dan ceramah undangan tidak bisa otomatis** — OpenAlex tak punya datanya.
  Bagian itu diisi tangan bila ada daftarnya.
- **Foto profil** masih kotak kosong. Simpan berkasnya sebagai `foto.jpg`
  (lebar ≥ 860 px), lalu ganti blok `<div class="foto">` di `profil.html`
  menjadi `<img src="foto.jpg" alt="Ganjar Fadillah">`.
- Repo harus **publik** agar GitHub Pages gratis aktif.

## Menjalankan sendiri di komputer

```bash
python tools/ambil-openalex.py          # perbarui data.js
python -m http.server 8080              # lalu buka http://127.0.0.1:8080
```

Hanya butuh Python 3.8+ tanpa pustaka tambahan.
