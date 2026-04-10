# Глава 4. Реализация в Blender

> *Первый рабочий результат — через 30 минут после открытия Blender.*

---

## 4.1 Что нужно установить

| Программа | Версия | Ссылка | Зачем |
|---|---|---|---|
| Blender | 4.x (рекомендуется) | https://blender.org | 3D-среда, Geometry Nodes, Python |
| VS Code | Любая актуальная | https://code.visualstudio.com | Редактор Python-скриптов |

Blender содержит встроенный Python 3.x и полноценный API (`bpy`). Ничего дополнительно устанавливать для скриптов не нужно.

---

## 4.2 Метод A: Geometry Nodes (рекомендуется как первый шаг)

**Зачем Geometry Nodes?**
Это система визуального программирования — вы соединяете «узлы» (nodes) вместо написания кода. Параметры поверхности (амплитуда, частота) становятся ползунками. Идеально для демонстрации на уроке: изменил ползунок → поверхность перестроилась мгновенно.

---

### Шаг 1: Создать новую сцену

**Зачем:** начинаем с чистого листа, без лишних объектов.

```
Действие:
1. Запустить Blender.
2. В стартовом диалоге — нажать «General» или просто закрыть диалог.
3. Нажать A (выделить все) → X → Delete (удалить куб, камеру, источник света).
4. (Опционально) Добавить обратно: камеру (Shift+A → Camera) и источник света (Shift+A → Light → Sun).
```

**Результат:** пустая сцена.

---

### Шаг 2: Создать объект Grid

**Зачем:** Grid — это сетка вершин, которую мы будем деформировать по формуле. Чем больше подразделений (Subdivisions), тем плавнее поверхность.

```
Действие:
1. Нажать Shift+A → Mesh → Grid.
2. В левом нижнем углу появится панель «Add Grid» — нажать на неё.
3. Установить:
   - X Size: 10
   - Y Size: 10
   - X Subdivisions: 100
   - Y Subdivisions: 100
```

**Результат:** плоская сетка 10×10 единиц, 100×100 вершин.

> ⚠️ Если панель «Add Grid» исчезла — нажмите F9, она появится снова.

---

### Шаг 3: Добавить модификатор Geometry Nodes

**Зачем:** модификатор Geometry Nodes — это «блок процедурной логики», который мы присоединяем к объекту. Внутри него мы напишем нашу формулу.

```
Действие:
1. Убедитесь, что Grid выделен (оранжевая обводка).
2. Справа нажмите на вкладку Properties (синяя гайка или список панелей).
3. Выберите «Modifier Properties» (иконка гаечного ключа).
4. Нажать «Add Modifier» → «Geometry Nodes».
5. Нажать «New» — создаётся пустой граф узлов.
6. Нажать «Open Shader Editor» или переключить рабочую область на «Geometry Node Editor».
```

**Результат:** открыт редактор Geometry Nodes с двумя базовыми узлами: «Group Input» и «Group Output».

---

### Шаг 4: Построить граф для параболоида z = x² + y²

**Зачем:** мы создадим узлы, которые вычитают координаты каждой вершины, возводят в квадрат и суммируют, затем устанавливают новую позицию.

```
Схема узлов:
[Group Input] ──────────────────────────────────┐
                                                 ↓
[Input: Geometry] → [Set Position] → [Group Output: Geometry]
                          ↑
                     [Offset Z]
                          ↑
           [Add] ← [Multiply(x,x)] ← [Separate XYZ → X]
                ↑
           [Multiply(y,y)] ← [Separate XYZ → Y]
```

**Пошаговая инструкция:**

```
Шаг 4.1: В редакторе GN — Add (Shift+A) → Input → Position
          Добавить узел Position — он даёт (x, y, z) текущей вершины.

Шаг 4.2: Add → Utilities → Vector → Separate XYZ
          Подключить Position → Separate XYZ.
          Теперь у нас есть X, Y, Z отдельно.

Шаг 4.3: Add → Utilities → Math (×2)
          Первый Math: операция «Multiply», подключить X → X → Value
          (x * x = x²)
          Второй Math: операция «Multiply», подключить Y → Y → Value
          (y * y = y²)

Шаг 4.4: Add → Utilities → Math
          Операция «Add», подключить x² + y²

Шаг 4.5: Add → Utilities → Vector → Combine XYZ
          Подключить: X=0, Y=0, Z = результат из шага 4.4

Шаг 4.6: Add → Geometry → Write Attributes → Set Position
          Подключить:
          — Geometry: от Group Input
          — Offset: от Combine XYZ (наш вектор смещения)

Шаг 4.7: Подключить Set Position → Group Output → Geometry
```

**Результат:** сетка деформируется в параболоид z = x² + y².

---

### Шаг 5: Добавить параметры через Group Input

**Зачем:** чтобы менять форму поверхности ползунками, нужно вынести параметры (A, k) в «Group Input» — тогда они появятся в панели модификатора.

**Для волновой поверхности z = A·sin(k·x)·cos(k·y):**

```
Шаг 5.1: В Group Input — нажать «+» → добавить Float «A» (амплитуда, default: 1.0)
Шаг 5.2: Добавить Float «k» (частота, default: 1.0)

Шаг 5.3: Схема:
[Separate XYZ → X] → [Math: Multiply by k] → [Math: Sine]   ──┐
                                                                 → [Math: Multiply] → [×A] → Z
[Separate XYZ → Y] → [Math: Multiply by k] → [Math: Cosine] ──┘
```

**Результат:** в панели модификатора появятся ползунки A и k. Двигайте их — поверхность перестраивается в реальном времени.

---

### Шаг 6: Применить материал (цветовая карта по высоте)

**Зачем:** цветовая окраска по высоте z помогает «читать» поверхность — сразу видно, где вершины и впадины.

```
Действие:
1. Выделить объект → Properties → Material Properties → New.
2. Переключить на «Shader Editor».
3. В шейдере:
   - Add → Input → Geometry → Position (получаем z-координату)
   - Add → Converter → Separate XYZ → Z
   - Add → Converter → Map Range (нормализовать z в диапазон 0–1)
   - Add → Converter → Color Ramp (задать цвета: синий→зелёный→красный)
   - Подключить к Base Color материала.
```

**Результат:** поверхность окрашена от синего (низ) до красного (верх).

---

## 4.3 Метод B: Python Script (bpy)

**Зачем Python?**
Когда нужна полная свобода: любая формула, любой масштаб, экспорт данных, интеграция с VS Code. Метод сложнее Geometry Nodes, но это уже настоящее программирование.

### 4.3.1 Как запустить скрипт в Blender

```
1. Открыть Blender.
2. В верхнем меню — переключить Workspace на «Scripting».
3. Нажать «New» в редакторе скриптов.
4. Вставить или открыть файл scripts/visualize_function.py.
5. Нажать «Run Script» (▶) или Alt+P.
```

### 4.3.2 Запуск из VS Code (командная строка)

```powershell
# Запустить скрипт в фоновом режиме с параметрами:
blender --background --python scripts\visualize_function.py -- --function wave --resolution 100 --amplitude 1.5 --frequency 2.0

# Рендер и сохранение PNG:
blender --background --python scripts\visualize_function.py -- --function wave --resolution 100 --amplitude 2.0 --frequency 3.0 --output assets\renders\wave_A2_k3.png
```

> 📝 Путь к Blender (`blender`) должен быть в PATH, иначе используйте полный путь, например:
> - Windows: `"C:\Program Files\Blender Foundation\Blender 4.x\blender.exe"`
> - macOS: `/Applications/Blender.app/Contents/MacOS/blender`
> - Linux: `/usr/bin/blender`

---

### 4.3.3 Как менять функцию и параметры

Теперь основные скрипты используют единый интерфейс:

- `--function` (`paraboloid`, `saddle`, `wave`, `ripple`, `gaussian`, `custom`)
- `--resolution`
- `--x-min`, `--x-max`, `--y-min`, `--y-max`
- `--amplitude`, `--frequency`, `--sigma`

Пример:

```powershell
blender --background --python scripts\generate_surface_mesh.py -- --function gaussian --sigma 1.2 --resolution 90 --output assets\renders\gaussian_sigma1_2.png
```

Если нужно добавить новую формулу, расширьте реестр в `scripts/function_library.py`.

---

## 4.4 Рендеринг и сохранение результата

```
1. Установить камеру: Numpad 0 → вид из камеры.
   Или: выделить камеру → G → переместить на нужную позицию.
2. Render → Render Image (F12).
3. В окне рендера: Image → Save As → выбрать путь и формат (PNG).
```

Для видео с анимацией ползунков:
```
1. Добавить ключевые кадры для параметра (ПКМ на ползунке → Insert Keyframe).
2. Render → Render Animation (Ctrl+F12).
3. В настройках вывода: Output Properties → путь, формат (MP4 или PNG-последовательность).
```

---

## 4.5 Типичные ошибки и решения

| Ошибка | Причина | Решение |
|---|---|---|
| Поверхность не деформируется | Не подключены узлы в Geometry Nodes | Проверить все связи (линии между узлами) |
| Поверхность «колышется» непредсказуемо | Значения k слишком большие | Уменьшить k до 0.5–2.0 |
| Слишком грубая сетка | Мало Subdivisions в Grid | Увеличить до 100–200 |
| Скрипт выдаёт ошибку ImportError | Пытается импортировать внешнюю библиотеку | Использовать только math и встроенные модули Python |
| Рендер слишком тёмный | Нет источника освещения | Add → Light → Sun или Environment Texture |
| Скрипт не применяет цвет | Не создан материал | В скрипте добавить создание материала (см. visualize_function.py) |

---

*Следующий раздел: [05 — Эксперименты](05_эксперименты.md)*
