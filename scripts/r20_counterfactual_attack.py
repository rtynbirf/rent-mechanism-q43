#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R20 — АТАКА НА КОНТРФАКТИЧЕСКИЙ КРИТЕРИЙ РЕНТЫ: R = max(0, Y - Y^cf)
Цель: СЛОМАТЬ критерий, а не подтвердить.
T1 — чувствительность к выбору контрфакта
T2 — капитализационная циркулярность (динамический брейкер)
T3 — классификация налог/рента/нормальный доход без институтов
T4 — квази-рента: конфликт глубины маржи
T5 — якорь свободного входа: спасает ли правило выбора критерий
"""
import json

OUT = {}

# ============================================================
# T1: ЧУВСТВИТЕЛЬНОСТЬ К КОНТРФАКТУ
# Один и тот же поток Y=100 (монопольное извлечение).
# Пять равно-легитимных контрфактов из стандартной теории.
# ============================================================
Y = 100.0
cf = {
    "competitive_benchmark (цена свободной конкуренции)": 80.0,
    "next_best_use (лучшая альтернативная база)":          60.0,
    "reservation_alternative (альтернатива держателя)":    95.0,
    "historical_baseline (исторический уровень)":          70.0,
    "market_value_anchor (якорь капитализированной цены)": 100.0,  # см. T2
}
R_by_cf = {k: max(0.0, Y - v) for k, v in cf.items()}
OUT["T1"] = {"Y": Y, "counterfactuals": cf, "R_measured": R_by_cf,
             "R_min": min(R_by_cf.values()), "R_max": max(R_by_cf.values()),
             "factor_disagreement": (max(R_by_cf.values()) - min(R_by_cf.values())) / max(min(R_by_cf.values()), 1e-12)}

# ============================================================
# T2: КАПИТАЛИЗАЦИОННАЯ ЦИРКУЛЯРНОСТЬ — БРЕЙКЕР
# Носитель: производительная база. Y=100 бесконечно (извлечение не падает).
# Нормальная отдача N_true=30 (= r*K_repro), истинная рента R_true=70.
# Якорь A: воспроизводственная стоимость K_repro = N_true/r
# Якорь B: рыночная цена актива A_t, которая сама капитализирует поток.
# Динамика якоря B: A_t = A_{t-1} + R_m,t  (цена актива вбирает измеренную
# ренту); измерение R_m,t = Y - r*A_{t-1}.
# ============================================================
r = 0.07
Y_f, N_true, R_true = 100.0, 30.0, 70.0
K_repro = N_true / r              # 428.57 — воспроизводственный якорь
A = K_repro                       # старт: актив по себестоимости воспроизводства
path = []
for t in range(60):
    R_m = Y_f - r * A             # измеренная рента при рыночном якоре
    path.append({"t": t, "A": round(A, 2), "rA": round(r*A, 2), "R_measured": round(R_m, 4)})
    A = A + R_m                   # капитализация: цена вбирает измеренную ренту
A_star = Y_f / r                  # теоретический предел: PV всего потока
R_repro_anchor = Y_f - r * K_repro
OUT["T2"] = {
    "params": {"r": r, "Y": Y_f, "N_true": N_true, "R_true": R_true,
               "K_repro": round(K_repro, 2), "A_star_theory": round(A_star, 2)},
    "identity_check": {
        "R_with_repro_anchor": round(R_repro_anchor, 4),
        "equals_R_true": abs(R_repro_anchor - R_true) < 1e-9,
        "R_with_market_anchor_static": round(Y_f - r*(R_true/r), 4),
        "equals_N_true": abs((Y_f - r*(R_true/r)) - N_true) < 1e-9,
    },
    "dynamic_path_head": path[:3],
    "dynamic_path_tail": path[-3:],
    "measured_rent_vanishes": path[-1]["R_measured"] < 1.0,
    "extraction_unchanged": True,
    "complementary_split": "якорь воспроизводства даёт (R,N)=(70,30); рыночный якорь после капитализации даёт (0,100)"
}

# ============================================================
# T3: КЛАССИФИКАЦИЯ БЕЗ ИНСТИТУТОВ
# Один носитель Q: Y=100, N_true=30, R_true=70.
# Три изъятия: нормальная прибыль (30), налог 25, налог 90.
# Вопрос: различает ли СТРУКТУРА налог от ренты? Что различает вообще?
# ============================================================
def classify(X, R_true, N_true):
    covered_by_surplus = X <= R_true
    digs_into_normal   = X > R_true
    continuation = "C holds: изъятие покрывается излишком" if covered_by_surplus \
                   else "C FAILS: изъятие проедает нормальную отдачу -> деградация носителя (R15-B/C)"
    return {"X": X, "X<=R_true": covered_by_surplus, "digs_into_N": digs_into_normal,
            "verdict_by_structure_only": continuation}
OUT["T3"] = {
    "carrier": {"Y": 100.0, "N_true": 30.0, "R_true": 70.0},
    "normal_profit_30": classify(30.0, 70.0, 30.0),
    "tax_25":           classify(25.0, 70.0, 30.0),
    "tax_90":           classify(90.0, 70.0, 30.0),
    "observation": "структура различает лишь СОВМЕСТИМОСТЬ ИЗЪЯТИЯ С ПРОДОЛЖЕНИЕМ (X vs R_true); "
                   "налог 25 и рента 25 структурно НЕРАЗЛИМИМЫ — различие лежит в свойствах F (compulsory/unrequited vs claim), вне ядра"
}

# ============================================================
# T4: КВАЗИ-РЕНТА — КОНФЛИКТ ГЛУБИНЫ МАРЖИ
# Оборудование фиксированного предложения: Y=100.
# Избежимые издержки 40; невозвратные постоянные 50.
# Маржа short-run (избегать только переменных): R_sr = 100-40 = 60
# Маржа long-run (полное покрытие): R_lr = 100-90 = 10
# ============================================================
OUT["T4"] = {
    "Y": 100.0, "avoidable_cost": 40.0, "full_cost": 90.0,
    "R_short_margin": 60.0, "R_long_margin": 10.0,
    "ratio": 6.0,
    "meaning": "один и тот же поток даёт ренту 60 или 10 в зависимости от глубины маржи; "
               "критерий без правила выбора маржи конфундирует квази-ренту со scarcity-рентой"
}

# ============================================================
# T5: ЯКОРЬ СВОБОДНОГО ВХОДА
# Два рынка, одинаковый спрос. Вход свободен vs заблокирован лицензией.
# Вход бесплатен: n фирм, y_i = A - b*n; profit_i = y_i - N_entry.
# Вход, пока profit>0 -> n* где y* = N_entry -> R=0.
# Лицензия: n_max < n* -> y > N_entry -> R>0 устойчиво.
# ============================================================
def free_entry(A, b, N_entry, n_max=None, T=200):
    n = 1.0
    traj = []
    for t in range(T):
        y = A - b*n
        pi = y - N_entry
        traj.append({"t": t, "n": round(n,3), "y": round(y,2), "profit": round(pi,4)})
        if pi > 0 and (n_max is None or n < n_max):
            n += 0.5 * pi / max(abs(pi), 1.0) * 2.0   # вход пропорционален соблазну
            if n_max is not None: n = min(n, n_max)
        elif pi <= 0:
            n = max(n - 0.05, 1.0)
    return traj
A, b, N_entry = 200.0, 10.0, 50.0
n_star = (A - N_entry) / b          # 15 — равновесие свободного входа
open_mkt  = free_entry(A, b, N_entry, n_max=None)
lic_mkt   = free_entry(A, b, N_entry, n_max=8)
OUT["T5"] = {
    "n_star_free_entry": n_star,
    "open_entry_tail": open_mkt[-3:],
    "license_tail":    lic_mkt[-3:],
    "prediction": "R>0 <=> вход заблокирован; при свободном входе R->0 (сходится с R11-A: Гордон, рассеяние)",
    "anchor_rule": "Y^cf = отдача на марже свободного входа/воспроизводства носителя",
}

print(json.dumps(OUT, indent=1, ensure_ascii=False))
