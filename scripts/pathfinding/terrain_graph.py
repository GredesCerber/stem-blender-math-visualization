"""
terrain_graph.py
================
Построение сеточного графа поверхности z = f(x, y).
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from dataclasses import dataclass

from function_library import SurfaceConfig, generate_surface_grid

from .cost_functions import CostWeights, composite_edge_cost

GridNode = tuple[int, int]
Point3D = tuple[float, float, float]
ObstacleCircle = tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class TerrainNodeData:
    x: float
    y: float
    z: float
    risk: float = 0.0
    blocked: bool = False

    @property
    def point(self) -> Point3D:
        return (self.x, self.y, self.z)


class TerrainGraph:
    def __init__(
        self,
        *,
        x_values: list[float],
        y_values: list[float],
        nodes: dict[GridNode, TerrainNodeData],
        connectivity: int = 8,
    ) -> None:
        if connectivity not in (4, 8):
            raise ValueError("connectivity должен быть 4 или 8.")
        self.x_values = x_values
        self.y_values = y_values
        self.nodes = nodes
        self.connectivity = connectivity

    def is_blocked(self, node: GridNode) -> bool:
        return self.nodes[node].blocked

    def point(self, node: GridNode) -> Point3D:
        return self.nodes[node].point

    def risk(self, node: GridNode) -> float:
        return self.nodes[node].risk

    def neighbors(self, node: GridNode) -> list[GridNode]:
        i, j = node
        cardinal = ((1, 0), (-1, 0), (0, 1), (0, -1))
        diagonal = ((1, 1), (1, -1), (-1, 1), (-1, -1))
        directions = cardinal + diagonal if self.connectivity == 8 else cardinal

        result: list[GridNode] = []
        for di, dj in directions:
            n = (i + di, j + dj)
            data = self.nodes.get(n)
            if data is not None and not data.blocked:
                result.append(n)
        return result

    def edge_cost(self, a: GridNode, b: GridNode, weights: CostWeights) -> float:
        risk_penalty = 0.5 * (self.risk(a) + self.risk(b))
        return composite_edge_cost(
            self.point(a),
            self.point(b),
            weights=weights,
            risk_penalty=risk_penalty,
        )

    def closest_node(self, x: float, y: float, *, allow_blocked: bool = False) -> GridNode:
        best_node: GridNode | None = None
        best_distance = math.inf
        for node, data in self.nodes.items():
            if data.blocked and not allow_blocked:
                continue
            dx = data.x - x
            dy = data.y - y
            distance = dx * dx + dy * dy
            if distance < best_distance:
                best_distance = distance
                best_node = node

        if best_node is None:
            raise ValueError("В графе нет доступных узлов для выбора start/goal.")
        return best_node

    def path_to_points(self, path: Iterable[GridNode]) -> list[Point3D]:
        return [self.point(node) for node in path]


def _inside_any_obstacle(
    x: float,
    y: float,
    obstacle_circles: Iterable[ObstacleCircle],
) -> bool:
    for cx, cy, radius in obstacle_circles:
        dx = x - cx
        dy = y - cy
        if dx * dx + dy * dy <= radius * radius:
            return True
    return False


def build_terrain_graph(
    config: SurfaceConfig,
    *,
    connectivity: int = 8,
    blocked_nodes: Iterable[GridNode] | None = None,
    blocked_z_greater_than: float | None = None,
    obstacle_circles: Iterable[ObstacleCircle] | None = None,
    risk_function: Callable[[float, float, float], float] | None = None,
) -> TerrainGraph:
    if connectivity not in (4, 8):
        raise ValueError("connectivity должен быть 4 или 8.")

    obstacle_circles = tuple(obstacle_circles or ())
    blocked_set = set(blocked_nodes or ())

    x_values, y_values, z_grid = generate_surface_grid(config)
    nodes: dict[GridNode, TerrainNodeData] = {}

    for j, y in enumerate(y_values):
        for i, x in enumerate(x_values):
            z = z_grid[j][i]
            blocked = (i, j) in blocked_set

            if blocked_z_greater_than is not None and z > blocked_z_greater_than:
                blocked = True
            if obstacle_circles and _inside_any_obstacle(x, y, obstacle_circles):
                blocked = True

            risk = 0.0
            if risk_function is not None:
                candidate = float(risk_function(x, y, z))
                if not math.isfinite(candidate):
                    raise ValueError("risk_function вернула некорректное значение.")
                risk = max(candidate, 0.0)

            nodes[(i, j)] = TerrainNodeData(x=x, y=y, z=z, risk=risk, blocked=blocked)

    return TerrainGraph(
        x_values=x_values,
        y_values=y_values,
        nodes=nodes,
        connectivity=connectivity,
    )
