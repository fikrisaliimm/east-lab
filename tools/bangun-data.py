# Bangun data.js murni dari DRH (tabel C), tanpa sumber luar.
import io, json, os, re

# drh.json ada di folder privat di sebelah situs, bukan di dalam folder ini.
SITUS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRIVAT = os.environ.get('GANJAR_PRIVAT') or (SITUS + '-privat')
drh = json.load(open(os.path.join(PRIVAT, 'data', 'drh.json'), encoding='utf-8'))
rows = drh[2][1:]

# Salah ketik pada DRH dibetulkan di sini, bukan di dokumen sumbernya.
KOREKSI = [
    ('utnuk', 'untuk'),
    ('Kemasaran', 'kemasan'),
    ('Nickle', 'Nickel'),
    ('Antu Reflekting', 'Anti Reflecting'),
]

def betulkan(s):
    for a, b in KOREKSI:
        s = s.replace(a, b)
    return s

def bersih(s):
    return betulkan(re.sub(r'\s+', ' ', (s or '')).strip())

data = []
for r in rows:
    penulis, judul, jurnal, indeks, vol, tahun, doi = [bersih(x) for x in r[1:8]]
    if doi.lower().startswith('https://doi.org/'):
        doi = doi[len('https://doi.org/'):]
    elif doi.lower().startswith('http'):
        doi = ''
    data.append({'t': int(tahun), 'p': penulis, 'j': judul, 'n': jurnal,
                 'v': (jurnal + (', ' + vol if vol else '')), 'q': indeks, 'd': doi})

data.sort(key=lambda x: (-x['t'], x['j']))
q1 = [d for d in data if d['q'] == 'Q1']
q2 = [d for d in data if d['q'] == 'Q2']
q3 = [d for d in data if d['q'] == 'Q3']
pr = [d for d in data if d['q'].lower().startswith('prosiding')]
terbaru = [d for d in data if d['t'] == max(x['t'] for x in data)]

out = {
    'meta': {'jumlah': len(data), 'q1': len(q1), 'q2': len(q2), 'q3': len(q3),
             'prosiding': len(pr), 'h': 27, 'terbit_terakhir': max(x['t'] for x in data),
             'sumber': 'DRH'},
    'terbaru': terbaru,
    'q1': q1, 'q2': q2, 'q3': q3, 'prosiding': pr,
}

p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data.js')
isi = ('/* Data publikasi: daftar riwayat hidup Ganjar Fadillah (tabel C).\n'
       '   Tidak ada data dari sumber luar. Jangan sunting manual: jalankan\n'
       '   tools/bangun-data.py. */\n'
       'window.KARYA = ' + json.dumps(out, ensure_ascii=False, indent=1) + ';\n')
io.open(p, 'w', encoding='utf-8', newline='\n').write(isi)

print('entri', len(data), '| Q1', len(q1), 'Q2', len(q2), 'Q3', len(q3),
      'Prosiding', len(pr), '| terbaru', len(terbaru))
sisa = [k for k, _ in KOREKSI if k in io.open(p, encoding='utf-8').read()]
print('salah ketik tersisa:', sisa or 'tidak ada')

# Stempel versi pada tautan aset: tanpa ini peramban memakai data.js lama
# dari cache dan angka di halaman tidak ikut berubah.
import hashlib
akar = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
h = hashlib.sha256()
for n in ('data.js', 'gaya.css'):
    h.update(open(os.path.join(akar, n), 'rb').read())
v = h.hexdigest()[:8]
for f in ('index.html', 'publikasi.html', 'profil.html', 'akses.html'):
    q = os.path.join(akar, f)
    s = io.open(q, encoding='utf-8').read()
    s2 = re.sub(r'(src="data\.js)(\?v=[0-9a-f]+)?"', r'\1?v=' + v + '"', s)
    s2 = re.sub(r'(href="gaya\.css)(\?v=[0-9a-f]+)?"', r'\1?v=' + v + '"', s2)
    if s2 != s:
        io.open(q, 'w', encoding='utf-8', newline='\n').write(s2)
print('versi aset', v)
print('byte', os.path.getsize(p))
