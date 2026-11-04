#!/usr/bin/env python3
"""r46c search helper: Yahoo + Bing web search, parse title/url/snippet."""
import sys, re, urllib.request, urllib.parse, html

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "ignore")

def strip(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()

def yahoo(q, n=8):
    h = fetch("https://search.yahoo.com/search?p=" + urllib.parse.quote(q))
    out = []
    # results: <div class="compTitle ..."><h3 class="title"><a href="RURL">TITLE</a></h3></div> ... <div class="compText"><p>SNIP</p>
    for m in re.finditer(r'class="compTitle[^"]*"[^>]*>.*?<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', h, re.S):
        u, t = m.group(1), strip(m.group(2))
        tail = h[m.end():m.end()+3000]
        sm = re.search(r'class="compText[^"]*"[^>]*>.*?<p[^>]*>(.*?)</p>', tail, re.S)
        snip = strip(sm.group(1)) if sm else ""
        mm = re.search(r'RU=([^/]+)', u)
        if mm:
            u = urllib.parse.unquote(mm.group(1))
        out.append((t, u, snip[:300]))
    return out[:n]

def bing(q, n=8):
    h = fetch("https://www.bing.com/search?q=" + urllib.parse.quote(q) + "&count=15")
    out = []
    for m in re.finditer(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>\s*</h2>(.*?)(?=<h2|<li class="b_algo|$)', h, re.S):
        u, t, rest = m.group(1), strip(m.group(2)), m.group(3)
        sm = re.search(r'<p[^>]*>(.*?)</p>', rest, re.S)
        snip = strip(sm.group(1)) if sm else ""
        if u.startswith("http"):
            out.append((t, u, snip[:300]))
    return out[:n]

if __name__ == "__main__":
    eng, q = sys.argv[1], sys.argv[2]
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    try:
        res = yahoo(q, n) if eng == "y" else bing(q, n)
    except Exception as e:
        print("ERROR", e); sys.exit(1)
    if not res:
        print("NO_RESULTS")
    for t, u, s in res:
        print("T:", t)
        print("U:", u)
        print("S:", s)
        print("--")
