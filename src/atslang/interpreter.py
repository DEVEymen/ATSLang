"""Tree-walking interpreter (spec §6)."""

from __future__ import annotations

import math
import random
import sys
from typing import TextIO

from atslang.builtins import BUILTINS, Context
from atslang.checker import check
from atslang.errors import ATSError
from atslang.lexer import tokenize
from atslang.nodes import (
    Assign, Binary, BoolLiteral, Break, Call, Continue, ExprStatement, Expression, FloatLiteral,
    DictLiteral, ForEach, ForRange, FunctionDef, If, Index, IndexAssign, IntLiteral, ListLiteral,
    Name,
    Program, Repeat, Return, Statement, StringLiteral, Unary, VarDecl, While,
    expression_position,
)
from atslang.parser import parse
from atslang.source import Position, SourceFile
from atslang.values import (
    KEY_TYPES, Value, coerce_to, fits_type, float_is_finite, int_in_range, is_number, type_name,
    values_equal,
)

ORDERING = ("<", "<=", ">", ">=")
EQUALITY = ("==", "!=")
MAX_CALL_DEPTH = 1000  # spec §6.11


def format_key(key: Value) -> str:
    return f'"{key}"' if isinstance(key, str) else str(key)


class _BreakSignal(Exception):
    pass


class _ContinueSignal(Exception):
    pass


class _ReturnSignal(Exception):
    def __init__(self, value: Value | None) -> None:
        self.value = value


class Interpreter:
    def __init__(self, out: TextIO, source: SourceFile | None = None,
                 inp: TextIO | None = None, seed: int | None = None) -> None:
        self.out = out
        self.inp = inp
        self.rng = random.Random(seed)
        self.source = source
        # One frame per open block: name -> [value, declared type or None]
        self.frames: list[dict[str, list]] = [{}]
        self.functions: dict[str, FunctionDef] = {}
        self.depth = 0

    def _slot(self, name: str) -> list:
        for frame in reversed(self.frames):
            if name in frame:
                return frame[name]
        raise KeyError(name)  # prevented by the checker

    def _error(self, code: str, position: Position | None, **kwargs: object) -> ATSError:
        return ATSError(code, position, source=self.source, **kwargs)

    # -- statements ------------------------------------------------------
    def run(self, program: Program) -> None:
        try:
            self._statements(program.statements)
        except ATSError:
            # Show the output produced so far before the error message.
            try:
                self.out.flush()
            except OSError:
                pass
            raise
        try:
            self.out.flush()
        except OSError as exc:
            raise self._error("ATS901", None, reason=exc.strerror or exc) from exc

    def evaluate(self, expression: Expression) -> Value | None:
        """Evaluate one expression at the top level (used by the REPL).
        A call to a function without a value gives None."""
        if isinstance(expression, Call):
            return self._call(expression)
        return self._evaluate(expression)

    def _statements(self, statements: tuple[Statement, ...]) -> None:
        for statement in statements:
            self._statement(statement)

    def _block(self, statements: tuple[Statement, ...], frame: dict | None = None) -> None:
        self.frames.append(frame if frame is not None else {})
        try:
            self._statements(statements)
        finally:
            self.frames.pop()

    def _statement(self, statement: Statement) -> None:
        if isinstance(statement, VarDecl):
            value = self._evaluate(statement.value)
            self._check_type(statement.name, statement.type_name, value, statement.value)
            self.frames[-1][statement.name] = [coerce_to(value, statement.type_name),
                                               statement.type_name]
        elif isinstance(statement, Assign):
            value = self._evaluate(statement.value)
            slot = self._slot(statement.name)
            self._check_type(statement.name, slot[1], value, statement.value)
            slot[0] = coerce_to(value, slot[1])
        elif isinstance(statement, IndexAssign):
            self._index_assign(statement)
        elif isinstance(statement, ExprStatement):
            self._call(statement.call)
        elif isinstance(statement, ForEach):
            self._for_each(statement)
        elif isinstance(statement, If):
            self._if(statement)
        elif isinstance(statement, While):
            self._while(statement)
        elif isinstance(statement, Repeat):
            self._repeat(statement)
        elif isinstance(statement, ForRange):
            self._for_range(statement)
        elif isinstance(statement, Break):
            raise _BreakSignal()
        elif isinstance(statement, Continue):
            raise _ContinueSignal()
        elif isinstance(statement, FunctionDef):
            self.functions[statement.name] = statement
        elif isinstance(statement, Return):
            value = None if statement.value is None else self._evaluate(statement.value)
            raise _ReturnSignal(value)

    def _check_type(self, name: str, declared: str | None, value: Value,
                    expression: Expression) -> None:
        if declared is not None and not fits_type(value, declared):
            raise self._error("ATS304", expression_position(expression), name=name,
                              expected=declared, given=type_name(value))

    def _if(self, node: If) -> None:
        if self._condition(node.condition):
            self._block(node.then_block)
        elif isinstance(node.else_branch, If):
            self._if(node.else_branch)
        elif node.else_branch is not None:
            self._block(node.else_branch)

    def _condition(self, expression: Expression) -> bool:
        value = self._evaluate(expression)
        if not isinstance(value, bool):
            raise self._error("ATS306", expression_position(expression), given=type_name(value))
        return value

    # -- loops -----------------------------------------------------------
    def _loop_iteration(self, body: tuple[Statement, ...], frame: dict | None = None) -> bool:
        """Run one iteration. Return False when the loop must stop (`dur`)."""
        try:
            self._block(body, frame)
        except _BreakSignal:
            return False
        except _ContinueSignal:
            pass
        return True

    def _while(self, node: While) -> None:
        while self._condition(node.condition):
            if not self._loop_iteration(node.body):
                break

    def _integer(self, expression: Expression, what: str) -> int:
        value = self._evaluate(expression)
        if type_name(value) != "tam":
            raise self._error("ATS308", expression_position(expression), what=what,
                              given=type_name(value))
        return value

    def _repeat(self, node: Repeat) -> None:
        count = self._integer(node.count, "tekrarla")
        if count < 0:
            raise self._error("ATS309", expression_position(node.count), count=count)
        for _ in range(count):
            if not self._loop_iteration(node.body):
                break

    def _for_range(self, node: ForRange) -> None:
        start = self._integer(node.start, "aralik")
        end = self._integer(node.end, "aralik")
        step = 1 if node.step is None else self._integer(node.step, "aralik")
        if step == 0:
            raise self._error("ATS310", expression_position(node.step))
        i = start
        while (i <= end) if step > 0 else (i >= end):
            if not self._loop_iteration(node.body, {node.variable: [i, None]}):
                break
            i += step

    def _for_each(self, node: ForEach) -> None:
        iterable = self._evaluate(node.iterable)
        if type_name(iterable) not in ("liste", "metin", "sozluk"):
            raise self._error("ATS318", expression_position(node.iterable),
                              given=type_name(iterable))
        # A snapshot: changing the list inside the loop does not change the turns.
        # A sozluk is walked by its keys.
        for item in list(iterable):
            if not self._loop_iteration(node.body, {node.variable: [item, None]}):
                break

    # -- lists -----------------------------------------------------------
    def _checked_index(self, container: Value, node: Index) -> int:
        if type_name(container) not in ("liste", "metin", "sozluk"):
            raise self._error("ATS316", node.position, given=type_name(container))
        index = self._evaluate(node.index)
        if type_name(index) != "tam":
            raise self._error("ATS308", expression_position(node.index), what="indeks",
                              given=type_name(index))
        if not 0 <= index < len(container):
            raise self._error("ATS314", expression_position(node.index), index=index,
                              length=len(container))
        return index

    def _key(self, node: Index) -> Value:
        key = self._evaluate(node.index)
        if type_name(key) not in KEY_TYPES:
            raise self._error("ATS319", expression_position(node.index), given=type_name(key))
        return key

    def _index(self, node: Index) -> Value:
        container = self._evaluate(node.target)
        if isinstance(container, dict):
            key = self._key(node)
            if key not in container:
                raise self._error("ATS320", expression_position(node.index),
                                  key=format_key(key))
            return container[key]
        return container[self._checked_index(container, node)]

    def _index_assign(self, node: IndexAssign) -> None:
        container = self._evaluate(node.target.target)
        if isinstance(container, str):
            raise self._error("ATS317", node.target.position)
        if isinstance(container, dict):
            key = self._key(node.target)
            container[key] = self._evaluate(node.value)
            return
        index = self._checked_index(container, node.target)
        container[index] = self._evaluate(node.value)

    # -- expressions -----------------------------------------------------
    def _evaluate(self, expression: Expression) -> Value:
        if isinstance(expression, (StringLiteral, IntLiteral, FloatLiteral, BoolLiteral)):
            return expression.value
        if isinstance(expression, Name):
            return self._slot(expression.name)[0]
        if isinstance(expression, Unary):
            return self._unary(expression)
        if isinstance(expression, Binary):
            return self._binary(expression)
        if isinstance(expression, ListLiteral):
            return [self._evaluate(element) for element in expression.elements]
        if isinstance(expression, DictLiteral):
            result: dict = {}
            for key_expr, value_expr in expression.entries:
                key = self._evaluate(key_expr)
                if type_name(key) not in KEY_TYPES:
                    raise self._error("ATS319", expression_position(key_expr),
                                      given=type_name(key))
                result[key] = self._evaluate(value_expr)
            return result
        if isinstance(expression, Index):
            return self._index(expression)
        if isinstance(expression, Call):
            result = self._call(expression)
            if result is None:
                # Only possible for user functions that ended without `dondur <ifade>`
                raise self._error("ATS311", expression.position, name=expression.name)
            return result
        raise TypeError(f"unknown expression: {expression!r}")

    def _call(self, call: Call) -> Value | None:
        args = tuple(self._evaluate(arg) for arg in call.arguments)
        function = self.functions.get(call.name)
        if function is not None:
            return self._call_user(function, call, args)
        ctx = Context(self.out, call.position, self.source, self.inp,
                      tuple(expression_position(a) for a in call.arguments), self.rng)
        try:
            return BUILTINS[call.name].implementation(ctx, args)
        except OSError as exc:
            raise self._error("ATS901", call.position, reason=exc.strerror or exc) from exc

    def _call_user(self, function: FunctionDef, call: Call, args: tuple[Value, ...]
                   ) -> Value | None:
        frame: dict[str, list] = {}
        for param, arg, arg_expr in zip(function.params, args, call.arguments):
            self._check_type(param.name, param.type_name, arg, arg_expr)
            frame[param.name] = [coerce_to(arg, param.type_name), param.type_name]

        if self.depth >= MAX_CALL_DEPTH:
            raise self._error("ATS313", call.position, limit=MAX_CALL_DEPTH)
        saved_frames = self.frames
        self.frames = [self.frames[0]]  # functions see globals and their own locals
        self.depth += 1
        result: Value | None = None
        try:
            self._block(function.body, frame)
        except _ReturnSignal as signal:
            result = signal.value
        finally:
            self.frames = saved_frames
            self.depth -= 1

        if function.return_type is not None:
            if result is None:
                raise self._error("ATS311", call.position, name=function.name)
            if not fits_type(result, function.return_type):
                raise self._error("ATS312", call.position, name=function.name,
                                  expected=function.return_type, given=type_name(result))
            result = coerce_to(result, function.return_type)
        return result

    def _unary(self, node: Unary) -> Value:
        value = self._evaluate(node.operand)
        if node.operator == "degil":
            if not isinstance(value, bool):
                raise self._error("ATS301", node.position, op="degil",
                                  types=f"degil {type_name(value)}")
            return not value
        if not is_number(value):
            raise self._error("ATS301", node.position, op=node.operator,
                              types=f"{node.operator}{type_name(value)}")
        result = -value if node.operator == "-" else value
        return self._checked(result, node.position)

    def _binary(self, node: Binary) -> Value:
        op = node.operator
        if op in ("ve", "veya"):
            return self._logical(node)

        left = self._evaluate(node.left)
        right = self._evaluate(node.right)

        if op in EQUALITY or op in ORDERING:
            return self._compare(node, left, right)

        if isinstance(left, dict) or isinstance(right, dict):
            raise self._error("ATS301", node.position, op=op,
                              types=f"{type_name(left)} {op} {type_name(right)}")

        if isinstance(left, list) or isinstance(right, list):
            if op == "+" and isinstance(left, list) and isinstance(right, list):
                return left + right  # a new list
            raise self._error("ATS301", node.position, op=op,
                              types=f"{type_name(left)} {op} {type_name(right)}")

        if isinstance(left, bool) or isinstance(right, bool):
            raise self._error("ATS301", node.position, op=op,
                              types=f"{type_name(left)} {op} {type_name(right)}")

        if isinstance(left, str) or isinstance(right, str):
            if op == "+" and isinstance(left, str) and isinstance(right, str):
                return left + right
            hint = "convert_to_text" if op == "+" else None
            raise self._error("ATS301", node.position, hint=hint, op=op,
                              types=f"{type_name(left)} {op} {type_name(right)}")

        if op in ("/", "//", "%") and right == 0:
            raise self._error("ATS302", node.position)

        if op == "+":
            result = left + right
        elif op == "-":
            result = left - right
        elif op == "*":
            result = left * right
        elif op == "/":
            result = left / right  # always ondalik
        elif op == "//":
            result = left // right
            if isinstance(result, float):
                result = float(math.floor(result))
        else:  # "%"
            result = left % right
        return self._checked(result, node.position)

    def _logical(self, node: Binary) -> bool:
        """`ve` / `veya` with short-circuit evaluation (spec §6.8)."""
        left = self._evaluate(node.left)
        if not isinstance(left, bool):
            raise self._error("ATS301", node.position, op=node.operator,
                              types=f"{type_name(left)} {node.operator} ...")
        if node.operator == "ve" and not left:
            return False
        if node.operator == "veya" and left:
            return True
        right = self._evaluate(node.right)
        if not isinstance(right, bool):
            raise self._error("ATS301", node.position, op=node.operator,
                              types=f"{type_name(left)} {node.operator} {type_name(right)}")
        return right

    def _compare(self, node: Binary, left: Value, right: Value) -> bool:
        op = node.operator
        lt, rt = type_name(left), type_name(right)
        comparable = (is_number(left) and is_number(right)) or lt == rt
        if op in ORDERING and lt in ("mantiksal", "liste", "sozluk"):
            comparable = False
        if not comparable:
            raise self._error("ATS301", node.position, op=op, types=f"{lt} {op} {rt}")
        if op == "==":
            return values_equal(left, right)
        if op == "!=":
            return not values_equal(left, right)
        if op == "<":
            return left < right
        if op == "<=":
            return left <= right
        if op == ">":
            return left > right
        return left >= right

    def _checked(self, result: Value, position: Position) -> Value:
        if isinstance(result, int) and not int_in_range(result):
            raise self._error("ATS303", position)
        if isinstance(result, float) and not float_is_finite(result):
            raise self._error("ATS303", position)
        return result


def compile_source(source: SourceFile) -> Program:
    """Lex, parse and check. Raises ATSError; nothing has run yet (spec §6.1)."""
    program = parse(tokenize(source), source)
    check(program, source)
    return program


def run_source(source: SourceFile, out: TextIO, inp: TextIO | None = None,
               seed: int | None = None) -> None:
    # Each ATSLang call uses several Python frames; MAX_CALL_DEPTH is the real limit.
    if sys.getrecursionlimit() < 50_000:
        sys.setrecursionlimit(50_000)
    Interpreter(out, source, inp, seed).run(compile_source(source))
