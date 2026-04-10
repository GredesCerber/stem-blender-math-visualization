# Copilot instructions for this repository

## Обязательное чтение перед изменениями

Перед любой работой сначала просмотрите:

1. `README.md`
2. `GETTING_STARTED.md`
3. `scripts/README.md`
4. `docs/ai-agent/AI_AGENT_HANDOFF.md`
5. `docs/ai-agent/AI_AGENT_ACCEPTANCE_CHECKLIST.md`
6. `docs/ai-agent/AI_AGENT_EXECUTION_PLAN.md`

Эти файлы задают актуальный scope, ограничения и приоритеты.

## Команды build / test / lint

Запускать из корня репозитория.

```powershell
# Полный прогон тестов
python -m unittest discover -s tests

# Один тестовый файл
python -m unittest tests\test_function_library.py
python -m unittest tests\test_pathfinding.py

# Один тест по имени (пример)
python -m unittest discover -s tests -p "test_pathfinding.py" -k avoids_circle_obstacle
```

```powershell
# Генерация готовых .blend-файлов
blender --background --python scripts\create_individual_blend_files.py
blender --background --python scripts\create_visualizer_blend.py

# Batch-render пресетов (сначала dry-run)
python scripts\batch_render.py --dry-run --output-dir assets\renders
python scripts\batch_render.py --blender-exe "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --output-dir assets\renders
```

Отдельной lint-конфигурации в репозитории нет (`ruff`/`flake8`/`mypy`/`black` files отсутствуют).

## High-level архитектура

### 1) Единое ядро математики и CLI
- `scripts\function_library.py` — источник истины для:
  - формул (`FUNCTION_REGISTRY`),
  - параметров (`SurfaceConfig`),
  - валидации (`validate_surface_config`),
  - генерации поверхности/сетки (`generate_surface_geometry`, `generate_surface_grid`),
  - общего CLI (`build_common_parser`, `parse_common_cli_args`).

### 2) Генерация и визуализация поверхностей
- `scripts\visualize_function.py` — быстрый генератор поверхности + материал + рендер.
- `scripts\generate_surface_mesh.py` — mesh-вариант через `bmesh`.
- `scripts\setup_geometry_nodes_surface.py` — интерактивный GN-режим (только `--function wave`).
- `scripts\enhanced_camera_utils.py` — единые пресеты камер/света.

### 3) Прикладной модуль поиска пути
- `scripts\pathfinding\terrain_graph.py` — дискретизация поверхности в граф.
- `scripts\pathfinding\cost_functions.py` — стоимость ребра (длина/уклон/risk).
- `scripts\pathfinding\search.py` — алгоритмы Dijkstra и A*.
- `scripts\pathfinding\visualize_path_in_blender.py` — расчет маршрута + визуализация в Blender.

### 4) Пайплайн артефактов и экспериментов
- `scripts\batch_render.py` — пакетные Blender-запуски и manifest (JSON/CSV).
- `scripts\export_experiment_table.py` — экспорт таблиц экспериментов (CSV/Markdown).
- `assets\renders\` и `FunctionVisualizer_*.blend` — учебные артефакты, синхронизированные с docs.

### 5) Покрытие тестами
- Тесты только на Python `unittest` (`tests\test_function_library.py`, `tests\test_pathfinding.py`).
- Blender-интеграционные тесты (`bpy`) автоматизированно не запускаются.

## Ключевые conventions проекта

- Не дублируйте формулы/дефолты/CLI: переиспользуйте `function_library.py`.
- Для Blender CLI-скриптов сохраняйте паттерн `--` + `extract_user_argv()`.
- Сохраняйте стандарт entrypoint:
  - `main()` под `if __name__ == "__main__":`
  - `ValueError` -> `[ERROR] ...` -> `SystemExit(2)`.
- При добавлении новых запускаемых скриптов сохраняйте `SCRIPT_DIR`/`sys.path` bootstrap.
- Не меняйте без запроса имена `FunctionVisualizer_*.blend`.
- Не удаляйте `scripts\enhanced_camera_utils.py` (на нем завязаны камеры в ключевых скриптах).
- Не добавляйте новые математические функции без явного запроса (сначала закрывается текущий scope).
- Держите команды и названия артефактов синхронизированными между `README.md`, `GETTING_STARTED.md` и `scripts/README.md`.
- Проект Windows-first: в инструкциях используйте Windows-пути и команды.
- В русскоязычных файлах сохраняйте русские пользовательские сообщения/формулировки.
