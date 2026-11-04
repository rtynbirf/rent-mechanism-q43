#!/usr/bin/env python3
"""Robust Wikipedia TextExtracts fetch with backoff (Wikimedia rate limits)."""
import json, subprocess, sys, time, urllib.parse

UA = "R44E-research/1.0 (research sandbox; contact: none)"

def wiki_extract(title, name, chars=30000, attempts=4):
    t = urllib.parse.quote(title)
    url = (f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts"
           f"&explaintext=1&format=json&redirects=1&formatversion=2&titles={t}")
    for i in range(attempts):
        r = subprocess.run(["curl", "-sS", "-m", "30", "-A", UA, url, "-o", f"/tmp/r44e_web/{name}.json"],
                           capture_output=True, text=True)
        try:
            d = json.load(open(f"/tmp/r44e_web/{name}.json"))
            p = d["query"]["pages"][0]
            if "extract" in p and p["extract"]:
                txt = p["extract"][:chars]
                open(f"/tmp/r44e_web/{name}.txt", "w").write(txt)
                print(f"=== WIKI {name}: {p.get('title')} | {len(txt)} chars ===")
                return txt
        except Exception:
            pass
        time.sleep(4 + 3 * i)
    print(f"FAIL wiki {title}")
    return ""

if __name__ == "__main__":
    wiki_extract(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 30000)
