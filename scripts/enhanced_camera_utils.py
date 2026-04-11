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


def aim_camera_at_bbox(
    camera: "bpy.types.Object",
    bbox_min: tuple[float, float, float],
    bbox_max: tuple[float, float, float],
    *,
    direction: tuple[float, float, float] = (1.0, -1.0, 0.7),
    distance_factor: float = 2.2,
) -> "bpy.types.Object":
    """Располагает камеру так, чтобы bbox объекта целиком попадал в кадр.

    Алгоритм:
    1. Находит центр bbox — это точка, куда камера будет смотреть.
    2. Считает радиус сферы, описанной вокруг bbox.
    3. Ставит камеру на `distance = distance_factor * radius` от центра
       в направлении `direction` (по умолчанию — диагональный 3/4-вид).
    4. Добавляет Track-To constraint на Empty в центре, чтобы камера
       всегда точно смотрела на центр независимо от её положения.

    Возвращает созданный Empty (цель трекинга) — полезно, если потом
    нужно сдвинуть фокус камеры.
    """
    cx = (bbox_min[0] + bbox_max[0]) / 2.0
    cy = (bbox_min[1] + bbox_max[1]) / 2.0
    cz = (bbox_min[2] + bbox_max[2]) / 2.0

    dx = bbox_max[0] - bbox_min[0]
    dy = bbox_max[1] - bbox_min[1]
    dz = bbox_max[2] - bbox_min[2]
    radius = max(1.0, 0.5 * math.sqrt(dx * dx + dy * dy + dz * dz))

    dnorm = math.sqrt(sum(d * d for d in direction))
    ux, uy, uz = (d / dnorm for d in direction)

    distance = distance_factor * radius
    camera.location = (
        cx + ux * distance,
        cy + uy * distance,
        cz + uz * distance,
    )

    target_name = "CameraTarget"
    if target_name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[target_name], do_unlink=True)
    bpy.ops.object.empty_add(location=(cx, cy, cz))
    target = bpy.context.active_object
    target.name = target_name

    for constraint in list(camera.constraints):
        camera.constraints.remove(constraint)
    track = camera.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    return target


def mesh_world_bbox(obj: "bpy.types.Object") -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
]:
    """Возвращает (min, max) мировой bounding box меша по его вершинам."""
    if obj.data is None or not hasattr(obj.data, "vertices"):
        raise ValueError("mesh_world_bbox: объект не является мешем")
    world_matrix = obj.matrix_world
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for v in obj.data.vertices:
        wv = world_matrix @ v.co
        xs.append(wv.x)
        ys.append(wv.y)
        zs.append(wv.z)
    return (min(xs), min(ys), min(zs)), (max(xs), max(ys), max(zs))
