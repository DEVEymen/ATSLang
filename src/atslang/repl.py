"""Interactive mode: `ats` in a terminal (spec §8.2)."""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import TextIO

from atslang import __version__, messages
from atslang.checker import Checker
from atslang.errors import ATSError, render_error
from atslang.interpreter import Interpreter
from atslang.lexer import tokenize
from atslang.nodes import ExprStatement
from atslang.parser import parse, parse_expression
from atslang.source import SourceFile
from atslang.values import repr_value

PROMPT = "ats> "
CONTINUATION = "...> "
EXIT_WORDS = ("cikis", "çıkış")
# Errors that only mean "the input is not finished yet"
INCOMPLETE = ("ATS102", "ATS106")
# Errors that may mean "this is an expression, show its value"
EXPRESSION_HINTS = ("ATS101", "ATS104")


class Repl:
    def __init__(self, read: Callable[[str], str], out: TextIO, err: TextIO, lang: str,
                 inp: TextIO | None = None, seed: int | None = None) -> None:
        self.read = read
        self.out = out
        self.err = err
        self.lang = lang
        self.source = SourceFile.from_text(self._source_name(), "")
        self.checker = Checker(self.source)
        self.interpreter = Interpreter(out, self.source, inp, seed)

    def _source_name(self) -> str:
        return "<girdi>" if self.lang == "tr" else "<input>"

    # -- main loop -------------------------------------------------------
    def run(self) -> int:
        self.out.write(messages.ui(self.lang, "repl_banner", version=__version__) + "\n")
        while True:
            try:
                text = self._read_chunk()
            except EOFError:
                self.out.write("\n")
                return 0
            except KeyboardInterrupt:
                self.out.write("\n")
                continue
            if text is None:
                continue
            if text.strip() in EXIT_WORDS:
                return 0
            try:
                self.execute(text)
            except KeyboardInterrupt:
                self.out.flush()
                self.err.write(f"{messages.UI[self.lang]['error']}: "
                               f"{messages.ui(self.lang, 'interrupted')}\n")

    def _read_chunk(self) -> str | None:
        """Read lines until they form a complete input. None for an empty line."""
        lines = [self._line(PROMPT)]
        if lines[0].strip() == "":
            return None
        while True:
            text = "\n".join(lines)
            if not self._needs_more(text):
                return text
            line = self._line(CONTINUATION)
            if line.strip() == "":
                return text  # an empty line ends the input; errors are shown then
            lines.append(line)

    def _line(self, prompt: str) -> str:
        return self.read(prompt).rstrip("\r\n")

    def _needs_more(self, text: str) -> bool:
        source = SourceFile.from_text(self._source_name(), text)
        try:
            parse(tokenize(source), source)
        except ATSError as error:
            return error.code in INCOMPLETE
        return False

    # -- one input -------------------------------------------------------
    def execute(self, text: str) -> None:
        source = SourceFile.from_text(self._source_name(), text)
        self.checker.source = source
        self.interpreter.source = source
        try:
            tokens = tokenize(source)
            try:
                program = parse(tokens, source)
                expression = None
            except ATSError as statement_error:
                if statement_error.code not in EXPRESSION_HINTS:
                    raise
                try:
                    expression = parse_expression(tokens, source)
                except ATSError:
                    raise statement_error from None
            if expression is None and len(program.statements) == 1:
                only = program.statements[0]
                if isinstance(only, ExprStatement) and self.checker.call_returns_value(only.call):
                    expression = only.call  # `kare(3)` shows its value
            self._check(program if expression is None else None, expression)
            if expression is None:
                self._run(program)
            else:
                self._show(expression)
        except ATSError as error:
            self.out.flush()
            self.err.write(render_error(error, self.lang) + "\n")

    def _check(self, program, expression) -> None:
        # The checker's global scope must not keep half of a failed input.
        saved = copy.copy(self.checker.scopes[0])
        try:
            if program is not None:
                self.checker.check(program)
            else:
                self.checker.check_expression(expression)
        except ATSError:
            self.checker.scopes[0].clear()
            self.checker.scopes[0].update(saved)
            raise

    def _run(self, program) -> None:
        try:
            self.interpreter.run(program)
        except (ATSError, KeyboardInterrupt):
            self._forget_what_did_not_run()
            raise

    def _show(self, expression) -> None:
        try:
            value = self.interpreter.evaluate(expression)
        except (ATSError, KeyboardInterrupt):
            self._forget_what_did_not_run()
            raise
        if value is not None:
            self.out.write(repr_value(value) + "\n")
        self.out.flush()

    def _forget_what_did_not_run(self) -> None:
        """After a runtime error, names declared after the failing statement
        were checked but never created. Remove them so later inputs see them
        as undefined (ATS203) instead of crashing."""
        defined = self.interpreter.frames[0]
        functions = self.interpreter.functions
        scope = self.checker.scopes[0]
        for name in list(scope):
            variable = scope[name]
            exists = name in functions if variable.function is not None else name in defined
            if not exists:
                del scope[name]
        # Blocks or calls interrupted by the error may have left frames open.
        del self.interpreter.frames[1:]
        self.interpreter.depth = 0


def run_repl(read: Callable[[str], str], out: TextIO, err: TextIO, lang: str,
             inp: TextIO | None = None, seed: int | None = None) -> int:
    return Repl(read, out, err, lang, inp, seed).run()
