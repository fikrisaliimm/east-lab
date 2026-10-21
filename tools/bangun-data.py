import json, io, os, shutil

SUMBER = r'C:\Users\ASUS\AppData\Local\Temp\profil-dosen\karya-rapi.json'
OUT = r'D:\Website\Profil-Ganjar'
os.makedirs(OUT, exist_ok=True)

W = json.load(io.open(SUMBER, encoding='utf-8'))

lihat, bersih = set(), []
for w in W:
    k = (w['judul'].lower()[:90], w['thn'])
    if k in lihat:
        continue
    lihat.add(k)
    bersih.append(w)

artikel = [w for w in bersih if w['type'] in ('article', 'review', 'preprint')]
prosiding = [w for w in bersih if w['type'] == 'conference-paper']
bab = [w for w in bersih if w['type'] == 'book-chapter']
lain = [w for w in bersih if w['type'] not in ('article', 'review', 'preprint', 'conference-paper', 'book-chapter')]

def kunci(w):
    return (-(w['thn'] or 0), w['judul'].lower())

for g in (artikel, prosiding, bab, lain):
    g.sort(key=kunci)

terpilih = sorted([w for w in bersih if w['type'] in ('article', 'review')],
                  key=lambda w: -w['sitasi'])[:12]

def kecil(w):
    return {'t': w['thn'], 'p': w['penulis'], 'j': w['judul'],
            'v': w['terbit'], 'd': w['doi'], 's': w['sitasi']}

data = {'terpilih': [kecil(w) for w in terpilih],
        'artikel': [kecil(w) for w in artikel],
        'prosiding': [kecil(w) for w in prosiding],
        'bab': [kecil(w) for w in bab],
        'lain': [kecil(w) for w in lain]}

print('artikel', len(artikel), '| prosiding', len(prosiding), '| bab', len(bab), '| lain', len(lain))
print('terpilih', len(terpilih))

js = 'window.KARYA = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n'
io.open(os.path.join(OUT, 'data.js'), 'w', encoding='utf-8', newline='\n').write(js)
print('data.js', os.path.getsize(os.path.join(OUT, 'data.js')), 'bita')
shutil.copy(SUMBER, os.path.join(OUT, 'karya-openalex.json'))
