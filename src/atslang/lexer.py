"""Lexer: turns source text into tokens (spec §4).

Newlines inside parentheses are not emitted, so expressions may continue on
the next line (spec §5).
"""

from __future__ import annotations

from atslang.errors import ATSError
from atslang.source import Position, SourceFile
from atslang.tokens import KEYWORDS, Token, TokenKind
from atslang.values import INT_MAX

TURKISH_TO_ASCII = {
    "ş": "s", "ğ": "g", "ı": "i", "ü": "u", "ö": "o", "ç": "c",
    "Ş": "S", "Ğ": "G", "İ": "I", "Ü": "U", "Ö": "O", "Ç": "C",
}

ESCAPES = {"n": "\n", "t": "\t", '"': '"', "\\": "\\"}

PUNCTUATION = {
    "(": TokenKind.LPAREN,
    ")": TokenKind.RPAREN,
    ",": TokenKind.COMMA,
    ";": TokenKind.SEMICOLON,
    ":": TokenKind.COLON,
    "[": TokenKind.LBRACKET,
    "]": TokenKind.RBRACKET,
    "{": TokenKind.LBRACE,
    "}": TokenKind.RBRACE,
    "+": TokenKind.PLUS,
    "-": TokenKind.MINUS,
    "*": TokenKind.STAR,
    "%": TokenKind.PERCENT,
}


# "=", "==", "!=", "<", "<=", ">", ">="
TWO_CHAR_STARTS = ("=", "!", "<", ">")


def _is_digit(ch: str) -> bool:
    return "0" <= ch <= "9"


def _is_ident_start(ch: str) -> bool:
    return ("a" <= ch <= "z") or ("A" <= ch <= "Z") or ch == "_"


def _is_ident_part(ch: str) -> bool:
    return _is_ident_start(ch) or ("0" <= ch <= "9")


def _describe_char(ch: str) -> str:
    if ch.isprintable() and not ch.isspace():
        return f"'{ch}'"
    return f"U+{ord(ch):04X}"


class Lexer:
    def __init__(self, source: SourceFile) -> None:
        self.source = source
        self.text = source.text
        self.index = 0
        self.line = 1
        self.column = 1
        self.depth = 0  # nesting depth of ( ) and [ ]

    # -- helpers ---------------------------------------------------------
    def _peek(self, offset: int = 0) -> str:
        i = self.index + offset
        return self.text[i] if i < len(self.text) else ""

    def _advance(self) -> str:
        ch = self.text[self.index]
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch

    def _position(self) -> Position:
        return Position(self.line, self.column)

    def _error(self, code: str, position: Position, **kwargs: object) -> ATSError:
        return ATSError(code, position, source=self.source, **kwargs)

    # -- main loop -------------------------------------------------------
    def tokenize(self) -> list[Token]:
        tokens: list[Token] = []
        while self.index < len(self.text):
            ch = self._peek()
            start = self._position()

            if ch in (" ", "\t"):
                self._advance()
            elif ch == "#":
                while self._peek() not in ("", "\n"):
                    self._advance()
            elif ch == "\n":
                self._advance()
                if self.depth == 0:
                    tokens.append(Token(TokenKind.NEWLINE, "\n", start))
            elif ch == '"':
                tokens.append(self._string())
            elif ch == "/":
                self._advance()
                if self._peek() == "/":
                    self._advance()
                    tokens.append(Token(TokenKind.SLASHSLASH, "//", start))
                else:
                    tokens.append(Token(TokenKind.SLASH, "/", start))
            elif ch in TWO_CHAR_STARTS:
                tokens.append(self._comparison_or_equal(start))
            elif _is_digit(ch):
                tokens.append(self._number())
            elif ch in PUNCTUATION:
                self._advance()
                kind = PUNCTUATION[ch]
                if kind in (TokenKind.LPAREN, TokenKind.LBRACKET):
                    self.depth += 1
                elif kind in (TokenKind.RPAREN, TokenKind.RBRACKET) and self.depth > 0:
                    self.depth -= 1
                tokens.append(Token(kind, ch, start))
            elif _is_ident_start(ch) or ch in TURKISH_TO_ASCII:
                tokens.append(self._identifier())
            elif ch == "'":
                raise self._error("ATS006", start)
            elif ch == "\r":
                raise self._error("ATS002", start, hint="carriage_return", char="U+000D")
            else:
                raise self._error("ATS002", start, char=_describe_char(ch))

        tokens.append(Token(TokenKind.EOF, "", self._position()))
        return tokens

    def _identifier(self) -> Token:
        start = self._position()
        begin = self.index
        first_turkish: tuple[str, Position] | None = None
        while (ch := self._peek()) and (_is_ident_part(ch) or ch in TURKISH_TO_ASCII):
            if ch in TURKISH_TO_ASCII and first_turkish is None:
                first_turkish = (ch, self._position())
            self._advance()
        name = self.text[begin:self.index]
        if first_turkish is not None:
            ch, pos = first_turkish
            suggestion = "".join(TURKISH_TO_ASCII.get(c, c) for c in name)
            raise self._error("ATS005", pos, char=ch, suggestion=suggestion)
        return Token(KEYWORDS.get(name, TokenKind.IDENT), name, start)

    def _comparison_or_equal(self, start: Position) -> Token:
        ch = self._advance()
        followed_by_equal = self._peek() == "="
        if followed_by_equal:
            self._advance()
        if ch == "=":
            return Token(TokenKind.EQEQ if followed_by_equal else TokenKind.EQUAL,
                         "==" if followed_by_equal else "=", start)
        if ch == "!":
            if not followed_by_equal:
                raise self._error("ATS002", start, hint="not_operator", char="'!'")
            return Token(TokenKind.NOTEQ, "!=", start)
        if ch == "<":
            return Token(TokenKind.LE if followed_by_equal else TokenKind.LT,
                         "<=" if followed_by_equal else "<", start)
        return Token(TokenKind.GE if followed_by_equal else TokenKind.GT,
                     ">=" if followed_by_equal else ">", start)

    def _number(self) -> Token:
        start = self._position()
        begin = self.index
        while _is_digit(self._peek()):
            self._advance()
        kind = TokenKind.INT
        if self._peek() == ".":
            self._advance()
            if not _is_digit(self._peek()):
                raise self._error("ATS007", start, hint="float_digits",
                                  text=self.text[begin:self.index])
            while _is_digit(self._peek()):
                self._advance()
            kind = TokenKind.FLOAT
        nxt = self._peek()
        if nxt and (_is_ident_part(nxt) or nxt in TURKISH_TO_ASCII or nxt == "."):
            while (c := self._peek()) and (_is_ident_part(c) or c in TURKISH_TO_ASCII or c == "."):
                self._advance()
            raise self._error("ATS007", start, hint="name_starts_digit",
                              text=self.text[begin:self.index])
        text = self.text[begin:self.index]
        if kind is TokenKind.INT and int(text) > INT_MAX:
            raise self._error("ATS008", start, text=text)
        return Token(kind, text, start)

    def _string(self) -> Token:
        start = self._position()
        self._advance()  # opening quote
        parts: list[str] = []
        while True:
            ch = self._peek()
            if ch in ("", "\n"):
                raise self._error("ATS003", start)
            if ch == '"':
                self._advance()
                return Token(TokenKind.STRING, "".join(parts), start)
            if ch == "\\":
                escape_pos = self._position()
                self._advance()
                nxt = self._peek()
                if nxt in ("", "\n"):
                    raise self._error("ATS003", start)
                self._advance()
                if nxt not in ESCAPES:
                    raise self._error("ATS004", escape_pos, seq=f"\\{nxt}")
                parts.append(ESCAPES[nxt])
                continue
            parts.append(self._advance())


def tokenize(source: SourceFile) -> list[Token]:
    return Lexer(source).tokenize()
