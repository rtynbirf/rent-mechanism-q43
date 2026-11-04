#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R32 — ЧТО ИМЕННО ПЕРЕДАЁТСЯ ПРИ Q_t -> Q_{t+1}?

Задача: проверить цепочку Access_t -> Access_{t+1} -> Benefit_{t+1} при P_entry = 0.
Кандидат-инвариант I: REPRODUCIBLE EXCLUSIVE ACCESS TO ECONOMIC BENEFIT.

Модель (игрушечная, но с раздельными операторами):
  Q  = позиция доступа (структура принудительного исключения)
  E  = Exclusion: номинальная сила исключения других из доступа, 0..1
  C  = Control: сила аппарата, который ИСПОЛНЯЕТ исключение, 0..1
  S  = Scarcity: базовая редкость ресурса (природа/технология/спрос), 0..1
  T  = Transmission: протокол передачи позиции
       {market, appointment, kinship, none}
  B_t = ВЫГОДА РЕГЕНЕРИРУЕТСЯ, а не передаётся:
        B_t = SCALE * E_t * C_t * S_t
  net_t = B_t - MAINT*1[E_t>0 and C_t>0]   (позицию надо содержать)
  P_entry: market -> капитализация ~4 периодов; иначе 0

Метод: 6 атак-кейсов + формальные проверки (PASS/FAIL) + вердикт.
"""

G = 8          # горизонт: 8 поколений/периодов
SCALE = 100.0  # масштаб валовой выгоды
MAINT = 10.0   # периодическая стоимость содержания позиции
CAP_YEARS = 4  # горизонт капитализации при рыночной передаче


def B(E, C, S):
    """Выгода РЕГЕНЕРИРУЕТСЯ каждый период из структуры и редкости."""
    return SCALE * E * C * S


def net(E, C, S):
    b = B(E, C, S)
    cost = MAINT if (E > 0.0 and C > 0.0) else 0.0
    return b - cost


def head(title):
    print("\n" + "=" * 84)
    print(title)
    print("=" * 84)


def table(header, rows):
    w = 10
    print("".join(f"{h:>{w}}" for h in header))
    for r in rows:
        cells = []
        for v in r:
            if isinstance(v, str):
                cells.append(f"{v:>{w}}")
            else:
                cells.append(f"{v:>{w}.2f}")
        print("".join(cells))


RESULTS = {}


def check(name, cond, detail=""):
    status = "PASS" if cond else "FAIL"
    print(f"[{status}] {name}  {detail}")
    RESULTS[name] = bool(cond)
    return bool(cond)


# ----------------------------------------------------------------------
# CASE 1 — EMPTY-TITLE: титул передаётся, ресурс исчез (S -> 0)
# ----------------------------------------------------------------------
def case1_empty_title():
    head("CASE 1 — EMPTY-TITLE: Q передаётся (kinship, P_entry=0), но S->0 (рыба ушла)")
    E, C = 0.9, 0.9
    S_seq = [0.9, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    rows = [[f"g{g}", E, C, S_seq[g], B(E, C, S_seq[g]), net(E, C, S_seq[g])]
            for g in range(G)]
    table(["gen", "E", "C", "S", "B", "net"], rows)
    print("T = kinship: (E,C) передаются полностью в каждом поколении.")
    ok = (B(E, C, S_seq[0]) > 0) and all(B(E, C, s) == 0.0 for s in S_seq[1:])
    return check("C1: Q передан, (E,C)=const, но B=0 c g1", ok,
                 "-> 'доступ к выгоде' НЕ является передаваемым объектом")


# ----------------------------------------------------------------------
# CASE 2 — WINDFALL: выгода один раз, передачи нет (T = none)
# ----------------------------------------------------------------------
def case2_windfall():
    head("CASE 2 — WINDFALL: B(g0)>0 есть, T=none -> Q не передаётся")
    E0, C0, S0 = 0.9, 0.9, 0.9
    rows = [["g0", E0, C0, S0, B(E0, C0, S0), net(E0, C0, S0)],
            ["g1", "--", "--", "--", 0.0, 0.0]]
    table(["gen", "E", "C", "S", "B", "net"], rows)
    print("g1: T=none -> Q отсутствует -> B(g1)=0 при любой S.")
    ok = net(E0, C0, S0) > 0.0
    return check("C2: рента-эпизод есть, механизм Q_t->Q_{t+1} отсутствует", ok,
                 "-> REPRODUCIBLE требует T != none")


# ----------------------------------------------------------------------
# CASE 3 — MEDALLION-COLLAPSE: E схлопывается, титул юридически цел
# ----------------------------------------------------------------------
def case3_medallion_collapse():
    head("CASE 3 — MEDALLION-COLLAPSE: E: 0.9->0.1 на g3 (технология открыла доступ)")
    C, S = 0.9, 0.9
    E_seq = [0.9, 0.9, 0.9, 0.1, 0.1, 0.1, 0.1, 0.1]
    rows = [[f"g{g}", E_seq[g], C, S, B(E_seq[g], C, S), net(E_seq[g], C, S)]
            for g in range(G)]
    table(["gen", "E", "C", "S", "B", "net"], rows)
    V_before = CAP_YEARS * B(E_seq[2], C, S)   # вход по старой цене на g2->g3
    V_after = CAP_YEARS * B(E_seq[3], C, S)
    print(f"Капитализованная цена титула: V_before={V_before:.1f} -> V_after={V_after:.1f} "
          f"({100.0 * V_after / V_before:.0f}% от прежней)")
    print("Входивший на g2->g3 заплатил капитализацию СТАРОГО E и получил НОВЫЙ E.")
    ok = V_after / V_before < 0.2
    return check("C3: титул цел, V(Q) схлопнулся >80%", ok,
                 "-> рента живёт в ИСПОЛНЯЕМОМ исключении, а не в бумаге")


# ----------------------------------------------------------------------
# CASE 4 — APPARATUS-COLLAPSE: C схлопывается, E номинален, T = appointment
# ----------------------------------------------------------------------
def case4_apparatus_collapse():
    head("CASE 4 — APPARATUS-COLLAPSE: C: 0.9->0.05 на g2 (аппарат ушёл)")
    E, S = 0.9, 0.9
    C_seq = [0.9, 0.9, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05]
    rows = [[f"g{g}", E, C_seq[g], S, B(E, C_seq[g], S), net(E, C_seq[g], S)]
            for g in range(G)]
    table(["gen", "E", "C", "S", "B", "net"], rows)
    print("T = appointment продолжает работать каждое поколение (P_entry=0):")
    print("Q формально 'передаётся', но без аппарата исключение неисполнимо.")
    ok = B(E, C_seq[0], S) > 0.0 and net(E, C_seq[-1], S) <= 0.0
    return check("C4: T активен, но при C->0 рента умирает (net<=0)", ok,
                 "-> T несамодостаточен; C — несущая стена")


# ----------------------------------------------------------------------
# CASE 5 — CARRIER-SUBSTITUTION: носитель меняется, позиция постоянна
# ----------------------------------------------------------------------
def case5_carrier_substitution():
    head("CASE 5 — CARRIER-SUBSTITUTION: новый носитель каждое поколение, P_entry=0")
    E, C, S = 0.9, 0.9, 0.9
    holders = ["A", "B", "C", "D", "E2", "F", "G", "H"]
    Ts = ["appointment", "kinship", "appointment", "kinship",
          "appointment", "kinship", "appointment", "kinship"]
    rows = [[f"g{g}:{holders[g]}", E, C, S, B(E, C, S), net(E, C, S)]
            for g in range(G)]
    table(["gen", "E", "C", "S", "B", "net"], rows)
    print("Передачи: " + ", ".join(f"{holders[g]}->{holders[(g+1) % G]}({Ts[g]})"
                                    for g in range(G - 1)))
    cum = G * net(E, C, S)
    print(f"Кумулятивное чистое извлечение позиции за {G} поколений при P_entry=0: {cum:.1f}")
    ok = all(net(E, C, S) > 0.0 for _ in range(G))
    return check("C5: Access->Access->Benefit ДЕРЖИТСЯ при P_entry=0", ok,
                 "-> рента привязана к ПОЗИЦИИ, не к носителю")


# ----------------------------------------------------------------------
# CASE 6 — INTERRUPTED-RESUMED: S=0 два поколения, затем восстановлена
# ----------------------------------------------------------------------
def case6_interrupted_resumed():
    head("CASE 6 — BENEFIT-INTERRUPTED-RESUMED: S=0 на g3..g4, восстановлена на g5")
    E, C = 0.9, 0.9
    S_seq = [0.9, 0.9, 0.9, 0.0, 0.0, 0.9, 0.9, 0.9]
    rows = [[f"g{g}", E, C, S_seq[g], B(E, C, S_seq[g]), net(E, C, S_seq[g])]
            for g in range(G)]
    table(["gen", "E", "C", "S", "B", "net"], rows)
    print("T = kinship: Q передаётся g2->g3 и g3->g4 даже при B=0 (титул держат 'в резерве').")
    print("На g5 B восстановился БЕЗ нового акта передачи (реституционный контур).")
    ok = B(E, C, S_seq[3]) == 0.0 and B(E, C, S_seq[5]) > 0.0
    return check("C6: B восстановился без нового T-акта", ok,
                 "-> выгода РЕГЕНЕРИРУЕТСЯ, а не наследуется")


# ----------------------------------------------------------------------
# SENSITIVITY: множительная структура V(Q) ~ E*C*S
# ----------------------------------------------------------------------
def sensitivity_grid():
    head("ЧУВСТВИТЕЛЬНОСТЬ B = SCALE*E*C*S: сетка E x C при S=0.9")
    Es = [1.0, 0.75, 0.5, 0.25, 0.05]
    Cs = [1.0, 0.75, 0.5, 0.25, 0.05]
    hdr = ["E\\C"] + [f"{c:.2f}" for c in Cs]
    rows = []
    for e in Es:
        rows.append([f"{e:.2f}"] + [B(e, c, 0.9) for c in Cs])
    table(hdr, rows)
    print("Вывод: ни E, ни C по отдельности не несут выгоду — произведение.")
    print("Номинальное E без исполняющего C даёт ноль так же, как C без E.")


def main():
    print(f"R32 — ЧТО ПЕРЕДАЁТСЯ ПРИ Q_t -> Q_(t+1)?  "
          f"(песочница: G={G}, SCALE={SCALE:.0f}, MAINT={MAINT:.0f}, CAP={CAP_YEARS} пер.)")
    r = {}
    r["C1"] = case1_empty_title()
    r["C2"] = case2_windfall()
    r["C3"] = case3_medallion_collapse()
    r["C4"] = case4_apparatus_collapse()
    r["C5"] = case5_carrier_substitution()
    r["C6"] = case6_interrupted_resumed()
    sensitivity_grid()

    head("ФОРМАЛЬНЫЙ ВЕРДИКТ R32")
    for k, v in r.items():
        print(f"  {k}: {'PASS' if v else 'FAIL'}")
    n_pass = sum(r.values())
    print(f"\nПроверок пройдено: {n_pass}/{len(r)}")

    print("""
ДЕКОМПОЗИЦИЯ ИНВАРИАНТА I = 'REPRODUCIBLE EXCLUSIVE ACCESS TO ECONOMIC BENEFIT':

  Компонент         Слой       Передаётся?   Доказательство
  ----------------  ---------  ------------  --------------
  ACCESS (Q)        объект     ДА, через T   C5
  EXCLUSIVE (E)     объект     ДА, при C>0   C3, C4
  BENEFIT (B)       состояние  НЕТ           C1, C6
  REPRODUCIBLE (T)  оператор   ДА, T!=P_entry, T умирает без C   C2, C4

  H1  ->  H1':
    ПЕРЕДАЁТСЯ:  Q = (E-механизм, C-механизм, T-протокол)
    РЕГЕНЕРИРУЕТСЯ:  B_t = SCALE * E_t * C_t * S_t   (условно на редкость S_t)
    рента в t  <=>  B_t > MAINT
    P_entry in T, но T != P_entry (цена — лишь один оператор передачи)

  СТАТУС:
    I как СИСТЕМНЫЙ инвариант (условие на состояние в каждом t):  CONFIRMED
    I как ОБЪЕКТНЫЙ инвариант (описание передаваемого):  REFUTED (BREAKER)
""")

    import json
    with open("/home/z/my-project/scripts/r32_results.json", "w") as f:
        json.dump({"passed": r, "G": G, "SCALE": SCALE, "MAINT": MAINT}, f,
                  ensure_ascii=False, indent=2)
    print("Сохранено: /home/z/my-project/scripts/r32_results.json")


if __name__ == "__main__":
    main()
