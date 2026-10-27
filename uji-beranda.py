"""Uji beranda baru: struktur, kontras, luberan, tautan. CDP headless."""
import json, time, urllib.request, functools, http.server, threading, subprocess, sys
import websocket

ROOT = r'D:\Website\Profil-Ganjar'
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
PORT, CDP = 8823, 9363
PROF = r'C:\Users\ASUS\AppData\Local\Temp\cdp-beranda'

class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), functools.partial(Q, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()

proc = subprocess.Popen([CHROME, '--headless=new', '--disable-gpu', '--no-sandbox',
    f'--remote-debugging-port={CDP}', '--remote-allow-origins=*',
    f'--user-data-dir={PROF}', '--window-size=1280,1000', 'about:blank'],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

ws_url = None
for _ in range(60):
    try:
        for t in json.load(urllib.request.urlopen(f'http://127.0.0.1:{CDP}/json', timeout=2)):
            if t['type'] == 'page':
                ws_url = t['webSocketDebuggerUrl']; break
    except Exception:
        pass
    if ws_url: break
    time.sleep(0.5)
assert ws_url, 'CDP tidak siap'

ws = websocket.create_connection(ws_url, timeout=40, suppress_origin=True)
i = [0]
def cmd(m, **p):
    i[0] += 1
    ws.send(json.dumps({'id': i[0], 'method': m, 'params': p}))
    while True:
        r = json.loads(ws.recv())
        if r.get('id') == i[0]:
            if 'error' in r: raise RuntimeError(r['error'])
            return r.get('result', {})
def ev(x):
    r = cmd('Runtime.evaluate', expression=x, returnByValue=True, awaitPromise=True)
    res = r.get('result', {})
    if res.get('subtype') == 'error':
        raise RuntimeError(res.get('description'))
    return res.get('value')

cmd('Page.enable'); cmd('Runtime.enable')
cmd('Network.enable'); cmd('Network.setCacheDisabled', cacheDisabled=True)

LULUS = gagal = 0
def cek(n, ok, info=''):
    global LULUS, gagal
    if ok: LULUS += 1
    else: gagal += 1
    print(('LULUS ' if ok else 'GAGAL ') + n + (f' | {info}' if info != '' else ''))

def buka(f, lebar=1280):
    cmd('Emulation.setDeviceMetricsOverride', width=lebar, height=1000,
        deviceScaleFactor=1, mobile=lebar < 700)
    cmd('Page.navigate', url=f'http://127.0.0.1:{PORT}/{f}')
    time.sleep(0.4)
    for _ in range(40):
        if ev("document.readyState==='complete' && document.styleSheets.length>0"
              " && !!document.querySelector('nav a.ini')"):
            break
        time.sleep(0.15)
    time.sleep(0.5)


def lum(h):
    h = h.lstrip('#'); r, g, b = (int(h[k:k+2], 16)/255 for k in (0, 2, 4))
    f = lambda c: c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
    return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)
def cr(a, b):
    la, lb = lum(a), lum(b); hi, lo = max(la, lb), min(la, lb)
    return round((hi+0.05)/(lo+0.05), 2)

print('\n=== BERANDA ===')
buka('index.html')
cek('tanpa galat JS', ev("window.__err||null") is None)
cek('judul tab', ev("document.title") == 'Ganjar Fadillah — Universitas Islam Indonesia',
    ev("document.title"))
cek('satu h1', ev("document.querySelectorAll('h1').length") == 1)

# angka ringkas
stat = ev("[...document.querySelectorAll('#statistik .angka')].map(e=>e.textContent)")
cek('angka 30/24/27/2026', stat == ['30', '24', '27', '2026'], stat)

# pilar
cek('3 pilar', ev("document.querySelectorAll('.pilar-sel').length") == 3)
cek('pilar punya judul + uraian',
    ev("[...document.querySelectorAll('.pilar-sel')].every(s=>s.querySelector('h2')&&s.querySelector('p'))"))

# sorotan
cek('sorotan: 3 terbitan', ev("document.querySelectorAll('.sorotan article').length") == 3)
cek('sorotan: utama punya DOI',
    ev("!!document.querySelector('.sorotan .utama h2 a[href^=\"https://doi.org/\"]')"))
cek('sorotan: 3 tautan DOI',
    ev("document.querySelectorAll('.sorotan a[href^=\"https://doi.org/\"]').length") == 3,
    ev("document.querySelectorAll('.sorotan a[href^=\"https://doi.org/\"]').length"))
cek('sorotan: 2026 disebut', '2026' in ev("document.querySelector('.sorotan-kepala').innerText"))
# DOI benar, dari data.js — bukan dikarang
doi_sorotan = ev("[...document.querySelectorAll('.sorotan a[href^=\"https://doi.org/\"]')].map(a=>a.href.replace('https://doi.org/',''))")
doi_data = ev("(()=>{const s=new Set();(KARYA.terbaru||[]).forEach(x=>x.d&&s.add(x.d));"
              "return [...s]})()")
cek('semua DOI sorotan ada di data.js',
    all(d in doi_data for d in doi_sorotan), doi_sorotan)

# feed
n = ev("document.querySelectorAll('#feed li').length")
cek('feed 11 baris (8 terbit + 3 rekognisi)', n == 11, n)
cek('feed: 8 tautan DOI', ev("document.querySelectorAll('#feed a[href^=\"https://doi.org/\"]').length") == 8)
cek('feed: 3 rekognisi', ev("document.querySelectorAll('#feed li.kegiatan').length") == 3)

# rahasia
bad = ev("document.body.innerText.match(/\\d{1,3}\\.\\d{3}\\.\\d{3}/g)")
cek('tanpa nominal dana', not bad, bad)
cek('tanpa nomor kontrak', not ev("/\\d{3}\\/[A-Z]/.test(document.body.innerText)"))
cek('tanpa kata OpenAlex', 'openalex' not in ev("document.body.innerText.toLowerCase()"))
cek('tanpa "Selamat datang"', 'selamat datang' not in ev("document.body.innerText.toLowerCase()"))

# nav
cek('4 tautan nav', ev("document.querySelectorAll('nav .tautan a').length") == 4)
cek('nav aktif ditandai', ev("document.querySelector('nav a.ini').textContent") == 'Beranda')

# kontras pita sorotan (emas #F7DE00 di navy-tua #04224F)
bg = ev("getComputedStyle(document.querySelector('.sorotan')).backgroundColor")
cek('latar sorotan navy tua', 'rgb(4, 34, 79)' in bg, bg)
cke = cr('F7DE00', '04224F')
cek('kontras emas/navy-tua >= 4.5', cke >= 4.5, cke)
cpen = cr('A9BAD6', '04224F')
cek('kontras penulis/navy-tua >= 4.5', cpen >= 4.5, cpen)
ctanda = cr('04224F', 'F7DE00')
cek('kontras label emas >= 4.5', ctanda >= 4.5, ctanda)

# tanpa efek terlarang
cek('tanpa backdrop-filter di .sorotan/.pilar',
    ev("(()=>{let h=0;document.querySelectorAll('.sorotan,.sorotan *,.pilar,.pilar *')"
       ".forEach(e=>{const s=getComputedStyle(e);if(s.backdropFilter&&s.backdropFilter!=='none')h++});return h})()") == 0)
cek('tanpa bayangan di pilar/sorotan',
    ev("(()=>{let h=0;document.querySelectorAll('.sorotan article,.pilar-sel')"
       ".forEach(e=>{const s=getComputedStyle(e);if(s.boxShadow&&s.boxShadow!=='none')h++});return h})()") == 0)

# luberan 4 lebar
print('\n=== LUBERAN ===')
for w in (360, 390, 768, 1280):
    buka('index.html', w)
    sc = ev("document.documentElement.scrollWidth")
    cw = ev("document.documentElement.clientWidth")
    cek(f'{w}px tidak meluber', sc <= cw + 1, f'scroll={sc} client={cw}')
    kecil = ev("(()=>{const b=[...document.querySelectorAll('a,button,input')]"
               ".filter(e=>{const r=e.getBoundingClientRect();return r.width>0&&(r.height<44||r.width<44)});"
               "return b.map(e=>(e.textContent||'').trim().slice(0,30)+':'+Math.round(e.getBoundingClientRect().height))})()")
    if w <= 640:
        cek(f'{w}px target >= 44px', not kecil, kecil[:4])

print('\n=== HALAMAN LAIN ===')
for f, tanda in (('publikasi.html', '30'), ('profil.html', '27'), ('akses.html', 'ganjar.fadillah@uii.ac.id')):
    buka(f)
    cek(f'{f}: tanpa galat JS', ev("window.__err||null") is None)
    cek(f'{f}: CSS baru termuat', ev("document.styleSheets.length>0"))
    buka(f, 360)
    sc = ev("document.documentElement.scrollWidth"); cw = ev("document.documentElement.clientWidth")
    cek(f'{f}: 360px tidak meluber', sc <= cw + 1, f'scroll={sc} client={cw}')

print('\n=== PENCARIAN ===')
buka('publikasi.html')
def ketik(s):
    ev('(()=>{const c=document.getElementById("cari");c.value=%s;'
       'c.dispatchEvent(new Event("input",{bubbles:true}));})()' % json.dumps(s))
    time.sleep(0.25)          # debounce 60 ms di halaman; beri ruang
    return ev('(()=>{const li=[...document.querySelectorAll('
              '"#q1 .daftar li,#q2 .daftar li,#prosiding .daftar li")];'
              'const kg=[...document.querySelectorAll("#pimpin .baris,#hibah .baris")];'
              'return [li.filter(e=>!e.hidden).length, kg.filter(e=>!e.hidden).length]})()')

# tiap kunci: [harapan karya, harapan kegiatan]
HARAP = {
    'sensor': [11, 6], 'bisphenol': [6, 3], 'nikel': [0, 2], '2026': [8, 5],
    'Q1': [24, 0], 'Q2': [3, 0], 'fadillah': [30, 0], 'air': [0, 6],
    'mikroplastik': [0, 3], 'ion transfer': [0, 5], 'hibah': [0, 1],
    'penelitian fundamental': [0, 4], 'kemitraan': [0, 0], 'xyz': [0, 0],
}
for k, (hk, hg) in HARAP.items():
    hasil = ketik(k); time.sleep(0.25)
    cek(f'cari "{k}" -> {hk} karya + {hg} kegiatan', hasil == [hk, hg], f'dapat {hasil}')

ketik('xyz'); time.sleep(0.2)
cek('tanpa hasil: pesan kosong tampil', ev('!document.getElementById("nir").hidden'))
cek('tanpa hasil: hitungan dikosongkan', ev('document.getElementById("ket").textContent') == '')
ev('document.getElementById("ulang").click()'); time.sleep(0.2)
cek('tombol "Tampilkan semua" memulihkan 30 karya',
    ketik('') == [30, 0] or ev('document.getElementById("ket").textContent') == '30 karya',
    ev('document.getElementById("ket").textContent'))
ketik('sensor'); time.sleep(0.2)
ev('document.getElementById("bersih").click()'); time.sleep(0.2)
cek('tombol bersih mengosongkan input', ev('document.getElementById("cari").value') == '')
cek('tombol bersih memulihkan daftar', ev(
    '[...document.querySelectorAll("#q1 .daftar li,#q2 .daftar li,#prosiding .daftar li")]'
    '.filter(e=>!e.hidden).length') == 30)
cek('fokus kembali ke kotak cari', ev('document.activeElement.id') == 'cari')
ketik('sensor'); time.sleep(0.2)
cmd('Input.dispatchKeyEvent', type='keyDown', key='Escape', code='Escape', windowsVirtualKeyCode=27)
cmd('Input.dispatchKeyEvent', type='keyUp', key='Escape', code='Escape', windowsVirtualKeyCode=27)
time.sleep(0.2)
cek('Escape mengosongkan pencarian', ev('document.getElementById("cari").value') == '')
buka('publikasi.html', 390)
cek('390px kotak cari >= 44px', ev(
    'Math.round(document.getElementById("cari").getBoundingClientRect().height)') >= 44)

print('\n=== RAHASIA DI FOLDER SITUS ===')
# Pola generik: bentuk nominal rupiah dan bentuk nomor kontrak. Jangan pakai
# angka aslinya di sini — berkas ini ikut terunggah ke repo publik.
import re, os as _os
POLA = [(re.compile(rb'\d{1,3}\.\d{3}\.\d{3}'), 'nominal rupiah'),
        (re.compile(rb'\d{3}/[A-Z][A-Za-z.]'), 'nomor kontrak/SK')]
bocor, diperiksa = [], 0
for akar, _d, berkas in _os.walk(ROOT):
    if '.git' in akar:
        continue
    for b in berkas:
        jal = _os.path.join(akar, b)
        rel = _os.path.relpath(jal, ROOT).replace('\\', '/')
        if b.endswith(('.jpg', '.png', '.ico')):
            continue
        diperiksa += 1
        try:
            isi = open(jal, 'rb').read()
        except Exception:
            continue
        for pola, nama in POLA:
            m = pola.search(isi)
            if m:
                bocor.append(f'{rel}: {nama} -> {m.group(0).decode(errors="replace")}')
cek('seluruh folder situs bebas nominal/kontrak', not bocor, bocor)
cek('folder situs diperiksa', diperiksa > 0, f'{diperiksa} berkas teks')
cek('tidak ada folder data/ di dalam situs', not _os.path.isdir(f'{ROOT}/data'))
cek('tidak ada berkas .docx di dalam situs',
    not any(b.endswith('.docx') for _a, _b, _c in _os.walk(ROOT) for b in _c
            if '.git' not in _a))

proc.kill()
print(f'\nLULUS {LULUS} · GAGAL {gagal}')
sys.exit(1 if gagal else 0)
