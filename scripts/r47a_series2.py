#!/usr/bin/env python3
"""R47-a SERIES 2 (combined): archive.org advancedsearch + Wikipedia list=search + Google News RSS."""
import json, re, html, subprocess, time, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
TMP = "/home/z/my-project/scripts/r47a_tmp"

def http(url, out, extra=None):
    cmd = ["curl", "-sS", "-L", "-m", "35", "-A", UA] + (extra or []) + [url, "-o", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0

print("== A. archive.org advancedsearch ==")
def ia(q, tag):
    u = ("https://archive.org/advancedsearch.php?q=" + urllib.parse.quote(q) +
         "&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=year&fl%5B%5D=creator&rows=25&page=1&output=json")
    if not http(u, f"{TMP}/ia_{tag}.json"):
        print(f"[{tag}] curl fail"); return
    try:
        d = json.load(open(f"{TMP}/ia_{tag}.json"))
        docs = d["response"]["docs"]; tot = d["response"]["numFound"]
    except Exception as e:
        print(f"[{tag}] json fail: {str(e)[:100]}"); return
    print(f"\n--- [{tag}] q='{q}' numFound={tot}")
    for it in docs[:25]:
        print(f"  * {it.get('identifier')} | {it.get('year','?')} | {str(it.get('title'))[:90]}")

ia('title:(jitney) AND mediatype:texts', "t")
ia('jitney AND year:[1914 TO 1922] AND mediatype:texts', "y")
ia('Eckert Hilton jitney', "eh")
ia('"jitney bus" AND date:[1915-01-01 TO 1916-12-31]', "jb")
time.sleep(1)

print()
print("== B. Wikipedia list=search (srsearch) ==")
def wps(q, tag):
    u = ("https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srlimit=15"
         f"&srsearch={urllib.parse.quote(q)}")
    if not http(u, f"{TMP}/wp_{tag}.json"):
        print(f"[{tag}] curl fail"); return
    try:
        d = json.load(open(f"{TMP}/wp_{tag}.json"))
        hits = d["query"]["search"]; tot = d["query"]["searchinfo"]["totalhits"]
    except Exception as e:
        print(f"[{tag}] json fail: {str(e)[:100]}"); return
    print(f"\n--- [{tag}] srsearch='{q}' totalhits={tot}")
    for h in hits[:15]:
        sn = re.sub(r"<[^>]+>", "", h.get("snippet", ""))
        print(f"  * {h['title']} | ...{sn[:200]}...")

wps("jitney", "j")
wps("jitney 1915 ordinance", "jo")
time.sleep(1)

print()
print("== C. Google News RSS ==")
def gn(q, tag):
    u = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en"
    if not http(u, f"{TMP}/gn_{tag}.xml"):
        print(f"[{tag}] curl fail"); return
    t = open(f"{TMP}/gn_{tag}.xml", errors="ignore").read()
    items = re.findall(r"<item>(.*?)</item>", t, re.S)
    print(f"\n--- [{tag}] q='{q}' items={len(items)}")
    for it in items[:12]:
        ti = re.search(r"<title>(.*?)</title>", it, re.S)
        pd = re.search(r"<pubDate>(.*?)</pubDate>", it, re.S)
        print("  *", (html.unescape(ti.group(1)) if ti else "?")[:180], "|", pd.group(1) if pd else "")

gn("jitney 1914 history", "h")
gn("jitney craze 1915", "c")
gn("Eckert Hilton jitneys", "eh")
print("\nDONE series2")
