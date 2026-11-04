#!/usr/bin/env python3
"""R44-a research helper: Bing/Yahoo search + page fetch (plain curl, no keys)."""
import sys, re, html, time, subprocess, urllib.request, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def http_get(url):
    r = subprocess.run(["curl", "-sL", "-m", "25", "-A", UA, "-H", "Accept-Language: en-US,en;q=0.9", url],
                       capture_output=True)
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
    if not blocks:
        blocks = re.findall(r'(?is)<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>(.*?)(?=class="result__a"|</div>\s*</div>\s*</div>|$)', raw)
    for u, t, rest in blocks[:8]:
        if "duckduckgo.com/y.js" in u or "uddg=" not in u and "duckduckgo" in u:
            continue
        m = re.search(r'uddg=([^&]+)', u)
        if m:
            u = urllib.parse.unquote(m.group(1))
        m2 = re.search(r'(?is)class="result__snippet"[^>]*>(.*?)</a>', rest)
        snip = striphtml(m2.group(1)).strip()[:300] if m2 else ""
        out.append((striphtml(t).strip(), u, snip))
    return out

def yahoo(q):
    out, seen = [], set()
    url = "https://search.yahoo.com/search?p=%s&n=10" % urllib.parse.quote(q)
    raw = http_get(url)
    for h in re.findall(r'href="https://r\.search\.yahoo\.com/[^"]+"', raw):
        m = re.search(r'RU=([^/"]+)/RK=', h)
        if not m:
            continue
        u = urllib.parse.unquote(m.group(1))
        dom = re.sub(r"^https?://", "", u).split("/")[0]
        if "yahoo" in dom or dom in seen:
            continue
        seen.add(dom)
        out.append(u)
        if len(out) >= 8:
            break
    return out

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "search":  # r44a_search.py search "q1;;q2;;q3"
        for qi, q in enumerate(sys.argv[2].split(";;")):
            res = ddg(q)
            eng = "DDG"
            if not res:
                res = [(u, u, "") for u in yahoo(q)]; eng = "YAHOO"
            print(f"=== [{qi+1}] {eng}: {q} | {len(res)} hits ===")
            if not res:
                ys = yahoo(q)
                print(f"  (empty, yahoo {len(ys)} urls)")
                for u in ys[:6]:
                    print("   ", u)
            for t, u, s in res:
                print(f"- {t}\n  {u}\n  {s}")
            time.sleep(1)
            print()
    elif cmd == "fetch":  # r44a_search.py fetch URL [chars]
        txt = striphtml(http_get(sys.argv[2]))
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 9000
        print(txt[:n])
