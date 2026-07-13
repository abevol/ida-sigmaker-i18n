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
    """With .mo present, _() returns the translated string for the detected locale."""
    from sigmaker import i18n
    lang = i18n.get_language()
    if lang == "zh_CN":
        assert i18n._("OK") == "确定"
        assert i18n._("Cancel") == "取消"
    else:
        assert i18n._("OK") == "OK"


def test_get_language_returns_string():
    from sigmaker import i18n
    lang = i18n.get_language()
    assert isinstance(lang, str)
    assert lang in ("en", "zh_CN")
