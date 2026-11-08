# R47-b — ряды цен квот НЗ/Исландия (FR6 повторяющееся плечо) — НАЧАЛО

Поток R47-b. Задача: закрыть количественные ряды цен квот: (1) NZ QMS — NZ$/т TAC по запасам, ≥3 точки, ≥2 запаса, orange roughy 1990-х; (2) Исландия — цена тресковой квоты ISK/кг код-экв.; (3) волатильность P (цена квоты) vs TAC/улов.

## Протокол и дисциплина
- Credential-файл upload/346543564356.txt НЕ открывался; токены не использовались.
- Поисковые серии: РОВНО 3 (см. ниже) — исполнены.
- WebFetch: 4 из 4 (в т.ч. 2 промаха по номерам RFF-DP, 403 FAO, HTTP 000 Motu) — бюджет исчерпан.
- Статус файла: создан РАНО (до финализации) согласно инструкции «Файл пиши РАНО».

## Журнал серий
- S1 (Исландия, GNews RSS): «kvótaverð» (is) — 0; «"cod quota" price Iceland ISK» — 3 заголовка; «þorskkvóti verð aflamark» (is) — 0.
- S2 (НЗ, archive.org advancedsearch ×2 + GNews RSS ×1): «"fair value" quota New Zealand fisheries» — 0; «Arnason ITQ Iceland quota» — 0; «"value of quota" New Zealand» — 5 заголовков.
- S3 (добор): GNews «"orange roughy" quota price» — 10 заголовков; archive.org «"fishing quota markets"» — 0; archive.org «aflamark» — 24k мусора (0 релевантных); GNews «New Zealand ITQ quota worth billion» — 2 заголовка.

## Журнал WebFetch
1. https://media.rff.org/documents/RFF-DP-04-03.pdf → 200, НО не тот paper (Margolis & Nævdal, Safe Minimum Standards).
2. https://media.rff.org/documents/RFF-DP-02-13.pdf → 200, НО не тот paper (Beierle, WTO agriculture).
3. https://www.fao.org/3/a1495e/a1495e00.pdf (FAO FTP 504, глава Arnason «Iceland's ITQ system evolves») → 403 (bot-block).
4. https://motu-www.vuw.ac.nz/pdf/wp07_02_lockleslie.pdf (Lock & Leslie 2007) → HTTP 000 (хост недоступен).

## Таблица результатов (ряд: год — запас — цена — источник — уверенность)

| # | Серия (год) | Запас | Цена квоты | Источник | Уверенность |
|---|---|---|---|---|---|
| 1 | 1990–2000 | НЗ, любое (цель: ≥2 запасов, incl. ORH) | **UNKNOWN** — ценовые таблицы Newell/Sanchirico/Kerr недоступны (номер RFF-DP не угадан: 04-03 и 02-13 = другие paper; archive.org advancedsearch 0) | fetch-журнал 1–2 | **UNKNOWN** |
| 2 | 1990-е | НЗ, orange roughy | **UNKNOWN** — вопрос «цена обваливалась при TACC-срезе?» не закрыт. Фон (LOW, без URL): канонический ответ — в Newell et al. 2005 (JARE 30(3)); в песочнице не добыт | модельный фон | **UNKNOWN** (фон LOW) |
| 3 | 2000-е–2020-е | НЗ, агрегат | **UNKNOWN** — «estimated value of quota» (MPI/FishServe) URL не найден ни в одной из 3 серий; archive.org 0; GNews 0 чисел | S2, S3 | **UNKNOWN** |
| 4 | 1990–2007 | Исландия, треска (ISK/кг код-экв.) | **UNKNOWN** — Arnason (глава FAO FTP 504) 403; Arnason 2005 MRE URL не известен; fiskistofa.is HTTP 000 (с r44b); GNews «kvótaverð» = 0 | fetch-журнал 3; r44b | **UNKNOWN** |
| 5 | 1990-е–2024 | НЗ, hoki (F-слой) | TACC-срез по плану восстановления 2006; стоки более чем удвоились после 2001; сертификация MSC сохранена | кэш r44d_tmp/msc_hoki.html.txt (r44d) | MED (F-слой) / P: UNKNOWN |
| 6 | 09.2024 | НЗ, orange roughy Challenger (ORH7B) (F-слой) | Министр Джонс «goes for maximum cut to Challenger orange roughy stock» — повторяющийся шок (TACC-срез) действует и в 2024; решение через обычный министериальный процесс (институт цел) | GNews RSS: BusinessDesk 26.09.2024; Newsroom 27.09.2024 «Minister goes down to the line on contested fish quotas»; BusinessDesk 23.09.2024 | MED (заголовок) |
| 7 | 02.2025 | НЗ↔Австралия, orange roughy | НЗ оспаривает австралийскую квоту ORH на SPRFMO — квота = торгуемый актив даже на межправительственном уровне («controversial bid») | GNews RSS: NZ Herald 19.02.2025 | MED (заголовок) |
| 8 | 1986–2025 | НЗ, Māori fisheries | Квота — капитализированный актив поселения (The Spinoff 09.04.2025: «Crown has been siphoning off Māori fisheries quota for decades») — P-слой воспроизводится десятилетиями | GNews RSS: The Spinoff 09.04.2025 | MED (заголовок) |
| 9 | 1984/1990 | Исландия, треска (механизм) | Рынок квот cod с 1984, отчуждаемость с 1990; лизинг = «fixed percentage of landed value» (исландский % UNKNOWN; класс-верх Bering Sea crab 80%) | кэш r44b_itq_wiki.txt (HIGH) | HIGH (механизм) / цены UNKNOWN |
| 10 | 06.2023 / 11.2025 | Исландия | Iceland Review «Give a Man a Fish» (07.06.2023); fiskerforum «Cod proposal from Iceland's small boat owners» (08.11.2025) — заголовки без чисел; icelandreview.com 403 (r46b) | GNews RSS S1 | MED (существование тем) / числа UNKNOWN |

## Волатильность P vs TAC/улов (задача 3)
- **UNKNOWN** по обоим случаям: нет ни одного количественного ряда цен квоты в добытом материале; TACC-амплитуды частичны (hoki 2006-срез — направление, числа в кэше отсутствуют; ORH7B 2024 — «maximum cut», тоннаж в заголовке не виден).
- Механистический каркас (LOW, совместим с r46e M1): для повторяющегося шока предсказание FR6 — dV≈0 при больших колебаниях спот-потока (реализация -95% спот ⇒ dV=0, наблюдаемый ресайклинг -14% — калибровка AU_water). NZ/Исландия должны лечь в этот же тип, но эмпирически НЕ замкнуто.

## Вердикт (FR6 повторяющееся плечо)
1. **Количественно НЕ ЗАКРЫТО** (третья попытка подряд: r46b, r46d, r47b). Ни одной точки ряда NZ$/т TAC по запасам и ни одной точки ISK/кг код-экв. добыть не удалось — рыночные ряды рыбных квот структурно недоступны в песочнице: (а) академические PDF — 403/мертвые хосты; (б) GNews RSS не выносит цифр квотных цен в заголовки; (в) archive.org advancedsearch — 0 аплоадов по 4 запросам.
2. **Институционально совместимо с FR6-повторяющимся**: квота как актив (P) пережила 30+ лет регулярных TACC-срезов — 2024-й «maximum cut» по Challenger ORH решён в обычном порядке, сертификаты MSC, Māori-актив, межправительственная борьба за ORH-квоту (заголовки 2024–2025, MED). Обвалов/отмены института в выдаче не видно; но отсутствие ценового ряда = тест амплитуд не проведён.
3. Вопрос брифа «orange roughy 1990-х — цена обваливалась?» — остаётся **UNKNOWN**; ожидание из модельного фона (LOW): да, цена должна была падать вслед за срезами (Newell et al. 2005 — ключ к следующему потоку).

## Протокол (аудит)
- Серия 1 (Исландия): GNews RSS «kvótaverð» (is) 0; «"cod quota" price Iceland ISK» 3; «þorskkvóti verð aflamark» (is) 0.
- Серия 2 (НЗ): archive.org «"fair value" quota New Zealand fisheries» 0; «Arnason ITQ Iceland quota» 0; GNews «"value of quota" New Zealand» 5 заголовков.
- Серия 3: GNews «"orange roughy" quota price» 10; archive.org «"fishing quota markets"» 0; archive.org «aflamark» 24 346 мусора/0 релев.; GNews «New Zealand ITQ quota worth billion» 2.
- WebFetch: 1) media.rff.org/documents/RFF-DP-04-03.pdf → 200, не тот paper (Margolis & Nævdal SMS); 2) RFF-DP-02-13.pdf → 200, не тот (Beierle WTO); 3) fao.org/3/a1495e/a1495e00.pdf (FTP 504 Arnason) → **403**; 4) motu-www.vuw.ac.nz/pdf/wp07_02_lockleslie.pdf (Lock & Leslie) → **HTTP 000**.
- Локальные чтения (лимит не тратят): r44b/r46b/r46d/r44d/r45/r47a findings, r44e/r46e_results.json, r44b_itq_wiki.txt, r44d_tmp/*, r46b_f1/f2 — квотных цен НЗ/Исландии нигде нет.
- Файл upload/346543564356.txt не открывался; токены не использовались.
- Шкала: HIGH = полный текст; MED = заголовок+дата из RSS/кэш; LOW = фон модели; UNKNOWN = не добыто.

## UNKNOWN-лист и playbook для следующего потока
- Newell, Sanchirico & Kerr «Fishing Quota Markets» (JARE 2005 / RFF DP): перебрать номера RFF DP (02-42? 02-32? 03-18?) — по 1 на fetch, или rff.org site-search; PDF-паттерн media.rff.org/documents/RFF-DP-XX-XX.pdf подтверждён (200).
- Motu WP 07-02 (Lock & Leslie): новый домен motu.nz / motu.co.nz/assets/... (старый motu-www.vuw.ac.nz мёртв, HTTP 000).
- Arnason (FAO FTP 504, «Iceland's ITQ system evolves»): openknowledge.fao.org / зеркало / archive.ph (fao.org 403 ботам).
- Fiskistofa (kaup- og leigusamningar) через archive.ph/newest; исландские запросы: «kvótaverðmæti», «aðflutningsverðmæti», «verð kvóta» (чистое «kvótaverð» = 0).
- FishServe fair value (fishserve.co.nz) и MPI «estimated value of quota» interactive — URL требует site-search (в этот прогон бюджет не хватило).
- Предложить правилотворцам: OpenAlex (api.openalex.org) / Semantic Scholar Graph API как разрешённые «поисковые серии» — они дают точные PDF-URL академических таблиц цен, которые RSS/advancedsearch не находят.
