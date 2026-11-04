#!/usr/bin/env python3
"""R47-a SERIES 3 (final): archive.org advancedsearch (caps/bans/court/ACJA) + WP list=search + GNews RSS (retrospectives, figures)."""
import json, re, html, subprocess, time, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
TMP = "/home/z/my-project/scripts/r47a_tmp"

def http(url, out):
    r = subprocess.run(["curl", "-sS", "-L", "-m", "35", "-A", UA, url, "-o", out], capture_output=True, text=True)
    return r.returncode == 0

print("== A. archive.org advancedsearch ==")
def ia(q, tag):
    u = ("https://archive.org/advancedsearch.php?q=" + urllib.parse.quote(q) +
         "&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=year&fl%5B%5D=creator&rows=20&page=1&output=json")
    if not http(u, f"{TMP}/ia_{tag}.json"):
        print(f"[{tag}] curl fail"); return
    try:
        d = json.load(open(f"{TMP}/ia_{tag}.json"))
        docs = d["response"]["docs"]; tot = d["response"]["numFound"]
    except Exception as e:
        print(f"[{tag}] json fail: {str(e)[:100]}"); return
    print(f"\n--- [{tag}] q='{q}' numFound={tot}")
    for it in docs[:20]:
        print(f"  * {it.get('identifier')} | {it.get('year','?')} | {str(it.get('title'))[:95]}")

ia('jitney AND (ordinance OR ordinance OR "city council") AND year:[1915 TO 1917] AND mediatype:texts', "ord2")
ia('"jitney" AND ("supreme court" OR injunction) AND year:[1915 TO 1921] AND mediatype:texts', "court2")
ia('"Atlantic City Jitney"', "acja")
ia('title:(jitney) AND year:[1915 TO 1922]', "t2")
time.sleep(1)

print()
print("== B. Wikipedia list=search ==")
def wps(q, tag):
    u = ("https://en.wikipedia.org/w/api.php?action=query&list=search&format=json&srlimit=12"
         f"&srsearch={urllib.parse.quote(q)}")
    if not http(u, f"{TMP}/wp_{tag}.json"):
        print(f"[{tag}] curl fail"); return
    try:
        d = json.load(open(f"{TMP}/wp_{tag}.json"))
        hits = d["query"]["search"]; tot = d["query"]["searchinfo"]["totalhits"]
    except Exception as e:
        print(f"[{tag}] json fail: {str(e)[:100]}"); return
    print(f"\n--- [{tag}] srsearch='{q}' totalhits={tot}")
    for h in hits[:12]:
        sn = re.sub(r"<[^>]+>", "", h.get("snippet", ""))
        print(f"  * {h['title']} | ...{sn[:180]}...")

wps("jitney bus regulation history 1914", "reg")
wps("jitney", "j2", )
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

gn("jitneys banned 1916 cities", "bans")
gn("jitney 62000", "n62")
gn("Atlantic City jitney permit price", "acja")
print("\nDONE series3")
