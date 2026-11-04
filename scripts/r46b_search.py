#!/usr/bin/env python3
"""R46-b search runner: Google News RSS + Bing + Mojeek + DDG-lite fallbacks.
Usage: r46b_search.py <TAG> <mode:q> [mode:q ...]   modes: gnews|bing|mojeek|ddg
"""
import sys, re, html, urllib.request, urllib.parse

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}

def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def strip(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()

def gnews(q):
    body = get("https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en")
    items = re.findall(r"<item>(.*?)</item>", body, flags=re.S)[:8]
    n = 0
    for it in items:
        t = re.search(r"<title>(.*?)</title>", it, flags=re.S)
        l = re.search(r"<link>(.*?)</link>", it, flags=re.S)
        d = re.search(r"<pubDate>(.*?)</pubDate>", it, flags=re.S)
        s = re.search(r"<source[^>]*>(.*?)</source>", it, flags=re.S)
        if not t: continue
        print(f"  * {strip(t.group(1))[:150]}")
        print(f"    {strip(s.group(1)) if s else '?'} | {strip(d.group(1)) if d else '?'}")
        if l: print(f"    {l.group(1).strip()[:140]}")
        n += 1
    if n == 0:
        print(f"  [GNEWS no items, len={len(body)}]")

def bing(q):
    body = get("https://www.bing.com/search?q=" + urllib.parse.quote(q) + "&count=12")
    chunks = body.split("<h2")[1:]
    n = 0
    for ch in chunks[:8]:
        m = re.search(r"<a[^>]+href=\"(http[^\"]+)\"[^>]*>(.*?)</a>", ch, flags=re.S)
        if not m: continue
        u, t = m.group(1), strip(m.group(2))
        pm = re.search(r"<p[^>]*>(.*?)</p>", ch, flags=re.S)
        sn = strip(pm.group(1))[:300] if pm else ""
        print(f"  * {t[:110]}\n    {u[:135]}\n    {sn}")
        n += 1
    if n == 0:
        flat = re.sub(r"\s+", " ", strip(body))
        i = flat.find("results")
        print(f"  [BING no results parsed, len={len(body)}] RAW: {flat[max(0,i-80):i+220]}")

def mojeek(q):
    body = get("https://www.mojeek.com/search?q=" + urllib.parse.quote(q))
    items = re.findall(r"<a class=\"ob\" href=\"([^\"]+)\"[^>]*>(.*?)</a>", body, flags=re.S)
    snips = re.findall(r"<p class=\"s\">(.*?)</p>", body, flags=re.S)
    n = 0
    for i, (u, t) in enumerate(items[:8]):
        sn = strip(snips[i])[:280] if i < len(snips) else ""
        print(f"  * {strip(t)[:110]}\n    {u[:135]}\n    {sn}")
        n += 1
    if n == 0:
        print(f"  [MOJEEK no results parsed, len={len(body)}]")

def ddg(q):
    body = get("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q))
    items = re.findall(r"<a rel=\"nofollow\" class=\"result__a\" href=\"([^\"]+)\">(.*?)</a>", body, flags=re.S)
    snips = re.findall(r"class=\"result__snippet\"[^>]*>(.*?)</a>", body, flags=re.S)
    n = 0
    for i, (u, t) in enumerate(items[:8]):
        sn = strip(snips[i])[:280] if i < len(snips) else ""
        print(f"  * {strip(t)[:110]}\n    {u[:135]}\n    {sn}")
        n += 1
    if n == 0:
        print(f"  [DDG no results parsed, len={len(body)}]")

FNS = {"gnews": gnews, "bing": bing, "mojeek": mojeek, "ddg": ddg}

def main():
    tag, specs = sys.argv[1], sys.argv[2:]
    for sp in specs:
        mode, q = sp.split(":", 1)
        print(f"### {tag} [{mode}] :: {q}")
        try:
            FNS[mode](q)
        except Exception as e:
            print(f"  [{mode.upper()} ERR {type(e).__name__}: {str(e)[:70]}]")
        print()

if __name__ == "__main__":
    main()
