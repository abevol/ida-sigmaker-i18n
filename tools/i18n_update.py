#!/usr/bin/env python3
"""Manage translation files from the _EN key dictionary."""
from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCALE_DIR = os.path.join(PROJECT_ROOT, "src", "sigmaker", "locale")
I18N_MODULE = os.path.join(PROJECT_ROOT, "src", "sigmaker", "i18n.py")
DOMAIN = "sigmaker"


def _load_en() -> dict[str, str]:
    spec = importlib.util.spec_from_file_location("sigmaker.i18n", I18N_MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod._EN


def _escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def write_pot(keys: list[str], en: dict[str, str]) -> str:
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
            '"Project-Id-Version: sigmaker 1.12.0\\n"\n'
            '"Content-Type: text/plain; charset=UTF-8\\n"\n'
            '"Content-Transfer-Encoding: 8bit\\n"\n'
            '"Plural-Forms: nplurals=2; plural=(n != 1);\\n"\n'
            '\n'
        )
        for k in keys:
            f.write(f'# {_escape(en[k])}\n')
            f.write(f'msgid "{k}"\n')
            f.write(f'msgstr ""\n\n')
    return pot_path


def init_language(lang: str) -> None:
    pot = os.path.join(LOCALE_DIR, f"{DOMAIN}.pot")
    po_dir = os.path.join(LOCALE_DIR, lang, "LC_MESSAGES")
    os.makedirs(po_dir, exist_ok=True)
    po_path = os.path.join(po_dir, f"{DOMAIN}.po")
    if os.path.exists(po_path):
        subprocess.run(["msgmerge", "--update", po_path, pot], check=True)
    else:
        subprocess.run(["msginit", "--no-translator", "-i", pot, "-o", po_path, "-l", lang], check=True)


def compile_po(lang: str) -> None:
    po_dir = os.path.join(LOCALE_DIR, lang, "LC_MESSAGES")
    po_path = os.path.join(po_dir, f"{DOMAIN}.po")
    mo_path = os.path.join(po_dir, f"{DOMAIN}.mo")
    subprocess.run(["msgfmt", po_path, "-o", mo_path], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sigmaker i18n update tool")
    parser.add_argument("--init", metavar="LANG", help="Initialize a new language (e.g. zh_CN)")
    parser.add_argument("--compile", action="store_true", help="Only compile .po -> .mo")
    args = parser.parse_args()

    en = _load_en()
    keys = sorted(en)

    if args.compile:
        for lang in os.listdir(LOCALE_DIR):
            po = os.path.join(LOCALE_DIR, lang, "LC_MESSAGES", f"{DOMAIN}.po")
            if os.path.exists(po):
                compile_po(lang)
        print("Compiled all .mo files")
        return

    write_pot(keys, en)
    pot_path = os.path.join(LOCALE_DIR, f"{DOMAIN}.pot")
    print(f"Wrote {pot_path} ({len(keys)} keys)")

    if args.init:
        init_language(args.init)
        print(f"Initialized {args.init}")
        return

    for lang in os.listdir(LOCALE_DIR):
        po = os.path.join(LOCALE_DIR, lang, "LC_MESSAGES", f"{DOMAIN}.po")
        if os.path.exists(po):
            subprocess.run(["msgmerge", "--update", po, pot_path], check=True)
            compile_po(lang)
            print(f"Updated {lang}")


if __name__ == "__main__":
    main()
