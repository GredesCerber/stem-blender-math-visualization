from __future__ import annotations

import math
import os
import sys
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
SCRIPTS_DIR = os.path.abspath(SCRIPTS_DIR)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from function_library import SurfaceConfig  # noqa: E402
from pathfinding.cost_functions import CostWeights  # noqa: E402
from pathfinding.search import a_star, dijkstra  # noqa: E402
from pathfinding.terrain_graph import build_terrain_graph  # noqa: E402


class PathfindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = SurfaceConfig(
            function="paraboloid",
            resolution=30,
            x_min=-5.0,
            x_max=5.0,
            y_min=-5.0,
            y_max=5.0,
            amplitude=0.1,
        )
        self.weights = CostWeights(w_len=1.0, w_slope=0.5, w_risk=0.0, alpha=1.0)

    def test_astar_and_dijkstra_find_path(self) -> None:
        graph = build_terrain_graph(self.config, connectivity=8)
        start = graph.closest_node(-4.0, -4.0)
        goal = graph.closest_node(4.0, 4.0)

        dijkstra_result = dijkstra(graph, start, goal, weights=self.weights)
        astar_result = a_star(graph, start, goal, weights=self.weights)

        self.assertTrue(dijkstra_result.success)
        self.assertTrue(astar_result.success)
        self.assertGreater(len(dijkstra_result.path), 2)
        self.assertGreater(len(astar_result.path), 2)
        self.assertTrue(math.isfinite(dijkstra_result.total_cost))
        self.assertTrue(math.isfinite(astar_result.total_cost))

    def test_path_avoids_circle_obstacle(self) -> None:
        graph = build_terrain_graph(
            self.config,
            connectivity=8,
            obstacle_circles=((0.0, 0.0, 1.5),),
        )
        start = graph.closest_node(-4.0, -4.0)
        goal = graph.closest_node(4.0, 4.0)
        result = a_star(graph, start, goal, weights=self.weights)

        self.assertTrue(result.success)
        for node in result.path:
            self.assertFalse(graph.is_blocked(node))


if __name__ == "__main__":
    unittest.main()
