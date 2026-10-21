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

1. Buat repo **publik** di GitHub, misal `profil-ganjar`.
2. Unggah seluruh isi folder ini (termasuk folder `.github` dan `tools`).
   Lewat web: **Add file → Upload files**, seret semua, Commit.
   Berkas tersembunyi `.github` harus ikut — kalau lewat seret di Windows Explorer,
   aktifkan dulu "Hidden items", atau pakai git di bawah.
3. **Settings → Pages** → Source: *Deploy from a branch* → Branch: `main`, folder `/ (root)` → Save.
4. Tunggu 1–2 menit. Alamat: `https://<namapengguna>.github.io/profil-ganjar/`

### Lewat git (lebih rapi)

```bash
cd "D:/Website/Profil-Ganjar"
git init
git add .
git commit -m "Profil Ganjar Fadillah"
git branch -M main
git remote add origin https://github.com/<namapengguna>/profil-ganjar.git
git push -u origin main
```

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
