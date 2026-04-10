"""
create_visualizer_blend.py
==========================
Создаёт FunctionVisualizer.blend — финальную учебную сцену для демонстраций.

Запуск:
  blender --background --python scripts/create_visualizer_blend.py

Содержимое сцены:
  - MathSurface_Python: поверхность wave A=1 k=1, цветовая карта RGB
  - MathSurface_GN: Geometry Nodes поверхность (параметры Amplitude/Frequency)
  - Camera (позиция для демонстрации)
  - SunLight
  - Коллекции: Python_Surface, GN_Surface, Lesson_Setup
  - Пресеты в кастомных свойствах объекта GN
"""

from __future__ import annotations

import math
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

try:
    import bpy
except ImportError:
    print("[ERROR] Этот скрипт должен запускаться через Blender!")
    sys.exit(1)

from function_library import (  # noqa: E402
    SurfaceConfig,
    generate_surface_geometry,
    validate_surface_config,
)


# ──────────────────────────────────────────────
# Параметры сцены
# ──────────────────────────────────────────────

OUTPUT_BLEND = os.path.join(
    os.path.dirname(SCRIPT_DIR), "FunctionVisualizer.blend"
)

# Конфигурация Python-поверхности (wave, демонстрационная)
PYTHON_SURFACE_CONFIG = SurfaceConfig(
    function="wave",
    resolution=80,
    x_min=-5.0,
    x_max=5.0,
    y_min=-5.0,
    y_max=5.0,
    amplitude=1.0,
    frequency=1.0,
)

# Конфигурация GN-поверхности (parametric grid)
GN_GRID_SUBDIVISIONS = 80
GN_DOMAIN_HALF = 5.0


# ──────────────────────────────────────────────
# Очистка сцены
# ──────────────────────────────────────────────

def clear_scene() -> None:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for ng in list(bpy.data.node_groups):
        bpy.data.node_groups.remove(ng)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)
    print("[OK] Сцена очищена.")


# ──────────────────────────────────────────────
# Коллекции
# ──────────────────────────────────────────────

def get_or_create_collection(name: str, parent=None) -> "bpy.types.Collection":
    if name in bpy.data.collections:
        return bpy.data.collections[name]
    col = bpy.data.collections.new(name)
    target = parent if parent else bpy.context.scene.collection
    target.children.link(col)
    return col


# ──────────────────────────────────────────────
# Python-поверхность
# ──────────────────────────────────────────────

def build_python_surface(
    config: SurfaceConfig,
    collection: "bpy.types.Collection",
) -> "bpy.types.Object":
    validate_surface_config(config)
    vertices, faces = generate_surface_geometry(config)

    mesh = bpy.data.meshes.new("MathSurface_Python_Mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    obj = bpy.data.objects.new("MathSurface_Python", mesh)
    collection.objects.link(obj)

    # Цветовой материал по высоте Z
    z_values = [v[2] for v in vertices]
    z_min, z_max = min(z_values), max(z_values)
    if z_max <= z_min:
        z_min, z_max = z_min - 1.0, z_max + 1.0

    mat = bpy.data.materials.new("Mat_Python_Surface")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)

    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    bsdf.inputs["Roughness"].default_value = 0.35
    bsdf.inputs["Metallic"].default_value = 0.05
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
    color_ramp.location = (100, 100)
    color_ramp.color_ramp.elements[0].color = (0.05, 0.2, 0.85, 1.0)   # синий (низ)
    color_ramp.color_ramp.elements[1].color = (0.9, 0.1, 0.1, 1.0)     # красный (верх)
    mid = color_ramp.color_ramp.elements.new(0.5)
    mid.color = (0.1, 0.8, 0.2, 1.0)                                    # зелёный (середина)
    links.new(map_range.outputs["Result"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])

    obj.data.materials.append(mat)

    # Кастомные свойства — описание пресетов
    obj["stem_function"] = config.function
    obj["stem_amplitude"] = config.amplitude
    obj["stem_frequency"] = config.frequency
    obj["stem_resolution"] = config.resolution
    obj["stem_description"] = "wave: z = A * sin(k*x) * cos(k*y)"
    obj["stem_preset_default"] = "A=1, k=1, res=80"
    obj["stem_preset_gentle"] = "A=0.5, k=0.7, res=70"
    obj["stem_preset_dynamic"] = "A=2.0, k=2.5, res=100"

    print(f"[OK] MathSurface_Python создан: {len(vertices)} вершин, {len(faces)} граней.")
    return obj


# ──────────────────────────────────────────────
# Geometry Nodes поверхность
# ──────────────────────────────────────────────

def _add_group_socket(node_group, *, name, socket_type, in_out):
    interface = getattr(node_group, "interface", None)
    if interface is not None and hasattr(interface, "new_socket"):
        return interface.new_socket(name=name, in_out=in_out, socket_type=socket_type)
    if in_out == "INPUT":
        return node_group.inputs.new(socket_type, name)
    return node_group.outputs.new(socket_type, name)


def build_gn_surface(
    collection: "bpy.types.Collection",
    amplitude: float = 1.0,
    frequency: float = 1.0,
    subdivisions: int = GN_GRID_SUBDIVISIONS,
    domain_half: float = GN_DOMAIN_HALF,
) -> "bpy.types.Object":
    # Grid объект
    bpy.ops.mesh.primitive_grid_add(
        x_subdivisions=subdivisions,
        y_subdivisions=subdivisions,
        size=domain_half * 2,
        location=(0, 0, 0),
    )
    obj = bpy.context.active_object
    # Убираем из Scene Collection и добавляем в нужную коллекцию
    bpy.context.scene.collection.objects.unlink(obj)
    collection.objects.link(obj)
    obj.name = "MathSurface_GN"

    # Node Group
    ng = bpy.data.node_groups.new("MathSurface_GN_Group", type="GeometryNodeTree")
    nodes = ng.nodes
    links = ng.links

    _add_group_socket(ng, name="Geometry", socket_type="NodeSocketGeometry", in_out="INPUT")
    amp_sock = _add_group_socket(ng, name="Amplitude", socket_type="NodeSocketFloat", in_out="INPUT")
    freq_sock = _add_group_socket(ng, name="Frequency", socket_type="NodeSocketFloat", in_out="INPUT")
    _add_group_socket(ng, name="Geometry", socket_type="NodeSocketGeometry", in_out="OUTPUT")

    for sock, default, mn, mx in [
        (amp_sock, amplitude, 0.0, 20.0),
        (freq_sock, frequency, 0.0, 20.0),
    ]:
        if hasattr(sock, "default_value"):
            sock.default_value = default
        if hasattr(sock, "min_value"):
            sock.min_value = mn
        if hasattr(sock, "max_value"):
            sock.max_value = mx

    n_in = nodes.new("NodeGroupInput")
    n_in.location = (-1200, 80)

    n_out = nodes.new("NodeGroupOutput")
    n_out.location = (900, 80)

    n_setpos = nodes.new("GeometryNodeSetPosition")
    n_setpos.location = (680, 80)

    n_pos = nodes.new("GeometryNodeInputPosition")
    n_pos.location = (-1200, -320)

    n_sep = nodes.new("ShaderNodeSeparateXYZ")
    n_sep.location = (-1000, -320)

    n_mul_x = nodes.new("ShaderNodeMath")
    n_mul_x.operation = "MULTIPLY"
    n_mul_x.location = (-700, -200)

    n_mul_y = nodes.new("ShaderNodeMath")
    n_mul_y.operation = "MULTIPLY"
    n_mul_y.location = (-700, -420)

    n_sin = nodes.new("ShaderNodeMath")
    n_sin.operation = "SINE"
    n_sin.location = (-450, -200)

    n_cos = nodes.new("ShaderNodeMath")
    n_cos.operation = "COSINE"
    n_cos.location = (-450, -420)

    n_mul_wave = nodes.new("ShaderNodeMath")
    n_mul_wave.operation = "MULTIPLY"
    n_mul_wave.location = (-220, -300)

    n_mul_amp = nodes.new("ShaderNodeMath")
    n_mul_amp.operation = "MULTIPLY"
    n_mul_amp.location = (20, -300)

    n_combine = nodes.new("ShaderNodeCombineXYZ")
    n_combine.location = (250, -80)

    links.new(n_in.outputs["Geometry"], n_setpos.inputs["Geometry"])
    links.new(n_setpos.outputs["Geometry"], n_out.inputs["Geometry"])
    links.new(n_pos.outputs["Position"], n_sep.inputs["Vector"])
    links.new(n_sep.outputs["X"], n_mul_x.inputs[0])
    links.new(n_in.outputs["Frequency"], n_mul_x.inputs[1])
    links.new(n_mul_x.outputs["Value"], n_sin.inputs["Value"])
    links.new(n_sep.outputs["Y"], n_mul_y.inputs[0])
    links.new(n_in.outputs["Frequency"], n_mul_y.inputs[1])
    links.new(n_mul_y.outputs["Value"], n_cos.inputs["Value"])
    links.new(n_sin.outputs["Value"], n_mul_wave.inputs[0])
    links.new(n_cos.outputs["Value"], n_mul_wave.inputs[1])
    links.new(n_mul_wave.outputs["Value"], n_mul_amp.inputs[0])
    links.new(n_in.outputs["Amplitude"], n_mul_amp.inputs[1])
    links.new(n_sep.outputs["X"], n_combine.inputs["X"])
    links.new(n_sep.outputs["Y"], n_combine.inputs["Y"])
    links.new(n_mul_amp.outputs["Value"], n_combine.inputs["Z"])
    links.new(n_combine.outputs["Vector"], n_setpos.inputs["Position"])

    mod = obj.modifiers.new("GeoNodes_Surface", "NODES")
    mod.node_group = ng

    # Материал GN
    mat = bpy.data.materials.new("Mat_GN_Surface")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.1, 0.4, 0.9, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.3
        bsdf.inputs["Metallic"].default_value = 0.1
    obj.data.materials.append(mat)

    # Пресеты в кастомных свойствах
    obj["gn_preset_lesson_default"] = "Amplitude=1.0, Frequency=1.0, res=80"
    obj["gn_preset_gentle_wave"] = "Amplitude=0.5, Frequency=0.7, res=70"
    obj["gn_preset_dynamic_wave"] = "Amplitude=2.0, Frequency=2.5, res=100"
    obj["gn_hint"] = (
        "Интерактивно: Properties > Object Data > Geometry Nodes modifier > "
        "менять Amplitude и Frequency в реальном времени"
    )

    # Смещаем GN-поверхность в сторону для сравнения
    obj.location.x = 12.0

    print(f"[OK] MathSurface_GN создан с Geometry Nodes (A={amplitude}, k={frequency}).")
    return obj


# ──────────────────────────────────────────────
# Камера и свет
# ──────────────────────────────────────────────

def setup_camera_and_light(collection: "bpy.types.Collection") -> None:
    # Sun light
    light_data = bpy.data.lights.new("SunLight_data", type="SUN")
    light_data.energy = 4.0
    light_obj = bpy.data.objects.new("SunLight", light_data)
    light_obj.location = (6.0, 6.0, 12.0)
    collection.objects.link(light_obj)

    # Camera
    cam_data = bpy.data.cameras.new("Camera_data")
    cam_data.lens = 35.0
    cam_obj = bpy.data.objects.new("LessonCamera", cam_data)
    cam_obj.location = (14.0, -16.0, 12.0)
    cam_obj.rotation_euler = (
        math.radians(55),
        math.radians(0),
        math.radians(45),
    )
    collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    print("[OK] Камера и свет настроены.")


# ──────────────────────────────────────────────
# Настройки рендера
# ──────────────────────────────────────────────

def setup_render_settings() -> None:
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.image_settings.file_format = "PNG"
    scene.render.filepath = "//render_output.png"
    # Фон — тёмный градиент (учебный стиль)
    world = bpy.data.worlds.get("World")
    if world is None:
        world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs["Color"].default_value = (0.05, 0.05, 0.1, 1.0)
        bg_node.inputs["Strength"].default_value = 0.3
    scene.world = world
    print("[OK] Настройки рендера: CYCLES, 1920×1080, 64 samples.")


# ──────────────────────────────────────────────
# Метаданные сцены
# ──────────────────────────────────────────────

def add_scene_metadata() -> None:
    scene = bpy.context.scene
    scene["stem_project"] = "STEM Blender Math Visualization"
    scene["stem_version"] = "1.0"
    scene["stem_description"] = (
        "Учебная сцена: 3D-визуализация z=f(x,y). "
        "Левая сетка — Python-поверхность wave. "
        "Правая сетка — Geometry Nodes (интерактивно). "
        "Пресеты: lesson_default / gentle_wave / dynamic_wave."
    )
    scene["stem_usage"] = (
        "1. Выберите MathSurface_GN → Properties > Modifiers > GeoNodes_Surface. "
        "2. Меняйте Amplitude и Frequency. "
        "3. Для рендера: Render > Render Image (F12)."
    )
    print("[OK] Метаданные сцены добавлены.")


# ──────────────────────────────────────────────
# Главная функция
# ──────────────────────────────────────────────

def main() -> None:
    print("[START] Создание FunctionVisualizer.blend")

    clear_scene()

    # Коллекции
    col_python = get_or_create_collection("Python_Surface")
    col_gn = get_or_create_collection("GN_Surface")
    col_setup = get_or_create_collection("Lesson_Setup")

    # Объекты
    build_python_surface(PYTHON_SURFACE_CONFIG, col_python)
    build_gn_surface(col_gn, amplitude=1.0, frequency=1.0)
    setup_camera_and_light(col_setup)
    setup_render_settings()
    add_scene_metadata()

    # Сохранение
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    print(f"[DONE] FunctionVisualizer.blend сохранён: {OUTPUT_BLEND}")


if __name__ == "__main__":
    main()
