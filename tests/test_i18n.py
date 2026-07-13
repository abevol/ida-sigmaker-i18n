# tests/test_i18n.py
from __future__ import annotations

import os
import sys
import tempfile
import unittest.mock

# sigmaker/__init__.py imports idaapi/idc (IDA Pro modules).
# Mock them before importing any sigmaker submodule outside of IDA.
sys.modules["idaapi"] = unittest.mock.MagicMock()
sys.modules["idc"] = unittest.mock.MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def test_i18n_imports():
    from sigmaker import i18n
    assert hasattr(i18n, "_")
    assert callable(i18n._)


def test_translation_loaded():
    """With .mo present, t() returns English fallback for untranslated keys."""
    from sigmaker import i18n
    lang = i18n.get_language()
    # All keys fall back to _EN (English) when .mo has empty msgstr
    assert i18n.t("ok") == "OK"
    assert i18n.t("cancel") == "Cancel"
    assert i18n.t("form.main.select_action") == "Select action"
    # Unknown keys return the key itself
    assert i18n.t("nonexistent_key") == "nonexistent_key"


def test_get_language_returns_string():
    from sigmaker import i18n
    lang = i18n.get_language()
    assert isinstance(lang, str)
    assert lang in ("en", "zh_CN")
