#!/usr/bin/env python3
# r44-b search runner v3 (final series S3): robust Bing chunk parser, Mojeek fallback
import sys, re, urllib.request, urllib.parse, html

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9"}

def get(url, timeout=28):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")

def strip(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()

def bing(q, out):
    body = get("https://www.bing.com/search?q=" + urllib.parse.quote(q) + "&count=12")
    chunks = body.split("<h2")[1:]
    n = 0
    for ch in chunks[:8]:
        m = re.search(r"<a[^>]+href=\"(http[^\"]+)\"[^>]*>(.*?)</a>", ch, flags=re.S)
        if not m:
            continue
        u, t = m.group(1), strip(m.group(2))
        pm = re.search(r"<p[^>]*>(.*?)</p>", ch, flags=re.S)
        sn = strip(pm.group(1))[:300] if pm else ""
        print(f"  * {t[:110]}\n    {u[:135]}\n    {sn}", file=out)
        n += 1
    if n == 0:
        print("  [BING no results parsed, len=%d]" % len(body), file=out)
        flat = re.sub(r"\s+", " ", strip(body))
        i = flat.find("results")
        print("  RAW:", flat[max(0,i-100):i+300], file=out)
    return n

def mojeek(q, out):
    body = get("https://www.mojeek.com/search?q=" + urllib.parse.quote(q))
    items = re.findall(r"<a class=\"ob\" href=\"([^\"]+)\"[^>]*>(.*?)</a>", body, flags=re.S)
    snips = re.findall(r"<p class=\"s\">(.*?)</p>", body, flags=re.S)
    n = 0
    for i, (u, t) in enumerate(items[:8]):
        sn = strip(snips[i])[:280] if i < len(snips) else ""
        print(f"  * {strip(t)[:110]}\n    {u[:135]}\n    {sn}", file=out)
        n += 1
    if n == 0:
        print("  [MOJEEK no results parsed, len=%d]" % len(body), file=out)
    return n

def one(q, out):
    try:
        if bing(q, out) > 0: return
    except Exception as e:
        print(f"  [BING ERR {type(e).__name__}: {str(e)[:50]}]", file=out)
    try:
        mojeek(q, out)
    except Exception as e:
        print(f"  [MOJEEK ERR {type(e).__name__}: {str(e)[:50]}]", file=out)

def main():
    tag, qs = sys.argv[1], sys.argv[2:]
    for q in qs:
        print(f"### {tag} :: {q}")
        one(q, sys.stdout)

if __name__ == "__main__":
    main()
