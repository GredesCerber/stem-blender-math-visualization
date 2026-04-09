"""
setup_geometry_nodes_surface.py
================================
Учебный STEM-проект: настройка Geometry Nodes для поверхности
z = A * sin(k*x) * cos(k*y).

Скрипт создаёт объект-сетку и модификатор Geometry Nodes с двумя
параметрами: Amplitude и Frequency.
"""

from __future__ import annotations

import math

try:
    import bpy

    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("[INFO] bpy не найден — запуск вне Blender (создание сцены пропущено)")


# ============================================================
# ПАРАМЕТРЫ СЦЕНЫ
# ============================================================

GRID_SIZE: float = 10.0
GRID_SUBDIVISIONS: int = 80
DEFAULT_AMPLITUDE: float = 1.0
DEFAULT_FREQUENCY: float = 1.0
OBJECT_NAME: str = "GN_Surface"
NODE_GROUP_NAME: str = "MathSurface_GN"


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def validate_parameters() -> None:
    if GRID_SIZE <= 0:
        raise ValueError("GRID_SIZE должен быть > 0.")
    if GRID_SUBDIVISIONS < 2:
        raise ValueError("GRID_SUBDIVISIONS должен быть >= 2.")

    for name, value in (
        ("DEFAULT_AMPLITUDE", DEFAULT_AMPLITUDE),
        ("DEFAULT_FREQUENCY", DEFAULT_FREQUENCY),
    ):
        if not math.isfinite(value):
            raise ValueError(f"{name} должен быть конечным числом.")
        if value < 0:
            raise ValueError(f"{name} должен быть >= 0.")


def remove_existing(name: str) -> None:
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)


def remove_node_group(name: str) -> None:
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])


def add_group_socket(
    node_group: "bpy.types.GeometryNodeTree",
    *,
    name: str,
    socket_type: str,
    in_out: str,
):
    """Создаёт сокет группы нод с поддержкой Blender 3.6+ и 4.x."""
    interface = getattr(node_group, "interface", None)
    if interface is not None and hasattr(interface, "new_socket"):
        return interface.new_socket(name=name, in_out=in_out, socket_type=socket_type)

    if in_out == "INPUT":
        return node_group.inputs.new(socket_type, name)
    return node_group.outputs.new(socket_type, name)


def configure_float_socket(socket, *, default: float, min_value: float, max_value: float) -> None:
    if hasattr(socket, "default_value"):
        socket.default_value = default
    if hasattr(socket, "min_value"):
        socket.min_value = min_value
    if hasattr(socket, "max_value"):
        socket.max_value = max_value


# ============================================================
# СОЗДАНИЕ GEOMETRY NODES ГРАФА
# ============================================================

def create_wave_node_group(name: str) -> "bpy.types.GeometryNodeTree":
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
        default=DEFAULT_AMPLITUDE,
        min_value=0.0,
        max_value=10.0,
    )
    configure_float_socket(
        freq_socket,
        default=DEFAULT_FREQUENCY,
        min_value=0.0,
        max_value=10.0,
    )

    n_input = nodes.new("NodeGroupInput")
    n_input.location = (-800, 0)

    n_output = nodes.new("NodeGroupOutput")
    n_output.location = (700, 0)

    n_position = nodes.new("GeometryNodeInputPosition")
    n_position.location = (-800, -220)

    n_sep = nodes.new("ShaderNodeSeparateXYZ")
    n_sep.location = (-600, -220)

    n_mul_x = nodes.new("ShaderNodeMath")
    n_mul_x.operation = "MULTIPLY"
    n_mul_x.location = (-420, -90)

    n_sin = nodes.new("ShaderNodeMath")
    n_sin.operation = "SINE"
    n_sin.location = (-220, -90)

    n_mul_y = nodes.new("ShaderNodeMath")
    n_mul_y.operation = "MULTIPLY"
    n_mul_y.location = (-420, -320)

    n_cos = nodes.new("ShaderNodeMath")
    n_cos.operation = "COSINE"
    n_cos.location = (-220, -320)

    n_mul_sincos = nodes.new("ShaderNodeMath")
    n_mul_sincos.operation = "MULTIPLY"
    n_mul_sincos.location = (0, -210)

    n_mul_amp = nodes.new("ShaderNodeMath")
    n_mul_amp.operation = "MULTIPLY"
    n_mul_amp.location = (190, -210)

    n_combine = nodes.new("ShaderNodeCombineXYZ")
    n_combine.location = (230, 80)

    n_setpos = nodes.new("GeometryNodeSetPosition")
    n_setpos.location = (470, 0)

    links.new(n_input.outputs["Geometry"], n_setpos.inputs["Geometry"])
    links.new(n_setpos.outputs["Geometry"], n_output.inputs["Geometry"])

    links.new(n_position.outputs["Position"], n_sep.inputs["Vector"])
    links.new(n_sep.outputs["X"], n_mul_x.inputs[0])
    links.new(n_input.outputs["Frequency"], n_mul_x.inputs[1])
    links.new(n_mul_x.outputs["Value"], n_sin.inputs["Value"])

    links.new(n_sep.outputs["Y"], n_mul_y.inputs[0])
    links.new(n_input.outputs["Frequency"], n_mul_y.inputs[1])
    links.new(n_mul_y.outputs["Value"], n_cos.inputs["Value"])

    links.new(n_sin.outputs["Value"], n_mul_sincos.inputs[0])
    links.new(n_cos.outputs["Value"], n_mul_sincos.inputs[1])

    links.new(n_mul_sincos.outputs["Value"], n_mul_amp.inputs[0])
    links.new(n_input.outputs["Amplitude"], n_mul_amp.inputs[1])

    links.new(n_sep.outputs["X"], n_combine.inputs["X"])
    links.new(n_sep.outputs["Y"], n_combine.inputs["Y"])
    links.new(n_mul_amp.outputs["Value"], n_combine.inputs["Z"])
    links.new(n_combine.outputs["Vector"], n_setpos.inputs["Position"])

    return node_group


# ============================================================
# СОЗДАНИЕ ОБЪЕКТА И НАСТРОЙКА СЦЕНЫ
# ============================================================

def create_grid_object(name: str, size: float, subdivisions: int) -> "bpy.types.Object":
    bpy.ops.mesh.primitive_grid_add(
        x_subdivisions=subdivisions,
        y_subdivisions=subdivisions,
        size=size,
        location=(0, 0, 0),
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def apply_geometry_nodes_modifier(
    obj: "bpy.types.Object",
    node_group: "bpy.types.GeometryNodeTree",
) -> "bpy.types.Modifier":
    modifier = obj.modifiers.new(name="GeoNodes_Wave", type="NODES")
    modifier.node_group = node_group
    return modifier


def add_material(obj: "bpy.types.Object") -> None:
    mat_name = "Mat_GN_Surface"
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.1, 0.4, 0.9, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.35
            bsdf.inputs["Metallic"].default_value = 0.1

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def setup_camera_and_light() -> None:
    if "GN_Light" not in bpy.data.objects:
        bpy.ops.object.light_add(type="SUN", location=(5, 5, 10))
        light = bpy.context.active_object
        light.name = "GN_Light"
        light.data.energy = 4.0

    if "GN_Camera" not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(12, -12, 10))
        cam = bpy.context.active_object
        cam.name = "GN_Camera"
        cam.rotation_euler = (math.radians(55), 0, math.radians(45))
        bpy.context.scene.camera = cam


# ============================================================
# ОСНОВНАЯ ЛОГИКА
# ============================================================

def main() -> None:
    validate_parameters()

    print(f"\n{'=' * 55}")
    print("  STEM-проект: Автонастройка Geometry Nodes")
    print("  Функция: z = A * sin(k*x) * cos(k*y)")
    print(f"  Сетка: {GRID_SUBDIVISIONS}×{GRID_SUBDIVISIONS}, размер {GRID_SIZE}")
    print(f"{'=' * 55}\n")

    if not HAS_BPY:
        print("Запустите скрипт через Blender: Scripting -> Open -> Run Script.")
        return

    remove_existing(OBJECT_NAME)
    node_group = create_wave_node_group(NODE_GROUP_NAME)
    obj = create_grid_object(OBJECT_NAME, GRID_SIZE, GRID_SUBDIVISIONS)
    apply_geometry_nodes_modifier(obj, node_group)
    add_material(obj)
    setup_camera_and_light()

    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    print("  ✓ Готово!")
    print(f"  Объект '{OBJECT_NAME}' с Geometry Nodes создан.")
    print("  Изменяйте Amplitude и Frequency в модификаторе Geometry Nodes.\n")


if __name__ == "__main__":
    main()
