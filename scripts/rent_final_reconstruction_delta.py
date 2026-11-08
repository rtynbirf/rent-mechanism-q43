# -*- coding: utf-8 -*-
# ЗАДАЧА 6: дельта-проверка ветки "ФИНАЛЬНАЯ РЕКОНСТРУКЦИЯ (Lumo, web-route)"
# против канонической цепи v2.3. 5 тестов: T-F1..T-F5.
import math, random

def card(tid, inp, method, expected, actual, status, lim="-"):
    print(f"\n=== {tid} ===")
    print(f"INPUT:    {inp}")
    print(f"METHOD:   {method}")
    print(f"EXPECTED: {expected}")
    print(f"ACTUAL:   {actual}")
    print(f"STATUS:   {status}")
    if lim != "-": print(f"LIMITS:   {lim}")

R, EPS, H, DA, PHI0, C = 0.35, 0.5, 0.3, 0.05, 0.3, 0.5

def two_sector(phi, steps=800, S0=0.9, A0=0.4, eps=EPS):
    S, A = S0, A0
    for _ in range(steps):
        E = eps * S * A / (H + A) if (S > 0 and A > 0) else 0.0
        S = max(0.0, S + R * S * (1 - S) - E)
        A = max(0.0, (1 - DA) * A + phi * E - C * A * A)
        if A <= 1e-9: return S, 0.0, 0.0, False
    E_star = eps * S * A / (H + A) if (S > 0 and A > 0) else 0.0
    return S, A, E_star, True

# T-F1: Meade (1-cc)r>g: доля потреблённой ренты cc=1-phi как бифуркационный параметр
def tf1():
    rows, lo, hi = [], None, None
    for i in range(0, 31):
        phi = i / 30.0
        S, A, E, ok = two_sector(phi)
        cc = 1 - phi
        rows.append((phi, cc, A, E, ok))
        if ok and phi > 0.02 and lo is None: lo = (phi, cc, A, E)
        if ok: hi = (phi, cc, A, E)
    # аналитический нижний порог: стационарность A требует phi*E* >= delta_A*A + c*A^2,
    # в аттракторе T7.1 E*=0.08687, A*=0.18371: phi_min ~ (DA*A+C*A^2)/E
    A0_, E0_ = 0.18371, 0.08687
    phi_min = (DA * A0_ + C * A0_ ** 2) / E0_
    surv = sum(1 for r_ in rows if r_[4])
    print("phi(cc=1-phi) sweep: выживание аппарата A:")
    for phi, cc, A, E, ok in rows[::3]:
        print(f"  phi={phi:.2f} cc={cc:.2f} -> A*={A:.4f} {'SURVIVE' if ok else 'COLLAPSE'}")
    card("T-F1_meade_cc_bifurcation",
         f"2-секторная модель T7.1 (r=0.35, eps=0.5, h=0.3, dA=0.05, c=0.5); phi=доля реинвеста ренты; cc=1-phi",
         "свип phi 0..1 (31 точка, 800 шагов) + аналитический порог phi_min=(dA*A*+c*A*^2)/E*",
         "существует phi_min: ниже аппарат вымирает (цикл ренты условен), выше — устойчив; cc — бифуркационный параметр (Lumo t10/t13, Meade (1-cc)r>g)",
         f"phi_min(аналит.)={phi_min:.3f} (cc_max={1-phi_min:.3f}); моделирование: SURVIVE при phi>~{lo[0]:.2f} (cc<~{lo[1]:.2f}), COLLAPSE ниже; выживших точек {surv}/31",
         "SUPPORTED" if surv > 5 and surv < 31 else "CHECK")
    return phi_min

# T-F2: типы редкости A/B (Lumo t16): снятие правила -> редистрибуция vs исчезновение потока
def tf2():
    def run_1d(eps, F, steps=600, S0=0.9):
        S = S0
        for _ in range(steps):
            S = max(0.0, min(1.0, S + R * S * (1 - S) - eps * S - F))
        return S
    # режим с позицией: eps=0.18, F=0.01 (аттрактор существует)
    S_with = run_1d(0.18, 0.01)
    # ТИП B (патент/платформа): правило снято -> редкость исчезает -> поток к нулю (eps->0)
    S_B = run_1d(0.0, 0.0)
    # ТИП A (земля/локация): правило снято -> редкость остаётся -> поток редистрибутируется
    # (изъятие продолжается теми, кто фактически держит ресурс; позиция децентрализована)
    S_A = run_1d(0.18, 0.0)
    card("T-F2_scarcity_typeAB",
         "1D-редукция (r=0.35); с позицией: eps=0.18,F=0.01; тип B: правило снято -> eps=0; тип A: позиция снята, редкость жива -> eps=0.18,F=0",
         "итерация 600 шагов по трём режимам",
         "A: S падает относительно аттрактора (поток остаётся, концентрация исчезает); B: S -> несущая ёмкость (поток исчезает целиком)",
         f"с позицией: S*={S_with:.3f}; ТИП A (редистрибуция): S={S_A:.3f} (поток сохранён, собирателя нет); ТИП B (исчезновение): S={S_B:.3f} ~ K=1",
         "SUPPORTED" if (S_B > 0.95 and S_A < S_B - 0.25 and S_A < S_with) else "CHECK",
         "в 1D редистрибуция A видна как отсутствие концентрации; 2-секторная проверка не проводилась")

# T-F3: диссипация (Tullock): утечка lambda из потока на обход позиции
def tf3():
    lam_lo, lam_hi = 0.0, 0.18   # ищем lambda*, при которой позиция перестаёт кормить аппарат
    def attractor(lam, steps=800):
        S, A = 0.9, 0.4
        for _ in range(steps):
            E = max(0.0, (EPS - lam)) * S * A / (H + A) if (S > 0 and A > 0) else 0.0
            S = max(0.0, S + R * S * (1 - S) - E)
            A = max(0.0, (1 - DA) * A + PHI0 * E - C * A * A)
            if A <= 1e-9: return S, 0.0
        return S, A
    rows = []
    for lam in [0.0, 0.10, 0.20, 0.30, 0.40, 0.45, 0.48, 0.50, 0.52]:
        S, A = attractor(lam)
        rows.append((lam, S, A, A > 1e-6))
    # порог: eps_eff = EPS - lam <= 0 -> поток нулевой; и выживание A требует eps_eff достаточного
    card("T-F3_dissipation_leakage",
         "2-секторная модель; lambda = доля потока, сжигаемая обходчиками позиции (Tullock/Krueger; эмп. платформенный leakage +3.2..+4.4 п.п.)",
         "eps_eff = EPS - lambda; свип lambda, 800 шагов",
         "рост lambda снижает E* и A*; при lambda ~ EPS позиция не генерирует ренту вовсе",
         "; ".join(f"lam={l:.3f}:S={s:.3f},A={a:.4f},{'SURV' if ok else 'COLL'}" for l, s, a, ok in rows),
         "SUPPORTED" if rows[-1][2] <= 1e-6 and rows[0][2] > 0.1 else "CHECK",
         "линейная утечка — нижняя оценка; реальная диссипация возвращает ресурсы конкурентам (рекурсия не смоделирована)")

# T-F4: суверенный haircut ~45%: потеря потока кредитором НЕ убивает позицию
def tf4():
    def run(shock_at=None, haircut=0.45, steps=1200):
        S, A = 0.9, 0.4
        traj = []
        for t in range(steps):
            E = EPS * S * A / (H + A) if (S > 0 and A > 0) else 0.0
            if shock_at is not None and t == shock_at:
                A = A * (1 - haircut)          # кредитор теряет 45% позиции
            S = max(0.0, S + R * S * (1 - S) - E)
            A = max(0.0, (1 - DA) * A + PHI0 * E - C * A * A)
            traj.append((S, A))
        return traj[-1], traj
    (S0_, A0_), tr0 = run(None)
    (S1_, A1_), tr1 = run(shock_at=300)
    # время возврата A к 0.9*A0_attr
    target = 0.9 * A0_
    t_rec = None
    for t in range(300, len(tr1)):
        if tr1[t][1] >= target: t_rec = t - 300; break
    card("T-F4_haircut_persistence",
         f"аттрактор T7.1; в t=300 позиция кредитора режется на {int(0.45*100)}% (средний haircut 1815-2020, Kiel/HKS)",
         "итерация 1200 шагов, сравнение с ненарушенной траекторией",
         "аттрактор восстанавливается (A* возвращается ~к 0.1837): потеря потока кредитором не разрушает ПОЗИЦИЮ — согласуется с Mesopotamia/haircut-веткой и 'держатель смертен, позиция persists'",
         f"без шока: A*={A0_:.4f}; с haircut -45%: A в конце={A1_:.4f}, восстановление до 0.9*A* за {t_rec} шагов, S*={S1_:.4f}",
         "SUPPORTED" if (A1_ > 0.9 * A0_ and S1_ > 0.35) else "CHECK",
         "модель без смены класса держателя; повторяемость реструктуризаций не смоделирована")

# T-F5: земля растёт ВНУТРИ стабильной доли капитала (Knoll et al.: x2 за 1930-2010)
def tf5():
    kappa = 0.301            # capital share (Tax Foundation, среднее 1929-Q2'23)
    land1930, land2010 = 0.175, 0.35   # доля земли в цене жилья США: рост ~x2 (Knoll-Schularick-Steeger)
    # рентная компонента в нац. доходе = kappa * land_share * housing_weight(0.123 GDP, NAHB) * Y
    hw = 0.123
    r1930 = kappa * land1930 * hw
    r2010 = kappa * land2010 * hw
    drift = r2010 / r1930
    card("T-F5_land_inside_capital",
         "kappa=30.1% (капитальная доля стабильна 1929-2023); доля земли в цене жилья США 17.5%->35% (Knoll et al., x2 за 1930-2010); housing=12.3% ВВП (NAHB)",
         "арифметическое разложение рентного потока: R = kappa * land_share * housing_weight * Y",
         "факторная доля капитала НЕ РАСТЁТ, а рентный поток внутри неё удваивается — спор 'labor share stable vs rentier rise' разрешается как артефакт агрегации",
         f"рентный поток (земельная компонента): {r1930*100:.2f}% Y (1930) -> {r2010*100:.2f}% Y (2010), рост x{drift:.2f} при стабильной kappa",
         "DERIVED (иллюстративно на опубликованных магнитудах)",
         "не эмпирическая оценка; land share взята грубо (Knoll даёт диапазон); France 40%->60% (2000-2010) даёт ещё более резкий дрейф")

if __name__ == "__main__":
    print("ДЕЛЬТА-ТЕСТЫ: ФИНАЛЬНАЯ РЕКОНСТРУКЦИЯ (Lumo web-route) x цепь v2.3")
    tf1(); tf2(); tf3(); tf4(); tf5()
    print("\nИТОГО: 5 тестов исполнено.")
