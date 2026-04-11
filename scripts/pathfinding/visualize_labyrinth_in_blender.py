r"""
visualize_labyrinth_in_blender.py
=================================
Генерация лабиринта и визуализация пути (A*/Dijkstra) в Blender.

Примеры:
1) Быстрый запуск с дефолтами:
   blender --background --python scripts\pathfinding\visualize_labyrinth_in_blender.py

2) Свой размер и seed:
   blender --background --python scripts\pathfinding\visualize_labyrinth_in_blender.py -- --rows 25 --cols 25 --seed 7 --algorithm dijkstra --output assets\renders\labyrinth_25x25_dijkstra.png

Вне Blender скрипт также работает — он напечатает ASCII-лабиринт с маршрутом
и (опционально) сохранит путь в CSV.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_ROOT = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(SCRIPTS_ROOT)
for path in (SCRIPT_DIR, SCRIPTS_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from pathfinding.labyrinth import (  # noqa: E402
    WALL,
    find_path_in_maze,
    generate_maze,
    maze_path_to_scene_points,
    maze_start_goal,
    print_maze,
)

try:
    import bpy  # type: ignore
    from enhanced_camera_utils import (
        aim_camera_at_bbox,
        mesh_world_bbox,
        setup_angled_camera,
        setup_dramatic_light,
    )

    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("[INFO] bpy не найден — будет только ASCII-вывод и (опционально) CSV.")


LABYRINTH_OBJECT = "Labyrinth_Walls"
FLOOR_OBJECT = "Labyrinth_Floor"
PATH_OBJECT = "Labyrinth_Path"
MARKER_START = "Labyrinth_START"
MARKER_GOAL = "Labyrinth_GOAL"
DEFAULT_STARTUP_OBJECTS = ("Cube", "Camera", "Light")


def extract_user_argv() -> list[str]:
    """Возвращает аргументы после `--` (для совместимости с blender --)."""
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1 :]
    # Запуск вне Blender: берём обычные аргументы.
    return sys.argv[1:]


def parse_cli() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Генерация лабиринта и поиск пути в нём."
    )
    parser.add_argument("--rows", type=int, default=21, help="Число строк (нечётное).")
    parser.add_argument("--cols", type=int, default=21, help="Число столбцов (нечётное).")
    parser.add_argument("--seed", type=int, default=42, help="Seed генерации.")
    parser.add_argument(
        "--algorithm",
        choices=("astar", "dijkstra"),
        default="astar",
        help="Алгоритм поиска пути.",
    )
    parser.add_argument(
        "--cell-size",
        type=float,
        default=1.0,
        help="Размер ячейки в единицах сцены.",
    )
    parser.add_argument(
        "--wall-height",
        type=float,
        default=1.0,
        help="Высота стен в единицах сцены.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Путь к PNG-рендеру (только внутри Blender).",
    )
    parser.add_argument(
        "--path-output",
        default=None,
        help="CSV-файл с координатами точек маршрута.",
    )
    parser.add_argument(
        "--no-path",
        action="store_true",
        help="Не рисовать маршрут и маркеры (только сам лабиринт).",
    )
    return parser.parse_args(extract_user_argv())


def write_path_csv(points: list[tuple[float, float, float]], output_path: str) -> None:
    target = output_path
    if not os.path.isabs(target):
        target = os.path.join(PROJECT_ROOT, target)
    target = os.path.normpath(target)

    directory = os.path.dirname(target)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x", "y", "z"])
        for x, y, z in points:
            writer.writerow([f"{x:.6f}", f"{y:.6f}", f"{z:.6f}"])
    print(f"[OK] Точки маршрута сохранены: {target}")


# ---------------------------------------------------------------------------
# Blender-часть: строится только при HAS_BPY.
# ---------------------------------------------------------------------------


def remove_object_if_exists(name: str) -> None:
    if name not in bpy.data.objects:
        return
    obj = bpy.data.objects[name]
    obj_type = obj.type
    data = getattr(obj, "data", None)
    bpy.data.objects.remove(obj, do_unlink=True)
    if data is not None and getattr(data, "users", 1) == 0:
        if obj_type == "MESH":
            bpy.data.meshes.remove(data)
        elif obj_type == "CURVE":
            bpy.data.curves.remove(data)


def clear_default_startup_objects() -> None:
    for name in DEFAULT_STARTUP_OBJECTS:
        remove_object_if_exists(name)


def build_walls_mesh(
    maze: list[list[int]],
    *,
    cell_size: float,
    wall_height: float,
) -> "bpy.types.Object":
    """Строит единый mesh из кубов-стен."""
    remove_object_if_exists(LABYRINTH_OBJECT)

    vertices: list[tuple[float, float, float]] = []
    faces: list[tuple[int, int, int, int]] = []

    rows = len(maze)
    cols = len(maze[0])
    half = cell_size / 2.0

    for i in range(rows):
        for j in range(cols):
            if maze[i][j] != WALL:
                continue
            cx = j * cell_size
            cy = i * cell_size
            base = len(vertices)
            # 8 вершин куба (низ + верх).
            corners = [
                (cx - half, cy - half, 0.0),
                (cx + half, cy - half, 0.0),
                (cx + half, cy + half, 0.0),
                (cx - half, cy + half, 0.0),
                (cx - half, cy - half, wall_height),
                (cx + half, cy - half, wall_height),
                (cx + half, cy + half, wall_height),
                (cx - half, cy + half, wall_height),
            ]
            vertices.extend(corners)
            faces.extend(
                [
                    (base + 0, base + 1, base + 2, base + 3),  # низ
                    (base + 4, base + 5, base + 6, base + 7),  # верх
                    (base + 0, base + 1, base + 5, base + 4),
                    (base + 1, base + 2, base + 6, base + 5),
                    (base + 2, base + 3, base + 7, base + 6),
                    (base + 3, base + 0, base + 4, base + 7),
                ]
            )

    mesh = bpy.data.meshes.new(name=f"{LABYRINTH_OBJECT}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(LABYRINTH_OBJECT, mesh)
    bpy.context.collection.objects.link(obj)

    mat = bpy.data.materials.new(name="Mat_LabyrinthWall")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.25, 0.3, 0.45, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.7
    obj.data.materials.append(mat)
    return obj


def build_floor(rows: int, cols: int, cell_size: float) -> "bpy.types.Object":
    remove_object_if_exists(FLOOR_OBJECT)
    half = cell_size / 2.0
    x_min = -half
    y_min = -half
    x_max = (cols - 1) * cell_size + half
    y_max = (rows - 1) * cell_size + half

    vertices = [
        (x_min, y_min, -0.01),
        (x_max, y_min, -0.01),
        (x_max, y_max, -0.01),
        (x_min, y_max, -0.01),
    ]
    faces = [(0, 1, 2, 3)]

    mesh = bpy.data.meshes.new(name=f"{FLOOR_OBJECT}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(FLOOR_OBJECT, mesh)
    bpy.context.collection.objects.link(obj)

    mat = bpy.data.materials.new(name="Mat_LabyrinthFloor")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.85, 0.85, 0.82, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.9
    obj.data.materials.append(mat)
    return obj


def build_path_curve(
    points: list[tuple[float, float, float]],
    *,
    wall_height: float,
) -> "bpy.types.Object":
    remove_object_if_exists(PATH_OBJECT)

    lifted = [(x, y, z + wall_height * 0.25) for (x, y, z) in points]

    curve_data = bpy.data.curves.new(name=f"{PATH_OBJECT}_curve", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.bevel_depth = 0.08
    curve_data.bevel_resolution = 6

    spline = curve_data.splines.new("POLY")
    spline.points.add(len(lifted) - 1)
    for idx, (x, y, z) in enumerate(lifted):
        spline.points[idx].co = (x, y, z, 1.0)

    obj = bpy.data.objects.new(PATH_OBJECT, curve_data)
    bpy.context.collection.objects.link(obj)

    mat = bpy.data.materials.new(name="Mat_LabyrinthPath")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (1.0, 0.2, 0.15, 1.0)
        emission = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission is not None:
            emission.default_value = (1.0, 0.3, 0.15, 1.0)
        strength = bsdf.inputs.get("Emission Strength")
        if strength is not None:
            strength.default_value = 1.0
    obj.data.materials.append(mat)
    return obj


def create_marker(
    name: str,
    position: tuple[float, float, float],
    color: tuple[float, float, float, float],
    radius: float = 0.25,
) -> "bpy.types.Object":
    remove_object_if_exists(name)
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius,
        location=(position[0], position[1], position[2] + radius),
        segments=16,
        ring_count=8,
    )
    obj = bpy.context.active_object
    obj.name = name

    mat = bpy.data.materials.new(name=f"Mat_{name}")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        emission = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission is not None:
            emission.default_value = color
        strength = bsdf.inputs.get("Emission Strength")
        if strength is not None:
            strength.default_value = 2.0
    obj.data.materials.append(mat)
    return obj


def ensure_camera_and_light(rows: int, cols: int, cell_size: float) -> None:
    cx = (cols - 1) * cell_size / 2.0
    cy = (rows - 1) * cell_size / 2.0
    span = max(rows, cols) * cell_size
    cam_loc = (cx + span * 0.55, cy - span * 0.55, span * 0.9)
    cam_rot = (math.radians(55), 0, math.radians(45))
    setup_angled_camera(location=cam_loc, rotation_euler=cam_rot)
    setup_dramatic_light(
        location=(cx + span * 0.5, cy + span * 0.5, span * 1.2),
        energy=5.0,
    )


def render_to_png(output_path: str) -> None:
    if output_path.startswith("//"):
        full_path = bpy.path.abspath(output_path)
    elif os.path.isabs(output_path):
        full_path = output_path
    else:
        full_path = os.path.join(PROJECT_ROOT, output_path)
    full_path = os.path.normpath(full_path)

    out_dir = os.path.dirname(full_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    scene = bpy.context.scene
    scene.render.filepath = full_path
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Рендер сохранён: {full_path}")


def main() -> None:
    args = parse_cli()
    maze = generate_maze(args.rows, args.cols, seed=args.seed)
    start, goal = maze_start_goal(maze)

    result = find_path_in_maze(
        maze,
        start,
        goal,
        algorithm=args.algorithm,
        cell_size=args.cell_size,
    )
    if not result.success:
        raise ValueError("Путь в лабиринте не найден — проверьте параметры.")

    print(
        f"[OK] Лабиринт {len(maze)}x{len(maze[0])} seed={args.seed} | "
        f"{args.algorithm}: {len(result.path)} ячеек, "
        f"стоимость={result.total_cost:.2f}, посещено={result.visited_nodes}."
    )
    print_maze(maze, path=result.path, start=start, goal=goal)

    scene_points = maze_path_to_scene_points(
        result.path,
        cell_size=args.cell_size,
        z=0.0,
    )
    if args.path_output:
        write_path_csv(scene_points, args.path_output)

    if not HAS_BPY:
        return

    clear_default_startup_objects()
    floor_obj = build_floor(len(maze), len(maze[0]), args.cell_size)
    walls_obj = build_walls_mesh(maze, cell_size=args.cell_size, wall_height=args.wall_height)

    if not args.no_path:
        build_path_curve(scene_points, wall_height=args.wall_height)
        start_point = (start[0] * args.cell_size, start[1] * args.cell_size, 0.0)
        goal_point = (goal[0] * args.cell_size, goal[1] * args.cell_size, 0.0)
        create_marker(MARKER_START, start_point, color=(0.05, 0.9, 0.15, 1.0))
        create_marker(MARKER_GOAL, goal_point, color=(1.0, 0.85, 0.0, 1.0))

    ensure_camera_and_light(len(maze), len(maze[0]), args.cell_size)

    # Динамически наводим камеру на реальный bbox всей сцены (пол + стены),
    # чтобы лабиринт целиком попадал в кадр при любом размере.
    (fmin_x, fmin_y, fmin_z), (fmax_x, fmax_y, fmax_z) = mesh_world_bbox(floor_obj)
    (wmin_x, wmin_y, wmin_z), (wmax_x, wmax_y, wmax_z) = mesh_world_bbox(walls_obj)
    scene_min = (min(fmin_x, wmin_x), min(fmin_y, wmin_y), min(fmin_z, wmin_z))
    scene_max = (max(fmax_x, wmax_x), max(fmax_y, wmax_y), max(fmax_z, wmax_z))
    camera_obj = bpy.data.objects.get("Camera")
    if camera_obj is not None:
        # Более крутой top-down ракурс, чтобы маршрут был виден между стен,
        # и чуть меньший distance_factor, чтобы лабиринт заполнял кадр.
        aim_camera_at_bbox(
            camera_obj,
            scene_min,
            scene_max,
            direction=(0.6, -0.6, 1.6),
            distance_factor=2.2,
        )

    if args.output:
        render_to_png(args.output)

    print("[DONE] Сцена лабиринта собрана.")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(2)
