from atslang.lexer import tokenize
from atslang.nodes import (
    Assign, Binary, Call, ExprStatement, IntLiteral, Name, Program, StringLiteral, Unary, VarDecl,
)
from atslang.parser import parse
from atslang.source import Position, SourceFile

from conftest import error_of


def parse_text(text: str) -> Program:
    source = SourceFile.from_text("t.atslang", text)
    return parse(tokenize(source), source)


def test_empty_program():
    assert parse_text("") == Program(())
    assert parse_text("\n\n;;# yorum\n") == Program(())


def test_call_with_string():
    program = parse_text('yaz("a")')
    assert program == Program((
        ExprStatement(Call("yaz", (StringLiteral("a", Position(1, 5)),), Position(1, 1))),
    ))


def test_multiple_statements():
    program = parse_text('yaz("a"); yaz("b")\n\nyaz("c");')
    assert [s.call.arguments[0].value for s in program.statements] == ["a", "b", "c"]


def test_parser_accepts_any_arity_checker_decides():
    assert len(parse_text("yaz()").statements[0].call.arguments) == 0
    assert len(parse_text('yaz("a", "b")').statements[0].call.arguments) == 2


def test_bare_string_hint():
    err = error_of('"merhaba"')
    assert (err.code, err.hint) == ("ATS101", "bare_string")


def test_missing_parentheses_hint():
    err = error_of('yaz "a"')
    assert (err.code, err.hint) == ("ATS101", "call_parens")


def test_unquoted_name_is_an_undefined_variable():
    err = error_of("yaz(merhaba)")
    assert (err.code, err.hint) == ("ATS203", "quote_name")


def value(text):
    return parse_text(f"var v = {text}").statements[0].value


def test_declarations():
    decl = parse_text("sabit PI: ondalik = 3.14").statements[0]
    assert isinstance(decl, VarDecl)
    assert (decl.name, decl.constant, decl.type_name) == ("PI", True, "ondalik")
    assert parse_text("var x = 1").statements[0].constant is False


def test_assignment():
    stmt = parse_text("x = 1").statements[0]
    assert isinstance(stmt, Assign) and stmt.name == "x"


def test_precedence():
    tree = value("1 + 2 * 3")
    assert isinstance(tree, Binary) and tree.operator == "+"
    assert isinstance(tree.right, Binary) and tree.right.operator == "*"


def test_left_associativity():
    tree = value("10 - 2 - 3")
    assert tree.operator == "-" and isinstance(tree.left, Binary)
    assert tree.right == IntLiteral(3, Position(1, 18))


def test_parentheses_and_unary():
    tree = value("-(1 + 2)")
    assert isinstance(tree, Unary) and isinstance(tree.operand, Binary)


def test_nested_calls():
    stmt = parse_text("yaz(metin(1))").statements[0]
    assert isinstance(stmt.call.arguments[0], Call)


def test_names():
    assert value("x") == Name("x", Position(1, 9))


def test_expression_without_effect():
    assert error_of("var x = 1\nx * 2").code == "ATS104"


def test_declaration_needs_value():
    err = error_of("var x")
    assert (err.code, err.hint) == ("ATS101", "needs_initial_value")


def test_keyword_is_not_a_name():
    assert error_of("var var = 1").code == "ATS101"


def test_trailing_comma():
    err = error_of('yaz("a",)')
    assert (err.code, err.hint) == ("ATS101", "trailing_comma")


def test_unclosed_parenthesis_at_eof():
    err = error_of('yaz("a"')
    assert (err.code, err.position) == ("ATS102", Position(1, 4))


def test_unclosed_parenthesis_followed_by_next_line():
    err = error_of('yaz("a"\nyaz("b")')
    assert (err.code, err.position) == ("ATS102", Position(1, 4))


def test_two_statements_without_separator():
    err = error_of('yaz("a") yaz("b")')
    assert (err.code, err.position) == ("ATS103", Position(1, 10))


def test_stray_closing_parenthesis():
    assert error_of(")").code == "ATS101"


def test_garbage_after_statement():
    err = error_of('yaz("a") "b"')
    assert (err.code, err.position) == ("ATS101", Position(1, 10))


# -- 0.3 ------------------------------------------------------------------
from atslang.nodes import If  # noqa: E402


def test_logical_precedence():
    tree = value("dogru veya yanlis ve degil 1 > 2")
    assert tree.operator == "veya"
    assert tree.right.operator == "ve"
    assert isinstance(tree.right.right, Unary) and tree.right.right.operator == "degil"
    assert tree.right.right.operand.operator == ">"


def test_comparison_binds_looser_than_arithmetic():
    tree = value("1 + 2 < 3 * 4")
    assert tree.operator == "<"
    assert tree.left.operator == "+" and tree.right.operator == "*"


def test_if_else_chain():
    stmt = parse_text("eger a { } degilse eger b { yaz(1) } degilse { }").statements[0]
    assert isinstance(stmt, If) and stmt.then_block == ()
    assert isinstance(stmt.else_branch, If)
    assert len(stmt.else_branch.then_block) == 1
    assert stmt.else_branch.else_branch == ()


def test_degilse_on_next_line():
    stmt = parse_text("eger a {\n}\n\ndegilse {\n}").statements[0]
    assert stmt.else_branch == ()


def test_brace_on_next_line():
    assert isinstance(parse_text("eger a\n{\n}").statements[0], If)


def test_block_needs_brace():
    err = error_of('eger dogru yaz("a")')
    assert err.code == "ATS101"


def test_assignment_in_condition_hint():
    err = error_of("var x = 1\neger x = 1 { }")
    assert (err.code, err.hint) == ("ATS101", "use_double_equal")


# -- 0.4 ------------------------------------------------------------------
from atslang.nodes import ForRange, FunctionDef, Repeat, Return, While  # noqa: E402


def test_loops():
    program = parse_text("iken a { dur }\ntekrarla 3 { devam }\nher i aralik(1, 10, 2) { }")
    w, r, f = program.statements
    assert isinstance(w, While) and isinstance(r, Repeat) and isinstance(f, ForRange)
    assert f.variable == "i" and f.step is not None


def test_function_definition():
    f = parse_text("fonksiyon topla(a: tam, b): tam { dondur a + b }").statements[0]
    assert isinstance(f, FunctionDef)
    assert [(p.name, p.type_name) for p in f.params] == [("a", "tam"), ("b", None)]
    assert f.return_type == "tam"
    assert isinstance(f.body[0], Return) and f.body[0].value is not None


def test_bare_return():
    f = parse_text("fonksiyon f() { dondur }").statements[0]
    assert f.body[0].value is None
