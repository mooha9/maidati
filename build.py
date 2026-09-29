#!/usr/bin/env python3
"""يبني نسخة مستقلة (PWA) من قصاصة الـArtifact في src/app.html."""
import pathlib, re, json, zlib, struct, argparse, hashlib

ROOT = pathlib.Path(__file__).parent
ap = argparse.ArgumentParser(); ap.add_argument("--env", default="production", choices=["production","staging"]); ap.add_argument("--out", default=str(ROOT / "public"))
A = ap.parse_args(); ENV = A.env
PUB = pathlib.Path(A.out); PUB.mkdir(parents=True, exist_ok=True)
frag = (ROOT / "src/app.html").read_text(encoding="utf-8")

name = re.search(r"<title>(.*?)</title>", frag).group(1)
title = name + (" · تجريبي" if ENV == "staging" else "")
fonts = re.findall(r'<link rel="(?:preconnect|stylesheet)"[^>]*>', frag)
style = re.search(r"<style>.*?</style>", frag, re.S).group(0)
body = frag[frag.index('<div class="app"'):]
DESC = "نظامك الغذائي في جيبك: وجبة الآن، فاحص الأطعمة، وصفات ملتزمة بالقواعد، وتذكير بالمواعيد."
ver = hashlib.sha1(frag.encode()).hexdigest()[:10]

html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{DESC}">
<meta name="theme-color" content="#F1F4EC" media="(prefers-color-scheme: light)">
<meta name="theme-color" content="#0F1510" media="(prefers-color-scheme: dark)">
<meta name="color-scheme" content="light dark">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{name}">
<meta name="mobile-web-app-capable" content="yes">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{DESC}">
<meta property="og:locale" content="ar_SA">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="manifest" href="manifest.webmanifest">
<script>window.MAIDATI={{env:"{ENV}"}}</script>
<style>:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0}}[hidden]{{display:none!important}}img{{max-width:100%}}</style>
{chr(10).join(fonts)}
{style}
</head>
<body>
{body}
<script>if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js').catch(()=>{{}});</script>
</body>
</html>
"""
(PUB / "index.html").write_text(html, encoding="utf-8")

(PUB / "manifest.webmanifest").write_text(json.dumps({
  "name": title, "short_name": name, "description": DESC, "lang": "ar", "dir": "rtl",
  "start_url": "./", "scope": "./", "display": "standalone",
  "background_color": "#F1F4EC", "theme_color": "#3E5E29",
  "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}]
}, ensure_ascii=False, indent=1), encoding="utf-8")

# عامل الخدمة: الشبكة أولاً ثم النسخة المحفوظة، ليعمل التطبيق بدون إنترنت
(PUB / "sw.js").write_text(f"""const C='maidati-{ENV}-{ver}';
self.addEventListener('install',e=>{{e.waitUntil(caches.open(C).then(c=>c.addAll(['./','index.html','manifest.webmanifest','icon-192.png'])));self.skipWaiting()}});
self.addEventListener('activate',e=>{{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==C).map(k=>caches.delete(k)))));self.clients.claim()}});
self.addEventListener('fetch',e=>{{if(e.request.method!=='GET')return;e.respondWith(fetch(e.request).then(r=>{{if(r.ok&&(r.type==='basic'||r.type==='cors')){{const cp=r.clone();caches.open(C).then(c=>c.put(e.request,cp))}}return r}}).catch(()=>caches.match(e.request).then(m=>m||caches.match('index.html'))))}});
self.addEventListener('notificationclick',e=>{{e.notification.close();e.waitUntil(self.clients.matchAll({{type:'window'}}).then(cs=>cs.length?cs[0].focus():self.clients.openWindow('./')))}});
""", encoding="utf-8")

# الأيقونة: زيتونة بيضاء مائلة على أخضر الزيتون
OL, WH = (0x3E,0x5E,0x29), (0xFF,0xFF,0xFF)
def png(path, n):
    import math
    out = bytearray(n*n*4); c = n/2; a, b = n*0.20, n*0.28; th = math.radians(-28)
    for y in range(n):
        for x in range(n):
            acc = [0.0,0.0,0.0]
            for sx in (.25,.75):
                for sy in (.25,.75):
                    px, py = x+sx-c, y+sy-c*1.06
                    u = px*math.cos(th)+py*math.sin(th); v = -px*math.sin(th)+py*math.cos(th)
                    col = WH if (u/a)**2+(v/b)**2 <= 1 else OL
                    # ساق صغيرة
                    if abs((x+sx)-(c+n*0.13+(c*0.62-(y+sy))*0.55)) < n*0.022 and n*0.16 < y+sy < n*0.30: col = WH
                    for i in range(3): acc[i] += col[i]/4
            o = (y*n+x)*4; out[o:o+4] = bytes([int(acc[0]),int(acc[1]),int(acc[2]),255])
    raw = b"".join(b"\x00"+out[y*n*4:(y+1)*n*4] for y in range(n))
    ch = lambda t,d: struct.pack(">I",len(d))+t+d+struct.pack(">I",zlib.crc32(t+d)&0xffffffff)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+ch(b"IHDR",struct.pack(">IIBBBBB",n,n,8,6,0,0,0))+ch(b"IDAT",zlib.compress(raw,9))+ch(b"IEND",b""))
for n, f in ((192,"icon-192.png"),(512,"icon-512.png"),(180,"apple-touch-icon.png")): png(PUB/f, n)
(PUB / "icon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#3E5E29"/><ellipse cx="32" cy="36" rx="13" ry="18" fill="#fff" transform="rotate(-28 32 36)"/><path d="M38 14c4-5 10-6 14-5" stroke="#fff" stroke-width="3.5" fill="none" stroke-linecap="round"/></svg>', encoding="utf-8")
print("built", ENV, "->", PUB)
