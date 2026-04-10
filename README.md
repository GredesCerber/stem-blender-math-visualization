# STEM-проект: 3D-визуализация математических поверхностей в Blender

Учебный проект для наглядного изучения функций вида `z = f(x, y)` через Blender (Python `bpy` + Geometry Nodes).  
Репозиторий объединяет готовые скрипты, методические материалы и шаблоны для отчёта/презентации.

## Что уже реализовано

- единая библиотека функций и параметров (`scripts/function_library.py`);
- 3 основных скрипта с согласованным CLI и валидацией параметров;
- генерация 3D-поверхностей из формулы + рендер PNG;
- интерактивная поверхность через Geometry Nodes;
- модуль прикладной задачи: поиск пути A*/Dijkstra на поверхности;
- методические материалы, эксперименты, шаблоны отчёта и презентации.

## Структура репозитория

```text
stem-blender-math-visualization/
├── README.md
├── FunctionVisualizer.blend          ← финальная учебная сцена
├── assets/
│   └── README.md
├── docs/
│   ├── 01_theory.md
│   ├── 02_stem_concept.md
│   ├── 03_blender_guide.md
│   ├── 04_experiments.md
│   ├── 05_report_template.md
│   ├── 06_presentation_template.md
│   ├── 01_введение_и_актуальность.md
│   ├── 02_теория_функции_поверхности.md
│   ├── 03_план_методички.md
│   ├── 04_реализация_blender.md
│   ├── 05_эксперименты.md
│   ├── 06_заключение.md
│   ├── advanced-examples.md
│   ├── 07_pathfinding_on_surface.md
│   └── metodichka/
│       ├── полная_методичка.md
│       └── Методичка.docx            ← канонический DOCX
└── scripts/
    ├── function_library.py
    ├── visualize_function.py
    ├── generate_surface_mesh.py
    ├── setup_geometry_nodes_surface.py
    ├── batch_render.py
    ├── export_experiment_table.py
    └── pathfinding/
        ├── terrain_graph.py
        ├── cost_functions.py
        ├── search.py
        └── visualize_path_in_blender.py
```

## Быстрый старт

1. Установите Blender 3.6+ (желательно 4.x).
2. Откройте Blender → Workspace **Scripting**.
3. Запустите `scripts/visualize_function.py` через **Open** → **Run Script**.
4. При необходимости задайте параметры через CLI-аргументы (`--function`, `--resolution`, `--amplitude`, `--frequency` и т.д.).

Для интерактивного режима с ползунками запустите `scripts/setup_geometry_nodes_surface.py`.
Для фонового рендера PNG используйте:  
`blender --background --python scripts/visualize_function.py -- --function wave --resolution 100 --amplitude 2 --frequency 3 --output assets/renders/wave_A2_k3.png`.

## Быстрая учебная демонстрация

1. Откройте `FunctionVisualizer.blend` в Blender.
2. Выберите объект `MathSurface_GN` → вкладка Properties > Modifiers > GeoNodes_Surface.
3. Меняйте **Amplitude** и **Frequency** — форма поверхности меняется в реальном времени.
4. Доступны пресеты (в Custom Properties объекта): `lesson_default`, `gentle_wave`, `dynamic_wave`.
5. Для рендера: **Render → Render Image** (F12).

## Минимальные требования ПК

- ОС: Windows 10/11, Linux или macOS
- Blender: 3.6+ (рекомендуется 4.x)
- CPU: 4 потока и выше
- RAM: от 8 ГБ (рекомендуется 16 ГБ для `resolution > 100`)
- GPU: любая современная, для учебных рендеров достаточно встроенной

## Скрипты

| Скрипт | Назначение | Когда использовать |
|---|---|---|
| `scripts/visualize_function.py` | Быстрый и понятный генератор поверхности | Первый запуск и учебные демонстрации |
| `scripts/generate_surface_mesh.py` | Генерация сетки с выбором предустановленных функций | Эксперименты с параметрами `A`, `k`, `sigma`, `resolution` |
| `scripts/setup_geometry_nodes_surface.py` | Автоматическая настройка Geometry Nodes | Интерактивное управление формой поверхности |
| `scripts/pathfinding/visualize_path_in_blender.py` | Поиск и визуализация маршрута на 3D-поверхности | Прикладные STEM-задачи (A*/Dijkstra) |

## Документация

**Базовый набор материалов:**

- `docs/01_theory.md`
- `docs/02_stem_concept.md`
- `docs/03_blender_guide.md`
- `docs/04_experiments.md`
- `docs/05_report_template.md`
- `docs/06_presentation_template.md`

**Расширенная версия методички (по главам):**

- `docs/01_введение_и_актуальность.md`
- `docs/02_теория_функции_поверхности.md`
- `docs/03_план_методички.md`
- `docs/04_реализация_blender.md`
- `docs/05_эксперименты.md`
- `docs/06_заключение.md`
- `docs/07_pathfinding_on_surface.md`
- `docs/metodichka/полная_методичка.md`

## Рекомендуемый учебный маршрут

1. Теория и мотивация: `docs/01_theory.md` + `docs/02_stem_concept.md`.
2. Практика в Blender: `docs/03_blender_guide.md` и запуск скриптов из `scripts/`.
3. Эксперименты: `docs/04_experiments.md` (или `docs/05_эксперименты.md` для расширенной версии).
4. Прикладной модуль: `docs/07_pathfinding_on_surface.md`.
5. Оформление результата: `docs/05_report_template.md` + `docs/06_presentation_template.md`.

## Поиск пути на поверхности (A* / Dijkstra)

Пример без препятствий:

```bash
blender --background --python scripts/pathfinding/visualize_path_in_blender.py -- --function paraboloid --algorithm astar --start-x -4 --start-y -4 --goal-x 4 --goal-y 4 --output assets/renders/path_paraboloid_astar.png
```

Пример с препятствием:

```bash
blender --background --python scripts/pathfinding/visualize_path_in_blender.py -- --function wave --algorithm dijkstra --obstacle-circle 0,0,1.5 --start-x -4 --start-y -4 --goal-x 4 --goal-y 4 --output assets/renders/path_wave_obstacle_dijkstra.png
```

## Тесты (без Blender)

Если установлен Python:

```powershell
python -m unittest discover -s tests
```

## Лицензия

Материалы предназначены для образовательного использования. Допускается свободная адаптация с указанием источника.
