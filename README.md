# STEM-проект: 3D-визуализация математических поверхностей в Blender

Учебный проект для наглядного изучения функций вида `z = f(x, y)` через Blender (Python `bpy` + Geometry Nodes).  
Репозиторий объединяет готовые скрипты, методические материалы и шаблоны для отчёта/презентации.

## Что уже реализовано

- генерация 3D-поверхностей из формулы (`scripts/generate_surface_mesh.py`, `scripts/visualize_function.py`);
- интерактивная поверхность через Geometry Nodes (`scripts/setup_geometry_nodes_surface.py`);
- методические материалы для занятия, экспериментов и защиты проекта;
- шаблоны отчёта и презентации.

## Структура репозитория

```text
stem-blender-math-visualization/
├── README.md
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
│   └── metodichka/
│       └── полная_методичка.md
└── scripts/
    ├── README.md
    ├── visualize_function.py
    ├── generate_surface_mesh.py
    └── setup_geometry_nodes_surface.py
```

## Быстрый старт

1. Установите Blender 3.6+ (желательно 4.x).
2. Откройте Blender → Workspace **Scripting**.
3. Запустите `scripts/visualize_function.py` через **Open** → **Run Script**.
4. Измените функцию в `surface_function(x, y)` и перезапустите скрипт.

Для интерактивного режима с ползунками запустите `scripts/setup_geometry_nodes_surface.py`.
Для фонового рендера PNG используйте:  
`blender --background --python scripts/visualize_function.py -- --output renders/surface.png`.

## Скрипты

| Скрипт | Назначение | Когда использовать |
|---|---|---|
| `scripts/visualize_function.py` | Быстрый и понятный генератор поверхности | Первый запуск и учебные демонстрации |
| `scripts/generate_surface_mesh.py` | Генерация сетки с выбором предустановленных функций | Эксперименты с параметрами `A`, `k`, `sigma`, `resolution` |
| `scripts/setup_geometry_nodes_surface.py` | Автоматическая настройка Geometry Nodes | Интерактивное управление формой поверхности |

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
- `docs/metodichka/полная_методичка.md`

## Рекомендуемый учебный маршрут

1. Теория и мотивация: `docs/01_theory.md` + `docs/02_stem_concept.md`.
2. Практика в Blender: `docs/03_blender_guide.md` и запуск скриптов из `scripts/`.
3. Эксперименты: `docs/04_experiments.md` (или `docs/05_эксперименты.md` для расширенной версии).
4. Оформление результата: `docs/05_report_template.md` + `docs/06_presentation_template.md`.

## Лицензия

Материалы предназначены для образовательного использования. Допускается свободная адаптация с указанием источника.
