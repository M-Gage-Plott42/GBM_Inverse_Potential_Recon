#!/usr/bin/env python3
"""Run the deterministic harmonic-oscillator public smoke example."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gbm_inverse_potential import harmonic_oscillator_demo


if __name__ == "__main__":
    print(json.dumps(harmonic_oscillator_demo(), indent=2, sort_keys=True))
