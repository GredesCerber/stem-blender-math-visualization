"""
setup_geometry_nodes_surface.py
===============================
Автонастройка Geometry Nodes для волновой поверхности z = A*sin(k*x)*cos(k*y).

Примеры:
1. Blender GUI: Scripting -> Open -> scripts/setup_geometry_nodes_surface.py -> Run Script.
2. CLI:
   blender --background --python scripts/setup_geometry_nodes_surface.py -- --function wave --resolution 90 --amplitude 2 --frequency 3
"""

from __future__ import annotations

import argparse
import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from function_library import (  # noqa: E402
    SurfaceConfig,
    build_common_parser,
    describe_surface_config,
    extract_user_argv,
    namespace_to_surface_config,
    preview_values,
    validate_surface_config,
)

try:
    import bpy
    from enhanced_camera_utils import setup_angled_camera, setup_dramatic_light

    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("[INFO] bpy не найден — запуск вне Blender (режим preview).")


OBJECT_NAME = "MathSurface_GN"
NODE_GROUP_NAME = "MathSurface_GN_Group"
DEFAULT_STARTUP_OBJECTS = ("Cube", "Camera", "Light")

PRESETS: dict[str, dict[str, float | int]] = {
    "lesson_default": {"amplitude": 1.0, "frequency": 1.0, "resolution": 80},
    "gentle_wave": {"amplitude": 0.5, "frequency": 0.7, "resolution": 70},
    "dynamic_wave": {"amplitude": 2.0, "frequency": 2.5, "resolution": 100},
}


def remove_existing(name: str) -> None:
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)


def clear_default_objects() -> None:
    """Удалить дефолтные объекты Blender (куб, свет, камеру)."""
    for obj_name in DEFAULT_STARTUP_OBJECTS:
        remove_existing(obj_name)


def remove_existing_for_grid(name: str) -> None:
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])


def add_group_socket(
    node_group: "bpy.types.GeometryNodeTree",
    *,
    name: str,
    socket_type: str,
    in_out: str,
):
    interface = getattr(node_group, "interface", None)
    if interface is not None and hasattr(interface, "new_socket"):
        return interface.new_socket(name=name, in_out=in_out, socket_type=socket_type)

    if in_out == "INPUT":
        return node_group.inputs.new(socket_type, name)
    return node_group.outputs.new(socket_type, name)


def configure_float_socket(
    socket,
    *,
    default: float,
    min_value: float,
    max_value: float,
) -> None:
    if hasattr(socket, "default_value"):
        socket.default_value = default
    if hasattr(socket, "min_value"):
        socket.min_value = min_value
    if hasattr(socket, "max_value"):
        socket.max_value = max_value


def create_wave_node_group(
    *,
    name: str,
    amplitude: float,
    frequency: float,
    domain_half_size: float,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
) -> "bpy.types.GeometryNodeTree":
    remove_node_group(name)
    node_group = bpy.data.node_groups.new(name=name, type="GeometryNodeTree")
    nodes = node_group.nodes
    links = node_group.links

    add_group_socket(
        node_group,
        name="Geometry",
        socket_type="NodeSocketGeometry",
        in_out="INPUT",
    )
    amp_socket = add_group_socket(
        node_group,
        name="Amplitude",
        socket_type="NodeSocketFloat",
        in_out="INPUT",
    )
    freq_socket = add_group_socket(
        node_group,
        name="Frequency",
        socket_type="NodeSocketFloat",
        in_out="INPUT",
    )
    add_group_socket(
        node_group,
        name="Geometry",
        socket_type="NodeSocketGeometry",
        in_out="OUTPUT",
    )

    configure_float_socket(
        amp_socket,
        default=amplitude,
        min_value=0.0,
        max_value=20.0,
    )
    configure_float_socket(
        freq_socket,
        default=frequency,
        min_value=0.0,
        max_value=20.0,
    )

    n_input = nodes.new("NodeGroupInput")
    n_input.location = (-1200, 80)

    n_output = nodes.new("NodeGroupOutput")
    n_output.location = (900, 80)

    n_setpos = nodes.new("GeometryNodeSetPosition")
    n_setpos.location = (680, 80)

    n_position = nodes.new("GeometryNodeInputPosition")
    n_position.location = (-1200, -320)

    n_sep = nodes.new("ShaderNodeSeparateXYZ")
    n_sep.location = (-1000, -320)

    n_map_x = nodes.new("ShaderNodeMapRange")
    n_map_x.location = (-790, -200)
    n_map_x.inputs["From Min"].default_value = -domain_half_size
    n_map_x.inputs["From Max"].default_value = domain_half_size
    n_map_x.inputs["To Min"].default_value = x_min
    n_map_x.inputs["To Max"].default_value = x_max

    n_map_y = nodes.new("ShaderNodeMapRange")
    n_map_y.location = (-790, -420)
    n_map_y.inputs["From Min"].default_value = -domain_half_size
    n_map_y.inputs["From Max"].default_value = domain_half_size
    n_map_y.inputs["To Min"].default_value = y_min
    n_map_y.inputs["To Max"].default_value = y_max

    n_mul_x = nodes.new("ShaderNodeMath")
    n_mul_x.operation = "MULTIPLY"
    n_mul_x.location = (-570, -200)

    n_mul_y = nodes.new("ShaderNodeMath")
    n_mul_y.operation = "MULTIPLY"
    n_mul_y.location = (-570, -420)

    n_sin = nodes.new("ShaderNodeMath")
    n_sin.operation = "SINE"
    n_sin.location = (-360, -200)

    n_cos = nodes.new("ShaderNodeMath")
    n_cos.operation = "COSINE"
    n_cos.location = (-360, -420)

    n_mul_wave = nodes.new("ShaderNodeMath")
    n_mul_wave.operation = "MULTIPLY"
    n_mul_wave.location = (-140, -300)

    n_mul_amp = nodes.new("ShaderNodeMath")
    n_mul_amp.operation = "MULTIPLY"
    n_mul_amp.location = (60, -300)

    n_combine = nodes.new("ShaderNodeCombineXYZ")
    n_combine.location = (300, -80)

    links.new(n_input.outputs["Geometry"], n_setpos.inputs["Geometry"])
    links.new(n_setpos.outputs["Geometry"], n_output.inputs["Geometry"])

    links.new(n_position.outputs["Position"], n_sep.inputs["Vector"])
    links.new(n_sep.outputs["X"], n_map_x.inputs["Value"])
    links.new(n_sep.outputs["Y"], n_map_y.inputs["Value"])

    links.new(n_map_x.outputs["Result"], n_mul_x.inputs[0])
    links.new(n_input.outputs["Frequency"], n_mul_x.inputs[1])
    links.new(n_mul_x.outputs["Value"], n_sin.inputs["Value"])

    links.new(n_map_y.outputs["Result"], n_mul_y.inputs[0])
    links.new(n_input.outputs["Frequency"], n_mul_y.inputs[1])
    links.new(n_mul_y.outputs["Value"], n_cos.inputs["Value"])

    links.new(n_sin.outputs["Value"], n_mul_wave.inputs[0])
    links.new(n_cos.outputs["Value"], n_mul_wave.inputs[1])

    links.new(n_mul_wave.outputs["Value"], n_mul_amp.inputs[0])
    links.new(n_input.outputs["Amplitude"], n_mul_amp.inputs[1])

    links.new(n_map_x.outputs["Result"], n_combine.inputs["X"])
    links.new(n_map_y.outputs["Result"], n_combine.inputs["Y"])
    links.new(n_mul_amp.outputs["Value"], n_combine.inputs["Z"])
    links.new(n_combine.outputs["Vector"], n_setpos.inputs["Position"])

    return node_group


def create_grid_object(
    *,
    name: str,
    half_size: float,
    subdivisions: int,
) -> "bpy.types.Object":
    bpy.ops.mesh.primitive_grid_add(
        x_subdivisions=subdivisions,
        y_subdivisions=subdivisions,
        size=half_size,
        location=(0, 0, 0),
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def apply_geometry_nodes_modifier(
    obj: "bpy.types.Object",
    node_group: "bpy.types.GeometryNodeTree",
) -> None:
    modifier = obj.modifiers.new(name="GeoNodes_Surface", type="NODES")
    modifier.node_group = node_group


def add_material(obj: "bpy.types.Object") -> None:
    mat_name = "Mat_GN_Surface"
    material = bpy.data.materials.get(mat_name)
    if material is None:
        material = bpy.data.materials.new(name=mat_name)
        material.use_nodes = True

    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.1, 0.4, 0.9, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.35
        bsdf.inputs["Metallic"].default_value = 0.1

    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def setup_camera_and_light() -> None:
    """Установить камеру сбоку с углом для 3D-эффекта."""
    setup_angled_camera(
        location=(13, -11, 8),
        rotation_euler=(math.radians(60), 0, math.radians(40)),
    )
    setup_dramatic_light(
        location=(10, 10, 12),
        energy=4.0,
    )


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


def parse_cli() -> tuple[SurfaceConfig, argparse.Namespace]:
    parser = build_common_parser(
        "Автонастройка Geometry Nodes для волновой поверхности.",
        include_output=True,
        default_function="wave",
        default_resolution=80,
    )
    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        default=None,
        help="Пользовательский пресет параметров.",
    )
    namespace = parser.parse_args(extract_user_argv())

    if namespace.preset is not None:
        preset = PRESETS[namespace.preset]
        namespace.amplitude = float(preset["amplitude"])
        namespace.frequency = float(preset["frequency"])
        namespace.resolution = int(preset["resolution"])

    config = namespace_to_surface_config(namespace)
    validate_surface_config(config)
    if config.function != "wave":
        raise ValueError(
            "setup_geometry_nodes_surface.py поддерживает только --function wave "
            "для интерактивного GN-режима."
        )
    return config, namespace


def print_preview(config: SurfaceConfig) -> None:
    print("Preview функции (вне Blender):")
    for x, y, z in preview_values(config):
        print(f"  f({x:5.1f}, {y:5.1f}) = {z:10.5f}")


def main() -> None:
    config, args = parse_cli()
    print(f"[START] setup_geometry_nodes_surface.py | {describe_surface_config(config)}")

    if not HAS_BPY:
    clear_default_objects()
    remove_existing_for_gridput:
            print("[WARN] Параметр --output работает только при запуске через Blender.")
        print_preview(config)
        return

    domain_half_size = max(config.x_span, config.y_span) / 2.0
    remove_existing(OBJECT_NAME)
    node_group = create_wave_node_group(
        name=NODE_GROUP_NAME,
        amplitude=config.amplitude,
        frequency=config.frequency,
        domain_half_size=domain_half_size,
        x_min=config.x_min,
        x_max=config.x_max,
        y_min=config.y_min,
        y_max=config.y_max,
    )
    obj = create_grid_object(
        name=OBJECT_NAME,
        half_size=domain_half_size,
        subdivisions=config.resolution,
    )
    apply_geometry_nodes_modifier(obj, node_group)
    add_material(obj)
    setup_camera_and_light()

    obj["gn_preset_lesson_default"] = "A=1.0,k=1.0,res=80"
    obj["gn_preset_gentle_wave"] = "A=0.5,k=0.7,res=70"
    obj["gn_preset_dynamic_wave"] = "A=2.0,k=2.5,res=100"

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    if args.output:
        render_to_png(args.output)

    print(f"[DONE] Объект '{obj.name}' с Geometry Nodes создан.")
    if args.preset:
        print(f"[INFO] Применён пресет: {args.preset}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(2)
