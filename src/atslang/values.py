"""Runtime values and their rules (spec §6.4, §6.5).

ATSLang 0.2 values map onto Python values:

========  ===========  ==========================================
ATSLang   Python       Rule
========  ===========  ==========================================
tam       int          64-bit signed; leaving the range is ATS303
ondalik   float        IEEE 754 double; inf/nan results are ATS303
metin     str          Unicode text
mantiksal bool         dogru / yanlis (0.3)
liste     list         mutable, shared by reference (0.5)
sozluk    dict         keys are metin or tam, insertion ordered (0.6)
========  ===========  ==========================================

Python's bool is a subclass of int, so every check below tests for bool
before int.
"""

from __future__ import annotations

import math

INT_MIN = -(2**63)
INT_MAX = 2**63 - 1

TYPE_NAMES = ("tam", "ondalik", "metin", "mantiksal", "liste", "sozluk")
KEY_TYPES = ("metin", "tam")

Value = bool | int | float | str | list | dict


def type_name(value: Value) -> str:
    if isinstance(value, dict):
        return "sozluk"
    if isinstance(value, list):
        return "liste"
    if isinstance(value, bool):
        return "mantiksal"
    if isinstance(value, str):
        return "metin"
    if isinstance(value, float):
        return "ondalik"
    return "tam"


def is_number(value: Value) -> bool:
    return type_name(value) in ("tam", "ondalik")


def int_in_range(value: int) -> bool:
    return INT_MIN <= value <= INT_MAX


def float_is_finite(value: float) -> bool:
    return math.isfinite(value)


def _quote(text: str) -> str:
    escaped = (text.replace("\\", "\\\\").replace('"', '\\"')
               .replace("\n", "\\n").replace("\t", "\\t"))
    return f'"{escaped}"'


def _format_item(item: Value, seen: set[int]) -> str:
    if isinstance(item, str):
        return _quote(item)
    if isinstance(item, (list, dict)):
        return _format_container(item, seen)
    return format_value(item)


def _format_container(container: list | dict, seen: set[int]) -> str:
    if id(container) in seen:
        return "[...]" if isinstance(container, list) else "{...}"  # contains itself
    seen.add(id(container))
    if isinstance(container, list):
        text = "[" + ", ".join(_format_item(x, seen) for x in container) + "]"
    else:
        text = "{" + ", ".join(f"{_format_item(k, seen)}: {_format_item(v, seen)}"
                               for k, v in container.items()) + "}"
    seen.discard(id(container))
    return text


def values_equal(a: Value, b: Value) -> bool:
    """Deep equality used by == (spec §6.12). Different kinds are never equal."""
    if is_number(a) and is_number(b):
        return a == b
    if type_name(a) != type_name(b):
        return False
    if isinstance(a, list):
        return len(a) == len(b) and all(values_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict):
        return a.keys() == b.keys() and all(values_equal(a[k], b[k]) for k in a)
    return a == b


def format_value(value: Value) -> str:
    """Text shown by ``yaz`` and produced by ``metin`` (spec §6.5).

    Floats use the shortest text that reads back as the same number and
    always contain a '.' or an exponent, so ``3.0`` stays ``3.0``.
    """
    if isinstance(value, (list, dict)):
        return _format_container(value, set())
    if isinstance(value, bool):
        return "dogru" if value else "yanlis"
    if isinstance(value, str):
        return value
    if isinstance(value, float):
        if value == 0.0:
            return "0.0"  # also for -0.0
        return repr(value)
    return str(value)


def fits_type(value: Value, declared: str) -> bool:
    """Whether ``value`` may be stored in a variable of type ``declared``.

    A ``tam`` may be stored in an ``ondalik`` variable (it is widened);
    nothing else converts implicitly.
    """
    actual = type_name(value)
    return actual == declared or (declared == "ondalik" and actual == "tam")


def coerce_to(value: Value, declared: str | None) -> Value:
    if declared == "ondalik" and type_name(value) == "tam":
        return float(value)
    return value


def repr_value(value: Value) -> str:
    """How the REPL echoes a value: like format_value, but texts are quoted."""
    return _format_item(value, set())
