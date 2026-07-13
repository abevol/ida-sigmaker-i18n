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


def test_gettext_identity_for_missing_translation():
    """When no .mo exists, _() returns the msgid unchanged."""
    from sigmaker import i18n
    assert i18n._("OK") == "OK"
    assert i18n._("Cancel") == "Cancel"


def test_get_language_returns_string():
    from sigmaker import i18n
    lang = i18n.get_language()
    assert isinstance(lang, str)
    assert lang in ("en", "zh_CN")
