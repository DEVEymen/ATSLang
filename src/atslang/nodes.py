"""AST nodes (spec §5, §9.2).

Nodes only carry data and source positions. They contain no execution logic,
so the future bytecode compiler can consume the same tree.
"""

from __future__ import annotations

from dataclasses import dataclass

from atslang.source import Position


# -- expressions ---------------------------------------------------------
@dataclass(frozen=True, slots=True)
class StringLiteral:
    value: str
    position: Position


@dataclass(frozen=True, slots=True)
class IntLiteral:
    value: int
    position: Position


@dataclass(frozen=True, slots=True)
class FloatLiteral:
    value: float
    position: Position


@dataclass(frozen=True, slots=True)
class BoolLiteral:
    value: bool
    position: Position


@dataclass(frozen=True, slots=True)
class Name:
    name: str
    position: Position


@dataclass(frozen=True, slots=True)
class Unary:
    operator: str  # "-", "+" or "degil"
    operand: Expression
    position: Position  # position of the operator


@dataclass(frozen=True, slots=True)
class Binary:
    # "+", "-", "*", "/", "//", "%", "==", "!=", "<", "<=", ">", ">=", "ve", "veya"
    operator: str
    left: Expression
    right: Expression
    position: Position  # position of the operator


@dataclass(frozen=True, slots=True)
class Call:
    name: str
    arguments: tuple[Expression, ...]
    position: Position


@dataclass(frozen=True, slots=True)
class ListLiteral:
    elements: tuple[Expression, ...]
    position: Position  # position of '['


@dataclass(frozen=True, slots=True)
class DictLiteral:
    entries: tuple[tuple[Expression, Expression], ...]
    position: Position  # position of '{'


@dataclass(frozen=True, slots=True)
class Index:
    target: Expression
    index: Expression
    position: Position  # position of '['


Expression = (StringLiteral | IntLiteral | FloatLiteral | BoolLiteral | Name | Unary | Binary
              | Call | ListLiteral | DictLiteral | Index)


# -- statements ----------------------------------------------------------
@dataclass(frozen=True, slots=True)
class VarDecl:
    name: str
    constant: bool  # True for `sabit`
    type_name: str | None
    type_position: Position | None
    value: Expression
    position: Position  # position of the name


@dataclass(frozen=True, slots=True)
class Assign:
    name: str
    value: Expression
    position: Position  # position of the name


@dataclass(frozen=True, slots=True)
class IndexAssign:
    target: Index
    value: Expression
    position: Position  # position of '='


@dataclass(frozen=True, slots=True)
class ExprStatement:
    call: Call


@dataclass(frozen=True, slots=True)
class If:
    condition: Expression
    then_block: tuple[Statement, ...]
    # `degilse { ... }` gives a tuple, `degilse eger ...` gives another If
    else_branch: tuple[Statement, ...] | If | None
    position: Position  # position of `eger`


@dataclass(frozen=True, slots=True)
class While:
    condition: Expression
    body: tuple[Statement, ...]
    position: Position


@dataclass(frozen=True, slots=True)
class Repeat:
    count: Expression
    body: tuple[Statement, ...]
    position: Position


@dataclass(frozen=True, slots=True)
class ForRange:
    variable: str
    variable_position: Position
    start: Expression
    end: Expression
    step: Expression | None
    body: tuple[Statement, ...]
    position: Position


@dataclass(frozen=True, slots=True)
class ForEach:
    variable: str
    variable_position: Position
    iterable: Expression
    body: tuple[Statement, ...]
    position: Position


@dataclass(frozen=True, slots=True)
class Break:
    position: Position


@dataclass(frozen=True, slots=True)
class Continue:
    position: Position


@dataclass(frozen=True, slots=True)
class Param:
    name: str
    type_name: str | None
    position: Position
    type_position: Position | None


@dataclass(frozen=True, slots=True)
class FunctionDef:
    name: str
    params: tuple[Param, ...]
    return_type: str | None
    return_type_position: Position | None
    body: tuple[Statement, ...]
    position: Position  # position of the name


@dataclass(frozen=True, slots=True)
class Return:
    value: Expression | None
    position: Position


Statement = (VarDecl | Assign | IndexAssign | ExprStatement | If | While | Repeat | ForRange
             | ForEach | Break | Continue | FunctionDef | Return)


@dataclass(frozen=True, slots=True)
class Program:
    statements: tuple[Statement, ...]


def expression_position(expression: Expression) -> Position:
    """The leftmost position of an expression (for error carets)."""
    while isinstance(expression, (Binary, Index)):
        expression = expression.left if isinstance(expression, Binary) else expression.target
    return expression.position
