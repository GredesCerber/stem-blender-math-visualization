# STEM-проект: 3D-визуализация математических поверхностей в Blender

Учебный проект для наглядного изучения функций вида `z = f(x, y)` через интерактивную 3D-визуализацию в Blender и поиск оптимального пути по полученной поверхности алгоритмами A* / Dijkstra.

---

## Главный документ

**Ознакомительная методичка «Математика в 3D: от формулы к маршруту»** — три акта, три картинки, три команды:

- [`docs/metodichka/Методичка.docx`](docs/metodichka/Методичка.docx) — готовый DOCX для печати и сдачи.
- [`docs/metodichka/методичка.md`](docs/metodichka/методичка.md) — исходный markdown.

Сборка DOCX из markdown-исходника:

```bash
python3 scripts/build_metodichka_docx.py
```

Подробная версия методички (с полным разбором каждого файла) перенесена в [`docs/metodichka/old/`](docs/metodichka/old/) как исторический артефакт. Новая методичка короткая и ознакомительная — её вектор описан в [`docs/metodichka/PLAN.md`](docs/metodichka/PLAN.md).

Дополнительно:

- [`docs/student_exercises.md`](docs/student_exercises.md) — рабочий лист студента.
- [`docs/08_lesson_scenario.md`](docs/08_lesson_scenario.md) — сценарий урока для преподавателя.
- [`docs/09_student_faq.md`](docs/09_student_faq.md) — FAQ для студента.
- [`docs/PROJECT_VISION.md`](docs/PROJECT_VISION.md) — архитектурный обзор проекта.

---

## Быстрый старт

```
1. Откройте: FunctionVisualizer_Wave.blend
2. Крутите волну средней кнопкой мыши
3. Меняйте Amplitude / Frequency ползунками справа
4. F12 — рендер в PNG
```

Остальные готовые сцены: `FunctionVisualizer_Paraboloid.blend`, `Saddle.blend`, `Ripple.blend`, `Gaussian.blend`.

---

## Ключевые функции

| Функция | Формула | Форма |
|---|---|---|
| **Wave** | `z = A·sin(k·x)·cos(k·y)` | Морская рябь |
| **Paraboloid** | `z = A·(x²+y²)` | Чаша |
| **Saddle** | `z = A·(x²−y²)` | Седло |
| **Ripple** | `z = A·sin(k·r)` | Круги на воде |
| **Gaussian** | `z = A·exp(−(x²+y²)/σ²)` | Гауссова гора |

Полные листинги и разбор — в методичке, глава 3.

---

## Запуск скриптов

Фоновый рендер поверхности:

```bash
blender --background --python scripts/visualize_function.py -- \
    --function wave --resolution 100 --amplitude 2 --frequency 3 \
    --output assets/renders/wave_A2_k3.png
```

Поиск пути (A* / Dijkstra) на поверхности:

```bash
blender --background --python scripts/pathfinding/visualize_path_in_blender.py -- \
    --function paraboloid --algorithm astar \
    --start-x -4 --start-y -4 --goal-x 4 --goal-y 4 \
    --output assets/renders/path_paraboloid_astar.png
```

Поиск пути в 2D-лабиринте (тот же движок, плоская сетка):

```bash
python -c "import sys; sys.path.insert(0,'scripts'); from pathfinding.labyrinth import generate_maze, find_path_in_maze, maze_start_goal, print_maze; m=generate_maze(21,21,seed=42); s,g=maze_start_goal(m); r=find_path_in_maze(m,s,g); print_maze(m, path=r.path, start=s, goal=g)"
```

---

## Тесты

```bash
python -m unittest discover -s tests
```

---

## Лицензия

Материалы предназначены для образовательного использования. Допускается свободная адаптация с указанием источника.
