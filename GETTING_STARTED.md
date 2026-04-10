# 🚀 STEM-Blender: 3D математические поверхности

**Быстрый старт для учителей и студентов**

👉 **Самодостаточная методичка (всё в одном файле):**
`docs/metodichka/полная_методичка.md`

---

## ⚡ За 2 минуты до результата

### 1. Откройте файл
```
Blender → File → Open → FunctionVisualizer_Wave.blend
```

### 2. Вы видите 3D-волну ✓

Поверхность перед вами — это график функции:
```
z = sin(2x) · cos(2y)
```

---

## 🎮 Как с ней играть

| Что? | Как? |
|---|---|
| **Вращать** | Средняя кнопка мышки (или Shift + правая) |
| **Приблизить/отдалить** | Scroll колёсика |
| **Менять параметры** | ↓ см. ниже |
| **Сделать рендер** | F12 |
| **Вид сверху** | Numpad 7 |
| **Вид спереди** | Numpad 1 |

---

## 🎛 Менять Amplitude и Frequency (ползунки)

### Где они?

1. **Выбрать волну** — кликни на неё (оранжевая рамка)
2. **Открыть свойства** — нажми `N` (если закрыто)
3. **Найти Modifier** — справа значок гаечного ключа 🔧
4. **Видишь ползунки:**
   - **Amplitude** — высота волны  
     (попробуй: 0.5, 1.0, 2.0, 3.0)
   - **Frequency** — сколько волн  
     (попробуй: 1.0, 2.0, 3.0, 5.0)

### Результат
Волна **меняется в реальном времени** при движении ползунков! 🌊

---

## 📚 Что это такое?

Здесь вы исследуете **функции двух переменных** — формулы, где:
- **x, y** — координаты на плоскости (как на карте)
- **z** — высота (третья координация)

**Примеры:**
- `z = x² + y²` → парабола (чаша)
- `z = x² − y²` → седло (ухо Принглса)
- `z = sin(x)·cos(y)` → волна (рябь на воде) ← вы здесь

---

## 🎓 На уроке учителю

### Сценарий (15 минут)

1. **Мотивация (2 мин)**
   - "Видели когда-нибудь горы на карте высот?"
   - "Вот это — математическая гора!"
   - Крутите мышкой, показывайте волну со всех сторон

2. **Интерактивная часть (8 мин)**
   - "Это не просто картинка — меняем ПАРАМЕТРЫ"
   - Меняете **Amplitude** → волна повыше
   - Меняете **Frequency** → волн становится больше
   - "Видите? Формула на боку меняет форму в реальном времени!"

3. **Выводы (5 мин)**
   - "Математика — это не скучные плоские графики"
   - "Это РЕЛЬЕФ, который можно покрутить и исследовать"
   - "Где ещё вы видели такие поверхности?" (антенны, линзы, ландшафты...)

### Домашнее задание
> Поиграйте с параметрами. Нарисуйте от руки, как выглядит волна при:
> - Amplitude = 0.5, Frequency = 1.0
> - Amplitude = 2.0, Frequency = 5.0

---

## 📖 Для студентов: копировать в Blender

### Scripting → Open → вставить этот код → Run Script

```python
# Быстрый генератор волны

import bpy
import math
from mathlib import generate_surface_geometry
from enhanced_camera_utils import setup_camera_for_function

# Параметры
resolution = 100
amplitude = 1.5
frequency = 2.0

# Удалить старую волну
if "QuickWave" in bpy.data.objects:
    bpy.data.objects.remove(bpy.data.objects["QuickWave"], do_unlink=True)

# Параметры поверхности
class Config:
    function = "wave"
    resolution = resolution
    x_min, x_max = -5, 5
    y_min, y_max = -5, 5
    amplitude = amplitude
    frequency = frequency
    sigma = 2.0

# Генерировать и вставить в Blender
vertices, faces = generate_surface_geometry(Config())
mesh = bpy.data.meshes.new("QuickWave_mesh")
mesh.from_pydata(vertices, [], faces)
mesh.update()

obj = bpy.data.objects.new("QuickWave", mesh)
bpy.context.collection.objects.link(obj)

# Камера
setup_camera_for_function("wave")

print(f"✓ Волна создана: {len(vertices)} вершин, {len(faces)} граней")
```

---

## 🔧 Другие функции

Если хочешь другую поверхность, есть файлы:
- `FunctionVisualizer_Paraboloid.blend` — чаша
- `FunctionVisualizer_Saddle.blend` — седло
- `FunctionVisualizer_Ripple.blend` — круги на воде
- `FunctionVisualizer_Gaussian.blend` — гора Гаусса

Или через Python (продвинутый уровень):
```bash
# Генерировать параболу с рендером
blender --background --python scripts/visualize_function.py -- \
    --function paraboloid --resolution 100 \
    --output paraboloid.png
```

---

## ❓ Частые вопросы

**Q: Почему волна видна со стороны, а не сверху?**  
A: Потому что камера расположена под углом — это **3D-вид**! Сверху смотреть скучно.

**Q: Как вернуть вид сверху?**  
A: Нажми **Numpad 7**. Потом **Numpad 0** вернуться в установленный вид.

**Q: Можно ли экспортировать в OBJ/STL для 3D-принтера?**  
A: Да! File → Export As → выбери формат. Волна будет реальным 3D-объектом!

**Q: Где находится формула функции?**  
A: В файле `scripts/function_library.py`. Там все 5 функций с подробным объяснением.

---

## 📁 Структура проекта

```
stem-blender-math-visualization/
├── FunctionVisualizer_Wave.blend            ← главный файл (открыть!)
├── FunctionVisualizer_Paraboloid.blend
├── FunctionVisualizer_Saddle.blend
├── FunctionVisualizer_Ripple.blend
├── FunctionVisualizer_Gaussian.blend
│
├── scripts/
│   ├── function_library.py                  ← все 5 функций
│   ├── enhanced_camera_utils.py             ← камера под углом
│   ├── pathfinding/                         ← поиск пути A*
│   └── ...
│
└── docs/
    └── metodichka\полная_методичка.md      ← полный самодостаточный формат
```

---

## 🎯 Что дальше?

### Уровень 1: Изучение
- [ ] Откройте `FunctionVisualizer_Wave.blend`
- [ ] Поиграйте с ползунками (Amplitude, Frequency)
- [ ] Посмотрите с разных углов
- [ ] Рендерьте (F12)

### Уровень 2: Экспериментирование
- [ ] Откройте другие `.blend` файлы
- [ ] Сравните разные функции
- [ ] Нарисуйте несколько вариантов от руки
- [ ] Предположите формулу для каждой

### Уровень 3: Создание
- [ ] Скопируйте код в Blender Scripting
- [ ] Измените параметры в коде
- [ ] Рендеры ваших вариантов

### Уровень 4: Продвинутый
- [ ] Прочитайте `docs/metodichka/полная_методичка.md`
- [ ] Напишите свою функцию
- [ ] Добавьте поиск пути (A*/Dijkstra)

---

## 🚀 Запуск из PowerShell (если нужно)

```powershell
# Откройте файл
& "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" FunctionVisualizer_Wave.blend

# Или рендерьте автоматически
& "C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe" `
  --background --python scripts/visualize_function.py `
  -- --function wave --output result.png
```

---

## 📞 Контакты

**Вопросы?** Смотри:
- Графический интерфейс Blender (нажми `H` или смотри справку)
- Полную методичку: `docs/metodichka/полная_методичка.md`
- Исходный код: `scripts/function_library.py`

---

**Готово! Откройте `FunctionVisualizer_Wave.blend` и начните исследовать! 🌊✨**
