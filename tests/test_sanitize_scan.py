from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


class SanitizeScanTests(unittest.TestCase):
    def test_release_manifest_and_sanitization_scan_pass(self) -> None:
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, "scripts/sanitize_scan.py", "."],
            cwd=root,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        self.assertEqual(result.returncode, 0, result.stdout)


if __name__ == "__main__":
    unittest.main()
