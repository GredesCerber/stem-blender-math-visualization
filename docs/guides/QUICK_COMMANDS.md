# ⚡ КОМАНДЫ ДЛЯ БЫСТРОГО СТАРТА

Копируй и пасти прямо в PowerShell / Terminal

---

## 🎬 Создать 5 красивых blend-файлов (3D-камера)

```powershell
cd C:\Users\GredesCerber\Desktop\Учеба\3\ курс\2\ семестр\stem-blender-math-visualization
blender --background --python scripts/create_individual_blend_files.py
```

**Результат:** создаёт 5 файлов в корне проекта:
- ✅ FunctionVisualizer_Paraboloid.blend
- ✅ FunctionVisualizer_Saddle.blend
- ✅ FunctionVisualizer_Wave.blend
- ✅ FunctionVisualizer_Ripple.blend
- ✅ FunctionVisualizer_Gaussian.blend

---

## 👀 Открыть файл в Blender (интерактивный режим)

```powershell
# Волна с 3D-камерой
blender FunctionVisualizer_Wave.blend &

# Парабола
blender FunctionVisualizer_Paraboloid.blend &

# Любой другой...
blender FunctionVisualizer_Saddle.blend &
```

**Как использовать:**
- Средняя кнопка мышки → крутить объект
- Scroll → приблизить/отдалить
- Numpad 7 → вид сверху
- Numpad 1 → вид спереди
- F12 → рендер (красивая картинка)

---

## 🖼 Рендер в PNG с 3D-камерой

```powershell
# Волна
blender --background --python scripts/visualize_function.py -- `
    --function wave --resolution 100 --amplitude 2 --frequency 3 `
    --output assets/renders/wave_3d_beautiful.png

# Парабола
blender --background --python scripts/generate_surface_mesh.py -- `
    --function paraboloid --resolution 80 `
    --output assets/renders/paraboloid_3d_beautiful.png

# Гаусс
blender --background --python scripts/visualize_function.py -- `
    --function gaussian --sigma 1.8 `
    --output assets/renders/gaussian_3d_beautiful.png
```

---

## 🎮 Интерактивная волна (ползунки в Blender)

```powershell
# Откроется Blender с волной, можно менять Amplitude и Frequency ползунками
blender --python scripts/setup_geometry_nodes_surface.py
```

**Как использовать:**
1. Откроется Blender
2. Выбрать объект MathSurface_GN
3. Properties (правая панель) → Modifier (синий гаечный ключ)
4. Менять Amplitude (высота) и Frequency (частота) с ползунков
5. Воля меняется в реальном времени!

---

## 🔍 Поиск пути A* на поверхности (3D-рендер)

```powershell
# Простой маршрут (без препятствий)
blender --background --python scripts/pathfinding/visualize_path_in_blender.py -- `
    --function wave --algorithm astar `
    --start-x -4 --start-y -4 --goal-x 4 --goal-y 4 `
    --output assets/renders/path_wave_astar.png

# С препятствием (круг)
blender --background --python scripts/pathfinding/visualize_path_in_blender.py -- `
    --function paraboloid --algorithm dijkstra `
    --obstacle-circle 0,0,1.5 `
    --start-x -4 --start-y -4 --goal-x 4 --goal-y 4 `
    --output assets/renders/path_with_obstacle.png
```

---

## 📚 Пакетный рендер (много вариантов сразу)

```powershell
# Рендерит 10+ пресетов (парабола, волна, волна с другими параметрами и т.д.)
cd scripts
python batch_render.py --blender-exe "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" `
    --output-dir ..\assets\renders `
    --metadata-json renders_report.json `
    --metadata-csv renders_report.csv
```

---

## 📖 Посмотреть документацию

```powershell
# Полная техническая документация (3D-камера, примеры кода)
notepad docs\guides\3D_CAMERA_GUIDE.md

# Быстрый старт (за 1 минуту)
notepad docs\guides\QUICK_START_3D.md

# Резюме всех изменений (апрель 2026)
notepad docs\status\SUMMARY_APRIL_2026.md

# Статус проекта и оставшиеся задачи
notepad docs\status\COMPLETED_AND_REMAINING.md
```

---

## 🐛 Если что-то не работает

```powershell
# Проверить версию Blender
blender --version

# Нужна версия 4.0 или выше. Если старше, обновить с blender.org

# Запустить скрипт в режиме Preview (без Blender)
cd scripts
python visualize_function.py --function wave --resolution 50
# Выведет значения функции в терминал (без 3D, но проверит код)
```

---

## 💡 Полезные советы

```powershell
# Добавить путь Blender в PATH (если команда `blender` не работает)
# Тогда можно просто: blender --background ... (без полного пути)

# Для красивого рендера используй высокое разрешение:
--resolution 120  # средне
--resolution 150  # хорошо
--resolution 200  # очень хорошо (долго рендерится)

# Менять параметры:
--amplitude 2.5      # высота
--frequency 4        # частота (скорость колебания)
--sigma 1.5          # ширина (для gaussian)
```

---

## 🎨 Ява хак: свои углы камеры

Если хочешь свой угол камеры, отредактируй файл `enhanced_camera_utils.py`:

```python
CAMERA_PRESETS["my_custom"] = {
    "location": (20, -20, 15),           # x, y, z позиция
    "rotation": (math.radians(50), 0, math.radians(60)),  # углы
    "light_energy": 5.0,
}

# Потом используй: --camera-preset my_custom
# (нужно добавить поддержку аргумента в скрипты)
```

---

## 📊 Шпаргалка по функциям

| Функция | Команда | Что видно |
|---|---|---|
| **Парабола** | `--function paraboloid` | Чаша/воронка |
| **Седло** | `--function saddle` | Седловидный изгиб |
| **Волна** | `--function wave` | Рябь в две стороны |
| **Рябь** | `--function ripple` | Круги на воде |
| **Гаусс** | `--function gaussian` | Куполообразная горка |

---

## ✅ Проверка установки

```powershell
# Проверить что есть Blender
blender --version

# Проверить что есть Pythonв Blender
blender --python -c "import bpy; print('OK!')"

# Проверить что есть пакет bmesh
blender --python -c "import bmesh; print('OK!')"
```

---

**Готово! Наслаждайся красивыми 3D-поверхностями! 🚀✨**
