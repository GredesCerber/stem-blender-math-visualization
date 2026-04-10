"""
visualize_function.py
=====================
Быстрый генератор поверхности z = f(x, y) в Blender с цветовой картой и рендером PNG.

Примеры:
1. Blender GUI: Scripting -> Open -> scripts/visualize_function.py -> Run Script.
2. CLI:
   blender --background --python scripts/visualize_function.py -- --function wave --resolution 100 --output assets/renders/wave_cli.png
"""

from __future__ import annotations

import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from function_library import (  # noqa: E402
    SurfaceConfig,
    describe_surface_config,
    generate_surface_geometry,
    parse_common_cli_args,
    preview_values,
)

try:
    import bpy
    from enhanced_camera_utils import setup_camera_for_function

    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("[INFO] bpy не найден — запуск вне Blender (режим preview).")


OBJECT_NAME = "MathSurface_Python"


def remove_existing_object(name: str) -> None:
    if name not in bpy.data.objects:
        return
    old_obj = bpy.data.objects[name]
    old_mesh = old_obj.data if getattr(old_obj, "type", None) == "MESH" else None
    bpy.data.objects.remove(old_obj, do_unlink=True)
    if old_mesh is not None and old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)


def create_surface_object(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int, int]],
    name: str,
) -> "bpy.types.Object":
    remove_existing_object(name)

    mesh = bpy.data.meshes.new(name=f"{name}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    return obj


def add_color_material(
    obj: "bpy.types.Object",
    *,
    z_min: float,
    z_max: float,
) -> None:
    if z_max <= z_min:
        z_min, z_max = z_min - 1.0, z_max + 1.0

    obj.data.materials.clear()

    mat = bpy.data.materials.new(name=f"{obj.name}_Material")
    mat.use_nodes = True
    obj.data.materials.append(mat)

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Metallic"].default_value = 0.0
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    geom = nodes.new("ShaderNodeNewGeometry")
    geom.location = (-420, 0)

    sep = nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-220, 0)
    links.new(geom.outputs["Position"], sep.inputs["Vector"])

    map_range = nodes.new("ShaderNodeMapRange")
    map_range.location = (-20, 0)
    map_range.inputs["From Min"].default_value = z_min
    map_range.inputs["From Max"].default_value = z_max
    map_range.inputs["To Min"].default_value = 0.0
    map_range.inputs["To Max"].default_value = 1.0
    links.new(sep.outputs["Z"], map_range.inputs["Value"])

    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.location = (170, 100)
    color_ramp.color_ramp.elements[0].color = (0.05, 0.2, 0.85, 1.0)
    color_ramp.color_ramp.elements[1].color = (0.9, 0.1, 0.1, 1.0)
    middle = color_ramp.color_ramp.elements.new(0.5)
    middle.color = (0.1, 0.8, 0.2, 1.0)

    links.new(map_range.outputs["Result"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])


def clear_default_objects() -> None:
    """Удалить дефолтные объекты Blender (куб, свет, камеру)."""
    for obj_name in ["Cube", "Camera", "Light"]:
        if obj_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)


def ensure_camera_and_light(function_name: str = "default") -> None:
    """Установить камеру и свет с оптимальным углом для 3D-вида."""
    setup_camera_for_function(function_name)


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


def print_formula_preview(config: SurfaceConfig) -> None:
    print("Preview функции (вне Blender):")
    for x, y, z in preview_values(config):
        print(f"  f({x:5.1f}, {y:5.1f}) = {z:10.5f}")


def main() -> None:
    config, cli_args = parse_common_cli_args(
        "Быстрый генератор поверхности с материалом и рендером.",
        include_output=True,
        default_function="paraboloid",
        default_resolution=100,
    )
    print(f"[START] visualize_function.py | {describe_surface_config(config)}")

    if not HAS_BPY:
        if cli_args.output:
            print("[WARN] Параметр --output работает только при запуске через Blender.")
        print_formula_preview(config)
        return

    clear_default_objects()
    vertices, faces = generate_surface_geometry(config)
    obj = create_surface_object(vertices, faces, OBJECT_NAME)
    z_values = [vertex[2] for vertex in vertices]
    add_color_material(obj, z_min=min(z_values), z_max=max(z_values))
    ensure_camera_and_light(config.function)  # оптимальная камера для каждой функции

    if cli_args.output:
        render_to_png(cli_args.output)

    print(
        f"[DONE] Объект '{obj.name}' создан: {len(vertices)} вершин, "
        f"{len(faces)} граней."
    )


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(2)
