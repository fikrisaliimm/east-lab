#!/usr/bin/env python3
"""Ambil karya Ganjar Fadillah dari OpenAlex, tulis data.js.

Dijalankan lokal maupun oleh .github/workflows/perbarui.yml.
Tanpa pustaka luar: hanya stdlib.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter

PENULIS = 'A5026624986'          # OpenAlex author id: Ganjar Fadillah (UII)
NAMA_PENULIS = 'Ganjar Fadillah'
KUNCI = os.environ.get('OPENALEX_KEY', '').strip()   # opsional, gratis dari openalex.org
AKAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KELUAR = os.path.join(AKAR, 'data.js')
ARSIP = os.path.join(AKAR, 'data', 'karya-openalex.json')
UA = f'profil-ganjar/1.0 (https://github.com/; mailto:ganjar.fadillah@uii.ac.id)'


def ambil(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def semua_karya():
    hasil, hal = [], 1
    while True:
        q = {
            'filter': f'author.id:{PENULIS}',
            'per-page': '200',
            'page': str(hal),
            'sort': 'publication_year:desc',
            'select': ('id,doi,title,publication_year,publication_date,type,'
                       'authorships,primary_location,cited_by_count,biblio,is_retracted'),
        }
        if KUNCI:
            q['api_key'] = KUNCI
        d = ambil('https://api.openalex.org/works?' + urllib.parse.urlencode(q))
        hasil += d['results']
        if len(d['results']) < 200:
            break
        hal += 1
        if hal > 20:
            break
    return hasil


def singkat(nama):
    p = nama.split()
    return ('. '.join(x[0] for x in p[:-1]) + '. ' + p[-1]) if len(p) >= 2 else nama


def penulis(w):
    out = []
    for a in w['authorships']:
        nm = singkat(a['author'].get('display_name') or '')
        out.append(nm + ('*' if a.get('is_corresponding') else ''))
    return ', '.join(x for x in out if x.strip('*'))


def terbitan(w):
    src = ((w.get('primary_location') or {}).get('source') or {}).get('display_name') or ''
    b = w.get('biblio') or {}
    vol, iss = b.get('volume'), b.get('issue')
    fp, lp = b.get('first_page'), b.get('last_page')
    bag = []
    if vol:
        bag.append(f'{vol}({iss})' if iss else str(vol))
    if fp:
        bag.append(f'{fp}-{lp}' if lp and lp != fp else str(fp))
    baris = ', '.join([x for x in [src] + bag if x])
    return re.sub(r'\b(\w+)-(\1)\b', r'\1', baris)


def rapikan(w):
    doi = (w.get('doi') or '').replace('https://doi.org/', '')
    tgl = w.get('publication_date') or (f"{w['publication_year']}-01-01" if w['publication_year'] else '')
    return {
        'id': w['id'].split('/')[-1],
        't': w['publication_year'],
        'tgl': tgl,
        'jenis': w['type'],
        'p': penulis(w),
        'j': (w['title'] or '').strip().rstrip('.'),
        'v': terbitan(w),
        'd': doi,
        's': w['cited_by_count'],
    }


def kunci_urut(x):
    return (-(x['t'] or 0), x['j'].lower())


def baca_lama():
    """Daftar id dari arsip sebelumnya. Kosong = belum ada pembanding."""
    if not os.path.exists(ARSIP):
        return None
    try:
        return {x['id'] for x in json.load(open(ARSIP, encoding='utf-8'))}
    except Exception:
        return None


def main():
    karya = [rapikan(w) for w in semua_karya() if not w.get('is_retracted')]

    # buang duplikat judul+tahun (OpenAlex kadang mencatat dua kali)
    lihat, bersih = set(), []
    for x in karya:
        k = (x['j'].lower()[:90], x['t'])
        if k in lihat:
            continue
        lihat.add(k)
        bersih.append(x)

    artikel = sorted([x for x in bersih if x['jenis'] in ('article', 'review', 'preprint')], key=kunci_urut)
    prosiding = sorted([x for x in bersih if x['jenis'] == 'conference-paper'], key=kunci_urut)
    bab = sorted([x for x in bersih if x['jenis'] == 'book-chapter'], key=kunci_urut)
    lain = sorted([x for x in bersih if x['jenis'] not in
                   ('article', 'review', 'preprint', 'conference-paper', 'book-chapter')], key=kunci_urut)
    terpilih = sorted([x for x in bersih if x['jenis'] in ('article', 'review')],
                      key=lambda x: -x['s'])[:12]

    # beranda: 9 karya terbaru menurut tanggal terbit
    terbaru = sorted([x for x in bersih if x['tgl']], key=lambda x: x['tgl'], reverse=True)[:9]

    lama = baca_lama()
    baru = [] if lama is None else [x for x in bersih if x['id'] not in lama]

    sitasi = sum(x['s'] for x in bersih)
    urut = sorted((x['s'] for x in bersih), reverse=True)
    h = max([i for i, c in enumerate(urut, 1) if c >= i], default=0)

    data = {'terpilih': terpilih, 'artikel': artikel, 'prosiding': prosiding,
            'bab': bab, 'lain': lain, 'terbaru': terbaru,
            'meta': {'diambil': __import__('datetime').date.today().isoformat(),
                     'penulis': PENULIS, 'jumlah': len(bersih),
                     'sitasi': sitasi, 'h': h,
                     'terbit_terakhir': max([x['t'] for x in bersih if x['t']], default=0)}}

    os.makedirs(os.path.dirname(ARSIP), exist_ok=True)
    with open(ARSIP, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(bersih, f, ensure_ascii=False, indent=1)

    with open(KELUAR, 'w', encoding='utf-8', newline='\n') as f:
        f.write('window.KARYA = ' + json.dumps(data, ensure_ascii=False, indent=1) + ';\n')

    jurnal = Counter()
    for x in bersih:
        if x['v']:
            jurnal[x['v'].split(',')[0]] += 1

    print(f"total {len(bersih)} | artikel {len(artikel)} | prosiding {len(prosiding)} "
          f"| bab {len(bab)} | lain {len(lain)} | sitasi {sum(x['s'] for x in bersih)}")
    print(f"BARU: {len(baru)}" + ("  (arsip awal dibuat, belum ada pembanding)" if lama is None else ""))
    for x in baru[:10]:
        print(f"  + {x['t']} {x['j'][:90]}")
    print('jurnal terbanyak:', jurnal.most_common(5))

    # tanda untuk pesan commit workflow
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as f:
            f.write(f'baru={len(baru)}\n')
            f.write(f'total={len(bersih)}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
