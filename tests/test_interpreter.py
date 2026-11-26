import io

import pytest

from atslang.errors import ATSError
from atslang.interpreter import run_source
from atslang.source import SourceFile

from conftest import run_text


def test_yaz_adds_newline():
    assert run_text('yaz("Merhaba")') == "Merhaba\n"


def test_statements_run_in_order():
    assert run_text('yaz("1. satir")\nyaz("2. satir"); yaz("3")') == "1. satir\n2. satir\n3\n"


def test_empty_program_prints_nothing():
    assert run_text("") == ""


class BrokenStream(io.StringIO):
    def write(self, s: str) -> int:
        raise BrokenPipeError(32, "Broken pipe")


def test_output_failure_is_ats901():
    with pytest.raises(ATSError) as info:
        run_source(SourceFile.from_text("t.atslang", 'yaz("a")'), BrokenStream())
    assert info.value.code == "ATS901"
    assert info.value.params["reason"] == "Broken pipe"


def test_ats901_through_cli(write_ats, tmp_path):
    from atslang.cli import main

    err = io.StringIO()
    code = main(
        [str(write_ats('yaz("a")'))],
        stdin=io.StringIO(), stdout=BrokenStream(), stderr=err,
        env={}, settings=tmp_path / "s.json", interactive=False,
    )
    assert code == 1
    assert "hata[ATS901]" in err.getvalue()


# -- 0.2 ------------------------------------------------------------------
from conftest import error_of  # noqa: E402


def runtime_error(text):
    with pytest.raises(ATSError) as info:
        run_text(text)
    return info.value


def test_variables_and_reassignment():
    assert run_text("var x = 1\nx = x + 1\nx = x * 10\nyaz(x)") == "20\n"


def test_ondalik_variable_widens_integers():
    assert run_text("var o: ondalik = 1\no = o + 1\nyaz(o)") == "2.0\n"


def test_untyped_variable_may_change_type():
    assert run_text('var x = 1\nx = "bir"\nyaz(x)') == "bir\n"


def test_int_and_float_mix():
    assert run_text("yaz(1 + 0.5)\nyaz(2 * 1.5)") == "1.5\n3.0\n"


def test_float_overflow_is_ats303():
    program = "var b = 10.0\nb = b * b\nb = b * b\nb = b * b\nb = b * b\nb = b * b\nb = b * b\nb = b * b\nb = b * b\nb = b * b\nyaz(b)"
    assert runtime_error(program).code == "ATS303"


def test_tam_of_huge_float_is_ats303():
    assert runtime_error("var b = 10.0 * 10.0\nb = b * b * b * b * b * b * b * b * b * b\nyaz(tam(b))").code == "ATS303"


@pytest.mark.parametrize("text", ["1e5", " 5", "", "5.", "inf", "nan", "1,5"])
def test_ondalik_rejects_non_plain_numbers(text):
    assert runtime_error(f'yaz(ondalik("{text}"))').code == "ATS305"


def test_conversion_accepts_signs():
    assert run_text('yaz(tam("-12") + tam("+3"))\nyaz(ondalik("-0.5"))') == "-9\n-0.5\n"


def test_long_value_is_shortened_in_message():
    err = runtime_error('yaz(tam("' + "x" * 100 + '"))')
    assert err.params["value"].endswith("...") and len(err.params["value"]) == 30


def test_runtime_error_keeps_earlier_output():
    out = io.StringIO()
    with pytest.raises(ATSError):
        run_source(SourceFile.from_text("t.atslang", 'yaz("a")\nyaz(1 / 0)\nyaz("b")'), out)
    assert out.getvalue() == "a\n"


def test_static_errors_are_found_before_running():
    assert error_of('yaz("a")\nyaz(tanimsiz)').code == "ATS203"
