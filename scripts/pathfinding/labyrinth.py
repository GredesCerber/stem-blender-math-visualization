"""
labyrinth.py
============
Генерация 2D-лабиринтов и поиск пути по ним.

Лабиринт хранится в 2D-массиве той же формы, что и сетка TerrainGraph:
    0 = свободная ячейка
    1 = стена

За счёт этого поиск пути (A*/Dijkstra) работает через ту же инфраструктуру
TerrainGraph без повторной дискретизации — критерий §12.5 AI_AGENT_HANDOFF.

Примеры использования:

    from pathfinding.labyrinth import (
        generate_maze,
        find_path_in_maze,
        maze_start_goal,
        print_maze,
    )

    maze = generate_maze(rows=21, cols=21, seed=42)
    start, goal = maze_start_goal(maze)
    result = find_path_in_maze(maze, start, goal, algorithm="astar")
    print_maze(maze, path=result.path)
"""

from __future__ import annotations

import random
from collections.abc import Iterable

from .cost_functions import CostWeights
from .search import SearchResult, a_star, dijkstra
from .terrain_graph import GridNode, TerrainGraph, TerrainNodeData

MazeGrid = list[list[int]]

FREE = 0
WALL = 1


def _ensure_odd(value: int, *, name: str) -> int:
    if value < 3:
        raise ValueError(f"{name} должен быть >= 3.")
    return value if value % 2 == 1 else value + 1


def generate_maze(rows: int, cols: int, seed: int | None = None) -> MazeGrid:
    """Генерирует лабиринт методом рекурсивного обхода (DFS).

    Алгоритм:
      1. Сетка заполняется стенами.
      2. «Комнаты» располагаются в ячейках с нечётными координатами.
      3. DFS обходит комнаты в случайном порядке, пробивая стену между
         текущей и следующей непосещённой комнатой.
      4. Результат — идеальный лабиринт (ровно один путь между двумя комнатами).

    Args:
        rows: Число строк. Если чётное — будет увеличено до ближайшего нечётного.
        cols: Число столбцов. Если чётное — будет увеличено до ближайшего нечётного.
        seed: Seed для воспроизводимости. Одинаковый seed + размеры → одинаковый лабиринт.

    Returns:
        2D-массив размера rows×cols: 0 = свободно, 1 = стена.
    """
    rows = _ensure_odd(rows, name="rows")
    cols = _ensure_odd(cols, name="cols")

    rng = random.Random(seed)
    maze: MazeGrid = [[WALL] * cols for _ in range(rows)]

    # Итеративный DFS, чтобы не упереться в лимит рекурсии на больших лабиринтах.
    stack: list[tuple[int, int]] = [(1, 1)]
    maze[1][1] = FREE
    directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]

    while stack:
        row, col = stack[-1]
        rng.shuffle(directions)
        carved = False
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 < nr < rows - 1 and 0 < nc < cols - 1 and maze[nr][nc] == WALL:
                maze[row + dr // 2][col + dc // 2] = FREE
                maze[nr][nc] = FREE
                stack.append((nr, nc))
                carved = True
                break
        if not carved:
            stack.pop()

    # Гарантируем проходимость канонических точек старта/финиша.
    maze[1][1] = FREE
    maze[rows - 2][cols - 2] = FREE
    return maze


def maze_start_goal(maze: MazeGrid) -> tuple[GridNode, GridNode]:
    """Стандартные точки: левый-верх (1,1) и правый-низ (cols-2, rows-2)."""
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0
    if rows < 3 or cols < 3:
        raise ValueError("Лабиринт слишком маленький для старта/финиша.")
    return (1, 1), (cols - 2, rows - 2)


def maze_to_terrain_graph(
    maze: MazeGrid,
    *,
    cell_size: float = 1.0,
    connectivity: int = 4,
) -> TerrainGraph:
    """Превращает 2D-лабиринт в плоский TerrainGraph (z = 0).

    Стены помечаются blocked=True и отбрасываются алгоритмами поиска,
    поэтому A*/Dijkstra работают без изменений.

    Args:
        maze: 2D-массив лабиринта.
        cell_size: Физический размер ячейки (в единицах сцены Blender).
        connectivity: 4 — только по сторонам (рекомендуется для лабиринтов),
            8 — включая диагонали.

    Returns:
        TerrainGraph с координатами (x = col·cell_size, y = row·cell_size, z = 0).
    """
    if connectivity not in (4, 8):
        raise ValueError("connectivity должен быть 4 или 8.")

    rows = len(maze)
    if rows == 0:
        raise ValueError("Лабиринт не должен быть пустым.")
    cols = len(maze[0])
    if cols == 0 or any(len(row) != cols for row in maze):
        raise ValueError("Все строки лабиринта должны быть одинаковой длины.")

    x_values = [j * cell_size for j in range(cols)]
    y_values = [i * cell_size for i in range(rows)]

    nodes: dict[GridNode, TerrainNodeData] = {}
    for i in range(rows):
        for j in range(cols):
            cell = maze[i][j]
            if cell not in (FREE, WALL):
                raise ValueError(
                    f"Ячейка ({i},{j}) содержит {cell!r}, ожидалось 0 или 1."
                )
            nodes[(j, i)] = TerrainNodeData(
                x=j * cell_size,
                y=i * cell_size,
                z=0.0,
                risk=0.0,
                blocked=(cell == WALL),
            )

    return TerrainGraph(
        x_values=x_values,
        y_values=y_values,
        nodes=nodes,
        connectivity=connectivity,
    )


def find_path_in_maze(
    maze: MazeGrid,
    start: GridNode,
    goal: GridNode,
    *,
    algorithm: str = "astar",
    cell_size: float = 1.0,
    connectivity: int = 4,
    weights: CostWeights | None = None,
) -> SearchResult:
    """Находит путь в лабиринте тем же движком, что и на 3D-поверхности.

    Args:
        maze: 2D-лабиринт.
        start: (col, row) — начальная ячейка (должна быть свободной).
        goal: (col, row) — конечная ячейка (должна быть свободной).
        algorithm: "astar" или "dijkstra".
        cell_size: Размер ячейки.
        connectivity: 4 или 8.
        weights: Веса стоимости. По умолчанию — только длина ребра
            (уклон не нужен на плоском лабиринте).

    Returns:
        SearchResult с найденным путём (или пустым path, если пути нет).
    """
    if weights is None:
        weights = CostWeights(w_len=1.0, w_slope=0.0, w_risk=0.0, alpha=0.0)

    graph = maze_to_terrain_graph(
        maze,
        cell_size=cell_size,
        connectivity=connectivity,
    )

    algo = algorithm.strip().lower()
    if algo in {"astar", "a*", "a-star"}:
        return a_star(graph, start, goal, weights=weights)
    if algo in {"dijkstra", "djikstra"}:
        return dijkstra(graph, start, goal, weights=weights)
    raise ValueError("algorithm должен быть 'astar' или 'dijkstra'.")


def print_maze(
    maze: MazeGrid,
    *,
    path: Iterable[GridNode] | None = None,
    start: GridNode | None = None,
    goal: GridNode | None = None,
) -> str:
    """Рендерит лабиринт в строку ASCII-графикой (и печатает в stdout).

    Символы:
        █  — стена
        ·  — ячейка пути
        S  — старт
        G  — финиш
        (пробел) — свободная ячейка
    """
    path_set = set(path) if path else set()
    rows = len(maze)
    cols = len(maze[0]) if rows > 0 else 0

    lines: list[str] = []
    for i in range(rows):
        chars: list[str] = []
        for j in range(cols):
            node = (j, i)
            if start is not None and node == start:
                chars.append("S")
            elif goal is not None and node == goal:
                chars.append("G")
            elif node in path_set:
                chars.append("·")
            elif maze[i][j] == WALL:
                chars.append("█")
            else:
                chars.append(" ")
        lines.append("".join(chars))

    rendered = "\n".join(lines)
    print(rendered)
    return rendered


def maze_path_to_scene_points(
    path: Iterable[GridNode],
    *,
    cell_size: float = 1.0,
    z: float = 0.0,
) -> list[tuple[float, float, float]]:
    """Конвертирует путь из ячеек в координаты сцены Blender.

    Полезно для передачи в create_path_curve() из visualize_path_in_blender.py.
    """
    return [(col * cell_size, row * cell_size, z) for (col, row) in path]
