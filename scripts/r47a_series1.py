#!/usr/bin/env python3
"""R47-a SERIES 1: Chronicling America JSON API (no keys).
Part A: per-year totalItems for 'jitney' (explosion proxy) + baseline words.
Part B: targeted queries (ordinance/license/ban/Chicago) with OCR snippets.
"""
import json, subprocess, time, urllib.parse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
BASE = "https://chroniclingamerica.loc.gov/search/pages/results/"

def get(url, out):
    r = subprocess.run(["curl", "-sS", "-m", "40", "-A", UA, url, "-o", out], capture_output=True, text=True)
    if r.returncode != 0:
        print("CURL FAIL", url, r.stderr[:200]); return None
    try:
        return json.load(open(out))
    except Exception as e:
        print("JSON FAIL", out, str(e)[:120]); return None

print("== PART A: per-year totals, q=jitney, rows=1 ==")
for y in range(1912, 1924):
    u = f"{BASE}?andtext=jitney&date1={y}&date2={y}&dateFilterType=yearRange&format=json&rows=1"
    d = get(u, f"/home/z/my-project/scripts/r47a_tmp/ca_y{y}.json")
    n = d.get("totalItems") if d else "?"
    print(f"YEAR {y}: {n}")
    time.sleep(0.6)

print()
print("== PART A2: per-year totals, q='jitney bus' ==")
for y in (1915, 1916, 1918, 1920):
    u = f"{BASE}?andtext=%22jitney+bus%22&date1={y}&date2={y}&dateFilterType=yearRange&format=json&rows=1"
    d = get(u, f"/home/z/my-project/scripts/r47a_tmp/ca_jb{y}.json")
    n = d.get("totalItems") if d else "?"
    print(f"YEAR {y} 'jitney bus': {n}")
    time.sleep(0.6)

print()
print("== PART B: targeted queries, rows=8, snippets from ocr_eng ==")
def snippets(q, y1, y2, tag, maxsnip=600):
    u = f"{BASE}?andtext={urllib.parse.quote(q)}&date1={y1}&date2={y2}&dateFilterType=yearRange&format=json&rows=8"
    d = get(u, f"/home/z/my-project/scripts/r47a_tmp/ca_{tag}.json")
    if not d: return
    print(f"\n--- [{tag}] q='{q}' {y1}-{y2} total={d.get('totalItems')}")
    for it in d.get("items", [])[:8]:
        txt = (it.get("ocr_eng") or "").replace("\n", " ")
        # find first mention of jitney
        low = txt.lower(); idx = low.find("jitney")
        win = txt[max(0, idx-250): idx+maxsnip] if idx >= 0 else txt[:maxsnip]
        print(f"* {it.get('date')} | {it.get('title',{}).get('name','?')} | {it.get('state','')} | p{it.get('page')}")
        print(f"  ...{win}...")

snippets("jitney ordinance", 1915, 1920, "ord")
snippets("jitney license", 1915, 1920, "lic")
snippets("jitney franchise", 1915, 1920, "franch")
snippets('"jitney" "supreme court"', 1916, 1920, "court")
snippets("jitney menace", 1915, 1916, "menace")
print("\nDONE series1")
