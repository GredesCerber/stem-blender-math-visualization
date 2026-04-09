"""
visualize_function.py
=====================
STEM-проект: интерактивная 3D-визуализация математических функций в Blender.

Использование:
1. Blender: Scripting -> Open -> scripts/visualize_function.py -> Run Script.
2. CLI (без Blender): python scripts/visualize_function.py
"""

import math
import os
import sys

try:
    import bpy

    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("[INFO] bpy не найден — запуск вне Blender (только preview формулы)")


# ============================================================
# === ФОРМУЛА — ЕДИНСТВЕННОЕ МЕСТО, КОТОРОЕ НУЖНО МЕНЯТЬ ===
# ============================================================

def surface_function(x: float, y: float) -> float:
    """
    Функция z = f(x, y).
    Измените тело функции для смены поверхности.
    """
    # Параболоид (чаша): z = x^2 + y^2
    return x**2 + y**2

    # Волна: z = A * sin(k*x) * cos(k*y)
    # A, k = 1.0, 1.0
    # return A * math.sin(k * x) * math.cos(k * y)

    # Седло: z = x^2 - y^2
    # return x**2 - y**2

    # Круговые волны: z = sin(sqrt(x^2 + y^2))
    # r = math.sqrt(x**2 + y**2)
    # return math.sin(r) if r > 1e-6 else 1.0

    # Гауссов колокол: z = exp(-(x^2 + y^2))
    # return math.exp(-(x**2 + y**2))

    # Затухающая волна: z = A * sin(k*x) * exp(-alpha*y^2)
    # A, k, alpha = 1.0, 2.0, 0.3
    # return A * math.sin(k * x) * math.exp(-alpha * y**2)


# ============================================================
# === ПАРАМЕТРЫ СЕТКИ ===
# ============================================================

GRID_SUBDIVISIONS = 100
GRID_HALF_SIZE = 5.0
OBJECT_NAME = "MathSurface"


# ============================================================
# === ВНУТРЕННЯЯ ЛОГИКА — ОБЫЧНО МЕНЯТЬ НЕ НУЖНО ===
# ============================================================

def validate_grid_parameters(n: int, half_size: float) -> None:
    if n < 2:
        raise ValueError("GRID_SUBDIVISIONS должен быть >= 2.")
    if half_size <= 0:
        raise ValueError("GRID_HALF_SIZE должен быть > 0.")


def get_cli_output_path() -> str | None:
    """
    Читает путь для рендера из аргументов Blender:
    blender --background --python scripts/visualize_function.py -- --output result.png
    """
    if "--" not in sys.argv:
        return None

    args = sys.argv[sys.argv.index("--") + 1 :]
    for index, arg in enumerate(args):
        if arg in ("--output", "-o"):
            if index + 1 >= len(args):
                raise ValueError("Параметр --output требует путь к файлу PNG.")
            return args[index + 1]
    return None


def generate_vertices_and_faces(
    func,
    n: int,
    half_size: float,
) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int, int]]]:
    validate_grid_parameters(n, half_size)

    vertices: list[tuple[float, float, float]] = []
    step = (2.0 * half_size) / n

    for j in range(n + 1):
        for i in range(n + 1):
            x = -half_size + i * step
            y = -half_size + j * step
            try:
                z = float(func(x, y))
            except (ValueError, ZeroDivisionError, OverflowError) as exc:
                raise ValueError(
                    f"Ошибка вычисления функции в точке (x={x:.4f}, y={y:.4f})."
                ) from exc

            if not math.isfinite(z):
                raise ValueError(
                    f"Функция вернула некорректное значение z={z} "
                    f"в точке (x={x:.4f}, y={y:.4f})."
                )
            vertices.append((x, y, z))

    faces: list[tuple[int, int, int, int]] = []
    row_len = n + 1
    for j in range(n):
        for i in range(n):
            v0 = j * row_len + i
            v1 = j * row_len + (i + 1)
            v2 = (j + 1) * row_len + (i + 1)
            v3 = (j + 1) * row_len + i
            faces.append((v0, v1, v2, v3))

    return vertices, faces


def create_surface_object(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int, int]],
    name: str,
) -> None:
    if name in bpy.data.objects:
        old_obj = bpy.data.objects[name]
        old_mesh = old_obj.data if getattr(old_obj, "type", None) == "MESH" else None
        bpy.data.objects.remove(old_obj, do_unlink=True)
        if old_mesh is not None and old_mesh.users == 0:
            bpy.data.meshes.remove(old_mesh)

    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    print(f"[OK] Объект '{name}' создан: {len(vertices)} вершин, {len(faces)} граней")


def add_color_material(obj_name: str) -> None:
    if obj_name not in bpy.data.objects:
        raise KeyError(f"Объект '{obj_name}' не найден для применения материала.")

    obj = bpy.data.objects[obj_name]
    obj.data.materials.clear()

    mat = bpy.data.materials.new(name=f"{obj_name}_Material")
    mat.use_nodes = True
    obj.data.materials.append(mat)

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    geom = nodes.new("ShaderNodeNewGeometry")
    geom.location = (-400, 0)

    sep = nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-200, 0)
    links.new(geom.outputs["Position"], sep.inputs["Vector"])

    map_range = nodes.new("ShaderNodeMapRange")
    map_range.location = (0, 0)
    map_range.inputs["From Min"].default_value = -GRID_HALF_SIZE
    map_range.inputs["From Max"].default_value = GRID_HALF_SIZE
    map_range.inputs["To Min"].default_value = 0.0
    map_range.inputs["To Max"].default_value = 1.0
    links.new(sep.outputs["Z"], map_range.inputs["Value"])

    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.location = (150, 100)
    color_ramp.color_ramp.elements[0].color = (0.0, 0.1, 0.8, 1.0)
    color_ramp.color_ramp.elements[1].color = (0.8, 0.0, 0.0, 1.0)
    mid_elem = color_ramp.color_ramp.elements.new(0.5)
    mid_elem.color = (0.0, 0.8, 0.1, 1.0)

    links.new(map_range.outputs["Result"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])

    print(f"[OK] Материал с цветовой картой применён к '{obj_name}'")


def ensure_camera_and_light() -> None:
    if "Camera" not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(10, -10, 10))
        cam = bpy.context.active_object
        cam.name = "Camera"
        cam.rotation_euler = (1.1, 0.0, 0.785)
        bpy.context.scene.camera = cam

    if "Sun" not in bpy.data.objects:
        bpy.ops.object.light_add(type="SUN", location=(5, 5, 10))
        sun = bpy.context.active_object
        sun.name = "Sun"
        sun.data.energy = 3.0


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


def print_formula_preview() -> None:
    print("Проверка формулы (без Blender):")
    for x in [-2.0, -1.0, 0.0, 1.0, 2.0]:
        for y in [-1.0, 0.0, 1.0]:
            z = surface_function(x, y)
            print(f"  f({x:5.1f}, {y:5.1f}) = {z:8.4f}")


def main() -> None:
    output_path = get_cli_output_path()

    if not HAS_BPY:
        if output_path:
            print("[WARN] Параметр --output доступен только при запуске через Blender.")
        print_formula_preview()
        return

    print(f"\n[START] Генерация поверхности '{OBJECT_NAME}'")
    print(
        f"  Сетка: {GRID_SUBDIVISIONS}×{GRID_SUBDIVISIONS}, "
        f"область: [{-GRID_HALF_SIZE}, {GRID_HALF_SIZE}]^2"
    )

    vertices, faces = generate_vertices_and_faces(
        func=surface_function,
        n=GRID_SUBDIVISIONS,
        half_size=GRID_HALF_SIZE,
    )
    create_surface_object(vertices, faces, OBJECT_NAME)
    add_color_material(OBJECT_NAME)
    ensure_camera_and_light()

    if output_path:
        render_to_png(output_path)

    print(f"[DONE] Объект '{OBJECT_NAME}' готов к рендеру\n")


if __name__ == "__main__":
    main()
