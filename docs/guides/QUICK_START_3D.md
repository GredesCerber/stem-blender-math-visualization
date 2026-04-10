# БЫСТРАЯ ИНСТРУКЦИЯ: 3D-камера и персональные blend-файлы

## 🎯 Самый быстрый способ (1 минута)

### Шаг 1: Создать 5 blend-файлов для каждой функции
```powershell
cd stem-blender-math-visualization
blender --background --python scripts/create_individual_blend_files.py
```

**Готово! В папке проекта появились:**
- `FunctionVisualizer_Paraboloid.blend` 
- `FunctionVisualizer_Saddle.blend`
- `FunctionVisializer_Wave.blend`
- `FunctionVisualizer_Ripple.blend`
- `FunctionVisualizer_Gaussian.blend`

### Шаг 2: Открыть любой файл в Blender
```powershell
blender FunctionVisualizer_Wave.blend &
```

**Вы увидите:**
- 3D-поверхность волны
- Камера расположена сбоку под углом (не сверху!)
- Свет хорошо освещает объект
- **Крутите мышкой** (средняя кнопка) чтобы вращать

---

## 🎨 Три варианта использования

### Вариант А: Просмотр (интерактивный)
```powershell
blender FunctionVisualizer_Wave.blend
# Средняя кнопка мышки → вращайте объект
# Numpad 7 → вид сверху
# Numpad 1 → вид спереди
# Numpad 0 → через камеру (установленный вид)
```

### Вариант Б: Рендер PNG (высокое качество 3D)
```powershell
blender --background --python scripts/visualize_function.py -- `
    --function wave --resolution 100 --amplitude 2 `
    --output renders/wave_3d.png
```

### Вариант В: Интерактивная волна (ползунки)
```powershell
blender --python scripts/setup_geometry_nodes_surface.py
# Properties → Modifier → Amplitude / Frequency
# Меняйте ползунки → поверхность меняется в реальном времени!
```

---

## 📊 Сравнение углов камеры

| Функция | Позиция камеры | Угол смотрения | Лучше всего видно |
|---|---|---|---|
| **Paraboloid** | (12, -10, 8) | 65° | Форма чаши |
| **Saddle** | (11, -11, 7) | 70° | Седловидный изгиб |
| **Wave** | (13, -11, 8) | 60° | Волновой узор |
| **Ripple** | (12, -12, 9) | 55° | Круговые волны |
| **Gaussian** | (12, -10, 10) | 55° | Куполообразная форма |

---

## 🔧 Что изменилось?

**Старая версия (вид сверху):**
```
Выглядит как плоская тепловая карта (2D)
```

**Новая версия (3D-камера):**
```
                      ╱─────╲
        волны видны  │ объём │  настоящая форма
        как рельеф   ╲─────╱   вместо плоскости
```

---

## 💚 Файлы, которые обновились

- ✅ `visualize_function.py` — теперь с 3D-камерой
- ✅ `generate_surface_mesh.py` — теперь с 3D-камерой
- ✅ `setup_geometry_nodes_surface.py` — теперь с 3D-камерой
- ✅ `visualize_path_in_blender.py` — теперь с 3D-камерой
- 🆕 `enhanced_camera_utils.py` — новые предустановки камеры
- 🆕 `create_individual_blend_files.py` — генератор 5 blend-файлов
- 🆕 `docs/guides/3D_CAMERA_GUIDE.md` — полная документация

---

## 📧 Вопросы?

Смотрите подробное объяснение в `docs/guides/3D_CAMERA_GUIDE.md`

**Основные команды:**
```powershell
# Создать все 5 blend-файлов
blender --background --python scripts/create_individual_blend_files.py

# Рендер конкретной функции
blender --background --python scripts/visualize_function.py -- --function wave --output wave.png

# Интерактивный режим
blender --python setup_geometry_nodes_surface.py
```

---

**Готово! Наслаждайтесь 3D-поверхностями! 🚀**
