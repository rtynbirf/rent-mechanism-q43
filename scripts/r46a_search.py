#!/usr/bin/env python3
"""R46-a search helper: DDG -> Bing -> Mojeek fallback, plain curl, no keys."""
import sys, re, html, time, subprocess, urllib.request, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def http_get(url):
    r = subprocess.run(["curl", "-sL", "-m", "25", "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9", url], capture_output=True)
    return r.stdout.decode("utf-8", "ignore")

def striphtml(s):
    s = re.sub(r"<script.*?</script>|<style.*?</style>", " ", s, flags=re.S | re.I)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s)

def ddg(q):
    url = "https://html.duckduckgo.com/html/?q=%s" % urllib.parse.quote(q)
    raw = http_get(url)
    out = []
    blocks = re.findall(r'(?is)<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>(.*?)</a>(.*?)(?=<a rel="nofollow" class="result__a"|<div class="nav-link"|$)', raw)
    for u, t, rest in blocks[:8]:
        m = re.search(r'uddg=([^&]+)', u)
        if m:
            u = urllib.parse.unquote(m.group(1))
        m2 = re.search(r'(?is)class="result__snippet"[^>]*>(.*?)</a>', rest)
        snip = striphtml(m2.group(1)).strip()[:300] if m2 else ""
        out.append((striphtml(t).strip(), u, snip))
    return out

def bing(q):
    url = "https://www.bing.com/search?q=%s&count=10" % urllib.parse.quote(q)
    raw = http_get(url)
    out = []
    for m in re.finditer(r'(?is)<li class="b_algo".*?<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>(.*?)</li>', raw):
        u, t, rest = m.group(1), m.group(2), m.group(3)
        sn = re.search(r'(?is)<p[^>]*>(.*?)</p>', rest)
        out.append((striphtml(t).strip(), u, striphtml(sn.group(1)).strip()[:300] if sn else ""))
    return out

def mojeek(q):
    url = "https://www.mojeek.com/search?q=%s" % urllib.parse.quote(q)
    raw = http_get(url)
    out = []
    for m in re.finditer(r'(?is)<a class="ob" href="([^"]+)"[^>]*>(.*?)</a>.*?(?:<p class="s">(.*?)</p>|</h2>)', raw):
        u, t, rest = m.group(1), m.group(2), m.group(3) or ""
        out.append((striphtml(t).strip(), u, striphtml(rest)[:300]))
    if not out:
        for m in re.finditer(r'(?is)<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>(.*?)</', raw):
            out.append((striphtml(m.group(2)).strip(), m.group(1), striphtml(m.group(3))[:250]))
    return out

if __name__ == "__main__":
    for qi, q in enumerate(sys.argv[1].split(";;")):
        res, eng = ddg(q), "DDG"
        if not res:
            res, eng = bing(q), "BING"
        if not res:
            res, eng = mojeek(q), "MOJEEK"
        print(f"=== [{qi+1}] {eng}: {q} | {len(res)} hits ===")
        for t, u, s in res[:7]:
            print(f"- {t}\n  {u}\n  {s}")
        time.sleep(1)
        print()
