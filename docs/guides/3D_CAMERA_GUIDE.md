# Использование улучшенных 3D-рендеров и индивидуальных .blend файлов

**Дата создания:** 11 апреля 2026  
**Версия:** 2.1 (с 3D-камерой и персональными blend-файлами)

---

## 🎬 Что было добавлено

### 1. **Улучшенная позиция камеры (3D-вид вместо сверху)**

Раньше все рендеры были **вид сверху** (камера смотрит точно вниз). Теперь камера расположена **сбоку под углом** — это даёт ощущение объёма!

**Где:** Все основные скрипты теперь используют `enhanced_camera_utils.py`:
- ✅ `visualize_function.py`
- ✅ `generate_surface_mesh.py`
- ✅ `setup_geometry_nodes_surface.py`
- ✅ `visualize_path_in_blender.py`

### 2. **Индивидуальные .blend файлы для каждой функции**

Создаёт 5 отдельных готовых файлов:
- `FunctionVisualizer_Paraboloid.blend` — параболоид
- `FunctionVisualizer_Saddle.blend` — седло
- `FunctionVisualizer_Wave.blend` — волна
- `FunctionVisualizer_Ripple.blend` — рябь
- `FunctionVisualizer_Gaussian.blend` — Гаусс

Каждый файл имеет оптимальную камеру и освещение для своей функции!

---

## 🚀 Быстрый старт

### Вариант 1: Создать 5 blend-файлов (автоматически)

```bash
blender --background --python scripts/create_individual_blend_files.py
```

**Результат:** в корне проекта появятся 5 файлов:
```
stem-blender-math-visualization/
├── FunctionVisualizer_Paraboloid.blend    ← новый
├── FunctionVisualizer_Saddle.blend        ← новый
├── FunctionVisualizer_Wave.blend          ← новый
├── FunctionVisualizer_Ripple.blend        ← новый
├── FunctionVisualizer_Gaussian.blend      ← новый
└── ...
```

Откройте любой файл и сразу увидите **3D-поверхность** с хорошей камерой!

### Вариант 2: Рендер с улучшенной камерой

```bash
# Волна (вид сбоку, под углом)
blender --background --python scripts/visualize_function.py -- \
    --function wave --resolution 100 --amplitude 2 --frequency 3 \
    --output assets/renders/wave_3d_view.png

# Парабола
blender --background --python scripts/generate_surface_mesh.py -- \
    --function paraboloid --resolution 80 \
    --output assets/renders/paraboloid_3d_view.png
```

### Вариант 3: Интерактивная волна (Geometry Nodes)

```bash
# Откроется Blender с волной, которой вы можете менять параметры ползунками
blender-python scripts/setup_geometry_nodes_surface.py
```

Меняйте **Amplitude** и **Frequency**, и камера будет смотреть сбоку!

---

## 📐 Технические детали

### Как работает улучшенная камера

**Новое:** файл `enhanced_camera_utils.py` содержит предустановки камеры для каждой функции:

```python
CAMERA_PRESETS = {
    "wave": {
        "location": (13, -11, 8),           # позиция камеры в 3D
        "rotation": (60°, 0, 40°),          # углы поворота
        "light_energy": 4.0,                # яркость света
    },
    "paraboloid": {
        "location": (12, -10, 8),
        "rotation": (65°, 0, 45°),
        "light_energy": 4.0,
    },
    # и так далее для saddle, ripple, gaussian
}
```

**Объяснение координат камеры:**
- `location = (x, y, z)`:
  - `x=12`: смещение в сторону (не по центру)
  - `y=-11`: отступ назад
  - `z=8`: на высоте 8 единиц (выше поверхности)
- `rotation = (rx, ry, rz)`:
  - `rx=60°`: наклон вниз (смотрим на поверхность под углом)
  - `ry=0`: без кручения
  - `rz=40°`: поворот вокруг вертикальной оси (вид сбоку)

### Как использовать в своём коде

Если вы пишете свой скрипт для Blender:

```python
from enhanced_camera_utils import setup_camera_for_function, setup_angled_camera

# Вариант 1: автоматически для известной функции
camera, light = setup_camera_for_function("wave")

# Вариант 2: создать свою позицию
import math
camera = setup_angled_camera(
    location=(15, -15, 10),  # ↑ выше, дальше
    rotation_euler=(math.radians(50), 0, math.radians(50))  # ↑ другие углы
)
```

---

## 🎨 Примеры результатов

### До (вид сверху)
```
Выглядит как 2D тепловая карта, плоская
```

### После (новая камера)
```
Выглядит ОБЪЁМНО:
  - Волны имеют высоту и форму
  - Парабола выглядит как настоящая 3D чаша
  - Седло имеет характерный изгиб
```

---

## 🔧 Что делают новые файлы

| Файл | Назначение |
|---|---|
| `enhanced_camera_utils.py` | Утилиты для позиции камеры (новое!) |
| `create_individual_blend_files.py` | Генератор 5 blend-файлов (новое!) |
| `visualize_function.py` | ✅ обновлён для 3D-камеры |
| `generate_surface_mesh.py` | ✅ обновлён для 3D-камеры |
| `setup_geometry_nodes_surface.py` | ✅ обновлён для 3D-камеры |
| `visualize_path_in_blender.py` | ✅ обновлён для 3D-камеры |

---

## 🎓 Для учителей

Теперь вы можете показывать студентам **настоящие 3D-объекты**, а не плоские тепловые карты!

### На уроке:

1. **Демонстрация (5 мин):**
   ```bash
   blender FunctionVisualizer_Wave.blend
   ```
   Откройте файл, крутите мышкой, показывайте разные углы.

2. **Интерактивная часть (10 мин):**
   ```bash
   blender FunctionVisualizer_Wave.blend
   # Выбрать объект → Properties → Modifier → Amplitude / Frequency
   # Меняйте параметры, ученики видят, как меняется форма!
   ```

3. **Рендер результатов (5 мин):**
   ```bash
   blender --background --python scripts/visualize_function.py -- \
       --function wave --amplitude 3 --frequency 4 \
       --output results/wave_student_version.png
   ```

---

## 📹 Видео-переходы

Если нужна **видео-анимация** переходов между углами:

```bash
# (пока не реализовано, но легко добавить)
# Например: создать 36 кадров с разными углами камеры
# и склеить в mp4 через ffmpeg
```

---

## ❓ FAQ

**Q: Почему рендер теперь выглядит не сверху?**  
A: Потому что камера теперь `location=(12, -11, 8)` вместо `(0, 0, 15)`. Это даёт 3D-эффект.

**Q: Как вернуть вид сверху?**  
A: Измените в коде:
```python
camera.location = (0, 0, 15)  # точно выше
camera.rotation = (0, 0, 0)   # прямо вниз
```

**Q: Зачем 5 отдельных blend-файлов?**  
A: Каждая функция требует свой угол камеры. Волны лучше видны сбоку, параболу красивее видно под углом 65°.

**Q: Я хочу свой угол камеры!**  
A: Отредактируйте `enhanced_camera_utils.py`:
```python
CAMERA_PRESETS["my_custom"] = {
    "location": (20, -20, 15),
    "rotation": (math.radians(45), 0, math.radians(60)),
    "light_energy": 5.0,
}
```

---

## 🚀 Дальнейшее развитие

- [ ] Быстрая видео-анимация (mp4)
- [ ] Интерактивный выбор угла камеры через CLI: `--camera-preset wave` или `--camera-custom 15,-15,10`
- [ ] Экспорт в 3D-формат OBJ/FBX для других приложений
- [ ] Виртуальная тур объекта (360° вращение)

---

**Спасибо за использование проекта! Теперь ваши математические поверхности выглядят реально объёмно! 🎉**
