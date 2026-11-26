from atslang.lexer import tokenize
from atslang.source import Position, SourceFile
from atslang.tokens import TokenKind as K

from conftest import error_of


def kinds(text: str) -> list[K]:
    return [t.kind for t in tokenize(SourceFile.from_text("t.atslang", text))]


def test_simple_call():
    assert kinds('yaz("a")') == [K.IDENT, K.LPAREN, K.STRING, K.RPAREN, K.EOF]


def test_newlines_and_semicolons():
    assert kinds('yaz("a")\nyaz("b");') == [
        K.IDENT, K.LPAREN, K.STRING, K.RPAREN, K.NEWLINE,
        K.IDENT, K.LPAREN, K.STRING, K.RPAREN, K.SEMICOLON, K.EOF,
    ]


def test_newlines_inside_parentheses_are_ignored():
    assert K.NEWLINE not in kinds('yaz(\n"a"\n)')


def test_comment_is_skipped_but_newline_kept():
    assert kinds("# yorum\n") == [K.NEWLINE, K.EOF]


def test_hash_inside_string_is_not_a_comment():
    tokens = tokenize(SourceFile.from_text("t.atslang", 'yaz("#a")'))
    assert tokens[2].value == "#a"


def test_escape_sequences():
    tokens = tokenize(SourceFile.from_text("t.atslang", r'"\n\t\"\\"'))
    assert tokens[0].value == '\n\t"\\'


def test_turkish_characters_in_strings():
    tokens = tokenize(SourceFile.from_text("t.atslang", '"şğıüöç İ"'))
    assert tokens[0].value == "şğıüöç İ"


def test_positions_count_characters_not_bytes():
    tokens = tokenize(SourceFile.from_text("t.atslang", '"ğğ" yaz'))
    assert tokens[1].position == Position(1, 6)


def test_identifier_case_is_preserved():
    tokens = tokenize(SourceFile.from_text("t.atslang", "Yaz _a1"))
    assert [t.value for t in tokens[:2]] == ["Yaz", "_a1"]


def test_unterminated_string():
    err = error_of('yaz("abc\n')
    assert (err.code, err.position) == ("ATS003", Position(1, 5))


def test_backslash_at_end_of_line_is_unterminated():
    assert error_of('yaz("abc\\\n").').code == "ATS003"


def test_invalid_escape():
    err = error_of(r'yaz("\x")')
    assert (err.code, err.params["seq"]) == ("ATS004", r"\x")


def test_turkish_identifier_suggests_ascii():
    err = error_of('İşlem("a")')
    assert err.code == "ATS005"
    assert err.position == Position(1, 1)
    assert err.params["suggestion"] == "Islem"


def test_single_quote():
    assert error_of("yaz('a')").code == "ATS006"


def test_numbers_and_operators():
    assert kinds("1 + 2.5 - 3 * 4 / 5 // 6 % 7") == [
        K.INT, K.PLUS, K.FLOAT, K.MINUS, K.INT, K.STAR, K.INT, K.SLASH, K.INT,
        K.SLASHSLASH, K.INT, K.PERCENT, K.INT, K.EOF,
    ]


def test_keywords_and_declaration_tokens():
    assert kinds("var x: tam = 1") == [K.VAR, K.IDENT, K.COLON, K.IDENT, K.EQUAL, K.INT, K.EOF]
    assert kinds("sabit") == [K.SABIT, K.EOF]
    assert kinds("Var degisken") == [K.IDENT, K.IDENT, K.EOF]  # case-sensitive


def test_float_needs_digits_after_point():
    err = error_of("yaz(1.)")
    assert (err.code, err.hint) == ("ATS007", "float_digits")


def test_name_cannot_start_with_digit():
    err = error_of("var 2ad = 1")
    assert (err.code, err.params["text"]) == ("ATS007", "2ad")


def test_two_decimal_points():
    assert error_of("yaz(1.2.3)").params["text"] == "1.2.3"


def test_integer_literal_limit():
    assert error_of("yaz(9223372036854775808)").code == "ATS008"


def test_point_without_leading_digit():
    assert error_of("yaz(.5)").code == "ATS002"


def test_non_breaking_space_is_unrecognised():
    err = error_of('yaz( "a")')
    assert (err.code, err.params["char"]) == ("ATS002", "U+00A0")
