"""Built-in functions (spec §6.3, §6.6)."""

from __future__ import annotations

import math
import random
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import TextIO

from atslang.errors import ATSError
from atslang.source import Position, SourceFile
from atslang.values import Value, float_is_finite, format_value, int_in_range, type_name

# `aralik(...)` is part of the `her` loop syntax, not a callable function (spec §6.10).
RANGE_NAME = "aralik"

INT_TEXT = re.compile(r"[+-]?[0-9]+")
FLOAT_TEXT = re.compile(r"[+-]?[0-9]+(\.[0-9]+)?")


@dataclass(frozen=True, slots=True)
class Context:
    out: TextIO
    position: Position
    source: SourceFile | None
    inp: TextIO | None = None
    arg_positions: tuple[Position, ...] = ()
    rng: random.Random | None = None

    def arg_position(self, i: int) -> Position:
        return self.arg_positions[i] if i < len(self.arg_positions) else self.position


@dataclass(frozen=True, slots=True)
class Builtin:
    name: str
    arity: int  # maximum number of arguments
    returns_value: bool
    implementation: Callable[[Context, tuple[Value, ...]], Value | None]
    min_arity: int | None = None  # defaults to arity

    @property
    def minimum(self) -> int:
        return self.arity if self.min_arity is None else self.min_arity


def _preview(text: str) -> str:
    return text if len(text) <= 30 else text[:27] + "..."


def _yaz(ctx: Context, args: tuple[Value, ...]) -> None:
    ctx.out.write(format_value(args[0]) + "\n")


def _metin(ctx: Context, args: tuple[Value, ...]) -> str:
    return format_value(args[0])


def _reject_type(ctx: Context, func: str, value: Value, accepted: tuple[str, ...]) -> None:
    if type_name(value) not in accepted:
        raise ATSError("ATS307", ctx.position, source=ctx.source, func=func,
                       given=type_name(value))


def _tam(ctx: Context, args: tuple[Value, ...]) -> int:  # noqa: C901
    value = args[0]
    _reject_type(ctx, "tam", value, ("tam", "ondalik", "metin"))
    if isinstance(value, str):
        if not INT_TEXT.fullmatch(value):
            raise ATSError("ATS305", ctx.position, source=ctx.source, hint="int_text",
                           func="tam", value=_preview(value))
        result = int(value)
    elif isinstance(value, float):
        result = int(value)  # toward zero
    else:
        result = value
    if not int_in_range(result):
        raise ATSError("ATS303", ctx.position, source=ctx.source)
    return result


def _ondalik(ctx: Context, args: tuple[Value, ...]) -> float:
    value = args[0]
    _reject_type(ctx, "ondalik", value, ("tam", "ondalik", "metin"))
    if isinstance(value, str):
        if not FLOAT_TEXT.fullmatch(value):
            raise ATSError("ATS305", ctx.position, source=ctx.source, hint="float_text",
                           func="ondalik", value=_preview(value))
        result = float(value)
    else:
        result = float(value)
    if not float_is_finite(result):
        raise ATSError("ATS303", ctx.position, source=ctx.source)
    return result


def _uzunluk(ctx: Context, args: tuple[Value, ...]) -> int:
    _reject_type(ctx, "uzunluk", args[0], ("liste", "metin", "sozluk"))
    return len(args[0])


def _ekle(ctx: Context, args: tuple[Value, ...]) -> None:
    _reject_type(ctx, "ekle", args[0], ("liste",))
    args[0].append(args[1])


def _sil(ctx: Context, args: tuple[Value, ...]) -> Value:  # noqa: C901
    items, index = args
    _reject_type(ctx, "sil", items, ("liste", "sozluk"))
    position = ctx.arg_position(1)
    if isinstance(items, dict):
        _check_key(ctx, index, position)
        if index not in items:
            raise ATSError("ATS320", position, source=ctx.source, key=_key_text(index))
        return items.pop(index)
    if type_name(index) != "tam":
        raise ATSError("ATS308", position, source=ctx.source, what="indeks",
                       given=type_name(index))
    if not 0 <= index < len(items):
        raise ATSError("ATS314", position, source=ctx.source, index=index, length=len(items))
    return items.pop(index)


def _oku(ctx: Context, args: tuple[Value, ...]) -> str:
    if args:
        _reject_type(ctx, "oku", args[0], ("metin",))
        ctx.out.write(args[0])
    ctx.out.flush()
    line = ctx.inp.readline() if ctx.inp is not None else ""
    if line == "":
        raise ATSError("ATS315", ctx.position, source=ctx.source)
    return line[:-1] if line.endswith("\n") else line


def _key_text(key: Value) -> str:
    return f'"{key}"' if isinstance(key, str) else str(key)


def _check_key(ctx: Context, key: Value, position: Position) -> None:
    if type_name(key) not in ("metin", "tam"):
        raise ATSError("ATS319", position, source=ctx.source, given=type_name(key))


# -- 0.6: text --------------------------------------------------------------
def _upper_tr(text: str) -> str:
    """Turkish rules (spec §6.14): i -> İ, ı -> I."""
    return text.replace("i", "İ").replace("ı", "I").upper()


def _lower_tr(text: str) -> str:
    """Turkish rules (spec §6.14): I -> ı, İ -> i."""
    return text.replace("I", "ı").replace("İ", "i").lower()


def _buyuk(ctx: Context, args: tuple[Value, ...]) -> str:
    _reject_type(ctx, "buyuk", args[0], ("metin",))
    return _upper_tr(args[0])


def _kucuk(ctx: Context, args: tuple[Value, ...]) -> str:
    _reject_type(ctx, "kucuk", args[0], ("metin",))
    return _lower_tr(args[0])


def _kirp(ctx: Context, args: tuple[Value, ...]) -> str:
    _reject_type(ctx, "kirp", args[0], ("metin",))
    return args[0].strip()


def _bol(ctx: Context, args: tuple[Value, ...]) -> list:
    _reject_type(ctx, "bol", args[0], ("metin",))
    if len(args) == 1:
        return args[0].split()
    _reject_type(ctx, "bol", args[1], ("metin",))
    if args[1] == "":
        raise ATSError("ATS321", ctx.arg_position(1), source=ctx.source)
    return args[0].split(args[1])


def _birlestir(ctx: Context, args: tuple[Value, ...]) -> str:
    items, separator = args
    _reject_type(ctx, "birlestir", items, ("liste",))
    _reject_type(ctx, "birlestir", separator, ("metin",))
    for item in items:
        _reject_type(ctx, "birlestir", item, ("metin",))
    return separator.join(items)


def _degistir(ctx: Context, args: tuple[Value, ...]) -> str:
    for value in args:
        _reject_type(ctx, "degistir", value, ("metin",))
    text, old, new = args
    if old == "":
        raise ATSError("ATS321", ctx.arg_position(1), source=ctx.source)
    return text.replace(old, new)


def _icerir(ctx: Context, args: tuple[Value, ...]) -> bool:
    container, item = args
    _reject_type(ctx, "icerir", container, ("liste", "metin", "sozluk"))
    if isinstance(container, str):
        _reject_type(ctx, "icerir", item, ("metin",))
        return item in container
    if isinstance(container, dict):
        _check_key(ctx, item, ctx.arg_position(1))
        return item in container
    from atslang.values import values_equal
    return any(values_equal(x, item) for x in container)


def _anahtarlar(ctx: Context, args: tuple[Value, ...]) -> list:
    _reject_type(ctx, "anahtarlar", args[0], ("sozluk",))
    return list(args[0].keys())


# -- 0.6: numbers -----------------------------------------------------------
def _rastgele(ctx: Context, args: tuple[Value, ...]) -> int:
    low, high = args
    _reject_type(ctx, "rastgele", low, ("tam",))
    _reject_type(ctx, "rastgele", high, ("tam",))
    if low > high:
        raise ATSError("ATS322", ctx.position, source=ctx.source, low=low, high=high)
    rng = ctx.rng or random
    return rng.randint(low, high)


def _mutlak(ctx: Context, args: tuple[Value, ...]) -> Value:
    _reject_type(ctx, "mutlak", args[0], ("tam", "ondalik"))
    result = abs(args[0])
    if not (isinstance(result, float) or int_in_range(result)):
        raise ATSError("ATS303", ctx.position, source=ctx.source)
    return result


def _yuvarla(ctx: Context, args: tuple[Value, ...]) -> int:
    """Nearest integer; halves go away from zero (2.5 -> 3, -2.5 -> -3)."""
    _reject_type(ctx, "yuvarla", args[0], ("tam", "ondalik"))
    value = args[0]
    if isinstance(value, int):
        return value
    result = int(math.floor(abs(value) + 0.5)) * (1 if value >= 0 else -1)
    if not int_in_range(result):
        raise ATSError("ATS303", ctx.position, source=ctx.source)
    return result


def _karekok(ctx: Context, args: tuple[Value, ...]) -> float:
    _reject_type(ctx, "karekok", args[0], ("tam", "ondalik"))
    if args[0] < 0:
        raise ATSError("ATS323", ctx.arg_position(0), source=ctx.source)
    return math.sqrt(args[0])


BUILTINS: dict[str, Builtin] = {
    "yaz": Builtin("yaz", 1, False, _yaz),
    "metin": Builtin("metin", 1, True, _metin),
    "tam": Builtin("tam", 1, True, _tam),
    "ondalik": Builtin("ondalik", 1, True, _ondalik),
    "uzunluk": Builtin("uzunluk", 1, True, _uzunluk),
    "ekle": Builtin("ekle", 2, False, _ekle),
    "sil": Builtin("sil", 2, True, _sil),
    "oku": Builtin("oku", 1, True, _oku, min_arity=0),
    # 0.6
    "buyuk": Builtin("buyuk", 1, True, _buyuk),
    "kucuk": Builtin("kucuk", 1, True, _kucuk),
    "kirp": Builtin("kirp", 1, True, _kirp),
    "bol": Builtin("bol", 2, True, _bol, min_arity=1),
    "birlestir": Builtin("birlestir", 2, True, _birlestir),
    "degistir": Builtin("degistir", 3, True, _degistir),
    "icerir": Builtin("icerir", 2, True, _icerir),
    "anahtarlar": Builtin("anahtarlar", 1, True, _anahtarlar),
    "rastgele": Builtin("rastgele", 2, True, _rastgele),
    "mutlak": Builtin("mutlak", 1, True, _mutlak),
    "yuvarla": Builtin("yuvarla", 1, True, _yuvarla),
    "karekok": Builtin("karekok", 1, True, _karekok),
}
