"""
setup_geometry_nodes_surface.py
================================
Учебный STEM-проект: Интерактивная 3D-визуализация математических функций
Павлодарский педагогический университет

НАЗНАЧЕНИЕ:
    Скрипт автоматически создаёт базовую сцену с Geometry Nodes для
    интерактивной визуализации поверхности z = A * sin(k*x) * cos(k*y).

    В отличие от generate_surface_mesh.py, здесь поверхность строится
    не через Python-вычисление вершин, а через граф Geometry Nodes Blender.
    После запуска скрипта в сцене появится объект с модификатором
    Geometry Nodes и двумя управляемыми параметрами: Amplitude и Frequency.

КАК ЗАПУСТИТЬ:
    1. Откройте Blender 3.6+ с ПУСТОЙ сценой (или удалите куб вручную).
    2. Перейдите во вкладку "Scripting".
    3. Нажмите "Open" и выберите этот файл.
    4. Нажмите ▶ "Run Script" (или Alt+P).
    5. Объект "GN_Surface" появится в сцене.
    6. Перейдите в Layout → выберите объект → нажмите N.
       В N-panel (вкладка Item) появятся ползунки Amplitude и Frequency.

ВАЖНОЕ ЗАМЕЧАНИЕ:
    Geometry Nodes — это визуальный (node-based) редактор. Полная настройка
    красивого графа нод вручную описана в docs/03_blender_guide.md.
    Данный скрипт создаёт минимальный рабочий вариант через bpy.

ТРЕБОВАНИЯ:
    Blender 3.6+. API Geometry Nodes менялось между версиями;
    скрипт протестирован на Blender 3.6 LTS.
"""

import bpy
import math


# ============================================================
# ПАРАМЕТРЫ СЦЕНЫ
# ============================================================

# Размер сетки (единицы Blender)
GRID_SIZE: float = 10.0

# Количество делений по каждой оси (влияет на качество поверхности)
GRID_SUBDIVISIONS: int = 80

# Начальная амплитуда (можно изменить ползунком после запуска)
DEFAULT_AMPLITUDE: float = 1.0

# Начальная частота (можно изменить ползунком после запуска)
DEFAULT_FREQUENCY: float = 1.0

# Имя объекта в сцене
OBJECT_NAME: str = "GN_Surface"

# Имя группы нод Geometry Nodes
NODE_GROUP_NAME: str = "MathSurface_GN"


# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================


def remove_existing(name: str) -> None:
    """Удаляет объект с заданным именем, если он есть в сцене."""
    if name in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)


def remove_node_group(name: str) -> None:
    """Удаляет группу нод Geometry Nodes с заданным именем."""
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])


def clear_default_scene() -> None:
    """Удаляет стандартные объекты Blender (куб, источник света, камеру).
    Вызывайте только если нужна чистая сцена.
    """
    for obj_name in ["Cube", "Light", "Camera"]:
        if obj_name in bpy.data.objects:
            bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)


# ============================================================
# СОЗДАНИЕ GEOMETRY NODES ГРАФА
# ============================================================


def create_wave_node_group(name: str) -> bpy.types.GeometryNodeTree:
    """Создаёт граф Geometry Nodes для поверхности z = A * sin(k*x) * cos(k*y).

    Структура графа:
        Group Input (Amplitude, Frequency)
            ↓
        [Position → Separate XYZ → X, Y]
        [X * Frequency → Sin]
        [Y * Frequency → Cos]
        [Sin * Cos → Z_raw]
        [Z_raw * Amplitude → Z_final]
        [Combine XYZ (X, Y, Z_final)]
            ↓
        Set Position
            ↓
        Group Output

    Returns:
        Созданная группа нод (bpy.types.GeometryNodeTree)
    """
    # Удаляем старую группу нод, если есть
    remove_node_group(name)

    # Создаём новую группу нод типа GeometryNodeTree
    node_group = bpy.data.node_groups.new(name=name, type="GeometryNodeTree")
    nodes = node_group.nodes
    links = node_group.links

    # --- Интерфейс: входы группы ---
    # Blender 3.x: interface через node_group.inputs / node_group.outputs
    # Geometry (вход и выход — обязательные для Geometry Nodes)
    node_group.inputs.new("NodeSocketGeometry", "Geometry")
    node_group.inputs.new("NodeSocketFloat", "Amplitude")
    node_group.inputs["Amplitude"].default_value = DEFAULT_AMPLITUDE
    node_group.inputs["Amplitude"].min_value = 0.0
    node_group.inputs["Amplitude"].max_value = 10.0

    node_group.inputs.new("NodeSocketFloat", "Frequency")
    node_group.inputs["Frequency"].default_value = DEFAULT_FREQUENCY
    node_group.inputs["Frequency"].min_value = 0.0
    node_group.inputs["Frequency"].max_value = 10.0

    node_group.outputs.new("NodeSocketGeometry", "Geometry")

    # --- Ноды ---

    # Group Input
    n_input = nodes.new("NodeGroupInput")
    n_input.location = (-800, 0)

    # Group Output
    n_output = nodes.new("NodeGroupOutput")
    n_output.location = (600, 0)

    # Position — текущие координаты каждой вершины
    n_position = nodes.new("GeometryNodeInputPosition")
    n_position.location = (-800, -200)

    # Separate XYZ — разделяем координаты на X, Y, Z
    n_sep = nodes.new("ShaderNodeSeparateXYZ")
    n_sep.location = (-600, -200)

    # Math: X * Frequency (для sin)
    n_mul_x = nodes.new("ShaderNodeMath")
    n_mul_x.operation = "MULTIPLY"
    n_mul_x.location = (-400, -100)

    # Math: Sin(k * x)
    n_sin = nodes.new("ShaderNodeMath")
    n_sin.operation = "SINE"
    n_sin.location = (-200, -100)

    # Math: Y * Frequency (для cos)
    n_mul_y = nodes.new("ShaderNodeMath")
    n_mul_y.operation = "MULTIPLY"
    n_mul_y.location = (-400, -300)

    # Math: Cos(k * y)
    n_cos = nodes.new("ShaderNodeMath")
    n_cos.operation = "COSINE"
    n_cos.location = (-200, -300)

    # Math: Sin * Cos
    n_mul_sincos = nodes.new("ShaderNodeMath")
    n_mul_sincos.operation = "MULTIPLY"
    n_mul_sincos.location = (0, -200)

    # Math: (Sin * Cos) * Amplitude
    n_mul_amp = nodes.new("ShaderNodeMath")
    n_mul_amp.operation = "MULTIPLY"
    n_mul_amp.location = (200, -200)

    # Combine XYZ — собираем новый вектор позиции (X, Y, Z_new)
    n_combine = nodes.new("ShaderNodeCombineXYZ")
    n_combine.location = (200, 100)

    # Set Position — применяем новые координаты к геометрии
    n_setpos = nodes.new("GeometryNodeSetPosition")
    n_setpos.location = (400, 0)

    # --- Соединения ---

    # Geometry: Group Input → Set Position → Group Output
    links.new(n_input.outputs["Geometry"], n_setpos.inputs["Geometry"])
    links.new(n_setpos.outputs["Geometry"], n_output.inputs["Geometry"])

    # Position → Separate XYZ
    links.new(n_position.outputs["Position"], n_sep.inputs["Vector"])

    # X * Frequency
    links.new(n_sep.outputs["X"], n_mul_x.inputs[0])
    links.new(n_input.outputs["Frequency"], n_mul_x.inputs[1])

    # Sin(k*x)
    links.new(n_mul_x.outputs["Value"], n_sin.inputs["Value"])

    # Y * Frequency
    links.new(n_sep.outputs["Y"], n_mul_y.inputs[0])
    links.new(n_input.outputs["Frequency"], n_mul_y.inputs[1])

    # Cos(k*y)
    links.new(n_mul_y.outputs["Value"], n_cos.inputs["Value"])

    # Sin * Cos
    links.new(n_sin.outputs["Value"], n_mul_sincos.inputs[0])
    links.new(n_cos.outputs["Value"], n_mul_sincos.inputs[1])

    # (Sin*Cos) * Amplitude = Z
    links.new(n_mul_sincos.outputs["Value"], n_mul_amp.inputs[0])
    links.new(n_input.outputs["Amplitude"], n_mul_amp.inputs[1])

    # Combine XYZ: X=X, Y=Y, Z=Z_new
    links.new(n_sep.outputs["X"], n_combine.inputs["X"])
    links.new(n_sep.outputs["Y"], n_combine.inputs["Y"])
    links.new(n_mul_amp.outputs["Value"], n_combine.inputs["Z"])

    # Set Position: Position = Combine XYZ result
    links.new(n_combine.outputs["Vector"], n_setpos.inputs["Position"])

    return node_group


# ============================================================
# СОЗДАНИЕ ОБЪЕКТА И ПРИМЕНЕНИЕ МОДИФИКАТОРА
# ============================================================


def create_grid_object(name: str, size: float, subdivisions: int) -> bpy.types.Object:
    """Создаёт плоскость-сетку (Grid) через bpy.ops.

    Args:
        name: имя объекта
        size: размер сетки
        subdivisions: количество делений

    Returns:
        Созданный объект Blender
    """
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
    obj: bpy.types.Object,
    node_group: bpy.types.GeometryNodeTree,
) -> bpy.types.Modifier:
    """Добавляет модификатор Geometry Nodes к объекту и подключает граф нод.

    Args:
        obj: объект Blender
        node_group: группа нод Geometry Nodes

    Returns:
        Созданный модификатор
    """
    modifier = obj.modifiers.new(name="GeoNodes_Wave", type="NODES")
    modifier.node_group = node_group
    return modifier


def add_material(obj: bpy.types.Object) -> None:
    """Добавляет базовый синий материал к объекту."""
    mat_name = "Mat_GN_Surface"
    if mat_name not in bpy.data.materials:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.1, 0.4, 0.9, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.35
            bsdf.inputs["Metallic"].default_value = 0.1
    else:
        mat = bpy.data.materials[mat_name]

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def setup_camera_and_light() -> None:
    """Добавляет камеру и источник света, если их нет в сцене."""
    # Источник света
    if "GN_Light" not in bpy.data.objects:
        bpy.ops.object.light_add(type="SUN", location=(5, 5, 10))
        light = bpy.context.active_object
        light.name = "GN_Light"
        light.data.energy = 4.0

    # Камера
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
    print(f"\n{'='*55}")
    print(f"  STEM-проект: Автонастройка Geometry Nodes")
    print(f"  Функция: z = A * sin(k*x) * cos(k*y)")
    print(f"  Сетка: {GRID_SUBDIVISIONS}×{GRID_SUBDIVISIONS}, размер {GRID_SIZE}")
    print(f"{'='*55}\n")

    # Удаляем предыдущий объект (если был)
    remove_existing(OBJECT_NAME)

    # Шаг 1: Создаём граф Geometry Nodes
    print("  [1/4] Создание графа Geometry Nodes...")
    node_group = create_wave_node_group(NODE_GROUP_NAME)
    print(f"        Группа нод '{NODE_GROUP_NAME}' создана.")

    # Шаг 2: Создаём сетку (Grid)
    print(f"  [2/4] Создание сетки ({GRID_SUBDIVISIONS}×{GRID_SUBDIVISIONS})...")
    obj = create_grid_object(OBJECT_NAME, GRID_SIZE, GRID_SUBDIVISIONS)
    print(f"        Объект '{OBJECT_NAME}' создан.")

    # Шаг 3: Применяем модификатор Geometry Nodes
    print("  [3/4] Применение модификатора Geometry Nodes...")
    apply_geometry_nodes_modifier(obj, node_group)
    print("        Модификатор применён.")

    # Шаг 4: Добавляем материал и свет
    print("  [4/4] Материал, освещение, камера...")
    add_material(obj)
    setup_camera_and_light()

    # Делаем объект активным
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    print("\n  ✓ Готово!")
    print(f"  Объект '{OBJECT_NAME}' с Geometry Nodes создан.")
    print()
    print("  Как изменить параметры:")
    print("  1. Нажмите N в 3D-вьюпорте → вкладка Item")
    print("  2. Найдите ползунки Amplitude и Frequency")
    print("  3. Двигайте ползунок — поверхность обновляется!")
    print()
    print("  Или перейдите в редактор Geometry Nodes")
    print("  (Shift+F3 или вкладка Geometry Nodes)")
    print("  для визуального редактирования графа нод.\n")


main()
