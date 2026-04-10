"""
create_individual_blend_files.py
=================================
Создаёт отдельные .blend файлы для каждой математической функции.

Каждый файл содержит:
- Поверхность с цветовой картой (вид сбоку для 3D эффекта)
- Оптимальную позицию камеры (не сверху, а сбоку с углом)
- Освещение
- Материал с цветом по высоте

Выход: 5 файлов в проекте:
  - FunctionVisualizer_Paraboloid.blend
  - FunctionVisualizer_Saddle.blend
  - FunctionVisualizer_Wave.blend
  - FunctionVisualizer_Ripple.blend
  - FunctionVisualizer_Gaussian.blend

Запуск:
  blender --background --python scripts/create_individual_blend_files.py
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

PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Функции с параметрами для демонстрации
FUNCTION_CONFIGS: dict[str, dict] = {
    "paraboloid": {
        "function": "paraboloid",
        "resolution": 80,
        "amplitude": 1.5,
        "frequency": 1.0,
        "camera_location": (12, -10, 8),
        "camera_rotation": (math.radians(65), 0, math.radians(45)),
        "light_location": (10, 8, 12),
        "light_energy": 4.0,
    },
    "saddle": {
        "function": "saddle",
        "resolution": 80,
        "amplitude": 1.5,
        "frequency": 1.0,
        "camera_location": (11, -11, 7),
        "camera_rotation": (math.radians(70), 0, math.radians(45)),
        "light_location": (8, 8, 11),
        "light_energy": 4.5,
    },
    "wave": {
        "function": "wave",
        "resolution": 100,
        "amplitude": 2.0,
        "frequency": 2.0,
        "camera_location": (13, -11, 8),
        "camera_rotation": (math.radians(60), 0, math.radians(40)),
        "light_location": (10, 10, 12),
        "light_energy": 4.0,
    },
    "ripple": {
        "function": "ripple",
        "resolution": 100,
        "amplitude": 1.5,
        "frequency": 2.0,
        "camera_location": (12, -12, 9),
        "camera_rotation": (math.radians(55), 0, math.radians(45)),
        "light_location": (9, 9, 13),
        "light_energy": 4.5,
    },
    "gaussian": {
        "function": "gaussian",
        "resolution": 90,
        "amplitude": 2.5,
        "sigma": 2.0,
        "frequency": 1.0,
        "camera_location": (12, -10, 10),
        "camera_rotation": (math.radians(55), 0, math.radians(45)),
        "light_location": (10, 8, 13),
        "light_energy": 4.0,
    },
}


def clear_scene() -> None:
    """Удалить все объекты и материалы из сцены."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat)
    for cam in list(bpy.data.cameras):
        bpy.data.cameras.remove(cam)
    for light in list(bpy.data.lights):
        bpy.data.lights.remove(light)


def create_surface_object(
    name: str,
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int, int]],
) -> "bpy.types.Object":
    """Создаёт объект поверхности в Blender."""
    mesh = bpy.data.meshes.new(name=f"{name}_mesh")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def add_color_material_to_surface(
    obj: "bpy.types.Object",
    *,
    z_min: float,
    z_max: float,
    function_name: str,
) -> None:
    """Добавляет цветовой материал (синий-зелёный-красный) по высоте."""
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


def create_scene(
    function_name: str,
    config_dict: dict,
) -> None:
    """Создаёт сцену для одной функции и сохраняет в .blend."""
    clear_scene()

    # Создаём конфиг поверхности
    config = SurfaceConfig(
        function=config_dict["function"],
        resolution=config_dict["resolution"],
        x_min=-5.0,
        x_max=5.0,
        y_min=-5.0,
        y_max=5.0,
        amplitude=config_dict.get("amplitude", 1.0),
        frequency=config_dict.get("frequency", 1.0),
        sigma=config_dict.get("sigma", 2.0),
    )
    validate_surface_config(config)

    # Генерируем геометрию
    vertices, faces = generate_surface_geometry(config)
    obj = create_surface_object(f"MathSurface_{function_name}", vertices, faces)
    
    # Добавляем материал
    z_values = [v[2] for v in vertices]
    add_color_material_to_surface(
        obj,
        z_min=min(z_values),
        z_max=max(z_values),
        function_name=function_name,
    )

    # Настраиваем камеру (3D вид!)
    bpy.ops.object.camera_add(location=config_dict["camera_location"])
    camera = bpy.context.active_object
    camera.name = f"Camera_{function_name}"
    camera.rotation_euler = config_dict["camera_rotation"]
    bpy.context.scene.camera = camera

    # Добавляем свет
    bpy.ops.object.light_add(type="SUN", location=config_dict["light_location"])
    light = bpy.context.active_object
    light.name = f"Sun_{function_name}"
    light.data.energy = config_dict["light_energy"]

    # Сохраняем .blend файл
    output_filename = f"FunctionVisualizer_{function_name.capitalize()}.blend"
    output_path = os.path.join(PROJECT_ROOT, output_filename)
    bpy.ops.wm.save_as_mainfile(filepath=output_path)
    print(f"[OK] Сохранён: {output_path}")


def main() -> None:
    for func_name, config_dict in FUNCTION_CONFIGS.items():
        print(f"[START] Создание: {func_name.upper()}")
        try:
            create_scene(func_name, config_dict)
        except Exception as exc:
            print(f"[ERROR] {func_name}: {exc}")
    
    print("\n[DONE] Все файлы созданы!")
    print("  - FunctionVisualizer_Paraboloid.blend")
    print("  - FunctionVisualizer_Saddle.blend")
    print("  - FunctionVisualizer_Wave.blend")
    print("  - FunctionVisualizer_Ripple.blend")
    print("  - FunctionVisualizer_Gaussian.blend")
    print("\nКаждый файл содержит оптимальную камеру для 3D вида (сбоку, под углом).")


if __name__ == "__main__":
    main()
