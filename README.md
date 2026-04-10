# STEM-проект: 3D-визуализация математических поверхностей в Blender

Учебный проект для наглядного изучения функций вида `z = f(x, y)` через интерактивную 3D-визуализацию в Blender.

---

## 🚀 БЫСТРЫЙ СТАРТ

**Главное:** откройте файл и начните экспериментировать!

```
1. Откройте: FunctionVisualizer_Wave.blend
2. Крутите волну мышкой
3. Меняйте параметры ползунками (Amplitude, Frequency)
4. Смотрите как меняется форма!
```

👉 **[Полная инструкция → GETTING_STARTED.md](GETTING_STARTED.md)**

---

## 📚 Что здесь

- ✅ **5 готовых 3D-файлов** (.blend) — просто открыть в Blender
- ✅ **Интерактивные ползунки** — менять параметры в реальном времени
- ✅ **Полная методичка** — для учителей и студентов
- ✅ **Python-скрипты** — для своих экспериментов

---

## 📖 Что отвечают

| Для кого | Смотри |
|---|---|
| **Я хочу на уроке показать волну** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Мне нужна полная методичка** | `docs/методичка_подробная.md` |
| **Я хочу писать свой код** | [docs/guides/QUICK_COMMANDS.md](docs/guides/QUICK_COMMANDS.md) |
| **Я хочу понять архитектуру** | `docs/PROJECT_VISION.md` |

---

## 🎬 На уроке (15 минут)

```
Учитель открывает: FunctionVisualizer_Wave.blend
Студенты видят: красивая 3D-волна
Учитель показывает: менять ползунки → волна меняется
Вывод: "Это математика! z = sin(2x)·cos(2y)"
```

👉 Подробный сценарий в [GETTING_STARTED.md](GETTING_STARTED.md)

---

## 📁 Главные файлы

```
FunctionVisualizer_Wave.blend           ← ОТКРОЙТЕ ЭТОТ!
FunctionVisualizer_Paraboloid.blend     ← для опыта
FunctionVisualizer_Saddle.blend         ← ещё вариант
FunctionVisualizer_Ripple.blend         ← волны от центра
FunctionVisualizer_Gaussian.blend       ← гора Гаусса

scripts/
├── function_library.py                 ← все 5 функций
├── visualize_function.py               ← генератор поверхностей
└── pathfinding/                        ← поиск пути A*/Dijkstra

docs/
├── GETTING_STARTED.md                  ← начните отсюда!
└── методичка_подробная.md             ← глубокое изучение
```

---

## 💡 Ключевые функции

| Функция | Формула | Форма |
|---|---|---|
| **Wave** | `z = A·sin(k·x)·cos(k·y)` | Морская рябь 🌊 |
| **Paraboloid** | `z = A·(x²+y²)` | Чаша 🥣 |
| **Saddle** | `z = A·(x²−y²)` | Седло 🐴 |
| **Ripple** | `z = A·sin(k·r)` | Круги на воде 💧 |
| **Gaussian** | `z = A·exp(−(x²+y²)/σ²)` | Гора 🏔️ |

---

## 🎮 Как работать с 3D

| Действие | Как |
|---|---|
| Вращать объект | Средняя кнопка мышки |
| Приблизить | Scroll вверх |
| Отдалить | Scroll вниз |
| Менять параметры | Amplitude/Frequency ползунки (справа) |
| Рендер | F12 |
| Вид сверху | Numpad 7 |
| Исходный вид | Numpad 0 |

---

## 📊 Что внутри

**Расширенная версия методички (по главам):**

- `docs/01_введение_и_актуальность.md`
- `docs/02_теория_функции_поверхности.md`
- `docs/03_план_методички.md`
- `docs/04_реализация_blender.md`
- `docs/05_эксперименты.md`
- `docs/06_заключение.md`
- `docs/07_pathfinding_on_surface.md`
- `docs/metodichka/полная_методичка.md`

## Рекомендуемый учебный маршрут

1. Теория и мотивация: `docs/01_theory.md` + `docs/02_stem_concept.md`.
2. Практика в Blender: `docs/03_blender_guide.md` и запуск скриптов из `scripts/`.
3. Эксперименты: `docs/04_experiments.md` (или `docs/05_эксперименты.md` для расширенной версии).
4. Прикладной модуль: `docs/07_pathfinding_on_surface.md`.
5. Оформление результата: `docs/05_report_template.md` + `docs/06_presentation_template.md`.

## Поиск пути на поверхности (A* / Dijkstra)

Пример без препятствий:

```bash
blender --background --python scripts/pathfinding/visualize_path_in_blender.py -- --function paraboloid --algorithm astar --start-x -4 --start-y -4 --goal-x 4 --goal-y 4 --output assets/renders/path_paraboloid_astar.png
```

Пример с препятствием:

```bash
blender --background --python scripts/pathfinding/visualize_path_in_blender.py -- --function wave --algorithm dijkstra --obstacle-circle 0,0,1.5 --start-x -4 --start-y -4 --goal-x 4 --goal-y 4 --output assets/renders/path_wave_obstacle_dijkstra.png
```

## Тесты (без Blender)

Если установлен Python:

```powershell
python -m unittest discover -s tests
```

## Лицензия

Материалы предназначены для образовательного использования. Допускается свободная адаптация с указанием источника.
