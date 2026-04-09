"""
visualize_function.py
=====================
STEM-проект: Интерактивная 3D-визуализация математических функций в Blender
Репозиторий: https://github.com/GredesCerber/stem-blender-math-visualization

Использование:
    1. В Blender: Scripting → Open → выбрать этот файл → Run Script (▶)
    2. Из командной строки:
       blender --background --python scripts/visualize_function.py

Что делает скрипт:
    - Создаёт сетку N×N вершин в области [-L, L] × [-L, L]
    - Для каждой вершины (x, y) вычисляет z = f(x, y)
    - Создаёт 3D-объект «MathSurface» в сцене Blender
    - Применяет материал с цветовой картой по высоте z
"""

import math

try:
    import bpy
    import bmesh
    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("[INFO] bpy не найден — запуск вне Blender (только проверка формулы)")


# ============================================================
# === ФОРМУЛА — ЕДИНСТВЕННОЕ МЕСТО, КОТОРОЕ НУЖНО МЕНЯТЬ ===
# ============================================================

def surface_function(x: float, y: float) -> float:
    """
    Функция z = f(x, y).
    Измените тело этой функции, чтобы изменить форму поверхности.

    ВАЖНО: в один момент должен быть активен только один оператор return.
    Раскомментируйте один из вариантов ниже (и закомментируйте остальные),
    или напишите собственную формулу.
    """
    # ----------------------------------------------------------
    # Параболоид (чаша): z = x² + y²
    return x**2 + y**2

    # ----------------------------------------------------------
    # Волновая поверхность: z = A·sin(k·x)·cos(k·y)
    # A = 1.0  # амплитуда
    # k = 1.0  # частота
    # return A * math.sin(k * x) * math.cos(k * y)

    # ----------------------------------------------------------
    # Седло (гиперболический параболоид): z = x² - y²
    # return x**2 - y**2

    # ----------------------------------------------------------
    # Круговые волны: z = sin(√(x²+y²))
    # r = math.sqrt(x**2 + y**2)
    # return math.sin(r) if r > 1e-6 else 1.0

    # ----------------------------------------------------------
    # Гауссов колокол: z = e^(-(x²+y²))
    # alpha = 1.0  # параметр ширины
    # return math.exp(-alpha * (x**2 + y**2))

    # ----------------------------------------------------------
    # Затухающая волна: z = A·sin(k·x)·e^(-α·y²)
    # A, k, alpha = 1.0, 2.0, 0.3
    # return A * math.sin(k * x) * math.exp(-alpha * y**2)

    # ----------------------------------------------------------
    # Ваша формула:
    # return ...


# ============================================================
# === ПАРАМЕТРЫ СЕТКИ ===
# ============================================================

GRID_SUBDIVISIONS = 100   # Число делений по каждой оси (качество сетки)
                           # 50 — быстро, 100 — норм, 200 — детально
GRID_HALF_SIZE = 5.0       # Половина размера области: от -L до +L по x и y
OBJECT_NAME = "MathSurface"  # Имя объекта в сцене Blender


# ============================================================
# === ВНУТРЕННЯЯ ЛОГИКА — ОБЫЧНО МЕНЯТЬ НЕ НУЖНО ===
# ============================================================

def generate_vertices_and_faces(
    func,
    n: int,
    half_size: float,
) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int, int]]]:
    """
    Генерирует список вершин и граней для 3D-поверхности.

    Args:
        func: функция z = f(x, y)
        n: число делений по каждой оси
        half_size: половина размера области (область: [-half_size, half_size]²)

    Returns:
        vertices: список кортежей (x, y, z)
        faces: список четырёхугольных граней (индексы вершин)
    """
    vertices = []
    step = (2.0 * half_size) / n

    # Генерируем вершины: (n+1) × (n+1) точек
    for j in range(n + 1):
        for i in range(n + 1):
            x = -half_size + i * step
            y = -half_size + j * step
            try:
                z = func(x, y)
            except (ValueError, ZeroDivisionError):
                z = 0.0
            vertices.append((x, y, z))

    # Генерируем четырёхугольные грани
    faces = []
    row_len = n + 1
    for j in range(n):
        for i in range(n):
            v0 = j * row_len + i          # нижний левый
            v1 = j * row_len + (i + 1)    # нижний правый
            v2 = (j + 1) * row_len + (i + 1)  # верхний правый
            v3 = (j + 1) * row_len + i    # верхний левый
            faces.append((v0, v1, v2, v3))

    return vertices, faces


def create_surface_object(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int, int]],
    name: str,
) -> None:
    """
    Создаёт объект Blender с заданными вершинами и гранями.
    Если объект с таким именем уже существует — удаляет его перед созданием.
    """
    # Удалить старый объект с тем же именем (если есть)
    if name in bpy.data.objects:
        old_obj = bpy.data.objects[name]
        bpy.data.objects.remove(old_obj, do_unlink=True)

    if name in bpy.data.meshes:
        bpy.data.meshes.remove(bpy.data.meshes[name])

    # Создать новый меш
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()

    # Создать объект и добавить его в сцену
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)

    # Сделать объект активным
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

    print(f"[OK] Объект '{name}' создан: {len(vertices)} вершин, {len(faces)} граней")


def add_color_material(obj_name: str) -> None:
    """
    Добавляет материал с псевдоцветовой картой по высоте z.
    Синий = низкие значения, красный = высокие значения.
    Используется атрибут вершины 'position' (z-компонента).
    """
    if obj_name not in bpy.data.objects:
        return

    obj = bpy.data.objects[obj_name]

    # Удалить старые материалы
    obj.data.materials.clear()

    # Создать новый материал
    mat = bpy.data.materials.new(name=f"{obj_name}_Material")
    mat.use_nodes = True
    obj.data.materials.append(mat)

    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Узел вывода
    output = nodes.new("ShaderNodeOutputMaterial")
    output.location = (600, 0)

    # Принципиальный BSDF-шейдер
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    links.new(bsdf.outputs["BSDF"], output.inputs["Surface"])

    # Geometry node — получить координаты вершины
    geom = nodes.new("ShaderNodeNewGeometry")
    geom.location = (-400, 0)

    # Separate XYZ — нам нужна z-компонента
    sep = nodes.new("ShaderNodeSeparateXYZ")
    sep.location = (-200, 0)
    links.new(geom.outputs["Position"], sep.inputs["Vector"])

    # Map Range — нормализовать z в [0, 1]
    map_range = nodes.new("ShaderNodeMapRange")
    map_range.location = (0, 0)
    map_range.inputs["From Min"].default_value = -GRID_HALF_SIZE
    map_range.inputs["From Max"].default_value = GRID_HALF_SIZE
    map_range.inputs["To Min"].default_value = 0.0
    map_range.inputs["To Max"].default_value = 1.0
    links.new(sep.outputs["Z"], map_range.inputs["Value"])

    # Color Ramp — синий → зелёный → красный
    color_ramp = nodes.new("ShaderNodeValToRGB")
    color_ramp.location = (150, 100)
    color_ramp.color_ramp.elements[0].color = (0.0, 0.1, 0.8, 1.0)   # синий
    color_ramp.color_ramp.elements[1].color = (0.8, 0.0, 0.0, 1.0)   # красный
    # Добавляем зелёную остановку посередине
    mid_elem = color_ramp.color_ramp.elements.new(0.5)
    mid_elem.color = (0.0, 0.8, 0.1, 1.0)   # зелёный
    links.new(map_range.outputs["Result"], color_ramp.inputs["Fac"])
    links.new(color_ramp.outputs["Color"], bsdf.inputs["Base Color"])

    print(f"[OK] Материал с цветовой картой применён к '{obj_name}'")


def ensure_camera_and_light() -> None:
    """
    Добавляет камеру и источник освещения в сцену, если их ещё нет.
    """
    # Камера
    if "Camera" not in bpy.data.objects:
        bpy.ops.object.camera_add(location=(10, -10, 10))
        cam = bpy.context.active_object
        cam.name = "Camera"
        cam.rotation_euler = (1.1, 0.0, 0.785)
        bpy.context.scene.camera = cam

    # Источник света
    if "Sun" not in bpy.data.objects:
        bpy.ops.object.light_add(type="SUN", location=(5, 5, 10))
        sun = bpy.context.active_object
        sun.name = "Sun"
        sun.data.energy = 3.0


# ============================================================
# === ГЛАВНАЯ ФУНКЦИЯ ===
# ============================================================

def main() -> None:
    """
    Точка входа: генерирует поверхность и создаёт объект в Blender.
    """
    if not HAS_BPY:
        # Режим проверки без Blender: просто печатаем несколько значений
        print("Проверка формулы (без Blender):")
        for x in [-2.0, -1.0, 0.0, 1.0, 2.0]:
            for y in [-1.0, 0.0, 1.0]:
                z = surface_function(x, y)
                print(f"  f({x:5.1f}, {y:5.1f}) = {z:8.4f}")
        return

    print(f"\n[START] Генерация поверхности '{OBJECT_NAME}'")
    print(f"  Сетка: {GRID_SUBDIVISIONS}×{GRID_SUBDIVISIONS}, область: "
          f"[{-GRID_HALF_SIZE}, {GRID_HALF_SIZE}]²")

    # Генерируем геометрию
    vertices, faces = generate_vertices_and_faces(
        func=surface_function,
        n=GRID_SUBDIVISIONS,
        half_size=GRID_HALF_SIZE,
    )

    # Создаём объект
    create_surface_object(vertices, faces, OBJECT_NAME)

    # Применяем материал
    add_color_material(OBJECT_NAME)

    # Добавляем камеру и свет
    ensure_camera_and_light()

    print(f"[DONE] Объект '{OBJECT_NAME}' готов к рендеру\n")


# ============================================================
# === ЗАПУСК ===
# ============================================================

if __name__ == "__main__" or HAS_BPY:
    main()
