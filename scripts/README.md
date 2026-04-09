# Скрипты / Scripts

В этой папке находятся Python-скрипты для работы в Blender.

---

## Файлы

| Файл | Описание |
|---|---|
| `visualize_function.py` | Основной скрипт: генерирует 3D-поверхность по формуле |

---

## Быстрый старт

### Вариант 1: запуск в Blender (рекомендуется)

```
1. Открыть Blender
2. В верхней панели переключить Workspace на «Scripting»
3. Нажать «Open» → выбрать scripts/visualize_function.py
4. Нажать ▶ (Run Script) или Alt+P
```

Объект «MathSurface» появится в сцене.

### Вариант 2: запуск из командной строки

```bash
# Linux / macOS:
blender --background --python scripts/visualize_function.py

# Windows (пример полного пути):
"C:\Program Files\Blender Foundation\Blender 4.x\blender.exe" --background --python scripts/visualize_function.py
```

> ⚠️ При запуске из командной строки Blender не открывает графический интерфейс.
> Для рендера добавьте параметры вывода в скрипт или используйте `blender --render-anim`.

### Вариант 3: проверка формулы без Blender (только Python)

```bash
python3 scripts/visualize_function.py
```

Скрипт напечатает несколько значений функции — удобно проверить формулу перед запуском в Blender.

---

## Как изменить функцию

Откройте `visualize_function.py` в VS Code. Найдите раздел:

```python
# === ФОРМУЛА ===
def surface_function(x: float, y: float) -> float:
```

Измените тело функции на любую из готовых или напишите свою:

```python
# Параболоид:
return x**2 + y**2

# Волновая поверхность:
A, k = 1.0, 1.0
return A * math.sin(k * x) * math.cos(k * y)

# Седло:
return x**2 - y**2

# Гауссов колокол:
return math.exp(-(x**2 + y**2))

# Круговые волны:
r = math.sqrt(x**2 + y**2)
return math.sin(r) if r > 1e-6 else 1.0
```

Запустите скрипт снова — объект перестроится.

---

## Параметры сетки

В файле `visualize_function.py` найдите раздел `# === ПАРАМЕТРЫ СЕТКИ ===`:

```python
GRID_SUBDIVISIONS = 100   # Качество сетки: 50 (быстро) / 100 (нормально) / 200 (детально)
GRID_HALF_SIZE = 5.0       # Область: от -5 до +5 по осям x и y
OBJECT_NAME = "MathSurface"  # Имя объекта в сцене
```

---

## Возможные ошибки

| Ошибка | Решение |
|---|---|
| `ModuleNotFoundError: No module named 'bpy'` | Запустите скрипт через Blender, а не обычный Python |
| `AttributeError: 'Context' object has no attribute ...` | Убедитесь, что версия Blender ≥ 3.0 |
| Объект создаётся, но форма плоская | Проверьте функцию — возможно, она всегда возвращает 0 |
| Медленная генерация | Уменьшите `GRID_SUBDIVISIONS` до 50 |

---

*Документация проекта: [../docs/](../docs/)*
