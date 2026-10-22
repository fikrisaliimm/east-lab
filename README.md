# Profil Ganjar Fadillah

Situs statis empat halaman untuk Ganjar Fadillah, S.Si., M.Si., Ph.D. (Kimia, UII).
Tanpa CDN, tanpa build, tanpa basis data.

**Seluruh isi berasal dari satu sumber: daftar riwayat hidup (DRH) yang bersangkutan.**
Tidak ada data dari OpenAlex, Scopus API, Google Scholar, atau laman lain.

## Halaman

| Berkas | Isi |
|---|---|
| `index.html` | Beranda: pengantar, angka ringkas, kabar |
| `publikasi.html` | 30 karya dari tabel C DRH, riset dipimpin, hibah |
| `profil.html` | Identitas, riwayat pendidikan, penghargaan, organisasi, bidang, hilirisasi |
| `akses.html` | Kontak |

## Alur data

```
DRH.docx ──tools/ambil-drh.py──> data/drh.json ──tools/bangun-data.py──> data.js
```

1. Taruh DRH terbaru di mana saja, lalu:

   ```
   python tools/ambil-drh.py "DRH-Ganjar.docx"
   python tools/bangun-data.py
   ```

2. `data.js` dihasilkan ulang. Halaman lain tidak perlu disentuh.

Isi `data/drh.json` adalah tabel DRH apa adanya (8 tabel). Nomor tabel:

| # | Tabel |
|---|---|
| 0 | Identitas |
| 1 | Riwayat pendidikan |
| 2 | Publikasi |
| 3 | Riset yang dipimpin |
| 4 | Hibah / pendanaan |
| 5 | Kelompok riset |
| 6 | Penghargaan |
| 7 | Hilirisasi |

## Angka

- **h-index 27** — sel "H-index (Scopus)" di tabel identitas DRH. Satu angka saja,
  tidak ada versi lain.
- **30 karya**, 24 di antaranya Q1, mengikuti kolom indeksasi DRH.
- **Sitasi tidak ditampilkan** — DRH tidak mencantumkannya.

## Yang tidak ditampilkan

- **Nominal dana hibah** dan **nomor kontrak/SK**, walau ada di tabel E DRH.
  Dijaga uji regex: `\d{1,3}\.\d{3}\.\d{3}` dan pola `\d{3}/…` harus nol temuan.

## Salah ketik

Salah ketik pada DRH dibetulkan, dicatat di satu tempat (`KOREKSI` pada
`tools/bangun-data.py`) supaya bisa diaudit:

| DRH | Situs |
|---|---|
| `utnuk` | untuk |
| `Kemasaran` | kemasan |
| `Nickle` | Nickel |
| `Antu Reflekting` | Anti Reflecting |
| `LTJi` | LTJ |

`Standford` → `Stanford` juga dibetulkan (nama institusi pemberi penghargaan).

## Uji

```
python uji.py
```

Memeriksa: jumlah entri per bagian, tidak ada nominal/kontrak, h-index 27,
tidak ada sisa kata "OpenAlex", judul tab, kontak, target sentuh ≥44px, dan
tidak ada luberan di 360/390/1280px.

## Catatan teknis

- Daftar karya di `publikasi.html` diisi JS dari `data.js`. Kalau JS mati, yang
  tampil hanya riset dan hibah (keduanya HTML statis).
- Font memakai tumpukan sistem; tidak ada berkas font yang diunduh.
- Foto: `foto.jpg` (900×1125) dan `foto-kecil.jpg` (420×525), dipakai sama di
  keempat halaman dengan `object-position` identik.
