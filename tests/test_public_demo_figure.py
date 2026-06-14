from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "reproduce_public_demo_figure.py"


class PublicDemoFigureTests(unittest.TestCase):
    def test_demo_figure_writes_svg_to_stdout(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertTrue(result.stdout.startswith("<svg"))
        self.assertIn("Analytic reduced density", result.stdout)
        self.assertIn("Reconstructed density", result.stdout)

    def test_demo_figure_writes_svg_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = Path(tmpdir) / "gbm_public_demo_density.svg"
            subprocess.run(
                [sys.executable, str(SCRIPT), "--output", str(output)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            text = output.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("<svg"))
        self.assertIn("Public harmonic-oscillator", text)


if __name__ == "__main__":
    unittest.main()
