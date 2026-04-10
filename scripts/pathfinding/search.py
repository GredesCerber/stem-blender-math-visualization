"""
search.py
=========
Алгоритмы Dijkstra и A* для поиска пути по графу поверхности.
"""

from __future__ import annotations

import heapq
import math
from dataclasses import dataclass

from .cost_functions import CostWeights, edge_length_3d
from .terrain_graph import GridNode, TerrainGraph


@dataclass(frozen=True, slots=True)
class SearchResult:
    algorithm: str
    start: GridNode
    goal: GridNode
    path: list[GridNode]
    total_cost: float
    visited_nodes: int
    expanded_edges: int

    @property
    def success(self) -> bool:
        return bool(self.path)


def _reconstruct_path(
    came_from: dict[GridNode, GridNode],
    start: GridNode,
    goal: GridNode,
) -> list[GridNode]:
    if goal != start and goal not in came_from:
        return []

    node = goal
    path = [node]
    while node != start:
        node = came_from[node]
        path.append(node)
    path.reverse()
    return path


def _heuristic(graph: TerrainGraph, node: GridNode, goal: GridNode) -> float:
    return edge_length_3d(graph.point(node), graph.point(goal))


def _validate_endpoints(graph: TerrainGraph, start: GridNode, goal: GridNode) -> None:
    if start not in graph.nodes:
        raise ValueError(f"Start-узел {start} отсутствует в графе.")
    if goal not in graph.nodes:
        raise ValueError(f"Goal-узел {goal} отсутствует в графе.")
    if graph.is_blocked(start):
        raise ValueError("Start-узел находится в блокированной зоне.")
    if graph.is_blocked(goal):
        raise ValueError("Goal-узел находится в блокированной зоне.")


def dijkstra(
    graph: TerrainGraph,
    start: GridNode,
    goal: GridNode,
    *,
    weights: CostWeights,
) -> SearchResult:
    weights.validate()
    _validate_endpoints(graph, start, goal)

    frontier: list[tuple[float, GridNode]] = [(0.0, start)]
    came_from: dict[GridNode, GridNode] = {}
    best_cost: dict[GridNode, float] = {start: 0.0}
    visited_nodes = 0
    expanded_edges = 0

    while frontier:
        current_cost, current = heapq.heappop(frontier)
        if current_cost > best_cost.get(current, math.inf):
            continue

        visited_nodes += 1
        if current == goal:
            break

        for neighbor in graph.neighbors(current):
            expanded_edges += 1
            new_cost = current_cost + graph.edge_cost(current, neighbor, weights)
            if new_cost < best_cost.get(neighbor, math.inf):
                best_cost[neighbor] = new_cost
                came_from[neighbor] = current
                heapq.heappush(frontier, (new_cost, neighbor))

    path = _reconstruct_path(came_from, start, goal)
    total_cost = best_cost.get(goal, math.inf)
    if not path:
        total_cost = math.inf

    return SearchResult(
        algorithm="dijkstra",
        start=start,
        goal=goal,
        path=path,
        total_cost=total_cost,
        visited_nodes=visited_nodes,
        expanded_edges=expanded_edges,
    )


def a_star(
    graph: TerrainGraph,
    start: GridNode,
    goal: GridNode,
    *,
    weights: CostWeights,
) -> SearchResult:
    weights.validate()
    _validate_endpoints(graph, start, goal)

    frontier: list[tuple[float, GridNode]] = [(0.0, start)]
    came_from: dict[GridNode, GridNode] = {}
    g_cost: dict[GridNode, float] = {start: 0.0}
    visited_nodes = 0
    expanded_edges = 0

    while frontier:
        _, current = heapq.heappop(frontier)
        current_g = g_cost[current]
        visited_nodes += 1
        if current == goal:
            break

        for neighbor in graph.neighbors(current):
            expanded_edges += 1
            tentative_g = current_g + graph.edge_cost(current, neighbor, weights)
            if tentative_g < g_cost.get(neighbor, math.inf):
                g_cost[neighbor] = tentative_g
                came_from[neighbor] = current
                priority = tentative_g + _heuristic(graph, neighbor, goal)
                heapq.heappush(frontier, (priority, neighbor))

    path = _reconstruct_path(came_from, start, goal)
    total_cost = g_cost.get(goal, math.inf)
    if not path:
        total_cost = math.inf

    return SearchResult(
        algorithm="astar",
        start=start,
        goal=goal,
        path=path,
        total_cost=total_cost,
        visited_nodes=visited_nodes,
        expanded_edges=expanded_edges,
    )


def run_search(
    algorithm: str,
    graph: TerrainGraph,
    start: GridNode,
    goal: GridNode,
    *,
    weights: CostWeights,
) -> SearchResult:
    normalized = algorithm.strip().lower()
    if normalized in {"dijkstra", "djikstra"}:
        return dijkstra(graph, start, goal, weights=weights)
    if normalized in {"astar", "a*", "a-star"}:
        return a_star(graph, start, goal, weights=weights)
    raise ValueError("algorithm должен быть 'dijkstra' или 'astar'.")
