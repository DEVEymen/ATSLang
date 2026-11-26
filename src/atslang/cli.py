"""The ``ats`` command-line tool (spec §8)."""

from __future__ import annotations

import os
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from atslang import __version__, messages, winassoc
from atslang.config import resolve_language, settings_path
from atslang.errors import ATSError, render_error
from atslang.interpreter import run_source
from atslang.source import SourceFile

EXIT_OK = 0
EXIT_PROGRAM_ERROR = 1
EXIT_USAGE_ERROR = 2
EXIT_INTERRUPTED = 130

HELP_FLAGS = ("-h", "--help", "--yardim")
VERSION_FLAGS = ("-v", "--version", "--surum")
LANGUAGE_FLAGS = ("--dil", "--lang")
WAIT_FLAGS = ("--bekle", "--wait")
REGISTER_FLAGS = ("--kur", "--register")
UNREGISTER_FLAGS = ("--kaldir", "--unregister")
SEED_FLAGS = ("--tohum", "--seed")
REPL_FLAGS = ("--etkilesimli", "--repl", "-i")


@dataclass
class ParsedArgs:
    help: bool = False
    version: bool = False
    language: str | None = None
    wait: bool = False
    register: bool = False
    unregister: bool = False
    seed: int | None = None
    repl: bool = False
    file: str | None = None
    error: tuple[str, dict[str, object]] | None = None


def parse_args(argv: Sequence[str]) -> ParsedArgs:
    parsed = ParsedArgs()

    def fail(key: str, **params: object) -> None:
        if parsed.error is None:
            parsed.error = (key, params)

    def set_language(option: str, value: str | None) -> None:
        if value is None or value == "":
            fail("missing_language", option=option)
            return
        normalised = value.lower()
        if normalised not in messages.LANGUAGES:
            fail("invalid_language", value=value)
            return
        parsed.language = normalised

    args = list(argv)
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in HELP_FLAGS:
            parsed.help = True
        elif arg in VERSION_FLAGS:
            parsed.version = True
        elif arg in REPL_FLAGS:
            parsed.repl = True
        elif arg in WAIT_FLAGS:
            parsed.wait = True
        elif arg in REGISTER_FLAGS:
            parsed.register = True
        elif arg in UNREGISTER_FLAGS:
            parsed.unregister = True
        elif arg in SEED_FLAGS or any(arg.startswith(f + "=") for f in SEED_FLAGS):
            if "=" in arg:
                option, _, value = arg.partition("=")
            else:
                option, value = arg, (args[i + 1] if i + 1 < len(args) else None)
                if value is not None:
                    i += 1
            if value is None or not value.lstrip("-").isdigit():
                fail("invalid_seed", option=option)
            else:
                parsed.seed = int(value)
        elif arg in LANGUAGE_FLAGS:
            value = args[i + 1] if i + 1 < len(args) else None
            if value is not None and value.startswith("-"):
                value = None
            else:
                i += 1
            set_language(arg, value)
        elif any(arg.startswith(flag + "=") for flag in LANGUAGE_FLAGS):
            option, _, value = arg.partition("=")
            set_language(option, value)
        elif arg.startswith("-") and arg != "-":
            fail("unknown_option", option=arg)
        elif parsed.file is None:
            parsed.file = arg
        else:
            fail("extra_argument", arg=arg)
        i += 1
    return parsed


def _is_interactive(stdin: TextIO, stdout: TextIO) -> bool:
    try:
        return stdin.isatty() and stdout.isatty()
    except (AttributeError, ValueError):
        return False


def main(
    argv: Sequence[str] | None = None,
    *,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
    env: Mapping[str, str] | None = None,
    settings: Path | None = None,
    interactive: bool | None = None,
    read: Callable[[str], str] | None = None,
    registry: winassoc.Registry | None = None,
    on_windows: bool | None = None,
) -> int:
    argv = sys.argv[1:] if argv is None else argv
    stdin = sys.stdin if stdin is None else stdin
    stdout = sys.stdout if stdout is None else stdout
    stderr = sys.stderr if stderr is None else stderr
    env = os.environ if env is None else env
    settings = settings_path(env) if settings is None else settings
    interactive = _is_interactive(stdin, stdout) if interactive is None else interactive

    if read is None and interactive and stdin is sys.stdin and stdout is sys.stdout:
        read = input  # line editing and history in a real terminal
    if read is None:
        def read(prompt: str) -> str:
            stdout.write(prompt)
            stdout.flush()
            line = stdin.readline()
            if line == "":
                raise EOFError
            return line

    parsed = parse_args(argv)
    choice = resolve_language(
        parsed.language,
        env=env,
        path=settings,
        interactive=interactive,
        read=read,
        write=stdout,
    )
    lang = choice.language
    words = messages.UI[lang]

    def warn(key: str, **params: object) -> None:
        stderr.write(f"{words['warning']}: {messages.ui(lang, key, **params)}\n")

    def usage_error(key: str, **params: object) -> int:
        stderr.write(f"{words['error']}: {messages.ui(lang, key, **params)}\n{words['see_help']}\n")
        return EXIT_USAGE_ERROR

    for notice in choice.warnings:
        warn(notice.key, **notice.params)

    code = _dispatch(parsed, lang, stdin, stdout, stderr, warn, usage_error, registry, on_windows,
                     interactive, read)

    if parsed.wait:
        # Opened by double-click (spec §8.1): keep the window open.
        stderr.flush()
        stdout.write("\n" + messages.ui(lang, "press_enter"))
        stdout.flush()
        try:
            stdin.readline()
        except (KeyboardInterrupt, EOFError, OSError, ValueError):
            pass
    return code


def _dispatch(parsed, lang, stdin, stdout, stderr, warn, usage_error, registry, on_windows,
              interactive=False, read=None) -> int:
    if parsed.error is not None:
        key, params = parsed.error
        return usage_error(key, **params)

    if parsed.help:
        stdout.write(messages.ui(lang, "help", version=__version__))
        return EXIT_OK

    if parsed.version:
        stdout.write(f"ATSLang {__version__}\n")
        return EXIT_OK

    if parsed.register or parsed.unregister:
        return _association(parsed, lang, stdout, usage_error, registry, on_windows)

    if parsed.file is None:
        if parsed.repl or interactive:
            from atslang.repl import run_repl
            return run_repl(read, stdout, stderr, lang, stdin, parsed.seed)
        stderr.write(messages.ui(lang, "help", version=__version__))
        return EXIT_USAGE_ERROR

    path = Path(parsed.file)
    if not path.exists():
        return usage_error("file_not_found", path=parsed.file)
    if not path.is_file():
        return usage_error("not_a_file", path=parsed.file)
    try:
        data = path.read_bytes()
    except OSError as exc:
        return usage_error("read_failed", path=parsed.file, reason=exc.strerror or exc)

    if path.suffix.lower() != ".atslang":
        warn("not_atslang_extension", path=parsed.file)

    try:
        source = SourceFile.from_bytes(parsed.file, data)
        run_source(source, stdout, stdin, parsed.seed)
    except ATSError as error:
        stderr.write(render_error(error, lang) + "\n")
        return EXIT_PROGRAM_ERROR
    except KeyboardInterrupt:
        try:
            stdout.flush()
        except (OSError, ValueError):
            pass
        stderr.write(f"\n{words_of(lang)['error']}: {messages.ui(lang, 'interrupted')}\n")
        return EXIT_INTERRUPTED
    return EXIT_OK


def words_of(lang: str) -> dict[str, str]:
    return messages.UI[lang]


def _association(parsed, lang, stdout, usage_error, registry, on_windows) -> int:
    on_windows = winassoc.is_windows() if on_windows is None else on_windows
    if not on_windows:
        return usage_error("windows_only")
    if registry is None:
        if parsed.register and not winassoc.package_is_installed(sys.executable):
            return usage_error("not_installed")
        registry = winassoc.WindowsRegistry()
    try:
        if parsed.register:
            winassoc.register(registry, sys.executable)
        else:
            winassoc.unregister(registry)
    except OSError as exc:
        return usage_error("association_failed", reason=exc.strerror or exc)
    winassoc.notify_shell()
    stdout.write(messages.ui(lang, "registered" if parsed.register else "unregistered") + "\n")
    return EXIT_OK


def _configure_standard_streams() -> None:
    """Spec §6.3: output is UTF-8 with \\n line endings on every platform."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8", newline="\n")
            except (ValueError, OSError):
                pass


def entry() -> None:
    _configure_standard_streams()
    sys.exit(main())
