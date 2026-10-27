# Ekstrak tabel dari DRH (.docx) -> data/drh.json. Jalankan ulang bila DRH diperbarui.
import json, os, re, sys, zipfile, xml.etree.ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
# data/drh.json memuat nominal dana hibah dan nomor kontrak -> WAJIB di luar
# folder situs. Default: folder sebelah bernama "<situs>-privat".
SITUS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.environ.get('GANJAR_PRIVAT') or (SITUS + '-privat')

def sel(tc):
    bagian = []
    for p in tc.iter(W + 'p'):
        bagian.append(''.join(t.text or '' for t in p.iter(W + 't')))
    return re.sub(r'\s+', ' ', ' '.join(bagian)).strip()

def tabel(path):
    xml = zipfile.ZipFile(path).read('word/document.xml')
    akar = ET.fromstring(xml)
    hasil = []
    for tbl in akar.iter(W + 'tbl'):
        baris = [[sel(tc) for tc in tr.findall(W + 'tc')] for tr in tbl.findall(W + 'tr')]
        baris = [b for b in baris if any(b)]
        if baris:
            hasil.append(baris)
    return hasil

if __name__ == '__main__':
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if not src:
        sys.exit('pakai: python tools/ambil-drh.py <DRH.docx>')
    t = tabel(src)
    out = os.path.join(ROOT, 'data', 'drh.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(t, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{len(t)} tabel -> data/drh.json')
    for i, x in enumerate(t):
        print(f'  [{i}] {len(x)-1} baris | {x[0][0][:50]}')
