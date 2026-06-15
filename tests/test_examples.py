from __future__ import annotations

import json
import math
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ExampleScriptTests(unittest.TestCase):
    def test_moment_series_example_emits_json_metrics(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "examples/moment_series_comparison.py",
                "--json",
                "--q-max",
                "1.5",
                "--q-points",
                "5",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertLess(payload["max_abs_error"], 1.0e-6)

    def test_alpha_sweep_example_emits_json_metrics(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "examples/alpha_sweep_smoke.py",
                "--json",
                "--alphas",
                "1.0",
                "--r-points",
                "120",
                "--q-points",
                "1000",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload), 1)
        self.assertTrue(math.isfinite(payload[0]["density_l2_rel"]))


if __name__ == "__main__":
    unittest.main()
