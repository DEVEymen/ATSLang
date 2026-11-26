"""Runs every program in tests/conformance (spec §10)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from atslang import messages

CASES = Path(__file__).parent / "conformance"
PROGRAMS = sorted(CASES.glob("*.atslang"))
EXPECTATION = re.compile(r"^(ATS\d{3}) (\d+):(\d+)$")


def test_every_program_has_an_expectation():
    assert PROGRAMS, "no conformance programs found"
    for program in PROGRAMS:
        assert program.with_suffix(".out").exists() or program.with_suffix(".err").exists(), \
            program.name


@pytest.mark.parametrize("program", PROGRAMS, ids=lambda p: p.stem)
def test_conformance(program: Path, run_cli):
    in_file = program.with_suffix(".in")
    stdin_text = in_file.read_bytes().decode("utf-8") if in_file.exists() else ""
    result = run_cli(str(program), "--dil", "tr", stdin_text=stdin_text)
    out_file = program.with_suffix(".out")
    err_file = program.with_suffix(".err")
    expected_out = out_file.read_bytes() if out_file.exists() else b""
    if not err_file.exists():
        assert result.stderr == ""
        assert result.code == 0
        assert result.stdout.encode("utf-8") == expected_out
    else:
        match = EXPECTATION.match(err_file.read_text(encoding="utf-8").strip())
        assert match, f"bad .err file for {program.name}"
        code, line, column = match.groups()
        assert result.code == 1
        # Static errors: nothing runs. Runtime errors: only the output
        # produced before the error (the .out file, if any).
        assert result.stdout.encode("utf-8") == expected_out
        assert f"hata[{code}]" in result.stderr
        assert f"{program}:{line}:{column}" in result.stderr


def test_every_error_code_is_covered():
    covered = set()
    for err in CASES.glob("*.err"):
        covered.add(err.read_text(encoding="utf-8").split()[0])
    covered.add("ATS901")  # needs a broken output stream; see test_interpreter.py
    assert covered == set(messages.ERROR_CODES)
