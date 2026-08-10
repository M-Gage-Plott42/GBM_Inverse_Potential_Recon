from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.sanitize_scan import is_text_candidate


class SanitizeScanTests(unittest.TestCase):
    def test_container_control_files_are_text_candidates(self) -> None:
        self.assertTrue(is_text_candidate(Path("Dockerfile")))
        self.assertTrue(is_text_candidate(Path(".dockerignore")))

    def test_container_control_file_contents_are_scanned(self) -> None:
        scanner = Path(__file__).resolve().parents[1] / "scripts" / "sanitize_scan.py"
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            (root / "docs").mkdir()
            (root / "Dockerfile").write_text(
                "ENV EXAMPLE=" + "ghp_" + "not_a_real_credential\n",
                encoding="utf-8",
            )
            (root / ".dockerignore").write_text(
                "# " + "/home/" + "gage\n",
                encoding="utf-8",
            )
            (root / "docs" / "release_file_manifest.txt").write_text(
                ".dockerignore\nDockerfile\ndocs/release_file_manifest.txt\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(scanner), str(root)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("Dockerfile", result.stdout)
        self.assertIn(".dockerignore", result.stdout)

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
