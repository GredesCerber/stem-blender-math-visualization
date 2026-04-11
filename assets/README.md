# assets

Эта папка предназначена для хранения скриншотов, рендеров и других визуальных материалов проекта.

## Структура

```
assets/
├── renders/        ← рендеры 3D-поверхностей из Blender
├── screenshots/    ← скриншоты интерфейса Blender (для методички)
└── diagrams/       ← схемы Geometry Nodes, диаграммы алгоритмов
```

## Как добавить скриншот

1. Создайте поверхность в Blender (инструкция в `docs/metodichka/методичка_подробная.md`, глава 4).
2. Нажмите F12 для рендера.
3. В окне рендера: Image → Save As → сохраните в папку `assets/renders/`.
4. Называйте файлы описательно, например:
   - `paraboloid_default.png`
   - `wave_A1_k2.png`
   - `saddle_vs_paraboloid.png`

## Уже подготовленные материалы

В `assets/renders/` добавлены готовые PNG для экспериментов (амплитуда, частота, сравнение функций), включая:

- `paraboloid_default.png`, `paraboloid_A05.png`, `paraboloid_A2.png`
- `wave_A1_k1.png`, `wave_A2_k3.png`, `wave_A1_k0_5.png`, `wave_A1_k8.png`
- `saddle_default.png`, `ripple_k1.png`, `gaussian_sigma2.png`

Также там лежат `render_manifest.csv` и `render_manifest.json` с перечнем файлов.
