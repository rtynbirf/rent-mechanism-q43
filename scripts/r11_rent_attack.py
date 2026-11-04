#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R11 — АТАКА НА КАНДИДАТ-ИНВАРИАНТ (B,P) → F → (B',P')
Цель: сломать, а не подтвердить.
Ветви:
  A  Rent без P            — Гордон-Шеффер, dissipation
  B  P при нулевой ренте   — спящая позиция в мёртвом рынке
  C  (веб-ветка, вне скрипта)
  D  F → P'                — связная динамика реинвестирования
  E  Необходимость цикла   — машина состояний dormant/active/transfer
"""
import json, math

OUT = {}

# ============================================================
# R11-A: МОЖЕТ ЛИ СУЩЕСТВОВАТЬ УСТОЙЧИВАЯ РЕНТА БЕЗ P?
# Модель Гордона-Шеффера: open access vs контролируемый доступ
#   dX/dt = r*X*(1 - X/K) - q*E*X
#   rent_pi(t) = (p*q*X - c) * E        <- поток захваченной ренты
#   open access: dE/dt = phi * pi      <- вход при pi>0, выход при pi<0
# ============================================================
def gordon_schaefer(r, K, q, p, c, E0, open_access, phi=0.3, T=300, X0=None):
    if X0 is None: X0 = 0.9*K
    X, E = X0, E0
    dt = 0.05
    cum_capture = 0.0
    potential_cum = 0.0
    hist = []
    for t in range(T):
        steps = int(1/dt)
        for _ in range(steps):
            X = max(X + dt*(r*X*(1-X/K) - q*E*X), 1e-9)
            pi = (p*q*X - c)*E
            potential = p*q*X - c          # потенциальная рента на единицу усилия
            cum_capture += pi*dt
            if potential > 0: potential_cum += potential*dt
            if open_access:
                E = max(E + dt*phi*pi, 0.0)
        hist.append((t, X, E, (p*q*X-c)*E, p*q*X-c))
    X_eq = c/(p*q) if p*q > 0 else None
    return {"X_final": X, "E_final": E,
            "rent_final": (p*q*X-c)*E, "rent_potential_final": p*q*X-c,
            "X_bioeconomic_eq": X_eq, "cum_capture": cum_capture,
            "cum_potential": potential_cum, "hist_last": hist[-1]}

A_open  = gordon_schaefer(r=0.4, K=100.0, q=0.02, p=10.0, c=5.0, E0=1.0, open_access=True)
A_mey   = gordon_schaefer(r=0.4, K=100.0, q=0.02, p=10.0, c=5.0, E0=8.0, open_access=False)
OUT["R11_A"] = {
    "open_access":  A_open,
    "controlled":   A_mey,
    "verdict_data": {
        "open_access_rent_final": A_open["rent_final"],
        "open_access_rent_potential_final": A_open["rent_potential_final"],
        "open_access_biomass_eq": A_open["X_bioeconomic_eq"],
        "X_be = c/(pq) = 5/(10*0.02)": 25.0,
        "controlled_rent_final": A_mey["rent_final"],
        "ratio_cum_capture": A_mey["cum_capture"]/max(A_open["cum_capture"],1e-12)
    }
}

# ============================================================
# R11-B: МОЖЕТ ЛИ БЫТЬ P=1 ПРИ НУЛЕВОЙ РЕНТЕ?
# Позиция постоянна, рента следует за спросом (циклы+шоки).
# F_t = P_t * R_t ; проверяем таблицу истинности и поток.
# ============================================================
def r11_b(T=48):
    P = 1.0
    rows = []
    for t in range(T):
        # рентный потенциал: сезонный цикл + структурный крах в t=20..27
        R = 0.5 + 0.5*math.sin(2*math.pi*t/12)
        if 20 <= t < 28: R = 0.0
        F = P * R
        rows.append({"t": t, "P": P, "R": round(R,4), "F": round(F,4),
                     "case": "P=1,R=0 -> F=0" if R==0 else ("P=1,R>0 -> F>0")})
    zeros = [r for r in rows if r["R"]==0]
    return {"rows": rows, "n_zero_R": len(zeros),
            "max_F_when_R_zero": max(r["F"] for r in zeros),
            "truth_table": [{"P":1,"R":0,"F":0},{"P":1,"R":1,"F":1},
                            {"P":0,"R":1,"F":0},{"P":0,"R":0,"F":0}]}
OUT["R11_B"] = r11_b()

# ============================================================
# R11-D: МОЖЕТ ЛИ F САМ СОЗДАТЬ НОВУЮ P' (И B')?
# Связная динамика: реинвестирование потока в позицию и в базу.
#   P_{t+1} = P_t + a*F_t - d*P_t        (лоббизм/приобретение/залог)
#   B_{t+1} = B_t + b*F_t                (расширение рентонесущей базы)
#   R_t = R0*B_t/100  (масштаб),  F_t = P_t*R_t
# Пороговая фазовая диаграмма по (a, R0).
# ============================================================
def r11_d(a, d, b, R0, T=40, P0=0.2, B0=100.0):
    P, B = P0, B0
    traj = []
    for t in range(T):
        R = R0*B/100.0
        F = P*R
        traj.append((t, round(P,4), round(B,1), round(R,4), round(F,4)))
        P = P + a*F - d*P
        B = B + b*F
        P = min(P, 1.0) if a*F - d*P >= 0 else P
        if P < 1e-12: P = 0.0
    return traj

D_dead   = r11_d(a=0.10, d=0.15, b=0.0,  R0=0.50)   # a*R0 < d  -> режим умирает
D_alive  = r11_d(a=0.40, d=0.15, b=0.0,  R0=0.50)   # a*R0 > d  -> самоподдержка
D_expand = r11_d(a=0.40, d=0.15, b=0.05, R0=0.50)   # + расширение базы
threshold = 0.15/0.40   # R0* = d/a
OUT["R11_D"] = {
    "threshold_R0": threshold,
    "meaning": "R0 > d/a: поток компенсирует распад позиции -> режим самовоспроизводится",
    "dead_regime_last5":  D_dead[-5:],
    "alive_regime_last5": D_alive[-5:],
    "expand_regime_last5":D_expand[-5:],
    "dead_P_path":  [r[1] for r in D_dead],
    "alive_P_path": [r[1] for r in D_alive],
    "expand_B_path":[r[2] for r in D_expand]
}

# ============================================================
# R11-E: ЯВЛЯЕТСЯ ЛИ ЦИКЛ Q -> F -> Q' НЕОБХОДИМЫМ?
# Машина состояний: Q=(B,P); спад спроса t=15..39 (R=0).
#  (a) DORMANT-HOLD: позиция удерживается обслуживанием (m из
#      внешних источников); F=0 весь спад; поток ВОЗОБНОВЛЯЕТСЯ.
#  (b) NO-MAINTENANCE: P распадается (P*=0.88^k); поток НЕ вернётся.
#  (c) TRANSFER: нацнационализация t=20: P_old->0, P_new=1; поток
#      продолжается к новому держателю (держатель не инвариант).
#  (d) OBSOLESCENCE: B уничтожен заменой технологии -> R=0 навсегда.
# ============================================================
def r11_e(T=60):
    rows = []
    # (a) dormant hold
    P, R, F = 1.0, 1.0, 0.0
    for t in range(T):
        R = 0.0 if 15 <= t < 40 else 1.0
        F = P*R
        rows.append({"mode":"dormant_hold","t":t,"P":P,"R":R,"F":F})
    # (b) decay of position
    P2 = 1.0
    for t in range(T):
        R = 0.0 if 15 <= t < 40 else 1.0
        if 15 <= t < 40: P2 *= 0.88
        F2 = P2*R
        rows.append({"mode":"no_maintenance","t":t,"P":round(P2,4),"R":R,"F":round(F2,4)})
    # (c) transfer at t=20
    P_old, P_new = 1.0, 0.0
    for t in range(T):
        R = 1.0
        if t == 20: P_old, P_new = 0.0, 1.0
        F3 = (P_new)*R
        rows.append({"mode":"transfer","t":t,"P_old":P_old,"P_new":P_new,"R":R,"F":F3})
    # (d) obsolescence
    P4, R4 = 1.0, 1.0
    for t in range(T):
        if t == 15: R4 = 0.0   # технология уничтожила базу
        F4 = P4*R4
        rows.append({"mode":"obsolescence","t":t,"P":P4,"R":R4,"F":F4})
    return rows

E_rows = r11_e()
E = {m: [r for r in E_rows if r["mode"]==m] for m in ("dormant_hold","no_maintenance","transfer","obsolescence")}
OUT["R11_E"] = {
    "dormant_resume_flow_t40_plus": [r["F"] for r in E["dormant_hold"][40:45]],
    "dormant_F_during_collapse":    [r["F"] for r in E["dormant_hold"][15:20]],
    "no_maint_P_at_t39": E["no_maintenance"][39]["P"],
    "no_maint_F_after_recovery": [r["F"] for r in E["no_maintenance"][40:45]],
    "transfer_F_after_t20": [ (r["t"], r["P_new"], r["F"]) for r in E["transfer"][19:25] ],
    "obsolescence_F_tail": [r["F"] for r in E["obsolescence"][-3:]]
}

print(json.dumps(OUT, indent=1, ensure_ascii=False))
