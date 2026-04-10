# Release Notes

## STEM Blender Math Visualization — hardening iteration

### Код и архитектура

- Добавлен единый модуль `scripts/function_library.py`:
  - реестр функций (`paraboloid`, `saddle`, `wave`, `ripple`, `gaussian`, `custom`);
  - единая валидация параметров;
  - единый CLI-парсер.
- Обновлены 3 основных скрипта:
  - `scripts/visualize_function.py`
  - `scripts/generate_surface_mesh.py`
  - `scripts/setup_geometry_nodes_surface.py`
- Скрипты приведены к согласованному интерфейсу (`--function`, `--resolution`, `--x-min`, `--x-max`, `--y-min`, `--y-max`, `--amplitude`, `--frequency`, `--sigma`, `--output` где применимо).

### Прикладное расширение pathfinding

- Добавлен пакет `scripts/pathfinding/`:
  - `terrain_graph.py` — граф поверхности;
  - `cost_functions.py` — стоимость с длиной/уклоном/риском;
  - `search.py` — A* и Dijkstra;
  - `visualize_path_in_blender.py` — построение маршрута и Curve в Blender.
- Добавлена документация запуска: `docs/07_pathfinding_on_surface.md`.

### Эксперименты и ассеты

- Заполнены реальные таблицы в:
  - `docs/04_experiments.md`
  - `docs/05_эксперименты.md`
- Создан каталог `assets/renders/` с набором PNG-рендеров для отчёта/презентации.
- Добавлены `render_manifest.csv` и `render_manifest.json`.

### Документация

- Синхронизированы `README.md`, `scripts/README.md`, `assets/README.md`.
- Исправлены несоответствия по количеству основных скриптов.
- В `docs/06_заключение.md` добавлены:
  - сценарий урока на 45 минут;
  - FAQ преподавателя;
  - типичные ошибки студента и быстрые фиксы.
- Обновлена `docs/metodichka/полная_методичка.md` (разделы про код и эксперименты).

### Тесты

- Добавлены базовые unit-тесты:
  - `tests/test_function_library.py`
  - `tests/test_pathfinding.py`

### Ограничения текущей итерации

- Финальный `FunctionVisualizer.blend` требует ручной сборки/проверки в Blender-среде.
- DOCX-артефакты (`docs/metodichka/*.docx`) требуют ручной проверки в Word (открытие/форматирование).
