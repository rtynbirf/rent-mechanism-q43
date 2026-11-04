#!/usr/bin/env python3
"""R44-d: OpenAlex (with mailto) workhorse: doi abstracts + search."""
import sys, json, time, urllib.request, urllib.parse

BASE = "https://api.openalex.org/works"
UA = "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0"

def get(u, to=20):
    req = urllib.request.Request(u, headers={"User-Agent": UA})
    return json.loads(urllib.request.urlopen(req, timeout=to).read().decode("utf-8", "ignore"))

def abstract_from_inv(inv):
    if not inv:
        return ""
    pos = {}
    for w, idxs in inv.items():
        for i in idxs:
            pos[i] = w
    return " ".join(pos[i] for i in sorted(pos))

def show(d, chars=1500):
    print("=====", d.get("title"), "|", d.get("publication_year"), "| cites:", d.get("cited_by_count"), "| DOI:", d.get("doi"))
    print((d.get("primary_location", {}) or {}).get("landing_page_url") or "")
    ab = abstract_from_inv(d.get("abstract_inverted_index"))
    print(ab[:chars])
    print()

def doi(dois, chars=1500):
    for i, d0 in enumerate(dois):
        try:
            d = get(BASE + "/doi:%s?mailto=r44d.research@example.org" % d0)
            show(d, chars)
        except Exception as e:
            print("DOI_ERR", d0, e)
        time.sleep(2)

def search(q, n=5, chars=1200, filt=None):
    u = BASE + "?search=%s&per-page=%d&mailto=r44d.research@example.org" % (urllib.parse.quote(q), n)
    if filt:
        u += "&filter=" + urllib.parse.quote(filt)
    try:
        d = get(u)
    except Exception as e:
        print("SEARCH_ERR", e); return
    for it in d.get("results", []):
        show(it, chars)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "doi":
        doi(sys.argv[2:])
    elif cmd == "search":
        n = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        search(sys.argv[2], n)
