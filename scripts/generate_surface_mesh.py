"""
generate_surface_mesh.py
========================
Генератор mesh-поверхности z = f(x, y) с единым CLI и валидацией.

Примеры:
1. Blender GUI: Scripting -> Open -> scripts/generate_surface_mesh.py -> Run Script.
2. CLI:
   blender --background --python scripts\generate_surface_mesh.py -- --function gaussian --sigma 1.8 --resolution 90
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
    import bmesh

    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("[INFO] bpy не найден — запуск вне Blender (режим preview).")


OBJECT_NAME = "MathSurface_Mesh"


def remove_existing_object(name: str) -> None:
    if name not in bpy.data.objects:
        return
    obj = bpy.data.objects[name]
    mesh = obj.data if getattr(obj, "type", None) == "MESH" else None
    bpy.data.objects.remove(obj, do_unlink=True)
    if mesh is not None and mesh.users == 0:
        bpy.data.meshes.remove(mesh)


def create_blender_mesh(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int, int]],
) -> "bpy.types.Object":
    remove_existing_object(name)

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


def add_default_material(obj: "bpy.types.Object", function_name: str) -> None:
    colors = {
        "paraboloid": (0.2, 0.5, 0.9, 1.0),
        "saddle": (0.25, 0.8, 0.4, 1.0),
        "wave": (0.9, 0.55, 0.1, 1.0),
        "ripple": (0.65, 0.3, 0.95, 1.0),
        "gaussian": (0.95, 0.25, 0.25, 1.0),
        "custom": (0.95, 0.9, 0.2, 1.0),
    }
    base_color = colors.get(function_name, (0.5, 0.5, 0.5, 1.0))
    material_name = f"Mat_{function_name}"

    material = bpy.data.materials.get(material_name)
    if material is None:
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True

    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = base_color
        bsdf.inputs["Roughness"].default_value = 0.4
        bsdf.inputs["Metallic"].default_value = 0.0

    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def ensure_camera_and_light() -> None:
    if "MeshCamera" not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(10, -10, 9))
        camera = bpy.context.active_object
        camera.name = "MeshCamera"
        camera.rotation_euler = (1.1, 0.0, 0.785)
        bpy.context.scene.camera = camera

    if "MeshSun" not in bpy.data.objects:
        bpy.ops.object.light_add(type="SUN", location=(5, 5, 10))
        sun = bpy.context.active_object
        sun.name = "MeshSun"
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


def print_preview(config: SurfaceConfig) -> None:
    print("Preview функции (вне Blender):")
    for x, y, z in preview_values(config):
        print(f"  f({x:5.1f}, {y:5.1f}) = {z:10.5f}")


def main() -> None:
    config, cli_args = parse_common_cli_args(
        "Генерация mesh-поверхности из математической функции.",
        include_output=True,
        default_function="wave",
        default_resolution=60,
    )
    print(f"[START] generate_surface_mesh.py | {describe_surface_config(config)}")

    if not HAS_BPY:
        if cli_args.output:
            print("[WARN] Параметр --output работает только при запуске через Blender.")
        print_preview(config)
        return

    vertices, faces = generate_surface_geometry(config)
    obj = create_blender_mesh(OBJECT_NAME, vertices, faces)
    add_default_material(obj, config.function)
    ensure_camera_and_light()

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

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
