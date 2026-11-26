"""Source files and source positions (spec §4.1, §7.1)."""

from __future__ import annotations

from dataclasses import dataclass

from atslang.errors import ATSError

UTF8_BOM = b"\xef\xbb\xbf"


@dataclass(frozen=True, slots=True)
class Position:
    """A 1-based line and column. Columns count characters, not bytes."""

    line: int
    column: int


@dataclass(frozen=True, slots=True)
class SourceFile:
    """Decoded, newline-normalised program text.

    ``\\r\\n`` is normalised to ``\\n``. A lone ``\\r`` is kept so the lexer can
    report it as an unrecognised character (ATS002).
    """

    name: str
    text: str

    def line_text(self, line: int) -> str:
        lines = self.text.split("\n")
        if 1 <= line <= len(lines):
            return lines[line - 1]
        return ""

    @classmethod
    def from_bytes(cls, name: str, data: bytes) -> SourceFile:
        if data.startswith(UTF8_BOM):
            data = data[len(UTF8_BOM):]
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            valid = data[: exc.start].decode("utf-8")
            normalised = valid.replace("\r\n", "\n")
            line = normalised.count("\n") + 1
            column = len(normalised) - (normalised.rfind("\n") + 1) + 1
            # Show what we could decode of the offending line.
            partial = cls(name, normalised)
            raise ATSError(
                "ATS001",
                Position(line, column),
                source=partial,
                byte=f"0x{data[exc.start]:02X}",
            ) from None
        return cls(name, text.replace("\r\n", "\n"))

    @classmethod
    def from_text(cls, name: str, text: str) -> SourceFile:
        return cls(name, text.replace("\r\n", "\n"))
