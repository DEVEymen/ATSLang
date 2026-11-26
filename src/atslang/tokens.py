"""Token definitions (spec §4)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from atslang.source import Position


class TokenKind(Enum):
    IDENT = "IDENT"
    STRING = "STRING"
    INT = "INT"
    FLOAT = "FLOAT"
    # keywords
    VAR = "VAR"
    SABIT = "SABIT"
    EGER = "EGER"
    DEGILSE = "DEGILSE"
    DOGRU = "DOGRU"
    YANLIS = "YANLIS"
    VE = "VE"
    VEYA = "VEYA"
    DEGIL = "DEGIL"
    IKEN = "IKEN"
    HER = "HER"
    TEKRARLA = "TEKRARLA"
    DUR = "DUR"
    DEVAM = "DEVAM"
    FONKSIYON = "FONKSIYON"
    DONDUR = "DONDUR"
    # punctuation
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    LBRACE = "LBRACE"
    RBRACE = "RBRACE"
    COMMA = "COMMA"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    EQUAL = "EQUAL"
    # operators
    PLUS = "PLUS"
    MINUS = "MINUS"
    STAR = "STAR"
    SLASH = "SLASH"
    SLASHSLASH = "SLASHSLASH"
    PERCENT = "PERCENT"
    EQEQ = "EQEQ"
    NOTEQ = "NOTEQ"
    LT = "LT"
    LE = "LE"
    GT = "GT"
    GE = "GE"
    # layout
    NEWLINE = "NEWLINE"
    EOF = "EOF"


KEYWORDS = {
    "var": TokenKind.VAR,
    "sabit": TokenKind.SABIT,
    "eger": TokenKind.EGER,
    "degilse": TokenKind.DEGILSE,
    "dogru": TokenKind.DOGRU,
    "yanlis": TokenKind.YANLIS,
    "ve": TokenKind.VE,
    "veya": TokenKind.VEYA,
    "degil": TokenKind.DEGIL,
    "iken": TokenKind.IKEN,
    "her": TokenKind.HER,
    "tekrarla": TokenKind.TEKRARLA,
    "dur": TokenKind.DUR,
    "devam": TokenKind.DEVAM,
    "fonksiyon": TokenKind.FONKSIYON,
    "dondur": TokenKind.DONDUR,
}


@dataclass(frozen=True, slots=True)
class Token:
    kind: TokenKind
    value: str
    position: Position
