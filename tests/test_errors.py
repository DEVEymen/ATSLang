import string

import pytest

from atslang import messages
from atslang.errors import render_error

from conftest import error_of


def test_render_matches_spec_example():
    err = error_of('yaz("once")\nyaz("x")\nyaz("Merhaba)')
    err.source = err.source.__class__("merhaba.atslang", err.source.text)
    assert render_error(err, "tr") == (
        "hata[ATS003]: metin kapatılmamış\n"
        "  --> merhaba.atslang:3:5\n"
        "   |\n"
        ' 3 | yaz("Merhaba)\n'
        "   |     ^ metin burada başlıyor\n"
        '   = öneri: metnin sonuna " ekleyin'
    )


def test_render_in_english():
    rendered = render_error(error_of('yaz("abc'), "en")
    assert rendered.startswith("error[ATS003]: unterminated string")
    assert "= hint:" in rendered


def test_caret_aligns_with_tabs():
    rendered = render_error(error_of('\tYaz("a")'), "tr")
    assert "   | \t^ bu ad tanımlı değil" in rendered


def test_gutter_grows_with_line_number():
    rendered = render_error(error_of("\n" * 9 + "yaz()"), "tr")
    assert "   --> test.atslang:10:1" in rendered
    assert " 10 | yaz()" in rendered
    assert "    | ^" in rendered


def test_token_descriptions_are_translated():
    err = error_of('yaz "a"')
    assert "beklenmeyen metin" in render_error(err, "tr")
    assert "unexpected string" in render_error(err, "en")


def _fields(template: str) -> set[str]:
    return {name for _, name, _, _ in string.Formatter().parse(template) if name}


@pytest.mark.parametrize("lang", messages.LANGUAGES)
def test_every_code_has_a_message_in_every_language(lang):
    assert set(messages.CODES[lang]) == set(messages.ERROR_CODES)


@pytest.mark.parametrize("table", ["CODES", "HINTS", "TOKENS", "UI"])
def test_languages_have_same_keys_and_placeholders(table):
    tr, en = getattr(messages, table)["tr"], getattr(messages, table)["en"]
    assert set(tr) == set(en)
    for key in tr:
        if isinstance(tr[key], dict):
            assert set(tr[key]) == set(en[key]), key
            for part in tr[key]:
                assert _fields(tr[key][part]) == _fields(en[key][part]), (key, part)
        else:
            assert _fields(tr[key]) == _fields(en[key]), key
