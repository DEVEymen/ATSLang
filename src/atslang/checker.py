"""Static checks that run before any statement executes (spec §6.1, §6.2, §6.10)."""

from __future__ import annotations

from dataclasses import dataclass

from atslang.builtins import BUILTINS, RANGE_NAME
from atslang.errors import ATSError
from atslang.nodes import (
    Assign, Binary, Break, Call, Continue, ExprStatement, Expression, ForEach, ForRange,
    DictLiteral, FunctionDef, If, Index, IndexAssign, ListLiteral, Name, Program, Repeat, Return, Statement,
    Unary, VarDecl, While,
)
from atslang.source import Position, SourceFile
from atslang.values import TYPE_NAMES

RESERVED = set(BUILTINS) | {RANGE_NAME}


def _edit_distance(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def _similar(name: str, candidates) -> str | None:
    """A candidate that differs only in case or by a single edit."""
    for candidate in candidates:
        if candidate == name:
            continue
        if candidate.lower() == name.lower():
            return candidate
        # One-letter differences between very short names are not meaningful (b / x).
        if max(len(name), len(candidate)) >= 3 and _edit_distance(candidate, name) <= 1:
            return candidate
    return None


def suggest_name(name: str) -> str | None:
    """Suggest a builtin function name."""
    return _similar(name, BUILTINS)


@dataclass
class Variable:
    constant: bool
    position: Position
    function: FunctionDef | None = None  # set for user-defined functions
    returns_value: bool = False


def _returns_value(statements) -> bool:
    """Whether a function body contains `dondur <ifade>` (not inside nested functions)."""
    for statement in statements:
        if isinstance(statement, Return) and statement.value is not None:
            return True
        if isinstance(statement, If):
            branches = [statement.then_block]
            branch = statement.else_branch
            while isinstance(branch, If):
                branches.append(branch.then_block)
                branch = branch.else_branch
            if branch is not None:
                branches.append(branch)
            if any(_returns_value(b) for b in branches):
                return True
        if isinstance(statement, (While, Repeat, ForRange, ForEach)) and _returns_value(statement.body):
            return True
    return False


class Checker:
    def __init__(self, source: SourceFile) -> None:
        self.source = source
        # One dict per open block; the first one is the global scope (spec §6.2).
        self.scopes: list[dict[str, Variable]] = [{}]
        self.loop_depth = 0
        self.function: FunctionDef | None = None

    def _lookup(self, name: str) -> Variable | None:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _visible_names(self) -> list[str]:
        return [name for scope in self.scopes for name in scope]

    def _error(self, code: str, position: Position, **kwargs: object) -> ATSError:
        return ATSError(code, position, source=self.source, **kwargs)

    def check(self, program: Program) -> None:
        self._statements(program.statements)

    def check_expression(self, expression: Expression) -> None:
        self._expression(expression)

    def call_returns_value(self, call: Call) -> bool:
        """Whether a call would give a value (unknown names count as no)."""
        variable = self._lookup(call.name)
        if variable is not None:
            return variable.function is not None and variable.returns_value
        builtin = BUILTINS.get(call.name)
        return builtin is not None and builtin.returns_value

    # -- statements ------------------------------------------------------
    def _statements(self, statements: tuple[Statement, ...]) -> None:
        for statement in statements:
            self._statement(statement)

    def _statement(self, statement: Statement) -> None:
        if isinstance(statement, VarDecl):
            self._declaration(statement)
        elif isinstance(statement, Assign):
            self._assignment(statement)
        elif isinstance(statement, IndexAssign):
            self._expression(statement.target)
            self._expression(statement.value)
        elif isinstance(statement, ForEach):
            self._check_new_name(statement.variable, statement.variable_position)
            self._expression(statement.iterable)
            self._loop_body(statement.body,
                            {statement.variable: Variable(False, statement.variable_position)})
        elif isinstance(statement, ExprStatement):
            self._call(statement.call, needs_value=False)
        elif isinstance(statement, If):
            self._if(statement)
        elif isinstance(statement, While):
            self._expression(statement.condition)
            self._loop_body(statement.body)
        elif isinstance(statement, Repeat):
            self._expression(statement.count)
            self._loop_body(statement.body)
        elif isinstance(statement, ForRange):
            self._for_range(statement)
        elif isinstance(statement, (Break, Continue)):
            if self.loop_depth == 0:
                keyword = "dur" if isinstance(statement, Break) else "devam"
                raise self._error("ATS211", statement.position, keyword=keyword)
        elif isinstance(statement, FunctionDef):
            self._function(statement)
        elif isinstance(statement, Return):
            if self.function is None:
                raise self._error("ATS213", statement.position)
            if statement.value is not None:
                self._expression(statement.value)

    def _block(self, statements: tuple[Statement, ...], names: dict[str, Variable] | None = None
               ) -> None:
        self.scopes.append(dict(names or {}))
        try:
            self._statements(statements)
        finally:
            self.scopes.pop()

    def _loop_body(self, statements: tuple[Statement, ...],
                   names: dict[str, Variable] | None = None) -> None:
        self.loop_depth += 1
        try:
            self._block(statements, names)
        finally:
            self.loop_depth -= 1

    def _if(self, node: If) -> None:
        self._expression(node.condition)
        self._block(node.then_block)
        if isinstance(node.else_branch, If):
            self._if(node.else_branch)
        elif node.else_branch is not None:
            self._block(node.else_branch)

    def _check_new_name(self, name: str, position: Position) -> None:
        if name in RESERVED:
            raise self._error("ATS206", position, name=name)
        previous = self._lookup(name)
        if previous is not None:
            raise self._error("ATS204", position, name=name, line=previous.position.line)

    def _check_type_name(self, type_name: str | None, position: Position | None) -> None:
        if type_name is not None and type_name not in TYPE_NAMES:
            suggestion = _similar(type_name, TYPE_NAMES)
            raise self._error("ATS209", position, name=type_name,
                              hint="did_you_mean" if suggestion else None, suggestion=suggestion)

    def _declaration(self, decl: VarDecl) -> None:
        if decl.name in RESERVED:
            raise self._error("ATS206", decl.position, name=decl.name)
        self._check_type_name(decl.type_name, decl.type_position)
        self._check_new_name(decl.name, decl.position)
        self._expression(decl.value)
        self.scopes[-1][decl.name] = Variable(decl.constant, decl.position)

    def _assignment(self, assign: Assign) -> None:
        if assign.name in RESERVED:
            raise self._error("ATS206", assign.position, name=assign.name)
        variable = self._lookup(assign.name)
        if variable is None:
            suggestion = _similar(assign.name, self._visible_names())
            if suggestion:
                raise self._error("ATS203", assign.position, name=assign.name,
                                  hint="did_you_mean", suggestion=suggestion)
            raise self._error("ATS203", assign.position, name=assign.name, hint="declare_first")
        if variable.function is not None:
            raise self._error("ATS208", assign.position, name=assign.name)
        if variable.constant:
            raise self._error("ATS205", assign.position, name=assign.name)
        self._expression(assign.value)

    def _for_range(self, node: ForRange) -> None:
        self._check_new_name(node.variable, node.variable_position)
        for expression in (node.start, node.end, node.step):
            if expression is not None:
                self._expression(expression)
        self._loop_body(node.body, {node.variable: Variable(False, node.variable_position)})

    def _function(self, node: FunctionDef) -> None:
        if len(self.scopes) > 1 or self.function is not None:
            raise self._error("ATS212", node.position, name=node.name)
        self._check_new_name(node.name, node.position)
        self._check_type_name(node.return_type, node.return_type_position)
        params: dict[str, Variable] = {}
        for param in node.params:
            self._check_type_name(param.type_name, param.type_position)
            if param.name in RESERVED:
                raise self._error("ATS206", param.position, name=param.name)
            earlier = params.get(param.name) or self._lookup(param.name)
            if earlier is not None:
                raise self._error("ATS204", param.position, name=param.name,
                                  line=earlier.position.line)
            params[param.name] = Variable(False, param.position)
        # Declared before checking the body, so the function may call itself.
        self.scopes[0][node.name] = Variable(True, node.position, function=node,
                                             returns_value=_returns_value(node.body))
        saved = (self.scopes, self.loop_depth, self.function)
        self.scopes, self.loop_depth, self.function = [self.scopes[0]], 0, node
        try:
            self._block(node.body, params)
        finally:
            self.scopes, self.loop_depth, self.function = saved

    # -- expressions -----------------------------------------------------
    def _expression(self, expression: Expression) -> None:
        if isinstance(expression, Name):
            self._name(expression)
        elif isinstance(expression, Unary):
            self._expression(expression.operand)
        elif isinstance(expression, Binary):
            self._expression(expression.left)
            self._expression(expression.right)
        elif isinstance(expression, Call):
            self._call(expression, needs_value=True)
        elif isinstance(expression, ListLiteral):
            for element in expression.elements:
                self._expression(element)
        elif isinstance(expression, DictLiteral):
            for key, value in expression.entries:
                self._expression(key)
                self._expression(value)
        elif isinstance(expression, Index):
            self._expression(expression.target)
            self._expression(expression.index)

    def _name(self, name: Name) -> None:
        variable = self._lookup(name.name)
        if variable is not None:
            if variable.function is not None:
                raise self._error("ATS208", name.position, name=name.name)
            return
        if name.name in RESERVED:
            raise self._error("ATS208", name.position, name=name.name)
        suggestion = _similar(name.name, self._visible_names())
        if suggestion:
            raise self._error("ATS203", name.position, name=name.name,
                              hint="did_you_mean", suggestion=suggestion)
        raise self._error("ATS203", name.position, name=name.name, hint="quote_name")

    def _call(self, call: Call, needs_value: bool) -> None:
        if call.name == RANGE_NAME:
            raise self._error("ATS214", call.position)
        variable = self._lookup(call.name)
        if variable is not None and variable.function is None:
            raise self._error("ATS207", call.position, name=call.name)
        if variable is not None:
            arity = minimum = len(variable.function.params)
            returns_value = variable.returns_value
        else:
            builtin = BUILTINS.get(call.name)
            if builtin is None:
                candidates = list(BUILTINS) + [
                    n for n, v in self.scopes[0].items() if v.function is not None]
                suggestion = _similar(call.name, candidates)
                raise self._error("ATS201", call.position, name=call.name,
                                  hint="did_you_mean" if suggestion else None,
                                  suggestion=suggestion)
            arity, minimum, returns_value = builtin.arity, builtin.minimum, builtin.returns_value
        if not minimum <= len(call.arguments) <= arity:
            expected = arity if minimum == arity else f"{minimum}-{arity}"
            raise self._error("ATS202", call.position, name=call.name,
                              expected=expected, given=len(call.arguments))
        if needs_value and not returns_value:
            raise self._error("ATS210", call.position, name=call.name)
        for argument in call.arguments:
            self._expression(argument)


def check(program: Program, source: SourceFile) -> None:
    Checker(source).check(program)
