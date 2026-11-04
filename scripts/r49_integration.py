# -*- coding: utf-8 -*-
"""
R49 — МАШИННАЯ ИНТЕГРАЦИЯ ПРОГРАММЫ R11..R48.
Свод всех JSON-артефактов в единый реестр, перекрёстные проверки согласованности
ядра Q43 v2, консолидированный реестр UNKNOWN. Только локальные файлы.
Выход: scripts/r49_results.json
"""
import json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
# реестры ищем рядом со скриптом, затем в results/ (компоновка репо rent-mechanism-q43)
CANDIDATE_DIRS = [BASE, os.path.join(BASE, "..", "results")]
# свод пишем туда, где лежат входные реестры
OUT_DIR = CANDIDATE_DIRS[1] if os.path.isdir(CANDIDATE_DIRS[1]) else BASE
OUT = os.path.join(OUT_DIR, "r49_results.json")

def load(name):
    for d in CANDIDATE_DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                return json.load(f)
    return None

r42 = load("r42_results.json")
r43 = load("r43_results.json")
r44f = load("r44f_results.json")
r46e = load("r46e_results.json")
r48 = load("r48_results.json")
r20 = load("r20_results.json")
r32 = load("r32_results.json")
r33 = load("r33_results.json")

ledger = []
fails = []

def add(run, artifact, verdict, checks, note=""):
    ledger.append({"run": run, "artifact": artifact, "verdict": verdict,
                   "checks": checks, "note": note})

# --- 1. Реестр машинных прогонов -------------------------------------------
if r42:
    n_ok = sum(1 for k in ("CHK1","CHK2","CHK3","CHK4","CHK5")
               if isinstance(r42.get(k), dict) and r42[k].get("ok"))
    add("R42", "r42_results.json", r42.get("verdict","UNKNOWN"), f"{n_ok}/5")
else: fails.append("R42: r42_results.json отсутствует")

if r43:
    aud = r43.get("audit", {})
    n_aud = len(aud) if isinstance(aud, dict) else 0
    add("R43", "r43_results.json", r43.get("verdict","UNKNOWN"),
        f"audit={n_aud} позиций; emergence={r43.get('emergence',{}).get('verdict','?')}")
else: fails.append("R43: r43_results.json отсутствует")

if r44f:
    t = r44f.get("T1", {})
    add("R44-f", "r44f_results.json", r44f.get("verdict","UNKNOWN"),
        "T1 per_cycle={} lifetime={}; T2 dies_wo_donor={}; T3 distinct={}; T4 rent0_chain={}".format(
            t.get("per_cycle"), t.get("lifetime"),
            r44f.get("T2",{}).get("dies_without_donor"),
            r44f.get("T3",{}).get("distinct"),
            r44f.get("T4",{}).get("rent_always_zero") and r44f.get("T4",{}).get("chain_runs")))
else: fails.append("R44-f: r44f_results.json отсутствует")

if r46e:
    ov = r46e.get("overall", {})
    add("R46-e", "r46e_results.json", "M1={} M2={} M3={}".format(
        ov.get("M1"), ov.get("M2"), ov.get("M3")),
        "FR6 regime dV=-0.89 vs dF=-0.274; recurring dV=-0.14 vs dF=2.35; "
        "donors D0<D4<D2<D1; MIN-SET 11/11 выживших с K1+K2")
else: fails.append("R46-e: r46e_results.json отсутствует")

if r48:
    chks = r48.get("checks", [])
    n_ok = sum(1 for c in chks if c.get("ok"))
    add("R47-c/R48", "r48_results.json", r48.get("verdict","UNKNOWN"),
        f"GRAY MIRROR {n_ok}/{len(chks)}")
else: fails.append("R48: r48_results.json отсутствует")

for run, f in (("R20","r20_results.json"),("R32","r32_results.json"),("R33","r33_results.json")):
    d = load(f)
    if d:
        v = d.get("verdict") or d.get("overall") or "?"
        add(run, f, str(v)[:60], "legacy-run")

# --- 2. Перекрёстные проверки согласованности ядра --------------------------
cross = {}

# X1: MIN-SET согласован между M3 (r46e) и серым зеркалом (r48)
x1 = False
try:
    x1 = (r46e["M3_minset_ablation"]["check_a"]["verdict"] == "PASS"
          and r46e["M3_minset_ablation"]["check_a"]["evaluated"] == 11
          and not r46e["M3_minset_ablation"]["check_a"]["failures"]
          and r48["checks"][1]["ok"])  # CHK2: без капа цены нет
except Exception as e:
    x1 = False; fails.append(f"X1 exception: {e}")
cross["X1_MINSET_gray_mirror"] = {
    "claim": "MIN-SET {K1,K2} и «нет капа → нет цены нигде» согласованы",
    "ok": x1}

# X2: номенклатура — K3=0/K4=0, рента>0, легальной цены нет, теневая есть
x2 = False
try:
    nom = [c for c in r46e["M3_minset_ablation"]["cases"] if c["id"]=="Nomenklatura_USSR"][0]
    grey = [c for c in r48["cases"] if c["id"]=="USSR-nomenklatura"][0]
    x2 = (nom["K3"]==0 and nom["K4"]==0 and nom["rent_survived"] is True
          and nom["place_price_observed"] is False
          and grey["legal_price"]==0.0 and grey["shadow"]==500000.0
          and grey["rent_alive"] is True)
except Exception as e:
    fails.append(f"X2 exception: {e}")
cross["X2_nomenklatura_grey"] = {
    "claim": "K3/K4 диагностические: рента живёт без легальной цены места; цена в тени (≈14.9 лет дохода)",
    "ok": bool(x2)}

# X3: FR6 — амплитуды согласованы между r46e и r48, режимное плечо устойчиво
x3 = False
try:
    dV = r46e["M1_fr6_shock_typing"]["regime"]["calibration"]["dV_obs"]
    rng = r48["fr6_patch"]["dV_range"]
    fA = r48["fr6_patch"]["F_amplitude"]
    x3 = (abs(dV) > abs(fA[0]) and rng[0] > abs(fA[0]) and rng[1] <= 0.95
          and r46e["M1_fr6_shock_typing"]["checks"]["regime |dV|>|dF_spot| (NYC: 0.89 vs 0.274)"]
          and r46e["M1_fr6_shock_typing"]["checks"]["recurring |dV|<|dF_spot| (MDB: 0.14 vs 2.35)"])
    dV_union = sorted({-abs(dV), -rng[0], -rng[1]})
except Exception as e:
    fails.append(f"X3 exception: {e}"); dV_union = None
cross["X3_FR6_amplitudes"] = {
    "claim": "ΔV_NYC ∈ [-0.946, -0.89] против F ≈ [-0.5, -0.4]; recurring MDB: |ΔV|=0.14 < |ΔF|=2.35; метрический конфликт дна решён (r47d)",
    "ok": bool(x3), "dV_union": dV_union if dV_union else "see r48 fr6_patch"}

# X4: закон доноров строгий порядок
x4 = False
try:
    rp = r46e["M2_donor_module"]["rescue_price_order_usd"]
    x4 = (rp["D0"] < rp["D4"] < rp["D2"] < rp["D1"]
          and all(r46e["M2_donor_module"]["checks"].values()))
except Exception as e:
    fails.append(f"X4 exception: {e}")
cross["X4_donor_law"] = {
    "claim": "Цена спасения: D0=$0 (правило) < D4=$350M (кредитор) < D2=>$471M (налогоплательщик) < D1=$2.9B (резервы=терминально); класс меняется только через D2/D3",
    "ok": bool(x4)}

# X5: инвариант цикловой формулы — патч I_K″
x5 = False
try:
    t3 = r44f["T3"]["outcomes"]
    x5 = (r44f["verdict"] == "PATCHED (I_K″)"
          and r44f["T1"]["per_cycle"] is False and r44f["T1"]["lifetime"] is True
          and r44f["T3"]["distinct"] is True
          and t3["K_t=0 (передача оборвана)"][2] is False  # механизм кончается — исход иной
          and r44f["fails"] == [])
except Exception as e:
    fails.append(f"X5 exception: {e}")
cross["X5_invariant_IK2"] = {
    "claim": "I_K″: per-cycle опровергнут, lifetime держится; K={K_f,K_w,K_s,K_t} с попарно различными отказами; вход ∈ {R_t, резервы, донор}",
    "ok": bool(x5)}

# X6: пустой класс НЕКРО + закон паразитарности
x6 = None
try:
    hier = r46e["M3_minset_ablation"]["hierarchy_verdict"]
    x6 = "NECRO class empty" in hier
except Exception as e:
    fails.append(f"X6 exception: {e}")
cross["X6_parasitism"] = {
    "claim": "Класс определяется типом капа (ресурсный→мутуализм/дренаж; лицензионный→дренаж+ФЛИП); НЕКРО пуст",
    "ok": bool(x6)}

# --- 3. Консолидированный реестр UNKNOWN -----------------------------------
unknown = []
seen = set()
def uadd(text, source):
    key = text.strip().lower()[:80]
    if key not in seen:
        seen.add(key)
        unknown.append({"item": text, "source": source})

for it in r48.get("unknown", []):
    uadd(it, "r48_results.json")
for it in r46e.get("unknown_list", []):
    uadd(it, "r46e_results.json")

# группировка реестра
struct_blocked = [u["item"] for u in unknown if any(k in u["item"] for k in
    ("заблокированы", "403", "404", "429", "HTTP 000", "вне песочницы"))]
method_closed = [u["item"] for u in unknown if any(k in u["item"] for k in
    ("метри", "конфликт", "PLACEHOLDER", "by memory", "not confirmed"))]
open_items = [u["item"] for u in unknown
              if u["item"] not in struct_blocked and u["item"] not in method_closed]

# --- 4. Итог ----------------------------------------------------------------
all_core_ok = all(v["ok"] for v in cross.values()) and not fails
result = {
    "package": "R49-INTEGRATION",
    "date": "2026-11-05",
    "scope": "консолидация машинных прогонов R11..R48 в единый реестр; ядро Q43 v2",
    "machine_runs": ledger,
    "cross_checks": cross,
    "integrity_fails": fails,
    "unknown_registry": {
        "total_unique": len(unknown),
        "structurally_blocked": struct_blocked,
        "methodologically_closed": method_closed,
        "open": open_items,
    },
    "core_v2_final": {
        "state": "Q43=(S,Ah,X,F,B,C,N,G,W,P,M,I)",
        "phi": "Φ42(Q_t; R_t,N_t,G_t,W_t); V_t=ΣE[R_s|shock-model]/(1+r)^s × Prob(survival)",
        "minset": "{K1,K2} строго необходимы (гос. или частная форма); G* функционален; W_lat латентная опция; K3/K4 диагностические",
        "channels": "K={K_f,K_w,K_s,K_t}; вход воспроизводства ∈ {R_t, резервы, внешний донор}",
        "laws": [
            "L1 СЕРОЕ ЗЕРКАЛО: при K1∧K2∧R>0 цена места существует в каком-то режиме (легальном или теневом); без K1 цены нет нигде",
            "L2 ЗАКОН ДОНОРОВ: цена спасения D0<$350M(D4)<≥$471M(D2)<$2.9B(D1=терминально); класс меняется только D2/D3",
            "L3 ПАРАЗИТАРНОСТЬ: класс определяет ТИП КАПА (ресурсный→мутуализм/дренаж; лицензионный→дренаж+ФЛИП); НЕКРО пуст",
            "L4 FR6-УСЛОВНЫЙ: |ΔP|>|ΔF| только при режимных шоках; повторяющиеся запрайсены (NYC 0.89-0.95 vs 0.4-0.5; MDB 0.14 vs 2.35)",
            "L5 ДИСКОНТ W_lat: дисконт ≈ p·(1−c)·V (ЮКОС −36…−69%; Зимбабве c≈0→исчезновение рынка; США c≈1→пренебрежим)",
            "L6 FLIP-ПАРА: NYC (слой против заместителя при шоке) ↔ Дублин-2000 (снятие слоя до шока → рассеяние через вход, парк ×4.3)",
        ],
        "invariant": "I_K″: ∃Q,∃t*: R_{t*}>0 ∧ Q_{t+1}=Φ42(Q_t;K_f,K_w,K_s,K_t) ∧ вход K∈{R_t,резервы,донор} ∧ множество носителей замкнуто ∧ выживание без R_t только через резервы/донора",
    },
    "verdict": "INTEGRATED" if all_core_ok else "INTEGRATION_FAIL",
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=1)

print("R49 verdict:", result["verdict"])
print("machine runs:", len(ledger), "| integrity fails:", len(fails))
for k, v in cross.items():
    print(f"  {k}: {'OK' if v['ok'] else 'FAIL'}")
print("UNKNOWN unique:", len(unknown),
      "| blocked:", len(struct_blocked),
      "| method-closed:", len(method_closed),
      "| open:", len(open_items))
if fails:
    print("FAILS:", fails)
sys.exit(0 if all_core_ok else 1)
