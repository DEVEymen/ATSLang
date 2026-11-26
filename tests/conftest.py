from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path

import pytest

from atslang.cli import main
from atslang.errors import ATSError
from atslang.interpreter import compile_source, run_source
from atslang.source import SourceFile


@dataclass
class Result:
    code: int
    stdout: str
    stderr: str


@pytest.fixture
def run_cli(tmp_path: Path):
    """Run ``ats`` in isolation: no real env, settings file or terminal."""

    def _run(*argv: str, env: dict[str, str] | None = None, settings: Path | None = None,
             interactive: bool = False, answers: list[str] | None = None,
             stdin_text: str = "") -> Result:
        out, err = io.StringIO(), io.StringIO()
        pending = list(answers or [])
        prompts: list[str] = []

        def read(prompt: str) -> str:
            prompts.append(prompt)
            if not pending:
                raise EOFError
            answer = pending.pop(0)
            if isinstance(answer, BaseException):
                raise answer
            return answer

        code = main(
            list(argv),
            stdin=io.StringIO(stdin_text),
            stdout=out,
            stderr=err,
            env=env or {},
            settings=settings or tmp_path / "ayarlar" / "ayarlar.json",
            interactive=interactive,
            read=read,
        )
        result = Result(code, out.getvalue(), err.getvalue())
        result.prompts = prompts  # type: ignore[attr-defined]
        return result

    return _run


@pytest.fixture
def write_ats(tmp_path: Path):
    def _write(content: str | bytes, name: str = "program.atslang") -> Path:
        path = tmp_path / name
        if isinstance(content, str):
            content = content.encode("utf-8")
        path.write_bytes(content)
        return path

    return _write


def run_text(text: str) -> str:
    out = io.StringIO()
    run_source(SourceFile.from_text("test.atslang", text), out)
    return out.getvalue()


def error_of(text: str | bytes) -> ATSError:
    with pytest.raises(ATSError) as info:
        if isinstance(text, bytes):
            source = SourceFile.from_bytes("test.atslang", text)
        else:
            source = SourceFile.from_text("test.atslang", text)
        compile_source(source)
    return info.value
