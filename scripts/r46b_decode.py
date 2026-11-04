#!/usr/bin/env python3
"""Resolve Google News RSS article IDs -> real URLs via batchexecute (search-redirect resolution).
Reads r46b_s*.log, extracts IDs + titles, decodes each."""
import re, json, sys, urllib.request, urllib.parse

def resolve(art_id):
    inner = json.dumps(["garturlreq",
                        [["X", "X", ["X", "X"], None, None, 1, 1, "US:en", None, 1,
                          None, None, None, None, 0, 1], "X", "X", 1, [1, 1, 1],
                         1, 1, None, 0, 0, None, 0],
                        art_id, 0])
    f_req = json.dumps([[["Fbv4je", inner, None, "generic"]]])
    payload = {"f.req": f_req}
    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(
        "https://news.google.com/_/DotsSplashUi/data/batchexecute",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
                 "User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read().decode("utf-8", "ignore")
    body = body.replace("\\/", "/").replace("\\u003d", "=").replace("\\u0026", "&").replace('\\"', '"')
    chunks = re.findall(r'"(https?://[^"]+)"', body)
    for c in chunks:
        if "news.google" not in c and "googleusercontent" not in c and "gstatic" not in c and "google.com" not in c:
            return c
    return None

def main():
    ids = {}
    for fn in sys.argv[1:]:
        cur = None
        for line in open(fn, encoding="utf-8", errors="ignore"):
            line = line.rstrip()
            t = re.match(r"  \* (.+)", line)
            if t: cur = t.group(1); continue
            l = re.match(r"    (https://news\.google\.com/rss/articles/[\w-]+)", line)
            if l and cur: ids[l.group(1)] = cur
    print(f"{len(ids)} ids to resolve\n")
    for aid, title in ids.items():
        try:
            u = resolve(aid)
        except Exception as e:
            u = f"ERR {type(e).__name__}: {str(e)[:60]}"
        print(f"T: {title[:110]}\nU: {u}\n")

if __name__ == "__main__":
    main()
