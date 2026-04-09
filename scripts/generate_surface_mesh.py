"""
generate_surface_mesh.py
========================
Учебный STEM-проект: Интерактивная 3D-визуализация математических функций.

Скрипт строит полигональную сетку для поверхности z = f(x, y).
Запуск в Blender создаёт объект в сцене, запуск вне Blender делает
текстовый preview нескольких значений функции.
"""

from __future__ import annotations

import math
from collections.abc import Callable

try:
    import bpy
    import bmesh

    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("[INFO] bpy не найден — запуск вне Blender (только preview формулы)")


# ============================================================
# ПАРАМЕТРЫ
# ============================================================

X_MIN: float = -5.0
X_MAX: float = 5.0
Y_MIN: float = -5.0
Y_MAX: float = 5.0

RESOLUTION: int = 60
AMPLITUDE: float = 1.0
FREQUENCY: float = 1.0
SIGMA: float = 2.0

# "paraboloid" | "saddle" | "wave" | "ripple" | "gaussian" | "custom"
FUNCTION_NAME: str = "wave"
OBJECT_NAME: str = "MathSurface"


# ============================================================
# ФУНКЦИИ z = f(x, y)
# ============================================================

SurfaceFunction = Callable[[float, float], float]


def f_paraboloid(x: float, y: float) -> float:
    return x**2 + y**2


def f_saddle(x: float, y: float) -> float:
    return x**2 - y**2


def f_wave(x: float, y: float) -> float:
    return AMPLITUDE * math.sin(FREQUENCY * x) * math.cos(FREQUENCY * y)


def f_ripple(x: float, y: float) -> float:
    radius = math.sqrt(x**2 + y**2)
    return AMPLITUDE * math.sin(radius)


def f_gaussian(x: float, y: float) -> float:
    return AMPLITUDE * math.exp(-(x**2 + y**2) / (SIGMA**2))


def f_custom(x: float, y: float) -> float:
    return math.sin(x) + math.cos(y)


FUNCTION_MAP: dict[str, SurfaceFunction] = {
    "paraboloid": f_paraboloid,
    "saddle": f_saddle,
    "wave": f_wave,
    "ripple": f_ripple,
    "gaussian": f_gaussian,
    "custom": f_custom,
}


# ============================================================
# ВАЛИДАЦИЯ И ВЫБОР ФУНКЦИИ
# ============================================================

def validate_parameters() -> None:
    if RESOLUTION < 2:
        raise ValueError("RESOLUTION должен быть >= 2.")
    if X_MAX <= X_MIN:
        raise ValueError("X_MAX должен быть больше X_MIN.")
    if Y_MAX <= Y_MIN:
        raise ValueError("Y_MAX должен быть больше Y_MIN.")
    if FUNCTION_NAME == "gaussian" and SIGMA <= 0:
        raise ValueError("SIGMA должен быть > 0 для гауссовой функции.")

    numeric_params = {
        "X_MIN": X_MIN,
        "X_MAX": X_MAX,
        "Y_MIN": Y_MIN,
        "Y_MAX": Y_MAX,
        "AMPLITUDE": AMPLITUDE,
        "FREQUENCY": FREQUENCY,
        "SIGMA": SIGMA,
    }
    for name, value in numeric_params.items():
        if not math.isfinite(value):
            raise ValueError(f"{name} должен быть конечным числом.")


def get_surface_function(function_name: str) -> SurfaceFunction:
    if function_name not in FUNCTION_MAP:
        allowed = ", ".join(FUNCTION_MAP.keys())
        raise ValueError(
            f"Неизвестная функция '{function_name}'. Допустимые значения: {allowed}."
        )
    return FUNCTION_MAP[function_name]


# ============================================================
# ПОСТРОЕНИЕ СЕТКИ (MESH)
# ============================================================

def build_surface_vertices(
    f_func: SurfaceFunction,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    n: int,
) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int, int]]]:
    dx = (x_max - x_min) / n
    dy = (y_max - y_min) / n

    vertices: list[tuple[float, float, float]] = []
    for i in range(n + 1):
        for j in range(n + 1):
            x = x_min + i * dx
            y = y_min + j * dy
            try:
                z = float(f_func(x, y))
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
    for i in range(n):
        for j in range(n):
            a = i * (n + 1) + j
            b = a + 1
            c = (i + 1) * (n + 1) + j + 1
            d = (i + 1) * (n + 1) + j
            faces.append((a, b, c, d))

    return vertices, faces


def create_blender_mesh(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int, int]],
) -> "bpy.types.Object":
    if not HAS_BPY:
        raise RuntimeError("create_blender_mesh доступен только внутри Blender.")

    mesh = bpy.data.meshes.new(name=f"{name}_mesh")
    obj = bpy.data.objects.new(name=name, object_data=mesh)
    bpy.context.collection.objects.link(obj)

    bm = bmesh.new()
    bm_verts = [bm.verts.new(vertex) for vertex in vertices]
    bm.verts.ensure_lookup_table()

    for face_indices in faces:
        bm.faces.new([bm_verts[index] for index in face_indices])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    mesh.calc_normals()

    return obj


def remove_existing_object(name: str) -> None:
    if not HAS_BPY:
        return
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        mesh = obj.data if getattr(obj, "type", None) == "MESH" else None
        bpy.data.objects.remove(obj, do_unlink=True)
        if mesh is not None and mesh.users == 0:
            bpy.data.meshes.remove(mesh)


def add_default_material(obj: "bpy.types.Object", function_name: str) -> None:
    color_map = {
        "paraboloid": (0.2, 0.5, 0.9, 1.0),
        "saddle": (0.2, 0.8, 0.4, 1.0),
        "wave": (0.9, 0.5, 0.1, 1.0),
        "ripple": (0.6, 0.2, 0.9, 1.0),
        "gaussian": (0.9, 0.2, 0.2, 1.0),
        "custom": (0.9, 0.9, 0.2, 1.0),
    }
    base_color = color_map.get(function_name, (0.5, 0.5, 0.5, 1.0))

    mat_name = f"Mat_{function_name}"
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = base_color
            bsdf.inputs["Roughness"].default_value = 0.4
            bsdf.inputs["Metallic"].default_value = 0.0

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


# ============================================================
# ОСНОВНАЯ ЛОГИКА
# ============================================================

def print_formula_preview(f_func: SurfaceFunction) -> None:
    print("Preview функции (без Blender):")
    sample_points = [(-2.0, -2.0), (-1.0, 0.0), (0.0, 0.0), (1.0, 1.0), (2.0, 2.0)]
    for x, y in sample_points:
        z = f_func(x, y)
        print(f"  f({x:5.1f}, {y:5.1f}) = {z:8.4f}")


def main() -> None:
    validate_parameters()
    f_func = get_surface_function(FUNCTION_NAME)

    print(f"\n{'=' * 50}")
    print("  STEM-проект: Визуализация поверхности")
    print(f"  Функция: {FUNCTION_NAME}")
    print(f"  Разрешение: {RESOLUTION}×{RESOLUTION}")
    print(f"  Область: X=[{X_MIN}, {X_MAX}], Y=[{Y_MIN}, {Y_MAX}]")
    print(f"{'=' * 50}\n")

    if not HAS_BPY:
        print_formula_preview(f_func)
        return

    remove_existing_object(OBJECT_NAME)
    vertices, faces = build_surface_vertices(f_func, X_MIN, X_MAX, Y_MIN, Y_MAX, RESOLUTION)
    print(f"  Вершин: {len(vertices)}, граней: {len(faces)}")

    obj = create_blender_mesh(OBJECT_NAME, vertices, faces)
    add_default_material(obj, FUNCTION_NAME)

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    print(f"\n  ✓ Объект '{OBJECT_NAME}' создан.")
    print("  Нажмите Numpad . для центровки вида на объект.\n")


if __name__ == "__main__":
    main()
