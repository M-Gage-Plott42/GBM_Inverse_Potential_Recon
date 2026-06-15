from __future__ import annotations

import contextlib
import io
import json
import unittest

from gbm_inverse_potential import cli


class CliTests(unittest.TestCase):
    def test_cli_json_output(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = cli.main(["--json", "--r-points", "120", "--q-points", "1000"])
        self.assertEqual(result, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(payload["r_points"], 120)
        self.assertEqual(payload["q_points"], 1000)

    def test_cli_text_output(self) -> None:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = cli.main(["--r-points", "120", "--q-points", "1000"])
        self.assertEqual(result, 0)
        self.assertIn("GBM inverse-potential harmonic-oscillator smoke demo", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
