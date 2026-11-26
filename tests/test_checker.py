from atslang.checker import suggest_name

from conftest import error_of


def test_unknown_function_with_suggestion():
    err = error_of('Yaz("a")')
    assert (err.code, err.hint, err.params["suggestion"]) == ("ATS201", "did_you_mean", "yaz")


def test_unknown_function_without_suggestion():
    err = error_of('yazdir("a")')
    assert (err.code, err.hint) == ("ATS201", None)


def test_suggestions():
    assert suggest_name("YAZ") == "yaz"
    assert suggest_name("yz") == "yaz"
    assert suggest_name("yazz") == "yaz"
    assert suggest_name("ab") is None


def test_wrong_argument_count():
    err = error_of("yaz()")
    assert err.code == "ATS202"
    assert (err.params["expected"], err.params["given"]) == (1, 0)
    assert error_of('yaz("a", "b")').params["given"] == 2


def test_check_runs_before_anything_executes():
    # The first line is valid, but the program must not run at all.
    assert error_of('yaz("a")\nbilinmeyen("b")').code == "ATS201"
