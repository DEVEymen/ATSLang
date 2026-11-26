import io

from atslang.cli import main
from atslang.repl import CONTINUATION, PROMPT, Repl


def session(*lines, inp=""):
    """Run the REPL over the given input lines; return (stdout, stderr, prompts)."""
    pending = list(lines)
    prompts = []

    def read(prompt):
        prompts.append(prompt)
        if not pending:
            raise EOFError
        line = pending.pop(0)
        if isinstance(line, BaseException):
            raise line
        return line

    out, err = io.StringIO(), io.StringIO()
    code = Repl(read, out, err, "tr", io.StringIO(inp)).run()
    assert code == 0
    banner_end = out.getvalue().index("\n", out.getvalue().index("Çıkmak")) + 1
    return out.getvalue()[banner_end:], err.getvalue(), prompts


def test_expressions_show_their_value():
    out, err, _ = session("1 + 2", '"a" + "b"', "[1, \"x\"]", "dogru", "3 / 2")
    assert out == '3\n"ab"\n[1, "x"]\ndogru\n1.5\n\n'
    assert err == ""


def test_state_is_kept_between_inputs():
    out, _, _ = session("var x = 5", "x = x + 1", "x * 2")
    assert out == "12\n\n"


def test_yaz_prints_text_without_quotes():
    out, _, _ = session('yaz("merhaba")')
    assert out == "merhaba\n\n"


def test_calls_with_values_are_shown_and_others_are_not():
    out, _, _ = session("fonksiyon kare(n) { dondur n * n }", "kare(4)", "var l = []",
                        "ekle(l, 1)", "l", 'buyuk("ılık")')
    assert out == '16\n[1]\n"ILIK"\n\n'


def test_multi_line_input():
    out, _, prompts = session("eger dogru {", '    yaz("içeride")', "}", "var l = [1,", "2]", "l")
    assert out == "içeride\n[1, 2]\n\n"
    assert prompts.count(CONTINUATION) == 3


def test_empty_line_ends_an_unfinished_input_with_an_error():
    out, err, _ = session("eger dogru {", "", "1")
    assert "hata[ATS106]" in err
    assert out.endswith("1\n\n")


def test_errors_are_shown_and_the_session_continues():
    out, err, _ = session("yaz(tanimsiz)", "1 / 0", "7")
    assert "hata[ATS203]" in err and "hata[ATS302]" in err
    assert "<girdi>:1:" in err
    assert out == "7\n\n"


def test_failed_check_does_not_keep_half_an_input():
    _, err, _ = session("var a = 1; var a = 2", "var a = 3", "a")
    assert err.count("hata[ATS204]") == 1  # the second `var a` is fine: nothing was kept


def test_runtime_error_forgets_names_that_were_never_created():
    out, err, _ = session("var a = 1; yaz(1 / 0); var b = 2", "a", "yaz(b)", "var b = 3", "b")
    assert "hata[ATS302]" in err and "hata[ATS203]" in err
    assert out == "1\n3\n\n"


def test_runtime_error_inside_function_and_block_leaves_clean_state():
    out, err, _ = session("fonksiyon f() { var ic = 1; dondur 1 / 0 }", "f()",
                          "eger dogru { var k = 1; yaz(1 / 0) }", "var k = 2", "k")
    assert err.count("hata[ATS302]") == 2
    assert out == "2\n\n"


def test_cikis_quits():
    out, _, prompts = session("cikis", "1")
    assert prompts == [PROMPT]
    assert out == ""


def test_ctrl_c_on_input_line_continues():
    out, _, _ = session(KeyboardInterrupt(), "5")
    assert out == "\n5\n\n"


def test_oku_reads_from_input():
    out, _, _ = session('var ad = oku("Ad: ")', '"Merhaba " + ad', inp="Ali\n")
    assert out == 'Ad: "Merhaba Ali"\n\n'


def test_cli_opens_repl_in_a_terminal(tmp_path):
    out, err = io.StringIO(), io.StringIO()
    lines = iter(["1 + 1"])

    def read(prompt):
        try:
            return next(lines)
        except StopIteration:
            raise EOFError from None

    code = main([], stdin=io.StringIO(), stdout=out, stderr=err, env={"ATS_DIL": "tr"},
                settings=tmp_path / "s.json", interactive=True, read=read)
    assert code == 0
    assert "etkileşimli mod" in out.getvalue() and "2\n" in out.getvalue()


def test_cli_repl_flag_without_terminal(tmp_path):
    out = io.StringIO()
    code = main(["--repl"], stdin=io.StringIO("var x = 2\nx * 21\n"), stdout=out,
                stderr=io.StringIO(), env={}, settings=tmp_path / "s.json", interactive=False)
    assert code == 0
    assert "42\n" in out.getvalue()
