"""
cost_functions.py
=================
Функции стоимости для перемещения по 3D-поверхности.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

Point3D = tuple[float, float, float]


@dataclass(frozen=True, slots=True)
class CostWeights:
    w_len: float = 1.0
    w_slope: float = 1.0
    w_risk: float = 0.0
    alpha: float = 1.0

    def validate(self) -> None:
        values = {
            "w_len": self.w_len,
            "w_slope": self.w_slope,
            "w_risk": self.w_risk,
            "alpha": self.alpha,
        }
        for name, value in values.items():
            if not math.isfinite(value):
                raise ValueError(f"Вес {name} должен быть конечным числом.")
            if value < 0:
                raise ValueError(f"Вес {name} должен быть >= 0.")


def edge_length_3d(a: Point3D, b: Point3D) -> float:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    return math.sqrt(dx * dx + dy * dy + dz * dz)


def horizontal_length(a: Point3D, b: Point3D) -> float:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    return math.sqrt(dx * dx + dy * dy)


def slope_penalty(a: Point3D, b: Point3D, *, alpha: float = 1.0) -> float:
    horizontal = horizontal_length(a, b)
    if horizontal <= 1e-12:
        return 0.0
    dz = b[2] - a[2]
    return alpha * abs(dz / horizontal)


def composite_edge_cost(
    a: Point3D,
    b: Point3D,
    *,
    weights: CostWeights,
    risk_penalty: float = 0.0,
) -> float:
    weights.validate()
    if not math.isfinite(risk_penalty):
        raise ValueError("risk_penalty должен быть конечным числом.")
    if risk_penalty < 0:
        raise ValueError("risk_penalty должен быть >= 0.")

    length = edge_length_3d(a, b)
    slope = slope_penalty(a, b, alpha=weights.alpha)
    return (
        weights.w_len * length
        + weights.w_slope * slope
        + weights.w_risk * risk_penalty
    )
