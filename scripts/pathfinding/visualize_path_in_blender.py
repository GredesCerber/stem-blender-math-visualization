"""
visualize_path_in_blender.py
============================
Построение маршрута (A* или Dijkstra) по поверхности z = f(x, y).

Примеры:
1) Без препятствий:
   blender --background --python scripts\pathfinding\visualize_path_in_blender.py -- --function paraboloid --algorithm astar --start-x -4 --start-y -4 --goal-x 4 --goal-y 4

2) С препятствием:
   blender --background --python scripts\pathfinding\visualize_path_in_blender.py -- --function wave --algorithm dijkstra --obstacle-circle 0,0,1.5 --start-x -4 --start-y -4 --goal-x 4 --goal-y 4
"""

from __future__ import annotations

import csv
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_ROOT = os.path.dirname(SCRIPT_DIR)
for path in (SCRIPT_DIR, SCRIPTS_ROOT):
    if path not in sys.path:
        sys.path.insert(0, path)

from function_library import (  # noqa: E402
    build_common_parser,
    describe_surface_config,
    extract_user_argv,
    generate_surface_geometry,
    namespace_to_surface_config,
    validate_surface_config,
)
from pathfinding.cost_functions import CostWeights  # noqa: E402
from pathfinding.search import run_search  # noqa: E402
from pathfinding.terrain_graph import ObstacleCircle, build_terrain_graph  # noqa: E402

try:
    import bpy

    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("[INFO] bpy не найден — маршрут будет рассчитан без 3D-визуализации.")


SURFACE_OBJECT_NAME = "MathSurface_Pathfinding"
PATH_OBJECT_NAME = "SurfacePath"


def parse_obstacle_circle(raw: str) -> ObstacleCircle:
    try:
        x_str, y_str, r_str = raw.split(",")
        x = float(x_str)
        y = float(y_str)
        radius = float(r_str)
    except ValueError as exc:
        raise ValueError(
            "Формат --obstacle-circle должен быть x,y,r (например 0,0,1.5)."
        ) from exc
    if radius <= 0:
        raise ValueError("Радиус obstacle-circle должен быть > 0.")
    return (x, y, radius)


def parse_cli():
    parser = build_common_parser(
        "Поиск пути по поверхности z = f(x, y).",
        include_output=True,
        default_function="paraboloid",
        default_resolution=80,
    )
    parser.add_argument(
        "--algorithm",
        choices=("astar", "dijkstra"),
        default="astar",
        help="Алгоритм поиска пути.",
    )
    parser.add_argument("--start-x", type=float, default=-4.0)
    parser.add_argument("--start-y", type=float, default=-4.0)
    parser.add_argument("--goal-x", type=float, default=4.0)
    parser.add_argument("--goal-y", type=float, default=4.0)
    parser.add_argument("--w-len", type=float, default=1.0, help="Вес длины ребра.")
    parser.add_argument("--w-slope", type=float, default=1.0, help="Вес уклона.")
    parser.add_argument("--w-risk", type=float, default=0.0, help="Вес risk-поля.")
    parser.add_argument(
        "--alpha",
        type=float,
        default=1.0,
        help="Коэффициент штрафа уклона.",
    )
    parser.add_argument(
        "--blocked-z-gt",
        type=float,
        default=None,
        help="Блокировать узлы с z выше указанного порога.",
    )
    parser.add_argument(
        "--obstacle-circle",
        action="append",
        default=[],
        help="Круговое препятствие в формате x,y,r (можно указать несколько раз).",
    )
    parser.add_argument(
        "--path-output",
        default=None,
        help="CSV для точек маршрута (полезно вне Blender).",
    )
    parser.add_argument(
        "--curve-name",
        default=PATH_OBJECT_NAME,
        help="Имя Curve-объекта маршрута в Blender.",
    )
    namespace = parser.parse_args(extract_user_argv())

    config = namespace_to_surface_config(namespace)
    validate_surface_config(config)

    weights = CostWeights(
        w_len=namespace.w_len,
        w_slope=namespace.w_slope,
        w_risk=namespace.w_risk,
        alpha=namespace.alpha,
    )
    weights.validate()

    circles = tuple(parse_obstacle_circle(item) for item in namespace.obstacle_circle)
    return config, namespace, weights, circles


def write_path_csv(points: list[tuple[float, float, float]], output_path: str) -> None:
    directory = os.path.dirname(output_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x", "y", "z"])
        for x, y, z in points:
            writer.writerow([f"{x:.6f}", f"{y:.6f}", f"{z:.6f}"])
    print(f"[OK] Точки маршрута сохранены: {output_path}")


def remove_object_if_exists(name: str) -> None:
    if name not in bpy.data.objects:
        return
    obj = bpy.data.objects[name]
    data = getattr(obj, "data", None)
    bpy.data.objects.remove(obj, do_unlink=True)
    if data is not None and getattr(data, "users", 1) == 0:
        if obj.type == "MESH":
            bpy.data.meshes.remove(data)
        elif obj.type == "CURVE":
            bpy.data.curves.remove(data)


def create_surface_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int, int]],
) -> "bpy.types.Object":
    remove_object_if_exists(name)
    mesh = bpy.data.meshes.new(name=f"{name}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def add_surface_material(obj: "bpy.types.Object") -> None:
    mat_name = "Mat_PathSurface"
    material = bpy.data.materials.get(mat_name)
    if material is None:
        material = bpy.data.materials.new(name=mat_name)
        material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.2, 0.45, 0.85, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.45
        bsdf.inputs["Metallic"].default_value = 0.0

    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def create_path_curve(
    name: str,
    points: list[tuple[float, float, float]],
) -> "bpy.types.Object":
    remove_object_if_exists(name)
    curve_data = bpy.data.curves.new(name=f"{name}_curve", type="CURVE")
    curve_data.dimensions = "3D"
    curve_data.resolution_u = 12
    curve_data.bevel_depth = 0.04
    curve_data.bevel_resolution = 6

    spline = curve_data.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for idx, (x, y, z) in enumerate(points):
        spline.points[idx].co = (x, y, z + 0.04, 1.0)

    obj = bpy.data.objects.new(name, curve_data)
    bpy.context.collection.objects.link(obj)
    return obj


def add_path_material(obj: "bpy.types.Object") -> None:
    mat_name = "Mat_PathCurve"
    material = bpy.data.materials.get(mat_name)
    if material is None:
        material = bpy.data.materials.new(name=mat_name)
        material.use_nodes = True
    nodes = material.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (1.0, 0.2, 0.15, 1.0)
        emission_color = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if emission_color is not None:
            emission_color.default_value = (1.0, 0.25, 0.15, 1.0)
        emission_strength = bsdf.inputs.get("Emission Strength")
        if emission_strength is not None:
            emission_strength.default_value = 0.5

    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def ensure_camera_and_light() -> None:
    if "PathCamera" not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(12, -12, 10))
        camera = bpy.context.active_object
        camera.name = "PathCamera"
        camera.rotation_euler = (1.1, 0.0, 0.785)
        bpy.context.scene.camera = camera
    if "PathSun" not in bpy.data.objects:
        bpy.ops.object.light_add(type="SUN", location=(6, 6, 11))
        sun = bpy.context.active_object
        sun.name = "PathSun"
        sun.data.energy = 3.5


def render_to_png(output_path: str) -> None:
    full_path = bpy.path.abspath(output_path)
    output_dir = os.path.dirname(full_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    scene = bpy.context.scene
    scene.render.filepath = full_path
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    print(f"[OK] Рендер сохранён: {full_path}")


def main() -> None:
    config, args, weights, circles = parse_cli()
    print(f"[START] pathfinding | {describe_surface_config(config)}")

    graph = build_terrain_graph(
        config,
        connectivity=8,
        blocked_z_greater_than=args.blocked_z_gt,
        obstacle_circles=circles,
    )
    start = graph.closest_node(args.start_x, args.start_y)
    goal = graph.closest_node(args.goal_x, args.goal_y)

    result = run_search(args.algorithm, graph, start, goal, weights=weights)
    if not result.success:
        raise ValueError("Маршрут не найден. Измените препятствия или область построения.")

    path_points = graph.path_to_points(result.path)
    print(
        f"[OK] Маршрут найден: {len(result.path)} узлов, "
        f"стоимость={result.total_cost:.4f}, "
        f"посещено={result.visited_nodes}, "
        f"проверено рёбер={result.expanded_edges}."
    )

    if args.path_output:
        write_path_csv(path_points, args.path_output)

    if not HAS_BPY:
        return

    vertices, faces = generate_surface_geometry(config)
    surface_obj = create_surface_object(SURFACE_OBJECT_NAME, vertices, faces)
    add_surface_material(surface_obj)

    path_obj = create_path_curve(args.curve_name, path_points)
    add_path_material(path_obj)
    ensure_camera_and_light()

    bpy.ops.object.select_all(action="DESELECT")
    path_obj.select_set(True)
    bpy.context.view_layer.objects.active = path_obj

    if args.output:
        render_to_png(args.output)

    print(f"[DONE] Curve-маршрут '{path_obj.name}' построен поверх '{surface_obj.name}'.")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(2)
