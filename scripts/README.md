# Скрипты проекта

В папке `scripts/` находятся основные Blender-скрипты и дополнительные утилиты.

## Основные скрипты (ядро проекта)

| Файл | Назначение |
|---|---|
| `visualize_function.py` | Быстрая генерация поверхности `z=f(x,y)` + colormap + `--output` для PNG |
| `generate_surface_mesh.py` | Генерация mesh-поверхности с материалом и единым CLI |
| `setup_geometry_nodes_surface.py` | Автоматическая сборка Geometry Nodes (интерактивная волна `A`, `k`) |

## Дополнительные скрипты

| Файл | Назначение |
|---|---|
| `function_library.py` | Единый реестр функций, валидация и общие CLI-аргументы |
| `batch_render.py` | Пакетный запуск рендеров через Blender CLI |
| `export_experiment_table.py` | Экспорт таблиц экспериментов в CSV/Markdown |
| `pathfinding\visualize_path_in_blender.py` | Поиск пути (A*/Dijkstra) и визуализация маршрута на поверхности |
| `pathfinding\*.py` | Модули графа/стоимости/поиска для прикладной задачи маршрутизации |

## Единый интерфейс CLI (для 3 основных скриптов)

Поддерживаемые аргументы:

- `--function`
- `--resolution`
- `--x-min`, `--x-max`, `--y-min`, `--y-max`
- `--amplitude`, `--frequency`, `--sigma`
- `--output` (для сохранения PNG, когда доступен Blender)

Пример:

```powershell
"C:\Program Files\Blender Foundation\Blender 4.x\blender.exe" --background --python scripts\visualize_function.py -- --function wave --resolution 100 --amplitude 2 --frequency 3 --output assets\renders\wave_A2_k3.png
```

## Запуск в Blender (GUI)

1. Откройте Blender.
2. Перейдите в Workspace **Scripting**.
3. Нажмите **Open** и выберите скрипт из `scripts/`.
4. Нажмите **Run Script** (`Alt+P`).

## Запуск без Blender

Все три основных скрипта завершаются предсказуемо:

- печатают preview значений `f(x,y)`;
- валидируют параметры CLI;
- не падают с неясными ошибками при отсутствии `bpy`.
