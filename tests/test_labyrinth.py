from __future__ import annotations

import os
import sys
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
SCRIPTS_DIR = os.path.abspath(SCRIPTS_DIR)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from pathfinding.labyrinth import (  # noqa: E402
    FREE,
    WALL,
    find_path_in_maze,
    generate_maze,
    maze_path_to_scene_points,
    maze_start_goal,
    maze_to_terrain_graph,
)


class LabyrinthGenerationTests(unittest.TestCase):
    def test_seed_is_reproducible(self) -> None:
        a = generate_maze(21, 21, seed=42)
        b = generate_maze(21, 21, seed=42)
        self.assertEqual(a, b)

    def test_different_seeds_produce_different_mazes(self) -> None:
        a = generate_maze(21, 21, seed=1)
        b = generate_maze(21, 21, seed=2)
        self.assertNotEqual(a, b)

    def test_even_dimensions_bumped_to_odd(self) -> None:
        maze = generate_maze(10, 12, seed=0)
        self.assertEqual(len(maze), 11)
        self.assertEqual(len(maze[0]), 13)

    def test_border_is_wall(self) -> None:
        maze = generate_maze(15, 15, seed=3)
        rows = len(maze)
        cols = len(maze[0])
        for j in range(cols):
            self.assertEqual(maze[0][j], WALL)
            self.assertEqual(maze[rows - 1][j], WALL)
        for i in range(rows):
            self.assertEqual(maze[i][0], WALL)
            self.assertEqual(maze[i][cols - 1], WALL)

    def test_start_and_goal_free(self) -> None:
        maze = generate_maze(21, 21, seed=99)
        start, goal = maze_start_goal(maze)
        self.assertEqual(maze[start[1]][start[0]], FREE)
        self.assertEqual(maze[goal[1]][goal[0]], FREE)

    def test_cells_are_only_zero_or_one(self) -> None:
        maze = generate_maze(13, 17, seed=5)
        for row in maze:
            for cell in row:
                self.assertIn(cell, (FREE, WALL))


class LabyrinthPathfindingTests(unittest.TestCase):
    def test_astar_finds_path(self) -> None:
        maze = generate_maze(21, 21, seed=42)
        start, goal = maze_start_goal(maze)
        result = find_path_in_maze(maze, start, goal, algorithm="astar")
        self.assertTrue(result.success)
        self.assertEqual(result.path[0], start)
        self.assertEqual(result.path[-1], goal)

    def test_dijkstra_finds_path(self) -> None:
        maze = generate_maze(21, 21, seed=42)
        start, goal = maze_start_goal(maze)
        result = find_path_in_maze(maze, start, goal, algorithm="dijkstra")
        self.assertTrue(result.success)

    def test_path_passes_only_through_free_cells(self) -> None:
        maze = generate_maze(21, 21, seed=42)
        start, goal = maze_start_goal(maze)
        result = find_path_in_maze(maze, start, goal, algorithm="astar")
        for col, row in result.path:
            self.assertEqual(maze[row][col], FREE)

    def test_path_steps_are_adjacent(self) -> None:
        """Соседние узлы пути должны отличаться ровно на 1 ячейку (4-связность)."""
        maze = generate_maze(15, 15, seed=7)
        start, goal = maze_start_goal(maze)
        result = find_path_in_maze(maze, start, goal, algorithm="astar")
        for (c1, r1), (c2, r2) in zip(result.path, result.path[1:]):
            distance = abs(c1 - c2) + abs(r1 - r2)
            self.assertEqual(distance, 1)

    def test_no_path_when_start_blocked(self) -> None:
        maze = generate_maze(11, 11, seed=1)
        # Намеренно превращаем старт в стену и берём другую свободную точку как цель.
        start, goal = maze_start_goal(maze)
        maze[start[1]][start[0]] = WALL
        with self.assertRaises(ValueError):
            find_path_in_maze(maze, start, goal, algorithm="astar")

    def test_astar_and_dijkstra_same_length_on_perfect_maze(self) -> None:
        """В идеальном лабиринте путь между двумя точками единственный."""
        maze = generate_maze(21, 21, seed=11)
        start, goal = maze_start_goal(maze)
        a = find_path_in_maze(maze, start, goal, algorithm="astar")
        d = find_path_in_maze(maze, start, goal, algorithm="dijkstra")
        self.assertEqual(len(a.path), len(d.path))


class LabyrinthIntegrationTests(unittest.TestCase):
    def test_maze_to_terrain_graph_structure(self) -> None:
        maze = generate_maze(9, 9, seed=0)
        graph = maze_to_terrain_graph(maze, cell_size=2.0)
        self.assertEqual(len(graph.nodes), 9 * 9)
        # Стена должна быть blocked.
        for i, row in enumerate(maze):
            for j, cell in enumerate(row):
                self.assertEqual(graph.is_blocked((j, i)), cell == WALL)
        # cell_size применяется к координатам.
        self.assertAlmostEqual(graph.point((1, 1))[0], 2.0)
        self.assertAlmostEqual(graph.point((1, 1))[1], 2.0)

    def test_scene_points_conversion(self) -> None:
        path = [(0, 0), (1, 0), (1, 1)]
        points = maze_path_to_scene_points(path, cell_size=0.5, z=1.0)
        self.assertEqual(
            points,
            [(0.0, 0.0, 1.0), (0.5, 0.0, 1.0), (0.5, 0.5, 1.0)],
        )


if __name__ == "__main__":
    unittest.main()
