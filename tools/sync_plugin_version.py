#!/usr/bin/env python3
"""Keep ``ida-plugin.json``'s version in sync with the latest git tag.

The single source of truth for the version is the latest ``v*`` git tag;
``setuptools-scm`` derives the package version from it at build time. The IDA
Plugin Repository and ``hcli`` read the version out of ``ida-plugin.json``,
so the two must agree. This script copies the git tag version into the
manifest.

Usage:
    python tools/sync_plugin_version.py            # write the manifest in place
    python tools/sync_plugin_version.py --check     # exit 1 if out of sync, no write

The pre-commit hook in ``.githooks/`` runs the writing form; CI acts as the
backstop.
"""
import argparse
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "ida-plugin.json"


def git_tag_version() -> str:
    """Return the latest ``v*`` tag, or ``\"0.0.0\"`` if none exists."""
    try:
        tag = subprocess.run(
            ["git", "describe", "--tags", "--match", "v*", "--abbrev=0"],
            capture_output=True, text=True, cwd=ROOT, check=True,
        ).stdout.strip()
        return tag.lstrip("v")
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "0.0.0"


def manifest_version(text: str) -> str:
    return json.loads(text)["plugin"]["version"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the manifest matches the git tag; do not write",
    )
    args = parser.parse_args(argv)

    version = git_tag_version()
    text = MANIFEST.read_text(encoding="utf-8")
    current = manifest_version(text)

    if current == version:
        return 0

    if args.check:
        print(
            f"ida-plugin.json version {current!r} != git tag version "
            f"{version!r}; run: python tools/sync_plugin_version.py",
            file=sys.stderr,
        )
        return 1

    new_text, n = re.subn(
        r'("version"\s*:\s*")[^"]*(")', r"\g<1>" + version + r"\g<2>", text, count=1
    )
    if n != 1:
        raise SystemExit("could not locate the version field in ida-plugin.json")
    MANIFEST.write_text(new_text, encoding="utf-8")
    print(f"synced ida-plugin.json version {current} -> {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
