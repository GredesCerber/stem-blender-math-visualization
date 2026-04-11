r"""
batch_render.py
===============
Пакетный рендер набора пресетов через Blender CLI.

Пример:
python scripts\batch_render.py --blender-exe "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --output-dir assets\renders
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_PRESETS: list[dict[str, Any]] = [
    # Параболоид — разные амплитуды
    {"name": "paraboloid_default", "function": "paraboloid", "resolution": 80, "amplitude": 1.0, "frequency": 1.0, "sigma": 2.0},
    {"name": "paraboloid_A05",     "function": "paraboloid", "resolution": 80, "amplitude": 0.5, "frequency": 1.0, "sigma": 2.0},
    {"name": "paraboloid_A2",      "function": "paraboloid", "resolution": 80, "amplitude": 2.0, "frequency": 1.0, "sigma": 2.0},
    {"name": "paraboloid_A5",      "function": "paraboloid", "resolution": 80, "amplitude": 5.0, "frequency": 1.0, "sigma": 2.0},
    # Седло
    {"name": "saddle_default", "function": "saddle", "resolution": 90, "amplitude": 1.0, "frequency": 1.0, "sigma": 2.0},
    # Волна — эксперимент по амплитуде и частоте
    {"name": "wave_A0_2_k1", "function": "wave", "resolution": 100, "amplitude": 0.2, "frequency": 1.0, "sigma": 2.0},
    {"name": "wave_A0_5_k1", "function": "wave", "resolution": 100, "amplitude": 0.5, "frequency": 1.0, "sigma": 2.0},
    {"name": "wave_A1_k0_5", "function": "wave", "resolution": 100, "amplitude": 1.0, "frequency": 0.5, "sigma": 2.0},
    {"name": "wave_A1_k1",   "function": "wave", "resolution": 100, "amplitude": 1.0, "frequency": 1.0, "sigma": 2.0},
    {"name": "wave_A1_k2",   "function": "wave", "resolution": 100, "amplitude": 1.0, "frequency": 2.0, "sigma": 2.0},
    {"name": "wave_A1_k4",   "function": "wave", "resolution": 100, "amplitude": 1.0, "frequency": 4.0, "sigma": 2.0},
    {"name": "wave_A1_k8",   "function": "wave", "resolution": 100, "amplitude": 1.0, "frequency": 8.0, "sigma": 2.0},
    {"name": "wave_A2_k1",   "function": "wave", "resolution": 100, "amplitude": 2.0, "frequency": 1.0, "sigma": 2.0},
    {"name": "wave_A2_k3",   "function": "wave", "resolution": 100, "amplitude": 2.0, "frequency": 3.0, "sigma": 2.0},
    {"name": "wave_A3_k5",   "function": "wave", "resolution": 100, "amplitude": 3.0, "frequency": 5.0, "sigma": 2.0},
    {"name": "wave_A5_k1",   "function": "wave", "resolution": 100, "amplitude": 5.0, "frequency": 1.0, "sigma": 2.0},
    # Рябь
    {"name": "ripple_k1", "function": "ripple", "resolution": 100, "amplitude": 1.0, "frequency": 1.0, "sigma": 2.0},
    {"name": "ripple_k3", "function": "ripple", "resolution": 100, "amplitude": 1.0, "frequency": 3.0, "sigma": 2.0},
    # Гауссиана — эксперимент по σ
    {"name": "gaussian_sigma0_32", "function": "gaussian", "resolution": 100, "amplitude": 1.0, "frequency": 1.0, "sigma": 0.32},
    {"name": "gaussian_sigma0_58", "function": "gaussian", "resolution": 100, "amplitude": 1.0, "frequency": 1.0, "sigma": 0.58},
    {"name": "gaussian_sigma1",    "function": "gaussian", "resolution": 100, "amplitude": 1.0, "frequency": 1.0, "sigma": 1.0},
    {"name": "gaussian_sigma1_41", "function": "gaussian", "resolution": 100, "amplitude": 1.0, "frequency": 1.0, "sigma": 1.41},
    {"name": "gaussian_sigma2",    "function": "gaussian", "resolution": 100, "amplitude": 1.0, "frequency": 1.0, "sigma": 2.0},
    {"name": "gaussian_sigma3_16", "function": "gaussian", "resolution": 100, "amplitude": 1.0, "frequency": 1.0, "sigma": 3.16},
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Пакетный рендер поверхностей через Blender.")
    parser.add_argument("--blender-exe", default="blender", help="Путь к blender.exe.")
    parser.add_argument("--output-dir", default=r"assets\renders", help="Каталог PNG-файлов.")
    parser.add_argument("--manifest", default=None, help="JSON с пресетами.")
    parser.add_argument("--metadata-json", default=None, help="Куда сохранить JSON-отчёт.")
    parser.add_argument("--metadata-csv", default=None, help="Куда сохранить CSV-отчёт.")
    parser.add_argument("--dry-run", action="store_true", help="Только вывести команды без запуска.")
    return parser.parse_args()


def load_presets(manifest_path: str | None) -> list[dict[str, Any]]:
    if manifest_path is None:
        return list(DEFAULT_PRESETS)
    with open(manifest_path, "r", encoding="utf-8") as handle:
        raw = json.load(handle)
    if not isinstance(raw, list):
        raise ValueError("manifest должен содержать JSON-массив пресетов.")
    return [dict(item) for item in raw]


def build_command(
    blender_exe: str,
    *,
    script_path: Path,
    output_file: Path,
    preset: dict[str, Any],
) -> list[str]:
    return [
        blender_exe,
        "--background",
        "--python",
        str(script_path),
        "--",
        "--function",
        str(preset["function"]),
        "--resolution",
        str(preset["resolution"]),
        "--x-min",
        str(preset.get("x_min", -5.0)),
        "--x-max",
        str(preset.get("x_max", 5.0)),
        "--y-min",
        str(preset.get("y_min", -5.0)),
        "--y-max",
        str(preset.get("y_max", 5.0)),
        "--amplitude",
        str(preset["amplitude"]),
        "--frequency",
        str(preset["frequency"]),
        "--sigma",
        str(preset["sigma"]),
        "--output",
        str(output_file),
    ]


def ensure_keys(preset: dict[str, Any], index: int) -> None:
    required = {"name", "function", "resolution", "amplitude", "frequency", "sigma"}
    missing = required - set(preset)
    if missing:
        missing_str = ", ".join(sorted(missing))
        raise ValueError(f"Пресет #{index} не содержит поля: {missing_str}.")


def write_metadata_csv(path: Path, rows: list[dict[str, Any]]) -> None:
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
                "output",
                "status",
                "return_code",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    args = parse_args()
    presets = load_presets(args.manifest)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    script_path = Path(__file__).with_name("visualize_function.py")
    blender_exists = shutil.which(args.blender_exe) is not None
    if not blender_exists and not args.dry_run:
        raise ValueError(
            f"Blender не найден по пути/алиасу '{args.blender_exe}'. "
            "Используйте --blender-exe с корректным путем."
        )

    metadata: list[dict[str, Any]] = []
    for idx, preset in enumerate(presets, start=1):
        ensure_keys(preset, idx)
        output_file = output_dir / f"{preset['name']}.png"
        command = build_command(
            args.blender_exe,
            script_path=script_path,
            output_file=output_file,
            preset=preset,
        )

        if args.dry_run:
            print("[DRY-RUN]", " ".join(command))
            status = "dry_run"
            return_code = 0
        else:
            print("[RUN]", " ".join(command))
            completed = subprocess.run(command, check=False)
            status = "ok" if completed.returncode == 0 else "failed"
            return_code = completed.returncode

        metadata.append(
            {
                "name": preset["name"],
                "function": preset["function"],
                "resolution": preset["resolution"],
                "amplitude": preset["amplitude"],
                "frequency": preset["frequency"],
                "sigma": preset["sigma"],
                "output": str(output_file),
                "status": status,
                "return_code": return_code,
            }
        )

    metadata_json = Path(args.metadata_json) if args.metadata_json else output_dir / "render_manifest.json"
    metadata_csv = Path(args.metadata_csv) if args.metadata_csv else output_dir / "render_manifest.csv"

    metadata_json.parent.mkdir(parents=True, exist_ok=True)
    with metadata_json.open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, ensure_ascii=False, indent=2)
    write_metadata_csv(metadata_csv, metadata)

    print(f"[DONE] Пресетов обработано: {len(metadata)}")
    print(f"[DONE] JSON: {metadata_json}")
    print(f"[DONE] CSV: {metadata_csv}")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        raise SystemExit(2)
