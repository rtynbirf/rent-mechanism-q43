#!/usr/bin/env python3
"""R44-e: Bing search + Wikipedia extract helper (curl-free urllib, plain GET)."""
import sys, re, html, subprocess, json, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def curl(url, out):
    r = subprocess.run(["curl", "-sS", "-m", "25", "-A", UA, url, "-o", out], capture_output=True, text=True)
    return r.returncode

def strip_html(raw):
    raw = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", raw)
    txt = re.sub(r"(?s)<[^>]+>", "\n", raw)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t\r]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    return txt

def bing(query, name, excerpt=2000):
    q = urllib.parse.quote(query)
    out = f"/tmp/r44e_web/{name}.html"
    rc = curl(f"https://www.bing.com/search?q={q}&count=12&setlang=en", out)
    if rc != 0:
        print(f"FAIL {name} rc={rc}"); return
    raw = open(out, encoding="utf-8", errors="ignore").read()
    # extract result blocks: <li class="b_algo"> ... <h2><a href="URL">Title</a>
    items = re.findall(r'(?is)<li class="b_algo".*?<h2[^>]*><a[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?(?:<p[^>]*>(.*?)</p>|<div class="b_caption"[^>]*>(.*?)</div>)', raw)
    print(f"=== BING {name}: {query} | {len(items)} results ===")
    for i, it in enumerate(items[:10]):
        url_ = it[0]
        title = strip_html(it[1]).strip().replace("\n", " ")
        snip = strip_html(it[2] or it[3] or "").strip().replace("\n", " ")[:320]
        print(f"[{i+1}] {title}\n    {url_}\n    {snip}")
    print()

def wiki(title, name, full=False, chars=3000):
    ex = "explaintext=1&exintro=1" if not full else "explaintext=1"
    t = urllib.parse.quote(title)
    out = f"/tmp/r44e_web/{name}.json"
    rc = curl(f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&{ex}&format=json&redirects=1&titles={t}", out)
    if rc != 0:
        print(f"FAIL {name} rc={rc}"); return
    d = json.load(open(out))
    p = list(d["query"]["pages"].values())[0]
    txt = (p.get("extract") or "")[:chars]
    print(f"=== WIKI {name}: {p.get('title')} ===\n{txt}\n")

if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "bing":
        bing(sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 2000)
    elif mode == "wiki":
        wiki(sys.argv[2], sys.argv[3], full=(len(sys.argv) > 4 and sys.argv[4] == "full"), chars=int(sys.argv[5]) if len(sys.argv) > 5 else 3000)
