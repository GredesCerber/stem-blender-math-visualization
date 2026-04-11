# Лабиринт и поиск пути

> Модуль `scripts/pathfinding/labyrinth.py` закрывает TODO §12.5 из `docs/ai-agent/AI_AGENT_HANDOFF.md`: **генерация препятствий и поиск пути на едином 2D-представлении данных.**

---

## 1. Идея

Проект уже умеет искать путь на 3D-поверхности `z = f(x, y)` через `TerrainGraph` + A\*/Dijkstra. Лабиринт — это та же задача, но на **плоской** сетке: вместо высоты у каждой ячейки — признак «стена / проход».

Формат данных — ровно тот же 2D-массив, на котором строится `TerrainGraph`:

```
0 = свободная ячейка
1 = стена
```

За счёт этого один и тот же движок поиска работает и на рельефе, и на лабиринте: `maze_to_terrain_graph(...)` превращает массив в плоский `TerrainGraph` (z = 0) с `blocked=True` для стен, а дальше — обычный `a_star` / `dijkstra`.

---

## 2. API

```python
from pathfinding.labyrinth import (
    generate_maze,
    find_path_in_maze,
    maze_start_goal,
    maze_to_terrain_graph,
    maze_path_to_scene_points,
    print_maze,
    FREE, WALL,
)
```

### `generate_maze(rows, cols, seed=None) -> list[list[int]]`
Идеальный лабиринт по алгоритму **рекурсивного обхода (DFS)**. Чётные размеры автоматически увеличиваются до ближайших нечётных, чтобы корректно легли «комнаты».

- `seed` делает результат **воспроизводимым**: одинаковый seed и размеры → одинаковый лабиринт. Это требование критерия готовности из §12.5.
- Границы всегда стены.
- `(1, 1)` и `(cols-2, rows-2)` гарантированно свободны.

### `maze_start_goal(maze) -> (start, goal)`
Возвращает канонические `start = (1, 1)` и `goal = (cols-2, rows-2)`. Формат — `(col, row)`, как и в `TerrainGraph`.

### `find_path_in_maze(maze, start, goal, *, algorithm="astar", cell_size=1.0, connectivity=4, weights=None) -> SearchResult`
Тонкая обёртка: строит `TerrainGraph` и вызывает нужный алгоритм. По умолчанию используется 4-связность (лабиринт без диагоналей) и вес только по длине ребра. Возвращает штатный `SearchResult` из `pathfinding.search`.

### `maze_to_terrain_graph(maze, *, cell_size=1.0, connectivity=4)`
Если нужно напрямую работать с графом (например, прикрутить `risk`).

### `maze_path_to_scene_points(path, *, cell_size=1.0, z=0.0)`
Конвертация пути из ячеек в координаты сцены Blender.

### `print_maze(maze, *, path=None, start=None, goal=None)`
ASCII-рендер: `█` — стена, `·` — путь, `S`/`G` — маркеры, пробел — свободно.

---

## 3. Быстрый пример (без Blender)

```python
import sys; sys.path.insert(0, "scripts")
from pathfinding.labyrinth import (
    generate_maze, find_path_in_maze, maze_start_goal, print_maze,
)

maze = generate_maze(rows=15, cols=21, seed=42)
start, goal = maze_start_goal(maze)
result = find_path_in_maze(maze, start, goal, algorithm="astar")

print(f"Путь: {len(result.path)} ячеек, посещено {result.visited_nodes}")
print_maze(maze, path=result.path, start=start, goal=goal)
```

Ожидаемый вывод:

```
Путь: 87 ячеек, посещено 121
█████████████████████
█S█···█    ···█···█ █
█·█·█·█████·█·█·█·█ █
█···█·····█·█···█···█
...
█  ···█·····█    ··G█
█████████████████████
```

Повторный запуск с тем же `seed=42` даст **ровно тот же лабиринт и тот же путь** — критерий воспроизводимости выполнен.

---

## 4. Визуализация в Blender

Скрипт `scripts/pathfinding/visualize_labyrinth_in_blender.py` строит сцену:
- плоский пол,
- стены как кубики высотой `--wall-height`,
- маршрут как Curve с эмиссией,
- маркеры старта (зелёный) и финиша (жёлтый),
- камера и свет через `enhanced_camera_utils`.

Команды запуска (Windows / Linux):

```
blender --background --python scripts/pathfinding/visualize_labyrinth_in_blender.py -- --rows 21 --cols 21 --seed 42 --algorithm astar --output assets/renders/labyrinth_21_astar.png
```

```
blender --background --python scripts/pathfinding/visualize_labyrinth_in_blender.py -- --rows 25 --cols 25 --seed 7 --algorithm dijkstra --output assets/renders/labyrinth_25_dijkstra.png
```

Без Blender скрипт тоже запускается — он напечатает ASCII-лабиринт и сохранит путь в CSV (`--path-output`).

### Параметры
| Флаг | По умолчанию | Что делает |
|---|---|---|
| `--rows`, `--cols` | 21 | Размер лабиринта (чётные → округляются вверх до нечётных) |
| `--seed` | 42 | Seed генерации |
| `--algorithm` | `astar` | `astar` или `dijkstra` |
| `--cell-size` | 1.0 | Физический размер ячейки в сцене |
| `--wall-height` | 1.0 | Высота стен |
| `--output` | — | PNG-рендер (только в Blender) |
| `--path-output` | — | CSV с точками маршрута |

---

## 5. Сравнение A\* и Dijkstra на лабиринте

В **идеальном** лабиринте между любыми двумя ячейками существует **ровно один** путь — поэтому длина пути у A\* и Dijkstra совпадает (этот факт зафиксирован тестом `test_astar_and_dijkstra_same_length_on_perfect_maze`).

Разница проявляется в числе **посещённых узлов**: у A\* эвристика направляет поиск в сторону цели, поэтому обычно `visited_nodes` меньше. Это хороший учебный сюжет для проекта C из `docs/student_exercises.md`.

---

## 6. Тесты

```
python -m unittest tests.test_labyrinth -v
```

14 тестов: репродуцируемость seed, корректность границ, соответствие формата, работа обоих алгоритмов, отсутствие прохода через стены, совпадение длин путей A\* и Dijkstra.

---

## 7. Что дальше (опционально)

- Добавить «дорогие» ячейки (не стены, а высокая стоимость) и показать, как `w_risk` влияет на маршрут.
- Генерация лабиринта с петлями (убрать часть стен после DFS) — и показать, что A\* начнёт выигрывать по длине.
- Анимация пошагового поиска (сохранять `visited_nodes` на каждом шаге и запекать keyframes).
