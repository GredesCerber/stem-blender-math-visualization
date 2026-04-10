# AI Agent Execution Plan (Опциональные задачи)

> **Статус:** Проект 92% готов, classroom-ready.  
> Основная функциональность **COMPLETE**. Ниже — опциональные улучшения.

---

## 📋 Предварительное условие

Перед тем как работать здесь, прочитайте:
1. `docs/ai-agent/AI_AGENT_HANDOFF.md` — текущий статус
2. `GETTING_STARTED.md` — что работает

**Текущее состояние:**
- ✅ 5 готовых .blend файлов (Wave, Paraboloid, Saddle, Ripple, Gaussian)
- ✅ Все баги исправлены (startup cube, 3D камеры)
- ✅ Python скрипты: function_library.py, enhanced_camera_utils.py, все визуализаторы
- ✅ Методичка: 1200 строк, 8 глав, практические сценарии

---

## 🎯 Опциональные задачи (prioritized)

### Task 1: Скриншоты в методичке 📸
**Приоритет:** MEDIUM  
**Сложность:** ⭐ (низкая - 1-2 часа)  
**Файл:** `docs/методичка_подробная.md`

```markdown
# Что делать:
1. Откройте любой .blend файл (например FunctionVisualizer_Wave.blend)
2. Найдите в методичке все строки с "📸 СКРИНШОТ"
3. Сделайте скриншоты Blender UI в указанных местах
4. Сохраните скриншоты в docs/screenshots/
5. Вставьте ссылки ![Alttext](path/to/screenshot.png) в методичку
```

**Примеры локаций:**
- Node Graph в Shader Editor (когда обсуждаем colormap)
- Modifier Properties с ползунками Amplitude/Frequency
- 3D Viewport с готовой волной
- Render Image (F12) - результат рендера

**Как запустить:** Просто откройте любой файл `FunctionVisualizer_*.blend` в Blender.

---

### Task 2: Student Workbook (рабочий лист) 📝
**Приоритет:** LOW  
**Сложность:** ⭐⭐ (средняя - 2-3 часа)  
**Создать:** `docs/student_exercises.md`

```markdown
# Структура рабочего листа:

## Part 1: Теория (10 вопросов)
- Что такое функция z = f(x, y)?
- Какая разница между волной и рябью?
- Почему амплитуда влияет на высоту?
- Как частота меняет кол-во периодов?
- Что такое градиент функции?
[... еще 5 вопросов]

## Part 2: Практика (5 упражнений)
- Упражнение 1: Откройте Wave.blend, поиграйте с ползунками, нарисуйте график
- Упражнение 2: Сравните волну и рябь для одинаковой амплитуды
- Упражнение 3: Найдите такую частоту, где волна имеет 4 полных периода
- Упражнение 4: Исследуйте парболоид, отметьте его экстремум
- Упражнение 5: Воспроизведите примеры из методички с разными параметрами

## Part 3: Проекты (3 задачи)
- Проект 1: Создать свою функцию и визуализировать её
- Проект 2: Исследовать семейство функций (например тройная волна)
- Проект 3: Применить A*/Dijkstra pathfinding на поверхности
```

**Как запустить:** Создайте файл `docs/student_exercises.md` с контентом выше.

---

### Task 3: Export to PDF/DOCX 📄
**Приоритет:** LOW  
**Сложность:** ⭐ (низкая - 1 час)  
**Инструмент:** pandoc или python-docx

```bash
# Вариант 1: pandoc (если установлен)
pandoc GETTING_STARTED.md -o GETTING_STARTED.pdf --pdf-engine=xelatex -V mainfont="Arial"

# Вариант 2: python-docx (если нужен .docx)
python scripts/export_to_docx.py GETTING_STARTED.md
```

**Файлы для экспорта:**
1. `GETTING_STARTED.md` → `GETTING_STARTED.pdf` (для печати на уроке)
2. `docs/методичка_подробная.md` → `методичка.pdf` (раздать студентам)
3. Создать `docs/student_exercises.md` → `student_exercises.pdf` (раздаточный материал)

---

### Task 4: Эталонные рендеры для assets/ 🖼️
**Приоритет:** LOW  
**Сложность:** ⭐ (низкая - 2 часа, но требует ручного запуска Blender)  
**Результат:** примеры в папке `assets/renders/`

```bash
# Запустить для каждой функции:
cd scripts

# Wave с разными параметрами
blender FunctionVisualizer_Wave.blend -b -P visualize_function.py -- --output ../assets/renders/wave_A2_k2.png
blender FunctionVisualizer_Wave.blend -b -P visualize_function.py -- --output ../assets/renders/wave_A4_k5.png
blender FunctionVisualizer_Wave.blend -b -P visualize_function.py -- --output ../assets/renders/wave_A1_k3.png

# Paraboloid
blender FunctionVisualizer_Paraboloid.blend -b -P visualize_function.py -- --output ../assets/renders/paraboloid_A1.png
blender FunctionVisualizer_Paraboloid.blend -b -P visualize_function.py -- --output ../assets/renders/paraboloid_A3.png

# Gaussian
blender FunctionVisualizer_Gaussian.blend -b -P visualize_function.py -- --output ../assets/renders/gaussian_sigma1.png
blender FunctionVisualizer_Gaussian.blend -b -P visualize_function.py -- --output ../assets/renders/gaussian_sigma2.png

# Ripple  
blender FunctionVisualizer_Ripple.blend -b -P visualize_function.py -- --output ../assets/renders/ripple_A2_k3.png

# Saddle
blender FunctionVisualizer_Saddle.blend -b -P visualize_function.py -- --output ../assets/renders/saddle_A2.png
```

**Результат:** Папка `assets/renders/` будет содержать 10-15 красивых примеров для презентаций.

---

## ✅ Complete Checklist (перед тем как закончить)

После выполнения ЛЮБОЙ из задач выше, проверьте:

- [ ] Файлы добавлены в правильное место
- [ ] Ссылки в документации обновлены
- [ ] Нет синтаксических ошибок (markdown/python)
- [ ] Если скриншоты - они читаемые (min 1024px ширина)
- [ ] Если код - протестирован хотя бы один раз
- [ ] Git status - нет случайных файлов (~$*.docx, .pyc, __pycache__)

---

## 🚫 НЕ ДЕЛАЙТЕ этого

```
❌ Не переписывайте основной функционал (он работает!)
❌ Не меняйте названия .blend файлов
❌ Не удаляйте enhanced_camera_utils.py (камеры сломаются)
❌ Не добавляйте новые математические функции (scope creep)
❌ Не переводите GETTING_STARTED.md на другой язык (сейчас жёсткий минимум)
```

---

## 📞 Помощь по каждой задаче

**Если ошибка при export to PDF:**
→ Используйте online pandoc converter (pandoc.org/try/) или просто оставьте markdown

**Если рендер не работает:**
→ Используйте full path к Blender из Task 4 выше, или откройте .blend вручную + F12

**Если скриншот недостаточно хорош:**
→ Используйте Blender's screenshot tool (Shift+F3) или встроенный выбор окна (Alt+PrintScreen)

**Если затрудняетесь придумать упражнения:**
→ Используйте примеры из `docs/методичка_подробная.md` главы 5-7

---

## ⏱️ Примерный таймлайн

| Задача | Время | Сложность |
|---|---|---|
| Screenshots | 1-2 часа | ⭐ |
| Student Workbook | 2-3 часа | ⭐⭐ |
| Export to PDF | 0.5-1 час | ⭐ |
| Render examples | 2 часа | ⭐ |
| **Total** | **5-8 часов** | **⭐ avg** |

**But project is COMPLETE without these tasks!**

## 3. Эксперименты и доказательная база

1. Прогони серии экспериментов (амплитуда, частота, тип функции, разрешение).
2. Заполни таблицы реальными значениями:
   - `docs/04_experiments.md`
   - `docs/05_эксперименты.md` (если ведёшь расширенную версию)
3. Подготовь рендеры в `assets/renders/`:
   - `paraboloid_default.png`
   - `wave_A1_k1.png`
   - `wave_A2_k3.png`
   - `saddle_default.png`
   - `gaussian_sigma2.png`
   - и т.д.

**Выход:** экспериментальные разделы больше не шаблон, а реальный отчёт.

---

## 4. Документация и синхронизация

Проверить и синхронизировать:

1. Число скриптов (везде должно быть 3).
2. Команды запуска (одинаковые в README и docs).
3. Список артефактов (наличие `.blend`, `.docx`, рендеров).
4. Ссылки между разделами и файлами.

Рекомендуемые правки:
- добавить «сценарий урока 45 минут»;
- добавить «FAQ преподавателя»;
- добавить «типичные ошибки студента и быстрые фиксы».

---

## 5. DOCX и финальная упаковка

1. Канонический DOCX методички: `docs/metodichka/Методичка.docx`.
2. Убедиться, что нет markdown-артефактов (`**`) в тексте DOCX.
3. Проверить шаблон отчёта:
   - `docs/STEM_отчет_шаблон_под_скриншоты.docx`.

---

## 6. Финальная валидация перед релизом

1. Пройти `docs/ai-agent/AI_AGENT_ACCEPTANCE_CHECKLIST.md`.
2. Если все пункты зелёные:
   - сделать коммит(ы),
   - синхронизировать ветку (`pull --rebase`, затем `push`),
   - подготовить краткий changelog.

---

## 7. Формат итогового отчёта ИИ

ИИ должен вернуть:

1. Что сделано (по фазам 0–6).
2. Какие файлы изменены и зачем.
3. Какие риски остались.
4. Что можно сделать в следующей итерации (не более 5 пунктов).

---

## 8. Расширение проекта: путь/оптимизация на 3D-поверхности

### 8.1 Цель
Перейти от «визуализации» к «решению прикладной задачи»:
поиск оптимального пути по поверхности `z = f(x,y)`.

### 8.2 Минимальная реализация (MVP)

1. Построить сеточный граф поверхности:
   - вершины = точки сетки;
   - рёбра = соседние точки;
   - вес ребра = расстояние + штраф за уклон.
2. Реализовать A* и Dijkstra.
3. Добавить выбор старта/финиша.
4. В Blender визуализировать маршрут как линию (Curve).

### 8.3 Полезные формулы стоимости

- Базовая длина ребра: `sqrt((dx)^2 + (dy)^2 + (dz)^2)`.
- Штраф уклона: `alpha * abs(dz / sqrt(dx^2 + dy^2))`.
- Общая стоимость: `w_len * length + w_slope * slope_penalty + w_risk * risk_penalty`.

### 8.4 Результаты, которые должны появиться в репозитории

1. Код модулей pathfinding.
2. Короткий гайд в docs (как запускать поиск пути).
3. Набор примеров:
   - простой путь на параболоиде,
   - путь с препятствиями,
   - сравнение A* и Dijkstra.
4. Скриншоты/рендеры маршрутов в `assets/renders/`.

