# KNOWN_ISSUES · rent-mechanism-q43 · Волна ×5 (2026-11-09)

## Красные CI (было → после патча)

| Run | Что было | Диагноз | После |
|---|---|---|---|
| 42312142153 (11-06 23:28) | guardian-tripwire failure, **0 jobs**, имя рана = путь к файлу | общий корень кластера ×5: пин-склейка `# vXwith:` → «Invalid workflow file» (PyYAML-репро по файлу SHA 17d3d35, строки 39–41) | волна ×4 переписала tripwire.yml; зелёный **42517829526** @ 9d6c2e76 (20:00); ×5-D диспатч: run ****42527374731** (workflow_dispatch → success, 21:52, sha 9d6c2e76)** |
| 42517267511 (11-08 19:53) | run «.github/workflows/caveats-registry.yml» failure, **0 jobs** | ДРУГОЙ корень: двоеточие в имени шага — `mapping values are not allowed here` (строка 30 caveats-registry.yml того SHA d9eb532) | фикс 9d6c2e7 «кавычки в имени шага»; зелёный **42517829605** @ 9d6c2e76 (20:00) |

## Квирки
- Соседний run 42517268634 (guardian-tripwire @ того же SHA d9eb532) — success: tripwire.yml того SHA был уже корректен, ломалось только caveats-registry.yml. Не смешивать два косяка.
