import ast
import math

ALLOWED_FUNCS = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "sqrt": math.sqrt,
    "abs": abs,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "sinh": math.sinh,
    "cosh": math.cosh,
    "tanh": math.tanh,
    "floor": math.floor,
    "ceil": math.ceil,
}

CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}

ALLOWED_NAMES = set(CONSTANTS) | {"x", "y"}


class MathParseError(ValueError):
    pass


def compile_function(expr: str):
    expr = expr.strip()
    if not expr:
        raise MathParseError("Пустое выражение")
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError as e:
        raise MathParseError(f"Синтаксическая ошибка: {e.msg}") from e
    _check_node(tree.body)
    return _make_evaluator(tree.body)


def _check_node(node):
    if isinstance(node, ast.Expression):
        _check_node(node.body)
    elif isinstance(node, ast.BinOp):
        _check_node(node.left)
        _check_node(node.right)
    elif isinstance(node, ast.UnaryOp):
        _check_node(node.operand)
    elif isinstance(node, ast.Constant):
        if not isinstance(node.value, (int, float)):
            raise MathParseError(f"Недопустимая константа: {node.value!r}")
    elif isinstance(node, ast.Name):
        if node.id not in ALLOWED_NAMES:
            raise MathParseError(f"Неизвестная переменная: {node.id}")
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in ALLOWED_FUNCS:
            raise MathParseError(f"Недопустимая функция")
        for arg in node.args:
            _check_node(arg)
    elif isinstance(node, ast.Pow):
        _check_node(node.left)
        _check_node(node.right)
    else:
        raise MathParseError(f"Недопустимая конструкция: {type(node).__name__}")


def _make_evaluator(node):
    if isinstance(node, ast.Expression):
        return _make_evaluator(node.body)
    if isinstance(node, ast.BinOp):
        left = _make_evaluator(node.left)
        right = _make_evaluator(node.right)
        op = node.op
        if isinstance(op, ast.Add):
            return lambda x, y: left(x, y) + right(x, y)
        if isinstance(op, ast.Sub):
            return lambda x, y: left(x, y) - right(x, y)
        if isinstance(op, ast.Mult):
            return lambda x, y: left(x, y) * right(x, y)
        if isinstance(op, ast.Div):
            return lambda x, y: left(x, y) / right(x, y)
        if isinstance(op, ast.Pow):
            return lambda x, y: left(x, y) ** right(x, y)
        if isinstance(op, ast.Mod):
            return lambda x, y: left(x, y) % right(x, y)
        if isinstance(op, ast.FloorDiv):
            return lambda x, y: left(x, y) // right(x, y)
        raise MathParseError(f"Недопустимая операция: {type(op).__name__}")
    if isinstance(node, ast.UnaryOp):
        operand = _make_evaluator(node.operand)
        if isinstance(node.op, ast.UAdd):
            return lambda x, y: +operand(x, y)
        if isinstance(node.op, ast.USub):
            return lambda x, y: -operand(x, y)
        raise MathParseError(f"Недопустимая операция: {type(node.op).__name__}")
    if isinstance(node, ast.Constant):
        val = node.value
        return lambda x, y: val
    if isinstance(node, ast.Name):
        if node.id == "x":
            return lambda x, y: x
        if node.id == "y":
            return lambda x, y: y
        return lambda x, y: CONSTANTS[node.id]
    if isinstance(node, ast.Call):
        func = ALLOWED_FUNCS[node.func.id]
        arg_evals = [_make_evaluator(a) for a in node.args]
        return lambda x, y: func(*[a(x, y) for a in arg_evals])
    raise MathParseError(f"Недопустимая конструкция: {type(node).__name__}")