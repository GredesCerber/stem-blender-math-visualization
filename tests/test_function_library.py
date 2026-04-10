from __future__ import annotations

import os
import sys
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
SCRIPTS_DIR = os.path.abspath(SCRIPTS_DIR)
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from function_library import (  # noqa: E402
    SurfaceConfig,
    available_functions,
    generate_surface_geometry,
    preview_values,
    validate_surface_config,
)


class FunctionLibraryTests(unittest.TestCase):
    def test_registry_contains_expected_functions(self) -> None:
        expected = {"paraboloid", "saddle", "wave", "ripple", "gaussian", "custom"}
        self.assertTrue(expected.issubset(set(available_functions())))

    def test_generate_surface_geometry_counts(self) -> None:
        config = SurfaceConfig(function="wave", resolution=10)
        vertices, faces = generate_surface_geometry(config)
        self.assertEqual(len(vertices), 121)
        self.assertEqual(len(faces), 100)

    def test_validate_rejects_invalid_resolution(self) -> None:
        with self.assertRaises(ValueError):
            validate_surface_config(SurfaceConfig(function="wave", resolution=1))

    def test_validate_rejects_invalid_sigma(self) -> None:
        with self.assertRaises(ValueError):
            validate_surface_config(SurfaceConfig(function="gaussian", sigma=0))

    def test_preview_values_returns_finite(self) -> None:
        config = SurfaceConfig(function="paraboloid", resolution=20)
        preview = preview_values(config)
        self.assertGreaterEqual(len(preview), 3)
        for _, _, z in preview:
            self.assertTrue(z == z)  # not NaN


if __name__ == "__main__":
    unittest.main()
