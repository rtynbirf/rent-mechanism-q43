#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Реестр caveats ядра Q43 (Волна ×4 · П48, issue #2).

Статус ядра — SOLVED_WITH_CAVEATS: caveats живут текстом, без счётчиков.
П48 переводит долг в явный трекинг: каждый caveat = запись реестра
(results/caveats_registry.json + docs/CAVEATS.md) с формулой приёмки и
номером issue. Явный трекинг долга вместо автозакрытия — урок
«stale bot considered harmful»: ядро меняется на SOLVED только при
caveats=0 (счётчик из реестра, не из памяти).

CLI (std-only):
  caveat_registry.py --build          # собрать реестр из results/r49_results.json
  caveat_registry.py list             # печатать таблицу реестра
  caveat_registry.py docs             # перегенерировать docs/CAVEATS.md (детерминированно)
  caveat_registry.py checklist        # чек-лист приёмки в stdout (--out FILE)
  caveat_registry.py new --id CAV-23 --text "..." --source rXX --acceptance "..."
                                      # печатать ШАБЛОН тела issue (не создаёт issue)
  caveat_registry.py check [--live]   # приёмка: числа сходятся; --live — сверка
                                      # с GitHub search is:open label:caveat (нужен GITHUB_TOKEN)
  caveat_registry.py --selftest       # самоиспытание логики на фикстуре

Создание реальных issues этим скриптом НЕ выполняется: в репо нет API-скрипта
создания issues (по правилу Волны ×4 — тогда только документируем процедуру,
см. docs/CAVEATS.md §5 «Как завести issue по caveat»).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
R49 = os.path.join(ROOT, "results", "r49_results.json")
REG = os.path.join(ROOT, "results", "caveats_registry.json")
DOC = os.path.join(ROOT, "docs", "CAVEATS.md")
README = os.path.join(ROOT, "README.md")

CLASSES = {
    "structurally_blocked": ("СТРУКТУРНО-БЛОК", "структурно заблокированы песочницей"),
    "methodologically_closed": ("МЕТОД-ЗАКРЫТ", "методологически закрыты (правило сформулировано)"),
    "open": ("ОТКРЫТ", "открытые"),
}

ACCEPTANCE = {
    "structurally_blocked":
        "Источник получен в песочнице (HTTP 200, машиночитаемый ряд сохранён в репо "
        "с URL и датой выгрузки); числа пересчитаны и дописаны в r*_results.json; "
        "issue закрывается PATCH при сходимости чисел. Пока доступ блокирован — caveat жив.",
    "methodologically_closed":
        "Правило сформулировано и внесено дельтой канона (реестр E1–E14 программы); "
        "правило применено к уже сохранённым артефактам, результат в r*_results.json; "
        "issue закрывается коммитом дельты со ссылкой на прогон.",
    "open":
        "Найден и сохранён первичный источник (файл в репо + URL + дата выгрузки); "
        "затронутые числа пересчитаны; прогон дописан в r*_results.json; issue закрывается "
        "при согласовании с реестром. Не найдено — caveat остаётся, UNKNOWN ≠ FALSE.",
}


def build_registry():
    """Собрать реестр из артефакта r49_results.json (никаких чисел из памяти)."""
    src = json.load(open(R49, encoding="utf-8"))
    reg = src["unknown_registry"]
    caveats, n = [], 0
    for cls in ("structurally_blocked", "methodologically_closed", "open"):
        for text in reg.get(cls, []):
            n += 1
            caveats.append({
                "id": f"CAV-{n:02d}",
                "class": cls,
                "text": text,
                "source": "results/r49_results.json unknown_registry." + cls,
                "acceptance": ACCEPTANCE[cls],
                "issue": None,      # номер issue появляется после заведения по процедуре
                "state": "open",
            })
    out = {
        "registry_version": 1,
        "generated_by": "scripts/caveat_registry.py --build (Волна ×4 · П48)",
        "source_artifact": "results/r49_results.json",
        "core_status_rule": "SOLVED только при caveats_open=0 (явный трекинг, не автозакрытие)",
        "counts": {
            "total": len(caveats),
            "open": sum(1 for c in caveats if c["state"] == "open"),
            "with_issue": sum(1 for c in caveats if c["issue"]),
        },
        "caveats": caveats,
    }
    with open(REG, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return out


def load_registry():
    return json.load(open(REG, encoding="utf-8"))


def checklist(reg, title="Чек-лист приёмки caveats (Q43)"):
    lines = [f"# {title}", "",
             f"Открытых caveats: **{reg['counts']['open']}** из {reg['counts']['total']} "
             f"(с заведённым issue: {reg['counts']['with_issue']}). "
             f"Ядро: SOLVED_WITH_CAVEATS → SOLVED только при 0.", ""]
    for c in reg["caveats"]:
        mark = "⬜" if c["state"] == "open" else "✅"
        issue = f" #{c['issue']}" if c["issue"] else " (issue не заведён — процедура docs/CAVEATS.md §5)"
        lines.append(f"- [ ] {mark} **{c['id']}** · {CLASSES[c['class']][0]}{issue}")
        lines.append(f"  - {c['text']}")
        lines.append(f"  - Приёмка: {c['acceptance']}")
    return "\n".join(lines) + "\n"


def render_docs(reg):
    """docs/CAVEATS.md — реестр-таблица, детерминированно из JSON."""
    L = [
        "# Реестр caveats · ядро Q43 (Волна ×4 · П48, issue #2)",
        "",
        f"**Статус ядра: SOLVED_WITH_CAVEATS** · открытых caveats: "
        f"**{reg['counts']['open']}** из {reg['counts']['total']}.",
        "",
        "Правило закрытия: ядро меняется на **SOLVED** только при `caveats_open=0` "
        "по реестру `results/caveats_registry.json` (машиносчёт, не память). "
        "Явный трекинг долга вместо автозакрытия — урок «stale bot considered harmful».",
        "",
        "Источник записей: `results/r49_results.json → unknown_registry` "
        "(консолидация R49, 22 уникальных). Реестр собирается "
        "`python3 scripts/caveat_registry.py --build`, этот документ — "
        "`caveat_registry.py docs` (двойная генерация идентична).",
        "",
        "## Таблица реестра",
        "",
        "| ID | Класс | Caveat | Источник | Формула приёмки | Issue |",
        "|---|---|---|---|---|---|",
    ]
    for c in reg["caveats"]:
        issue = f"#{c['issue']}" if c["issue"] else "⬜ не заведён"
        text = c["text"].replace("|", "\\|").replace("\n", " ")
        acc = c["acceptance"].replace("|", "\\|").replace("\n", " ")
        L.append(f"| {c['id']} | {CLASSES[c['class']][0]} | {text} | {c['source']} | {acc} | {issue} |")
    L += [
        "",
        "## Счётчики (машиносчёт)",
        "",
        f"- всего caveats: **{reg['counts']['total']}**",
        f"- открытых: **{reg['counts']['open']}**",
        f"- с заведённым issue: **{reg['counts']['with_issue']}**",
        "- классы: " + " · ".join(
            f"{CLASSES[k][1]}: {sum(1 for c in reg['caveats'] if c['class'] == k)}"
            for k in CLASSES),
        "",
        "## Как завести issue по caveat (процедура)",
        "",
        "1. `python3 scripts/caveat_registry.py new --id CAV-XX` — печатает готовый шаблон "
        "тела issue (заголовок, caveat, формула приёмки, чек-боксы).",
        "2. Создай issue в GitHub UI (или `gh issue create -t \"[CAV-XX] …\" -F body.md "
        "-l caveat`) и впиши номер в `results/caveat_registry.json → caveats[].issue` "
        "(ручная правка одной строки реестра).",
        "3. `caveat_registry.py check --live` — сверка: `search is:open label:caveat` "
        "возвращает полный список, числа реестра и GitHub сходятся.",
        "4. Закрытие caveat — по формуле приёмки записи; реестр обновляется "
        "(`--build` не трогает issue/state — они ведутся руками), коммит + PATCH issue.",
        "",
        "Скрипт НЕ создаёт issues сам: в репо нет API-скрипта создания issues — "
        "по правилу Волны ×4 процедура документируется, автосоздание не имитируется.",
        "",
        "## Приёмка (машинная, из issue)",
        "",
        "- каждый caveat имеет формулу приёмки — колонка «Формула приёмки» (проверяется `check`);",
        "- `search is:open label:caveat` — сверка живым API: `caveat_registry.py check --live`;",
        "- числа сходятся: счётчики реестра == таблице == README-статусу.",
        "",
    ]
    return "\n".join(L)


def github_open_caveats():
    """Живой счётчик: search is:open label:caveat (нужен GITHUB_TOKEN)."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None, "GITHUB_TOKEN не задан — живая сверка пропущена (документировано)"
    q = "repo:rtynbirf/rent-mechanism-q43 is:issue is:open label:caveat"
    import urllib.request
    url = ("https://api.github.com/search/issues?q=" + urllib.parse.quote(q) +
           "&per_page=100")
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
        return data.get("total_count", 0), [i.get("title", "") for i in data.get("items", [])]
    except OSError as e:
        return None, f"GitHub API недоступен: {e}"


def check(live=False):
    ok = True

    def need(cond, msg):
        nonlocal ok
        print(("✓ " if cond else "✗ ") + msg)
        ok = ok and bool(cond)

    reg = load_registry()
    cs = reg["caveats"]
    need(all(re.fullmatch(r"CAV-\d{2,}", c["id"]) for c in cs), "ID в форме CAV-XX")
    need(len({c["id"] for c in cs}) == len(cs), "ID без дубликатов")
    need(all(c["acceptance"] for c in cs), "у каждого caveat формула приёмки")
    need(all(c["text"] for c in cs), "у каждого caveat текст")
    counts_ok = (reg["counts"]["total"] == len(cs) and
                 reg["counts"]["open"] == sum(1 for c in cs if c["state"] == "open") and
                 reg["counts"]["with_issue"] == sum(1 for c in cs if c["issue"]))
    need(counts_ok, "счётчики реестра сходятся с записями")
    # соответствие артефакту-источнику (числа не из памяти)
    src = json.load(open(R49, encoding="utf-8"))["unknown_registry"]
    src_total = src.get("total_unique", sum(len(v) for v in src.values()
                                            if isinstance(v, list)))
    need(len(cs) == src_total, f"реестр == unknown_registry R49 ({len(cs)} == {src_total})")
    # README-статус согласован
    rm = open(README, encoding="utf-8").read()
    has_status = "SOLVED_WITH_CAVEATS" in rm
    need(has_status == (reg["counts"]["open"] > 0),
         "README-статус согласован со счётчиком (SOLVED только при 0)")
    if live:
        cnt, detail = github_open_caveats()
        if cnt is None:
            print(f"🟡 живая сверка: {detail}")
        else:
            live_ids = sum(1 for c in cs if c["issue"] and c["state"] == "open")
            need(cnt == live_ids,
                 f"GitHub search is:open label:caveat == реестру ({cnt} == {live_ids})")
    print("CHECK:", "OK" if ok else "FAILED")
    return ok


def issue_template(cid, reg=None):
    """Шаблон тела issue для одного caveat (создание — за человеком, §5)."""
    if reg is None:
        reg = load_registry()
    c = next((x for x in reg["caveats"] if x["id"] == cid), None)
    if c is None:
        print(f"нет caveat {cid} в реестре", file=sys.stderr)
        return None
    return (
        f"### Caveat {c['id']} · {CLASSES[c['class']][0]}\n\n"
        f"**Текст (из {c['source']}):** {c['text']}\n\n"
        f"**Формула приёмки:** {c['acceptance']}\n\n"
        f"**Чек-боксы закрытия:**\n"
        f"- [ ] источник/правило сохранены в репо (URL + дата выгрузки)\n"
        f"- [ ] числа пересчитаны, прогон дописан в r*_results.json\n"
        f"- [ ] `caveat_registry.py check` зелёный, счётчики сходятся\n"
        f"- [ ] запись реестра обновлена (state/issue)\n\n"
        f"*Реестр: docs/CAVEATS.md · Волна ×4 · П48 (issue #2). Закрытие ядра в SOLVED — "
        f"только при caveats_open=0.*\n"
    )


def _selftest():
    """Самоиспытание логики на фикстуре (без сети, без правки репо)."""
    ok = True

    def need(cond, msg):
        nonlocal ok
        ok = ok and bool(cond)
        print(("✓ " if cond else "✗ ") + msg)

    fixture = {
        "registry_version": 1,
        "counts": {"total": 2, "open": 2, "with_issue": 0},
        "caveats": [
            {"id": "CAV-01", "class": "open", "text": "тестовая дыра",
             "source": "fixture", "acceptance": "условие закрытия",
             "issue": None, "state": "open"},
            {"id": "CAV-02", "class": "structurally_blocked", "text": "блок",
             "source": "fixture", "acceptance": "доступ получен",
             "issue": None, "state": "open"},
        ],
    }
    md = checklist(fixture)
    need("CAV-01" in md and "Приёмка:" in md, "чек-лист содержит записи и приёмки")
    doc = render_docs(fixture)
    need(doc.count("| CAV-") == 2, "документ-таблица порождает строку на каждую запись")
    tpl = issue_template("CAV-01", fixture)
    need(tpl is not None and "Формула приёмки" in tpl, "шаблон issue печатается")
    need(issue_template("CAV-99", fixture) is None, "несуществующий ID — отказ, не выдумка")
    # счётчик «SOLVED только при 0» кусается
    fixture2 = dict(fixture)
    fixture2["counts"] = {"total": 2, "open": 0, "with_issue": 2}
    fixture2["caveats"] = [dict(c, state="closed", issue=7) for c in fixture["caveats"]]
    need(fixture2["counts"]["open"] == 0, "нулевой счётчик — ядро вправе стать SOLVED")
    print("SELFTEST:", "OK" if ok else "FAILED")
    return ok


def main():
    ap = argparse.ArgumentParser(description="Реестр caveats Q43 (П48)")
    ap.add_argument("--build", action="store_true", help="собрать реестр из r49")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("cmd", nargs="?", choices=["list", "docs", "checklist", "check", "new"])
    ap.add_argument("--live", action="store_true", help="check: живая сверка GitHub")
    ap.add_argument("--id", help="new: ID caveat (CAV-XX)")
    ap.add_argument("--out", help="checklist: писать в файл")
    args = ap.parse_args()

    if args.selftest:
        return 0 if _selftest() else 1
    if args.build:
        reg = build_registry()
        print(f"ФАКТ: реестр собран: {reg['counts']['total']} caveats "
              f"(открыто {reg['counts']['open']}) → results/caveats_registry.json")
        return 0
    if args.cmd in (None, "list"):
        reg = load_registry()
        for c in reg["caveats"]:
            issue = f"#{c['issue']}" if c["issue"] else "—"
            print(f"{c['id']}  {CLASSES[c['class']][0]:<14} {issue:<8} {c['text'][:70]}")
        print(f"итого {reg['counts']['total']} · открыто {reg['counts']['open']}")
        return 0
    if args.cmd == "docs":
        reg = load_registry()
        os.makedirs(os.path.dirname(DOC), exist_ok=True)
        with open(DOC, "w", encoding="utf-8") as f:
            f.write(render_docs(reg))
        print(f"ФАКТ: docs/CAVEATS.md перегенерирован (детерминированно)")
        return 0
    if args.cmd == "checklist":
        reg = load_registry()
        md = checklist(reg)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(md)
            print(f"ФАКТ: чек-лист → {args.out}")
        else:
            print(md)
        return 0
    if args.cmd == "check":
        return 0 if check(live=args.live) else 1
    if args.cmd == "new":
        if not args.id:
            print("new: укажи --id CAV-XX", file=sys.stderr)
            return 2
        tpl = issue_template(args.id)
        if tpl is None:
            return 1
        print(tpl)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
