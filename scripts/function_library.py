"""
function_library.py
===================
Единый слой математических функций, параметров и CLI-аргументов
для скриптов STEM-визуализации поверхностей.

Пример запуска через Blender:
blender --background --python scripts/visualize_function.py -- --function wave --resolution 80 --output assets/renders/wave.png
"""

from __future__ import annotations

import argparse
import math
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass

SurfaceFormula = Callable[[float, float, "SurfaceConfig"], float]
GridIndex = tuple[int, int]

DEFAULT_X_MIN = -5.0
DEFAULT_X_MAX = 5.0
DEFAULT_Y_MIN = -5.0
DEFAULT_Y_MAX = 5.0
DEFAULT_RESOLUTION = 60
DEFAULT_AMPLITUDE = 1.0
DEFAULT_FREQUENCY = 1.0
DEFAULT_SIGMA = 2.0
DEFAULT_FUNCTION = "wave"


@dataclass(frozen=True, slots=True)
class SurfaceConfig:
    function: str = DEFAULT_FUNCTION
    resolution: int = DEFAULT_RESOLUTION
    x_min: float = DEFAULT_X_MIN
    x_max: float = DEFAULT_X_MAX
    y_min: float = DEFAULT_Y_MIN
    y_max: float = DEFAULT_Y_MAX
    amplitude: float = DEFAULT_AMPLITUDE
    frequency: float = DEFAULT_FREQUENCY
    sigma: float = DEFAULT_SIGMA

    @property
    def x_span(self) -> float:
        return self.x_max - self.x_min

    @property
    def y_span(self) -> float:
        return self.y_max - self.y_min


def _paraboloid(x: float, y: float, config: SurfaceConfig) -> float:
    return config.amplitude * (x**2 + y**2)


def _saddle(x: float, y: float, config: SurfaceConfig) -> float:
    return config.amplitude * (x**2 - y**2)


def _wave(x: float, y: float, config: SurfaceConfig) -> float:
    k = config.frequency
    return config.amplitude * math.sin(k * x) * math.cos(k * y)


def _ripple(x: float, y: float, config: SurfaceConfig) -> float:
    radius = math.sqrt(x**2 + y**2)
    return config.amplitude * math.sin(config.frequency * radius)


def _gaussian(x: float, y: float, config: SurfaceConfig) -> float:
    sigma_sq = config.sigma**2
    return config.amplitude * math.exp(-(x**2 + y**2) / sigma_sq)


def _custom(x: float, y: float, config: SurfaceConfig) -> float:
    k = config.frequency
    return config.amplitude * (math.sin(k * x) + math.cos(k * y))


FUNCTION_REGISTRY: dict[str, SurfaceFormula] = {
    "paraboloid": _paraboloid,
    "saddle": _saddle,
    "wave": _wave,
    "ripple": _ripple,
    "gaussian": _gaussian,
    "custom": _custom,
}

DEFAULT_PREVIEW_POINTS: tuple[tuple[float, float], ...] = (
    (-2.0, -2.0),
    (-1.0, 0.0),
    (0.0, 0.0),
    (1.0, 1.0),
    (2.0, 2.0),
)


def available_functions() -> tuple[str, ...]:
    return tuple(sorted(FUNCTION_REGISTRY))


def get_surface_function(name: str) -> SurfaceFormula:
    try:
        return FUNCTION_REGISTRY[name]
    except KeyError as exc:
        allowed = ", ".join(available_functions())
        raise ValueError(
            f"Неизвестная функция '{name}'. Допустимые значения: {allowed}."
        ) from exc


def validate_surface_config(config: SurfaceConfig) -> None:
    get_surface_function(config.function)

    if config.resolution < 2:
        raise ValueError("Параметр resolution должен быть >= 2.")
    if config.x_max <= config.x_min:
        raise ValueError("Параметр x_max должен быть больше x_min.")
    if config.y_max <= config.y_min:
        raise ValueError("Параметр y_max должен быть больше y_min.")
    if config.frequency < 0:
        raise ValueError("Параметр frequency должен быть >= 0.")
    if config.sigma <= 0:
        raise ValueError("Параметр sigma должен быть > 0.")

    finite_params = {
        "x_min": config.x_min,
        "x_max": config.x_max,
        "y_min": config.y_min,
        "y_max": config.y_max,
        "amplitude": config.amplitude,
        "frequency": config.frequency,
        "sigma": config.sigma,
    }
    for name, value in finite_params.items():
        if not math.isfinite(value):
            raise ValueError(f"Параметр {name} должен быть конечным числом.")


def evaluate_point(
    config: SurfaceConfig,
    x: float,
    y: float,
    *,
    surface_function: SurfaceFormula | None = None,
) -> float:
    formula = surface_function or get_surface_function(config.function)
    try:
        z = float(formula(x, y, config))
    except (ValueError, ZeroDivisionError, OverflowError) as exc:
        raise ValueError(
            f"Ошибка вычисления функции в точке (x={x:.4f}, y={y:.4f})."
        ) from exc

    if not math.isfinite(z):
        raise ValueError(
            f"Функция вернула некорректное значение z={z} "
            f"в точке (x={x:.4f}, y={y:.4f})."
        )
    return z


def generate_surface_geometry(
    config: SurfaceConfig,
) -> tuple[list[tuple[float, float, float]], list[tuple[int, int, int, int]]]:
    validate_surface_config(config)
    formula = get_surface_function(config.function)

    vertices: list[tuple[float, float, float]] = []
    step_x = config.x_span / config.resolution
    step_y = config.y_span / config.resolution

    for j in range(config.resolution + 1):
        y = config.y_min + j * step_y
        for i in range(config.resolution + 1):
            x = config.x_min + i * step_x
            z = evaluate_point(config, x, y, surface_function=formula)
            vertices.append((x, y, z))

    faces: list[tuple[int, int, int, int]] = []
    row_len = config.resolution + 1
    for j in range(config.resolution):
        for i in range(config.resolution):
            v0 = j * row_len + i
            v1 = v0 + 1
            v2 = v0 + row_len + 1
            v3 = v0 + row_len
            faces.append((v0, v1, v2, v3))

    return vertices, faces


def generate_surface_grid(
    config: SurfaceConfig,
) -> tuple[list[float], list[float], list[list[float]]]:
    validate_surface_config(config)
    formula = get_surface_function(config.function)

    step_x = config.x_span / config.resolution
    step_y = config.y_span / config.resolution
    x_values = [config.x_min + i * step_x for i in range(config.resolution + 1)]
    y_values = [config.y_min + j * step_y for j in range(config.resolution + 1)]

    z_grid: list[list[float]] = []
    for y in y_values:
        row: list[float] = []
        for x in x_values:
            row.append(evaluate_point(config, x, y, surface_function=formula))
        z_grid.append(row)

    return x_values, y_values, z_grid


def preview_values(
    config: SurfaceConfig,
    points: Iterable[tuple[float, float]] = DEFAULT_PREVIEW_POINTS,
) -> list[tuple[float, float, float]]:
    validate_surface_config(config)
    formula = get_surface_function(config.function)
    samples: list[tuple[float, float, float]] = []
    for x, y in points:
        samples.append((x, y, evaluate_point(config, x, y, surface_function=formula)))
    return samples


def extract_user_argv(raw_argv: list[str] | None = None) -> list[str]:
    source = list(sys.argv[1:] if raw_argv is None else raw_argv)
    if "--" in source:
        return source[source.index("--") + 1 :]
    return source


def build_common_parser(
    description: str,
    *,
    include_output: bool = False,
    default_function: str = DEFAULT_FUNCTION,
    default_resolution: int = DEFAULT_RESOLUTION,
) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--function",
        default=default_function,
        choices=available_functions(),
        help="Имя функции поверхности.",
    )
    parser.add_argument(
        "--resolution",
        type=int,
        default=default_resolution,
        help="Разрешение сетки по каждой оси (N -> N×N).",
    )
    parser.add_argument("--x-min", type=float, default=DEFAULT_X_MIN)
    parser.add_argument("--x-max", type=float, default=DEFAULT_X_MAX)
    parser.add_argument("--y-min", type=float, default=DEFAULT_Y_MIN)
    parser.add_argument("--y-max", type=float, default=DEFAULT_Y_MAX)
    parser.add_argument(
        "--amplitude",
        type=float,
        default=DEFAULT_AMPLITUDE,
        help="Амплитуда A.",
    )
    parser.add_argument(
        "--frequency",
        type=float,
        default=DEFAULT_FREQUENCY,
        help="Частота k.",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=DEFAULT_SIGMA,
        help="Параметр sigma для гауссовой функции.",
    )
    if include_output:
        parser.add_argument(
            "--output",
            "-o",
            default=None,
            help="Путь для PNG-рендера (работает только в Blender).",
        )
    return parser


def namespace_to_surface_config(namespace: argparse.Namespace) -> SurfaceConfig:
    return SurfaceConfig(
        function=namespace.function,
        resolution=namespace.resolution,
        x_min=namespace.x_min,
        x_max=namespace.x_max,
        y_min=namespace.y_min,
        y_max=namespace.y_max,
        amplitude=namespace.amplitude,
        frequency=namespace.frequency,
        sigma=namespace.sigma,
    )


def parse_common_cli_args(
    description: str,
    *,
    include_output: bool = False,
    default_function: str = DEFAULT_FUNCTION,
    default_resolution: int = DEFAULT_RESOLUTION,
    raw_argv: list[str] | None = None,
) -> tuple[SurfaceConfig, argparse.Namespace]:
    parser = build_common_parser(
        description,
        include_output=include_output,
        default_function=default_function,
        default_resolution=default_resolution,
    )
    namespace = parser.parse_args(extract_user_argv(raw_argv))
    config = namespace_to_surface_config(namespace)
    validate_surface_config(config)
    return config, namespace


def describe_surface_config(config: SurfaceConfig) -> str:
    return (
        f"function={config.function}, resolution={config.resolution}, "
        f"x=[{config.x_min}, {config.x_max}], y=[{config.y_min}, {config.y_max}], "
        f"A={config.amplitude}, k={config.frequency}, sigma={config.sigma}"
    )
