#!/usr/bin/env python3
"""R44-e web fetch helper: plain HTTP GET, strip HTML, save txt, print excerpt.
No tokens, no auth — public pages only."""
import sys, re, urllib.request, html, os

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
OUT = "/tmp/r44e_web"

def fetch(url, name, excerpt=1800):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=25) as r:
        raw = r.read().decode("utf-8", "ignore")
    txt = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", raw)
    txt = re.sub(r"(?s)<[^>]+>", " ", txt)
    txt = html.unescape(txt)
    txt = re.sub(r"[ \t\r]+", " ", txt)
    txt = re.sub(r"\n\s*\n+", "\n", txt)
    path = os.path.join(OUT, name + ".txt")
    with open(path, "w") as f:
        f.write(txt)
    print(f"=== {name} | {url} | {len(raw)}B raw, {len(txt)}B text ===")
    print(txt[:excerpt].strip())
    print("...\n")

if __name__ == "__main__":
    jobs = []
    if len(sys.argv) > 1:
        jobs.append((sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 1800))
    for url, name, ex in jobs:
        try:
            fetch(url, name, ex)
        except Exception as e:
            print(f"FAIL {name} {url}: {e}")
