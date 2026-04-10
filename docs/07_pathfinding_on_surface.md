# Глава 7. Поиск пути на 3D-поверхности `z = f(x, y)`

> *Следующий шаг после визуализации формы — решение прикладной задачи на этой форме.*

---

## 7.1 Постановка задачи

Нужно найти маршрут от точки старта до точки финиша по поверхности.  
Поверхность задаётся функцией `z = f(x, y)`, а путь ищется не в плоскости, а по 3D-рельефу.

### Что учитывает стоимость шага

1. Длина ребра в 3D:
   `length = sqrt(dx^2 + dy^2 + dz^2)`
2. Штраф за уклон:
   `slope_penalty = alpha * abs(dz / sqrt(dx^2 + dy^2))`
3. Общая стоимость:
   `cost = w_len * length + w_slope * slope_penalty + w_risk * risk_penalty`

---

## 7.2 Реализация в проекте

Модули расположены в `scripts/pathfinding/`:

- `terrain_graph.py` — дискретизация поверхности в граф (узлы/рёбра, препятствия, риск);
- `cost_functions.py` — функции стоимости и веса;
- `search.py` — алгоритмы A* и Dijkstra;
- `visualize_path_in_blender.py` — расчёт маршрута и визуализация Curve в Blender.

---

## 7.3 Базовый запуск

```powershell
blender --background --python scripts\pathfinding\visualize_path_in_blender.py -- --function paraboloid --algorithm astar --resolution 80 --start-x -4 --start-y -4 --goal-x 4 --goal-y 4 --output assets\renders\path_paraboloid_astar.png
```

Что получится:

- создаётся поверхность;
- строится маршрут как Curve-объект поверх поверхности;
- при `--output` сохраняется PNG.

---

## 7.4 Пример с препятствием

Круговое препятствие в центре:

```powershell
blender --background --python scripts\pathfinding\visualize_path_in_blender.py -- --function wave --algorithm dijkstra --resolution 90 --amplitude 1.5 --frequency 2.0 --obstacle-circle 0,0,1.5 --start-x -4 --start-y -4 --goal-x 4 --goal-y 4 --output assets\renders\path_wave_obstacle_dijkstra.png
```

Дополнительно можно блокировать слишком высокие области:

```powershell
blender --background --python scripts\pathfinding\visualize_path_in_blender.py -- --function gaussian --blocked-z-gt 0.7 --start-x -4 --start-y 0 --goal-x 4 --goal-y 0
```

---

## 7.5 Сравнение A* и Dijkstra

- **Dijkstra**: всегда ищет кратчайший путь, но чаще посещает больше узлов.
- **A\***: использует эвристику расстояния до цели, поэтому обычно быстрее на больших сетках.

Рекомендация для урока:

1. Сначала показать Dijkstra как «эталон полного поиска».
2. Затем показать A* и сравнить число посещённых узлов в логах.
3. Обсудить, почему эвристика ускоряет поиск.

---

## 7.6 Типичные сценарии применения в STEM

1. «Маршрут дрона» с ограничением по уклону.
2. «Безопасный путь» с обходом опасной зоны (obstacle-circle).
3. «Сравнение алгоритмов» по стоимости пути и числу проверок.

---

## 7.7 Мини-практикум для студентов

1. Постройте путь на `paraboloid` без препятствий.
2. Добавьте препятствие `--obstacle-circle 0,0,1.2` и сравните маршрут.
3. Повторите оба сценария для `--algorithm dijkstra` и `--algorithm astar`.
4. Сформулируйте вывод: где A* даёт преимущество и почему.
