#!/usr/bin/env python3
"""Local public-release sanitation scan for this derivative repo."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path, PurePosixPath

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ASIA[0-9A-Z]{16}"),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"ghp_[A-Za-z0-9_]+"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"BEGIN (RSA|DSA|EC|OPENSSH|PRIVATE) KEY"),
]

PRIVATE_PATTERNS = [
    re.compile("/home/" + "gage"),
    re.compile("/mnt/" + "c", re.IGNORECASE),
    re.compile("C:" + r"\\Users", re.IGNORECASE),
    re.compile("GBM_" + "Main"),
    re.compile("Dissertation_" + "Main"),
    re.compile("Paper_" + "Two"),
    re.compile("ad" + "visor", re.IGNORECASE),
    re.compile("ref" + "eree", re.IGNORECASE),
    re.compile("conf" + "idential", re.IGNORECASE),
]

BLOCKED_ROOT_DIRS = {"handoff", "runs", "snapshots", "spectrum_data"}
BLOCKED_PATHS = {PurePosixPath("docs/archive")}
SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
    "build",
    "dist",
    "site",
}
SKIP_FILE_NAMES = {".coverage", "coverage.xml"}
BLOCKED_SUFFIXES = {".gif", ".gz", ".jpeg", ".jpg", ".mp4", ".pdf", ".png", ".tar", ".tgz", ".zip"}
MAX_FILE_BYTES = 1_000_000
MANIFEST_PATH = PurePosixPath("docs/release_file_manifest.txt")
TEXT_SUFFIXES = {
    ".cff",
    ".cfg",
    ".csv",
    ".gitignore",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".sh",
    ".svg",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}


def _skip_dir(name: str) -> bool:
    return name in SKIP_DIR_NAMES or name.endswith(".egg-info")


def _rel_posix(path: Path, root: Path) -> PurePosixPath:
    return PurePosixPath(path.relative_to(root).as_posix())


def iter_files(root: Path):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not _skip_dir(d)]
        current = Path(dirpath)
        for name in filenames:
            if name in SKIP_FILE_NAMES:
                continue
            yield current / name


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in TEXT_SUFFIXES or path.name in {"LICENSE", "Makefile"}


def _load_expected_manifest(root: Path) -> set[PurePosixPath]:
    path = root / MANIFEST_PATH
    if not path.exists():
        return set()
    expected: set[PurePosixPath] = set()
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        expected.add(PurePosixPath(line))
    return expected


def _check_expected_manifest(root: Path, actual_files: set[PurePosixPath], findings: list[str]) -> None:
    expected = _load_expected_manifest(root)
    if not expected:
        findings.append(f"missing expected release manifest: {MANIFEST_PATH}")
        return
    missing = sorted(expected - actual_files)
    unexpected = sorted(actual_files - expected)
    for path in missing:
        findings.append(f"manifest-listed file missing: {path}")
    for path in unexpected:
        findings.append(f"file not listed in release manifest: {path}")


def _check_blocked_paths(root: Path, actual_files: set[PurePosixPath], findings: list[str]) -> None:
    for dirname in sorted(BLOCKED_ROOT_DIRS):
        if (root / dirname).exists():
            findings.append(f"blocked directory present: {dirname}")
    for blocked in sorted(BLOCKED_PATHS):
        if (root / blocked).exists():
            findings.append(f"blocked path present: {blocked}")
    for rel in sorted(actual_files):
        if any(part in BLOCKED_ROOT_DIRS for part in rel.parts):
            findings.append(f"file under blocked directory: {rel}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan for public-release blockers.")
    parser.add_argument("root", nargs="?", default=".", help="Repository root to scan.")
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    findings: list[str] = []
    actual_files = {_rel_posix(path, root) for path in iter_files(root)}
    _check_expected_manifest(root, actual_files, findings)
    _check_blocked_paths(root, actual_files, findings)

    for path in iter_files(root):
        rel = _rel_posix(path, root)
        try:
            size = path.stat().st_size
        except OSError as exc:
            findings.append(f"could not stat {rel}: {exc}")
            continue
        if size > MAX_FILE_BYTES:
            findings.append(f"large file over {MAX_FILE_BYTES} bytes: {rel} ({size} bytes)")
        if path.suffix.lower() in BLOCKED_SUFFIXES:
            findings.append(f"blocked binary/archive suffix: {rel}")
        if not is_text_candidate(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"non-utf8 text candidate: {rel}")
            continue
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"secret-like pattern {pattern.pattern!r} in {rel}")
        for pattern in PRIVATE_PATTERNS:
            if pattern.search(text):
                findings.append(f"private/sensitive token {pattern.pattern!r} in {rel}")

    if findings:
        print("sanitization scan failed:")
        for item in findings:
            print(f"- {item}")
        return 1
    print(f"sanitization scan passed ({len(actual_files)} manifest files checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
