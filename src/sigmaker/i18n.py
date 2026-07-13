import locale
import gettext
import os

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")

_language: str = "en"


def _detect_language() -> str:
    try:
        lang, _ = locale.getdefaultlocale()
    except (ValueError, TypeError):
        return "en"
    if not lang:
        return "en"
    code = lang.split("_")[0]
    if code == "en":
        return "en"
    return lang


_language = _detect_language()

try:
    _trans = gettext.translation(
        "sigmaker", _LOCALE_DIR, languages=[_language], fallback=True
    )
except FileNotFoundError:
    _trans = gettext.NullTranslations()

_ = _trans.gettext


def get_language() -> str:
    return _language
