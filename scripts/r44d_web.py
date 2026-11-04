#!/usr/bin/env python3
"""R44-d research helper: Yahoo/Bing search + page fetch + Wikipedia/S2 API. No keys, all timeouts short."""
import sys, re, json, html, urllib.request, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
OUT = "/home/z/my-project/scripts/r44d_tmp"

def _get(url, timeout=22):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")

def striphtml(s):
    s = re.sub(r"(?is)<(script|style|head|noscript)[^>]*>.*?</\1>", " ", s)
    s = re.sub(r"(?s)<[^>]+>", "\n", s)
    s = html.unescape(s)
    s = re.sub(r"[ \t\r]+", " ", s)
    return re.sub(r"\n\s*\n+", "\n", s)

def yahoo(q, count=12):
    out, seen = [], set()
    for start in (1, 11):
        try:
            raw = _get("https://search.yahoo.com/search?p=%s&n=10&b=%d" % (urllib.parse.quote(q), start))
        except Exception as e:
            print("YAHOO_ERR", e); break
        for m in re.finditer(r'RU=(https?%3a%2f%2f[^"]+?)%2fRK=', raw):
            u = urllib.parse.unquote(m.group(1))
            dom = re.sub(r"^https?://", "", u).split("/")[0]
            if "yahoo" in dom or "bing.com" in dom or dom in seen:
                continue
            seen.add(dom); out.append(u)
            if len(out) >= count:
                return out
    return out

def bing(q, count=10):
    try:
        raw = _get("https://www.bing.com/search?q=%s&count=12&setlang=en" % urllib.parse.quote(q))
    except Exception as e:
        print("BING_ERR", e); return []
    items = re.findall(r'(?is)<li class="b_algo".*?<h2[^>]*><a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw)
    return [(u, striphtml(t).strip()[:110]) for u, t in items[:count]]

def wiki(title, name, chars=6000, full=True):
    ex = "explaintext=1" if full else "explaintext=1&exintro=1"
    d = json.loads(_get("https://en.wikipedia.org/w/api.php?action=query&prop=extracts&%s&format=json&redirects=1&titles=%s" % (ex, urllib.parse.quote(title))))
    p = list(d["query"]["pages"].values())[0]
    txt = (p.get("extract") or "")[:chars]
    open("%s/%s.wiki" % (OUT, name), "w").write(txt)
    print("=== WIKI %s: %s (%d chars) ===" % (name, p.get("title"), len(txt)))

def fetch(url, name, chars=14000, to=28):
    try:
        raw = _get(url, to)
    except Exception as e:
        print("FETCH_FAIL %s: %s" % (name, e)); return ""
    txt = striphtml(raw)
    open("%s/%s.html.txt" % (OUT, name), "w").write(txt)
    print("=== FETCH %s (%d chars) ===" % (name, len(txt)))
    return txt[:chars]

def s2(query, n=5):
    u = "https://api.semanticscholar.org/graph/v1/paper/search?query=%s&limit=%d&fields=title,year,abstract,venue,externalIds,citationCount" % (urllib.parse.quote(query), n)
    try:
        d = json.loads(_get(u))
    except Exception as e:
        print("S2_ERR", e); return
    for p in d.get("data", []):
        ab = (p.get("abstract") or "")[:500].replace("\n", " ")
        print("- %s (%s, %s) cites=%s\n  %s\n  %s" % (p.get("title"), p.get("year"), p.get("venue"), p.get("citationCount"), (p.get("externalIds") or {}).get("DOI", ""), ab))


def news(q, n=12):
    u = "https://news.google.com/rss/search?q=%s&hl=en-US&gl=US&ceid=US:en" % urllib.parse.quote(q)
    try:
        raw = _get(u)
    except Exception as e:
        print("NEWS_ERR", e); return
    items = re.findall(r"<item>(.*?)</item>", raw, re.S)[:n]
    for it in items:
        t = re.search(r"<title>(.*?)</title>", it, re.S)
        d = re.search(r"<pubDate>(.*?)</pubDate>", it)
        l = re.search(r"<link>(.*?)</link>", it)
        src = re.search(r"<source[^>]*>(.*?)</source>", it)
        print("* [%s] %s" % (d.group(1) if d else "?", html.unescape(t.group(1)) if t else "?"))
        print("   src=%s %s" % (html.unescape(src.group(1)) if src else "?", (l.group(1) if l else "")[:160]))

def xref(q, n=6):
    u = "https://api.crossref.org/works?query=%s&rows=%d&mailto=r44d.research@example.org&select=title,author,issued,container-title,DOI,abstract,URL" % (urllib.parse.quote(q), n)
    try:
        d = json.loads(_get(u))
    except Exception as e:
        print("XREF_ERR", e); return
    for it in d.get("message", {}).get("items", []):
        yr = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        ti = (it.get("title") or ["?"])[0][:140]
        ct = (it.get("container-title") or ["?"])[0][:80]
        ab = re.sub(r"<[^>]+>", " ", it.get("abstract") or "")[:420]
        print("- %s (%s) %s | DOI:%s\n  %s" % (ti, yr, ct, it.get("DOI",""), ab.strip()))

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "search":
        for u in yahoo(" ".join(sys.argv[2:])):
            print(u)
        print("--- bing alt ---")
        for u, t in bing(" ".join(sys.argv[2:])):
            print(u, "|", t)
    elif cmd == "fetch":
        fetch(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 14000, int(sys.argv[5]) if len(sys.argv) > 5 else 28)
    elif cmd == "wiki":
        wiki(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 6000, (len(sys.argv) > 5 and sys.argv[5] == "full"))
    elif cmd == "news":
        news(" ".join(sys.argv[2:]))
    elif cmd == "xref":
        xref(" ".join(sys.argv[2:]))
    elif cmd == "s2":
        s2(" ".join(sys.argv[2:]))
