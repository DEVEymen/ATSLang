"""Hand-written recursive-descent parser (spec §5, §9.1)."""

from __future__ import annotations

from atslang.errors import ATSError
from atslang.nodes import (
    Assign, Binary, BoolLiteral, Break, Call, Continue, ExprStatement, Expression, FloatLiteral,
    DictLiteral, ForEach, ForRange, FunctionDef, If, Index, IndexAssign, IntLiteral, ListLiteral, Name, Param,
    Program, Repeat, Return, Statement, StringLiteral, Unary, VarDecl, While,
    expression_position,
)
from atslang.source import SourceFile
from atslang.tokens import Token, TokenKind

K = TokenKind
SEPARATORS = (K.NEWLINE, K.SEMICOLON)
STATEMENT_STARTS = (K.IDENT, K.VAR, K.SABIT, K.EGER, K.IKEN, K.HER, K.TEKRARLA, K.DUR,
                    K.DEVAM, K.FONKSIYON, K.DONDUR)
ADDITIVE = {K.PLUS: "+", K.MINUS: "-"}
MULTIPLICATIVE = {K.STAR: "*", K.SLASH: "/", K.SLASHSLASH: "//", K.PERCENT: "%"}
COMPARISON = {K.EQEQ: "==", K.NOTEQ: "!=", K.LT: "<", K.LE: "<=", K.GT: ">", K.GE: ">="}


class Parser:
    def __init__(self, tokens: list[Token], source: SourceFile) -> None:
        self.tokens = tokens
        self.source = source
        self.index = 0
        self.open_parens: list[Token] = []

    # -- helpers ---------------------------------------------------------
    def _peek(self, offset: int = 0) -> Token:
        return self.tokens[min(self.index + offset, len(self.tokens) - 1)]

    def _previous(self) -> Token:
        return self.tokens[self.index - 1]

    def _advance(self) -> Token:
        token = self.tokens[self.index]
        if token.kind is not K.EOF:
            self.index += 1
        return token

    def _unexpected(self, token: Token, expected_key: str, hint: str | None = None,
                    **params: object) -> ATSError:
        # Inside parentheses newlines are ignored, so a missing ')' shows up
        # as end of file or as a token on a later line: report ATS102.
        if self.open_parens and (
            token.kind is K.EOF or token.position.line > self._previous().position.line
        ):
            return ATSError("ATS102", self.open_parens[-1].position, source=self.source)
        if hint is None and token.kind is K.EQUAL and expected_key in ("LBRACE", "statement"):
            hint = "use_double_equal"
        if hint is None and token.kind is K.DEGILSE:
            hint = "else_without_if"
        return ATSError(
            "ATS101", token.position, source=self.source, hint=hint,
            found_key=token.kind.value, expected_key=expected_key, value=token.value, **params,
        )

    def _expect(self, kind: TokenKind, expected_key: str, hint: str | None = None,
                **params: object) -> Token:
        token = self._peek()
        if token.kind is not kind:
            raise self._unexpected(token, expected_key, hint, **params)
        return self._advance()

    def _skip_separators(self) -> None:
        while self._peek().kind in SEPARATORS:
            self._advance()

    def _skip_newlines(self) -> None:
        while self._peek().kind is K.NEWLINE:
            self._advance()

    # -- statements ------------------------------------------------------
    def parse_program(self) -> Program:
        return Program(self._statements(closing=None))

    def _statements(self, closing: Token | None) -> tuple[Statement, ...]:
        """Statements up to end of file (closing is None) or up to the '}'
        that matches the '{' token ``closing``."""
        end = K.EOF if closing is None else K.RBRACE
        statements: list[Statement] = []
        self._skip_separators()
        while self._peek().kind is not end:
            if self._peek().kind is K.EOF:
                raise ATSError("ATS106", closing.position, source=self.source)
            statements.append(self._statement())
            token = self._peek()
            if token.kind in SEPARATORS:
                self._skip_separators()
            elif token.kind is end:
                break
            elif token.kind is K.EOF:
                raise ATSError("ATS106", closing.position, source=self.source)
            elif token.kind in STATEMENT_STARTS:
                raise ATSError("ATS103", token.position, source=self.source)
            else:
                raise self._unexpected(token, "statement")
        return tuple(statements)

    def _statement(self) -> Statement:
        token = self._peek()
        if token.kind in (K.VAR, K.SABIT):
            return self._declaration()
        if token.kind is K.EGER:
            return self._if()
        if token.kind is K.IKEN:
            self._advance()
            condition = self._expression()
            return While(condition, self._block(), token.position)
        if token.kind is K.TEKRARLA:
            self._advance()
            count = self._expression()
            return Repeat(count, self._block(), token.position)
        if token.kind is K.HER:
            return self._for_range()
        if token.kind is K.DUR:
            self._advance()
            return Break(token.position)
        if token.kind is K.DEVAM:
            self._advance()
            return Continue(token.position)
        if token.kind is K.FONKSIYON:
            return self._function()
        if token.kind is K.DONDUR:
            self._advance()
            if self._peek().kind in (*SEPARATORS, K.RBRACE, K.EOF):
                return Return(None, token.position)
            return Return(self._expression(), token.position)
        if token.kind is K.IDENT:
            if self._peek(1).kind is K.EQUAL:
                return self._assignment()
            start = token.position
            expression = self._expression()
            if isinstance(expression, Index) and self._peek().kind is K.EQUAL:
                equal = self._advance()
                return IndexAssign(expression, self._expression(), equal.position)
            if isinstance(expression, Call):
                return ExprStatement(expression)
            nxt = self._peek()
            if isinstance(expression, Name) and nxt.kind in (K.STRING, K.INT, K.FLOAT, K.IDENT):
                # `yaz "a"`: a call written without parentheses
                raise self._unexpected(nxt, "LPAREN", hint="call_parens", name=expression.name)
            raise ATSError("ATS104", start, source=self.source)
        hint = "bare_string" if token.kind is K.STRING else None
        raise self._unexpected(token, "statement", hint=hint)

    def _declaration(self) -> VarDecl:
        keyword = self._advance()
        name = self._expect(K.IDENT, "name")
        type_name = type_position = None
        if self._peek().kind is K.COLON:
            self._advance()
            type_token = self._expect(K.IDENT, "type_name")
            type_name, type_position = type_token.value, type_token.position
        self._expect(K.EQUAL, "EQUAL", hint="needs_initial_value", name=name.value)
        value = self._expression()
        return VarDecl(name.value, keyword.kind is K.SABIT, type_name, type_position,
                       value, name.position)

    def _assignment(self) -> Assign:
        name = self._advance()
        self._advance()  # '='
        return Assign(name.value, self._expression(), name.position)

    def _if(self) -> If:
        keyword = self._advance()  # 'eger'
        condition = self._expression()
        then_block = self._block()
        else_branch: tuple[Statement, ...] | If | None = None
        # `degilse` may be on the line after the closing '}'
        offset = 0
        while self._peek(offset).kind is K.NEWLINE:
            offset += 1
        if self._peek(offset).kind is K.DEGILSE:
            self._skip_newlines()
            self._advance()  # 'degilse'
            if self._peek().kind is K.EGER:
                else_branch = self._if()
            else:
                else_branch = self._block()
        return If(condition, then_block, else_branch, keyword.position)

    def _for_range(self) -> ForRange | ForEach:
        keyword = self._advance()  # 'her'
        variable = self._expect(K.IDENT, "name")
        range_name = self._peek()
        if not (range_name.kind is K.IDENT and range_name.value == "aralik"
                and self._peek(1).kind is K.LPAREN):
            if range_name.kind in (K.LBRACE, K.NEWLINE, K.EOF):
                raise self._unexpected(range_name, "aralik", hint="for_needs_range")
            iterable = self._expression()
            return ForEach(variable.value, variable.position, iterable, self._block(),
                           keyword.position)
        self._advance()
        lparen = self._expect(K.LPAREN, "LPAREN")
        self.open_parens.append(lparen)
        start = self._expression()
        self._expect(K.COMMA, "COMMA", hint="range_arguments")
        end = self._expression()
        step = None
        if self._peek().kind is K.COMMA:
            self._advance()
            step = self._expression()
        self._expect(K.RPAREN, "RPAREN", hint="range_arguments")
        self.open_parens.pop()
        return ForRange(variable.value, variable.position, start, end, step, self._block(),
                        keyword.position)

    def _function(self) -> FunctionDef:
        self._advance()  # 'fonksiyon'
        name = self._expect(K.IDENT, "name")
        lparen = self._expect(K.LPAREN, "LPAREN")
        self.open_parens.append(lparen)
        params: list[Param] = []
        if self._peek().kind is not K.RPAREN:
            while True:
                param = self._expect(K.IDENT, "name")
                type_name = type_position = None
                if self._peek().kind is K.COLON:
                    self._advance()
                    type_token = self._expect(K.IDENT, "type_name")
                    type_name, type_position = type_token.value, type_token.position
                params.append(Param(param.value, type_name, param.position, type_position))
                if self._peek().kind is K.COMMA:
                    self._advance()
                    continue
                break
        self._expect(K.RPAREN, "comma_or_rparen")
        self.open_parens.pop()
        return_type = return_type_position = None
        if self._peek().kind is K.COLON:
            self._advance()
            type_token = self._expect(K.IDENT, "type_name")
            return_type, return_type_position = type_token.value, type_token.position
        return FunctionDef(name.value, tuple(params), return_type, return_type_position,
                           self._block(), name.position)

    def _block(self) -> tuple[Statement, ...]:
        self._skip_newlines()  # allow '{' on the next line
        lbrace = self._expect(K.LBRACE, "LBRACE", hint=None)
        statements = self._statements(closing=lbrace)
        self._advance()  # '}'
        return statements

    # -- expressions -----------------------------------------------------
    def _expression(self) -> Expression:
        return self._or()

    def _or(self) -> Expression:
        left = self._and()
        while self._peek().kind is K.VEYA:
            token = self._advance()
            left = Binary("veya", left, self._and(), token.position)
        return left

    def _and(self) -> Expression:
        left = self._not()
        while self._peek().kind is K.VE:
            token = self._advance()
            left = Binary("ve", left, self._not(), token.position)
        return left

    def _not(self) -> Expression:
        if self._peek().kind is K.DEGIL:
            token = self._advance()
            return Unary("degil", self._not(), token.position)
        return self._comparison()

    def _comparison(self) -> Expression:
        left = self._additive()
        op = COMPARISON.get(self._peek().kind)
        if op is None:
            return left
        token = self._advance()
        result = Binary(op, left, self._additive(), token.position)
        if self._peek().kind in COMPARISON:
            raise ATSError("ATS105", self._peek().position, source=self.source)
        return result

    def _additive(self) -> Expression:
        left = self._term()
        while (op := ADDITIVE.get(self._peek().kind)) is not None:
            token = self._advance()
            left = Binary(op, left, self._term(), token.position)
        return left

    def _term(self) -> Expression:
        left = self._unary()
        while (op := MULTIPLICATIVE.get(self._peek().kind)) is not None:
            token = self._advance()
            left = Binary(op, left, self._unary(), token.position)
        return left

    def _unary(self) -> Expression:
        token = self._peek()
        if token.kind in (K.MINUS, K.PLUS):
            self._advance()
            return Unary(ADDITIVE[token.kind], self._unary(), token.position)
        return self._postfix()

    def _postfix(self) -> Expression:
        expression = self._primary()
        while self._peek().kind is K.LBRACKET:
            lbracket = self._advance()
            self.open_parens.append(lbracket)
            index = self._expression()
            self._expect(K.RBRACKET, "RBRACKET")
            self.open_parens.pop()
            expression = Index(expression, index, lbracket.position)
        return expression

    def _primary(self) -> Expression:
        token = self._peek()
        if token.kind is K.STRING:
            self._advance()
            return StringLiteral(token.value, token.position)
        if token.kind is K.INT:
            self._advance()
            return IntLiteral(int(token.value), token.position)
        if token.kind is K.FLOAT:
            self._advance()
            return FloatLiteral(float(token.value), token.position)
        if token.kind in (K.DOGRU, K.YANLIS):
            self._advance()
            return BoolLiteral(token.kind is K.DOGRU, token.position)
        if token.kind is K.IDENT:
            self._advance()
            if self._peek().kind is K.LPAREN:
                return self._call(token)
            return Name(token.value, token.position)
        if token.kind is K.LBRACKET:
            return self._list_literal()
        if token.kind is K.LBRACE:
            return self._dict_literal()
        if token.kind is K.LPAREN:
            self.open_parens.append(self._advance())
            inner = self._expression()
            self._expect(K.RPAREN, "RPAREN")
            self.open_parens.pop()
            return inner
        raise self._unexpected(token, "expression")

    def _list_literal(self) -> ListLiteral:
        lbracket = self._advance()
        self.open_parens.append(lbracket)
        elements: list[Expression] = []
        if self._peek().kind is not K.RBRACKET:
            while True:
                elements.append(self._expression())
                token = self._peek()
                if token.kind is K.RBRACKET:
                    break
                if token.kind is K.COMMA:
                    self._advance()
                    if self._peek().kind is K.RBRACKET:
                        raise self._unexpected(self._peek(), "expression", hint="trailing_comma")
                    continue
                raise self._unexpected(token, "comma_or_rbracket")
        self._advance()  # ']'
        self.open_parens.pop()
        return ListLiteral(tuple(elements), lbracket.position)

    def _dict_literal(self) -> DictLiteral:
        """`{anahtar: deger, ...}`. The lexer keeps newlines inside braces
        (they separate statements in blocks), so they are skipped here."""
        lbrace = self._advance()
        entries: list[tuple[Expression, Expression]] = []
        self._skip_newlines()
        if self._peek().kind is K.EOF:
            raise ATSError("ATS102", lbrace.position, source=self.source)
        if self._peek().kind is not K.RBRACE:
            while True:
                key = self._expression()
                self._skip_newlines()
                self._expect(K.COLON, "COLON", hint="dict_entry")
                self._skip_newlines()
                value = self._expression()
                entries.append((key, value))
                self._skip_newlines()
                token = self._peek()
                if token.kind is K.RBRACE:
                    break
                if token.kind is K.COMMA:
                    self._advance()
                    self._skip_newlines()
                    if self._peek().kind is K.RBRACE:
                        raise self._unexpected(self._peek(), "expression", hint="trailing_comma")
                    continue
                if token.kind is K.EOF:
                    raise ATSError("ATS102", lbrace.position, source=self.source)
                raise self._unexpected(token, "comma_or_rbrace")
        self._advance()  # '}'
        return DictLiteral(tuple(entries), lbrace.position)

    def _call(self, name: Token) -> Call:
        lparen = self._advance()
        self.open_parens.append(lparen)
        arguments: list[Expression] = []
        if self._peek().kind is not K.RPAREN:
            while True:
                arguments.append(self._expression())
                token = self._peek()
                if token.kind is K.RPAREN:
                    break
                if token.kind is K.COMMA:
                    self._advance()
                    if self._peek().kind is K.RPAREN:
                        raise self._unexpected(self._peek(), "expression", hint="trailing_comma")
                    continue
                raise self._unexpected(token, "comma_or_rparen")
        self._advance()  # ')'
        self.open_parens.pop()
        return Call(name.value, tuple(arguments), name.position)


def parse(tokens: list[Token], source: SourceFile) -> Program:
    return Parser(tokens, source).parse_program()


def parse_expression(tokens: list[Token], source: SourceFile) -> Expression:
    """A single expression filling the whole input (used by the REPL)."""
    parser = Parser(tokens, source)
    parser._skip_separators()
    expression = parser._expression()
    parser._skip_separators()
    if parser._peek().kind is not K.EOF:
        raise parser._unexpected(parser._peek(), "statement")
    return expression


__all__ = ["parse", "parse_expression", "Parser", "expression_position"]
