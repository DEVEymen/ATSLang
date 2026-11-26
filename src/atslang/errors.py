"""ATS errors and their rendering (spec §7)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from atslang import messages

if TYPE_CHECKING:
    from atslang.source import Position, SourceFile


class ATSError(Exception):
    """An error in the user's program, identified by a stable ATS code.

    ``hint`` selects a situation-specific hint from ``messages.HINTS``; when it
    is ``None`` the code's default hint (if any) is used. ``params`` fill the
    placeholders of the title, label and hint. Values in ``params`` that are
    message keys (such as token descriptions) are passed as ``found_key`` /
    ``expected_key`` and translated at render time.
    """

    def __init__(
        self,
        code: str,
        position: Position | None = None,
        *,
        source: SourceFile | None = None,
        hint: str | None = None,
        **params: object,
    ) -> None:
        super().__init__(code)
        self.code = code
        self.position = position
        self.source = source
        self.hint = hint
        self.params = params

    def __repr__(self) -> str:
        pos = f"{self.position.line}:{self.position.column}" if self.position else "-"
        return f"ATSError({self.code} at {pos})"


def _translated_params(error: ATSError, lang: str) -> dict[str, object]:
    params = dict(error.params)
    tokens = messages.TOKENS[lang]
    for key in ("found", "expected"):
        token_key = params.pop(f"{key}_key", None)
        if token_key is not None:
            params[key] = tokens[str(token_key)].format(value=params.get("value", ""))
    return params


def render_error(error: ATSError, lang: str, source: SourceFile | None = None) -> str:
    """Render ``error`` in the format of spec §7.2."""
    source = error.source or source
    entry = messages.CODES[lang][error.code]
    params = _translated_params(error, lang)
    words = messages.UI[lang]

    lines = [f"{words['error']}[{error.code}]: {entry['title'].format(**params)}"]

    if error.hint is not None:
        hint = messages.HINTS[lang][error.hint].format(**params)
    elif "hint" in entry:
        hint = entry["hint"].format(**params)
    else:
        hint = None

    pos = error.position
    if pos is not None and source is not None:
        number = str(pos.line)
        pad = " " * (len(number) + 1)
        lines.append(f"{pad}--> {source.name}:{pos.line}:{pos.column}")
        lines.append(f"{pad} |")
        line_text = source.line_text(pos.line)
        lines.append(f" {number} | {line_text}".rstrip())
        prefix = "".join("\t" if ch == "\t" else " " for ch in line_text[: pos.column - 1])
        label = entry.get("label")
        marker = f"{prefix}^" + (f" {label.format(**params)}" if label else "")
        lines.append(f"{pad} | {marker}")
        if hint:
            lines.append(f"{pad} = {words['hint']}: {hint}")
    else:
        if pos is not None:
            lines.append(f"  --> {pos.line}:{pos.column}")
        if hint:
            lines.append(f"  = {words['hint']}: {hint}")

    return "\n".join(lines)
