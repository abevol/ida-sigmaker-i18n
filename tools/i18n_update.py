#!/usr/bin/env python3
"""Extract _() strings from sigmaker source, update .pot, merge .po, compile .mo."""
from __future__ import annotations

import ast
import argparse
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE_DIR = os.path.join(PROJECT_ROOT, "src", "sigmaker", "locale")
SOURCE_FILE = os.path.join(PROJECT_ROOT, "src", "sigmaker", "__init__.py")
DOMAIN = "sigmaker"


def extract_strings() -> list[str]:
    """Walk AST of __init__.py, find all _("...") calls, return sorted unique strings."""
    with open(SOURCE_FILE, encoding="utf-8") as f:
        tree = ast.parse(f.read())
    strings: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_":
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    strings.append(arg.value)
    return sorted(set(strings))


def write_pot(strings: list[str]) -> str:
    """Write .pot file, return its path."""
    os.makedirs(LOCALE_DIR, exist_ok=True)
    pot_path = os.path.join(LOCALE_DIR, f"{DOMAIN}.pot")
    with open(pot_path, "w", encoding="utf-8") as f:
        f.write(
            '# Sigmaker translations\n'
            '# Copyright (C) 2026 Mahmoud Abdelkader\n'
            '# This file is distributed under the MIT license.\n'
            '#\n'
            '# FIRST AUTHOR <EMAIL@ADDRESS>, 2026.\n'
            '#\n'
            'msgid ""\n'
            'msgstr ""\n'
            '"Project-Id-Version: sigmaker 1.11.0\\n"\n'
            '"Content-Type: text/plain; charset=UTF-8\\n"\n'
            '"Content-Transfer-Encoding: 8bit\\n"\n'
            '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n'
            '\n'
        )
        for s in strings:
            f.write(f'msgid "{_escape(s)}"\nmsgstr ""\n\n')
    return pot_path


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def init_language(lang: str) -> None:
    """Create .po from .pot for a new language."""
    pot = os.path.join(LOCALE_DIR, f"{DOMAIN}.pot")
    po_dir = os.path.join(LOCALE_DIR, lang, "LC_MESSAGES")
    os.makedirs(po_dir, exist_ok=True)
    po_path = os.path.join(po_dir, f"{DOMAIN}.po")
    if os.path.exists(po_path):
        subprocess.run(["msgmerge", "--update", po_path, pot], check=True)
    else:
        subprocess.run(["msginit", "--no-translator", "-i", pot, "-o", po_path, "-l", lang], check=True)


def compile_po(lang: str) -> None:
    """Compile .po -> .mo."""
    po_dir = os.path.join(LOCALE_DIR, lang, "LC_MESSAGES")
    po_path = os.path.join(po_dir, f"{DOMAIN}.po")
    mo_path = os.path.join(po_dir, f"{DOMAIN}.mo")
    subprocess.run(["msgfmt", po_path, "-o", mo_path], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sigmaker i18n update tool")
    parser.add_argument("--init", metavar="LANG", help="Initialize a new language (e.g. zh_CN)")
    parser.add_argument("--compile", action="store_true", help="Only compile .po -> .mo")
    args = parser.parse_args()

    if args.compile:
        for lang in os.listdir(LOCALE_DIR):
            po = os.path.join(LOCALE_DIR, lang, "LC_MESSAGES", f"{DOMAIN}.po")
            if os.path.exists(po):
                compile_po(lang)
        print("Compiled all .mo files")
        return

    if args.init:
        strings = extract_strings()
        write_pot(strings)
        init_language(args.init)
        print(f"Initialized {args.init}")
        return

    strings = extract_strings()
    pot_path = write_pot(strings)
    print(f"Wrote {pot_path} ({len(strings)} strings)")

    for lang in os.listdir(LOCALE_DIR):
        po = os.path.join(LOCALE_DIR, lang, "LC_MESSAGES", f"{DOMAIN}.po")
        if os.path.exists(po):
            subprocess.run(["msgmerge", "--update", po, pot_path], check=True)
            compile_po(lang)
            print(f"Updated {lang}")


if __name__ == "__main__":
    main()
