# Скрипты проекта

В этой папке находятся Python-скрипты для визуализации математических поверхностей в Blender.

## Файлы

| Файл | Назначение |
|---|---|
| `visualize_function.py` | Быстрый запуск поверхности `z = f(x, y)` и цветовая карта по высоте |
| `generate_surface_mesh.py` | Генерация mesh-поверхности с выбором предустановленных функций |
| `setup_geometry_nodes_surface.py` | Автоматическая настройка Geometry Nodes для волновой поверхности |

## Запуск в Blender (рекомендуется)

1. Откройте Blender.
2. Перейдите в Workspace **Scripting**.
3. Нажмите **Open** и выберите нужный скрипт из папки `scripts/`.
4. Нажмите **Run Script** (или `Alt+P`).

## Запуск из командной строки

```powershell
"C:\Program Files\Blender Foundation\Blender 4.x\blender.exe" --background --python scripts\visualize_function.py
"C:\Program Files\Blender Foundation\Blender 4.x\blender.exe" --background --python scripts\generate_surface_mesh.py
"C:\Program Files\Blender Foundation\Blender 4.x\blender.exe" --background --python scripts\setup_geometry_nodes_surface.py
```

Для `visualize_function.py` поддерживается рендер в PNG:

```powershell
"C:\Program Files\Blender Foundation\Blender 4.x\blender.exe" --background --python scripts\visualize_function.py -- --output renders\surface.png
```

## Запуск без Blender

- `visualize_function.py` и `generate_surface_mesh.py` в обычном Python печатают preview значений функции.
- `setup_geometry_nodes_surface.py` вне Blender выводит подсказку и завершает работу без ошибки.

## Что менять в первую очередь

1. `visualize_function.py` -> функция `surface_function(x, y)`.
2. `generate_surface_mesh.py` -> параметры `FUNCTION_NAME`, `AMPLITUDE`, `FREQUENCY`, `SIGMA`, `RESOLUTION`.
3. `setup_geometry_nodes_surface.py` -> `DEFAULT_AMPLITUDE`, `DEFAULT_FREQUENCY`, `GRID_SUBDIVISIONS`.
