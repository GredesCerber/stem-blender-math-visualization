"""
enhanced_camera_utils.py
========================
Утилиты для улучшенной позиции камеры (3D вид, не сверху).

Используется в других скриптах для лучшего 3D-эффекта.
"""

from __future__ import annotations

import math

try:
    import bpy
except ImportError:
    pass


def setup_angled_camera(
    location: tuple[float, float, float] | None = None,
    rotation_euler: tuple[float, float, float] | None = None,
) -> "bpy.types.Object":
    """
    Создаёт камеру с хорошим 3D углом обзора (не сверху-вниз).
    
    Args:
        location: (x, y, z) позиция камеры. По умолчанию (12, -11, 8)
        rotation_euler: (rx, ry, rz) углы поворота в радианах. По умолчанию (60°, 0, 45°)
    
    Returns:
        camera object
    
    Примеры:
        >>> camera = setup_angled_camera()  # дефолтные значения
        >>> camera = setup_angled_camera(
        ...     location=(15, -15, 10),
        ...     rotation_euler=(math.radians(55), 0, math.radians(45))
        ... )
    """
    if location is None:
        location = (12, -11, 8)
    if rotation_euler is None:
        rotation_euler = (math.radians(60), 0, math.radians(45))
    
    if "Camera" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Camera"], do_unlink=True)
    
    bpy.ops.object.camera_add(location=location)
    camera = bpy.context.active_object
    camera.name = "Camera"
    camera.rotation_euler = rotation_euler
    bpy.context.scene.camera = camera
    
    return camera


def setup_dramatic_light(
    location: tuple[float, float, float] | None = None,
    energy: float = 4.5,
) -> "bpy.types.Object":
    """
    Создаёт солнечный свет для драматичного освещения.
    
    Args:
        location: (x, y, z) позиция света. По умолчанию (10, 10, 13)
        energy: мощность света. По умолчанию 4.5
    
    Returns:
        light object
    """
    if location is None:
        location = (10, 10, 13)
    
    if "Sun" in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects["Sun"], do_unlink=True)
    
    bpy.ops.object.light_add(type="SUN", location=location)
    light = bpy.context.active_object
    light.name = "Sun"
    light.data.energy = energy
    
    return light


# Предустановки для разных функций
CAMERA_PRESETS: dict[str, dict] = {
    "default": {
        "location": (12, -11, 8),
        "rotation": (math.radians(60), 0, math.radians(45)),
        "light_energy": 4.0,
    },
    "paraboloid": {
        "location": (12, -10, 8),
        "rotation": (math.radians(65), 0, math.radians(45)),
        "light_energy": 4.0,
    },
    "saddle": {
        "location": (11, -11, 7),
        "rotation": (math.radians(70), 0, math.radians(45)),
        "light_energy": 4.5,
    },
    "wave": {
        "location": (13, -11, 8),
        "rotation": (math.radians(60), 0, math.radians(40)),
        "light_energy": 4.0,
    },
    "ripple": {
        "location": (12, -12, 9),
        "rotation": (math.radians(55), 0, math.radians(45)),
        "light_energy": 4.5,
    },
    "gaussian": {
        "location": (12, -10, 10),
        "rotation": (math.radians(55), 0, math.radians(45)),
        "light_energy": 4.0,
    },
}


def setup_camera_for_function(function_name: str) -> tuple["bpy.types.Object", "bpy.types.Object"]:
    """
    Настраивает камеру и свет оптимально для конкретной функции.
    
    Args:
        function_name: имя функции ('wave', 'paraboloid', etc.)
    
    Returns:
        (camera, light) objects
    """
    preset = CAMERA_PRESETS.get(function_name, CAMERA_PRESETS["default"])
    
    camera = setup_angled_camera(
        location=preset["location"],
        rotation_euler=preset["rotation"],
    )
    light = setup_dramatic_light(energy=preset["light_energy"])
    
    return camera, light
