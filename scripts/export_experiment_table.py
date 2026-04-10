"""
export_experiment_table.py
==========================
Генерация таблиц экспериментов (CSV/Markdown) из набора пресетов.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from function_library import SurfaceConfig, generate_surface_grid

DEFAULT_PRESETS: list[dict[str, Any]] = [
    {"name": "wave_A0.5_k1", "function": "wave", "resolution": 60, "amplitude": 0.5, "frequency": 1.0, "sigma": 2.0},
    {"name": "wave_A1_k1", "function": "wave", "resolution": 60, "amplitude": 1.0, "frequency": 1.0, "sigma": 2.0},
    {"name": "wave_A2_k1", "function": "wave", "resolution": 60, "amplitude": 2.0, "frequency": 1.0, "sigma": 2.0},
    {"name": "wave_A2_k3", "function": "wave", "resolution": 60, "amplitude": 2.0, "frequency": 3.0, "sigma": 2.0},
    {"name": "saddle_default", "function": "saddle", "resolution": 60, "amplitude": 1.0, "frequency": 1.0, "sigma": 2.0},
    {"name": "paraboloid_default", "function": "paraboloid", "resolution": 60, "amplitude": 1.0, "frequency": 1.0, "sigma": 2.0},
    {"name": "gaussian_sigma2", "function": "gaussian", "resolution": 60, "amplitude": 1.0, "frequency": 1.0, "sigma": 2.0},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Экспорт сводной таблицы экспериментов.")
    parser.add_argument("--manifest", default=None, help="JSON-манифест пресетов.")
    parser.add_argument("--output-csv", default=r"assets\renders\experiment_table.csv")
    parser.add_argument("--output-md", default=r"assets\renders\experiment_table.md")
    return parser.parse_args()


def load_presets(manifest: str | None) -> list[dict[str, Any]]:
    if manifest is None:
        return list(DEFAULT_PRESETS)
    with open(manifest, "r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, list):
        raise ValueError("manifest должен быть JSON-массивом.")
    return [dict(item) for item in raw]


def estimate_min_max(config: SurfaceConfig) -> tuple[float, float]:
    _, _, z_grid = generate_surface_grid(config)
    z_flat = [z for row in z_grid for z in row]
    return (min(z_flat), max(z_flat))


def build_rows(presets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for preset in presets:
        config = SurfaceConfig(
            function=str(preset["function"]),
            resolution=int(preset.get("resolution", 60)),
            x_min=float(preset.get("x_min", -5.0)),
            x_max=float(preset.get("x_max", 5.0)),
            y_min=float(preset.get("y_min", -5.0)),
            y_max=float(preset.get("y_max", 5.0)),
            amplitude=float(preset.get("amplitude", 1.0)),
            frequency=float(preset.get("frequency", 1.0)),
            sigma=float(preset.get("sigma", 2.0)),
        )
        z_min, z_max = estimate_min_max(config)
        rows.append(
            {
                "name": preset["name"],
                "function": config.function,
                "resolution": config.resolution,
                "amplitude": config.amplitude,
                "frequency": config.frequency,
                "sigma": config.sigma,
                "z_min": f"{z_min:.4f}",
                "z_max": f"{z_max:.4f}",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "name",
                "function",
                "resolution",
                "amplitude",
                "frequency",
                "sigma",
                "z_min",
                "z_max",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_markdown(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Сводная таблица экспериментов",
        "",
        "| Пресет | Функция | Resolution | A | k | sigma | z_min | z_max |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            "| {name} | {function} | {resolution} | {amplitude} | {frequency} | {sigma} | {z_min} | {z_max} |".format(
                **row
            )
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    presets = load_presets(args.manifest)
    rows = build_rows(presets)
    output_csv = Path(args.output_csv)
    output_md = Path(args.output_md)
    write_csv(output_csv, rows)
    write_markdown(output_md, rows)
    print(f"[DONE] CSV: {output_csv}")
    print(f"[DONE] MD: {output_md}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(2)
