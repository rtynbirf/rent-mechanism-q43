#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R40 — АУДИТ V7.0 ПОЛНЫЙ СИНТЕЗ против внешнего лиджера.

Канон §2: артефакт с претензией «ГОТОВ К ПРОДАКШЕНУ» проверяется по лестнице:
уровень 3 (пересчёт кодом из первичных JSON песочниц) + уровень 4 (корпус-файл).
Канон §7: REINJECT только из ΔS — здесь ΔS = расхождения V7.0 vs ledger.

Проверяемые классы:
  A. LEDGER-числа R11 (r11_results.json)
  B. LEDGER-числа R20 (r20_results.json)
  C. Числа R32 (закрытая форма — пересчёт другим путём)
  D. Арифметика V7.0 (R25 PV, квадранты, R31-контрпример)
  E. КОРПУС-заявки (строки в FINALNIY_PROMPT_V6.0_EDINYI_KANON.md)
  F. КРОСС-РЕФЕРЕНСЫ и ВЕРДИКТЫ (сверка формулировок с T3/R32/R33)
"""

import json

BASE = "/home/z/my-project/scripts/"
CORPUS = "/home/z/my-project/download/FINALNIY_PROMPT_V6.0_EDINYI_KANON.md"

with open(BASE + "r11_results.json") as f:
    R11 = json.load(f)
with open(BASE + "r20_results.json") as f:
    R20 = json.load(f)
with open(BASE + "r32_results.json") as f:
    R32 = json.load(f)

rows = []


def check(cid, claim, expected, actual, source, verdict=None, note=""):
    if verdict is None:
        verdict = "MATCH" if expected == actual else "MISMATCH"
    rows.append({"id": cid, "claim": claim, "expected": expected,
                 "actual": actual, "source": source, "verdict": verdict,
                 "note": note})
    mark = {"MATCH": "+", "MISMATCH": "X", "DRIFT": "~", "COMPLIANT": "c",
            "UNVERIFIABLE": "?"}[verdict]
    print(f"[{mark}] {cid:<6} {claim}")
    if verdict != "MATCH":
        print(f"         ожидание: {expected}")
        print(f"         факт:     {actual}")
    if note:
        print(f"         примечание: {note}")
    return verdict


print("=" * 88)
print("КЛАСС A/B/C — ЧИСЛА ПРОТИВ ЛИДЖЕРА ПЕСОЧНИЦ")
print("=" * 88)

# --- R11 ---
check("A1", "R11-A открытый доступ: рента ≈ 0", "≈0 (|r|<1e-3)",
      "≈0 (|r|<1e-3)" if abs(R11["R11_A"]["open_access"]["rent_final"]) < 1e-3
      else str(R11["R11_A"]["open_access"]["rent_final"]),
      "r11_results.json:R11_A.open_access")
check("A2", "R11-A биомасса X_be = c/(pq) = 25.0", 25.0,
      R11["R11_A"]["open_access"]["X_bioeconomic_eq"],
      "r11_results.json:R11_A.open_access")
check("A3", "R11-A контролируемый доступ: рента 56.0", 56.0,
      round(R11["R11_A"]["controlled"]["rent_final"], 6),
      "r11_results.json:R11_A.controlled")
ratio = R11["R11_A"]["verdict_data"]["ratio_cum_capture"]
check("A4", "R11-A накопленный захват 363×", "363.4x", f"{ratio:.1f}x",
      "r11_results.json:R11_A.verdict_data")
check("A5", "R11-B: 11 периодов R=0 при P=1, F=0 ровно", 11,
      R11["R11_B"]["n_zero_R"], "r11_results.json:R11_B",
      note="max_F_when_R_zero = " + str(R11["R11_B"]["max_F_when_R_zero"]))
tt = R11["R11_B"]["truth_table"]
ok_tt = (tt == [{"P": 1, "R": 0, "F": 0}, {"P": 1, "R": 1, "F": 1},
                {"P": 0, "R": 1, "F": 0}, {"P": 0, "R": 0, "F": 0}])
check("A6", "R11-B таблица истинности F=P·R", True, ok_tt,
      "r11_results.json:R11_B.truth_table")
check("A7", "R11-D порог R0* = δ/α = 0.375", 0.375,
      round(R11["R11_D"]["threshold_R0"], 12), "r11_results.json:R11_D")
check("A8", "R11-D мёртвый режим P→0.003", "0.003",
      f"{R11['R11_D']['dead_regime_last5'][-1][1]:.4f}",
      "r11_results.json:R11_D (0.0033)")
check("A9", "R11-D живой режим P→1.0", 1.0,
      R11["R11_D"]["alive_regime_last5"][-1][1], "r11_results.json:R11_D")
check("A10", "R11-E no-maintenance: 0.88^25 → 0.0409", round(0.88 ** 25, 4),
      R11["R11_E"]["no_maint_P_at_t39"], "r11_results.json:R11_E (пересчёт)")
check("A11", "R11-E dormant: F=0 в крах, поток возобновляется полностью",
      True,
      all(v == 0.0 for v in R11["R11_E"]["dormant_F_during_collapse"]) and
      all(v == 1.0 for v in R11["R11_E"]["dormant_resume_flow_t40_plus"]),
      "r11_results.json:R11_E")

# --- R20 ---
t1 = R20["T1"]
check("B1", "R20-T1: R∈[0,40] при Y=100, 5 контрфактов",
      (100.0, 0.0, 40.0),
      (t1["Y"], t1["R_min"], t1["R_max"]), "r20_results.json:T1")
t2 = R20["T2"]
tail_R = t2["dynamic_path_tail"][-1]["R_measured"]
check("B2", "R20-T2: рента затухает 70 → 0.97 при Y=100", "0.97",
      f"{tail_R:.4f}", "r20_results.json:T2.tail (0.9674)")
check("B3", "R20-T2: A* = Y/r = 1428.57", round(100.0 / 0.07, 2),
      t2["params"]["A_star_theory"], "r20_results.json:T2 (пересчёт)")
ic = t2["identity_check"]
check("B4", "R20-T2: якорь воспроизводства R=70=R_true; рыночный R=30=N_true",
      (70.0, True, 30.0, True),
      (ic["R_with_repro_anchor"], ic["equals_R_true"],
       ic["R_with_market_anchor_static"], ic["equals_N_true"]),
      "r20_results.json:T2.identity_check")
check("B5", "R20-T3: налог 25 ≡ рента 25 структурно; tax90 FAIL (проедает N)",
      True,
      (t3_ok := (R20["T3"]["tax_25"]["X"] == 25.0 and
                 R20["T3"]["tax_25"]["X<=R_true"] and
                 not R20["T3"]["tax_25"]["digs_into_N"] and
                 not R20["T3"]["tax_90"]["X<=R_true"] and
                 R20["T3"]["tax_90"]["digs_into_N"])),
      "r20_results.json:T3")
check("B6", "R20-T4: маржи 60 vs 10 (6:1)", 6.0, R20["T4"]["ratio"],
      "r20_results.json:T4")
check("B7", "R20-T5: n*=15; лицензия n=8 → profit=70 устойчиво", (15.0, 70.0),
      (t5 := R20["T5"], None) and (t5["n_star_free_entry"],
                                   t5["license_tail"][-1]["profit"]),
      "r20_results.json:T5")

# --- R32 (закрытая форма, другой путь) ---
SCALE, E, C, S = 100.0, 0.9, 0.9, 0.9
Bv = SCALE * E * C * S
V_before, V_after = 4 * Bv, 4 * SCALE * 0.1 * C * S
all_pass = all(R32["passed"].values())
check("C1", "R32: 6/6 проверок PASS", True, all_pass and len(R32["passed"]) == 6,
      "r32_results.json:passed")
check("C2", "R32-C3: V 291.6 → 32.4 (11%)", (291.6, 32.4, "11%"),
      (round(V_before, 1), round(V_after, 1),
       f"{round(100 * V_after / V_before)}%"),
      "пересчёт закрытой формы B=SCALE·E·C·S")
check("C3", "R32-C4: net = 4.05−10 = −5.95", -5.95,
      round(SCALE * E * 0.05 * S - 10.0, 2), "пересчёт закрытой формы")
check("C4", "R32-C5: net 62.9/поколение, кумулятив 503.2", (62.9, 503.2),
      (round(Bv - 10.0, 1), round(8 * (Bv - 10.0), 1)),
      "пересчёт закрытой формы")

print()
print("=" * 88)
print("КЛАСС D — АРИФМЕТИКА V7.0")
print("=" * 88)
pv10 = 100.0 * (1 - 1.1 ** -10) / 0.1
check("D1", "R25: PV аннуитета R=100, i=10%, T=10 → 614.46", 614.46,
      round(pv10, 2), "пересчёт")
check("D2", "R25: перпетуитет R/i = 1000", 1000.0, 100.0 / 0.1, "пересчёт")
check("D3", "Квадранты 13+39+612+3+357 = 1024", 1024,
      13 + 39 + 612 + 3 + 357, "пересчёт")
check("D4", "R31 контрпример: 100−20−50 = 30", 30, 100 - 20 - 50,
      "пересчёт (B=100, Cost=20, Y^cf=50)")

print()
print("=" * 88)
print("КЛАСС E — КОРПУС-ЗАЯВКИ (строки в V6.0 ЕДИНЫЙ КАНОН)")
print("=" * 88)
try:
    with open(CORPUS, encoding="utf-8") as f:
        corpus = f.read()
    has = lambda s: s in corpus
    check("E1", "Вето 63/64 присутствует в корпусе", True, has("63/64"),
          "V6.0 corpus")
    check("E2", "FSM 19 состояний / 4 терминала / 25 рёбер", True,
          has("19 состояний") and has("4 терминала") and has("25 рёбер"),
          "V6.0 corpus")
    check("E3", "P7 опровергнут/переформулирован на карте v2.0", True,
          has("P7") and ("v2.0" in corpus or "v2.2" in corpus),
          "V6.0 corpus")
    check("E4", "Квадранты 13|39|612|3|357 в корпусе", True,
          all(has(x) for x in ["13", "39", "612", "357"]) and has("1024"),
          "V6.0 corpus")
except FileNotFoundError:
    check("E1", "Корпус V6.0 недоступен", "present", "FILE_MISSING",
          "download/", verdict="UNVERIFIABLE")

print()
print("=" * 88)
print("КЛАСС F — ВЕРДИКТЫ И КРОСС-РЕФЕРЕНСЫ (семантическая сверка)")
print("=" * 88)
check("F1", "V7.0: «Налог = рента ❌ ОПРОВЕРГНУТО (R20, структура)»",
      "вердикт R20-T3",
      "DRIFT",
      "r20_results.json:T3.observation", verdict="DRIFT",
      note="Лиджер: «налог 25 и рента 25 структурно НЕРАЗЛИМИМЫ — различие "
           "лежит в свойствах F (compulsory/unrequited vs claim), вне ядра». "
           "Тождество не опровергнуто — оно ВЫНЕСЕНО ЗА ЯДРО. "
           "Опровергнуто другое: произвольность изъятия (X≤R_true). "
           "Корректная строка: «⚠️ неразличимы структурой (R20-T3); различие "
           "— F-свойства, вне ядра; тождество UNRESOLVED».")
check("F2", "V7.0 Часть IV: «S входит в ядро (R33)»", "R32",
      "DRIFT", "r32 ledger + V7.0 Часть II (R33: ОТКРЫТО)", verdict="DRIFT",
      note="S вошла в ядро как сомножитель — находка R32; R33 — открытый "
           "вопрос её эндогенности. Атрибуция сдвинута на один узел.")
check("F3", "V7.0 Часть IV: «Государство = картель → R36»", "R37",
      "DRIFT", "V7.0 Часть II (R36=картель, R37=государство)", verdict="DRIFT",
      note="Перекрёстная ссылка указывает на соседний узел.")
check("F4", "V7.0 Часть IV: «закрытые бюджеты → R35-гипотеза»", "R39",
      "DRIFT", "V7.0 Часть II (R39=информационная асимметрия)", verdict="DRIFT",
      note="Частота закрытых потоков — вопрос R28→R39, не R35 (налог).")
check("F5", "Карантин: 18.15%, 25-е ребро, доля секретных бюджетов — "
      "держатся вне посылок", "COMPLIANT", "COMPLIANT",
      "V7.0 Часть IV (структура карантина воспроизведена)", verdict="COMPLIANT",
      note="Ровно тот класс честности, которого требовал пользователь: "
           "UNKNOWN не превращён в FALSE и в TRUE.")

# --- сводка ---
print()
print("=" * 88)
n = {"MATCH": 0, "MISMATCH": 0, "DRIFT": 0, "COMPLIANT": 0,
     "UNVERIFIABLE": 0}
for r in rows:
    n[r["verdict"]] += 1
print(f"ИТОГ: MATCH={n['MATCH']}  COMPLIANT={n['COMPLIANT']}  "
      f"DRIFT={n['DRIFT']}  MISMATCH={n['MISMATCH']}  "
      f"UNVERIFIABLE={n['UNVERIFIABLE']}")

with open(BASE + "r40_audit.json", "w", encoding="utf-8") as f:
    json.dump({"rows": rows, "summary": n}, f, ensure_ascii=False, indent=1)
print("Сохранено: " + BASE + "r40_audit.json")
