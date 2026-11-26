import subprocess
import sys
from pathlib import Path

import pytest

from atslang import __version__


@pytest.mark.parametrize("flag", ["--yardim", "--help", "-h"])
def test_help(run_cli, flag):
    result = run_cli(flag)
    assert result.code == 0
    assert "Kullanım:" in result.stdout
    assert "--yardim" in result.stdout


def test_help_in_english_shows_english_names(run_cli):
    result = run_cli("--help", "--dil", "en")
    assert "Usage:" in result.stdout
    assert "--help" in result.stdout and "--yardim" not in result.stdout


@pytest.mark.parametrize("flag", ["--surum", "--version", "-v"])
def test_version(run_cli, flag):
    result = run_cli(flag)
    assert (result.code, result.stdout) == (0, f"ATSLang {__version__}\n")


def test_no_arguments_shows_usage_and_exits_2(run_cli):
    result = run_cli()
    assert result.code == 2
    assert "Kullanım:" in result.stderr
    assert result.stdout == ""


def test_runs_program(run_cli, write_ats):
    result = run_cli(str(write_ats('yaz("Merhaba dünya")')))
    assert (result.code, result.stdout, result.stderr) == (0, "Merhaba dünya\n", "")


def test_program_error_exits_1(run_cli, write_ats):
    result = run_cli(str(write_ats("yaz(")))
    assert result.code == 1
    assert "hata[ATS102]" in result.stderr


@pytest.mark.parametrize("args", [["--dil", "en"], ["--lang", "en"], ["--dil=en"], ["--lang=EN"]])
def test_language_option(run_cli, write_ats, args):
    result = run_cli(*args, str(write_ats("yaz(")))
    assert "error[ATS102]: unclosed parenthesis" in result.stderr


def test_options_may_follow_the_file(run_cli, write_ats):
    result = run_cli(str(write_ats("yaz(")), "--dil", "en")
    assert "error[ATS102]" in result.stderr


def test_env_language(run_cli, write_ats):
    result = run_cli(str(write_ats("yaz(")), env={"ATS_DIL": "en"})
    assert "error[ATS102]" in result.stderr


@pytest.mark.parametrize("args, message", [
    (["--dil", "de", "a.atslang"], "geçersiz dil: 'de'"),
    (["--dil"], "--dil seçeneği bir değer ister"),
    (["--dil", "--help"], "--dil seçeneği bir değer ister"),
    (["--bilinmeyen"], "bilinmeyen seçenek: --bilinmeyen"),
    (["a.atslang", "b.atslang"], "fazladan argüman: b.atslang"),
    (["yok.atslang"], "dosya bulunamadı: yok.atslang"),
])
def test_usage_errors_exit_2(run_cli, args, message):
    result = run_cli(*args)
    assert result.code == 2
    assert message in result.stderr
    assert "yardım için: ats --yardim" in result.stderr


def test_directory_is_not_a_file(run_cli, tmp_path):
    result = run_cli(str(tmp_path))
    assert result.code == 2
    assert "bir dosya değil" in result.stderr


def test_non_ats_extension_warns_but_runs(run_cli, write_ats):
    result = run_cli(str(write_ats('yaz("a")', name="betik")))
    assert (result.code, result.stdout) == (0, "a\n")
    assert "uyarı:" in result.stderr and ".atslang değil" in result.stderr


def test_first_run_prompt_through_cli(run_cli, write_ats, tmp_path):
    settings = tmp_path / "ayar" / "ayarlar.json"
    program = str(write_ats("yaz("))
    first = run_cli(program, settings=settings, interactive=True, answers=["en"])
    assert "error[ATS102]" in first.stderr
    assert len(first.prompts) == 1
    second = run_cli(program, settings=settings, interactive=True, answers=["tr"])
    assert "error[ATS102]" in second.stderr
    assert second.prompts == []


def test_no_prompt_without_terminal(run_cli, write_ats):
    result = run_cli(str(write_ats('yaz("a")')), interactive=False, answers=["en"])
    assert result.prompts == []


def test_real_process_with_redirected_output(tmp_path):
    """End to end: `python -m atslang` with pipes (no terminal) writes UTF-8."""
    program = tmp_path / "p.atslang"
    program.write_text('yaz("Merhaba dünya: şğıüöç")', encoding="utf-8")
    src = Path(__file__).parent.parent / "src"
    env = {"PYTHONPATH": str(src), "HOME": str(tmp_path), "APPDATA": str(tmp_path),
           "SYSTEMROOT": __import__("os").environ.get("SYSTEMROOT", "")}
    completed = subprocess.run([sys.executable, "-m", "atslang", str(program)],
                               capture_output=True, env=env, stdin=subprocess.DEVNULL)
    assert completed.returncode == 0
    assert completed.stdout == "Merhaba dünya: şğıüöç\n".encode("utf-8")
    assert completed.stderr == b""
    assert not (tmp_path / ".config").exists(), "no prompt or settings file without a terminal"


def test_ctrl_c_stops_program(run_cli, write_ats, monkeypatch):
    import atslang.cli

    def interrupted(source, out, inp=None, seed=None):
        out.write("yarım\n")
        raise KeyboardInterrupt

    monkeypatch.setattr(atslang.cli, "run_source", interrupted)
    result = run_cli(str(write_ats("iken dogru { }")))
    assert result.code == 130
    assert result.stdout == "yarım\n"
    assert "program durduruldu" in result.stderr


@pytest.mark.parametrize("flag", [["--tohum", "7"], ["--seed=7"]])
def test_seed_makes_random_repeatable(run_cli, write_ats, flag):
    program = str(write_ats("yaz(rastgele(1, 1000000))"))
    first = run_cli(*flag, program)
    second = run_cli(*flag, program)
    assert first.code == 0 and first.stdout == second.stdout


def test_invalid_seed(run_cli):
    result = run_cli("--tohum", "abc", "a.atslang")
    assert result.code == 2
    assert "--tohum seçeneği bir tam sayı ister" in result.stderr
