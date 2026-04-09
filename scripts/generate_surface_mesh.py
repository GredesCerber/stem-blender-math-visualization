"""
generate_surface_mesh.py
========================
Учебный STEM-проект: Интерактивная 3D-визуализация математических функций
Павлодарский педагогический университет

НАЗНАЧЕНИЕ:
    Скрипт создаёт полигональную сетку (mesh) в Blender, представляющую
    поверхность z = f(x, y) для выбранной математической функции.

КАК ЗАПУСТИТЬ:
    1. Откройте Blender 3.6+.
    2. Перейдите во вкладку "Scripting" (верхняя строка вкладок).
    3. Нажмите "Open" и выберите этот файл — или вставьте содержимое вручную.
    4. Измените параметры в блоке "ПАРАМЕТРЫ" ниже.
    5. Нажмите ▶ "Run Script" (или Alt+P).
    6. В 3D-вьюпорте появится объект "MathSurface".

ИЗМЕНИТЬ ФУНКЦИЮ:
    Установите FUNCTION_NAME = "wave" | "paraboloid" | "saddle" |
                                       "ripple" | "gaussian" | "custom"
    При выборе "custom" — напишите свою формулу в функции f_custom(x, y).
"""

import bpy
import bmesh
import math


# ============================================================
# ПАРАМЕТРЫ: меняйте здесь!
# ============================================================

# Диапазон по осям X и Y
X_MIN: float = -5.0
X_MAX: float = 5.0
Y_MIN: float = -5.0
Y_MAX: float = 5.0

# Количество делений сетки по каждой оси (N×N вершин)
# Рекомендация: 40–80 для плавного вида, 20 — для быстрого теста
RESOLUTION: int = 60

# Амплитуда (A) — влияет на высоту «гребней» и «впадин»
AMPLITUDE: float = 1.0

# Частота (k) — влияет на количество повторений волны
FREQUENCY: float = 1.0

# Ширина гауссиана (σ) — только для функции "gaussian"
SIGMA: float = 2.0

# Выбор функции: "paraboloid" | "saddle" | "wave" | "ripple" | "gaussian" | "custom"
FUNCTION_NAME: str = "wave"

# Имя объекта в Blender (предыдущий объект с таким именем будет удалён)
OBJECT_NAME: str = "MathSurface"

# ============================================================
# ФУНКЦИИ z = f(x, y)
# ============================================================


def f_paraboloid(x: float, y: float) -> float:
    """Параболоид вращения: z = x² + y²
    Форма: «чаша», минимум в точке (0, 0, 0).
    """
    return x**2 + y**2


def f_saddle(x: float, y: float) -> float:
    """Гиперболический параболоид (седло): z = x² - y²
    Форма: «седло» — вогнутый вдоль X, выпуклый вдоль Y.
    Седловая точка в (0, 0, 0).
    """
    return x**2 - y**2


def f_wave(x: float, y: float) -> float:
    """Тригонометрическая волна: z = A * sin(k*x) * cos(k*y)
    Параметры: AMPLITUDE (A), FREQUENCY (k).
    """
    return AMPLITUDE * math.sin(FREQUENCY * x) * math.cos(FREQUENCY * y)


def f_ripple(x: float, y: float) -> float:
    """Радиальная волна (воронка): z = A * sin(sqrt(x² + y²))
    Форма: концентрические кольца вокруг начала координат.
    """
    r = math.sqrt(x**2 + y**2)
    return AMPLITUDE * math.sin(r)


def f_gaussian(x: float, y: float) -> float:
    """Гауссова поверхность (колокол): z = A * exp(-(x² + y²) / σ²)
    Форма: гладкий купол с максимумом в (0, 0, A).
    Параметры: AMPLITUDE (A), SIGMA (σ).
    """
    return AMPLITUDE * math.exp(-(x**2 + y**2) / (SIGMA**2))


def f_custom(x: float, y: float) -> float:
    """Пользовательская функция — измените формулу здесь!
    Примеры:
        return math.sin(x) + math.cos(y)
        return math.sin(x * y)
        return x * math.exp(-(x**2 + y**2))
    """
    return math.sin(x) + math.cos(y)


# ============================================================
# ВЫБОР АКТИВНОЙ ФУНКЦИИ
# ============================================================

FUNCTION_MAP: dict = {
    "paraboloid": f_paraboloid,
    "saddle": f_saddle,
    "wave": f_wave,
    "ripple": f_ripple,
    "gaussian": f_gaussian,
    "custom": f_custom,
}

if FUNCTION_NAME not in FUNCTION_MAP:
    raise ValueError(
        f"Неизвестная функция: '{FUNCTION_NAME}'. "
        f"Допустимые значения: {list(FUNCTION_MAP.keys())}"
    )

f = FUNCTION_MAP[FUNCTION_NAME]


# ============================================================
# ПОСТРОЕНИЕ СЕТКИ (MESH)
# ============================================================


def build_surface_vertices(
    f_func,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    n: int,
) -> tuple[list, list]:
    """Генерирует вершины и грани для поверхности z = f(x, y).

    Алгоритм:
        1. Делим [x_min, x_max] и [y_min, y_max] на n равных отрезков.
        2. Для каждой пары (i, j) вычисляем x, y, z = f(x, y).
        3. Соединяем четыре соседних вершины в квадратный полигон.

    Returns:
        vertices: список из (n+1)*(n+1) кортежей (x, y, z)
        faces: список из n*n кортежей-индексов (a, b, c, d)
    """
    dx = (x_max - x_min) / n
    dy = (y_max - y_min) / n

    vertices = []
    for i in range(n + 1):
        for j in range(n + 1):
            x = x_min + i * dx
            y = y_min + j * dy
            z = f_func(x, y)
            vertices.append((x, y, z))

    # Индекс вершины в строке i, столбце j: i*(n+1) + j
    faces = []
    for i in range(n):
        for j in range(n):
            a = i * (n + 1) + j
            b = a + 1
            c = (i + 1) * (n + 1) + j + 1
            d = (i + 1) * (n + 1) + j
            faces.append((a, b, c, d))

    return vertices, faces


def create_blender_mesh(name: str, vertices: list, faces: list) -> bpy.types.Object:
    """Создаёт объект Blender с заданными вершинами и гранями.

    Args:
        name: имя объекта в Blender
        vertices: список вершин [(x, y, z), ...]
        faces: список граней [(a, b, c, d), ...]

    Returns:
        Новый объект Blender (bpy.types.Object)
    """
    # Создаём пустой mesh и объект
    mesh = bpy.data.meshes.new(name=name + "_mesh")
    obj = bpy.data.objects.new(name=name, object_data=mesh)

    # Добавляем объект в текущую коллекцию сцены
    bpy.context.collection.objects.link(obj)

    # Используем bmesh для заполнения данных
    bm = bmesh.new()

    # Добавляем вершины
    bm_verts = [bm.verts.new(v) for v in vertices]

    # Обновляем таблицу вершин (обязательно перед созданием граней)
    bm.verts.ensure_lookup_table()

    # Добавляем грани
    for face_indices in faces:
        bm.faces.new([bm_verts[i] for i in face_indices])

    # Пересчитываем нормали
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    # Записываем bmesh в mesh Blender
    bm.to_mesh(mesh)
    bm.free()

    # Пересчитываем нормали на уровне mesh (для корректного освещения)
    mesh.calc_normals()

    return obj


def remove_existing_object(name: str) -> None:
    """Удаляет объект с заданным именем из сцены, если он существует."""
    if name in bpy.data.objects:
        obj = bpy.data.objects[name]
        bpy.data.objects.remove(obj, do_unlink=True)


def add_default_material(obj: bpy.types.Object, function_name: str) -> None:
    """Добавляет простой материал с цветом, зависящим от типа функции."""
    color_map = {
        "paraboloid": (0.2, 0.5, 0.9, 1.0),   # синий
        "saddle":     (0.2, 0.8, 0.4, 1.0),   # зелёный
        "wave":       (0.9, 0.5, 0.1, 1.0),   # оранжевый
        "ripple":     (0.6, 0.2, 0.9, 1.0),   # фиолетовый
        "gaussian":   (0.9, 0.2, 0.2, 1.0),   # красный
        "custom":     (0.9, 0.9, 0.2, 1.0),   # жёлтый
    }
    base_color = color_map.get(function_name, (0.5, 0.5, 0.5, 1.0))

    mat_name = f"Mat_{function_name}"
    if mat_name in bpy.data.materials:
        mat = bpy.data.materials[mat_name]
    else:
        mat = bpy.data.materials.new(name=mat_name)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = base_color
            bsdf.inputs["Roughness"].default_value = 0.4
            bsdf.inputs["Metallic"].default_value = 0.0

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


# ============================================================
# ОСНОВНАЯ ЛОГИКА
# ============================================================

def main() -> None:
    print(f"\n{'='*50}")
    print(f"  STEM-проект: Визуализация поверхности")
    print(f"  Функция: {FUNCTION_NAME}")
    print(f"  Разрешение: {RESOLUTION}×{RESOLUTION}")
    print(f"  Область: X=[{X_MIN}, {X_MAX}], Y=[{Y_MIN}, {Y_MAX}]")
    print(f"{'='*50}\n")

    # Удаляем предыдущий объект (если есть)
    remove_existing_object(OBJECT_NAME)

    # Строим сетку
    print("  Генерация вершин и граней...")
    vertices, faces = build_surface_vertices(f, X_MIN, X_MAX, Y_MIN, Y_MAX, RESOLUTION)
    print(f"  Вершин: {len(vertices)}, Граней: {len(faces)}")

    # Создаём объект в Blender
    print("  Создание объекта в Blender...")
    obj = create_blender_mesh(OBJECT_NAME, vertices, faces)

    # Добавляем материал
    add_default_material(obj, FUNCTION_NAME)

    # Сбрасываем выделение и выбираем новый объект
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    print(f"\n  ✓ Объект '{OBJECT_NAME}' создан!")
    print(f"  Нажмите Numpad . для центровки вида на объект.\n")


main()
